import mistune
from mistune import InlineLexer, BlockLexer
import re
try:
    from .renderer_math import MathInlineMixin, MathRendererMixin, MathBlockMixin
except Exception:
    from renderer_math import MathInlineMixin, MathRendererMixin, MathBlockMixin

import mistune
import urllib.parse
# from pygments import highlight
# from pygments.lexers import get_lexer_by_name
# from pygments.formatters import html

def link_in_this_site(link):
    if not "://" in link:
        return True
    return False

class Block_Quote_Renderer(mistune.Renderer):
    def block_quote(self, text):
        text = mistune.Renderer.block_quote(self, text)
        text = text.replace('<blockquote><p>!', '<blockquote class="spoiler warning"><p>')
        return text

    def autolink(self, link, is_email=False):
        link = mistune.escape_link(link)
        if is_email:
            link = 'mailto:%s' % link
        target = 'target="_blank"' if not link_in_this_site(link) else ''
        return f'<a href="{link}" {target}>{link}</a>'

    def link(self, link, title, content):
        link = mistune.escape_link(link)
        title = f'title="{title}"' if title else ''
        target = 'target="_blank"' if not link_in_this_site(link) else ''
        return f'<a href="{link}" {title} {target}>{content}</a>'

class Header_Renderer(mistune.Renderer):
    def header(self, text, level, raw = None):
        html = mistune.Renderer.header(self, text, level, raw)
        escaped_id = urllib.parse.quote(text.replace(' ', "-"))
        html = html.replace(f'<h{level}>', f'<h{level} id="{escaped_id}">')
        return html

class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre class="language-none"><code class="language-none">{}</code></pre>\n'.format(
                mistune.escape(code))
        if lang == "mermaid":
            return '\n<div class="mermaid">{}</div>\n'.format(mistune.escape(code))
        return '\n<pre class="language-{}"><code class="language-{}">{}</code></pre>\n'.format(
                lang, lang, mistune.escape(code))
        # lexer = get_lexer_by_name(lang, stripall=True)
        # formatter = html.HtmlFormatter()
        # return highlight(code, lexer, formatter)

class TasklistRenderMixin:

     def list_item(self, text):
         """render list item with task list support"""

         # list_item implementation in mistune.Renderer
         old_list_item = mistune.Renderer.list_item
         new_list_item = lambda _, text: '<li class="task-list-item">%s</li>\n' % text

         task_list_re = re.compile(r'\[[xX ]\] ')
         m = task_list_re.match(text)
         if m is None:
             return old_list_item(self, text)
         prefix = m.group()
         checked = False
         if prefix[1].lower() == 'x':
             checked = True
         if checked:
             checkbox = '<input type="checkbox" class="task-list-item-checkbox" checked disabled/> '
         else:
             checkbox = '<input type="checkbox" class="task-list-item-checkbox" disabled /> '
         return new_list_item(self, checkbox + text[m.end():])


class MathInlineLexer(MathInlineMixin, InlineLexer):
    def __init__(self, *args, **kwargs):
        super(MathInlineLexer, self).__init__(*args, **kwargs)
        self.enable_math()

class MathBlockLexer(MathBlockMixin, BlockLexer):
    def __init__(self, *args, **kwargs):
        BlockLexer.__init__(self, *args, **kwargs)
        self.enable_math()

class MDRenderer(
                 # HighlightMixin,
                 MathRendererMixin,
                 TasklistRenderMixin,
                 Block_Quote_Renderer,
                 Header_Renderer,
                 HighlightRenderer,
                 mistune.Renderer):
    def __init__(self):
        mistune.Renderer.__init__(self, escape = False, hard_wrap = True)

class MarkdownWithMath(mistune.Markdown):
    def __init__(self, renderer, **kwargs):
        if 'inline' not in kwargs:
            kwargs['inline'] = MathInlineLexer
        if 'block' not in kwargs:
            kwargs['block'] = MathBlockLexer
        super().__init__(renderer, **kwargs)

    def output_block_math(self):
        return self.inline(self.token["text"])

def create_markdown_parser():

    class MathRendrerer(MathRendererMixin, mistune.Renderer):
        def __init__(self, *args, **kwargs):
            super(MathRendrerer, self).__init__(*args, **kwargs)


    renderer = MDRenderer()
    # inline_lexer = MathInlineLexer(renderer)
    # block_lexer = MathBlockLexer() # FIXME: not work!!
    parser = MarkdownWithMath(renderer=renderer)
    return parser

if __name__ == "__main__":
    math_test = '''
假设 $z = f(u,v)$ 在点，求 $z$ 在 $t$ 点的导数。 $**hello**$
$$
**hello**{f[g(x)]}'=2[g(x)] \\times g'(x)=2[2x+1] \\times 2=8x+4
$$
    '''
#     math_test = '''
# $$
# **hello**{f[g(x)]}'=2[g(x)] \\times g'(x)=2[2x+1] \\times 2=8x+4
# $$
#     '''
    parser = create_markdown_parser()
    html = parser(math_test)
    print(html)
