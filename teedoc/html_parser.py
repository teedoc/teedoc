import re
import os
import html2text

def extract_content_from_html(html):
    return html2text.html2text(html)

def generate_html_item_from_html_file(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        title = ""
        # find <h1> title from html
        match = re.findall(r"<h1.*?>(.*?)</h1>", html)
        if len(match) > 0:
            title = match[0]
        return {
            "title": title,
            "desc": "",
            "keywords": "",
            "tags": [],
            "body": html,
            "date": None,
            "ts": int(os.stat(html_path).st_mtime),
            "author": None,
            "toc": "",
            "metadata": {},
            "raw": extract_content_from_html(html)
        }
