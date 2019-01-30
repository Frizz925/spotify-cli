from . import get_authorization_code, get_access_token, refresh_access_token, \
    get_current_playing, format_current_playing

import click
import json
import os
import sys

@click.command()
def main():
    credentials = load_credentials()
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
    if not 'access_token' in credentials:
        logerr('Access token not found. Opening browser for authorization.')
        code = get_authorization_code(client_id)
        access_token = get_access_token(client_id, client_secret, code)
        credentials['access_token'] = access_token
        save_credentials(credentials)
    else:
        access_token = credentials['access_token']
        new_access_token = refresh_access_token(client_id, client_secret, access_token)
        if new_access_token is not None:
            access_token = new_access_token
            credentials['access_token'] = access_token
            save_credentials(credentials)
    current_playing = get_current_playing(access_token)
    if current_playing is None:
        logerr('Not currently playing any track.')
        sys.exit(1)
    sys.stdout.write(format_current_playing(current_playing).encode('utf-8'))

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

if __name__ == '__main__':
    sys.exit(main())
