#!/usr/bin/env python3

import constants as constants

import subprocess

# pybabel compile -d translations

if __name__ == '__main__':
    subprocess.call(['pybabel', 'compile', '-d', 'translations'])