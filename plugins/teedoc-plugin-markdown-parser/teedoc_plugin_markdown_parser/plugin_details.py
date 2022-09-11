'''
    details plugin for mistune
    usage:
        .. details::Title
            :open: true(optional)

            Full markdown supported content

    @author neucrack
    @license MIT
'''

from mistune.directives.base import Directive


class Details(Directive):
    def parse(self, block, m, state):
        options = self.parse_options(m)
        default_open = False
        for k,v in options:
            if k == "open":
                default_open = v.lower() == "true"
        title = m.group('value')
        text = self.parse_text(m)

        rules = list(block.rules)
        rules.remove('directive')
        children = block.parse(text, state, rules)
        return {
            'type': 'details',
            'children': children,
            'params': (title, default_open)
        }

    def __call__(self, md):
        '''
            generate html:
                <details>
                    <summary></summary>
                    <div class="details-content">
                </details>
        '''
        self.register_directive(md, 'details')

        if md.renderer.NAME == 'html':
            md.renderer.register('details', render_html_details)
        elif md.renderer.NAME == 'ast':
            md.renderer.register('tabset', render_ast_details)


def render_html_details(text, title="", open=False):
    '''
        <details open>
            <summary></summary>
            <div class="details-content">
        </details>
    '''
    html = f'<details{" open" if open else ""}>\n'
    if title:
        html += '<summary>' + title + '</summary>\n'
    if text:
        html += '<div class="details-content">' + text + '</div>\n'
    return html + '</details>\n'


def render_ast_details(children, title="", open=False):
    return {
        'type': 'details',
        'children': children,
        'title': title,
        'open': open
    }
