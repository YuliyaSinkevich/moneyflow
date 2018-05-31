#!/usr/bin/env python3
from app import app
import argparse

HOST = '127.0.0.1'
PORT = 8080
PROJECT_NAME = 'moneyflow'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, usage='%(prog)s [options]')
    parser.add_argument('--port', help='port (default: {0})'.format(PORT), default=PORT)
    parser.add_argument('--host', help='host (default: {0})'.format(HOST), default=HOST)
    argv = parser.parse_args()

    app.run(host=argv.host, port=argv.port, debug=True)
