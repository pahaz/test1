import os
import re
import cgi
import time
import random

from urllib.parse import parse_qs
from warnings import warn
from wsgiref.headers import Headers
from wsgiref.util import request_uri


def parse_http_get_data(environ):
    qs = environ.get("QUERY_STRING", "")
    if isinstance(qs, bytes):
        qs = qs.decode('utf-8')
    return parse_qs(qs)


def parse_http_x_www_form_urlencoded_post_data(environ):
    """
    Parse HTTP 'application/x-www-form-urlencoded' post data.
    """
    try:
        request_body_size = int(environ.get("CONTENT_LENGTH", 0))
    except ValueError:
        request_body_size = 0

    CONTENT_TYPE, CONTENT_TYPE_KWARGS = parse_http_content_type(environ)
    if CONTENT_TYPE != 'application/x-www-form-urlencoded':
        warn(" * WARNING * Used parse_http_x_www_form_urlencoded_post_data "
             "when CONTENT_TYPE != 'application/x-www-form-urlencoded'")
        return {}

    request_body_bytes = environ["wsgi.input"].read(request_body_size)
    request_body_text = request_body_bytes.decode('utf-8')
    body_query_dict = parse_qs(request_body_text)
    return body_query_dict


def parse_http_content_type(environ):
    return cgi.parse_header(environ.get('CONTENT_TYPE', ''))


def parse_http_headers(environ):
    h = Headers([])
    for k, v in environ.items():
        if k.startswith('HTTP_'):
            name = k[5:]
            h.add_header(name, v)
    return h


def parse_http_uri(environ):
    return request_uri(environ)


def get_first_element(dict_, key, default=None):
    """
    Take one value by key from dict or return None.
        >>> d = {"foo":[1,2,3], "baz":7}
        >>> get_first_element(d, "foo")
        1
        >>> get_first_element(d, "bar") is None
        True
        >>> get_first_element(d, "bar", "") == ""
        True
        >>> get_first_element(d, "baz")
        7
    """
    val = dict_.get(key, default)
    if type(val) in (list, tuple) and len(val) > 0:
        val = val[0]
    return val


def generate_name(dirname, extension):
    if not extension.startswith('.'):
        extension = '.' + extension

    def current_time_str():
        return str(round(time.time() * 1000))

    filename = current_time_str() + extension
    while os.path.isfile(os.path.join(dirname, filename)):
        filename = current_time_str() + extension

    return filename


def buffered(fileitem, block_size=1024):
    while True:
        block = fileitem.read(block_size)
        if not block:
            break
        yield block


def remove_html_tags(line):
    return re.sub(r'<[^>]*>', '', line)
