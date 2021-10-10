#!python

import os, sys, shutil

plugin_dir = None
if len(sys.argv) > 1:
    plugin_dir = sys.argv[1]

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


