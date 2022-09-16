import shutil
from setuptools import setup, find_packages
import os
from teedoc import __version__
from glob import glob
import sys

print("generate locale files")
# os.system("cd teedoc && ./trans_prepare.sh && ./trans_finish.sh")
os.chdir("teedoc")
exec(open("trans_prepare.py").read())
exec(open("trans_finish.py").read())
os.chdir("..")
print("generate locale files complete")

curr_dir = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(curr_dir, "README.md")

with open(readme_path, encoding="utf-8") as f:
     long_description = f.read()

install_requires = [ "coloredlogs >= 15.0.1",
                     "mistune >=2.0.3,<3",
                     "watchdog >= 2.1.7",
                     "nbconvert >= 7.0.0",
                     "PyYaml >= 5.4.1",
                     "jinja2 >= 3.1.1",
                     "flask >= 2.0.2",
                     "babel >= 2.9.1",
                     "requests",
                     "progress",
                     "html2text"
                   ]
packages = find_packages()
print("packages:", packages)

def delete_out_dir(root, max_depth = 2, depth = 0):
    if depth >= max_depth:
        return
    dirs = os.listdir(root)
    for d in dirs:
        out_dir = os.path.join(root, d)
        if os.path.isdir(out_dir):
            if d == "out":
                print("-- remove out dir:", out_dir)
                shutil.rmtree(out_dir)
            else:
                delete_out_dir(out_dir, max_depth = max_depth, depth = depth + 1)

def check_submodule():
    if not os.path.exists(os.path.join("teedoc", "templates", "template", "site_config.json")):
        print("[!! error !!] template submodule in {} not init".format(os.path.join("teedoc", "templates", "template")))
        print("please update submodule")
        return False
    return True

def delete_build():
    if os.path.exists("dist"):
        print("delte dist dir")
        shutil.rmtree("dist")
        print("delte dist dir end")
    if os.path.exists("build"):
        print("delte build dir")
        shutil.rmtree("build")
        print("delte build dir end")

# remove out files first
delete_out_dir(os.path.join("teedoc", "templates"))
# check submodule
if not check_submodule():
    sys.exit(1)
# remove build files
delete_build()

os.chdir("teedoc")
tempalte_files = glob("templates/**", recursive=True)
package_data_files = ['static/js/*', "locales/*/*/*.?o", "templates/*"]
package_data_files.extend(tempalte_files)
print(package_data_files)
os.chdir("..")
setup(
    name='teedoc',
    version=__version__,
    author='Neucrack',
    author_email='CZD666666@gmail.com',

    description='doc site generator with multiple doc support',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Neutree/teedoc',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],

    keywords='doc website markdown jupyter notbook generator teedoc',

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=install_requires,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        # 'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=packages,

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        "teedoc" : package_data_files,
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[
        ],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
        # # 'gui_scripts': [
            'teedoc=teedoc.teedoc_main:main',
            'teedoc-list-files=teedoc.teedoc_list_files:main',
            "teedoc-compare=teedoc.teedoc_compare:main",
            "teedoc-upload=teedoc.teedoc_upload:main",
        ],
    },
)