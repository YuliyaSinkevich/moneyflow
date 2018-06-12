#!/usr/bin/env python3

import constants as constants

import subprocess

# pybabel update -i messages.pot -d translations

if __name__ == '__main__':
    subprocess.call(['pybabel', 'update', '-i', 'messages.pot', '-d', 'translations'])
