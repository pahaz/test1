import os
import re
import cgi
import random
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
IMAGE_PATTERN = """<a href="/static/{0}">
<img src="/static/{0}" class="related" /> </a>
"""

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
    GET = parse_http_get_data(environ)
    POST = parse_http_x_www_form_urlencoded_post_data(environ)

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

        POST = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=environ,
            keep_blank_values=True
        )

        status = '303 See Other'
        headers.append(('Location', '/'))
        name = POST['name'].value
        message = POST['message'].value
        fileitem = POST['file']

        message_text = MESSAGE_PATTERN.format(name, message)

        if fileitem.filename:
            extension = os.path.splitext(fileitem.filename)[1]
            filename = get_random_name(STATIC_ROOT, extension, 10)
            fullname = os.path.join(STATIC_ROOT, filename)

            with open(fullname, 'wb') as out:
                out.write(fileitem.file.read())

            print("\nFile saved to: " + fullname)

            if extension in ('.png', '.jpg', '.jpeg'):
                image_text = IMAGE_PATTERN.format(filename)
                message_text += image_text

        message_bytes = message_text.encode('utf-8')
        data_messages.append(message_bytes)
        start_response(status, headers)
        return [b'']

    messages = b'<hr>'.join(data_messages)
    template_bytes = template_bytes.replace(b'{{messages}}', messages)

    start_response(status, headers)
    return [template_bytes]


def get_random_name(dirname, extension, name_length):
    upper_border = int('9'*name_length)
    name = '{0:0>{name_length}}{extension}'

    filename = name.format(random.randint(0, upper_border), **locals())
    while os.path.isfile(os.path.join(dirname, filename)):
        filename = name.format(random.randint(0, upper_border), **locals())

    return filename
