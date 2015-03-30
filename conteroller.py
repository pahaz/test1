from __future__ import unicode_literals, print_function, generators, division
import cgi
import os
from manager import Manager
from model import Message
from utils import get_first_element
from view import View

__author__ = 'pahaz'

view = View('main.html')
manager = Manager('data.db')

STATIC_ROOT = 'data/'


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

        fileItem = post['file']
        if fileItem.filename:
            fullPath = os.path.join(STATIC_ROOT, fileItem.filename)
            i = 0
            while os.path.exists(fullPath):
                fullPath = os.path.join(STATIC_ROOT, "(" + str(i) + ")" + fileItem.filename)
                i += 1
            with open(fullPath, "wb") as out:
                out.write(fileItem.file.read())

        message_name = post['name'].value
        message_message = post['message'].value

        if message_name != "" or message_message != "":
            message = Message(message_name, message_message)
            manager.save(message)

    return status, body
