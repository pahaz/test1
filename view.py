class View:
    def __init__(self, template_path):
        self._template_path = template_path
        with open(template_path, 'rb') as f:
            self._template_bytes = f.read()

    def render(self, **context):
        rendered = self._template_bytes
        for key, value in context.items():
            if isinstance(key, str):
                key = key.encode('utf-8')
            if isinstance(value, str):
                value = value.encode('utf-8')
            rendered = rendered.replace(b'{{' + key + b'}}', value)
        return rendered