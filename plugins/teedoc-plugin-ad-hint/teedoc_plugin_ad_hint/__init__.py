from genericpath import exists
import os, sys
from os.path import join
import tempfile
import shutil
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

__version__ = "1.0.6"

class Plugin(Plugin_Base):
    name = "teedoc-plugin-ad-hint"
    desc = "advertisement adn hint support for teedoc"
    defautl_config = {
        "type": "hint",     # new warning ad
        "label": "New",
        # "brief": "",
        "content": "",
        # "target": "_self",
        # "url": "#",
        "show_times": 2, # disapear after visit show_times pages, always show if <= 0
        "show_after_s": 60 * 60 * 24 * 5,  # show again after 5 days
        "color": "#a0421d",
        "link_color": "#e53935",
        "link_bg_color": "#e6ae5c",
        "bg_color": "#ffcf89",
        "color_hover": "white",
        "bg_color_hover": "#f57c00",
        "close_color": "#eab971"
    }

    def on_init(self, config, doc_src_path, site_config, logger = None, multiprocess = True, **kw_args):
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
        self.module_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        self.assets_abs_path = os.path.join(self.module_path, "assets")
        self.temp_dir = self.get_temp_dir()

        self.footer_js = {
            # don't use ad(advertisement) keyword, may blocked by browser plugin
            "/static/js/add_hint/style.css": os.path.join(self.assets_abs_path, "style.css"),
            "/static/js/add_hint/main.js": os.path.join(self.assets_abs_path, "main.js")
        }
        vars = self.config
        self.footer_js = self.update_file_var(self.footer_js, vars, self.temp_dir)
        self.files_to_copy = self.footer_js
        self.html_footer_items = []
        for url in self.footer_js:
            if url.endswith(".css"):
                item = '<link rel="stylesheet" href="{}" type="text/css"/>'.format(url)
            else:
                item = '<script src="{}"></script>'.format(url)
            self.html_footer_items.append(item)


    def on_add_html_footer_js_items(self, type_name):
        return self.html_footer_items

    def on_copy_files(self):
        res = self.files_to_copy
        self.files_to_copy = {}
        return res


if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

