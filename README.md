teedoc
===========
[中文 README](./README_ZH.md)

Official site: [teedoc.github.io](https://teedoc.github.io/)

documentation generate tool from markdown and jupyter notebook to html

![](./assets/images/teedoc_screenshot_0.jpg)

## Features

- [x] Easy to use, cross platform, only need `Python3`
- [x] Easy to write, markdown support
- [ ] Jupyter notebook support
- [x] Multiple docs support
- [x] Plugin support
- [x] Multiple theme support(support by plugin)
- [x] Multi-level directory support
- [x] Multiple language support(manually translate)
- [ ] Multiple language support(auto translate)
- [x] Multiple version support
- [x] Search support
- [x] SEO friendly
- [x] Real-time preview file changes
- [ ] Blog support


## Usage

Install `Python3` first, **only support `Python3.7` or higher version**

e.g. on `Ubuntu`:
```
sudo apt install python3 python3-pip
```

`Windows` or `macOS` just visit [Python official site](https://www.python.org/downloads/)


### Install

```
pip3 install teedoc
```

And upgrade with command:
```
pip3 install teedoc --upgrade
```

now you can use `teedoc` command

if not, ensure python3 bin path in your env PATH,
e.g. `~/.local/bin`


### Build website

* Get template site source code

```
git clone https://github.com/teedoc/teedoc.github.io my_site
```

* Install pulgins

```
cd my_site
teedoc install
```

* Build `HTML` pages and start a `HTTP` server

```
teedoc serve
```

After show `Starting server at 0.0.0.0:2333 ....`

Open brower visit: [http://127.0.0.1:2333](http://127.0.0.1:2333)


or only build

```
teedoc build
```

then you can find website in `out` directory

## More see [teedoc.github.io](https://teedoc.github.io/)


