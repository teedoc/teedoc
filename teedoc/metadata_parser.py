'''
    Parse the meta data of source file.
'''
import re
import yaml
import datetime
import os
import time

class Metadata_Parser:
    def __init__(self):
        self.re_meta_flag = re.compile("[-]{2}[-]$\n(.*?)\n[-]{3}(.*)", re.MULTILINE|re.DOTALL)

    def parse_meta(self, text, file=None):
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
        self.file = file
        meta_kvs = {
            "title": "",
            "desc": "",
            "keywords": [],
            "tags": [],
            "date": None, # None, False, datetime.date
            "update": [],
            "ts": 0,
            "author": "",
            "brief": "",
            "cover": "",
        }
        text = text.strip()
        if not text.startswith("---"):
            return self.parse_no_meta(meta_kvs, text)
        m = self.re_meta_flag.findall(text)
        if not m:
            return meta_kvs, text
        meta = yaml.load(m[0][0].strip(), Loader=yaml.Loader)
        meta_kvs.update(meta)
        meta_kvs = self.check_meta(meta_kvs)
        return meta_kvs, m[0][1].strip()

    def parse_no_meta(self, meta_kvs, text):
        '''
            parse the text without meta data,
            default parse markdown title.
            you can override this method to parse the text according to your own rules
        '''
        idx = text.find("\n")
        if idx > 0:
            if text.startswith("# "): # h1 header
                meta_kvs["title"] = text[2:idx]
                text = text[idx+1:].strip()
            elif text[idx+1:].startswith("==="): # h1 header
                idx2 = text[idx+1:].find("\n")
                if idx2 > 0:
                    meta_kvs["title"] = text[:idx]
                    text = text[ idx2 + idx + 1:].strip()
        return meta_kvs, text

    def check_meta(self, metadata):
        # keywords
        if type(metadata["keywords"]) != list:
            if not metadata["keywords"]:
                metadata["keywords"] = []
            elif type(metadata["keywords"]) == str:
                metadata["keywords"] = metadata["keywords"].split(",")
            else:
                raise Exception("keywords must be a list or a string split with ','")
        # tags
        if type(metadata["tags"]) != list:
            if type(metadata["tags"]) == str:
                metadata["tags"] = metadata["tags"].split(",")
            else:
                raise Exception("tags must be a list or a string split with ','")
        # date
        if len(metadata["update"]) > 0:
            metadata["update"] = sorted(metadata["update"], key=lambda x:x["date"], reverse=True)
            metadata["date"] = metadata["update"][0]["date"]
        if (type(metadata["date"]) == datetime.datetime or type(metadata["date"]) == datetime.date):
            date = metadata["date"]
            if type(date) == datetime.date:
                metadata["ts"] = int(time.mktime(date.timetuple()))
            else:
                metadata["ts"] = int(date.timestamp())
                metadata["date"] = datetime.datetime.date(date)
        elif not metadata["date"]:
            metadata["date"] = False
        elif self.file:
            metadata["ts"] = int(os.stat(self.file).st_mtime)
            metadata["date"] = datetime.datetime.date(datetime.datetime.fromtimestamp(metadata["ts"]))
        return metadata


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

