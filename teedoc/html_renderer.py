from jinja2 import Environment, FileSystemLoader
import os
from babel.support import Translations, NullTranslations

class Renderer:
    def __init__(self, template_name, search_paths, log, html_templates_i18n_dirs = [], locale = None):
        '''
            @template_name e.g. "base.html"
            @search_paths list type, start elements has high priority
        '''
        self.log = log
        self.env = None
        if html_templates_i18n_dirs:
            if not locale:
                locale = "en"
            translations_merge = Translations.load(html_templates_i18n_dirs[0], [locale])
            if type(translations_merge) != NullTranslations:
                for dir in html_templates_i18n_dirs[1:]:
                    translations = Translations.load(dir, [locale])
                    if type(translations) != NullTranslations:
                        translations_merge.merge(translations)
            self.env = Environment(
                extensions=['jinja2.ext.i18n'],
                loader=FileSystemLoader(search_paths)
            )
            self.env.install_gettext_translations(translations_merge)
        if not self.env:
            self.env = Environment(
                    loader=FileSystemLoader(search_paths)
                )
        self.template = template_name

    def render(self, **kw_args):
        try:
            template = self.env.get_template(self.template)
            html = template.render(**kw_args)
        except Exception as e:
            self.log.e("render with template {} fail".format(self.template))
            raise e
        return html


