teedoc
=====

中文 | [English](./README.md)

[![License](https://img.shields.io/github/license/teedoc/teedoc?color=red&label=开源协议)](./LICENSE) [![PyPI](https://img.shields.io/pypi/v/teedoc?label=版本)](https://pypi.org/project/teedoc/#history) ![PyPI - Downloads](https://img.shields.io/pypi/dm/teedoc?color=brightgreen&label=下载次数) ![PyPI - Downloads](https://img.shields.io/pypi/dw/teedoc?color=brightgreen&label=下载次数) [![GitHub Repo stars](https://img.shields.io/github/stars/teedoc/teedoc?style=social&label=收藏)](https://github.com/teedoc/teedoc)

<img src="https://teedoc.github.io/static/image/logo.png" height=64/> 

官网: [teedoc.neucrack.com](https://teedoc.neucrack.com) 或者 [teedoc.github.io](https://teedoc.github.io/)

更多样例: 看[这里](https://teedoc.neucrack.com/get_started/zh/usage/sites.html) 或 [这里](https://teedoc.github.io/get_started/zh/usage/sites.html)

将 `Markdown` 或者 `Jupyter Notebook` 格式的文档转换为 `HTML` 网页

![](./assets/images/teedoc_screenshot_0.png)

以下场景可使用`teedoc`：
* 建文档网站，并且最好支持放多份文档，和自定义页面
* 组织或者企业有很多份文档分散在各个域名，希望统一到一个域名下
* 建`WiKi`网站
* 建个人或者企业知识库
* 建个人或者企业网站

## Features

- [x] 使用简单， 跨平台，只依赖 `Python3`
- [x] 部署简单， 生成的网站是全静态页面，直接拷贝到服务器或者上传到三方机构即可部署
- [x] 书写简单，使用 Markdown 语法编写
- [x] Jupyter notebook 支持
- [x] 多文档支持
- [x] 插件支持
- [x] 多主题支持（由插件实现）
- [x] 通过 css 控制精确到页的样式（通过自定义每页的 id 和 class 实现）
- [x] 多级目录支持
- [x] 多语言支持（手动翻译）(国际化/i18n)
- [x] 多语言支持（翻译插件）
- [x] 搜索支持
- [x] SEO 友好
- [x] 实时预览更改
- [x] 并行构建，更快的构建速度
- [x] 博客支持
- [x] Jinja2 HTML 布局模板支持


## 开始使用吧

官网: [teedoc.github.io](https://teedoc.github.io/) 或者 [teedoc.neucrack.com](https://teedoc.neucrack.com/)


## 几分钟内在 github pages 服务上搭建你自己的网站

查看 [template 仓库](https://github.com/teedoc/template)


## 快速开始

* 安装 python3

`Windows` 或 `macOS`, 从 [python.org](https://www.python.org/downloads/) 下载安装包安装

`Linux`, 如 `Ubuntu`:

```
sudo apt install python3 python3-pip
```

* 安装 teedoc

这条命令会 **安装 teedoc 主程序**

```
pip3 install -U teedoc
```

* 初始化文档

```
mkdir my_site
cd my_site
teedoc init
```

或者

```
teedoc -d my_site init
```

> 根据提示选择 minimal 模板

* 安装插件

这条命令会 **安装文档需要的插件**(在`site_config.json`里设置)

```
cd my_site
teedoc install
```

* 构建（`build`） 或者 预览（`serve`）

```
teedoc serve
```

然后浏览器访问 [http://127.0.0.1:2333](http://127.0.0.1:2333)

如果只需要构建生成网页:

```
teedoc build
```

