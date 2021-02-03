---
title: 部署 teedoc 生成的网站
keywords: teedoc, 部署
desc: teedoc 生成的网站部署到服务器
---


由于 `teedoc` 生成的网页都是静态网页，所以直接按照常规的部署静态页面的方式部署即可

`teedoc`生成的页面会在`out`目录

使用`teedoc serve`会起一个`HTTP`服务，但是请不要使用在生产环境，是不可靠的

对于生产环境，这里有几个简单实用的方法：

* [部署到 github pages](./deploy_github_pages.md)
* [使用 nginx 部署到自建服务器](./deploy_nginx.md)
* [使用 CDN 加速网站](./deploy_cdn.md)


