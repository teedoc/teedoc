import os, sys, time
try:
    from .html_renderer import Renderer
    from . import utils
    from .html_parser import generate_html_item_from_html_file
except Exception:
    from html_renderer import Renderer
    from html_parser import generate_html_item_from_html_file
    import utils
import subprocess
import shutil
import re
from collections import OrderedDict
import multiprocessing
import copy
import datetime
import tempfile
import gettext
from babel import Locale

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
        robots_txt += "{}: {}\n".format(k, v)
    robots_txt += "Sitemap: {}://{}/sitemap.xml\n".format(site_config["site_protocol"], site_config["site_domain"])
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(robots_txt)

def get_last_modify_time(html, file_path, git = False):
    '''
        return datetime.date or None
    '''
    last_edit_time = None
    if html.get("date", "") is False:
        return None
    if html.get('date'):
        try:
            if type(html["date"]) == datetime.date:
                last_edit_time = html["date"]
            elif type(html["date"]) == datetime.datetime:
                last_edit_time = datetime.datetime.date(html["date"])
            elif type(html["date"]) == str:
                date = html['date'].strip().split(" ")[0]
                last_edit_time = datetime.datetime.strptime(date,"%Y-%m-%d")
        except:
            pass
    if last_edit_time is None:
        last_edit_time = utils.get_file_last_modify_time(file_path, git = git)
    if last_edit_time and type(last_edit_time) == datetime.datetime:
        last_edit_time = datetime.datetime.date(last_edit_time)
    return last_edit_time


def generate_sitemap(update_htmls, out_path, site_domain, site_protocol, log):
    log.i("generate sitemap.xml")
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n'
    for doc_url in update_htmls:
        htmls = update_htmls[doc_url]
        for url, html in htmls.items():
            url = "{}://{}{}".format(site_protocol, site_domain, url)
            last_edit_time = get_last_modify_time(html, html['file_path']).isoformat()
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
    import math
    dist = math.ceil(len(obj)/n)
    for i in range(0, len(obj), dist):
        yield obj[i:i+dist]

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
    try:
        shutil.copyfile(src, dst)
    except Exception:
        return False
    return True

def get_files(dir_path, except_dirs, warn=None):
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
                    warn("dir {} include index file and readme file, please only use one!!!".format(dir_path))
                    break
                flag = True
    for name in files:
        path = os.path.join(dir_path, name)
        if os.path.isdir(path):
            if not path in except_dirs:
                f_list = get_files(path, except_dirs, warn)
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

def load_config(doc_dir, config_template_dir, config_name="config"):
    '''
        @doc_dir doc diretory, abspath
        @config_dir config template files dir, abspath
    '''
    import json, yaml
    try:
        from .utils import update_config
    except Exception:
        from utils import update_config

    config = {}
    config_path = os.path.join(doc_dir, config_name + ".json")
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            try:
                config_load = json.load(f)
            except Exception as e:
                raise Exception('\n\ncan not parse json file "{}"\njson format error: {}'.format(config_path, e))
    else:
        config_path = os.path.join(doc_dir, config_name + ".yaml")
        if not os.path.exists(config_path):
            config_path = os.path.join(doc_dir, config_name + ".yml")
        if not os.path.exists(config_path):
            raise Exception("can not open file: {}".format(config_path))
        with open(config_path, encoding="utf-8") as f:
            try:
                config_load = yaml.load(f.read(), Loader=yaml.Loader)
            except Exception as e:
                raise Exception('\ncan not parse yaml file "{}"\nyaml format error: {}'.format(config_path, e))
    config.update(config_load)

    if "import" in config:
        # update parent config
        config_name = config["import"]
        if config_name.endswith(".json") or config_name.endswith(".yaml"):
            config_name = config_name[:-5]
        config_parent = load_config(config_template_dir, config_template_dir, config_name = config_name)
        config = update_config(config_parent, config, ignore=["import"])
    return config

def check_udpate_routes(site_config, doc_root, log):
    '''
        @return True, or False if have fatal error
                and will change all src dir to list [dir, abs_dir], e.g.
                "/get_started/zh": "docs/get_started/zh", to 
                "/get_started/zh": ["docs/get_started/zh", "/home/xxx/site/docs/get_started/zh"],
    '''
    def validate_url(url, check_translate_url = False):
        if not url.startswith("/"):
            url = "{}{}".format("/", url)
        if not url.endswith("/"):
            url = "{}{}".format(url, "/")
        if check_translate_url:
            locale = url[:-1].split("/")[-1]
            if "-" in locale or ("_" in locale and not locale.split("_")[1].isupper()):
                log.w('translate doc url {} error! Should be end with locale name and format should be like "/zh_CN/" "/en_US/" "/en/" "/zh/"'.format(url))
        return url

    def is_dir_valid(rel_dir, doc_root, check_config = True):
        if rel_dir[0] == "/":
            rel_dir = rel_dir[1:]
        if rel_dir[-1] == "/":
            rel_dir = rel_dir[:-1]
        dir_abs = os.path.abspath(os.path.join(doc_root, rel_dir)).replace("\\", "/")
        if not os.path.exists(dir_abs):
            log.w("dir {} not exists!!!".format(dir_abs))
            return "no", rel_dir
        if check_config and not os.path.exists(os.path.join(dir_abs, "config.json")) and not os.path.exists(os.path.join(dir_abs, "config.yaml")):
            log.e("dir {} not have config file!!!".format(dir_abs))
            return "fatal", rel_dir
        return dir_abs, rel_dir
    # only run once
    temp = site_config["route"]["docs"]
    for k in temp:
        if type(temp[k]) == list:
            return True
        break
    # "route" key
    types = [["docs", True], ["pages", True], ["assets", False], ["blog", True]]
    for type_name, check_config in types:
        if type_name in site_config["route"]:
            new_conf = {}
            for url in site_config["route"][type_name]:
                rel_dir = site_config["route"][type_name][url]
                res, rel_dir = is_dir_valid(rel_dir, doc_root, check_config)
                if res == "fatal":
                    return False
                elif res == "no":
                    continue
                new_conf[validate_url(url)] = [rel_dir, res]
            site_config["route"][type_name] = new_conf
    # "translate" key
    types = ["docs", "pages"]
    if "translate" in site_config:
        if "blog" in site_config["translate"]:
            log.w("not support blog translate yet")
        for type_name in types:
            if type_name in site_config["translate"]:
                new_conf = {}
                for url in site_config["translate"][type_name]:
                    new_items = []
                    for item in site_config["translate"][type_name][url]:
                        res, rel_dir = is_dir_valid(item["src"], doc_root)
                        if res == "fatal":
                            return False
                        elif res == "no":
                            continue
                        new_items.append({
                            "url": validate_url(item["url"], check_translate_url = True),
                            "src": [rel_dir, res]
                        })
                    new_conf[validate_url(url)] = new_items
                site_config["translate"][type_name] = new_conf
    return True

def load_doc_config(doc_dir, config_template_dir):
    config = load_config(doc_dir, config_template_dir)
    return config

def get_sidebar(doc_dir, config_template_dir):
    return load_config(doc_dir, config_template_dir, config_name="sidebar")

def get_navbar(doc_dir, config_template_dir):
    return load_config(doc_dir, config_template_dir)["navbar"]

def get_plugins_config(doc_dir, config_template_dir):
    return load_config(doc_dir, config_template_dir)["plugins"]

def get_footer(doc_dir, config_template_dir):
    return load_config(doc_dir, config_template_dir)["footer"]

def generate_navbar_language_items(routes, doc_configs, addtion_items={}):
    '''
        @routes {url: dir, }
        @doc_configs {url: doc_config_dict, }, doc_config_dict must have "locale" keyword
        @addtion_items {url: locale, }
    '''
    items = []
    for url, dir in routes.items():
        locale = Locale.parse(doc_configs[url]["locale"])
        item = {
            "url": url,
            "label": locale.language_name + (" " + locale.script_name if locale.script_name else ""),
            "comment": "language"
        }
        items.append(item)
    for url, locale in addtion_items.items():
        locale = Locale.parse(locale)
        item = {
            "url": url,
            "label": locale.language_name + (" " + locale.script_name if locale.script_name else ""),
            "comment": "language"
        }
        items.append(item)
    return items

def update_navbar_language(navbar, nav_lang_items):
    '''
        add language items to navbar which type == "language", and change type to "selection"
        @navbar dict
        @nav_lang_items list, return by generate_navbar_language_items
    '''
    new_items = []
    for item in navbar["items"]:
        if "type" in item and item["type"] == "language":
            if not nav_lang_items:
                continue
            item["type"] = "selection"
            item["items"] = nav_lang_items
        new_items.append(item)
    navbar["items"] = new_items
    return navbar

def update_navbar_language_urls(items, doc_url, page_url, not_found_urls):
    '''
        Add page url to language items
        @param items [{'url': '/more/en/', 'label': 'English', 'comment': 'language'},
                      {'url': '/more/', 'label': '中文 简体', 'comment': 'language'}]
        @param doc_url  /more/
        @param page_url /more/index.html
        @param not_found_items {url: redirect_url}
        @return [{'url': '/more/en/index.html', 'label': 'English', 'comment': 'language'},
                 {'url': '/more/index.html', 'label': '中文 简体', 'comment': 'language'}]
    '''
    new_items = []
    tail = page_url.replace(doc_url, "")
    for item in items:
        new = item.copy()
        new["url"] += tail
        if not_found_urls:
            print(new["url"])
        if new["url"] in not_found_urls.keys():
            new["url"] = not_found_urls[new["url"]]
        new_items.append(new)
    return new_items

def get_sidebar_list(sidebar, doc_path, doc_url, log, redirect_err_file = False, redirct_url=f"no_translate.html", ref_doc_url="", add_file_item = True):
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
            },
            {
                "not found url": "redirect_url"
            }
        '''
        not_found_items = {}
        is_dir = "items" in config
        items = OrderedDict()
        if "label" in config and "file" in config and config["file"] != None and config["file"] != "null":
            # syntax/syntax_markdown.md#Markdown-文.件头部
            path = config["file"].split("#")
            config["file"] = path[0]
            _id = ""
            if len(path) > 1:
                _id = path[1]
            file_abs = os.path.join(doc_path, config["file"]).replace("\\", "/")
            url = utils.get_url_by_file_rel(config["file"], doc_url)
            if not os.path.exists(file_abs):
                if redirect_err_file:
                    url_rel = utils.get_url_by_file_rel(config["file"], rel = True)
                    _url = f'{redirct_url}?ref={ref_doc_url}{url_rel}&from={url}'
                    not_found_items[url] = _url
                    url = _url
                else:
                    log.w("file {} not found, but set in {} sidebar config file, maybe letter case wrong?".format(file_abs, doc_path))
            if file_abs.endswith("no_translate.md"):
                print(url, file_abs)
            if _id:
                url += f'#{_id}'
            items[file_abs] = {
                "curr": (url, config["label"])
            }
            if add_file_item:
                items[file_abs]["file"] = config["file"]
        if is_dir:
            for item in config["items"]:
                _items, _not_found_items = get_sidebar_list(item, doc_path, doc_url, log, redirect_err_file = redirect_err_file, redirct_url=redirct_url, ref_doc_url=ref_doc_url)
                items.update(_items)
                not_found_items.update(_not_found_items)
        return items, not_found_items

    dict_items, not_found_items = get_items(sidebar, doc_url)
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
    return dict_items, not_found_items

def generate_sidebar_html(htmls, sidebar, doc_path, doc_url, sidebar_title_html, redirect_err_file=False, redirct_url="", ref_doc_url=""):
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
                                "body": html,
                                "sidebar": (sidebar_title, sidebar_items_html)
                                }
                }
    '''
    def generate_items(config, doc_path_relative, doc_url, level=0):
        html = ""
        li = False
        is_dir = "items" in config
        active = False
        li_item_html = ""
        collapsed = False if ("collapsed" in config and config["collapsed"] == False) else True
        if "label" in config:
            if "file" in config and config["file"] != None and config["file"] != "null":
                file_abs = os.path.join(doc_path, config["file"]).replace("\\", "/")
                url = utils.get_url_by_file_rel(config["file"], doc_url)
                if not os.path.exists(file_abs):
                    if redirect_err_file:
                        url_rel = utils.get_url_by_file_rel(config["file"], rel = True)
                        url = f'{redirct_url}?ref={ref_doc_url}{url_rel}&from={url}'
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
                target = config["target"].strip() if "target" in config else ""
                li_item_html = '<li class="{} with_link"><a href="{}" {}><span class="label">{}</span>{}<span class="{}"></span></a>'.format(
                    "not_active {}".format("ext_link" if target else ""),
                    config["url"],
                    'target="{}"'.format(target) if target else "",
                    config["label"],
                    '<span class="ext_link_icon"></span>' if target == "_blank" else "",
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
                if not collapsed:
                    li_item_html = li_item_html.replace("sub_indicator", "sub_indicator")
                else:
                    li_item_html = li_item_html.replace("sub_indicator", "sub_indicator sub_indicator_collapsed")
            html += li_item_html
            html += '<ul class="{}">\n{}</ul>\n'.format("show" if (active or not collapsed) else "", dir_html)
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
        # sidebar_html = '''
        #     <div id="sidebar_wrapper">
        #         <div id="sidebar">
        #             <div id="sidebar_title">
        #                 {}
        #             </div>
        #             {}
        #         </div>
        #         <div id="sidebar_splitter">
        #         </div>
        #     </div>'''.format(sidebar_title_html, items)
        html["sidebar"] = (sidebar_title_html, items)
        htmls[file] = html
    return htmls

def generate_navbar_html(htmls, navbar, doc_path, doc_url, plugins_objs, log, not_found_items = {}):
    '''
        @doc_path  doc path, contain config.json and sidebar.json
        @doc_url   doc url, config in "route" of site_config.json
        @htmls  {
                "file1_path": {
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html,
                                "sidebar": ""
                                }
                }
        @return {
                "file1_path": {
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html,
                                "sidebar": "",
                                "navbar": (logo_url, logo_alt, home_url, navbar_title, navbar_main, navbar_options, navbar_plugins)
                                }
                }
    '''
    def generate_items(config, doc_url, page_url, level=0, parent_item_type="link", active_class = "active"):
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
            if _config_url.endswith("index.html"):
                _config_url = _config_url[:-10]
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
            if item_type == "selection":
                item_htmls = []
                active_items = [None] * len(config["items"])
                count = 0
                items = config["items"]
                if len(config["items"]) > 0 and "language" in config["items"][0].get("comment", ""):
                    items = update_navbar_language_urls(config["items"], doc_url, page_url, not_found_items)
                for i, item in enumerate(items):
                    _active_class = active_class + "tmp"
                    item_html, _active_item = generate_items(item, doc_url, page_url, level = level + 1, parent_item_type = item_type, active_class= _active_class)
                    if _active_item:
                        active_items[i] = _active_item
                        count += 1
                    item_htmls.append(item_html)
                if count >= 1:
                    final = 0
                    max_len = 0
                    for i, item in enumerate(active_items):
                        if item and len(item["url"]) >= max_len:
                            max_len = len(item["url"])
                            final = i
                    item_htmls[final] = item_htmls[final].replace(_active_class, active_class)
                    active_item = active_items[final]
                    for i in range(len(item_htmls)):
                        if i != final:
                            item_htmls[i] = item_htmls[i].replace(_active_class, "")
                sub_items_html = "".join(item_htmls)
            else:
                for item in config["items"]:
                    item_html, _active_item = generate_items(item, doc_url, page_url, level = level + 1, parent_item_type = item_type)
                    if _active_item:
                        active_item = _active_item
                    sub_items_html += item_html
            sub_items_ul_html = "<ul>{}</ul>".format(sub_items_html)
        if item_type == "list":
            li_html = '<li class="sub_items {}"><a {}>{}</a>{}\n'.format(
                            "active_parent" if active_item else "",
                            'href="{}"'.format(config["url"]) if have_url else "",
                            "{}".format(config["label"]) if have_label else "",
                            sub_items_ul_html
                        )
        elif item_type == "selection":
            li_html = '<li class="sub_items {}"><a {} href="{}">{}{}</a>{}'.format(
                active_class if active else '',
                'target="{}"'.format(config["target"]) if "target" in config else "",
                config["url"] if have_url else "", config["label"], active_item["label"] if active_item else "",
                sub_items_ul_html
            )
        else: # link
            li_html = '<li class="{}"><a {} href="{}">{}</a>'.format(
                active_class if active else '',
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
        url = utils.get_url_by_file_rel(file.replace(doc_path, "")[1:], doc_url)
        navbar_main, navbar_options = generate_lef_right_items(navbar, doc_url, url)
        home_url = navbar["home_url"]
        navbar_title = navbar["title"]
        if "src" in navbar["logo"] and navbar["logo"]["src"]:
            if navbar["logo"]["src"].startswith("/"):
                logo_url = navbar["logo"]["src"]
            else:
                log.w("logo's src item only support url now, e.g. /static/image/logo.png")
                logo_url = None
            logo_alt = navbar["logo"]["alt"]
        elif "url" in navbar["logo"] and navbar["logo"]["url"]:
            logo_url = navbar["logo"]["url"]
            logo_alt = navbar["logo"]["alt"]
        else:
            logo_url = None
            logo_alt = None

        # add navbar items from plugins
        # and add js vars to page
        navbar_plugins = ""
        js_vars = {}
        for plugin in plugins_objs:
            vars = plugin.on_js_vars()
            if vars:
                js_vars[plugin.name] = vars
            _items = plugin.on_add_navbar_items()
            if not _items:
                continue
            items_html = '<ul class="nav_plugins">'
            for item in _items:
                items_html += "<li>{}</li>".format(item)
            items_html += "</ul>"
            navbar_plugins += items_html
        if js_vars:
            html["js_vars"] = js_vars
        else:
            html["js_vars"] = {}
        html["navbar"] = (logo_url, logo_alt, home_url, navbar_title, navbar_main, navbar_options, navbar_plugins)
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
                                "sidebar": "",
                                "navbar": ""
                                }
                }
        @return {
                "file1_path": {
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html,
                                "sidebar": "",
                                "navbar": "",
                                "footer": (footer_top, footer_bottom)
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
        html["footer"] = (footer_top, footer_bottom)
        htmls[file] = html
    return htmls

def construct_html(html_template, html_templates_i18n_dirs, htmls, header_items_in, js_items_in, site_config, sidebar_list, doc_config, doc_src_path, plugins_objs, log, is_build, layout_usage_queue = None):
    '''
        @htmls  {
            "title": "",
            "desc": "",
            "keywords": ["", ],
            "tags": ["", ],
            "body": "",
            "toc": "", # may not exists
            "sidebar": (sidebar_title, sidebar_items_html),
            "navbar": (logo_url, logo_alt, home_url, navbar_title, navbar_main, navbar_options, navbar_plugins),
            "metadata": {},
            "footer": (footer_top, footer_bottom),
            "show_source": ("Edit this page", source_url), # may not exists
            "date": "2021-3-14", # None means not set, False mean not show date
            "author": "", # may not exists
        }
    '''
    template_root = os.path.join(doc_src_path, site_config["layout_root_dir"]) if "layout_root_dir" in site_config else os.path.join(doc_src_path, "layout")
    theme_layout_root = os.path.dirname(html_template)
    locale = doc_config["locale"].replace("-", "_") if "locale" in doc_config else None
    lang = locale.replace("_", "-") if locale else None
    renderer0 = Renderer(os.path.basename(html_template), [theme_layout_root], log, html_templates_i18n_dirs, locale=locale)
    files = {}
    items = list(htmls.items())
    for i, (file, html) in enumerate(items):
        try:
            if not html:
                files[file] = None
            else:
                if file.endswith(".html"):
                    renderer = Renderer(os.path.basename(file), [os.path.dirname(file), theme_layout_root], log, html_templates_i18n_dirs, locale=locale)
                else:
                    renderer = renderer0
                metadata = copy.deepcopy(html["metadata"])
                if "title" in metadata:
                    metadata.pop("title")
                if "keywords" in metadata:
                    metadata.pop("keywords")
                if "desc" in metadata:
                    metadata.pop("desc")
                if "tags" in metadata:
                    metadata.pop("tags")
                if "id" in metadata:
                    metadata.pop("id")
                if "layout" in html["metadata"]:
                    html["metadata"]["layout"] = str(html["metadata"]["layout"])
                    if not html["metadata"]["layout"].endswith(".html"):
                        html["metadata"]["layout"] = html["metadata"]["layout"] + ".html"
                    layout = os.path.join(template_root, html["metadata"]["layout"])
                    if not os.path.exists(layout):
                        layout = os.path.join(theme_layout_root, html["metadata"]["layout"])
                    if os.path.exists(layout):
                        # mark file use layout
                        if layout_usage_queue is not None:
                            layout_usage_queue.put([layout.replace("\\", "/"), file.replace("\\", "/")])
                        renderer = Renderer(html["metadata"]["layout"], [template_root, theme_layout_root], log, html_templates_i18n_dirs, locale=locale)
                id, classes = get_html_start_id_class(html, doc_config["id"] if "id" in doc_config else None, doc_config['class'] if 'class' in doc_config else None)
                if "sidebar" in html:
                    previous_article = None
                    next_article = None
                    if file in sidebar_list:
                        if sidebar_list[file]["previous"]:
                            previous_article = {
                                    "url": sidebar_list[file]["previous"][0],
                                    "title": sidebar_list[file]["previous"][1]
                                }
                        if sidebar_list[file]["next"]:
                            next_article = {
                                    "url": sidebar_list[file]["next"][0],
                                    "title": sidebar_list[file]["next"][1]
                                }
                    last_edit_time = get_last_modify_time(html, file, git = is_build)
                    html["date"] = last_edit_time.strftime("%Y-%m-%d") if last_edit_time else None
                    vars = {
                        "lang": lang,
                        "metadata": metadata,
                        "page_id" : id,
                        "page_classes" : classes,
                        "keywords" : html["keywords"],
                        "description" : html["desc"],
                        "header_items" : header_items_in,
                        "title" : html["title"],
                        "site_name" : site_config["site_name"],
                        "js_vars": html["js_vars"],
                        # navbar
                        # (logo_url, logo_alt, home_url, navbar_title, navbar_main, navbar_options, navbar_plugins),
                        "logo_url" : html["navbar"][0],
                        "logo_alt" : html["navbar"][1],
                        "home_url" : html["navbar"][2],
                        "navbar_title" : html["navbar"][3],
                        "navbar_main" : html["navbar"][4],
                        "navbar_options" : html["navbar"][5],
                        "navbar_plugins" : html["navbar"][6],
                        # sidebar info
                        "sidebar_title" : html["sidebar"][0],
                        "sidebar_items_html" : html["sidebar"][1],
                        # docs body info
                        "article_title" : html["title"],
                        "tags" : html["tags"],
                        "author" : html["author"] if "author" in html else None,
                        "date" : html["date"],
                        "show_source" : html["show_source"][0] if "show_source" in html else None,
                        "source_url" : html["show_source"][1] if "show_source" in html else None,
                        "body" : html["body"],
                        "previous" : previous_article,
                        "next" : next_article,
                        "toc" : html["toc"] if "toc" in html else None,
                        # footer
                        "footer_top" : html["footer"][0],
                        "footer_bottom" : html["footer"][1],
                        "footer_js_items" : js_items_in
                    }
                    for plugin in plugins_objs:
                        vars = plugin.__getattribute__("on_render_vars")(vars)
                    rendered_html = renderer.render(**vars)
                else:
                    vars = {
                        "lang": lang,
                        "metadata": metadata,
                        "page_id" : id,
                        "page_classes" : classes,
                        "keywords" : html["keywords"],
                        "description" : html["desc"],
                        "header_items" : header_items_in,
                        "title" : html["title"],
                        "site_name" : site_config["site_name"],
                        "js_vars": html["js_vars"],
                        # navbar
                        # (logo_url, logo_alt, home_url, navbar_title, navbar_main, navbar_options, navbar_plugins),
                        "logo_url" : html["navbar"][0],
                        "logo_alt" : html["navbar"][1],
                        "home_url" : html["navbar"][2],
                        "navbar_title" : html["navbar"][3],
                        "navbar_main" : html["navbar"][4],
                        "navbar_options" : html["navbar"][5],
                        "navbar_plugins" : html["navbar"][6],
                        # docs body info
                        "body" : html["body"],
                        # footer
                        "footer_top" : html["footer"][0],
                        "footer_bottom" : html["footer"][1],
                        "footer_js_items" : js_items_in
                    }
                    for plugin in plugins_objs:
                        vars = plugin.__getattribute__("on_render_vars")(vars)
                    rendered_html = renderer.render(**vars)
                files[file] = rendered_html
        except Exception as e:
            log.e("Error rendering file: %s" % file)
            raise e
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
        elif content.startswith("url"):
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
        file_htmls[path] = re.sub(r'url\(.*?\)', re_del, file_htmls[path])
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
        url_path = utils.get_url_by_file_rel(file_path_rel, url_path)
        htmls_valid[url_path] = htmls[file_path]
        htmls_valid[url_path]["file_path"] = file_path
    return htmls_valid

def get_html_start_id_class(html, id, classes):
    if id:
        id = id.split(" ")[0]
    else:
        id = None
    if classes:
        classes = classes.split(",")
    else:
        classes = []
    if "id" in html["metadata"]:
        id = html["metadata"]["id"].split(" ")[0]
    if "class" in html["metadata"]:
        classes.extend(html["metadata"]["class"].split(","))
    if "" in classes:
        classes.remove("")
    return id, classes

def htmls_add_source(htmls, repo_addr, label, doc_src_path):
    '''
        @htmls {
            "file_path": {
                "metadata": {
                    "show_source": "Edit this page"
                }
            }
        }
        @repo_addr https://github.com/teedoc/teedoc.github.io/blob/main

        @return {
            "file_path": {
                "metadata": {
                    "show_source": "Edit this page"
                },
                "show_source": ("Edit this page", source_url)
            }
        }
    '''
    if not repo_addr:
        return htmls
    for file, v in htmls.items():
        # not show source
        if "show_source" in v["metadata"]:
            show_source = v["metadata"]["show_source"]
            if type(show_source) == str:
                label = v["metadata"]["show_source"]
            elif not show_source:
                continue
        source_url = repo_addr
        if source_url.endswith("/"):
            source_url = source_url[:-1]
        source_url += file.replace(doc_src_path, "")
        htmls[file]["show_source"] = (label, source_url)

    return htmls

def generate_return(plugins_objs, ok, multiprocess):
    if multiprocess:
        for p in plugins_objs:
            p.on_new_process_del()
        if not ok:
            sys.exit(1)
    return ok

def generate(multiprocess, html_template, html_templates_i18n_dirs, files, url, dir, doc_config, plugin_func, routes,
             site_config, doc_src_path, log, out_dir, plugins_objs, header_items, js_items,
             sidebar, sidebar_list, allow_no_navbar, site_root_url, navbar, footer, queue, pipe_rx, pipe_tx,
             redirect_err_file, redirct_url, ref_doc_url, is_build, layout_usage_queue=None, sidebar_root_dir = None,
             not_found_items = {}):
    if not sidebar_root_dir:
        sidebar_root_dir = dir
    if pipe_tx is not None:
        def on_err():
            pipe_tx.send(True)

        def is_err():
            if pipe_rx.poll():
                pipe_rx.recv()
                return True
            return False
    else:
        is_err_flag = False
        def on_err():
            global is_err_flag
            is_err_flag = True

        def is_err():
            return is_err_flag

    try:
        # call init in new process
        if multiprocess:
            for p in plugins_objs:
                p.on_new_process_init()

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
            result = plugin.__getattribute__(plugin_func)(files)
            if result:
                if not result['ok']:
                    log.e("plugin <{}> {} error: {}".format(plugin.name, plugin_func, result['msg']))
                    on_err()
                    return generate_return(plugins_objs, False, multiprocess)
                else:
                    for key in result['htmls']:
                        if result['htmls'][key]:
                            result_htmls[key] = result['htmls'][key]  # will cover the before
                        elif key not in result_htmls:
                            result_htmls[key] = None
            if is_err():
                return generate_return(plugins_objs, False, multiprocess)
        # parse html files
        unrecognized = []
        for file, html in result_htmls.items():
            if not html:
                if file.endswith(".html"):
                    result_htmls[file] = generate_html_item_from_html_file(file)
                else:
                    unrecognized.append(file)
        for file in unrecognized:
            result_htmls.pop(file)
        # copy not parsed files
        for path in files:
            if not path in result_htmls:
                copy_file(path, path.replace(in_path, out_path))
        # no file parsed, just return
        if not result_htmls:
            log.d("parse files empty: {}".format(files))
            # on_err()
            return generate_return(plugins_objs, True, multiprocess)

        htmls = result_htmls
        # generate sidebar to html
        if sidebar:
            htmls = generate_sidebar_html(htmls, sidebar, sidebar_root_dir, url, sidebar["title"] if "title" in sidebar else "",
                                        redirect_err_file=redirect_err_file, redirct_url=redirct_url, ref_doc_url=ref_doc_url)
        if is_err():
            return generate_return(plugins_objs, False, multiprocess)
        # generate navbar to html
        if navbar:
            htmls = generate_navbar_html(htmls, navbar, dir, url, plugins_objs, log, not_found_items = not_found_items)
        if footer:
            htmls = generate_footer_html(htmls, footer, dir, url, plugins_objs)
        if is_err():
            return generate_return(plugins_objs, False, multiprocess)
        # show source code url
        if "source" in site_config:
            label = None
            if not "show_source" in doc_config:
                label = "Edit this page"
            elif doc_config["show_source"]:
                label = doc_config["show_source"]
            if label:
                htmls = htmls_add_source(htmls, site_config["source"], label, doc_src_path)

        # consturct html page
        htmls_str = construct_html(html_template, html_templates_i18n_dirs, htmls, header_items, js_items, site_config, sidebar_list, doc_config, doc_src_path, plugins_objs, log, is_build, layout_usage_queue)
        if is_err():
            return generate_return(plugins_objs, False, multiprocess)
        # check abspath
        if site_root_url != "/":
            htmls_str = update_html_abs_path(htmls_str, site_root_url)
        if is_err():
            return generate_return(plugins_objs, False, multiprocess)
        # write to file
        ok, msg = write_to_file(htmls_str, in_path, out_path)
        if not ok:
            log.e("write files error: {}".format(msg))
            on_err()
            return generate_return(plugins_objs, False, multiprocess)
        if is_err():
            return generate_return(plugins_objs, False, multiprocess)
        # add url, add "url" keyword for htmls, will remove empty html items
        htmls = add_url_item(htmls, rel_url, dir, site_root_url)
        if len(htmls) > 0:
            queue.put((url, htmls))
    except Exception as e:
        import traceback
        traceback.print_exc()
        log.e("generate html fail: {}".format(e))
        on_err()
        return generate_return(plugins_objs, False, multiprocess)
    log.d("generate ok")
    return generate_return(plugins_objs, True, multiprocess)

def get_configs(routes, config_template_dir, log):
    doc_configs = {}
    for url, dir in routes.items():
        _dir, dir = dir
        # load doc config
        # log.i("load config from {}".format(_dir))
        doc_config = load_doc_config(dir, config_template_dir)
        if not "locale" in doc_config:
            doc_config["locale"] = "en"
            log.w(f'locale of <{_dir}> not set, will default as "en", value can be "zh" "zh_CN" "en" "en_US" etc.')
        doc_configs[url] = doc_config
    return doc_configs

def get_nav_translate_lang_items(doc_url, site_config, doc_src_path, config_template_dir, type_name, log):
    '''
        "translate": {
            "docs":{
                "/get_started/zh/": [ {
                        "locale": "en",
                        "url": "/get_started/en/",
                        "src": "docs/get_started/en"
                    }
                ]
            }
        }
    '''
    #   check translation add navbar language items
    lang_items = []
    keys = {
        "doc": "docs",
        "page": "pages",
        "blog": "blog"
    }
    type_name = keys[type_name]
    if "translate" in site_config and type_name in site_config["translate"] and doc_url in site_config["translate"][type_name]:
        docs_translates = site_config["translate"][type_name][doc_url]
        routes = {}
        for dst in docs_translates:
            routes[dst["url"]] = dst["src"]
        src_dir = site_config["route"][type_name][doc_url][1]
        config = load_doc_config(src_dir, config_template_dir)
        if not "locale" in config:
            config["locale"] = "en"
        doc_configs = get_configs(routes, config_template_dir, log)
        lang_items = generate_navbar_language_items(routes, doc_configs, addtion_items={doc_url: config["locale"]})
    return lang_items

def get_templates_i18n_dirs(site_config, doc_src_path, log):
    '''
        get template_i18n_dirs from site_config's  layout_i18n_dirs key, key canbe path str, or list
        @return list, dirs path list, if no, return []
    '''
    def is_dir_valid(dir, rel_dir):
        if not os.path.isabs(dir):
            dir = os.path.join(rel_dir, dir).replace("\\", "/")
        if os.path.exists(dir):
            return dir
        return False
    html_templates_i18n_dirs = []
    if "layout_i18n_dirs" in site_config:
        if type(site_config["layout_i18n_dirs"]) == str:
            abs_dir = is_dir_valid(site_config["layout_i18n_dirs"], doc_src_path)
            if abs_dir:
                html_templates_i18n_dirs.append(abs_dir)
            else:
                log.w("setting layout_i18n_dirs {} from site_config, dir not found".format(site_config["layout_i18n_dirs"]))
        elif type(site_config["layout_i18n_dirs"]) == list:
            for dir in site_config["layout_i18n_dirs"]:
                abs_dir = is_dir_valid(dir, doc_src_path)
                if abs_dir:
                    html_templates_i18n_dirs.append(abs_dir)
                else:
                    log.w("setting layout_i18n_dirs {} from site_config, dir not found".format(dir))
    return html_templates_i18n_dirs

def parse(type_name, plugin_func, routes, routes_trans, site_config, doc_src_path, config_template_dir, log, out_dir, plugins_objs,
            sidebar, allow_no_navbar, update_files, max_threads_num, preview_mode, html_templates_i18n_dirs=[], multiprocess = True,
            translate = False, ref_doc_url="", ref_doc_dir = "", ref_locale = "en", translate_src_sidebar_list = None,
            doc_configs = {}, nav_lang_items = [], is_build = True, layout_usage_queue = None,
            rebuild_docs = None):
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
    if not multiprocess:
        import threading
    try:
        from .utils import check_sidebar_diff
    except Exception:
        from utils import check_sidebar_diff
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    site_root_url = site_config["site_root_url"]
    if not doc_configs:
        doc_configs = get_configs(routes, config_template_dir, log)

    # parse all docs in route
    for url, dirs in routes.items():
        _dir, dir = dirs
        if rebuild_docs and dir not in rebuild_docs:
            continue
        # get files
        except_dirs = utils.get_sub_dirs(dir, routes_trans.get(url, []))
        if update_files:
            all_files = []
            for modify_file in update_files:
                if modify_file.startswith(dir):
                    valid = True
                    for d in except_dirs:
                        if modify_file.startswith(d):
                            valid = False
                            break
                    if valid:
                        all_files.append(modify_file)
            if len(all_files) == 0:
                continue
            log.i("update file:", all_files)
        else:
            all_files = get_files(dir, except_dirs, warn = log.w)
        if not update_files:
            name = doc_configs[url].get("name", "")
            log.i('''
 -----------------------------------------------------
|parse {} {} {}:
|dir:  {}
|url:  {}
|name: {}
|files: {}
 -----------------------------------------------------
'''.format(
        "🌎" if translate else "",
        "📖" if type_name == "doc" else "🌈" if type_name == "page" else "🍉" if type_name == "blog" else "",
        type_name, dir, url, name, len(all_files))
    )
        nav_lang_items = get_nav_translate_lang_items(ref_doc_url if translate else url, site_config, doc_src_path, config_template_dir, type_name, log)
        doc_config = doc_configs[url]
        # inform plugin parse doc start
        try:
            plugins_new_config = doc_config['plugins']
        except Exception as e:
            plugins_new_config = {}
        for plugin in plugins_objs:
            if plugin.name in plugins_new_config:
                new_config = plugins_new_config[plugin.name]["config"]
            else:
                new_config = {}
            plugin.on_parse_start(type_name, url, dirs, doc_config, new_config)
        # get header footer items, and template dir
        # get html header item from plugins
        header_items = []
        footer_js_items = []
        #     get html template from plugins
        html_template = None
        html_templates_i18n_dirs = []
        for plugin in plugins_objs:
            items = plugin.on_add_html_header_items(type_name)
            _js_items = plugin.on_add_html_footer_js_items(type_name)
            if type(items) != list or type(_js_items) != list:
                log.e("plugin <{}> error, on_add_html_header_items should return list type".format(plugin.name))
                return False, None
            if items:
                items = utils.convert_file_tag_items(items, out_dir, plugin.name)
                header_items.extend(items)
            if _js_items:
                _js_items = utils.convert_file_tag_items(_js_items, out_dir, plugin.name)
                footer_js_items.extend(_js_items)
            temp = plugin.on_html_template(type_name)
            if temp and os.path.exists(temp):
                html_template = temp
            temp = plugin.on_html_template_i18n_dir(type_name)
            if temp and os.path.exists(temp):
                html_templates_i18n_dirs.append(temp.replace("\\", "/"))
        if not html_template:
            log.e("no html templates for {}, please install theme plugin".format(type_name))
            return False
        if not update_files:
            log.d("html_templates_i18n_dirs: {}".format("\n -- "+"\n -- ".join(html_templates_i18n_dirs)))

        # preview_mode js file
        if preview_mode:
            footer_js_items.append('<script type="text/javascript" src="{}static/js/live.js"></script>'.format(site_config['site_root_url']))

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
            # remove empty language item, update valid language item to selection item
            navbar = update_navbar_language(navbar, nav_lang_items)
        except Exception as e:
            if not allow_no_navbar:
                log.e("parse config.json navbar fail: {}".format(e))
                return False, None
            navbar = None
        try:
            footer = doc_config['footer']
        except Exception as e:
            footer = None
        redirect_err_file = translate,
        redirct_url=f"{url}no_translate.html"
        if sidebar_dict:
            sidebar_list, not_found_items = get_sidebar_list(sidebar_dict, dir, url, log,
                                redirect_err_file = redirect_err_file,
                                redirct_url=redirct_url,
                                ref_doc_url = ref_doc_url)
            # if not translate: # find all not translate yet items
            #     not_found_items = get_not_trans_items(sidebar_dict, )
            if translate:
                check_sidebar_diff(translate_src_sidebar_list, sidebar_list, ref_doc_url, url, ref_doc_dir, dir, doc_src_path, log)
        else:
            sidebar_list = {}
            not_found_items = {}
        if max_threads_num > 1 and len(all_files) > 10:
            all_files = split_list(all_files, max_threads_num)
            ts = []
            pipes_child_to_parent = []
            pipes_parent_to_child = []
            for files in all_files:
                pipe_rx_c2p, pipe_tx_c2p = multiprocessing.Pipe()
                pipes_child_to_parent.append((pipe_rx_c2p, pipe_tx_c2p))
                pipe_rx_p2c, pipe_tx_p2c = multiprocessing.Pipe()
                pipes_parent_to_child.append((pipe_rx_p2c, pipe_tx_p2c))
                args = (multiprocess, html_template, html_templates_i18n_dirs, files, url, dir, doc_config, plugin_func,
                                            routes, site_config, doc_src_path, log, out_dir, plugins_objs,
                                            header_items, footer_js_items, sidebar_dict, sidebar_list, allow_no_navbar,
                                            site_root_url, navbar, footer, queue, pipe_rx_p2c, pipe_tx_c2p,
                                            redirect_err_file, redirct_url, ref_doc_url, is_build, layout_usage_queue,
                                            None, not_found_items)
                if multiprocess:
                    p = multiprocessing.Process(target=generate, args=args)
                else:
                    p = threading.Thread(target=generate, args=args)
                    p.setDaemon(True)
                p.start()
                ts.append(p)
            have_err = False
            while 1:
                for i in range(len(pipes_child_to_parent)):
                    rx = pipes_child_to_parent[i][0]
                    if rx.poll(): # have error
                        rx.recv()
                        have_err = True
                        # inform all threads or process
                        for j in range(len(pipes_parent_to_child)):
                            tx = pipes_parent_to_child[j][0]
                            tx.send(True)
                all_died = True
                for p in ts:
                    if p.is_alive():
                        all_died = False
                        break
                    elif have_err:
                        raise Exception("generate html fail, see log before")
                if all_died:
                    break
                time.sleep(0.05)
        else:
            ok = generate(multiprocess, html_template, html_templates_i18n_dirs, all_files, url, dir, doc_config, plugin_func,
                          routes, site_config, doc_src_path, log, out_dir, plugins_objs, header_items,
                          footer_js_items, sidebar_dict, sidebar_list, allow_no_navbar, site_root_url, navbar, footer, queue, None, None,
                          redirect_err_file, redirct_url, ref_doc_url, is_build, layout_usage_queue, None, not_found_items)
            if not ok:
                return False, None
        # create no_translate.html
        if translate:
            temp = os.path.join(dir, "no_translate.html")
            if not os.path.exists(temp) and not os.path.exists(os.path.join(dir, "no_translate.md")):
                root_dir = os.path.abspath(os.path.dirname(__file__))
                try:
                    locale = doc_config["locale"]
                    lang = gettext.translation('messages', localedir=os.path.join(root_dir, 'locales'), languages=[locale])
                    lang.install()
                    _ = lang.gettext
                    no_translate_title = _("no_translate_title")
                    no_translate_hint = _("no_translate_hint")
                    visit_hint = _("visit_hint")
                except Exception as e:
                    no_translate_hint = "This page not translated yet"
                    visit_hint = "Please visit"
                    no_translate_title = "no translation"
                with open(os.path.join(root_dir, "templates", "no_translate.md"), "r") as f:
                    content = f.read().replace('<div id="no_translate_hint"></div>', f'<div id="no_translate_hint">{no_translate_hint}</div>').replace(
                        '<span id="visit_hint"></span>', f'<span id="visit_hint">{visit_hint}</span>').replace(
                            "no_translate_title", no_translate_title
                        )
                tmp_dir = tempfile.gettempdir()
                all_files = [os.path.join(tmp_dir, "no_translate.md")]
                with open(all_files[0], "w") as f:
                    f.write(content)
                ok = generate(multiprocess, html_template, html_templates_i18n_dirs, all_files, url, tmp_dir, doc_config, plugin_func,
                          routes, site_config, doc_src_path, log, out_dir, plugins_objs, header_items,
                          footer_js_items, sidebar_dict, sidebar_list, allow_no_navbar, site_root_url, navbar, footer, queue, None, None,
                          redirect_err_file, redirct_url, ref_doc_url, is_build, layout_usage_queue, sidebar_root_dir=dir, not_found_items=not_found_items)
                if not ok:
                    return False, None
        log.d("generate {} ok".format(dir))
    htmls = {}
    for i in range(queue.qsize()):
        url, _htmls = queue.get()
        if not url in htmls:
            htmls[url] = {}
        htmls[url].update(_htmls)
    for plugin in plugins_objs:

        plugin.on_parse_end()
    return True, htmls

def build(doc_src_path, config_template_dir, plugins_objs, site_config, out_dir, log, update_files=None,
             preview_mode = False, max_threads_num = 1, multiprocess=True, parse_pages=True, copy_assets=True,
             is_build = True, layout_usage_queue = None,
             rebuild_docs = None):
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
    # check routes
    if not update_files:
        if not check_udpate_routes(site_config, doc_src_path, log):
            return False
    if parse_pages:
        # get html template i18n dir
        html_templates_i18n_dirs = get_templates_i18n_dirs(site_config, doc_src_path, log)
        # parse all docs
        if "docs" in site_config["route"]:
            routes = site_config["route"]["docs"]
            routes_trans = site_config.get("translate", {}).get("docs", {})
            ok, htmls_files = parse("doc", "on_parse_files", routes, routes_trans, site_config, doc_src_path, config_template_dir, log, out_dir, plugins_objs,
                        sidebar=True, allow_no_navbar=False, update_files=update_files, max_threads_num=max_threads_num, preview_mode=preview_mode,
                        html_templates_i18n_dirs = html_templates_i18n_dirs, multiprocess = multiprocess, is_build = is_build, layout_usage_queue=layout_usage_queue,
                        rebuild_docs = rebuild_docs)
            if not ok:
                return False
        # parse all pages
        if "pages" in site_config["route"]:
            routes = site_config["route"]["pages"]
            routes_trans = site_config.get("translate", {}).get("docs", {})
            ok, htmls_pages = parse("page", "on_parse_pages", routes, routes_trans, site_config, doc_src_path, config_template_dir, log, out_dir, plugins_objs,
                        sidebar=False, allow_no_navbar=True, update_files=update_files, max_threads_num=max_threads_num, preview_mode=preview_mode,
                        html_templates_i18n_dirs = html_templates_i18n_dirs, multiprocess = multiprocess, is_build = is_build, layout_usage_queue = layout_usage_queue,
                        rebuild_docs = rebuild_docs)
            if not ok:
                return False
        # parse all blogs
        htmls_blog = None
        if "blog" in site_config["route"]:
            routes = site_config["route"]["blog"]
            ok, htmls_blog = parse("blog", "on_parse_blog", routes, {}, site_config, doc_src_path, config_template_dir, log, out_dir, plugins_objs,
                        sidebar={"items":[]}, allow_no_navbar=True, update_files=update_files, max_threads_num=max_threads_num, preview_mode=preview_mode,
                        html_templates_i18n_dirs = html_templates_i18n_dirs, multiprocess = multiprocess, is_build = is_build, layout_usage_queue = layout_usage_queue,
                        rebuild_docs = rebuild_docs)
            if not ok:
                return False
        # parse all translate docs
        if "translate" in site_config:
            if "docs" in site_config["translate"]:
                docs_translates = site_config["translate"]["docs"]
                for src in docs_translates:
                    routes = {}
                    for dst in docs_translates[src]:
                        routes[dst["url"]] = dst["src"]
                    src_dir = site_config["route"]["docs"][src][1]
                    sidebar_dict = get_sidebar(src_dir, config_template_dir) # must be success
                    sidebar_list, not_found_items = get_sidebar_list(sidebar_dict, src_dir, src, log)
                    #    pase mannually translated files, and change links of sidebar items that no mannually translated file
                    ok, htmls_files2 = parse("doc", "on_parse_files", routes, {}, site_config, doc_src_path, config_template_dir, log, out_dir, plugins_objs,
                                sidebar=True, allow_no_navbar=False, update_files=update_files, max_threads_num=max_threads_num, preview_mode=preview_mode,
                                html_templates_i18n_dirs = html_templates_i18n_dirs, multiprocess = multiprocess,
                                translate=True, ref_doc_url=src, ref_doc_dir=src_dir, translate_src_sidebar_list = sidebar_list, is_build = is_build,
                                layout_usage_queue = layout_usage_queue,
                                rebuild_docs = rebuild_docs
                                )
                    #    create
                    htmls_files.update(htmls_files2)
                    if not ok:
                        return False
            if "pages" in site_config["translate"]:
                docs_translates = site_config["translate"]["pages"]
                for src in docs_translates:
                    routes = {}
                    for dst in docs_translates[src]:
                        routes[dst["url"]] = dst["src"]
                    src_dir = site_config["route"]["pages"][src][1]
                    #    pase mannually translated files, and change links of sidebar items that no mannually translated file
                    ok, htmls_pages2 = parse("page", "on_parse_pages", routes, {}, site_config, doc_src_path, config_template_dir, log, out_dir, plugins_objs,
                                sidebar=False, allow_no_navbar=True, update_files=update_files, max_threads_num=max_threads_num, preview_mode=preview_mode,
                                html_templates_i18n_dirs = html_templates_i18n_dirs, multiprocess = multiprocess,
                                translate=True, ref_doc_url=src, ref_doc_dir=src_dir, is_build = is_build, layout_usage_queue = layout_usage_queue,
                                rebuild_docs = rebuild_docs
                                )
                    #    create
                    htmls_pages.update(htmls_pages2)
                    if not ok:
                        return False
        # generate sitemap.xml
        if is_build: # only generate when build mode, not generate when preview mode
            sitemap_out_path = os.path.join(out_dir, "sitemap.xml")
            generate_sitemap(htmls_files, sitemap_out_path, site_config["site_domain"], site_config["site_protocol"], log)

        # send all htmls to plugins
        for plugin in plugins_objs:
            ok = plugin.on_htmls(htmls_files = htmls_files, htmls_pages = htmls_pages, htmls_blog = htmls_blog)
            if not ok:
                return False

    # copy assets
    if copy_assets:
        if not update_files:
            log.i("copy assets files")
        assets = site_config["route"]["assets"]
        for target_dir, from_dir in assets.items(): 
            in_path  = from_dir[1]
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
                        if not copy_file(file, out_path):
                            log.w("copy {} to {} fail".format(file, out_path))
            else:
                if not copy_dir(in_path, out_path):
                    return False
        # copy files from pulgins
        log.i("copy assets files of plugins")
        for plugin in plugins_objs:
            files = plugin.on_copy_files()
            for dst,src in files.items():
                if dst.startswith("/"):
                    dst = dst[1:]
                dst = os.path.join(out_dir, dst)
                if not os.path.isabs(src):
                    log.e("plugin <{}> on_copy_files error, file path {} must be abspath".format(plugin.name, src))
                if not copy_file(src, dst):
                    log.e("copy plugin <{}> file {} to {} error".format(plugin.name, src, dst))
                    return False
        # preview mode js
        if preview_mode:
            js_out_dir = os.path.join(out_dir, "static/js")
            curr_dir_path = os.path.dirname(os.path.abspath(__file__))
            copy_file(os.path.join(curr_dir_path, "static", "js", "live.js"), os.path.join(js_out_dir, "live.js"))
    return True

def get_layout_used_by(layout_root, path, layout_usages):
    files = []
    layout = path.replace(layout_root, "")[1:]
    if path in layout_usages:
        # print(f"find files used layout {layout}: {layout_usages[path]}")
        files = layout_usages[path]
    return files

def check_layout_usage(files, layout_root, layout_usages):
    final_files = []
    for path in files:
        if path.startswith(layout_root):
            files = get_layout_used_by(layout_root, path, layout_usages)
            if len(files) > 0:
                final_files.extend(files)
        else:
            final_files.append(path)
    return final_files

def files_watch(doc_src_path, site_config, log, delay_time, queue, layout_usage_queue):
    from watchdog.observers import Observer
    from watchdog.events import RegexMatchingEventHandler
    import time
    import threading

    class FileEventHandler(RegexMatchingEventHandler):
        def __init__(self, doc_src_path):
            RegexMatchingEventHandler.__init__(self, ignore_regexes=[r"[\\\/]+out[\\\/]+", r"[\\\/]+.git[\\\/]", r".*\.\~.*?\..*", r".*\.sw"])
            self.update_files = []
            self.doc_src_path = doc_src_path
            self.lock = threading.Lock()

        def get_update_files(self):
            self.lock.acquire()
            self.update_files = list(set(self.update_files))  # remove dumplicated files
            files = self.update_files
            if files:
                self.update_files = []
            self.lock.release()
            return files

        def _append_files(self, files):
            self.lock.acquire()
            self.update_files.extend(files)
            self.lock.release()

        def on_moved(self, event):
            if event.is_directory:
                # print("directory created:{0}".format(event.src_path))
                pass
            else:
                print("file moved:{0}".format(event.dest_path))
                files = [os.path.abspath(os.path.join(self.doc_src_path, event.dest_path)).replace("\\", "/")]
                self._append_files(files)

        def on_created(self, event):
            if event.is_directory:
                log.d("directory created:{0}".format(event.src_path))
                pass
            else:
                log.d("file created:{0}".format(event.src_path))
                files = [os.path.abspath(os.path.join(self.doc_src_path, event.src_path)).replace("\\", "/")]
                self._append_files(files)

        def on_deleted(self, event):
            pass

        def on_modified(self, event):
            if event.is_directory:
                # print("directory modified:{0}".format(event.src_path))
                pass
            else:
                log.d("file modified:{0}".format(event.src_path))
                files = [os.path.abspath(os.path.join(self.doc_src_path, event.src_path)).replace("\\", "/")]
                self._append_files(files)

    layout_root = os.path.join(doc_src_path, site_config["layout_root_dir"]) if "layout_root_dir" in site_config else os.path.join(doc_src_path, "layout")
    layout_root = os.path.abspath(layout_root).replace("\\", "/")
    observer = Observer()
    handler = FileEventHandler(doc_src_path)
    files = os.listdir(doc_src_path)
    ignores = [".git", "out"]
    layout_usages = {}
    for name in files:
        if name in ignores:
            continue
        observer.schedule(handler, os.path.join(doc_src_path, name), True)
    observer.start()
    try:
        while True:
            time.sleep(delay_time)
            update_files = handler.get_update_files()
            update_files = check_layout_usage(update_files, layout_root, layout_usages)
            if update_files:
                log.i("file changes detected:", update_files)
                queue.put(update_files)
            try:
                while 1:
                    layout, file = layout_usage_queue.get(timeout=0.1)
                    if not layout in layout_usages:
                        layout_usages[layout] = [file]
                    else:
                        if file not in layout_usages[layout]:
                            layout_usages[layout].append(file)
            except Exception as e:
                pass
    except KeyboardInterrupt:
        observer.stop()
        observer.join()



def main():
    try:
        from .logger import Logger
        from .http_server import HTTP_Server
        from .version import __version__
        from .utils import sidebar_summary2dict
    except Exception:
        from logger import Logger
        from http_server import HTTP_Server
        from version import __version__
        from utils import sidebar_summary2dict
    import argparse
    import json, yaml
    import threading
    from queue import Queue, Empty
    from multiprocessing import Queue as MultiQueue
    import platform

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    templates = {
        "minimal": {
                "dir": "minimal",
                "help": "minimal template",
                "default": True
            },
        "complete": {
                "dir": "template",
                "help": "complete template, have more features settings like multi language"
            },
    }

    parser = argparse.ArgumentParser(prog="teedoc", description="teedoc, a doc generator, generate html from markdown and jupyter notebook\nrun 'teedoc install && teedoc serve'")
    parser.add_argument("-d", "--dir", default=".", help="doc source root path" )
    parser.add_argument("-f", "--file", type=str, default="", help="file path for json2yaml or yaml2json command")
    parser.add_argument("-p", "--preview", action="store_true", default=False, help="preview mode, provide live preview support for build command, serve command always True" )
    parser.add_argument("-t", "--delay", type=int, default=-1, help="automatically rebuild and refresh page delay time")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s v{}".format(__version__))
    parser.add_argument("-i", "--index-url", type=str, default="", help="for install command, base URL of the Python Package Index (default https://pypi.org/simple). This should point to a repository compliant with PEP 503 (the simple repository API) or a local directory laid out in the same format.\ne.g. Chinese can use https://pypi.tuna.tsinghua.edu.cn/simple")
    parser.add_argument("-log", "--log-level", type=str, default="i", choices=["d", "i", "w", "e"], help="log level")
    parser.add_argument("--thread", type=int, default=0, help="how many threads use to building, default 0 will use max CPU supported")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="host address for serve command")
    parser.add_argument("--port", type=int, default=2333, help="port for serve command")
    parser.add_argument("-m", "--multiprocess", action="store_true", default=platform.system().lower() != 'windows', help="use multiple process instead of threads, default mutiple process in unix like systems" )
    parser.add_argument("--fast", action="store_true", default=False, help="fast build mode for serve command")
    parser.add_argument("--template", type=str, default=None, help="for init command, based on which template to create project", choices=list(templates.keys()))
    parser.add_argument("--search-dir", type=str, default=None, help="local plugins search dir for install command, install plugins from local dir and ignore site_config plugin from keyword")
    parser.add_argument("command", choices=["install", "init", "build", "serve", "json2yaml", "yaml2json", "summary2yaml", "summary2json"])
    args = parser.parse_args()

    if args.log_level == "d":
        log_format = '%(asctime)s - [%(levelname)s] - [%(processName)s - %(threadName)s] %(message)s'
    else:
        log_format = '%(asctime)s - [%(levelname)s] -%(message)s'
    log = Logger(level=args.log_level, fmt=log_format)
    if not utils.check_git():
        log.w("git not found, please install git first")
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
    elif args.command == "summary2json":
        if not os.path.exists(args.file):
            log.e("file {} not found".format(args.file))
            return 1
        with open(args.file, encoding="utf-8") as f:
            obj = sidebar_summary2dict(f.read())
            json_path = os.path.join(os.path.dirname(args.file), "sidebar.json")
            with open(json_path, "w", encoding="utf-8") as f2:
                json.dump(obj, f2, ensure_ascii=False, indent=4)
            log.i("convert json from gitbook summary complete, file at: {}".format(json_path))
        return 0
    elif args.command == "summary2yaml":
        if not os.path.exists(args.file):
            log.e("file {} not found".format(args.file))
            return 1
        with open(args.file, encoding="utf-8") as f:
            obj = sidebar_summary2dict(f.read())
            yaml_str = yaml.dump(obj, allow_unicode=True, indent=4, sort_keys=False)
            yaml_path = os.path.join(os.path.dirname(args.file), "sidebar.yaml")
            with open(yaml_path, "w", encoding="utf-8") as f2:
                f2.write(yaml_str)
            log.i("convert yaml from gitbook summary complete, file at: {}".format(yaml_path))
        return 0
    elif args.command == "init":
        log.i("init doc now")
        if not os.path.exists(args.dir):
            os.makedirs(args.dir, exist_ok=True)
        if os.listdir(args.dir):
            log.e("directory {} not empty, please init in empty directory".format(args.dir))
            return 1
        if args.template:
            template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", templates[args.template]["dir"])
        else:
            selected_template = "minimal"
            while 1:
                print("\n====== select template =======\n")
                templates_names = list(templates.keys())
                default_template = None
                for i, template in enumerate(templates_names):
                    default = template if "default" in templates[template] else None
                    if default:
                        default_template = default
                    print(f'{i+1}: {template}{" (default)" if default else ""}: {templates[template]["help"]}')
                n = input(f"\nInput number and press Enter(default {templates_names.index(default_template) + 1}): ")
                if (not n) and default_template:
                    selected_template = default_template
                    break
                try:
                    n = int(n)
                    if n > 0 and n <= len(templates_names):
                        selected_template = templates_names[n - 1]
                        break
                except Exception:
                    pass
            template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", templates[selected_template]["dir"]) 
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
    t_build = None
    log.i(f"teedoc version: {__version__}")
    while 1: # for rebuild all files
        plugins_objs = []
        try:
            # doc source code root path
            doc_src_path = os.path.abspath(args.dir).replace("\\", "/")
            # parse site config
            ok, site_config = parse_site_config(doc_src_path)
            if not ok:
                log.e(site_config)
                return 1
            if "config_template_dir" in site_config:
                config_template_dir = os.path.abspath(os.path.join(doc_src_path, site_config["config_template_dir"])).replace("\\", "/")
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
            log.i("max thread number: {}".format(max_threads_num))
            if args.command in ["build", "serve"]:
                # init plugins
                plugins = list(site_config['plugins'].keys())
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
                    log.i(f"== plugin {plugin} v{module.__version__} ==")
                    plugin_obj = module.Plugin(doc_src_path=doc_src_path, config=plugin_config, site_config=site_config, logger=log, multiprocess = args.multiprocess)
                    plugin_obj.module_path = os.path.abspath(os.path.dirname(module.__file__))
                    plugins_objs.append(plugin_obj)
            # execute command
            if args.command == "install":
                log.i("install, source doc root path: {}".format(doc_src_path))
                log.i("plugins: {}".format(list(site_config["plugins"].keys())))
                curr_path = os.getcwd()
                plugins_dir = None if args.search_dir == "." else args.search_dir
                if plugins_dir and not os.path.exists(plugins_dir):
                    log.e("plugins dir not exist: {}".format(plugins_dir))
                    sys.exit(1)
                for plugin, info in site_config['plugins'].items():
                    path = info["from"]
                    local_path = None
                    if plugins_dir:
                        local_path = utils.find_plugin_in_dir(plugins_dir, plugin)
                    # force install from local source code
                    if local_path:
                        log.i("install plugin <{}> from {}".format(plugin, local_path))
                        cmd = [site_config["executable"]["pip"], "install", "--upgrade", local_path]
                        p = subprocess.Popen(cmd, shell=False)
                        p.communicate()
                        if p.returncode != 0:
                            log.e("install <{}> fail".format(plugin))
                            return 1
                        log.i("install <{}> complete".format(plugin))
                    # install from pypi.org
                    elif (not path) or path.lower() == "pypi":
                        if "version" in info:
                            plugin = f"{plugin}=={info['version']}"
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
                        log.i("Use local plugin <{}> from {}".format(plugin, path))
                os.chdir(curr_path)
                log.i("all plugins install complete")
            elif args.command == "build":
                # parse files
                if not build(doc_src_path, config_template_dir, plugins_objs, site_config=site_config, out_dir=out_dir, log=log,
                            preview_mode=args.preview, max_threads_num=max_threads_num, multiprocess=args.multiprocess, is_build=True):
                    return 1
                add_robots_txt(site_config, out_dir, log)
                log.i("build ok")
            elif args.command == "serve":
                if args.fast:
                    log.w("using fast mode, will build when visit page, blog and search is not supported in this mode")
                layout_usage_queue = MultiQueue() if args.multiprocess else Queue()
                build_lock = threading.Lock()
                # if fast mode, only copy assets
                if not build(doc_src_path, config_template_dir, plugins_objs, site_config=site_config, out_dir=out_dir, log=log,
                            preview_mode = True, max_threads_num = max_threads_num,
                            multiprocess = args.multiprocess,
                            parse_pages = not args.fast,
                            copy_assets = True, is_build = False,
                            layout_usage_queue = layout_usage_queue):
                    return 1
                def build_all():
                    build(doc_src_path, config_template_dir, plugins_objs, site_config=site_config, out_dir=out_dir, log=log,
                            preview_mode = True, max_threads_num = max_threads_num,
                            multiprocess = args.multiprocess,
                            parse_pages = True,
                            copy_assets = False, is_build = False, layout_usage_queue = layout_usage_queue)
                # continue to build all pages
                if args.fast and not t_build:
                    t_build = threading.Thread(target=build_all)
                    t_build.setDaemon(True)
                    t_build.start()
                add_robots_txt(site_config, out_dir, log)
                log.i("build ok")

                host = (args.host, args.port)

                def on_visit(url):
                    if args.fast:
                        path = utils.get_file_path_by_url(url, doc_src_path, site_config["route"], site_config["translate"])
                        if path:
                            log.i(f"visit {url}, update {path}")
                            build_lock.acquire()
                            queue.put([path])
                            build_lock.acquire() # block until build page complete
                            build_lock.release()

                if not t:
                    queue = Queue(maxsize=50)
                    delay_time = (int(site_config["rebuild_changes_delay"]) if "rebuild_changes_delay" in site_config else 3) if int(args.delay) < 0 else int(args.delay)
                    t = threading.Thread(target=files_watch, args=(doc_src_path, site_config, log, delay_time, queue, layout_usage_queue))
                    t.daemon = True
                    t.start()
                    def server_loop(host, log):
                        server = HTTP_Server(host[0], host[1], serve_dir, visit_callback=on_visit)
                        log.i("root dir: {}".format(serve_dir))
                        log.i("Starting server at {}:{} ....".format(host[0], host[1]))
                        if host[0] == "0.0.0.0":
                            log.i("You can visit http://127.0.0.1:{}{}".format(host[1], site_config["site_root_url"]))
                        server.run()

                    if not t2:
                        t2 = threading.Thread(target=server_loop, args=(host, log))
                        t2.daemon = True
                        t2.start()
                # clear file changed queue for rebuild
                while not queue.empty():
                    queue.get()
                while 1:
                    try:
                        files_changed = queue.get(timeout=1)
                    except Empty:
                        continue
                    # detect config.json or site_config.json change, if changed, update all docs file along with the json file
                    files = []
                    docs = []
                    for path in files_changed:
                        # if path.replace(doc_src_path, "")
                        ext = os.path.splitext(path)
                        if ".sw" in ext:
                            log.w("ingnore {} temp file".format(path))
                            continue
                        dir = os.path.dirname(path)
                        file_name = os.path.splitext(path)[0]
                        if file_name.endswith("site_config"): # site_config changed, rebuild all
                            raise RebuildException()
                        elif config_template_dir == dir:      # config template changed, just rebuild all
                            raise RebuildException()
                        elif file_name.endswith("config") or file_name.endswith("sidebar"):    # doc or pages config or sidebar changed, rebuild the changed doc
                            docs.append(os.path.dirname(file_name))
                        else:                                 # normal file, nonly rebuild this file
                            files.append(path)
                    if files:
                        if not build(doc_src_path, config_template_dir, plugins_objs, site_config=site_config, out_dir=out_dir, log=log, update_files = files, preview_mode=True, max_threads_num=max_threads_num, is_build=False, layout_usage_queue = layout_usage_queue):
                            return 1
                        log.i("rebuild ok\n")
                    if docs:
                        if not build(doc_src_path, config_template_dir, plugins_objs, site_config=site_config, out_dir=out_dir, log=log, update_files = [], preview_mode=True, max_threads_num=max_threads_num, is_build=False, layout_usage_queue = layout_usage_queue,
                                    rebuild_docs = docs):
                            return 1
                        log.i("rebuild ok\n")
                    if build_lock.locked():
                        build_lock.release()
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
