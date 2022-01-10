import mistune
import urllib.parse

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
