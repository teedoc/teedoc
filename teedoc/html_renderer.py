from jinja2 import Environment, FileSystemLoader
import os

class Renderer:
    def __init__(self, path):
        self.path = path

    def __init__(self, template_path):
        self.env = Environment(
                loader=FileSystemLoader(os.path.dirname(template_path))
            )
        self.template = os.path.basename(template_path)

    def render(self, **kw_args):
        template = self.env.get_template(self.template)
        html = template.render(**kw_args)
        return html

