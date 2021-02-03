---
title: 开始写文档
keywords: teedoc, markdown, jupyter notebook, html, 文档生成, 替代gitbook, 网站生成, 静态网站, 写文档
desc: teedoc， 将 markdown 或者 jupyter notbook 转换成 html 静态网页， 介绍了 teedoc 的基本使用
---


## 构建与预览

在有`site_config.json`的文档目录下执行
```
teedoc serve
```

在显示 `Starting server at 0.0.0.0:2333 ....` 后，就可以了

打开浏览器访问: [http://127.0.0.1:2333](http://127.0.0.1:2333)


实时修改文件，保存文件后，默认过`3`秒后，会自动重新构建这个文件，然后浏览器会自动刷新
> 自动刷新的延迟时间可以设置，可以加 `-t` 参数， 比如`teedoc -t 0 serve`设置为`0`秒延迟，
> 另外也可以在文档配置中设置，见后面配置参数`rebuild_changes_delay`的说明


如果只需要构建生成`HTML`页面，只需要执行

```
teedoc build
```

>! 注意，如果是最终生成发布版本的文档， 一定要用`build`命令来生成网站页面，`serve`命令生成的页面只能用于本地预览，会有多余的预览相关的代码，不适合用在生产环境部署


另外，也可以指定参数`-d`或者`--dir` 来指定文档目录，这样就不用在文档目录下面执行命令了，比如
```
teedoc -d /home/teedoc/my_doc build
```


## 构建文档删除


构建好的文档会被放到`out`目录下，程序不会主动删除，如果需要清除，请手动删除



## 文档目录结构

```
├─.github
├─docs
│  ├─develop
│  │  ├─en
│  │  └─zh
│  └─get_started
│      ├─assets
│      ├─en
│      └─zh
├─pages
│  └─index
│      ├─en
│      └─zh
├─static
│
└─site_config.json
```

* `.github`: 自动构建脚本，在后面的章节将如何使用
* `docs`: 文档，包含了多份文档， 每份文档都是单独一个文件夹
* `pages`: 页面，包括主页、404页面等等页面
* `static`: 静态文件文件夹，比如存放图片
* `site_config.json`: 网站配置文件
* `config.json`: 除了`site_config.json`外，每个文档目录下都可以有`config.json`用来配置文档相关页面
* `sidebar.json`: 文档目录

## site_config.json 网站配置

网站的配置项，比如网站名称，页面路由，插件配置等等

下面的示例配置文件看起来配置项比较多，不要被吓到，其实很简单，主要几个配置项，掌握了就思想就容易了

配置文件是`json`格式， 比如：

```json
{
    "site_name": "teedoc",
    "site_slogon": "happy to write",
    "route": {
        "docs": {
            "/get_started/zh": "docs/get_started/zh",
            "/get_started/en": "docs/get_started/en",
            "/develop/zh": "docs/develop/zh",
            "/develop/en": "docs/develop/en"
        },
        "pages": {
            "/": "pages/index/zh",
            "/en": "pages/index/en"
        },
        "assets": {
            "/static": "static",
            "/get_started/assets": "docs/get_started/assets"
        },
        "/blog": "blog"
    },
    "executable": {
        "python": "python3",
        "pip": "pip3"
    },
    "plugins": {
        "teedoc-plugin-markdown-parser":{
            "from": "pypi",
            "config": {
            }
        },
        "teedoc-plugin-theme-default":{
            "from": "pypi",
            "config": {
                "dark": true,
                "env":{
                    "main_color": "#4caf7d"
                },
                "css": "/static/css/custom.css",
                "js": "/static/js/custom.js"
            }
        }
    }
}

```

* `site_name`: 网站名
* `site_slogon`: 网站标语
* `route`: 网页路由，包含了文档和页面以及资源文件的路由，比如文档的路由
```json
"docs": {
    "/get_started/zh": "docs/get_started/zh",
    "/get_started/en": "docs/get_started/en",
    "/develop/zh": "docs/develop/zh",
    "/develop/en": "docs/develop/en"
},
```
`key`代表了最终生成的网站中文档的`url`, 后面的值则是对应的源文档路径，
比如源文档`docs/get_started/zh/README.md`，构建后会生成文件`out/get_started/zh/index.html`, 如果不是`md`文件（即不支持的文件），则会原封不动地拷贝文件，最后`out`目录就是生成的网站

`pages`同理，`assets`则不会进行文档转换，直接拷贝到相应的目录

* `executable`: 可执行程序设置， 这里可以设置`python`和`pip`的可执行程序名，在安装插件时会用到
* `plugins`: 插件配置， 主要有名字， 来源， 配置项组成。
名字可以在[github](https://github.com) 搜索`teedoc-plugin`来找到开源的插件，也欢迎你参与编写插件（只需要动 `Python` 语法即可）； 
`from`字段填`pypi`即可，如果插件下载到了本地也可以填写文件夹路径，也可以直接填`git`路径比如`git+https://github.com/*****/******.git`
配置项则由具体的插件决定，比如`teedoc-plugin-theme-default`就有`dark`选项来选择是否启用暗黑主题
* `rebuild_changes_delay`: 检测到文件更改后，延迟多少秒自动重新生成该文档， 浏览器中会自动刷新页面，默认为`3`秒，最短可以设置为`0`秒, 可以使用`teedoc -t 3 serve` 或者 `teedoc --delay serve` 来覆盖这个设置

## config.json 文档配置

这是针对每个文档的配置，放在每个文档的根目录， 比如`docs/get_started/zh/config.json`， 各个文档相互独立，可以设置一样的来保持网站导航栏一致

在这里面可以配置每个文档的导航栏， 以及页尾（`footer`）的内容, 也可以设置插件的`config`项，在当前文档会覆盖`site_config.json`中的配置，从而实现不同文档不同语言（国际化/i18n）或者样式等

比如：

```json
{
    "navbar": {
        "title": "teedoc",
        "logo": {
            "alt": "teedoc logo",
            "src": "/static/image/logo.png"
        },
        "home_url": "/",
        "items": [
            {
                "url": "/get_started/zh",
                "label": "安装使用",
                "position": "left"
            },
            {
                "url": "/develop/zh",
                "label": "开发",
                "position": "left"
            },
            {
                "url": "https://github.com/neutree/teedoc",
                "label": "github",
                "target": "_blank",
                "position": "right"
            },
            {
                "label": "语言: ",
                "position": "right",
                "items": [
                    {
                        "url": "/get_started/zh",
                        "label": "中文"
                    },
                    {
                        "url": "/get_started/en",
                        "label": "English"
                    }
                ]
            }
        ]
    },
    "footer":{
        "items":[
            {
                "url": "https://github.com/neutree/teedoc",
                "label": "github",
                "target": "_blank",
                "position": "left"
            },
            {
                "url": "https://github.com/neutree/teedoc",
                "label": "使用 teedoc 生成",
                "target": "_blank",
                "position": "right"
            },
            {
                "url": "https://neucrack.com",
                "label": "neucrack",
                "target": "_blank",
                "position": "right"
            },
            {
                "url": "https://beian.miit.gov.cn",
                "label": "*ICP备********号-1",
                "target": "_blank",
                "position": "middle"
            },
            {
                "url": "https://beian.miit.gov.cn/#/Integrated/index",
                "label": "*公网安备**************号",
                "target": "_blank",
                "position": "middle"
            }
        ]
    },
    "plugins": {
        "teedoc-plugin-search":{
            "config": {
                "search_hint": "搜索",
                "input_hint": "输入关键词，多关键词空格隔开",
                "loading_hint": "正在加载，请稍候。。。",
                "download_err_hint": "下载文件失败，请刷新重试或检查网络",
                "other_docs_result_hint": "来自其它文档的结果",
                "curr_doc_result_hint": "当前文档搜索结果"
            }
        }
    }
}
```


## sidebar.json 文档目录（侧边栏）设置

这里面设置文档的目录，每个文档一份，相互独立

文件路径使用相对路径，填文件名即可， `README.md` 会被自动转换成`index.html`

另外也可以不写`file`路径，直接`url`， 比如`"url": "/get_started/zh"`, 同时可以设置`"target":"_blank"` 在新窗口打开，不设置则在当前窗口打开

比如：

```json
{
    "items":[
        {
            "label": "teedoc 简介",
            "file": "README.md"
        },
        {
            "label": "安装 teedoc",
            "file": "install/README.md"
        },
        {
            "label": "开始写文档",
            "file": "usage/start.md"
        },
        {
            "label": "插件",
            "file": "plugins/README.md",
            "items":[
                {
                    "label": "主题插件",
                    "file": "plugins/themes.md"
                },
                {
                    "label": "其它插件",
                    "file": "plugins/others.md"
                }
            ]
        },
        {
            "label": "markdown 语法",
            "file": "syntax/syntax_markdown.md"
        },
        {
            "label": "使用了 teedoc 的网站",
            "file": "usage/sites.md"
        },
        {
            "label": "更多样例",
            "items":[
                {
                    "label": "二级子目录样例",
                    "items":[
                        {
                            "label": "三级子目录样例",
                            "items":[
                                {
                                    "label": "文章1",
                                    "file": "more/example_docs/doc1.md"
                                }
                            ]
                        },
                        {
                            "label": "文章2",
                            "file": "more/example_docs/doc2.md"
                        }
                    ]
                },
                {
                    "label": "这是一个链接",
                    "url": "https://github.com/teedoc/teedoc",
                    "target": "_blank"
                }
            ]
        }
    ]
}
```

## 链接、图片等资源文件

放在文档目录下面的文件，如果是可是识别的文件，比如`*.md`， 则会转换成`*.html`， 如果不能识别，比如`*.jpg`， 则会原封不动地拷贝

### 最简单和推荐的方法

资源文件可以放在文档对应的目录，比如文档`docs/get_started/zh`， 可以创建`docs/get_started/zh/assets/images/logo.png`,
然后在`docs/get_started/zh/README.md`中使用相对路径引用，即`![](assets/images/logo.png)`

### 进阶方法

这种情况适用于多份文档都引用同一个文件夹下（`url`）的资源， 方便维护多份文档，比如多语言翻译，或者减少 `CDN` 流量消耗

使用文档路径外的资源，在`site_config.json` 中配置
```json
{
    "route": {
        "docs": {
            "/get_started/zh": "docs/get_started/zh",
        },
        "assets": {
            "/get_started/assets": "docs/get_started/assets"
        }
    }
}
```
这个设置会将`docs/get_started/assets`整个目录拷贝为`/get_started/assets`
所以只需要在`docs/get_started/zh/README.md`中使用相对路径引用，即`![](../assets/images/logo.png)`




