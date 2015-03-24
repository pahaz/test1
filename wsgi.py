import wsgiref.validate

from utils import parse_http_x_www_form_urlencoded_post_data, \
    get_first_element, parse_http_get_data, parse_http_headers, \
    parse_http_content_type, parse_http_uri, parse_http_multipart_form_data

DEBUG = True
STATIC_URL = '/static/'
STATIC_ROOT = 'data'

data_messages = []


@wsgiref.validate.validator
def application(environ, start_response):
    REQUEST_METHOD = environ['REQUEST_METHOD']
    CONTENT_TYPE, CONTENT_TYPE_KWARGS = parse_http_content_type(environ)
    SERVER_PROTOCOL = environ['SERVER_PROTOCOL']
    HEADERS = parse_http_headers(environ)
    URI_PATH = environ['PATH_INFO']
    URI_QUERY = environ['QUERY_STRING']
    URI = parse_http_uri(environ)
    POST = parse_http_multipart_form_data(environ)
    GET = parse_http_get_data(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]

    if URI_PATH.startswith(STATIC_URL):
        headers = [('Content-type', 'message/http; charset=utf-8')]
        with open(('data/' + URI_PATH[8:]).replace('../', ''), 'rb') as f:
            template_bytes = f.read()
        start_response(status, headers)
        return [template_bytes]
        

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
        filename = POST['filename']
        if(not name):
            name = 'anonimus'
        if(message):
            data_message_text = "Name: {0}<br>Message: {1}".format(name, message)
            data_message_bytes = data_message_text.encode('utf-8')
            data_messages.append(data_message_bytes)
        if(filename):
            with open('data/' + filename, 'wb') as file:
                file.write(POST['file'])
        start_response(status, headers)
        return [b'']

    messages = b'<hr>'.join(data_messages)
    template_bytes = template_bytes.replace(b'{{messages}}', messages)

    start_response(status, headers)
    return [template_bytes]
