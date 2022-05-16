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