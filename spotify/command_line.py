from spotify import get_authorization_code, get_access_token, get_current_playing, format_current_playing

import click
import json
import os
import sys

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
    if current_playing is None:
        logerr('Not currently playing any track.')
        sys.exit(1)
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

if __name__ == '__main__':
    sys.exit(main())