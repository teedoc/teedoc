import os, sys
from collections import OrderedDict
import datetime
import json
try:
    curr_path = os.path.dirname(os.path.abspath(__file__))
    teedoc_project_path = os.path.abspath(os.path.join(curr_path, "..", "..", ".."))
    if os.path.basename(teedoc_project_path) == "teedoc":
        sys.path.insert(0, teedoc_project_path)
except Exception:
    pass
from teedoc import Plugin_Base
from teedoc import Fake_Logger
import tempfile
import time

__version__ = "2.10.4"

class Plugin(Plugin_Base):
    name = "teedoc-plugin-markdown-parser"
    desc = "markdown parser plugin for teedoc"
    defautl_config = {
        "parse_files": ["md"],
        "mermaid": True,
        "mermaid_use_cdn": False,
        "mermaid_cdn_url": "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js",
        "mathjax": {
            "enable": True,
            "file_name": "tex-mml-chtml", # http://docs.mathjax.org/en/latest/web/components/index.html
            "config": {
                "loader": {
                    "load": ['output/svg']
                },
                "tex": {
                    "inlineMath": [['$', '$'], ['\\(', '\\)']]
                },
                "svg": {
                    "fontCache": 'global'
                }
            }
        }
    }

    def on_init(self, config, doc_src_path, site_config, logger = None, multiprocess = True, **kw_args):
        '''
            @config a dict object
            @logger teedoc.logger.Logger object
        '''
        self.multiprocess = multiprocess
        self.logger = Fake_Logger() if not logger else logger
        self.doc_src_path = doc_src_path
        self.site_config = site_config
        self.config = Plugin.defautl_config
        mathjax_config = self.config["mathjax"]
        if "mathjax" in config:
            for k,v in config["mathjax"].items():
                if type(v) != dict:
                    mathjax_config[k] = v
                else:
                    mathjax_config[k].update(v)
        self.config.update(config)
        self.config["mathjax"] = mathjax_config
        self.logger.i("-- plugin <{}> init".format(self.name))
        self.logger.i("-- plugin <{}> config: {}".format(self.name, self.config))
        if not self.multiprocess:
            from .renderer import create_markdown_parser
            from teedoc.metadata_parser import Metadata_Parser
            self.create_markdown_parser = create_markdown_parser 
            self.Meta_Parser = Metadata_Parser
        self.assets_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.files_to_copy = {}
        if self.config["mermaid"]:
            self.files_to_copy[f'{self.name}/mermaid.min.js'] = os.path.join(self.assets_abs_path, "mermaid.min.js")

    def on_new_process_init(self):
        '''
            for multiple processing, for below func, will be called in new process,
            every time create a new process, this func will be invoke
        '''
        from .renderer import create_markdown_parser
        from teedoc.metadata_parser import Metadata_Parser
        self.md_parser = create_markdown_parser()
        self.meta_parser = Metadata_Parser()


    def on_new_process_del(self):
        '''
            for multiple processing, for below func, will be called in new process,
            every time exit a new process, this func will be invoke
        '''
        del self.md_parser
        del self.meta_parser

    def on_parse_files(self, files):
        # result, format must be this
        result = {
            "ok": False,
            "msg": "",
            "htmls": OrderedDict()
        }
        # function parse md file is disabled
        if not "md" in self.config["parse_files"]:
            result["msg"] = "disabled markdown parse, but only support markdown"
            return result
        self.logger.d("-- plugin <{}> parse {} files".format(self.name, len(files)))
        # self.logger.d("files: {}".format(files))

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext.endswith("md"):
                with open(file, encoding="utf-8") as f:
                    content = f.read().strip()
                    content = self._update_link(content)
                    try:
                        if not self.multiprocess:
                            md_parser = self.create_markdown_parser()
                            meta_parser = self.Meta_Parser()
                        else:
                            md_parser = self.md_parser
                            meta_parser = self.meta_parser
                        metadata, content_no_meta = meta_parser.parse_meta(content, file)
                        html = md_parser(content_no_meta)
                    except Exception as e:
                        self.logger.w("parse markdown file {} fail, please check markdown content format".format(file))
                        raise e
                    result["htmls"][file] = {
                        "title": metadata["title"],
                        "desc": metadata["desc"],
                        "keywords": metadata["keywords"],
                        "tags": metadata["tags"],
                        "body": html,
                        "date": metadata["date"],
                        "ts": metadata["ts"],
                        "author": metadata["author"],
                        # "toc": html.toc_html if html.toc_html else "",
                        "toc": "", # just empty, toc generated by js but not python
                        "metadata": metadata,
                        "raw": content
                    }
            else:
                result["htmls"][file] = None
        result['ok'] = True
        return result
    
    def on_parse_pages(self, files):
        result = self.on_parse_files(files)
        return result

    
    def on_add_html_header_items(self, type_name):
        items = []
        items.append('<meta name="markdown-generator" content="teedoc-plugin-markdown-parser">')
        if self.config["mathjax"]["enable"]:
            items.append('''<script>
MathJax = {};
</script>'''.format(json.dumps(self.config["mathjax"]["config"])))
            temp_dir = os.path.join(tempfile.gettempdir(), "teedoc_plugin_markdown_parser")
            os.makedirs(temp_dir, exist_ok=True)
            mathjax_js = os.path.join(temp_dir, f'{self.config["mathjax"]["file_name"]}.js')
            # items.append('<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>') # this feature will make page load slowly because bad network in China
            items.append('<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/{}.js"></script>'.format(self.config["mathjax"]["file_name"]))
            # url = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/{}.js'.format(self.config["mathjax"]["file_name"])
            # self.logger.i("Download file", url, "to", mathjax_js)
            # if not os.path.exists(mathjax_js):
            #     utils.download_file(url, mathjax_js)
            # item = {
            #     "path": mathjax_js,
            #     "options": ["async", 'id="MathJax-script"']
            # }
            # items.append(item)
        return items

    def on_add_html_footer_js_items(self, type_name):
        items = []
        if self.config["mermaid"]:
            if self.config["mermaid_use_cdn"]:
                items.append(f'<script src="{self.config["mermaid_cdn_url"]}"></script>')
            else:
                items.append(f'<script src="/{self.name}/mermaid.min.js"></script>')
            items.append('<script>mermaid.initialize({startOnLoad:true});</script>')
        return items

    def on_copy_files(self):
        res = self.files_to_copy
        self.files_to_copy = {}
        return res

    def _update_link(self, content):
        '''
            \[你好                              => \[你好
            [你好[hello]                        => [你好[hello]
            [你好]hello                         => [你好]hello
            [你好](a.md)                        => [你好](a.html)
            [你好](./a.md)                      => [你好](./a.html)
            [你好](./a.md                       => error
            \[你好\](./a.md)                    => \[你好\](./a.md)
            [[你好](a.md)](a.md)                => [[你好](a.html)](a.html)
            [[你好](https://a.com/a.md)](a.md)  => [[你好](https://a.com/a.md)](a.html)
            [[你好](a.md)](a(3).md)             => [[你好](a.html)](a(3).html)
            [[你好](a.md)](a[3].md)             => [[你好](a.html)](a[3].html)
            [[你好](a.md)](a[3](123).md)        => [[你好](a.html)](a[3](123).html)
            [[你好]]                            => [[你好]]
            [你好](README.md)                   => [你好](index.html)
            [你好](readme.md)                   => [你好](index.html)
        '''
        def is_abs_link(link):
            if link.startswith("/") or link.startswith("http"):
                return True
            start = link.split(":")[0]
            if start and start in ["ftp", "nfs", "smb", "file"]:
                return True
            return False

        def replace_ext(data, exts):
            final = ""
            flag_len = 2 # “](”
            while 1:
                # find [...]()
                idx = data.find("](")
                if idx < 0:
                    final += data
                    break
                elif idx > 0 and data[idx-1] == "\\": # \](
                    final += data[:idx + 1]
                    data = data[idx + 1:]
                    continue
                # find )
                sub = 0
                idx2 = idx
                for i, c in enumerate(data[idx + flag_len:]):
                    if c == "(":
                        sub += 1
                        continue
                    if c == "\n":
                        break
                    if c == ")":
                        sub -= 1
                        if sub < 0:
                            idx2 += i + flag_len
                            break
                if idx2 == idx: # not find valid []()
                    raise Exception('only have "[](", need ")" to close link')
                # ](....md )
                link = data[idx + flag_len: idx2].strip()
                if (not is_abs_link(link)):
                    for ext in exts:
                        if link.endswith(ext):
                            link = link[:-len(ext)] + "html"
                            break
                    if link.lower().endswith("readme.html"):
                        link = link[:-len("readme.html")] + "index.html"
                final += f'{data[:idx]}]({link})'
                data = data[idx2 + 1:]
            return final

        content = replace_ext(content, ["md", "ipynb"])
        return content

if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config, "", {})
    content = '''
\[你好
[你好[hello]
[你好]hello
[你好](a.md)
[你好](./a.md)
\[你好\](./a.md)
[[你好](a.md)](a.md)
[[你好](https://a.com/a.md)](a.md)
[[你好](a.md)](a(3).md)
[[你好](a.md)](a[3].md)
[[你好](a.md)](a[3](123).md)
[[你好]]                            => [[你好]]
[你好](README.md)                   => [你好](index.html)
[你好](readme.ipynb)                   => [你好](index.html)                   '''
    content = plug._update_link(content)
    print(content)

