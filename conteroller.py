from __future__ import unicode_literals, print_function, generators, division
import os
from manager import Manager
from model import Message
from utils import get_first_element
from view import View

__author__ = 'pahaz'

STATIC_ROOT = 'data/'

view = View('main.html')
manager = Manager('data.db')


def index(method, get, POST, headers):
    messages = manager.all()
    byte_messages = b'<hr>'.join([m.name.encode() + b" <br> Message: "
                                  + m.message.encode() for m in messages])
    status = '200 OK'
    body = view.render(messages=byte_messages)

    if method == 'POST':
        status = '303 See Other'
        body = b''
        headers.append(('Location', '/'))

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

        message_name = POST['name'].value
        message_message = POST['message'].value

        if message_name != '':
            message = Message(message_name, message_message)
            manager.save(message)

    return status, body
