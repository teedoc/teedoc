import mistune
import urllib.parse

class Block_Quote_Renderer(mistune.Renderer):
    def block_quote(self, text):
        text = mistune.Renderer.block_quote(self, text)
        text = text.replace('<blockquote><p>!', '<blockquote class="spoiler warning"><p>')
        return text

class Header_Renderer(mistune.Renderer):
    def header(self, text, level, raw = None):
        html = mistune.Renderer.header(self, text, level, raw)
        escaped_id = urllib.parse.quote(text.replace(' ', "-"))
        html = html.replace(f'<h{level}>', f'<h{level} id="{escaped_id}">')
        return html
