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
    name = "teedoc-plugin-assets"
    desc = "add assets(css js) support for teedoc"
    defautl_config = {
        "header_items": [],
        "footer_items": [],
        "env":{}
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

        self.files_to_copy = {}
        self.html_header_items = []
        self.html_footer_items = []
        for item in self.config["header_items"]:
            if item.startswith("/"):
                path = os.path.join(self.doc_src_path, item[1:])
                if os.path.exists(path):
                    if path.endswith(".js"):
                        self.html_header_items.append(f'<script src="{item}"></script>')
                        self.files_to_copy[item] = path
                    elif path.endswith(".css"):
                        self.html_header_items.append(f'<link rel="stylesheet" href="{item}" type="text/css"/>')
                        self.files_to_copy[item] = path
                    else:
                        self.logger.e(f"config: url {item} not support! you can use html tag instead")
                else:
                    self.logger.e(f"config: url {item} wrong, file {path} no found ")
            else:
                self.html_header_items.append(item)
        for item in self.config["footer_items"]:
            if item.startswith("/"):
                path = os.path.join(self.doc_src_path, item[1:])
                if os.path.exists(path):
                    if path.endswith(".js"):
                        self.html_footer_items.append(f'<script src="{item}"></script>')
                        self.files_to_copy[item] = path
                    elif path.endswith(".css"):
                        self.html_footer_items.append(f'<link rel="stylesheet" href="{item}" type="text/css"/>')
                        self.files_to_copy[item] = path
                    else:
                        self.logger.e(f"config: url {item} not support! you can use html tag instead")
                else:
                    self.logger.e(f"config: url {item} wrong, file {path} no found ")
            elif item.startswith("http"):
                if item.endswith(".js"):
                    self.html_footer_items.append(f'<script src="{item}"></script>')
                elif item.endswith(".css"):
                    self.html_footer_items.append(f'<link rel="stylesheet" href="{item}" type="text/css"/>')
                else:
                    self.logger.e(f"config: url {item} not support! you can use html tag instead")
            else:
                self.html_footer_items.append(item)

        self.temp_dir = os.path.join(tempfile.gettempdir(), "teedoc_plugin_assets")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)
            
        self.files_to_copy  = self._update_file_var(self.files_to_copy, self.config["env"], self.temp_dir)


    def on_add_html_header_items(self, type_name):
        return self.html_header_items

    def on_add_html_footer_js_items(self, type_name):
        return self.html_footer_items

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

