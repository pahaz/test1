import response


class Router:
    def __init__(self):
        self._routes = {}

    def add_route(self, uri_prefix, controller):
        self._routes[uri_prefix] = controller

    def resolve(self, uri_path):
        for uri_prefix in self._routes:
            if uri_path.startswith(uri_prefix):
                return self._routes[uri_prefix]
        return self.default_callback

    @staticmethod
    def default_callback(request):
        return response.default_responses[404]