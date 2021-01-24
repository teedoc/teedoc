import os, sys
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
    name = "theme-default"
    desc = "default theme for teedoc"
    defautl_config = {
        "light": True,
        "dark":  True
    }

    def __init__(self, config = {}, doc_src_path = ".", logger = None):
        '''
            @config a dict object
            @logger teedoc.logger.Logger object
        '''
        self.logger = Fake_Logger() if not logger else logger
        self.doc_src_path = doc_src_path
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
        self.dark_js = {

        }
        self.light_js = {
        }
        self.js = {
            "/static/js/theme_default/jquery.min.js": os.path.join(self.assets_abs_path, "jquery.min.js"),
            "/static/js/theme_default/main.js": os.path.join(self.assets_abs_path, "main.js")
        }
        self.images = {
            "/static/image/theme_default/indicator.svg": os.path.join(self.assets_abs_path, "indicator.svg")
        }
        self.html_header_items = self._generate_html_header_items()
        self.files_to_copy = {}
        if self.config["dark"]:
            self.files_to_copy.update(self.dark_css)
            self.files_to_copy.update(self.dark_js)
        if self.config["light"]:
            self.files_to_copy.update(self.light_css)
            self.files_to_copy.update(self.light_js)
        self.files_to_copy.update(self.js)
        self.files_to_copy.update(self.images)
        self.themes_btn = '<div class="themes"></div>'


    def _generate_html_header_items(self):
        items = []
        # css
        if self.config["dark"]:
            for url in self.dark_css:
                item = '<link rel="stylesheet" href="{}" type="text/css"/>'.format(url)
                items.append(item)
        if self.config["light"]:
            for url in self.light_css:
                item = '<link rel="stylesheet" href="{}" type="text/css"/>'.format(url)
                items.append(item)
        # js
        for url in self.js:
            item = '<script src="{}"></script>'.format(url)
            items.append(item)
        if self.config["dark"]:
            for url in self.dark_js:
                item = '<script src="{}"></script>'.format(url)
                items.append(item)
        if self.config["light"]:
            for url in self.light_js:
                item = '<script src="{}"></script>'.format(url)
                items.append(item)
        return items
        

    def on_add_html_header_items(self):
        return self.html_header_items
    
    def on_add_navbar_items(self):
        items = [self.themes_btn]
        return items
        # TODO:
        return []
    
    def on_copy_files(self):
        return self.files_to_copy

if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

