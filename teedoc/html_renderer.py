from jinja2 import Environment, FileSystemLoader
import os

class Renderer:
    def __init__(self, template_name, search_paths):
        '''
            @template_name e.g. "base.html"
            @search_paths list type, start elements has high priority
        '''
        self.env = Environment(
                loader=FileSystemLoader(search_paths)
            )
        self.template = template_name

    def render(self, **kw_args):
        template = self.env.get_template(self.template)
        html = template.render(**kw_args)
        return html


