from jinja2 import Environment, FileSystemLoader
import os
from babel.support import Translations

class Renderer:
    def __init__(self, template_name, search_paths, html_templates_i18n_dirs = [], lang = None):
        '''
            @template_name e.g. "base.html"
            @search_paths list type, start elements has high priority
        '''
        if html_templates_i18n_dirs:
            if not lang:
                lang = "en"
            self.env = Environment(
                extensions=['jinja2.ext.i18n'],
                loader=FileSystemLoader(search_paths)
            )
            translations_merge = Translations.load(html_templates_i18n_dirs[0], [lang])
            for dir in html_templates_i18n_dirs[1:]:
                translations = Translations.load(dir, [lang])
                translations_merge.merge(translations)
            self.env.install_gettext_translations(translations_merge)
        else:    
            self.env = Environment(
                    loader=FileSystemLoader(search_paths)
                )
        self.template = template_name

    def render(self, **kw_args):
        template = self.env.get_template(self.template)
        html = template.render(**kw_args)
        return html


