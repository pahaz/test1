from __future__ import unicode_literals, print_function, generators, division

__author__ = 'pahaz'


class Router:
    def __init__(self):
        self._routs = {}

    def register_controller(self, url, controller):
        self._routs[url] = controller

    def resolve(self, url):
        callback = self._routs.get(url)
        # print('Tanya', callback, url, self._routs)
        if callback:
            return callback
        return self.default_controller

    def default_controller(self, *args, **kwargs):
        print("Jopka")
        status = '404 Not Found'
        body = b''
        return status, body
