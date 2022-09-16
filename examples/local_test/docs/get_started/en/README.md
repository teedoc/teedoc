---
title: Hello
date: 2022-09-03
update:
  - date: 2022-09-15
    version: 1.2.0
    author: xxx
    content:
      - 修复了错误BBB
      - 优化了内容CCC，参考<a>aaa</a>
  - date: 2022-09-08
    version: 1.1.0
    author: UUU
    content: 修复了错误AAA
---

Official website: [teedoc.neucrack.com](https://teedoc.neucrack.com/) or [teedoc.github.io](https://teedoc.github.io/)
Source file of this document: [github.com/teedoc/teedoc.github.io](https://github.com/teedoc/teedoc.github.io)
Source code: [https://github.com/teedoc/teedoc](https://github.com/teedoc/teedoc) Welcome star

Convert documents in `Markdown` or `Jupyter Notebook` format into `HTML` static web pages

`teedoc` can be used in the following scenarios:
* Build a document website, and it’s best to support multiple documents and custom pages
* Build a `WiKi` website
* Build a personal or corporate knowledge base
* Build a personal or corporate website
* Blog

If you encounter problems during use, you can find similar problems in [here](https://github.com/teedoc/teedoc/issues) (you need to register and log in to github) to find similar issues, or create an issue


## Features

- [x] Simple to use, cross-platform, only dependent on `Python3`
- [x] No database required, all static pages of the website
- [x] The deployment is simple, the generated website is a fully static page, which can be directly copied to the server or uploaded to a third party organization for deployment
- [x] Easy to write, using Markdown syntax
- [x] Jupyter notebook support
- [x] HTML support, you can directly use HTML to write pages, with great freedom
- [x] Multi-document support
- [x] Plug-in support
- [x] Multi-theme support (implemented by plug-in)
- [x] Control the style accurate to the page through css (implemented by customizing the id and class of each page)
- [x] Multi-level directory support(infinite levels)
- [x] Multi-language support (manual translation) (Internationalization/i18n)
- [ ] Multilingual support (automatic translation)
- [x] Multi-version support (implementation method is the same as multi-language)
- [x] Search support
- [x] SEO friendly
- [x] Real-time preview of changes
- [x] Multi-threaded construction, faster construction speed
- [x] Blog support
- [x] Switch from gitbook is easy, just config `route` and convert `SUMMARY.md` by `summary2yaml` command
- [x] Comments(Plugins), e.g. `gitalk`


## Demo

[This website](https://teedoc.github.io/) is generated using `teedoc`, what you see now is what the generated website looks like.

In addition, there are other websites that use `teedoc`, please see [here](./usage/sites.md) for details


## Similar tools

In fact, there are many tools of this type, but each one is slightly different. Just choose one according to your needs.

If you have choice difficulties, you are recommended to use teedoc if you meet some of the following conditions:
* Use `Jupyter notebook` to write documents or code? Decisively choose teedoc
* Does the function meet your needs?
* Does the interface meet your aesthetics (you can customize css, or change the theme plug-in)
* Familiar with Python? Plug-ins and functions can be customized at any time

Other similar tools:
* docusaurus: The UI layout of teedoc is almost similar to it, but it uses vue to write, teedoc is native js, if you use vue, you can consider this
* gitbook: a tool that used to be very useful, but it is no longer maintained by the government, and it is turned to commercial. It is not recommended to use it
* docsify: Only one page is needed. Markdown is rendered in the browser instead of pre-rendered into HTML. The advantage is that it is lightweight, but SEO is not friendly. You can use its SSR function, written in nodejs
* readthedocs: A tool used by many open source projects. Like gitbook, it also has a website service. You can start writing documents after registering and logging in, or you can download the software to generate the website yourself, which is friendly to the RST format.


## Some usage suggestions

* Add `Generate with teedoc` in footer to help more people discover teedoc and promote the growth of the project
* Use the template project to start a new document project, you can run it first, and then modify it according to your own needs, so that you can get started faster
