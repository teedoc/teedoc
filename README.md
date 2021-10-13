teedoc
===========

[中文](./README_ZH.md) | English

[![License](https://img.shields.io/github/license/teedoc/teedoc?color=red)](./LICENSE) [![PyPI](https://img.shields.io/pypi/v/teedoc)](https://pypi.org/project/teedoc/#history) ![PyPI - Downloads](https://img.shields.io/pypi/dm/teedoc?color=brightgreen) ![PyPI - Downloads](https://img.shields.io/pypi/dw/teedoc?color=brightgreen) [![build](https://github.com/teedoc/teedoc/actions/workflows/test.yml/badge.svg)](https://github.com/teedoc/teedoc/actions/workflows/test.yml) [![GitHub Repo stars](https://img.shields.io/github/stars/teedoc/teedoc?style=social)](https://github.com/teedoc/teedoc)

<img src="https://teedoc.github.io/static/image/logo.png" height=64/> 

Official site: [teedoc.neucrack.com](https://teedoc.neucrack.com) or [teedoc.github.io](https://teedoc.github.io/)

More demo: see [here](https://teedoc.neucrack.com/get_started/zh/usage/sites.html) or [here](https://teedoc.github.io/get_started/zh/usage/sites.html)

documentation generate tool from markdown and jupyter notebook to html

![](./assets/images/teedoc_screenshot_0.png)

`teedoc` can be used in the following scenarios:
* Build a document website, and it is best to support multiple documents and custom pages
* Organizations' or companies' docs spread in different domains, wish to combine them to one site(domain)
* Build a `WiKi` website
* Build personal or corporate knowledge base
* Build personal or corporate website


## Features

- [x] Easy to use, cross platform, only need `Python3`
- [x] Easy to deploy, only copy generated staitc HTML files to your server or other host
- [x] Easy to write, markdown support
- [x] Jupyter notebook support
- [x] Multiple docs support
- [x] Plugin support
- [x] Multiple theme support(support by plugin)
- [x] Control the style accurate to the page through css (implemented by customizing the id and class of each page)
- [x] Multi-level directory support
- [x] Multi-language support (manual translation) (Internationalization/i18n)
- [x] Multilingual support (translation plugin)
- [x] Multiple version support
- [x] Search support
- [x] SEO friendly
- [x] Real-time preview file changes
- [x] Parallel build, faster build speed
- [x] Blog support
- [x] Jinja2 HTML layout template support


## Get Started

Visit official site: [teedoc.github.io](https://teedoc.github.io/) or [teedoc.neucrack.com](https://teedoc.neucrack.com/)

## Create your website on github pages in minutes

See [template repo](https://github.com/teedoc/template)

## Quik start

* Install python3

On `Windows` or `macOS`, download from [python.org](https://www.python.org/downloads/)

On `Linux`, `Ubuntu` for example:

```
sudo apt install python3 python3-pip
```

* Install teedoc

This command will **install teedoc program**

```
pip3 install -U teedoc
```

* Initialize document

```
mkdir my_site
cd my_site
teedoc init
```

or

```
teedoc -d my_site init
```

> select minimal template in promot

* Install plugins

This command will **install plugins** used by doc(set in `site_config.json`)

```
cd my_site
teedoc install
```

* build or serve

```
teedoc serve
```

then visit [http://127.0.0.1:2333](http://127.0.0.1:2333) in browser

If you only want to generate htmls:

```
teedoc build
```

