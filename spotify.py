#!/usr/bin/env python
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import base64
import click
import json
import os
import sys
import requests
import urllib
import urlparse
import webbrowser

REDIRECT_URI = 'http://localhost:9020/'
LISTENER_PORT = 9020

@click.command()
def main():
    credentials = load_credentials()
    if not 'access_token' in credentials:
        logerr('Access token not found. Opening browser for authorization.')
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        code = get_authorization_code(client_id)
        access_token = get_access_token(client_id, client_secret, code)
        credentials['access_token'] = access_token
        save_credentials(credentials)
    else:
        access_token = credentials['access_token']
    current_playing = get_current_playing(access_token)
    print(format_current_playing(current_playing))

def logerr(msg):
    sys.stderr.write(msg + '\n')

def load_credentials():
    with open(get_credentials_filename(), 'r') as f:
        content = json.load(f)
    return content

def save_credentials(credentials):
    with open(get_credentials_filename(), 'w') as f:
        json.dump(credentials, f, sort_keys=False, indent=2)

def get_credentials_filename():
    return os.path.expanduser('~/.spotify.json')

def get_authorization_code(client_id):
    class AuthorizationHandler(BaseHTTPRequestHandler):
        last_code = None

        def do_GET(self):
            self.send_response(200, 'OK')
            self.end_headers()

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
        'scope': ' '.join([
            'user-read-currently-playing',
            'user-read-playback-state'
        ])
    }
    return 'https://accounts.spotify.com/authorize?' + urllib.urlencode(query)

def get_access_token(client_id, client_secret, code):
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode('%s:%s' % (client_id, client_secret)),
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    r = requests.post(url, data=payload, headers=headers)
    payload = r.json()
    return payload['access_token']

def get_current_playing(access_token):
    url = 'https://api.spotify.com/v1/me/player/currently-playing'
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    r = requests.get(url, headers=headers)
    return r.json()

def format_current_playing(playing_data):
    item = playing_data['item']
    artists = format_artists(item['artists'])
    album = item['album']
    return '%s [%s] - %s' % (artists, album['name'], item['name'])

def format_artists(artists):
    return ', '.join(map(lambda x: x['name'], artists))

if __name__ == '__main__':
    main()
