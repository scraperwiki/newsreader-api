#!/usr/bin/python
#
# This starts a FastCGI server listening on the Unix socket SOCK.
#
# Derived from example at http://flask.pocoo.org/docs/deploying/fastcgi/

# See https://pypi.python.org/pypi/flup/1.0
from flup.server.fcgi import WSGIServer

from app import app

SOCK = '/var/run/newsreader/fcgi.sock'

if __name__ == '__main__':
    print("Running on {}".format(SOCK))
    WSGIServer(app, bindAddress=SOCK).run()

