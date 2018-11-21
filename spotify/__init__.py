from threading import Thread
try:
    # Python 3 modules
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    import urllib.parse as urlparse
except ImportError:
    # Python 2 modules
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from BaseHTTPServer import HTTPServer
    import urlparse

import base64
import time
import requests
import webbrowser

LISTENER_PORT = 9020
REDIRECT_URI = 'http://localhost:%d/' % LISTENER_PORT
SCOPES = [
    'user-read-currently-playing',
    'user-read-playback-state'
]
RESPONSE_HTML = """
<html>
<head>
    <title>Spotify CLI</title>
</head>
<body>
    <script type="text/javascript">
        window.close();
    </script>
</body>
</html>
"""

def get_authorization_code(client_id):
    class AuthorizationHandler(SimpleHTTPRequestHandler):
        last_code = None

        def do_GET(self):
            self.send_response(200, 'OK')
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(RESPONSE_HTML, 'utf-8'))

            parsed = urlparse.parse_qs(self.path[2:])
            if 'code' not in parsed:
                return
            code = parsed['code'][0]
            AuthorizationHandler.last_code = code

            t = Thread(target=self.server.shutdown)
            t.daemon = True
            t.start()

        def log_message(self, format, *args):
            pass

    server = HTTPServer(('localhost', LISTENER_PORT), AuthorizationHandler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()
    authorize_user(client_id)
    server_thread.join()
    return AuthorizationHandler.last_code

def authorize_user(client_id):
    url = get_authorization_url(client_id)
    webbrowser.open_new(url)

def get_authorization_url(client_id):
    query = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES)
    }
    return 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode(query)

def get_access_token(client_id, client_secret, code):
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    return request_access_token(client_id, client_secret, payload)

def refresh_access_token(client_id, client_secret, access_token):
    token_time = access_token['time']
    current_time = int(time.time())
    expires_in = access_token['expires_in']
    if current_time - token_time < expires_in:
        return None
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': access_token['refresh_token']
    }
    return request_access_token(client_id, client_secret, payload)

def request_access_token(client_id, client_secret, payload):
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    r = requests.post(url, data=payload, headers=headers, auth=(client_id, client_secret))
    r.raise_for_status()
    access_token = r.json()
    access_token['time'] = int(time.time())
    return access_token

def get_current_playing(access_token):
    url = 'https://api.spotify.com/v1/me/player/currently-playing'
    headers = {
        'Authorization': access_token['token_type'] + ' ' + access_token['access_token']
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    if r.status_code == 204:
        return None
    return r.json()

def format_current_playing(playing_data):
    item = playing_data['item']
    artists = format_artists(item['artists'])
    album = item['album']
    return '%s [%s] - %s' % (artists, album['name'], item['name'])

def format_artists(artists):
    return ', '.join(map(lambda x: x['name'], artists))
