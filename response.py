class Response:
    def __init__(self, status, body):
        self.status = status
        self.body = body
        self.headers = [('Content-type', 'text/html')]

default_responses = {
    403: Response('403 Forbidden', b'403 Forbidden'),
    404: Response('404 Not Found', b'404 Not Found')
}