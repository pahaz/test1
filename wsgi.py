import wsgiref.validate
import cgi
import os.path as path

from utils import parse_http_x_www_form_urlencoded_post_data, \
    get_first_element, parse_http_get_data, parse_http_headers, \
    parse_http_content_type, parse_http_uri

DEBUG = True
STATIC_URL = '/static/'
STATIC_ROOT = 'data/'

MEDIA_ROOT = 'media/'
MEDIA_URL = '/upload/'

data_messages = [
    b'Name: user<br>Message: hi!',
    b'Name: user<br>Message: hi!',
]


@wsgiref.validate.validator
def application(environ, start_response):
    # https://www.python.org/dev/peps/pep-3333/#environ-variables

    URI_PATH = environ['PATH_INFO']
    URI_QUERY = environ['QUERY_STRING']
    SERVER_PROTOCOL = environ['SERVER_PROTOCOL']
    REQUEST_METHOD = environ['REQUEST_METHOD']

    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]

    if URI_PATH == '/favicon.ico':
        status = '404 Not Found'
        start_response(status, headers)
        return [b'']

    if URI_PATH.startswith(STATIC_URL):
        relative_path = URI_PATH.split(STATIC_URL)[-1]

        norm_path = path.normpath(relative_path)

        if REQUEST_METHOD == "GET":
            result_path = STATIC_ROOT + norm_path
            if not path.exists(result_path):
                start_response("404 Not found", headers)
                return [b'top kek']
            with open(result_path, 'rb') as f:
                headers = [('Content-type', 'application/octet-stream; charset=utf-8')]
                start_response(status, headers)
                return [f.read()]

    if URI_PATH.startswith(MEDIA_URL):
        relative_path = URI_PATH.split(MEDIA_URL)[-1]

        norm_path = path.normpath(relative_path)

        if REQUEST_METHOD == "GET":
            result_path = MEDIA_ROOT + norm_path
            if not path.exists(result_path):
                start_response("404 Not found", headers)
                return [b'top kek']
            with open(result_path, 'rb') as f:
                headers = [('Content-type', 'application/octet-stream; charset=utf-8')]
                start_response(status, headers)
                return [f.read()]


        if REQUEST_METHOD == "POST":
            form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
            with open(form['upload'].filename, 'wb') as f:
                data = form['upload'].value
                f.write(data)
            headers.append(('Location', '/'))
            status = '303 See Other'
            start_response(status, headers)
            return [b'']

    CONTENT_TYPE, CONTENT_TYPE_KWARGS = parse_http_content_type(environ)
    HEADERS = parse_http_headers(environ)
    URI = parse_http_uri(environ)
    POST = parse_http_x_www_form_urlencoded_post_data(environ)
    GET = parse_http_get_data(environ)

    if DEBUG:
        print("{REQUEST_METHOD} {URI_PATH}?{URI_QUERY} {SERVER_PROTOCOL}\n"
              "CONTENT_TYPE: {CONTENT_TYPE}; {CONTENT_TYPE_KWARGS}\n"
              "POST: {POST}\n"
              "GET: {GET}\n"
              ":HEADERS:\n{HEADERS}\n"
              .format(**locals()))

    if URI_PATH == '/':
        with open('main.html', 'rb') as f:
            template_bytes = f.read()

        if REQUEST_METHOD == 'POST':
            status = '303 See Other'
            headers.append(('Location', '/'))
            name = get_first_element(POST, 'name', '')
            message = get_first_element(POST, 'message', '')
            data_message_text = "Name: {0}<br>Message: {1}".format(name, message)
            data_message_bytes = data_message_text.encode('utf-8')
            data_messages.append(data_message_bytes)
            start_response(status, headers)
            return [b'']

        messages = b'<hr>'.join(data_messages)
        template_bytes = template_bytes.replace(b'{{messages}}', messages)

        start_response(status, headers)
        return [template_bytes]

    start_response('404 Not found', headers)
    return [b'Gavno mocha']
