import cgi
import os
import wsgiref.validate

from conteroller import index
from router import Router
from utils import parse_http_x_www_form_urlencoded_post_data, \
    parse_http_get_data, parse_http_headers, \
    parse_http_content_type, parse_http_uri


DEBUG = True
STATIC_URL = '/static/'
STATIC_ROOT = 'data/'

router = Router()
router.add_route('/', index)


@wsgiref.validate.validator
def application(environ, start_response):
    # https://www.python.org/dev/peps/pep-3333/#environ-variables
    REQUEST_METHOD = environ['REQUEST_METHOD']
    CONTENT_TYPE, CONTENT_TYPE_KWARGS = parse_http_content_type(environ)
    SERVER_PROTOCOL = environ['SERVER_PROTOCOL']
    HEADERS = parse_http_headers(environ)
    URI_PATH = environ['PATH_INFO']
    URI_QUERY = environ['QUERY_STRING']
    URI = parse_http_uri(environ)
    POST = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    GET = parse_http_get_data(environ)

    headers = [('Content-type', 'text/html; charset=utf-8')]

    controller_callback = router.resolve(URI_PATH)
    status, body = controller_callback(REQUEST_METHOD, GET, POST, headers)

    if URI_PATH.startswith(STATIC_URL):
        URI_PATH = URI_PATH.replace(STATIC_URL, STATIC_ROOT)
        URI_PATH = os.path.normpath(URI_PATH)
        if os.path.exists(URI_PATH):
            with open(URI_PATH, 'rb') as f:
                contentLogo = f.read()
            status = '200 OK'
            headers = [('Content-type', "application/octet-stream")]
            start_response(status, headers)
            return [contentLogo]

        status = '404 Not Found'
        start_response(status, headers)
        return [b'']

    if DEBUG:
        print("{REQUEST_METHOD} {URI_PATH}?{URI_QUERY} {SERVER_PROTOCOL}\n"
              "CONTENT_TYPE: {CONTENT_TYPE}; {CONTENT_TYPE_KWARGS}\n"
              "POST: {POST}\n"
              "GET: {GET}\n"
              ":HEADERS:\n{HEADERS}\n"
              .format(**locals()))

    start_response(status, headers)
    return [body]