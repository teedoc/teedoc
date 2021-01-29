---
title: markdown 语法
tags: teedoc, markdown, 语法
keywords: teedoc, markdown, 语法
desc: teedoc 的 markdown 语法介绍和实例
---

一级标题（`#`）最好不要使用， 因为上面的`title`会自动生成一个一级标题（`<h1>`标签），一个页面最好只有一个一级标题，方便搜索引擎爬取收录

`keywords` 是生成的 `html` 页面的 `keywords`， 不会显示到页面，主要提供给搜索引擎使用
`desc` 是生成的 `html` 页面的 `description`， 不会显示到页面，主要提供给搜索引擎使用
`tags` 是给文章的标签，会显示在页面


## 二级标题

### 三级标题

#### 四级标题

#### 四级标题2

#### 四级标题3

##### 五级标题

###### 六级标题

最多 6 级标题

## 链接

[teedoc 简介](../README.md)


## 列表

列表项:
* 包子
* 馒头
* 茶叶蛋


* aaaaaaa
  * 二级列表
  * 二级列表
  * 二级列表
* bbbbbb


## code

这是一段行内代码`print("hello")`，或者强调`teedoc`

```python
print("hello")

print("world")
```

```c
#include "stdio.h"

int main()
{
    printf("hello world");
}
```


## 注释(引用块)

下面是一段注释
> 这里是一段注释 (`<blockquote></blockquote>`)
> 这是注释的第二行
```python
# 这里是注释里面的代码段
print("hello")
```


> 注释
>> 注释嵌套
>> 注释嵌套



## 警告

下面是一段警告信息

>! 这是一段警告信息(`<blockquote class="spoiler"></blockquote>`)

## 图片

要显示这张图片，需要在`site_config.json`中设置`route`键值

![这是一张图片](../../assets/images/logo.jpg)
![这是一张图片](../assets/images/logo.jpg)

![这是一张图片](../../assets/images/logo.jpg)![这是一张图片](../assets/images/logo.jpg)

## 视频


```html
<video src="https://****.com/***.mp4" controls="controls" preload="auto">your brower not support play video</video>
```

这里没有放视频， 所以是空白, 放入正确的视频就可以播放了

<video src="" controls="controls" preload="auto">your brower not support play video</video>


## iframe 嵌入网页

<iframe src="//player.bilibili.com/player.html?aid=52613549&bvid=BV144411J72P&cid=92076022&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" style="width:43vw;height:34vw;min-width: 85%;"> </iframe>


## 引用标记

我能干饭我自豪。[^干饭人]

[^干饭人]: 老子说道

这会在文章末尾进行注解


## 划线

我是~~天神~~打工人啊


## 表格


| Header 1 | *Header* 2 |
| -------- | -------- |
| `Cell 1` | [Cell 2](http://example.com) link |
| Cell 3 | **Cell 4** |


## 任务列表

- [x] 任务1
- [x] 任务2
- [ ] 任务3
- [ ] 任务4

