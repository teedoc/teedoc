import re
import yaml

class Meta_Parser:
    def __init__(self):
        self.re_meta_flag = re.compile("[-]{2}[-]$\n(.*?)\n[-]{3}(.*)", re.MULTILINE|re.DOTALL)

    def parse_meta(self, text):
        """
            Parse the given text into metadata and strip it for a Markdown parser.
                metadata:
    ---
    title: markdown 语法
    tags: teedoc, markdown, 语法
    keywords: teedoc, markdown, 语法
    desc: teedoc 的 markdown 语法介绍和实例
    ---
            :param text: text to be parsed
        """
        meta_kvs = {}
        text_strip = text.strip()
        if not text_strip.startswith("---"):
            idx = text_strip.find("\n")
            if idx > 0:
                if text_strip.startswith("# "): # h1 header
                    meta_kvs["title"] = text_strip[2:idx]
                    text = text_strip[idx+1:].strip()
                elif text_strip[idx+1:].startswith("==="): # h1 header
                    idx2 = text_strip[idx+1:].find("\n")
                    if idx2 > 0:
                        meta_kvs["title"] = text_strip[:idx]
                        text = text_strip[ idx2 + idx + 1:].strip()
            return meta_kvs, text
        m = self.re_meta_flag.findall(text_strip)
        if not m:
            return meta_kvs, text
        meta_kvs = yaml.load(m[0][0].strip(), Loader=yaml.Loader)
        return meta_kvs, m[0][1]

if __name__ == "__main__":
    import time
    with open("md_files/basic.md") as f:
        content = f.read()
    parse = Meta_Parser()
    t = time.time()
    for i in range(100):
        meta, pure_content = parse.parse_meta(content)
    print(time.time() - t)
    print(meta, len(content), len(pure_content))

