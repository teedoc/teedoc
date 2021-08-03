import re


re_meta_flag = re.compile(r'---(.*?)\n---(.*)', re.MULTILINE|re.DOTALL)
re_meta = re.compile("(.*): (.*)")

def parse_meta(text):
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
        return meta_kvs, text
    m = re_meta_flag.match(text_strip)
    if not m:
        return meta_kvs, text
    meta = m[1].strip()
    meta = re_meta.findall(meta)
    if len(meta) == 0:
        return meta_kvs, text
    for k, v in meta:
        meta_kvs[k] = v

    return meta_kvs, m[2]

if __name__ == "__main__":
    import time
    with open("test.md") as f:
        content = f.read()
    t = time.time()
    for i in range(100):
        meta, pure_content = parse_meta(content)
    print(time.time() - t)
    print(meta, len(content), len(pure_content))

