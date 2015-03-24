import os
import wsgiref.validate
import cgi
from router import Router

from utils import parse_http_x_www_form_urlencoded_post_data, \
    parse_http_get_data, parse_http_headers, \
    parse_http_content_type, parse_http_uri

DEBUG = True
STATIC_URL = '/static/'
STATIC_ROOT = 'data/'

data_messages = [
    b'Name: user<br>Message: hi!',
    b'Name: user<br>Message: hi!',
]


@wsgiref.validate.validator
def application(environ, start_response):
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


    if URI_PATH.startswith(STATIC_URL):
        URI_PATH = URI_PATH.replace(STATIC_URL, STATIC_ROOT)
        URI_PATH = os.path.normpath(URI_PATH)
        file = URI_PATH.split('\\')[-1]
        for dirpath, dirnames, filenames in os.walk(STATIC_ROOT):
            for filename in filenames:
                if filename == file:
                    with open(os.path.join(dirpath, filename), 'rb') as f:
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

    with open('main.html', 'rb') as f:
        template_bytes = f.read()

    if REQUEST_METHOD == 'POST':
        status = '303 See Other'
        headers.append(('Location', '/'))

        POST = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)

        fileItem = POST['file']
        if fileItem.filename:
            fullname = os.path.join(STATIC_ROOT, fileItem.filename)
            i = 0
            path = fileItem.filename
            while os.path.exists(fullname):  # Переименовываем если такой файл существует.
                path = str(i) + path
                fullname = os.path.join(STATIC_ROOT, path)
                i += 1

            with open(fullname, 'wb') as out:
                out.write(fileItem.file.read())
            print("File saved to: " + fullname)

        name = POST['name'].value
        message = POST['message'].value
        data_message_text = "Name: {0}<br>Message: {1}".format(name, message)
        data_message_bytes = data_message_text.encode('utf-8')
        data_messages.append(data_message_bytes)
        start_response(status, headers)
        return [b'']

    messages = b'<hr>'.join(data_messages)
    template_bytes = template_bytes.replace(b'{{messages}}', messages)

    start_response(status, headers)
    return [template_bytes]
