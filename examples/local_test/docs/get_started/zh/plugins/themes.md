---
title: teedoc 主题插件
keywords: teedoc, 主题插件, 主题, 插件
desc: teedoc 主题插件
---


## `teedoc-plugin-theme-default`: 默认主题插件

在`site_config.json`中配置插件
```json
    "plugins": {
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
```

* `main_color`: 主题主颜色
* `css`: `css`文件，可以覆盖默认的样式，会被插入到页面的`head`标签中
* `js`： `js`文件，可以写`js`程序，会被放在页面的末尾加载

支持 `白天` 和 `夜间` 模式， 夜间模式会在`body`加一个`dark`类， 如果要该夜间模式的`css`样式，可以基于这个类名修改


