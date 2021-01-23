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
    
    def on_add_html_header_items(self):
        return []
    
    def on_add_navbar_items(self):
        return []
    
    def on_copy_files(self):
        items = {}
        dark_assets = {
            "/static/css/default/dark.css": os.path.join(self.assets_abs_path, "dark.css")
        }
        light_assets = {
            "/static/css/default/light.css": os.path.join(self.assets_abs_path, "light.css")
        }
        if self.config["dark"]:
            items.update(dark_assets)
        if self.config["light"]:
            items.update(light_assets)
        return items

if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

