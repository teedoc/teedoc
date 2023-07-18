from jinja2 import Environment, FileSystemLoader
import os
from babel.support import Translations, NullTranslations
import datetime
import json

def to_json_support_datetime(value, format="%Y-%m-%d", format_datetime = "%Y-%m-%d %H:%M:%S"):
    def update_datetime(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                obj[k] = update_datetime(v)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                obj[i] = update_datetime(v)
        elif isinstance(obj, tuple):
            obj = tuple(update_datetime(v) for v in obj)
        elif isinstance(obj, datetime.date):
            return obj.strftime(format)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime(format_datetime)
        return obj
    return json.dumps(update_datetime(value), ensure_ascii=False)

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
            self.env.filters["tojson2"] = to_json_support_datetime
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


