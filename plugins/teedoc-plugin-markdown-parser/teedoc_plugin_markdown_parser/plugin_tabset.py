'''
    tabset plugin for mistune
    usage:
        .. tabset::Title(optional)
            :id: id(optional)

            ## Label1

            Full markdown supported content

            # Label2

            Full markdown supported content

    @author neucrack
    @license MIT
'''

from mistune.directives.base import Directive

def parse_tabset_content(items):
    '''
        [{'type': 'heading', 'text': '标签一', 'params': (2,)}, {'type': 'paragraph', 'text': '内容一，可以使用 Markdown 语法'}, {'type': 'paragraph', 'text': '内容一，可以使用 Markdown 语法'}, {'type': 'heading', 'text': '
标签二', 'params': (2,)}, {'type': 'paragraph', 'text': '内容二，可以使用 Markdown 语法'}]
    '''
    new_items = [
        {
            "type": "tabset-tab",
            "children": []
        }, # tabs
        {
            "type": "tabset-text-container",
            "children": []
        } # tabs content text
    ]
    # find first h2
    tabs_count = -1
    for item in items:
        if item['type'] == 'heading' and item['params'][0] == 2:
            item['type'] = 'tabset-tab-label'
            item.pop('params')
            item["params"] = (tabs_count + 1,)
            new_items[0]["children"].append(item)
            new_items[1]["children"].append({
                "type": "tabset-text",
                "children": [],
                "params": (tabs_count + 1,)
            })
            tabs_count += 1
            continue
        new_items[1]["children"][tabs_count]["children"].append(item)
    return new_items

class Tabset(Directive):
    def parse(self, block, m, state):
        options = self.parse_options(m)
        tabset_id = None
        for k,v in options:
            if k == "id":
                tabset_id = v
        title = m.group('value')
        text = self.parse_text(m)

        rules = list(block.rules)
        rules.remove('directive')
        children = block.parse(text, state, rules)
        children = parse_tabset_content(children)
        return {
            'type': 'tabset',
            'children': children,
            'params': (title, tabset_id)
        }

    def __call__(self, md):
        '''
            generate html:
                <div class="tabset">
                    <div class="tabset-title">Title</div>
                    <div class="tabset-content">
                        <div class="tabset-tab">
                            <span class="tabset-tab-label>标签一</span>
                            <span class="tabset-tab-label>标签二</span>
                        </div>
                        <div class="tabset-text-container">
                            <div class="tabset-text">
                                <p>内容一，可以使用 Markdown 语法</p>
                                <p>内容一，可以使用 Markdown 语法</p>
                            </div>
                            <div class="tabset-text">
                                <p>内容二，可以使用 Markdown 语法</p>
                            </div>
                        </div>
                    </div>
                </div>
        '''
        self.register_directive(md, 'tabset')

        if md.renderer.NAME == 'html':
            md.renderer.register('tabset', render_html_tabset)
            md.renderer.register('tabset-tab', render_html_tab)
            md.renderer.register('tabset-tab-label', render_html_tab_label)
            md.renderer.register('tabset-text', render_html_tab_text)
            md.renderer.register('tabset-text-container', render_html_tab_text_container)
        elif md.renderer.NAME == 'ast':
            md.renderer.register('tabset', render_ast_tabset)
            md.renderer.register('tabset-tab', render_ast_tab)
            md.renderer.register('tabset-tab-label', render_ast_tab_label)
            md.renderer.register('tabset-text', render_ast_tab_text)
            md.renderer.register('tabset-text-container', render_ast_tab_text_container)

def render_html_tab_text_container(text):
    html = ''
    if text:
        html += '<div class="tabset-text-container">' + text + '</div>\n'
    return html

def render_html_tab_text(text, idx):
    html = ''
    if text:
        html += f'<div class="tabset-text {"tabset-text-active" if idx == 0 else ""}" idx={idx}>' + text + '</div>\n'
    return html

def render_html_tab(text):
    html = ''
    if text:
        html += '<div class="tabset-tab">' + text + '</div>\n'
    return html

def render_html_tab_label(text, idx):
    html = ''
    if text:
        html += f'<span class="tabset-tab-label {"tabset-tab-active" if idx == 0 else ""}" idx={idx}>' + text + '</span>\n'
    return html

def render_html_tabset(text, title="", id=None):
    html = f'<div class="tabset {"tabset-id-" + id if id else ""}">\n'
    if title:
        html += '<div class="tabset-title">' + title + '</div>\n'
    if text:
        html += '<div class="tabset-content">' + text + '</div>\n'
    return html + '</div>\n'


def render_ast_tabset(children, title="", id=None):
    return {
        'type': 'tabset',
        'children': children,
        'title': title,
        'id': id
    }

def render_ast_tab(children):
    return {
        'type': 'tabset-tab',
        'children': children
    }

def render_ast_tab_label(children, idx):
    return {
        'type': 'tabset-tab-label',
        'children': children,
        "idx": idx
    }

def render_ast_tab_text(children, idx):
    return {
        'type': 'tabset-text',
        'children': children,
        "idx": idx
    }

def render_ast_tab_text_container(children):
    return {
        'type': 'tabset-text-container',
        'children': children
    }
