---
title: Hello
keywords:
  - hello
  - world
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



官网: [teedoc.github.io](https://teedoc.github.io/)
本文档源文件: [github.com/teedoc/teedoc.github.io](https://github.com/teedoc/teedoc.github.io)

将 `Markdown` 或者 `Jupyter Notebook` 格式的文档转换为 `HTML` 网页



## Features

- [x] 使用简单， 跨平台，只依赖 `Python3`
- [x] 书写简单，使用 Markdown 语法编写
- [ ] Jupyter notebook 支持
- [x] 多文档支持
- [x] 插件支持
- [x] 多主题支持（由插件实现）
- [x] 通过 css 控制精确到页的样式（通过自定义每页的 id 和 class 实现）
- [x] 多级目录支持
- [x] 多语言支持（手动翻译）(国际化/i18n)
- [ ] 多语言支持（自动翻译）
- [x] 多版本支持（实现方法同多语言）
- [x] 搜索支持
- [x] SEO 友好
- [x] 实时预览更改
- [ ] 博客支持


## 类似的工具

实际上这种类型的工具已经有很多了，按照自己的需求选择一个就好了

* docusaurus: teedoc 的 UI 布局几乎和它类似，不过它使用 vue 写的， teedoc 是原生 js, 如果你用的是 vue 可以考虑用这个
* gitbook: 曾经很好用的工具，但是官方不维护了，转向商业了，不建议再使用
* docsify: 只需要一个页面，markdown 在浏览器渲染，而不是预先渲染成 HTML， 好处就是轻量，但是 SEO 不太友好，可以用它的 SSR 功能， nodejs 编写
* readthedocs: 很多开源项目使用的工具， 和 gitbook 一样也有网站服务，注册登录就可以开始写文档，也可以下载软件自己生成网站，对 RST 格式支持友好

如果你有选择困难症，那么符合以下部分条件，都建议使用 teedoc：
* 功能符合你的需求吗
* 界面符合你的审美吗（可以自定义 css， 或者换主题插件）
* 对 Python 熟悉？ 可以随时自定义插件


## 一些使用建议

* 在 footer 添加 `使用 teedoc 生成`， 帮助更多人发现 teedoc，促进项目的成长
* 使用模板项目开始一个新的文档项目，可以先跑起来，然后再根据自己的需求修改，这样上手更快哦



