---
title: 使用 nginx 部署 teedoc 生成的网站到服务器
keywords: teedoc, 部署, nginx
desc: 使用 nginx 部署 teedoc 生成的网站到服务器
---


这里简要介绍，更多详细使用请自行查找文档或教程， 比如 `HTTPS`

## 安装 nginx

服务器安装 `nginx`， 比如`ubuntu`：
```
sudo apt update
sudo apt install nginx
```

## 配置并启动 nginx 服务

```
nginx -t
```
可以看到配置文件路径，一般是`/etc/nginx/nginx.conf `， 可以看到文件里面包含了`/etc/nginx/site-enabled/`

查看下面的`default`文件，可以看到语句
```
listen 80 default_server;
root /var/www/html;
```
即监听`80`端口，网站根目录在这里，我们将我们的网站内容拷贝到这里，即`out`目录下所有文件拷贝到`/var/www/html/`目录下

然后：
```
service nginx start
```

访问`http://ip:80`就可以访问到网站了，`:80`也可以省略， 也可以修改成其它端口，因为国内没有备案的网站不允许使用`80`端口，海外的服务器则没有限制

