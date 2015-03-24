import wsgiref.validate
from tempfile import TemporaryFile
import cgi
import os

from utils import parse_http_x_www_form_urlencoded_post_data, \
    get_first_element, parse_http_get_data, parse_http_headers, \
    parse_http_content_type, parse_http_uri

DEBUG = True
STATIC_URL = '/static/'
STATIC_ROOT = 'data'

data_messages = [
    b'Name: user<br>Message: hi!',
    b'Name: user<br>Message: hi!',
]
#import wsgiref.util
#wsgiref.util.FileWrapper().filelike()

def read(environ):
    length = int(environ.get('CONTENT_LENGTH', 0))
    stream = environ['wsgi.input']
    body = TemporaryFile(mode='w+b')
    while length > 0:
        part = stream.read(min(length, 1024*200)) # 200KB buffer size
        if not part: break
        body.write(part)
        length -= len(part)
    body.seek(0)
    environ['wsgi.input'] = body
    return body

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

    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]

    if URI_PATH == '/favicon.ico':
        status = '404 Not Found'
        start_response(status, headers)
        return [b'']
    print(environ)
    if DEBUG:
        print("{REQUEST_METHOD} {URI_PATH}?{URI_QUERY} {SERVER_PROTOCOL}\n"
              "CONTENT_TYPE: {CONTENT_TYPE}; {CONTENT_TYPE_KWARGS}\n"
              "POST: {POST}\n"
              "GET: {GET}\n"
              ":HEADERS:\n{HEADERS}\n"
              .format(**locals()))

    if URI_PATH == "/upload":
        status = '303 See Other'
        headers.append(('Location', '/'))
        body = read(environ)
        form = cgi.FieldStorage(fp=body, environ=environ, keep_blank_values=True)
        try:
            fileitem = form['file']
        except KeyError:
            fileitem = None
        if fileitem is not None and fileitem.file is not None:
            fn = os.path.basename(fileitem.filename)
            with open("data/" + fn, 'wb') as f:
                data = fileitem.file.read(1024)
                while data:
                    f.write(data)
                    data = fileitem.file.read(1024)

        start_response(status, headers)
        return [b'']

    if URI_PATH.startswith(STATIC_URL):
        path = URI_PATH.split(STATIC_URL)[-1]
        if "../" in path:
            status = '404 Not Found'
            start_response(status, headers)
            return [b'']

        with open(STATIC_ROOT + "/" + path, 'rb') as f:
            start_response(status, [('Content-type', 'application/octet-stream; charset=utf-8')])
            return [f.read()]



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
