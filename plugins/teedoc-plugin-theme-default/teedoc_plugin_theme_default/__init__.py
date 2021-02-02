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
    name = "teedoc-plugin-theme-default"
    desc = "default theme for teedoc"
    defautl_config = {
        "light": True
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

        self.dark_css  = {
            "/static/css/theme_default/dark.css": os.path.join(self.assets_abs_path, "dark.css")
        }
        self.light_css = {
            "/static/css/theme_default/light.css": os.path.join(self.assets_abs_path, "light.css")
        }
        self.css = {
            "/static/css/theme_default/prism.min.css": os.path.join(self.assets_abs_path, "prism.min.css"),
        }
        # js files
        self.dark_js = {

        }
        self.light_js = {
        }
        self.header_js = {
            "/static/js/theme_default/jquery.min.js": os.path.join(self.assets_abs_path, "jquery.min.js"),
            "/static/js/theme_default/pre_main.js": os.path.join(self.assets_abs_path, "pre_main.js")
        }
        self.footer_js = {
            "/static/js/theme_default/main.js": os.path.join(self.assets_abs_path, "main.js"),
            "/static/css/theme_default/prism.min.js": os.path.join(self.assets_abs_path, "prism.min.js")
        }
        self.images = {
            "/static/image/theme_default/indicator.svg": os.path.join(self.assets_abs_path, "indicator.svg"),
            "/static/image/theme_default/menu.svg": os.path.join(self.assets_abs_path, "menu.svg"),
            "/static/image/theme_default/to-top.svg": os.path.join(self.assets_abs_path, "to-top.svg"),
            "/static/image/theme_default/light_mode.svg": os.path.join(self.assets_abs_path, "light_mode.svg"),
            "/static/image/theme_default/dark_mode.svg": os.path.join(self.assets_abs_path, "dark_mode.svg")
        }
        # set site_root_url env value
        if not "env" in config:
            config['env'] = {}
        config['env']["site_root_url"] = self.site_config["site_root_url"]
        # replace variable in css with value
        vars = config["env"]
        self.temp_dir = os.path.join(tempfile.gettempdir(), "teedoc_plugin_theme_default")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)
        self.dark_css  = self._update_file_var(self.dark_css, vars, self.temp_dir)
        self.light_css = self._update_file_var(self.light_css, vars, self.temp_dir)
        self.css       = self._update_file_var(self.css, vars, self.temp_dir)
        self.header_js = self._update_file_var(self.header_js, vars, self.temp_dir)
        # files to copy
        self.html_header_items = self._generate_html_header_items()
        self.files_to_copy = {}
        if self.config["dark"]:
            self.files_to_copy.update(self.dark_css)
            self.files_to_copy.update(self.dark_js)
        self.files_to_copy.update(self.light_css)
        self.files_to_copy.update(self.css)
        self.files_to_copy.update(self.light_js)
        self.files_to_copy.update(self.header_js)
        self.files_to_copy.update(self.footer_js)
        self.files_to_copy.update(self.images)
        if self.config["dark"]:
            self.themes_btn = '<a id="themes" class="light"></a>'
        else:
            self.themes_btn = ""

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
        if self.config["dark"]:
            for url in self.dark_css:
                item = '<link rel="stylesheet" href="{}" type="text/css"/>'.format(url)
                items.append(item)
        for url in self.light_css:
            item = '<link rel="stylesheet" href="{}" type="text/css"/>'.format(url)
            items.append(item)
        if "css" in self.config:
            item = '<link rel="stylesheet" href="{}" type="text/css"/>'.format(self.config["css"])
            items.append(item)
        # header_js
        for url in self.header_js:
            item = '<script src="{}"></script>'.format(url)
            items.append(item)
        if self.config["dark"]:
            for url in self.dark_js:
                item = '<script src="{}"></script>'.format(url)
                items.append(item)
        for url in self.light_js:
            item = '<script src="{}"></script>'.format(url)
            items.append(item)
        return items

    def _generate_html_js_items(self):
        items = []
        for url in self.footer_js:
            item = '<script src="{}"></script>'.format(url)
            items.append(item)
        if "js" in self.config:
            item = '<script src="{}"></script>'.format(self.config["js"])
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
        items = [self.themes_btn]
        return items
    
    def on_copy_files(self):
        return self.files_to_copy

if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

