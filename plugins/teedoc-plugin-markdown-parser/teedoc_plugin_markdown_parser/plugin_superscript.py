
DEF_SUPERSCRIPT = (
    # find superscript, e.g. y=X^2^
    r'\^'
    r'([\S]+?)'
    r'\^(?!\^)'
)

def parse_def_subscript(inline, m, state):
    text = m.group(1)
    return 'superscript', text

def render_html_subscript(text):
    return '<sup>' + text + '</sup>'


def render_ast_subscript(text):
    return {'type': 'superscript', 'text': text}

def plugin_superscript(md):
    md.inline.register_rule('superscript', DEF_SUPERSCRIPT, parse_def_subscript)
    md.inline.rules.append('superscript')

    if md.renderer.NAME == 'html':
        md.renderer.register('superscript', render_html_subscript)
    elif md.renderer.NAME == 'ast':
        md.renderer.register('superscript', render_ast_subscript)

