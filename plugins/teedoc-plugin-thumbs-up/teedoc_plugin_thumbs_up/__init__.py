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
from teedoc.utils import update_config
import copy
from .version import __version__


class Plugin(Plugin_Base):
    name = "teedoc-plugin-thumbs-up"
    desc = "thumbs up support for teedoc"
    defautl_config = {
        "label_up": "Helpful",
        "label_down": "Not Helpful",
        "icon": "/static/images/thumbs_up/up.svg",
        "icon_clicked": "/static/images/thumbs_up/upped.svg",
        "url": None,
        "show_up_count": True,
        "show_down_count": False,
        "msg_already_voted": "You have already voted",
        "msg_thanks": "Thanks for your vote",
        "msg_down_prompt": "Thanks to tell us where we can improve?(At least 10 characters)",
        "msg_down_prompt_error": "Message should be at least 10 characters and less than 256 characters",
        "msg_error": "Request server failed!"
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
        if not self.config["url"]:
            raise Exception("teedoc-plugin-thumbs-up: config.url is required")
        if self.config["url"].endswith("/"):
            self.config["url"] = self.config["url"][:-1]
        self.module_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        self.assets_abs_path = os.path.join(self.module_path, "assets")
        self.temp_dir = self.get_temp_dir()

        self.header_css = {
            "/static/js/thumbs_up/style.css": os.path.join(self.assets_abs_path, "style.css")
        }
        self.footer_js = {
            # don't use ad(advertisement) keyword, may blocked by browser plugin
            "/static/js/thumbs_up/main.js": os.path.join(self.assets_abs_path, "main.js")
        }
        self.images = self._get_all_img_assets("/static/images/thumbs_up", self.assets_abs_path)
        self.html_header_items = []
        self.html_footer_items = []
        for url in self.header_css:
            item = '<link rel="stylesheet" href="{}" type="text/css"/>'.format(url)
            self.html_header_items.append(item)
        for url in self.footer_js:
            item = '<script src="{}"></script>'.format(url)
            self.html_footer_items.append(item)
        vars = self.config
        self.header_css = self.update_file_var(self.header_css, vars, self.temp_dir)
        self.footer_js = self.update_file_var(self.footer_js, vars, self.temp_dir)
        self.files_to_copy = self.footer_js
        self.files_to_copy.update(self.header_css)
        self.files_to_copy.update(self.images)

    def _get_all_img_assets(self, to_url, from_dir):
        assets = {}
        names = os.listdir(from_dir)
        for name in names:
            ext = os.path.splitext(name)[1]
            if ext not in [".jpg", ".png", ".svg", ".icon"]:
                continue
            assets[f'{to_url}/{name}'] = os.path.join(from_dir, name)
        return assets

    def on_parse_start(self, type_name, url, dirs, doc_config, new_config):
        '''
            call when start parse one doc
            @type_name canbe "doc" "page" "blog"
            #url doc url, e.g. /get_started/zh/
            @doc_config config of doc, get from config.json or config.yaml
            @new_config this plugin's config from doc_config
        '''
        # can update plugin config from site_config with new_config by teedoc.utils.update_config
        self.new_config = copy.deepcopy(self.config)
        self.new_config = update_config(self.new_config, new_config)

    def on_add_html_header_items(self, type_name):
        return self.html_header_items

    def on_add_html_footer_js_items(self, type_name):
        return self.html_footer_items

    def on_copy_files(self):
        res = self.files_to_copy
        self.files_to_copy = {}
        return res

    def on_js_vars(self):
        return self.new_config


if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

