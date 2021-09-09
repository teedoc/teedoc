from genericpath import exists
import os, sys
from os.path import join
import tempfile
import shutil
import json
import copy
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

__version__ = "1.0.0"

class Plugin(Plugin_Base):
    name = "teedoc-plugin-google-translate"
    desc = "Google translate support for teedoc"
    defautl_config = {
    }

    def on_init(self, config, doc_src_path, site_config, logger = None):
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
        # self.module_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

    def on_del(self):
        pass

    # def on_parse_start(self, type_name, doc_config, new_config):
    #     self.doc_locale = doc_config["locale"] if "locale" in doc_config else None
    #     self.new_config = copy.deepcopy(self.config)
    #     self.new_config = update_config(self.new_config, new_config)

    def on_add_html_header_items(self, type_name):
        return []
    
    def on_add_html_footer_js_items(self, type_name):
        return [
            '''<script type="text/javascript">
                function googleTranslateElementInit() {
                    var html=document.getElementsByTagName("html")[0];
                    var lang = 'auto';
                    if(html.lang){
                        lang = html.lang;
                    }
                    new google.translate.TranslateElement({pageLanguage: lang, layout: google.translate.TranslateElement.InlineLayout.SIMPLE}, 'google_translate_element');
                }</script>
            ''',
            '<script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>'
        ]
    
    def on_add_navbar_items(self):
        trans_btn = '<a id="google_translate_element"></a>'
        items = [trans_btn]
        return items
    


if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

