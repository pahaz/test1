import os
import mimetypes
from view import View
from manager import Manager
from response import Response, default_responses
from model import Entry
from utils import get_first_element
import config
from utils import get_file_contents, get_file_path


home_view = View('home.html')
messages_view = View('messages.html')
upload_view = View('upload.html')
manager = Manager('data.db')


def static_controller(request):
    if config.DEBUG:
        print('Static file requested: {}'.format(request.URI_PATH))
    requested_uri = os.path.join(config.STATIC_BASE_DIR, request.URI_PATH[len(config.STATIC_BASE_URI):])
    try:
        requested_path = get_file_path(requested_uri, config.STATIC_BASE_DIR)
        content = get_file_contents(requested_path)
    except IOError:
        return default_responses[403]
    mime_type, encoding = mimetypes.guess_type(requested_path)
    status = '200 OK'
    headers = [('Content-type', mime_type or 'application/octet-stream')]
    if encoding:
        headers.append(('Content-encoding', encoding))
    response = Response(status, content)
    response.headers = headers
    return response


def home_controller(request):
    body = home_view.render()
    return Response('200 OK', body)


def messages_controller(request):
    if request.REQUEST_METHOD == 'POST':
        name = get_first_element(request.POST, 'name', '')
        message = get_first_element(request.POST, 'message', '')
        entry = Entry(name, message)
        manager.save(entry)

        response = Response('303 See Other', b'303 See Other')
        response.headers.append(('Location', '/messages'))
        return response

    entries = manager.get_all()
    entries_encoded = b'<hr />'.join(e.name.encode('utf-8') + b': ' + e.message.encode('utf-8')
                                     for e in entries)
    body = messages_view.render(messages=entries_encoded)
    return Response('200 OK', body)


def upload_controller(request):
    # TODO
    body = upload_view.render()
    return Response('200 OK', body)