from genericpath import exists
import os, sys
from os.path import join
import tempfile
import shutil
import markdown2
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



class Plugin(Plugin_Base):
    name = "teedoc-plugin-search"
    desc = "search support for teedoc"
    defautl_config = {
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
        self.assets_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.temp_dir = os.path.join(tempfile.gettempdir(), "teedoc_plugin_search")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)

        self.css = {
            "/static/css/search/style.css": os.path.join(self.assets_abs_path, "style.css"),
        }
        self.footer_js = {
            "/static/js/search/main.js": os.path.join(self.assets_abs_path, "main.js")
        }
        self.images = {
            "/static/image/search/close.svg": os.path.join(self.assets_abs_path, "close.svg"),
            "/static/image/search/search.svg": os.path.join(self.assets_abs_path, "search.svg"),
        }
        
        # set site_root_url env value
        if not "env" in config:
            config['env'] = {}
        config['env']["site_root_url"] = self.site_config["site_root_url"]
        # replace variable in css with value
        vars = config["env"]
        self.css       = self._update_file_var(self.css, vars, self.temp_dir)
        self.footer_js = self._update_file_var(self.footer_js, vars, self.temp_dir)
        # files to copy
        self.html_header_items = self._generate_html_header_items()
        self.files_to_copy = {}
        self.files_to_copy.update(self.css)
        self.files_to_copy.update(self.footer_js)
        self.files_to_copy.update(self.images)

        self.html_js_items = self._generate_html_js_items()
        self.content = {
            "articles": {},
            "pages": {}
        }

    def __del__(self):
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass

    def _generate_html_header_items(self):
        items = []
        # css
        for url in self.css:
            item = '<link rel="stylesheet" href="{}" type="text/css"/>'.format(url)
            items.append(item)
        return items

    def _generate_html_js_items(self):
        items = []
        for url in self.footer_js:
            item = '<script src="{}"></script>'.format(url)
            items.append(item)
        return items

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
        

    def on_add_html_header_items(self):
        return self.html_header_items
    
    def on_add_html_js_items(self):
        return self.html_js_items
    
    def on_add_navbar_items(self, new_config):
        '''
            @config config cover self.config
        '''
        search_hint = "Search"
        search_input_hint = "Keywords separated by space"
        search_loading_hint = "Loading, wait please ..."
        search_download_err_hint = "Download error, please check network and refresh again"
        search_other_docs_result_hint = "Result from other docs"
        search_curr_doc_result_hint = "Result from current doc"
        if "search_hint" in new_config:
            search_hint = new_config["search_hint"]
        elif "search_hint" in self.config:
            search_hint = self.config["search_hint"]
        if "input_hint" in new_config:
            search_input_hint = new_config["input_hint"]
        elif "input_hint" in self.config:
            search_input_hint = self.config["input_hint"]
        if "loading_hint" in new_config:
            search_loading_hint = new_config["loading_hint"]
        elif "loading_hint" in self.config:
            search_loading_hint = self.config["loading_hint"]
        if "download_err_hint" in new_config:
            search_download_err_hint = new_config["download_err_hint"]
        elif "download_err_hint" in self.config:
            search_download_err_hint = self.config["download_err_hint"]
        if "other_docs_result_hint" in new_config:
            search_other_docs_result_hint = new_config["other_docs_result_hint"]
        elif "other_docs_result_hint" in self.config:
            search_other_docs_result_hint = self.config["other_docs_result_hint"]
        if "curr_doc_result_hint" in new_config:
            search_curr_doc_result_hint = new_config["curr_doc_result_hint"]
        elif "curr_doc_result_hint" in self.config:
            search_curr_doc_result_hint = self.config["curr_doc_result_hint"] 
        search_btn = '''<a id="search"><span class="icon"></span><span class="placeholder">{}</span>
                            <div id="search_hints">
                                <span id="search_input_hint">{}</span>
                                <span id="search_loading_hint">{}</span>
                                <span id="search_download_err_hint">{}</span>
                                <span id="search_other_docs_result_hint">{}</span>
                                <span id="search_curr_doc_result_hint">{}</span>
                            </div></a>'''.format(
                        search_hint, search_input_hint, search_loading_hint, search_download_err_hint, search_other_docs_result_hint, search_curr_doc_result_hint)
        items = [search_btn]
        return items
    
    def on_copy_files(self):
        res = self.files_to_copy
        self.files_to_copy = {}
        return res

    def on_htmls(self, htmls_files, htmls_pages, htmls_blog=None):
        '''
            update htmls, may not all html, just partially
            htmls_files: {
                "/get_started/zh":{
                    "url":{
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html,
                                "url": "",
                                "raw": ""
                          }
                }
            }
        '''
        # for file, html in htmls_files.items():
        #     self.content["articles"][html["url"]] = html["raw"]
        # for file, html in htmls_pages.items():
        #     self.content["pages"][html["url"]] = html["raw"]
        docs_url = htmls_files.keys()
        pages_url = htmls_pages.keys()
        index_content = {}
        sub_index_path = []
        generated_index_json = {}
        for i, url in enumerate(docs_url):
            index_content[url] = "{}static/search_index/index_{}.json".format(self.site_config["site_root_url"], i)
            path = os.path.join(self.temp_dir, "index_{}.json".format(i))
            sub_index_path.append(path)
            #   write content to sub index file
            with open(path, "w", encoding="utf-8") as f:
                htmls_files[url]["body"] = "" # remove body, only use raw
                json.dump(htmls_files[url], f, ensure_ascii=False)
        for i, url in enumerate(pages_url, len(docs_url)):
            index_content[url] = "{}static/search_index/index_{}.json".format(self.site_config["site_root_url"], i)
            path = os.path.join(self.temp_dir, "index_{}.json".format(i))
            sub_index_path.append(path)
            #   write content to sub index file
            with open(path, "w", encoding="utf-8") as f:
                htmls_pages[url]["body"] = "" # remove body, only use raw
                json.dump(htmls_pages[url], f, ensure_ascii=False)
        # write content to files
        #   index file
        index_path = os.path.join(self.temp_dir, "index.json")
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_content, f, ensure_ascii=False)

        # add to copy file list
        generated_index_json["/static/search_index/index.json"] = index_path
        for i, path in enumerate(sub_index_path):
            generated_index_json["/static/search_index/index_{}.json".format(i)] = path
        self.files_to_copy.update(generated_index_json)
        return True
        



if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

