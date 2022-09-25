
import os, sys
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
import tempfile, shutil, json
import time
import datetime

import mistune
mistune_version = mistune.__version__.split(".") # 0.8.4, 2.0.0rc1
mistune_version = int(mistune_version[0]) * 10 + int(mistune_version[1]) # 8, 20
local_plugin_path = os.path.join(teedoc_project_path, "plugins", "teedoc-plugin-markdown-parser")
if os.path.exists(local_plugin_path):
    sys.path.insert(0, local_plugin_path)
from teedoc.metadata_parser import Metadata_Parser
from teedoc_plugin_markdown_parser.renderer import create_markdown_parser


__version__ = "1.1.5"


class Plugin(Plugin_Base):
    name = "teedoc-plugin-blog"
    desc = "blog plugin for teedoc"
    defautl_config = {
        "parse_files": ["md"]
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
        self.config.update(config)
        self.logger.i("-- plugin <{}> init".format(self.name))
        self.logger.i("-- plugin <{}> config: {}".format(self.name, self.config))
        self.temp_dir = os.path.join(tempfile.gettempdir(), "teedoc_plugin_blog")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)
        self.assets_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.assets = {
            "/static/js/plugin_blog/main.js": os.path.join(self.assets_abs_path, "main.js"),
        }
        vars = {
            "site_root_url": self.site_config["site_root_url"]
        }
        self.assets = self._update_file_var(self.assets, vars, self.temp_dir)
        self.files_to_copy = self.assets.copy() # must use copy
        blog_url = list(self.site_config["route"]["blog"].keys())
        if len(blog_url) > 1:
            self.logger.e("only support one blog url path")
            raise Exception("only support one blog url path")
        self.blog_url = blog_url[0]
        self.blog_dir = os.path.join(self.doc_src_path, self.site_config["route"]["blog"][self.blog_url]).replace("\\", "/")
        self.index_content = {
            "items": {}
        }

    def on_new_process_init(self):
        '''
            for multiple processing, for below func, will be called in new process,
            every time create a new process, this func will be invoke
        '''
        self.md_parser = create_markdown_parser()
        self.meta_parser = Metadata_Parser()

    def on_new_process_del(self):
        '''
            for multiple processing, for below func, will be called in new process,
            every time exit a new process, this func will be invoke
        '''
        del self.md_parser
        del self.meta_parser

    def on_parse_blog(self, files):
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
                    blog_index_file_path = os.path.join(self.blog_dir, "readme.md").replace("\\", "/").lower()
                    is_blog_index = file.lower() == blog_index_file_path
                    if is_blog_index:
                        content += '\n<div id="blog_list"></div>'
                    if not self.multiprocess:
                        md_parser = create_markdown_parser()
                        meta_parser = Metadata_Parser()
                    else:
                        md_parser = self.md_parser
                        meta_parser = self.meta_parser
                    metadata, content_no_meta = meta_parser.parse_meta(content, file)
                    html = md_parser(content_no_meta)
                    if "<!-- more -->" in html:
                        brief = html[:html.find("<!-- more -->")].strip()
                    else:
                        brief = html[:500].strip()
                    parent_url = os.path.dirname(file.replace(self.doc_src_path, ""))
                    brief = self._update_relative_brief_links(brief, parent_url)
                    if metadata["cover"]:
                        metadata["cover"] = self._rel_to_abs_url(metadata["cover"], parent_url)
                        html = '<div class="blog_cover"><img src="{}" alt="{} cover"></div>'.format(metadata["cover"], metadata["title"]) + html
                    html_str = '<span id="blog_start"></span>' + html
                    result["htmls"][file] = {
                        "title": metadata["title"],
                        "desc": metadata["desc"],
                        "keywords": metadata["keywords"],
                        "tags": metadata["tags"],
                        "body": html_str,
                        # "toc": html.toc_html if html.toc_html else "",
                        "toc": "", # just empty, toc generated by js but not python
                        "metadata": metadata,
                        "raw": content,
                        "date": metadata["date"],
                        "ts": metadata["ts"],
                        "author": metadata["author"],
                        "brief": metadata["brief"],
                        "cover": metadata["cover"],
                    }
            else:
                result["htmls"][file] = None
        result['ok'] = True
        return result
    
    def on_add_html_header_items(self, type_name):
        items = []
        items.append('<meta name="blog-generator" content="teedoc-plugin-blog">')
        return items

    def _update_link(self, content):
        def re_del(c):
            ret = c[0]
            links = re.findall('\((.*?)\)', c[0])
            if len(links) > 0:
                for link in links:
                    if link.startswith(".") or os.path.isabs(link):
                        ret = re.sub("README.md", "index.html", c[0], flags=re.I)
                        ret = re.sub(r".md", ".html", ret, re.I)
                        return ret
            return ret
        def re_del_ipynb(c):
            ret = c[0]
            links = re.findall('\((.*?)\)', c[0])
            if len(links) > 0:
                for link in links:
                    if link.startswith(".") or os.path.isabs(link):
                        ret = re.sub("README.ipynb", "index.html", c[0], flags=re.I)
                        ret = re.sub(r".ipynb", ".html", ret, re.I)
                        return ret
            return ret
        # <a class="anchor-link" href="#&#38142;&#25509;"> </a></h2><p><a href="./syntax_markdown.md">markdown 语法</a>
        content = re.sub(r'\[.*?\]\(.*?\.md\)', re_del, content, flags=re.I)
        content = re.sub(r'\[.*?\]\(.*?\.ipynb\)', re_del_ipynb, content, flags=re.I)
        return content
    
    def on_htmls(self, htmls_files, htmls_pages, htmls_blog=None):
        '''
            update htmls, may not all html, just partially
            htmls_blog: {
                "/blog/":{
                    "url":{
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html,
                                "tags": [],
                                "url": "",
                                "raw": "",
                                "date": date,
                                "ts": 12344566,
                                "author": author,
                                "brief": "",
                                "metadata": {}
                          }
                }
            }
        '''
        if not htmls_blog:
            return True
        blog_url = list(htmls_blog.keys())
        if len(blog_url) == 0:
            return True
        index_url = ""
        blog_url = blog_url[0]
        index_url = "{}static/blog_index/index.json".format(self.site_config["site_root_url"])
        index_path = os.path.join(self.temp_dir, "index.json")
        for url, item in htmls_blog[blog_url].items():
            # except blog index.html
            if url == os.path.join(blog_url, "index.html"):
                continue
            new_item = {
                "title": item["title"],
                "desc": item["desc"],
                "keywords": item["keywords"],
                "tags": item["tags"],
                "url": url,
                "date": item["date"],
                "ts": item["ts"],
                "author": item["author"],
                "brief": item["brief"],
                "cover": item["cover"]
            }
            self.index_content["items"][url] = new_item
        # sort by date
        self.index_content["items"] = OrderedDict(sorted(self.index_content["items"].items(), key=lambda v: v[1]["ts"], reverse=True))
        #   write content to sub index file
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(self.index_content, f, ensure_ascii=False)

        # add to copy file list
        generated_index_json = {
            "/static/blog_index/index.json": index_path
        }
        self.files_to_copy.update(generated_index_json)
        return True

    def on_copy_files(self):
        res = self.files_to_copy
        self.files_to_copy = {}
        return res

    def on_add_html_footer_js_items(self, type_name):
        for url in self.assets:
            html_js_items = ['<script src="{}"></script>'.format(url)]
        return html_js_items
    
    def _update_file_var(self, files, vars, temp_dir):
        for url, path in files.items():
            with open(path, encoding='utf-8') as f:
                content = f.read()
                for k, v in vars.items():
                    content = content.replace("${}{}{}".format("{", k.strip(), "}"), v)
                temp_path = os.path.join(temp_dir, os.path.basename(path))
                with open(temp_path, "w", encoding='utf-8') as fw:
                    fw.write(content)
                files[url] = temp_path
        return files

    def _update_relative_brief_links(self, brief, parent_url):
        '''
            @brief html format brief
            @parent_url: parent url, e.g. /blog/category1
        '''
        def update_links(c, prefix):
            ret = c[0]
            links = re.findall('"(.*?)"', ret)
            if len(links) > 0:
                for link in links:
                    if not (link.startswith("http") or os.path.isabs(link)):
                        link = f'{parent_url}/{link}'.replace("/./", "/")
                        ret = f'{prefix}="{link}"'
                        return ret
            return ret

        def update_links_src(c):
            return update_links(c, "src")

        def update_links_href(c):
            return update_links(c, "href")

        brief = re.sub(r'src=".*?"', update_links_src, brief, flags=re.I)
        brief = re.sub(r'href=".*?"', update_links_href, brief, flags=re.I)
        return brief

    def _rel_to_abs_url(self, url, parent_url):
        '''
            @url: relative url, e.g. ./assets/snake.jpg
            @parent_url: parent url, e.g. /blog/category1
        '''
        if not (url.startswith("http") or os.path.isabs(url)):
            url = f'{parent_url}/{url}'.replace("/./", "/")
        return url

if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)
    res = plug.parse_files(["md_files/basic.md"])
    print(res)
    if not os.path.exists("out"):
        os.makedirs("out")
    for file, html in res["htmls"].items():
        if html:
            file = "{}.html".format(os.path.splitext(os.path.basename(file))[0])
            with open(os.path.join("out", file), "w") as f:
                f.write(html)

