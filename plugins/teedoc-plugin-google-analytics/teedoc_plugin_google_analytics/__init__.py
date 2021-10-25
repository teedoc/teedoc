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

__version__ = "1.0.1"

class Plugin(Plugin_Base):
    name = "teedoc-plugin-google-analytics"
    desc = "google analytics support for teedoc"
    defautl_config = {
        "id": None
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
        self.html_header_items = []
        
        # set site_root_url env value
        if not "id" in config:
            self.logger.e('can not find config["id"] in plugin {}'.format(self.name))
            return
        code_raw = '''    <script async src="https://www.googletagmanager.com/gtag/js?id={}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
  
      gtag('config', '{}');
    </script>'''.format(config["id"], config["id"])
        self.html_header_items = [code_raw]


    def on_add_html_header_items(self, type_name):
        return self.html_header_items



if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

