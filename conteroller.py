from __future__ import unicode_literals, print_function, generators, division
from manager import Manager
from model import Message
from utils import get_first_element
from view import View

__author__ = 'pahaz'

view = View('main.html')
manager = Manager('data.db')


def index(method, get, post, headers):
    messages = manager.all()
    byte_messages = b'<hr>'.join([m.name.encode() + b" <br> Message: "
                                  + m.message.encode() for m in messages])
    status = '200 OK'
    body = view.render(messages=byte_messages)

    if method == 'POST':
        status = '303 See Other'
        body = b''

        headers.append(('Location', '/'))

        message_name = get_first_element(post, 'name', '')
        message_message = get_first_element(post, 'message', '')

        message = Message(message_name, message_message)
        manager.save(message)

    return status, body


def add(method, get, post, headers):
    a = get_first_element(get, 'a', '')
    b = get_first_element(get, 'b', '')
    print(a, b)
    status = '200 OK'
    summ = int(a) + int(b)
    body = b'<p>' + str(summ).encode() + b'</p>'
    return status, body


# def static(method, get, post, headers):
#     headers[0] = ('Content-type', 'image/png; charset=utf-8')
#     status = '200 OK'
#     f = open('data/logo.png', 'rb')
#     body = f.read()
#     f.close()
#     return status, body