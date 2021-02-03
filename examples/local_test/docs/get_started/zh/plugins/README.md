---
title: teedoc 插件
keywords: teedoc, 插件
desc: teedoc， 将 markdown 或者 jupyter notbook 转换成 html 静态网页， 介绍了 teedoc 的的插件
---


## 插件使用介绍

teedoc 使用了插件系统，方便扩充功能


在`site_config.json` 文件中， 设置`plugins`字段， 比如
```json
{
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

这里默认安装了两个插件，分别是`teedoc-plugin-markdown-parser`和`teedoc-plugin-theme-default`，均直接从`pypi.org`安装，主题插件有配置项

配置项包括是否使用`dark`主题，以及插件的环境变量`env`，设置了`main_color`为`#4caf7d`，这个值会在插件中用到，将主题色设置为对应的颜色；

以及设置自定义`css`文件和`js`文件，值是`url`，不是文件路径（文件路径和`url`的映射请看前面的`route`（路由）介绍， 通过设置这个`css`文件，可以覆盖主题插件默认的样式，实现简单的自定义功能


*  [主题插件](./themes.md)
*  [其它插件](./others.md)

