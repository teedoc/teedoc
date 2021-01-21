import argparse
from logger import Logger
import os, sys
import json
import subprocess

def parse_site_config(doc_src_path):
    site_config_path = os.path.join(doc_src_path, "site_config.json")
    if not os.path.exists(site_config_path):
        return False, "can not find site config file: {}".format(site_config_path)
    with open(site_config_path) as f:
        try:
            site_config = json.load(f)
        except Exception as e:
            return False, "can not parse json file, json format error: {}".format(e)
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
        for plugin, path in site_config['plugins'].items():
            if not path or path.lower() == "pypi":
                log.i("install plugin <{}> from pypi.org".format(plugin))
            elif path.startswith("http") or path.startswith("git"):
                log.e("not support yet")
            else:
                path = os.path.abspath(os.path.join(doc_src_path, path))
                if not os.path.exists(path):
                    log.e("{} not found".format(path))
                    return 1
                cmd = "cd {} && pip install .".format(path)
                log.i("plugin path: {}".format(path))
                log.i("install by pip: {}".format(cmd))
                p = subprocess.Popen([cmd], shell=True)
                p.communicate()
                if p.returncode != 0:
                    log.e("install {} fail".format(plugin))
                    return 1
                log.i("install complete")
                
    else:
        log.e("command error")
        return 1
    return 0



if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
