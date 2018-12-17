#!/usr/bin/env python
from setuptools import setup


def read_requirements(filename):
    with open(filename, 'r') as f:
        reqs = f.read().splitlines()
    return reqs


setup(**{
    'name': 'Spotify CLI',
    'version': '1.0',
    'description': 'Access your Spotify data through CLI',
    'author': 'Izra Faturrahman',
    'author_email': 'Frizz925@hotmail.com',
    'entry_points': {
        'console_scripts': [
            'spotify-cli = spotify.cli:main'
        ]
    },
    'packages': ['spotify'],
    'install_requires': read_requirements('requirements.txt')
})
