from setuptools import setup, find_packages
import os

curr_dir = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(curr_dir, "README.md")

with open(readme_path) as f:
     long_description = f.read()

install_requires = []
packages = find_packages()
print("packages:", packages)

setup(
    name='teedoc-plugin-theme-default',
    version="1.9.0",
    author='Neucrack',
    author_email='CZD666666@gmail.com',

    description='default theme for teedoc',
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
        'Programming Language :: Python :: 3'
    ],

    keywords='doc website markdown jupyter notbook generator teedoc theme',

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
        "teedoc_plugin_theme_default" : ['assets/*', 'templates/*'],
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
        # 'console_scripts': [
        # # 'gui_scripts': [
        #     'teedoc=teedoc-plugin-markdown-parser.main:main',
        # ],
    },
)