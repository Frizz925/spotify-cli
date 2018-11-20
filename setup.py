#!/usr/bin/env python
from setuptools import setup

setup(name='Spotify CLI',
      version='1.0',
      description='Access your Spotify data through CLI',
      author='Izra Faturrahman',
      author_email='Frizz925@hotmail.com',
      scripts=['spotify/command_line.py'],
      packages=['spotify']
)