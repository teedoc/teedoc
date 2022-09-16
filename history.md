teedoc update history
========

## 2022-9-16 v1.31.0

* Support directly use Jinja2 template in html file with out use layout in md file, more info see doc's html syntax part.

## 2022-9-16 v1.30.1

* Optimize sidebar
* Add mermaid support for markdown
* Ignore to detect all tempfiles
* Update markdown parser mistune to V2
* Add `teedoc-list-files` tool to list files by file size
* Add `teedoc-compare` tool to compare two directories' files' difference
* Add `teedoc-upload` tool to upload files to remote server, support tencent cloud and qiniu cloud
* Optimize build log
* New Markdown syntax:
  * `tabset` (jupyter not support yet)
  * `details`(jupyter not support yet)
  * Support customize header ID with `{#id}` syntax
* Metadata full support `yaml` format, and support `update` key to generate update history
* New teedoc logo
* Fix long TOC can not show completely bug
* Remove install local plugins in `teedoc install` command
* Optimize last modify date show

## 2022-05-08

* Update theme plugin support TOC for mobile
* Update blog plugin support image in brief and support `cover` meta key


## 2022-01-06 v1.26.0

* Add fast mode for serve command, if use `teedoc serve --fast`, it will only copy assets first, no build pages, then you can visit page, the page will build when you visit this page. And build all pages task will work in background too.

## 2022-01-06 v1.25.0

* Plugin teedoc-plugin-theme-default support layout template `redirect.html`
e.g. If we want `/maixpy` and `/maixpy.html` redirect to `/soft/maixpy.html`, just create a `maixpy.md` file add
```markdown
---
layout: redirect
redirect_url: /soft/maixpy/zh/
---
```

* Change http serve from http.server to flask to become more compatible for more devices


## 2021-09-18 v1.24.0

* Plugin teedoc-plugin-ad-hint support config in doc config, not only site_config
* (for developers)plugin support add js_vars variable

## 2021-09-18 v1.23.1

* Add 404.html template, support i18n

## 2021-09-8 v1.19.0

* Add i18n support for plugins and templates
* Add comment plugin teedoc-plugin-comments-gitalk
* Add print page support
* Add anchor for titles
* Add warning log for wrong sidebar item
* Fix bug: not auto refresh page when content changed in previwe mode
* Fix search index file too large bug
* Fix navbar list item z-index error
* Fix toc smooth scroll bug when id is escaped charactors

## 2021-08-7 v1.17.1

* Add layout template customize support(Jinja2)

## 2021-08-3 v1.16.1

* Change markdown parser from markdown2 to mistune, now build faster at least 2x
* Ignore .git folder in file watcher

## 2021-07-22 v1.15.8


* Optimize file watcher, fix rename in file browser can't trigger event issue
* Fix error when copy error(not found error)

plugin theme_default: Add image viewer for img item

## 2021-05-21 v1.15.0

* Add summary2json and summary2yaml command for gitbook sidebar file
* Add sidebar splitter, you can set `sidebar_width`(default sidebar width) config for plugin  `teedoc-plugin-theme-default`, e.g.:
```
"teedoc-plugin-theme-default": {
            "from": "../../plugins/teedoc-plugin-theme-default",
            "config": {
                "env": {
                    "sidebar_width": "300px"
                }
            }
}
```


## 2021-05-21 v1.14.0

Speed up build by change multithread build to multiprocess build

## 2021-05-21 v1.13.0

Add `collapsed: false` option for sidebar directory to show sub directory by default

## 2021-04-14 v1.12.3

* fix sidebar active error
* optimize navbar list type display
* add navbar list type url support
* add --thread parameter, to set build thread number
* update markdown plugin to v1.0.8, warning when parse markdown error instead of program crash

## 2021-1-28 v1.0.1

Basic functions


## 2021-1-16

project started

