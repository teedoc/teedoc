from genericpath import exists
import os, sys
import tempfile
import shutil
import markdown2
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
    name = "search"
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
        self.temp_dir = os.path.join(tempfile.gettempdir(), "teedoc_plugin_search")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)
        self.css       = self._update_file_var(self.css, vars, self.temp_dir)
        # files to copy
        self.html_header_items = self._generate_html_header_items()
        self.files_to_copy = {}
        self.files_to_copy.update(self.css)
        self.files_to_copy.update(self.footer_js)
        self.files_to_copy.update(self.images)
        self.search_btn = '<a id="search"><span class="icon"></span><span class="placeholder">Search</span></a>'

        self.html_js_items = self._generate_html_js_items()

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
    
    def on_add_navbar_items(self):
        items = [self.search_btn]
        return items
    
    def on_copy_files(self):
        return self.files_to_copy

if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

