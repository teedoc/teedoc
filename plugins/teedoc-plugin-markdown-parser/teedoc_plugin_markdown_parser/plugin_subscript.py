
DEF_SUBSCRIPT = (
    # find subscript, e.g. H~2~O
    r'~'
    r'([\S]+?)'
    r'~(?!~)'
)

def parse_def_subscript(inline, m, state):
    text = m.group(1)
    return 'subscript', text

def render_html_subscript(text):
    return '<sub>' + text + '</sub>'


def render_ast_subscript(text):
    return {'type': 'subscript', 'text': text}

def plugin_subscript(md):
    md.inline.register_rule('subscript', DEF_SUBSCRIPT, parse_def_subscript)
    md.inline.rules.append('subscript')

    if md.renderer.NAME == 'html':
        md.renderer.register('subscript', render_html_subscript)
    elif md.renderer.NAME == 'ast':
        md.renderer.register('subscript', render_ast_subscript)

