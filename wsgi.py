import wsgiref.validate

import mimetypes
import os.path

from conteroller import index, add
from router import Router
from utils import parse_http_x_www_form_urlencoded_post_data, \
    parse_http_get_data, parse_http_headers, \
    parse_http_content_type, parse_http_uri


DEBUG = True
STATIC_URL = '/static/'
STATIC_ROOT = 'data'

os.curdir
startdir = os.path.abspath(STATIC_ROOT)
# print(startdir)


router = Router()
router.register_controller('/', index)
router.register_controller('/add/', add)
# router.register_controller('/static/logo.png', logo)


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
    POST = parse_http_x_www_form_urlencoded_post_data(environ)
    GET = parse_http_get_data(environ)

    headers = [('Content-type', 'text/html; charset=utf-8')]

    controller_callback = router.resolve(URI_PATH)
    status, body = controller_callback(REQUEST_METHOD, GET, POST, headers)

    if URI_PATH.startswith(STATIC_URL):
        print('STATIC FILE DETECTED!')
        print(URI_PATH)
        file = str(URI_PATH).replace(STATIC_URL, "", 1)
        requested_path = os.path.join(startdir, file)
        requested_path = os.path.abspath(requested_path)
        print(requested_path)
        if not requested_path.startswith(startdir):
            raise OSError("Hack")
        headers[0] = ('Content-type', mimetypes.guess_type(URI_PATH, strict=True)[0]+'; charset=utf-8')
        try:
            f = open(requested_path, 'rb')
        except FileExistsError:
            status = '404 Not Found'
        status = '200 OK'
        body = f.read()
        f.close()


    # if DEBUG:
    #     print("{REQUEST_METHOD} {URI_PATH}?{URI_QUERY} {SERVER_PROTOCOL}\n"
    #           "CONTENT_TYPE: {CONTENT_TYPE}; {CONTENT_TYPE_KWARGS}\n"
    #           "POST: {POST}\n"
    #           "GET: {GET}\n"
    #           ":HEADERS:\n{HEADERS}\n"
    #           .format(**locals()))

    start_response(status, headers)
    return [body]
