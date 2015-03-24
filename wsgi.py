import wsgiref.validate
import os
import mimetypes

from utils import parse_http_x_www_form_urlencoded_post_data, \
    get_first_element, parse_http_get_data, parse_http_headers, \
    parse_http_content_type, parse_http_uri, get_file_path, get_file_contents

DEBUG = True
APPLICATION_BASE_DIR = r'D:\IT\Универ\PythonWeb\git\python_web_hw1'
STATIC_BASE_URI = '/static/'
STATIC_BASE_DIR = 'data/'

data_messages = [
    b'Name: user<br>Message: hi!',
    b'Name: user<br>Message: hi!',
]


def error_app(environ, start_response, error_code):
    statuses = {
        403: '403 Forbidden',
        404: '404 Not Found'
    }
    status = statuses.get(error_code, '500 Internal Server Error')
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    return [status.encode('utf-8')]


def static_app(environ, start_response):
    # print('STATIC FILE DETECTED!')
    URI_PATH = environ['PATH_INFO']
    requested_uri = os.path.join(STATIC_BASE_DIR, URI_PATH[len(STATIC_BASE_URI):])
    try:
        requested_path = get_file_path(requested_uri, STATIC_BASE_DIR)
        content = get_file_contents(requested_path)
    except IOError:
        return error_app(environ, start_response, 403)
    mime_type, encoding = mimetypes.guess_type(requested_path)
    status = '200 OK'
    headers = [('Content-type', mime_type or 'application/octet-stream')]
    if encoding:
        headers.append(('Content-encoding', encoding))
    start_response(status, headers)
    return [content]


def messages_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]

    if environ['REQUEST_METHOD'] == 'POST':
        post_data = parse_http_x_www_form_urlencoded_post_data(environ)
        name = get_first_element(post_data, 'name', '')
        message = get_first_element(post_data, 'message', '')
        data_message_text = "Name: {0}<br>Message: {1}".format(name, message)
        print(data_message_text)
        data_message_bytes = data_message_text.encode('utf-8')
        data_messages.append(data_message_bytes)

        status = '303 See Other'
        headers.append(('Location', '/'))
        start_response(status, headers)
        return [b'']

    with open('main.html', 'rb') as f:
        template_bytes = f.read()

    messages = b'<hr>'.join(data_messages)
    template_bytes = template_bytes.replace(b'{{messages}}', messages)

    start_response(status, headers)
    return [template_bytes]


@wsgiref.validate.validator
def application(environ, start_response):
    request_path = environ['PATH_INFO']
    if request_path.startswith(STATIC_BASE_URI):
        return static_app(environ, start_response)
    if request_path == '/':
        return messages_app(environ, start_response)
    return error_app(environ, start_response, 404)
