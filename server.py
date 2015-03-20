#!/usr/bin/env python3

from wsgiref.simple_server import make_server
import wsgi

PORT = 8001

print("Open: http://127.0.0.1:{0}/".format(PORT))
httpd = make_server('', PORT, wsgi.application)
httpd.serve_forever()
