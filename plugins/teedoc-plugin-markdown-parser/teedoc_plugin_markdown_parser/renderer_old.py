import mistune
from mistune import InlineLexer, BlockLexer
import re
try:
    from .renderer_base import Block_Quote_Renderer, Header_Renderer
    from .renderer_math import MathInlineMixin, MathRendererMixin, MathBlockMixin
except Exception:
    from renderer_base import Block_Quote_Renderer, Header_Renderer
    from renderer_math import MathInlineMixin, MathRendererMixin, MathBlockMixin

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
        super(MathBlockLexer, self).__init__(*args, **kwargs)
        self.enable_math()

class MDRenderer(
                 # HighlightMixin,
                 MathRendererMixin,
                 TasklistRenderMixin,
                 Block_Quote_Renderer,
                 Header_Renderer,
                 mistune.Renderer):
    def __init__(self):
        mistune.Renderer.__init__(self, escape = False, hard_wrap = True)

def create_markdown_parser():

    class MathRendrerer(MathRendererMixin, mistune.Renderer):
        def __init__(self, *args, **kwargs):
            super(MathRendrerer, self).__init__(*args, **kwargs)


    renderer = MDRenderer()
    inline_lexer = MathInlineLexer(renderer)
    block_lexer = MathBlockLexer() # FIXME: not work!!
    parser = mistune.Markdown(renderer=renderer, inline=inline_lexer) #, block=block_lexer)
    return parser

if __name__ == "__main__":
    math_test = '''
假设 $z = f(u,v)$ 在点，求 $z$ 在 $t$ 点的导数。 $**hello**$
$$
**hello**{f[g(x)]}'=2[g(x)] \times g'(x)=2[2x+1] \times 2=8x+4
$$
    '''
    parser = create_markdown_parser()
    html = parser(math_test)
    print(html)
