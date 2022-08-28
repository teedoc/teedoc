# coding: utf-8

"""
    mistune_contrib.math
    ~~~~~~~~~~~~~~~~~~~~
    Support Math features for mistune.
    :copyright: (c) 2014 by Hsiaoming Yang.
"""

import re
# from functools import partial
# try:
#     from html import escape
#     html_escape = partial(escape, quote=False)
# except ImportError:
#     # Python 2
#     from cgi import escape as html_escape
import mistune

class MathBlockMixin(object):
    """Math mixin for BlockLexer, mix this with BlockLexer::
        class MathBlockLexer(MathBlockMixin, BlockLexer):
            def __init__(self, *args, **kwargs):
                super(MathBlockLexer, self).__init__(*args, **kwargs)
                self.enable_math()
    """
    def enable_math(self):
        self.rules.block_math = re.compile(r"^\$\$.*?\$\$", re.DOTALL)
        self.rules.block_latex = re.compile(
            r'^\\begin\{([a-z]*\*?)\}(.*?)\\end\{\1\}', re.DOTALL
        )
        # self.default_rules.extend(['block_math', 'block_latex'])
        self.default_rules.insert(0, 'block_math')
        self.default_rules.insert(0, 'block_latex')

    def parse_block_math(self, m):
        """Parse a $$math$$ block"""
        self.tokens.append({
            'type': 'block_math',
            'text': m.group(0)
        })

    def parse_block_latex(self, m):
        self.tokens.append({
            'type': 'block_latex',
            'name': m.group(1),
            'text': m.group(2)
        })


class MathInlineMixin(object):
    """Math mixin for InlineLexer, mix this with InlineLexer::
        class MathInlineLexer(InlineLexer, MathInlineMixin):
            def __init__(self, *args, **kwargs):
                super(MathInlineLexer, self).__init__(*args, **kwargs)
                self.enable_math()
    """

    def enable_math(self):
        self.rules.math = re.compile(r"^\$(.+?)\$|^\\\\\((.+?)\\\\\)", re.DOTALL)
        self.default_rules.insert(0, 'math')
        # self.rules.text = re.compile(r'^[\s\S]+?(?=[\\<!\[_*`~\$]|https?://| {2,}\n|$)')

    def output_math(self, m):
        return self.renderer.math(m.group(1))

    def output_block_math(self, m):
        return self.renderer.block_math(m.group(1) or m.group(2) or "")

    def output_block_latex(self, m):
        return self.renderer.block_latex(m.group(1),
                                               m.group(2))


class MathRendererMixin(object):
    def block_math(self, text):
        return '$$%s$$' % mistune.util.escape_html(text)

    def block_latex(self, name, text):
        name = mistune.util.escape_html(name)
        return r'\begin{%s}%s\end{%s}' % (name, mistune.util.escape_html(text), name)

    def math(self, text):
        return '$%s$' % mistune.util.escape_html(text)

