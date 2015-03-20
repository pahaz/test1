import os
import mimetypes

import wsgiref.validate

from utils import parse_http_x_www_form_urlencoded_post_data, \
    get_first_element, parse_http_get_data, parse_http_headers, \
    parse_http_content_type, parse_http_uri


CWD = os.path.dirname(os.path.abspath(__file__))

DEBUG = True
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(CWD, 'data')

MESSAGE_PATTERN = '<p class="name">{0}</p><p class="message">{1}</p>'

data_messages = [
    b'<p class="name">user</p><p class="message">hi!</p>',
    b'<p class="name">admin</p><p class="message">banhammer awaiting!</p>',
]


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

    if URI_PATH.startswith(STATIC_URL):
        print('STATIC FILE DETECTED!')

        file_path = URI_PATH.replace(STATIC_URL, '')
        full_path = os.path.join(STATIC_ROOT, file_path)
        normalized_path = os.path.normpath(full_path)

        try:
            if not normalized_path.startswith(STATIC_ROOT):
                raise IOError

            with open(normalized_path, 'rb') as f:
                content = f.read()
                mime_type = mimetypes.guess_type(normalized_path)[0]
        except:
            status = '404 Not Found'
            start_response(status, headers)
            return [b'']

        status = '200 OK'
        headers = [('Content-type', mime_type)]
        start_response(status, headers)
        return [content]

    if DEBUG:
        print("{REQUEST_METHOD} {URI_PATH}?{URI_QUERY} {SERVER_PROTOCOL}\n"
              "CONTENT_TYPE: {CONTENT_TYPE}; {CONTENT_TYPE_KWARGS}\n"
              "POST: {POST}\n"
              "GET: {GET}\n"
              ":HEADERS:\n{HEADERS}\n"
              .format(**locals()))

    with open('main.html', 'rb') as f:
        template_bytes = f.read()

    if REQUEST_METHOD == 'POST':
        status = '303 See Other'
        headers.append(('Location', '/'))
        name = get_first_element(POST, 'name', '')
        message = get_first_element(POST, 'message', '')
        data_message_text = MESSAGE_PATTERN.format(name, message)
        data_message_bytes = data_message_text.encode('utf-8')
        data_messages.append(data_message_bytes)
        start_response(status, headers)
        return [b'']

    messages = b'<hr>'.join(data_messages)
    template_bytes = template_bytes.replace(b'{{messages}}', messages)

    start_response(status, headers)
    return [template_bytes]
