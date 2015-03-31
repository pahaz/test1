from utils import parse_http_x_www_form_urlencoded_post_data, \
    parse_http_get_data, parse_http_headers, parse_http_content_type, parse_http_uri
import cgi

class Request:
    def __init__(self, environ):
        # https://www.python.org/dev/peps/pep-3333/#environ-variables
        self.REQUEST_METHOD = environ['REQUEST_METHOD']
        self.CONTENT_TYPE, self.CONTENT_TYPE_KWARGS = parse_http_content_type(environ)
        self.SERVER_PROTOCOL = environ['SERVER_PROTOCOL']
        self.HEADERS = parse_http_headers(environ)
        self.URI_PATH = environ['PATH_INFO']
        self.URI_QUERY = environ['QUERY_STRING']
        self.URI = parse_http_uri(environ)
        self.POST = parse_http_x_www_form_urlencoded_post_data(environ)
        self.GET = parse_http_get_data(environ)