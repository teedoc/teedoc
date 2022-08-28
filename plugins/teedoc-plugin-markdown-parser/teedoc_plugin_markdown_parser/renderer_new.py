import mistune
from .renderer_math import MathRendererMixin
import re
import mistune
import urllib.parse
# from pygments import highlight
# from pygments.lexers import get_lexer_by_name
# from pygments.formatters import html
import mistune
from mistune import InlineParser, BlockParser
from .renderer_math import MathInlineMixin, MathRendererMixin, MathBlockMixin


def link_in_this_site(link):
    if not "://" in link:
        return True
    return False

class Block_Quote_Renderer(mistune.HTMLRenderer):
    def block_quote(self, text):
        text = mistune.HTMLRenderer.block_quote(self, text)
        text = text.replace('<blockquote>\n<p>!', '<blockquote class="spoiler warning">\n<p>')
        return text

    def autolink(self, link, is_email=False):
        link = mistune.util.escape_url(link)
        if is_email:
            link = 'mailto:%s' % link
        target = 'target="_blank"' if not link_in_this_site(link) else ''
        return f'<a href="{link}" {target}>{link}</a>'

    def link(self, link, text=None, title=None):
        if text is None:
            text = link
        link = mistune.util.escape_url(self._safe_url(link))
        title = f'title="{title}"' if title else ''
        target = 'target="_blank"' if not link_in_this_site(link) else ''
        return f'<a href="{link}" {title} {target}>{text}</a>'

class Header_Renderer(mistune.HTMLRenderer):
    def heading(self, text, level):
        html = mistune.HTMLRenderer.heading(self, text, level)
        escaped_id = urllib.parse.quote(text.replace(' ', "-"))
        html = html.replace(f'<h{level}>', f'<h{level} id="{escaped_id}">')
        return html

class HighlightRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info = None):
        if info is not None:
            info = info.strip()
        if not info:
            return '\n<pre class="language-none"><code class="language-none">{}</code></pre>\n'.format(
                mistune.escape(code))
        lang = info.split(None, 1)[0]
        lang = mistune.escape_html(lang)
        if info == "mermaid":
            return '\n<div class="mermaid">{}</div>\n'.format(mistune.escape(code))
        return '\n<pre class="language-{}"><code class="language-{}">{}</code></pre>\n'.format(
                lang, lang, mistune.escape(code))
        # lexer = get_lexer_by_name(lang, stripall=True)
        # formatter = html.HtmlFormatter()
        # return highlight(code, lexer, formatter)

class TasklistRenderMixin:

     def list_item(self, text, level):
         """render list item with task list support"""

         # list_item implementation in mistune.Renderer
         old_list_item = mistune.HTMLRenderer.list_item
         new_list_item = lambda _, text: '<li class="task-list-item">%s</li>\n' % text

         task_list_re = re.compile(r'\[[xX ]\] ')
         m = task_list_re.match(text)
         if m is None:
             return old_list_item(self, text, level)
         prefix = m.group()
         checked = False
         if prefix[1].lower() == 'x':
             checked = True
         if checked:
             checkbox = '<input type="checkbox" class="task-list-item-checkbox" checked disabled/> '
         else:
             checkbox = '<input type="checkbox" class="task-list-item-checkbox" disabled /> '
         return new_list_item(self, checkbox + text[m.end():])

class MathInlineLexer(MathInlineMixin, InlineParser):
    def __init__(self, *args, **kwargs):
        super(MathInlineLexer, self).__init__(*args, **kwargs)
        self.enable_math()

class MathBlockLexer(MathBlockMixin, BlockParser):
    def __init__(self, *args, **kwargs):
        BlockParser.__init__(self, *args, **kwargs)
        self.enable_math()

class MarkdownWithMath(mistune.Markdown):
    def __init__(self, renderer, **kwargs):
        if 'inline' not in kwargs:
            kwargs['inline'] = MathInlineLexer
        if 'block' not in kwargs:
            kwargs['block'] = MathBlockLexer
        super().__init__(renderer, **kwargs)

    def output_block_math(self):
        return self.inline(self.token["text"])

class MDRenderer(
                 MathRendererMixin,
                 TasklistRenderMixin,
                 Block_Quote_Renderer,
                 Header_Renderer,
                 HighlightRenderer,
                 mistune.HTMLRenderer):
    def __init__(self):
        mistune.HTMLRenderer.__init__(self, escape=False)

def create_markdown_parser():
    plugins = [
       # "abbr",
        'strikethrough',
        'footnotes',
        'table',
        'url',
        'task_lists',
        'def_list',
    ]
    _plugins = []
    for p in plugins:
        if isinstance(p, str):
            _plugins.append(mistune.PLUGINS[p])
        else:
            _plugins.append(p)
    plugins = _plugins
    renderer = MDRenderer()
    parser = MarkdownWithMath(renderer=renderer, plugins=plugins, inline = MathInlineLexer(renderer, hard_wrap = True))
    return parser

