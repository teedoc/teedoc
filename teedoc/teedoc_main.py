import argparse
import sys
from typing import Optional
try:
    from .logger import Logger
    from .http_server import HTTP_Server
    from .version import __version__
except Exception:
    from logger import Logger
    from http_server import HTTP_Server
    from version import __version__
import os, sys
import json, yaml
import subprocess
import shutil
import re
from collections import OrderedDict
import multiprocessing
import threading
import math
from queue import Queue, Empty
from datetime import datetime

class RebuildException(Exception):
    pass

g_sitemap_content = {}
def add_robots_txt(site_config, out_dir, log):
    if not "robots" in site_config:
        site_config["robots"] = {}
    out_path = os.path.join(out_dir, "robots.txt")
    log.i("generate robots.txt")
    robots_items = site_config["robots"]
    robots_txt = ""
    if not "User-agent" in robots_items:
        robots_items["User-agent"] = "*"
    for k, v in robots_items.items():
        robots_txt += f"{k}: {v}\n"
    robots_txt += "Sitemap: {}://{}/sitemap.xml\n".format(site_config["site_protocol"], site_config["site_domain"])
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(robots_txt)

def generate_sitemap(update_htmls, out_path, site_domain, site_protocol, log):
    log.i("generate sitemap.xml")
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n'
    for doc_url in update_htmls:
        htmls = update_htmls[doc_url]
        for url, html in htmls.items():
            url = "{}://{}{}".format(site_protocol, site_domain, url)
            file_path = html['file_path']
            last_edit_time = datetime.fromtimestamp(os.stat(file_path).st_mtime)
            last_edit_time = str(last_edit_time).replace(" ", "T")
            change_freq = "weekly"
            priority = 1.0
            sitemap_item = '''    <url>
            <loc>{}</loc>
            <lastmod>{}</lastmod>
            <changefreq>{}</changefreq>
            <priority>{}</priority>
        </url>
    '''.format(url, last_edit_time, change_freq, priority)
            g_sitemap_content[url] = sitemap_item
    for url in g_sitemap_content:
        sitemap_content += g_sitemap_content[url]
    sitemap_content += '</urlset>\r\n'
    with open(out_path, "w", encoding='utf-8') as f:
        f.write(sitemap_content)


def split_list(obj, n):
    dist = math.ceil(len(obj)/n)
    for i in range(0, len(obj), dist):
        yield obj[i:i+dist]

def get_content_type_by_path(file_path):
    ext = os.path.splitext(file_path)[1][1:].lower()
    content_type = "text/plain"
    if ext == "svg":
        content_type = "image/svg+xml"
    elif ext == "html":
        content_type = "text/html"
    elif ext == "jpeg" or ext == "jpg" or ext == "png":
        content_type = "image/{}".format(ext)
    elif ext == "css":
        content_type = "text/css"
    elif ext == "js":
        content_type = "application/javascript"
    elif ext == "xml":
        content_type = "text/xml"
    elif ext == "json":
        content_type = "application/json"

    return content_type

def parse_site_config(doc_src_path):
    site_config_path = os.path.join(doc_src_path, "site_config.json")
    def check_site_config(config):
        configs = ["site_name", "site_slogon", "site_root_url", "site_domain", "site_protocol", "route", "executable", "plugins"]
        for c in configs:
            if not c in config:
                return False, "need {} keys, see example docs".format(configs)
        if not site_config['site_root_url'].endswith("/"):
            site_config['site_root_url'] = "{}/".format(site_config['site_root_url'])
        return True, ""
    site_config = load_config(doc_src_path, doc_src_path, config_name="site_config")    
    ok, msg = check_site_config(site_config)
    if not ok:
        return False, "check site_config.json fail: {}".format(msg)
    return True, site_config

def copy_dir(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return True

def copy_file(src, dst):
    dir = os.path.dirname(dst)
    if not os.path.exists(dir):
        os.makedirs(dir, exist_ok=True)
    shutil.copyfile(src, dst)
    return True

def get_files(dir_path, warn=None):
    result = []
    files = os.listdir(dir_path)
    if not files:
        return []
    # check index.* and readme.*, only allow one
    if warn:
        flag = False
        for name in files:
            name0 = os.path.splitext(name)[0].lower()
            if name0 == "index" or name0 == "readme":
                if flag:
                    warn(f"dir {dir_path} include index file and readme file, please only use one!!!")
                    break
                flag = True
    for name in files:
        path = os.path.join(dir_path, name)
        if os.path.isdir(path):
            f_list = get_files(path, warn)
            result.extend(f_list)
        else:
            result.append(path.replace("\\", "/"))
    return result

def write_to_file(files_content, in_path, out_path):
    '''
        @files_content      { "/home/neucrack/site/docs/get_started/zh/README.md": "<h1>index page</h1>"
        @in_path      "/home/neucrack/site/docs/get_started/zh"
        @out_path     "/home/neucrack/site/out/get_started/zh"
    '''
    for file, html in files_content.items():
        f_path = file.replace(in_path, out_path)
        d_path = os.path.dirname(f_path)
        if not os.path.exists(d_path):
            os.makedirs(d_path, exist_ok=True)
        # TODO: check file update, if not, skip
        if html: # html, change name
            if os.path.basename(f_path).lower() == "readme.md": # change readme.md to index.html
                f_path = os.path.join(os.path.dirname(f_path), "index.html")
            else:
                f_path = "{}.html".format(os.path.splitext(f_path)[0])
            with open(f_path, "w", encoding="utf-8") as f:
                f.write(html)
        else:    # normal files, just copy
            with open(f_path, "wb") as f:
                with open(file, "rb") as s:
                    f.write(s.read())
    return True, ""

def update_config(old, update, level = 0):
    new = old.copy()
    for key in update.keys():
        if key == "import":
            continue
        if not key in old:
            new[key] = update[key]
            continue
        if type(update[key]) == dict:
            new[key] = update_config(old[key], update[key], level + 1)
        elif type(update[key]) == list:
            # convert list to OrderedDict
            old_list_item = OrderedDict()
            for i, item in enumerate(old[key]):
                if "id" in item:
                    old_list_item[item["id"]] = item
                else:
                    old_list_item[str(i)] = item\
            # update item
            for i, item in enumerate(update[key]):
                if "id" in item:
                    if type(old_list_item[item["id"]]) == dict:
                        old_list_item[item["id"]] = update_config(old_list_item[item["id"]], item, level + 1)
                    else:
                        old_list_item[item["id"]] = item
                else:
                    old_list_item[f"n{i}"] = item
            # convert back to list
            items = []
            for id in old_list_item:
                items.append(old_list_item[id])
            new[key] = items
        else:
            new[key] = update[key]
    return new

def load_config(doc_dir, config_template_dir, config_name="config"):
    '''
        @doc_dir doc diretory, abspath
        @config_dir config template files dir, abspath
    '''
    config = None
    config_path = os.path.join(doc_dir, f"{config_name}.json")
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            try:
                config = json.load(f)
            except Exception as e:
                raise Exception('\n\ncan not parse json file "{}"\njson format error: {}'.format(config_path, e))
    else:
        config_path = os.path.join(doc_dir, f"{config_name}.yaml")
        if not os.path.exists(config_path):
            config_path = os.path.join(doc_dir, f"{config_name}.yml")
        if not os.path.exists(config_path):
            raise Exception("can not open file: {}".format(config_path))
        with open(config_path, encoding="utf-8") as f:
            try:
                config = yaml.load(f.read(), Loader=yaml.Loader)
            except Exception as e:
                raise Exception('\ncan not parse yaml file "{}"\nyaml format error: {}'.format(config_path, e))
    if "import" in config:
        # update parent config
        config_name = config["import"]
        if config_name.endswith(".json") or config_name.endswith(".yaml"):
            config_name = config_name[:-5]
        config_parent = load_config(config_template_dir, config_template_dir, config_name = config_name)
        config = update_config(config_parent, config)
    return config

def load_doc_config(doc_dir, config_template_dir):
    return load_config(doc_dir, config_template_dir)

def get_sidebar(doc_dir, config_template_dir):
    return load_config(doc_dir, config_template_dir, config_name="sidebar")

def get_navbar(doc_dir, config_template_dir):
    return load_config(doc_dir, config_template_dir)["navbar"]

def get_plugins_config(doc_dir, config_template_dir):
    return load_config(doc_dir, config_template_dir)["plugins"]

def get_footer(doc_dir, config_template_dir):
    return load_config(doc_dir, config_template_dir)["footer"]

def get_url_by_file_rel(file_path, doc_url):
    url = os.path.splitext(file_path)[0]
    tmp = os.path.split(url)
    if tmp[1].lower() == "readme":
        url = "{}/index".format(tmp[0])
        if url.startswith("/"):
            url = url[1:]
    if(doc_url.endswith("/")):
        url = "{}{}.html".format(doc_url, url)
    else:
        url = "{}/{}.html".format(doc_url, url)
    return url

def get_sidebar_list(sidebar, doc_path, doc_url):
    '''
        @return {
            "file_path": {
                "curr": (url, label),
                "previous": (url, label),
                "next": (url, label),
            }
        }
    '''
    def get_items(config, doc_url, level=0):
        '''
            @return {
                "file_path": {
                    "curr": (url, label),
                }
            }
        '''
        is_dir = "items" in config
        items = OrderedDict()
        if "label" in config and "file" in config and config["file"] != None and config["file"] != "null":
            url = get_url_by_file_rel(config["file"], doc_url)
            items[os.path.join(doc_path, config["file"]).replace("\\", "/")] = {
                "curr": (url, config["label"])
            }
        if is_dir:
            for item in config["items"]:
                _items = get_sidebar_list(item, doc_path, doc_url)
                items.update(_items)
        return items

    dict_items = get_items(sidebar, doc_url)
    items = list(dict_items.items())
    length = len(items)
    for i, (path, item) in enumerate(items):
        p = None
        n = None
        if i > 0:
            p = items[i - 1][1]["curr"]
        if i < length - 1:
            n = items[i + 1][1]["curr"]
        if not "previous" in item or not item["previous"]:
            item["previous"] = p
        if not "next" in item or not item["next"]:
            item["next"] = n
        dict_items[path]= item
    return dict_items

def generate_sidebar_html(htmls, sidebar, doc_path, doc_url, sidebar_title_html):
    '''
        @htmls  {
                "file1_path": {
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html
                                }
                }
        @return {
                "file1_path": {
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html，
                                “sidebar": ""
                                }
                }
    '''
    def generate_items(config, doc_path_relative, doc_url, level=0):
        html = ""
        li = False
        is_dir = "items" in config
        active = False
        li_item_html = ""
        if "label" in config:
            if "file" in config and config["file"] != None and config["file"] != "null":
                url = get_url_by_file_rel(config["file"], doc_url)
                if config["file"].startswith("./"):
                    active = doc_path_relative.lower() == config["file"][2:].lower()
                else:
                    active = doc_path_relative.lower() == config["file"].lower()
                li_item_html = '<li class="{} with_link"><a href="{}"><span class="label">{}</span><span class="{}"></span></a>'.format(
                    "active" if active else "not_active",
                    url, config["label"],
                    "sub_indicator" if is_dir else ""
                )
            elif "url" in config and config["url"] != None and config["url"] != "null":
                li_item_html = '<li class="{} with_link"><a href="{}" {}><span class="label">{}</span><span class="{}"></span></a>'.format(
                    "not_active",
                    config["url"],
                    'target="{}"'.format(config["target"]) if "target" in config else "",
                    config["label"],
                    "sub_indicator" if is_dir else ""
                )
            elif not is_dir and level == 1:
                # first level label with no url or file and items, add sidebar_category class
                li_item_html = '<li class="not_active no_link sidebar_category"><span class="label">{}</span>'.format(
                    config["label"]
                )
            else:
                li_item_html = '<li class="not_active no_link"><a><span class="label">{}</span><span class="{}"></span></a>'.format(
                    config["label"], "sub_indicator" if is_dir else ""
                )
            li = True
        if is_dir:
            dir_html = ""
            _active = False
            for item in config["items"]:
                item_html, _active_sub = generate_items(item, doc_path_relative, doc_url, level + 1)
                _active |= _active_sub
                dir_html += item_html
            active |= _active
            if _active:
                li_item_html = li_item_html.replace("not_active", 'active_parent')
            elif not active:
                li_item_html = li_item_html.replace("sub_indicator", "sub_indicator sub_indicator_collapsed")
            html += li_item_html
            html += '<ul class="{}">\n{}</ul>\n'.format("show" if active else "", dir_html)
        else:
            html += li_item_html
        if li:
            html += "</li>\n"
        return html, active


    for file, html in htmls.items():
        if not html:
            continue
        doc_path_relative = file.replace(doc_path, "")[1:].replace("\\", "/")
        items, _ = generate_items(sidebar, doc_path_relative, doc_url)
        sidebar_html = '''
            <div id="sidebar_wrapper">
                <div id="sidebar">
                    <div id="sidebar_title">
                        {}
                    </div>
                    {}
                </div>
            </div>'''.format(sidebar_title_html, items)
        html["sidebar"] = sidebar_html
        htmls[file] = html
    return htmls

def generate_navbar_html(htmls, navbar, doc_path, doc_url, plugins_objs, plugins_new_config):
    '''
        @doc_path  doc path, contain config.json and sidebar.json
        @doc_url   doc url, config in "route" of site_config.json
        @htmls  {
                "file1_path": {
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html,
                                “sidebar": ""
                                }
                }
        @return {
                "file1_path": {
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html，
                                "sidebar": "",
                                "navbar": ""
                                }
                }
    '''
    def generate_items(config, doc_url, page_url, level=0, parent_item_type="link"):
        active_item = None
        have_label = "label" in config
        have_url = "url" in config and config["url"] != None and config["url"] != "null"
        li_html = ""
        active = False
        # item_type: link, list, selection
        item_type = config["type"] if "type" in config else ("selection" if "items" in config else "link")
        if have_label and have_url:
            if not config["url"].startswith("http"):
                if not config["url"].startswith("/"):
                    config["url"] = "/{}".format(config["url"])
            _doc_url = doc_url+"/" if not doc_url.endswith("/") else doc_url
            _config_url = config["url"] + "/" if (not config["url"].endswith(".html") and not config["url"].endswith("/")) else config["url"]
            # print(parent_item_type, _doc_url, _config_url, page_url)
            if _doc_url == "/":
                if page_url == "/index.html" and _config_url == "/":       # / / /index.html
                    active = True
                elif _config_url == page_url:      # / /store.html /store.html
                    active = True
                elif parent_item_type == "selection" and _doc_url == _config_url: # / / /store.html
                    active = True
            else:
                if _config_url != "/" and page_url.startswith(_config_url):
                    active = True
                else:
                    active = _doc_url == _config_url
            if active:
                active_item = config
        sub_items_ul_html = ""
        if "items" in config:
            sub_items_html = ""
            for item in config["items"]:
                item_html, _active_item = generate_items(item, doc_url, page_url, level = level + 1, parent_item_type = item_type)
                if _active_item:
                    active_item = _active_item
                sub_items_html += item_html
            sub_items_ul_html = "<ul>{}</ul>".format(sub_items_html)
        if item_type == "list":
            li_html = '<li class="sub_items {}"><a {}>{}</a>{}\n'.format(
                            "active_parent" if active_item else "",
                            f'href="{config["url"]}"' if have_url else "",
                            "{}".format(config["label"]) if have_label else "",
                            sub_items_ul_html
                        )
        elif item_type == "selection":
            li_html = '<li class="sub_items {}"><a {} href="{}">{}{}</a>{}'.format(
                "active" if active else '',
                'target="{}"'.format(config["target"]) if "target" in config else "",
                config["url"] if have_url else "", config["label"], active_item["label"] if active_item else "",
                sub_items_ul_html
            )
        else: # link
            li_html = '<li class="{}"><a {} href="{}">{}</a>'.format(
                "active" if active else '',
                'target="{}"'.format(config["target"]) if "target" in config else "",
                config["url"] if have_url else "", config["label"]
            )
        html = '{}</li>\n'.format(li_html)
        return html, active_item
    
    def generate_lef_right_items(config, doc_url, page_url):
        left = '<ul id="nav_left">\n'
        right = '<ul id="nav_right">\n'
        for item in config["items"]:
            html, _ = generate_items(item, doc_url, page_url, level = 0)
            if "position" in item and item["position"] == "right":
                right += html
            else:
                left  += html
        left += "</ul>\n"
        right += "</ul>\n"
        return left, right

    for file, html in htmls.items():
        if not html:
            continue
        # get file file url
        url = get_url_by_file_rel(file.replace(doc_path, "")[1:], doc_url)
        nav_left, nav_right = generate_lef_right_items(navbar, doc_url, url)
        if "src" in navbar["logo"] and navbar["logo"]["src"]:
            logo_html = '<a class="site_title" href="{}"><img class="site_logo" src="{}" alt="{}"><h2>{}</h2></a>'.format(
                            navbar["home_url"], navbar["logo"]["src"], navbar["logo"]["alt"], navbar["title"]
                        )
        else:
            logo_html = '<a class="site_title" href="{}"><h2>{}</h2></a>'.format(
                            navbar["home_url"], navbar["title"]
                        )
        # add navbar items from plugins
        items_plugins_html = ""
        for plugin in plugins_objs:
            if plugin.name in plugins_new_config:
                new_config = plugins_new_config[plugin.name]["config"]
            else:
                new_config = {}
            _items = plugin.on_add_navbar_items(new_config)
            if not _items:
                continue
            items_html = '<ul class="nav_plugins">'
            for item in _items:
                items_html += "<li>{}</li>".format(item)
            items_html += "</ul>"
            items_plugins_html += items_html
        navbar_html = '''
            <div id="navbar">
                <div id="navbar_menu">
                    {}
                    <a id="navbar_menu_btn"></a>
                </div>
                <div id="navbar_items">
                    <div>
                        {}
                    </div>
                    <div>
                        {}
                        {}
                    </div>
                </div>
            </div>'''.format(logo_html, nav_left, nav_right, items_plugins_html)
        html["navbar"] = navbar_html
        htmls[file] = html
    return htmls

def generate_footer_html(htmls, footer, doc_path, doc_url, plugins_objs):
    '''
        @doc_path  doc path, contain config.json and sidebar.json
        @doc_url   doc url, config in "route" of site_config.json
        @htmls  {
                "file1_path": {
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html,
                                “sidebar": "",
                                "navbar": ""
                                }
                }
        @return {
                "file1_path": {
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html，
                                "sidebar": "",
                                "navbar": "",
                                "footer": ""
                                }
                }
    '''
    def generate_items(config, doc_url, level):
        have_url = "url" in config and config["url"] != None and config["url"] != "null"
        have_label = "label" in config
        li_html = ""
        active = False
        if have_url:
            if (not config["url"].startswith("http") and
                not config["url"].startswith("mailto")):
                if not config["url"].startswith("/"):
                    config["url"] = "/{}".format(config["url"])
            have_url = True
        sub_items_ul_html = ""
        if "items" in config:
            sub_items_html = ""
            for item in config["items"]:
                item_html = generate_items(item, doc_url, level + 1)
                sub_items_html += item_html
            sub_items_ul_html = "<ul>{}</ul>".format(sub_items_html)
        if not have_url:
            li_html = '<li><a>{}</a>{}\n'.format(
                        config["label"] if have_label else "",
                        sub_items_ul_html)
        else:
            li_html = '<li><a {} href="{}">{}</a>{}'.format(
                'target="{}"'.format(config["target"]) if "target" in config else "",
                config["url"], config["label"], sub_items_ul_html
            )
        html = '{}</li>\n'.format(li_html)
        return html
    
    def generate_footer_items(config, doc_url):
        top = '<ul>\n'
        bottom = '<ul>\n'
        for item in config["top"]:
            html = generate_items(item, doc_url, 0)
            top += html
        if "bottom" in config:
            for item in config["bottom"]:
                html = generate_items(item, doc_url, 0)
                bottom += html
        top += "</ul>\n"
        bottom += "</ul>\n"
        return top, bottom

    for file, html in htmls.items():
        if not html:
            continue
        footer_top, footer_bottom = generate_footer_items(footer, doc_url)
        footer_html = '''
            <div id="footer">
                <div id="footer_top">
                    {}
                </div>
                <div id="footer_bottom">
                    {}
                </div>
            </div>'''.format(footer_top, footer_bottom)
        html["footer"] = footer_html
        htmls[file] = html
    return htmls

def construct_html(htmls, header_items_in, js_items_in, site_config, sidebar_list, doc_config, doc_src_path):
    '''
        @htmls  {
            "title": "",
            "desc": "",
            "keywords": [],
            "tags": [],
            "body": "",
            "toc": "",
            "sidebar": "",
            "navbar": ""
            "metadata": {},
            "footer": "",
            "show_source": "Edit this page" or no this key,
            "date": "2021-3-14", # may not exists
            "author": "", # may not exists
        }
    '''
    files = {}
    items = list(htmls.items())
    for i, (file, html) in enumerate(items):
        if not html:
            files[file] = None
        else:
            if html["title"]:
                page_title = "{} - {}".format(html["title"], site_config["site_name"])
                article_title = html["title"]
            else:
                page_title = site_config["site_name"]
                article_title = ""
            header_items = "\n        ".join(header_items_in)
            js_items = "\n".join(js_items_in)
            tags_html = ""
            footer_html = html["footer"] if "footer" in html else ""
            for tag in html["tags"]:
                tags_html += '<li>{}</li>\n'.format(tag)
            tags_html = '<ul>{}</ul>'.format(tags_html)
            if "sidebar" in html:
                previous_item_html = ""
                next_item_html = ""
                if file in sidebar_list:
                    if sidebar_list[file]["previous"]:
                        previous_item_html = '<a href="{}"><span class="icon"></span><span class="label">{}</span></a>'.format(sidebar_list[file]["previous"][0], sidebar_list[file]["previous"][1])
                    if sidebar_list[file]["next"]:
                        next_item_html = '<a href="{}"><span class="label">{}</span><span class="icon"></span></a>'.format(sidebar_list[file]["next"][0], sidebar_list[file]["next"][1])
                menu_html = '''<div id="menu_wrapper">
                                    <div id="menu">
                                    </div>
                                </div>'''
                if "show_source" in html:
                    source_url = site_config["source"]
                    if source_url.endswith("/"):
                        source_url = source_url[:-1]
                    source_url += file.replace(doc_src_path, "")
                    source_html = '''<div id="source_link"><a href="{}" target="_blank">{}</a></div>'''.format(
                                    source_url, html["show_source"]
                    )
                else:
                    source_html = ""
                info_html = '<span class="article_author">{}</span><span class="article_date">{}</span>'.format(
                    html["author"] if "author" in html else "",
                    html["date"] if "date" in html else "",
                )

                body_html = '''
        <div id="wrapper">
            {}
            {}
            <div id="article">
                <div id="content_wrapper">
                    <div id="content_body">
                        <div id="article_head">
                            <div id="article_title">
                                <h1>{}</h1>
                            </div>
                            <div id="article_tags">
                                {}
                            </div>
                            <div id="article_info">
                            <div>
                                {}
                            </div>
                            <div>
                                {}
                            </div>
                            </div>
                        </div>
                        <div id="article_content">
                            {}
                        </div>
                    </div>
                    <div id="previous_next">
                        <div id="previous">
                            {}
                        </div>
                        <div id="next">
                            {}
                        </div>
                    </div>
                </div>
                <div id="toc">
                    <div id="toc_content">
                            {}
                    </div>
                </div>
            </div>
        </div>
        <a id="to_top" href="#"></a>
        <div id="doc_footer">
                        {}
                    </div>'''.format(
                        html["sidebar"],
                        menu_html,
                        article_title,
                        tags_html,
                        info_html,
                        source_html,
                        html["body"],
                        previous_item_html, 
                        next_item_html,
                        html["toc"] if "toc" in html else "",
                        footer_html,
                )
            else: # not "sidebar" in html
                body_html = '''
                <div id="page_wrapper">
                    <div id="page_content"><div>{}</div></div>
                    <a id="to_top" href="#"></a>
                    <div id="page_footer">{}</div>
                </div>'''.format(html["body"], footer_html)
            html_start = get_html_start_id_class(html, doc_config["id"] if "id" in doc_config else None, doc_config['class'] if 'class' in doc_config else None)
            files[file] = '''<!DOCTYPE html>
{}
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="keywords" content="{}">
    <meta name="description" content="{}">
    <meta name="generator" content="teedoc">
    {}
    <title>{}</title>
</head>
<body>
    {}
    {}
</body>
{}
</html>
'''.format( html_start,
            ",".join(html["keywords"]),
            html["desc"], 
            header_items,
            page_title,
            html["navbar"] if "navbar" in html else "",
            body_html,
            js_items
            )
    return files

def update_html_abs_path(file_htmls, root_path):
    def re_del(c):
        content = c[0]
        if content.startswith("src"):
            if content[5] == "/" and content[6] != "/":
                content = "{}{}{}".format(content[:5], root_path[:-1], content[5:])
        elif content.startswith("href"):
            if content[6] == "/" and content[7] != "/": # href="/static/..."
                content = "{}{}{}".format(content[:6], root_path[:-1], content[6:])
        else:
            if content[4] != "/" and content[5] == "/" and content[6] != "/": # url("/static/...")
                content = "{}{}{}".format(content[:5], root_path[:-1], content[5:])
            elif content[4] == "/" and content[5] != "/": # url(/static/...)
                content = "{}{}{}".format(content[:4], root_path[:-1], content[4:])
        return content

    for path in file_htmls:
        if not file_htmls[path]:
            continue
        file_htmls[path] = re.sub(r'href=".*?"', re_del, file_htmls[path])
        file_htmls[path] = re.sub(r'src=".*?"', re_del, file_htmls[path])
        file_htmls[path] = re.sub(r'url(.*?)', re_del, file_htmls[path])
    return file_htmls

def add_url_item(htmls, url, dir, site_root_url):
    '''
        will remove empty html items, only return valid html items
        @htmls {
            "file_path":{
                "title": ""
                "body": ""
                "raw": ""
            }
        }
        
        @return {
            "url":{
                "title": ""
                "body": ""
                "raw": ""
                "file_path": ""
            }
        }
    '''
    htmls_valid = {}
    for file_path in htmls:
        if not htmls[file_path]:
            continue
        if not url:
            url_path = site_root_url[:-1]
        else:
            url_path = "{}{}".format(site_root_url, url)
        file_path_rel = file_path.replace(dir, "")
        if file_path_rel.startswith("/"):
            file_path_rel = file_path_rel[1:]
        url_path = get_url_by_file_rel(file_path_rel, url_path)
        htmls_valid[url_path] = htmls[file_path]
        htmls_valid[url_path]["file_path"] = file_path
    return htmls_valid

def get_html_start_id_class(html, id, classes):
    if id:
        id = id.split(" ")[0] # remove space
    if classes:
        classes = classes.split(",")
    else:
        classes = []
    if "id" in html["metadata"]:
        id = html["metadata"]["id"].split(" ")[0] # remove space
    if "class" in html["metadata"]:
        classes.extend(html["metadata"]["class"].split(","))
    if "" in classes:
        classes.remove("")
    html_start = '<html {} {}>'.format(f'id="{id}"' if id else "", 'class="{}"'.format(" ".join(classes)) if classes else "")
    return html_start

def htmls_add_source(htmls, repo_addr, label):
    '''
        @htmls {
            "file_path": {
                "metadata": {
                    "show_source": "Edit this page"
                }
            }
        }
        @repo_addr https://github.com/teedoc/teedoc

        @return {
            "file_path": {
                "metadata": {
                    "show_source": "Edit this page"
                },
                "show_source": "Edit this page"
            }
        }
    '''
    if not repo_addr:
        return htmls
    for file, v in htmls.items():
        # not show source
        if "show_source" in v["metadata"]:
            show_source = v["metadata"]["show_source"].strip().lower()
            if show_source == "false":
                continue
            elif show_source != "true":
                label = v["metadata"]["show_source"]
        htmls[file]["show_source"] = label

    return htmls

def parse(name, plugin_func, routes, site_config, doc_src_path, config_template_dir, log, out_dir, plugins_objs, header_items, js_items, sidebar, allow_no_navbar, update_files, max_threads_num):
    '''
        @return {
            "doc_url", {
                "page_url": {
                    "title": "",
                    "desc": "",
                    "keywords": "",
                    "tasg": [],
                    "body": "",
                    "toc": "",
                    "raw": "",
                    "sidebar": "",
                    "navbar": "",
                    "metadata": {},
                    "footer": ""
                }
            }
        }
    '''
    queue = Queue()
    site_root_url = site_config["site_root_url"]
    global g_is_error
    g_is_error = False
    for url, dir in routes.items():
        if not url.startswith(site_root_url):
            url = "{}{}".format(site_root_url[:-1], url)
        dir = os.path.abspath(os.path.join(doc_src_path, dir)).replace("\\", "/")
        if not os.path.exists(dir):
            log.w("dir {} not exists!!!".format(dir))
            continue
        if update_files:
            all_files = []
            for modify_file in update_files:
                if modify_file.startswith(dir):
                    all_files.append(modify_file)
            if len(all_files) == 0:
                continue
            log.i("update file:", all_files)
        else:
            all_files = get_files(dir, warn = log.w)
        log.i("parse {}: {}, url:{}".format(name, dir, url))
        doc_config = load_doc_config(dir, config_template_dir)
        # get sidebar config
        sidebar_dict = {}
        if sidebar is True:
            try:
                sidebar_dict = get_sidebar(dir, config_template_dir)
            except Exception as e:
                log.e("parse sidebar.json fail: {}".format(e))
                return False, None
        elif sidebar:
            sidebar_dict = sidebar
        try:
            navbar = doc_config['navbar']
        except Exception as e:
            if not allow_no_navbar:
                log.e("parse config.json navbar fail: {}".format(e))
                return False, None
            navbar = None
        try:
            plugins_new_config = doc_config['plugins']
        except Exception as e:
            plugins_new_config = {}
        try:
            footer = doc_config['footer']
        except Exception as e:
            footer = None
        def on_err():
            global g_is_error
            g_is_error = True
        def is_err():
            global g_is_error
            return g_is_error
        

        def generate(files, url, dir, doc_config, plugin_func, routes, site_config, doc_src_path, log, out_dir, plugins_objs, header_items, js_items, sidebar, allow_no_navbar, queue, plugins_new_config):
            try:
                if url.startswith("/"):
                    rel_url = url[1:]
                else:
                    rel_url = url
                out_path = os.path.join(out_dir, rel_url)
                in_path  = os.path.join(doc_src_path, dir)
                if in_path.endswith("/"):
                    in_path = in_path[:-1]
                if out_path.endswith("/"):
                    out_path = out_path[:-1]
                # call plugins to parse files
                result_htmls = {}
                for plugin in plugins_objs:
                    # parse file content
                    if plugin.name in plugins_new_config:
                        new_config = plugins_new_config[plugin.name]["config"]
                    else:
                        new_config = {}
                    result = plugin.__getattribute__(plugin_func)(files, new_config=new_config)
                    if result:
                        if not result['ok']:
                            log.e("plugin <{}> {} error: {}".format(plugin.name, plugin_func, result['msg']))
                            on_err()
                            return False
                        else:
                            for key in result['htmls']:
                                if result['htmls'][key]:
                                    result_htmls[key] = result['htmls'][key] # will cover the before
                    if is_err():
                        return False
                # copy not parsed files
                for path in files:
                    if not path in result_htmls:
                        copy_file(path, path.replace(in_path, out_path))
                # no file parsed, just return
                if not result_htmls:
                    log.d("parse files empty: {}".format(files))
                    # on_err()
                    return True
                htmls = result_htmls
                # generate sidebar to html
                if sidebar:
                    sidebar_list = get_sidebar_list(sidebar, dir, url)
                    htmls = generate_sidebar_html(htmls, sidebar, dir, url, sidebar["title"] if "title" in sidebar else "")
                else:
                    sidebar_list = {}
                if is_err():
                    return False
                # generate navbar to html
                if navbar:
                    htmls = generate_navbar_html(htmls, navbar, dir, url, plugins_objs, plugins_new_config)
                if footer:
                    htmls = generate_footer_html(htmls, footer, dir, url, plugins_objs)
                if is_err():
                    return False
                # show source code url
                if "source" in site_config:
                    label = None
                    if not "show_source" in doc_config:
                        label = "Edit this page"
                    elif doc_config["show_source"]:
                        label = doc_config["show_source"]
                    if label:
                        htmls = htmls_add_source(htmls, site_config["source"], label)

                # consturct html page
                htmls_str = construct_html(htmls, header_items, js_items, site_config, sidebar_list, doc_config, doc_src_path)
                if is_err():
                    return False
                # check abspath
                if site_root_url != "/":
                    htmls_str = update_html_abs_path(htmls_str, site_root_url)
                if is_err():
                    return False
                # write to file
                ok, msg = write_to_file(htmls_str, in_path, out_path)
                if not ok:
                    log.e("write files error: {}".format(msg))
                    on_err()
                    return False
                if is_err():
                    return False
                # add url, add "url" keyword for htmls, will remove empty html items
                htmls = add_url_item(htmls, rel_url, dir, site_root_url)
                if len(htmls) > 0:
                    queue.put((url, htmls))
            except Exception as e:
                log.e("generate html fail: {}".format(e))
                on_err()
                raise e
                return False
            log.i("generate ok")
            return True

        if len(all_files) > 10:
            all_files = split_list(all_files, max_threads_num)
            ts = []
            for files in all_files:
                t = threading.Thread(target=generate, args=(files, url, dir, doc_config, plugin_func, routes, site_config, doc_src_path, log, out_dir, plugins_objs, header_items, js_items, sidebar_dict, allow_no_navbar, queue, plugins_new_config))
                t.setDaemon(True)
                t.start()
                ts.append(t)
            for t in ts:
                t.join()
                # log.i("{} generate ok".format(t.name))
        else:
            if not generate(all_files, url, dir, doc_config, plugin_func, routes, site_config, doc_src_path, log, out_dir, plugins_objs, header_items, js_items, sidebar_dict, allow_no_navbar, queue, plugins_new_config):
                return False, None
    htmls = {}
    for i in range(queue.qsize()):
        url, _htmls = queue.get()
        if not url in htmls:
            htmls[url] = {}
        htmls[url].update(_htmls)
    return True, htmls

def build(doc_src_path, config_template_dir, plugins_objs, site_config, out_dir, log, update_files=None, preview_mode = False, max_threads_num = 1):
    '''
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
            "/blog": "blog"
        }
    '''
    # get html header item from plugins
    header_items = []
    js_items = []
    for plugin in plugins_objs:
        items = plugin.on_add_html_header_items()
        _js_items = plugin.on_add_html_js_items()
        if type(items) != list or type(_js_items) != list:
            log.e("plugin <{}> error, on_add_html_header_items should return list type".format(plugin.name))
            return False
        if items:
            header_items.extend(items)
        if _js_items:
            js_items.extend(_js_items)
    # preview_mode js file
    if preview_mode:
        js_items.append('<script type="text/javascript" src="{}static/js/live.js"></script>'.format(site_config['site_root_url']))
    # parse all docs
    routes = site_config["route"]["docs"]
    ok, htmls_files = parse("docs", "on_parse_files", routes, site_config, doc_src_path, config_template_dir, log, out_dir, plugins_objs, header_items, js_items,
                 sidebar=True, allow_no_navbar=False, update_files=update_files, max_threads_num=max_threads_num)
    if not ok:
        return False

    # parse all pages
    routes = site_config["route"]["pages"]
    ok, htmls_pages = parse("pages", "on_parse_pages", routes, site_config, doc_src_path, config_template_dir, log, out_dir, plugins_objs, header_items, js_items,
                 sidebar=False, allow_no_navbar=True, update_files=update_files, max_threads_num=max_threads_num)
    if not ok:
        return False
    # parse all blogs
    htmls_blog = None
    if "blog" in site_config["route"]:
        routes = site_config["route"]["blog"]
        ok, htmls_blog = parse("blog", "on_parse_blog", routes, site_config, doc_src_path, config_template_dir, log, out_dir, plugins_objs, header_items, js_items,
                    sidebar={"items":[]}, allow_no_navbar=True, update_files=update_files, max_threads_num=max_threads_num)
        if not ok:
            return False

    # generate sitemap.xml
    if not update_files: # only generate when build all
        sitemap_out_path = os.path.join(out_dir, "sitemap.xml")
        generate_sitemap(htmls_files, sitemap_out_path, site_config["site_domain"], site_config["site_protocol"], log)

    # send all htmls to plugins
    for plugin in plugins_objs:
        ok = plugin.on_htmls(htmls_files = htmls_files, htmls_pages = htmls_pages, htmls_blog = htmls_blog)
        if not ok:
            return False

    # copy assets
    assets = site_config["route"]["assets"]
    for target_dir, from_dir in assets.items(): 
        in_path  = os.path.join(doc_src_path, from_dir)
        if target_dir.startswith("/"):
            target_dir = target_dir[1:]
        out_path = os.path.join(out_dir, target_dir).replace("\\", "/")
        if update_files:
            for file in update_files:
                if file.startswith(in_path):
                    log.i("update assets file: {}".format(file))
                    in_path = file.replace(in_path+"/", "")
                    out_path = os.path.join(out_path, in_path)
                    log.i("copy", file, out_path)
                    copy_file(file, out_path)
        else:
            if not copy_dir(in_path, out_path):
                return False
    # copy files from pulgins
    for plugin in plugins_objs:
        files = plugin.on_copy_files()
        for dst,src in files.items():
            if dst.startswith("/"):
                dst = dst[1:]
            dst = os.path.join(out_dir, dst)
            if not os.path.isabs(src):
                log.e("plugin <{}> on_copy_files error, file path {} must be abspath".format(plugin.name, src))
            if not copy_file(src, dst):
                return False
    if not update_files:
        # preview mode js
        if preview_mode:
            js_out_dir = os.path.join(out_dir, "static/js")
            curr_dir_path = os.path.dirname(os.path.abspath(__file__))
            copy_file(os.path.join(curr_dir_path, "static", "js", "live.js"), os.path.join(js_out_dir, "live.js"))
    return True

def files_watch(doc_src_path, log, delay_time, queue):
    from watchdog.observers import Observer
    from watchdog.events import RegexMatchingEventHandler
    import time
 
    class FileEventHandler(RegexMatchingEventHandler):
        def __init__(self, doc_src_path):
            ignore = "{}/out/.*".format(doc_src_path)
            RegexMatchingEventHandler.__init__(self, ignore_regexes=[r".*out.*"])
            self.update_files = []
            self.doc_src_path = doc_src_path
            self.lock = threading.Lock()
        
        def get_update_files(self):
            self.lock.acquire()
            files = self.update_files
            if files:
                self.update_files = []
            self.lock.release()
            return files

        def on_moved(self, event):
            pass
        
        def on_created(self, event):
            if event.is_directory:
                # print("directory created:{0}".format(event.src_path))
                pass
            else:
                # print("file created:{0}".format(event.src_path))
                files = [os.path.abspath(os.path.join(self.doc_src_path, event.src_path)).replace("\\", "/")]
                self.lock.acquire()
                self.update_files.extend(files)
                self.update_files = list(set(self.update_files))
                self.lock.release()
        
        def on_deleted(self, event):
            pass
        
        def on_modified(self, event):
            if event.is_directory:
                # print("directory modified:{0}".format(event.src_path))
                pass
            else:
                # log.d("file modified:{0}".format(event.src_path))
                files = [os.path.abspath(os.path.join(self.doc_src_path, event.src_path)).replace("\\", "/")]
                self.lock.acquire()
                self.update_files.extend(files)
                self.update_files = list(set(self.update_files))
                self.lock.release()
 
    observer = Observer()
    handler = FileEventHandler(doc_src_path)
    observer.schedule(handler, doc_src_path, True)
    observer.start()
    try:
        while True:
            time.sleep(delay_time)
            update_files = handler.get_update_files()
            if update_files:
                log.i("file changes detected:", update_files)
                queue.put(update_files)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()



def main():
    log = Logger(level="i")
    parser = argparse.ArgumentParser(prog="teedoc", description="teedoc, a doc generator, generate html from markdown and jupyter notebook\nrun 'teedoc install && teedoc serve'")
    parser.add_argument("-d", "--dir", default=".", help="doc source root path" )
    parser.add_argument("-f", "--file", type=str, default="", help="file path for json2yaml or yaml2json command")
    parser.add_argument("-p", "--preview", action="store_true", default=False, help="preview mode, provide live preview support for build command, serve command always True" )
    parser.add_argument("-t", "--delay", type=int, default=-1, help="automatically rebuild and refresh page delay time")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s v{}".format(__version__))
    parser.add_argument("-i", "--index-url", type=str, default="", help="for install command, base URL of the Python Package Index (default https://pypi.org/simple). This should point to a repository compliant with PEP 503 (the simple repository API) or a local directory laid out in the same format.\ne.g. Chinese can use https://pypi.tuna.tsinghua.edu.cn/simple")
    parser.add_argument("--thread", type=int, default=0, help="how many threads use to building, default 0 will use max CPU supported")
    parser.add_argument("command", choices=["install", "init", "build", "serve", "json2yaml", "yaml2json"])
    args = parser.parse_args()
    # convert json or yaml file
    if args.command == "json2yaml":
        if not os.path.exists(args.file):
            log.e("file {} not found".format(args.file))
            return 1
        with open(args.file, encoding="utf-8") as f:
            obj = json.load(f)
            yaml_str = yaml.dump(obj, allow_unicode=True, indent=4, sort_keys=False)
            yaml_path = "{}.yaml".format(os.path.splitext(args.file)[0])
            with open(yaml_path, "w", encoding="utf-8") as f2:
                f2.write(yaml_str)
            log.i("convert yaml from json complete, file at: {}".format(yaml_path))
        return 0
    elif args.command == "yaml2json":
        if not os.path.exists(args.file):
            log.e("file {} not found".format(args.file))
            return 1
        with open(args.file, encoding="utf-8") as f:
            obj = yaml.load(f.read(), Loader=yaml.Loader)
            json_path = "{}.json".format(os.path.splitext(args.file)[0])
            with open(json_path, "w", encoding="utf-8") as f2:
                json.dump(obj, f2, ensure_ascii=False, indent=4)
            log.i("convert json from yaml complete, file at: {}".format(json_path))
        return 0
    elif args.command == "init":
        log.i("init doc now")
        if not os.path.exists(args.dir):
            os.makedirs(args.dir, exist_ok=True)
        if os.listdir(args.dir):
            log.e("directory {} not empty, please init in empty directory".format(args.dir))
            return 1
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template")
        for name in os.listdir(template_path):
            path = os.path.join(template_path, name)
            to_path = os.path.join(args.dir, name)
            if os.path.isfile(path):
                shutil.copyfile(path, to_path)
            else:
                shutil.copytree(path, to_path)
        log.i("init doc complete, doc root: {}".format(args.dir))
        return 0
    t = None
    t2 = None
    while 1: # for rebuild all files
        try:
            # doc source code root path
            doc_src_path = os.path.abspath(args.dir).replace("\\", "/")
            # parse site config
            ok, site_config = parse_site_config(doc_src_path)
            if not ok:
                log.e(site_config)
                return 1
            if "config_template_dir" in site_config:
                config_template_dir = os.path.abspath(os.path.join(doc_src_path, site_config["config_template_dir"]))
            else:
                config_template_dir = doc_src_path
            # out_dir
            if site_config["site_root_url"] != "/":
                serve_dir = os.path.join(doc_src_path, "out").replace("\\", "/")
                out_dir = os.path.join(serve_dir, site_config["site_root_url"][1:]).replace("\\", "/")
            else:
                serve_dir = os.path.join(doc_src_path, "out").replace("\\", "/")
                out_dir = serve_dir
            # thread num
            if args.thread > 0:
                max_threads_num = args.thread
            else:
                max_threads_num = multiprocessing.cpu_count()
            log.i(f"max thread number: {max_threads_num}")
            if args.command in ["build", "serve"]:
                # init plugins
                plugins = list(site_config['plugins'].keys())
                plugins_objs = []
                log.i("plugins: {}".format(plugins))
                for plugin, info in site_config['plugins'].items():
                    try:
                        plugin_config = info['config']
                    except Exception:
                        plugin_config = {}
                    # import plugin from local source code
                    path = info["from"]
                    if not os.path.isabs(path):
                        path = os.path.abspath(os.path.join(doc_src_path, path))
                    if os.path.exists(path):
                        sys.path.insert(0, path)
                    plugin_import_name = plugin.replace("-", "_")
                    module = __import__(plugin_import_name)
                    plugin_obj = module.Plugin(doc_src_path=doc_src_path, config=plugin_config, site_config=site_config, logger=log)
                    plugins_objs.append(plugin_obj)
            else:
                plugins_objs = []
            # execute command
            if args.command == "install":
                log.i("install, source doc root path: {}".format(doc_src_path))
                log.i("plugins: {}".format(list(site_config["plugins"].keys())))
                curr_path = os.getcwd()
                for plugin, info in site_config['plugins'].items():
                    path = info['from']
                    # install from pypi.org
                    if not path or path.lower() == "pypi":
                        log.i("install plugin <{}> from pypi.org".format(plugin))
                        if args.index_url:
                            cmd = [site_config["executable"]["pip"], "install", "--upgrade", plugin, "-i", args.index_url]
                        else:
                            cmd = [site_config["executable"]["pip"], "install", "--upgrade", plugin]
                        p = subprocess.Popen(cmd, shell=False)
                        p.communicate()
                        if p.returncode != 0:
                            log.e("install <{}> fail".format(plugin))
                            return 1
                        log.i("install <{}> complete".format(plugin))
                    # install from git like: git+https://github.com/Neutree/COMTool.git#egg=comtool
                    elif path.startswith("svn") or path.startswith("git"):
                        log.i("install plugin <{}> from {}".format(plugin, path))
                        cmd = [site_config["executable"]["pip"], "install", "-e", path]
                        log.i("install <{}> by pip: {}".format(plugin, " ".join(cmd)))
                        p = subprocess.Popen(cmd, shell=False)
                        p.communicate()
                        if p.returncode != 0:
                            log.e("install <{}> fail".format(plugin))
                            return 1
                        log.i("install <{}> complete".format(plugin))
                    # install from local file system
                    else:
                        if not os.path.isabs(path):
                            path = os.path.abspath(os.path.join(doc_src_path, path))
                        if not os.path.exists(path):
                            log.e("{} not found".format(path))
                            return 1
                        os.chdir(path)
                        cmd = [site_config["executable"]["pip"], "install", "."]
                        log.i("plugin path: {}".format(path))
                        log.i("install <{}> by pip: {}".format(plugin, " ".join(cmd)))
                        p = subprocess.Popen(cmd, shell=False)
                        p.communicate()
                        if p.returncode != 0:
                            log.e("install <{}> fail".format(plugin))
                            return 1
                        log.i("install <{}> complete".format(plugin))
                os.chdir(curr_path)
                log.i("all plugins install complete")
            elif args.command == "build":
                # parse files
                if not build(doc_src_path, config_template_dir, plugins_objs, site_config=site_config, out_dir=out_dir, log=log, preview_mode=args.preview, max_threads_num=max_threads_num):
                    return 1
                add_robots_txt(site_config, out_dir, log)
                log.i("build ok")
            elif args.command == "serve":
                from http.server import SimpleHTTPRequestHandler
                from http import HTTPStatus

                if not build(doc_src_path, config_template_dir, plugins_objs, site_config=site_config, out_dir=out_dir, log=log, preview_mode=True, max_threads_num=max_threads_num):
                    return 1
                add_robots_txt(site_config, out_dir, log)
                log.i("build ok")

                host = ('0.0.0.0', 2333)
                
                class On_Resquest(SimpleHTTPRequestHandler):

                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs, directory=serve_dir)

                    def do_GET(self):
                        file_path = self.path[1:].split("?")[0]
                        if not file_path:
                            file_path = "index.html"
                        file_path = os.path.join(serve_dir, file_path)
                        if not os.path.exists(file_path) or not os.path.isfile(file_path):
                            file_path = os.path.join(file_path, "index.html")
                        if not os.path.exists(file_path):
                            file_path = os.path.join(out_dir, "404.html")
                            self.send_response(404)
                        else:
                            self.send_response(200)
                        if not os.path.exists(file_path):
                            content = b"page not found"
                            content_type = "text/html"
                        else:
                            with open(file_path, "rb") as f:
                                content = f.read()
                            content_type = get_content_type_by_path(file_path)
                        self.send_header('Content-type', content_type)
                        self.end_headers()
                        self.wfile.write(content)
                        # print(self.address_string())
                        # print(self.request)

                    def do_HEAD(self):
                        f = self.send_head()
                        if f:
                            f.close()
                    
                    def log_request(self, code='-', size='-'):
                        if isinstance(code, HTTPStatus):
                            code = code.value
                        if code == 304 or code == 200 or code == 301:
                            return
                        self.log_message('"%s" %s %s',
                                        self.requestline, str(code), str(size))
                                    
                    def log_message(self, format, *args):
                        sys.stderr.write("%s - - [%s] %s\n" %
                                        (self.address_string(),
                                        self.log_date_time_string(),
                                        format%args))
                if not t:
                    queue = Queue(maxsize=50)
                    delay_time = (int(site_config["rebuild_changes_delay"]) if "rebuild_changes_delay" in site_config else 3) if int(args.delay) < 0 else int(args.delay)
                    t = threading.Thread(target=files_watch, args=(doc_src_path, log, delay_time, queue))
                    t.setDaemon(True)
                    t.start()
                    def server_loop(host, log):
                        server = HTTP_Server(host, On_Resquest)
                        log.i("root dir: {}".format(serve_dir))
                        log.i("Starting server at {}:{} ....".format(host[0], host[1]))
                        server.serve_forever()
                    if not t2:
                        t2 = threading.Thread(target=server_loop, args=(host, log))
                        t2.setDaemon(True)
                        t2.start()
                while 1:
                    try:
                        files_changed = queue.get(timeout=1)
                    except Empty:
                        continue
                    # detect config.json or site_config.json change, if changed, update all docs file along with the json file
                    files = []
                    for path in files_changed:
                        ext = os.path.splitext(path)
                        if ".sw" in ext:
                            log.w("ingnore {} temp file".format(path))
                            continue
                        dir = os.path.dirname(path)
                        if path[:-5].endswith("site_config"): # site_config changed, rebuild all
                            raise RebuildException()
                        elif config_template_dir == dir:      # config template changed, just rebuild all
                            raise RebuildException()
                        elif path[:-5].endswith("config") or path[:-5].endswith("sidebar"):    # doc or pages config or sidebar changed, rebuild the changed doc
                            files.extend(get_files(dir))
                        else:                                 # normal file, nonly rebuild this file
                            files.append(path)
                    if files:
                        if not build(doc_src_path, config_template_dir, plugins_objs, site_config=site_config, out_dir=out_dir, log=log, update_files = files, preview_mode=True, max_threads_num=max_threads_num):
                            return 1
                        log.i("rebuild ok")
                t.join()
                t2.join()
            else:
                log.e("command error")
                return 1
        except RebuildException:
            continue
        break
    return 0



if __name__ == "__main__":
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 7:
        print('''only support python 3.7 or higher, now python version: {}.{}, please upgrade
or use miniconda to create a virtual env by:
                                            "conda create -n 3.9 python=3.9"
                                            "conda activate 3.9"'''.format(python_version.major, python_version.minor))
        sys.exit(1)
    ret = main()
    sys.exit(ret)
