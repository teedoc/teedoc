import os, sys
import markdown2
import re
from collections import OrderedDict
try:
    curr_path = os.path.dirname(os.path.abspath(__file__))
    teedoc_project_path = os.path.abspath(os.path.join(curr_path, "..", "..", ".."))
    if os.path.basename(teedoc_project_path) == "teedoc":
        sys.path.insert(0, teedoc_project_path)
except Exception:
    pass
from teedoc import Plugin_Base
from teedoc import Fake_Logger
try:
    from .jupyter_convert import convert_ipynb_to_html
except Exception:
    from jupyter_convert import convert_ipynb_to_html


class Plugin(Plugin_Base):
    name = "teedoc-plugin-jupyter-notebook-parser"
    desc = "jupyter notebook parser plugin for teedoc"
    defautl_config = {
        "parse_files": ["ipynb"]
    }

    def __init__(self, config, doc_src_path, site_config, logger = None):
        '''
            @config a dict object
            @logger teedoc.logger.Logger object
        '''
        self.logger = Fake_Logger() if not logger else logger
        self.doc_src_path = doc_src_path
        self.site_config = site_config
        self.config = Plugin.defautl_config
        self.config.update(config)
        self.logger.i("-- plugin <{}> init".format(self.name))
        self.logger.i("-- plugin <{}> config: {}".format(self.name, self.config))

        

    def on_parse_files(self, files):
        # result, format must be this
        result = {
            "ok": False,
            "msg": "",
            "htmls": OrderedDict()
        }
        # function parse md file is disabled
        if not "ipynb" in self.config["parse_files"]:
            result["msg"] = "disabled notebook parse, but only support notebook"
            return result
        self.logger.d("-- plugin <{}> parse {} files".format(self.name, len(files)))
        # self.logger.d("files: {}".format(files))
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext.endswith("ipynb"):
                # content = self._update_link(content)
                html = convert_ipynb_to_html(file)
                result["htmls"][file] = {
                    "title": html.title,
                    "desc": html.desc,
                    "keywords": html.keywords,
                    "tags": html.tags,
                    "body": html.body,
                    "toc": html.toc,
                    "metadata": html.metadata,
                    "raw": html.raw
                }
            else:
                result["htmls"][file] = None
        result['ok'] = True
        return result
    
    def on_parse_pages(self, files):
        result = self.on_parse_files(files)
        return result

    
    def on_add_html_header_items(self):
        items = []
        items.append('<meta name="html-generator" content="teedoc-plugin-jupyter-notebook-parser">')
        return items
    
    def _update_link(self, content):
        def re_del(c):
            ret = c[0].replace(".md", ".html") 
            ret = re.sub("README.md", "index.html", c[0], flags=re.I)
            ret = re.sub(r".md", ".html", ret, re.I)
            return ret

        content = re.sub(r'\[.*?\]\(.*?\.md\)', re_del, content, flags=re.I)
        return content

if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config, "./", {})
    res = plug.on_parse_files(["tests/test.ipynb"])
    if not os.path.exists("out"):
        os.makedirs("out")
    for file, html in res["htmls"].items():
        if html:
            file = "{}.html".format(os.path.splitext(os.path.basename(file))[0])
            with open(os.path.join("out", file), "w") as f:
                f.write(html['body'])

