class View():
    def __init__(self, template_name):
        self.template_name = template_name
        with open(self.template_name, 'rb') as f:
            template_bytes = f.read()
        self._template = template_bytes

    def render(self, **context):
        rendered = self._template
        for k, v in context.items():
            if isinstance(v, str):
                rendered = rendered.replace(k.encode(), v)
        return rendered