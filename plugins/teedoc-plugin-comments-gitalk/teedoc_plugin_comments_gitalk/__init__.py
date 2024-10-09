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
from .version import __version__


class Plugin(Plugin_Base):
    name = "teedoc-plugin-comments-gitalk"
    desc = "gitalk comment support for teedoc"
    defautl_config = {
        "contrainer": "comments-container",
        "env":{
            "clientID": 'GitHub Application Client ID',
            "clientSecret": 'GitHub Application Client Secret',
            "repo": 'GitHub repo',
            "owner": 'GitHub repo owner',
            "admin": ['GitHub repo owner and collaborators, only these guys can initialize github issues'],
            "adminAutoCreate": False
            # "id": location.pathname,      // Ensure uniqueness and length less than 50
            # "distractionFreeMode": false  // Facebook-like distraction free mode
            # "main_color": "#4caf7d",
            # "second_color": "#0a7d43"
        },
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
        # check config
        for key in self.config["env"]:
            if not key in config["env"]:
                self.logger.e('you MUST set env var "{}" for gitalk plugin in site_config'.format(key))
        self.config.update(config)
        self.logger.i("-- plugin <{}> init".format(self.name))
        self.logger.i("-- plugin <{}> config: {}".format(self.name, self.config))
        self.assets_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

        self.files_to_copy = {
            "/static/js/gitalk/gitalk.min.js": os.path.join(self.assets_abs_path, "gitalk.min.js"),
            "/static/js/gitalk/main.js": os.path.join(self.assets_abs_path, "main.js"),
            "/static/css/gitalk/gitalk.css": os.path.join(self.assets_abs_path, "gitalk.css")
        }
        self.html_header_items = [
            '<link rel="stylesheet" href="{}" type="text/css"/>'.format("/static/css/gitalk/gitalk.css"),
        ]
        self.html_js_items = [
            '<script src="{}"></script>'.format("/static/js/gitalk/gitalk.min.js"),
            '<script src="{}"></script>'.format("/static/js/gitalk/main.js")
        ]

        self.temp_dir = os.path.join(tempfile.gettempdir(), "teedoc_plugin_comments_gitalk")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)
            
        # custom main color
        custom_color_vars = {}
        if "main_color" in self.config["env"]:
            self.logger.i("-- plugin <{}> get main_color {}".format(self.name, self.config["env"]["main_color"]))
            self.html_header_items.append('<link rel="stylesheet" href="{}" type="text/css"/>'.format("/static/css/gitalk/custom_gitalk.css"))
            self.files_to_copy["/static/css/gitalk/custom_gitalk.css"] = os.path.join(self.assets_abs_path, "custom_gitalk.css")
            # remove color vars from env, for env used by js
            if not "second_color" in self.config["env"]:
                self.config["env"]["second_color"] = self.config["env"]["main_color"]
            custom_color_vars["main_color"] = self.config["env"]["main_color"]
            custom_color_vars["second_color"] = self.config["env"]["second_color"]
            self.config["env"].pop("main_color")
            self.config["env"].pop("second_color")
        else:
            self.logger.i("-- plugin <{}> use default color")
        vars = {
            "comment_contrainer_id": self.config["contrainer"],
            "config": json.dumps(self.config["env"])
        }
        vars.update(custom_color_vars)
        self.files_to_copy  = self._update_file_var(self.files_to_copy, vars, self.temp_dir)


    def on_add_html_header_items(self, type_name):
        return self.html_header_items

    def on_add_html_footer_js_items(self, type_name):
        return self.html_js_items

    def on_copy_files(self):
        res = self.files_to_copy
        self.files_to_copy = {}
        return res

    def on_del(self):
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass

    def _update_file_var(self, files, vars, temp_dir):
        for url, path in files.items():
            with open(path, encoding='utf-8') as f:
                content = f.read()
                for k, v in vars.items():
                    content = content.replace("${}{}{}".format("{", k.strip(), "}"), str(v))
                temp_path = os.path.join(temp_dir, os.path.basename(path))
                with open(temp_path, "w", encoding='utf-8') as fw:
                    fw.write(content)
                files[url] = temp_path
        return files

if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)

