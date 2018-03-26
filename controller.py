from __future__ import unicode_literals, print_function, generators, division
from manager import MessageManager
from model import Message
from utils import get_first_element
from view import View

__author__ = 'pahaz'


# ===========================
#
#    [mvC] 3.0 Controller
#
# ===========================


message_manager = MessageManager('data.db')


def index(method, get, post, headers):
    messages = message_manager.all()
    status = '200 OK'
    view = View('main.html')
    body = view.render(messages=messages)

    if method == 'POST':
        status = '303 See Other'
        body = b''

        headers.append(('Location', '/'))

        message_name = get_first_element(post, 'name', '')
        message_message = get_first_element(post, 'message', '')

        message = Message(message_name, message_message)
        message_manager.save(message)

    return status, body
