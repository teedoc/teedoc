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
    name = "teedoc-plugin-baidu-tongji"
    desc = "baidu tongji support for teedoc"
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
        
        # set site_root_url env value
        if not "code" in config:
            self.logger.e('can not find config["code"] in plugin {}'.format(self.name))
            return
        baidu_tongji_code = '''<script>
var _hmt = _hmt || [];
(function() {{
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?{}";
  var s = document.getElementsByTagName("script")[0]; 
  s.parentNode.insertBefore(hm, s);
}})();
</script>'''.format(config["code"])
        self.html_header_items = [baidu_tongji_code]


    def on_add_html_header_items(self):
        return self.html_header_items



if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

