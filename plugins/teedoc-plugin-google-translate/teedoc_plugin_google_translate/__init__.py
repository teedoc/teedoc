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

__version__ = "1.1.4"

class Plugin(Plugin_Base):
    name = "teedoc-plugin-google-translate"
    desc = "Google translate support for teedoc"
    defautl_config = {
        "lang": "auto",  # source page language
        "doc_types": ["page", "doc", "blog"],
        "domain": "/"   # translate.google.com / translate.google.cn
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

    def on_del(self):
        pass

    def on_copy_files(self):
        res = {
            "/static/image/google_translate/translate.svg": os.path.join(self.assets_abs_path, "translate.svg"),
            "/static/image/google_translate/cleardot.gif": os.path.join(self.assets_abs_path, "cleardot.gif"),
            "/static/js/google_translate/main.js": os.path.join(self.assets_abs_path, "main.js"),
            "/static/js/google_translate/element_main.js": os.path.join(self.assets_abs_path, "element_main.js"),
            "/static/js/google_translate/element.js": os.path.join(self.assets_abs_path, "element.js"),
        }
        return res

    def on_parse_start(self, type_name, url, dirs, doc_config, new_config):
        # self.doc_locale = doc_config["locale"] if "locale" in doc_config else None
        self.new_config = copy.deepcopy(self.config)
        self.new_config = update_config(self.new_config, new_config)
        self.type_name = type_name

    def on_add_html_header_items(self, type_name):
        return [
        ]
    
    def on_add_html_footer_js_items(self, type_name):
        if not type_name in self.new_config["doc_types"]:
            return []
        lang = self.new_config["lang"]
        domain = self.new_config["domain"]
        return [
            '''<script type="text/javascript">
                var transLoaded = false;
                var loading = false;
                var domain = "''' + domain +'''";
                var domainDefault = domain;
                var storeDomain = localStorage.getItem("googleTransDomain");
                if(storeDomain){
                    domain = storeDomain;
                }
                function getUrl(domain){
                    if(domain == "/")
                        return "/static/js/google_translate/element.js?cb=googleTranslateElementInit";
                    else
                        return "https://" + domain + "/translate_a/element.js?cb=googleTranslateElementInit";
                }
                var url = getUrl(domain);
                function googleTranslateElementInit() {
                    new google.translate.TranslateElement({pageLanguage: "''' + lang + '''", layout: google.translate.TranslateElement.InlineLayout.SIMPLE}, 'google_translate_element');
                }
                function loadJS( url, callback ){
                    var script = document.createElement('script');
                    fn = callback || function(){ };
                    script.type = 'text/javascript';
                    if(script.readyState){
                        script.onreadystatechange = function(){
                            if( script.readyState == 'loaded' || script.readyState == 'complete' ){
                                script.onreadystatechange = null;
                                fn();
                            }
                        };
                    }else{
                        script.onload = function(){
                            fn();
                        };
                    }
                    script.src = url;
                    document.getElementsByTagName('head')[0].appendChild(script);
                }
                function removeHint(){
                    var hint = document.getElementById("loadingTranslate");
                    if(hint){
                        hint.remove();
                    }
                }
                var btn = document.getElementById("google_translate_element");
                btn.onclick = function(){
                    if(transLoaded) return;
                    if(loading){
                        var flag = confirm("loading from " + domain + ", please wait, or change domain?");
                        if(flag){
                            newDomain = prompt("domain, default: " + domainDefault + ", now: " + domain);
                            if(newDomain){
                                domain = newDomain;
                                console.log(domain);
                                url = getUrl(domain);
                                loadJS(url, function(){
                                    localStorage.setItem("googleTransDomain", domain);
                                    removeHint()
                                    transLoaded = true;
                                });
                            }
                        }
                        return;
                    }
                    btn.innerHTML = '<span id="loadingTranslate"><img class="icon" src="/static/image/google_translate/translate.svg"/>Loading ...</span>';
                    loading = true;
                    loadJS(url, function(){
                        localStorage.setItem("googleTransDomain", domain);
                        removeHint()
                        transLoaded = true;
                    });
                }
                </script>
            ''',
            # f'<script type="text/javascript" src="//{domain}/translate_a/element.js?cb=googleTranslateElementInit"></script>'
        ]
    
    def on_add_navbar_items(self):
        if not self.type_name in self.new_config["doc_types"]:
            return []
        trans_btn = '<a id="google_translate_element"><img class="icon" src="/static/image/google_translate/translate.svg"/>Translate</a>'
        items = [trans_btn]
        return items
    


if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

