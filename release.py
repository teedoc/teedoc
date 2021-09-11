#!python

import os, sys, shutil

plugin_dir = None
if len(sys.argv) > 1:
    plugin_dir = sys.argv[1]

if not os.path.exists(os.path.join("teedoc", "template", "site_config.json")):
    print("[error] no init template submodule in {}".format(os.path.join("teedoc", "template")))
    print("please update submodule")
    sys.exit(1)

if os.path.exists(os.path.join("teedoc", "template", "out")):
    print("will delete build dir out in template")
    shutil.rmtree(os.path.join("teedoc", "template", "out"))
    print("delete build dir out in template complete")

if plugin_dir:
    os.chdir(plugin_dir)

if os.path.exists("dist"):
    print("delte dist dir")
    shutil.rmtree("dist")
    print("delte dist dir end")
if os.path.exists("build"):
    print("delte build dir")
    shutil.rmtree("build")
    print("delte build dir end")

os.system("python setup.py sdist bdist_wheel")
os.system("twine upload dist/*")


