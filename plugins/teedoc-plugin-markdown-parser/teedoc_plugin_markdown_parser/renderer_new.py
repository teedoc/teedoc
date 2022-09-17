import mistune
import re
import mistune
import urllib.parse
# from pygments import highlight
# from pygments.lexers import get_lexer_by_name
# from pygments.formatters import html
import mistune
from mistune import InlineParser, BlockParser
from .plugin_tabset import Tabset
from .plugin_details import Details
from .plugin_subscript import plugin_subscript
from .plugin_superscript import plugin_superscript

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
        '''
            ## Header {#spec_id}
            <h2 id="spec_id">Header</h2>
        '''
        have_spec_id = re.compile(r'{#(.*?)}$')

        m = have_spec_id.search(text)
        if m is not None:
            _text = text[:m.span(0)[0]].strip()
            html = mistune.HTMLRenderer.heading(self, _text, level)
            _id = m.group(0).replace('{#','').replace('}','')
            escaped_id = _id
        else:
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

class MathBlockParser(BlockParser):
    """This acts as a pass-through to the MathInlineParser. It is needed in
    order to avoid other block level rules splitting math sections apart.
    """

    MULTILINE_MATH = re.compile(
        r"(?<!\\)[$]{2}.*?(?<!\\)[$]{2}|"
        r"\\\\\[.*?\\\\\]|"
        r"\\begin\{([a-z]*\*?)\}.*?\\end\{\1\}",
        re.DOTALL,
    )

    RULE_NAMES = ("multiline_math",) + BlockParser.RULE_NAMES

    # Regex for header that doesn't require space after '#'
    AXT_HEADING = re.compile(r" {0,3}(#{1,6})(?!#+)(?: *\n+|([^\n]*?)(?:\n+|\s+?#+\s*\n+))")

    def parse_multiline_math(self, m, state):
        """Pass token through mutiline math."""
        return {"type": "multiline_math", "text": m.group(0)}


def _dotall(pattern):
    """Make the '.' special character match any character inside the pattern, including a newline.
    This is implemented with the inline flag `(?s:...)` and is equivalent to using `re.DOTALL` when
    it is the only pattern used. It is necessary since `mistune>=2.0.0`, where the pattern is passed
    to the undocumented `re.Scanner`.
    """
    return f"(?s:{pattern})"


class MathInlineParser(InlineParser):
    r"""This interprets the content of LaTeX style math objects.
    In particular this grabs ``$$...$$``, ``\\[...\\]``, ``\\(...\\)``, ``$...$``,
    and ``\begin{foo}...\end{foo}`` styles for declaring mathematics. It strips
    delimiters from all these varieties, and extracts the type of environment
    in the last case (``foo`` in this example).
    """
    BLOCK_MATH_TEX = _dotall(r"(?<!\\)\$\$(.*?)(?<!\\)\$\$")
    BLOCK_MATH_LATEX = _dotall(r"(?<!\\)\\\\\[(.*?)(?<!\\)\\\\\]")
    INLINE_MATH_TEX = _dotall(r"(?<![$\\])\$(.+?)(?<![$\\])\$")
    INLINE_MATH_LATEX = _dotall(r"(?<!\\)\\\\\((.*?)(?<!\\)\\\\\)")
    LATEX_ENVIRONMENT = _dotall(r"\\begin\{([a-z]*\*?)\}(.*?)\\end\{\1\}")

    # The order is important here
    RULE_NAMES = (
        "block_math_tex",
        "block_math_latex",
        "inline_math_tex",
        "inline_math_latex",
        "latex_environment",
    ) + InlineParser.RULE_NAMES

    def parse_block_math_tex(self, m, state):
        # sometimes the Scanner keeps the final '$$', so we use the
        # full matched string and remove the math markers
        text = m.group(0)[2:-2]
        return "block_math", text

    def parse_block_math_latex(self, m, state):
        text = m.group(1)
        return "block_math", text

    def parse_inline_math_tex(self, m, state):
        text = m.group(1)
        return "inline_math", text

    def parse_inline_math_latex(self, m, state):
        text = m.group(1)
        return "inline_math", text

    def parse_latex_environment(self, m, state):
        name, text = m.group(1), m.group(2)
        return "latex_environment", name, text

class MarkdownWithMath(mistune.Markdown):
    def __init__(self, renderer, block=None, inline=None, plugins=None):
        if block is None:
            block = MathBlockParser()
        if inline is None:
            inline = MathInlineParser(renderer, hard_wrap=True)
        super().__init__(renderer, block, inline, plugins)

    def render(self, s):
        """Compatibility method with `mistune==0.8.4`."""
        return self.parse(s)

class MathRendererMixin:
        def multiline_math(self, text):
            return text

        def block_math(self, text):
            return f"$${mistune.util.escape_html(text)}$$"

        def latex_environment(self, name, text):
            name, text = mistune.util.escape_html(name), mistune.util.escape_html(text)
            return f"\\begin{{{name}}}{text}\\end{{{name}}}"

        def inline_math(self, text):
            return f"${mistune.util.escape_html(text)}$"


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
        # 'abbr',
        'strikethrough',
        'footnotes',
        'table',
        'url',
        'task_lists',
        'def_list',
        plugin_subscript,
        plugin_superscript,
        Tabset(),
        Details()
    ]
    _plugins = []
    for p in plugins:
        if isinstance(p, str):
            _plugins.append(mistune.PLUGINS[p])
        else:
            _plugins.append(p)
    plugins = _plugins
    renderer = MDRenderer()
    # parser = mistune.create_markdown(renderer=renderer, plugins=plugins, hard_wrap=True)
    parser = MarkdownWithMath(renderer=renderer, plugins=plugins)
    return parser

