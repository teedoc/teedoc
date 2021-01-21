import argparse
from logger import Logger
import os, sys
import json
import subprocess

def parse_site_config(doc_src_path):
    site_config_path = os.path.join(doc_src_path, "site_config.json")
    def check_site_config(site_config):
        if not "route" in site_config or \
           not "plugins" in site_config or \
           not "executable" in site_config:
           return False, "need route, plugins, executable keys, see example docs"
        return True, ""
    if not os.path.exists(site_config_path):
        return False, "can not find site config file: {}".format(site_config_path)
    with open(site_config_path) as f:
        try:
            site_config = json.load(f)
        except Exception as e:
            return False, "can not parse json file, json format error: {}".format(e)
    ok, msg = check_site_config(site_config)
    if not ok:
        return False, "check site_config.json fail: {}".format(msg)
    return True, site_config

def main():
    log = Logger(level="d")
    parser = argparse.ArgumentParser(description="teedoc, a doc generator, generate html from markdown and jupyter notebook")
    parser.add_argument("-p", "--path", default=".", help="doc source root path" )
    parser.add_argument("command", choices=["install", "build", "serve"])
    args = parser.parse_args()
    doc_src_path = os.path.abspath(args.path)
    # parse site config
    ok, site_config = parse_site_config(doc_src_path)
    if not ok:
        log.e(site_config)
        return 1
    # execute command
    if args.command == "install":
        log.i("install, source doc root path: {}".format(doc_src_path))
        log.i("plugins: {}".format(list(site_config["plugins"].keys())))
        curr_path = os.getcwd()
        for plugin, info in site_config['plugins'].items():
            path = info['from']
            # install from pypi.org
            if not path or path.lower() == "pypi":
                log.i("install plugin <{}> from pypi.org".format(plugin))
                cmd = [site_config["executable"]["pip"], "install", plugin]
                p = subprocess.Popen(cmd, shell=False)
                p.communicate()
                if p.returncode != 0:
                    log.e("install <{}> fail".format(plugin))
                    return 1
                log.i("install <{}> complete".format(plugin))
            # install from git like: git+https://github.com/Neutree/COMTool.git#egg=comtool
            elif path.startswith("svn") or path.startswith("git"):
                log.i("install plugin <{}> from {}".format(plugin, path))
                cmd = [site_config["executable"]["pip"], "install", "-e", path]
                log.i("install <{}> by pip: {}".format(plugin, " ".join(cmd)))
                p = subprocess.Popen(cmd, shell=False)
                p.communicate()
                if p.returncode != 0:
                    log.e("install <{}> fail".format(plugin))
                    return 1
                log.i("install <{}> complete".format(plugin))
            # install from local file system
            else:
                path = os.path.abspath(os.path.join(doc_src_path, path))
                if not os.path.exists(path):
                    log.e("{} not found".format(path))
                    return 1
                os.chdir(path)
                cmd = [site_config["executable"]["pip"], "install", "."]
                log.i("plugin path: {}".format(path))
                log.i("install <{}> by pip: {}".format(plugin, " ".join(cmd)))
                p = subprocess.Popen(cmd, shell=False)
                p.communicate()
                if p.returncode != 0:
                    log.e("install <{}> fail".format(plugin))
                    return 1
                log.i("install <{}> complete".format(plugin))
        os.chdir(curr_path)
        log.i("all plugins install complete")
    elif args.command == "build":
        # init plugins
        plugins = list(site_config['plugins'].keys())
        plugins_objs = []
        log.i("plugins: {}".format(plugins))
        for plugin, info in site_config['plugins'].items():
            try:
                plugin_config = info['config']
            except Exception:
                plugin_config = {}
            plugin_import_name = plugin.replace("-", "_")
            module = __import__(plugin_import_name)
            plugin_obj = module.Plugin(doc_src_path=doc_src_path, config=plugin_config, logger=log)
            plugins_objs.append(plugin_obj)
        for plugin_obj in plugins_objs:
            plugin_obj.build()
        
    else:
        log.e("command error")
        return 1
    return 0



if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
