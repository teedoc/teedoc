import mistune
import re
from .renderer import Block_Quote_Renderer, Header_Renderer
from .renderer_math import MathRendererMixin

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


class MDRenderer(
                 # HighlightMixin,
                 MathRendererMixin,
                 TasklistRenderMixin,
                 Block_Quote_Renderer,
                 Header_Renderer,
                 mistune.Renderer):
    def __init__(self):
        mistune.Renderer.__init__(self, escape = False, hard_wrap = True)
