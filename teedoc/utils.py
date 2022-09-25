import re, os
from collections import OrderedDict
import shutil
import requests
import subprocess
from datetime import datetime

has_git = False

def sidebar_summary2dict(content):
    '''
        convert gitbook summary.md to dict
    '''
    def parse_line(line, start=""):
        match = re.findall(r"\[(.*)\]\((.*)\)", line, flags=re.M)
        if not match:
            return line, "#", "url"
        label = match[0][0].strip()
        url = match[0][1].strip()
        if url.endswith(".md") or url.endswith(".ipynb"):
            url_type = "file"
        else:
            url_type = "url"
        return label, url, url_type

    # remove comment
    def re_del(c):
        return ""
    content = re.sub(r'<!--.*?-->', re_del, content, flags=re.M|re.S)
    # remove h1
    content = re.sub(r"^# .*", re_del, content, flags=re.I)

    content = content.split("\n")

    level_mark = None
    sidebar_items = []
    for i, line in enumerate(content):
        if line.strip() == "":
            continue
        if level_mark is None:
            if line.startswith("\t* ") or line.startswith("\t- "):
                level_mark = "\t"
            elif line.startswith(" * ") or line.startswith(" - "):
                level_mark = " "
            elif line.startswith("  * ") or line.startswith("  - "):
                level_mark = "  "
            elif line.startswith("    * ") or line.startswith("    - "):
                level_mark = "    "
            if not level_mark is None:
                print("level symbol:=={}==".format(level_mark))
        if line.startswith("## "): # label
            item = {
                "label": line.strip()[3:]
            }
            sidebar_items.append(item)
        elif line.startswith("* ") or line.startswith("- "): # link
            label, url, url_type = parse_line(line[2:])
            item = {
                "label": label
            }
            item[url_type] = url
            sidebar_items.append(item)
        elif line.startswith("{}* ".format(level_mark)) or line.startswith("{}- ".format(level_mark)): # level 2 label
            label, url, url_type = parse_line(line[len(level_mark)+2:])
            item = {
                "label": label,
                url_type: url
            }
            if not "items" in sidebar_items[-1]:
                sidebar_items[-1]["items"] = []
            sidebar_items[-1]["items"].append(item)
        elif line.startswith("{}{}* ".format(level_mark, level_mark)) or line.startswith("{}{}- ".format(level_mark, level_mark)): # level 3 label
            label, url, url_type = parse_line(line[len(level_mark) * 2 + 2:])
            item = {
                "label": label,
                url_type: url
            }
            if not "items" in sidebar_items[-1]["items"][-1]:
                sidebar_items[-1]["items"][-1]["items"] = []
            sidebar_items[-1]["items"][-1]["items"].append(item)
        elif line.startswith("{}{}{}* ".format(level_mark, level_mark, level_mark)) or line.startswith("{}{}{}- ".format(level_mark, level_mark, level_mark)): # level 4 label
            label, url, url_type = parse_line(line[len(level_mark) * 3 + 2:])
            item = {
                "label": label,
                url_type: url
            }
            if not "items" in sidebar_items[-1]["items"][-1]["items"][-1]:
                sidebar_items[-1]["items"][-1]["items"][-1]["items"] = []
            sidebar_items[-1]["items"][-1]["items"][-1]["items"].append(item)
        elif line.startswith("{}{}{}{}* ".format(level_mark, level_mark, level_mark, level_mark)) or line.startswith("{}{}{}{}- ".format(level_mark, level_mark, level_mark, level_mark)): # level 5 label
            label, url, url_type = parse_line(line[len(level_mark) * 4 + 2:])
            item = {
                "label": label,
                url_type: url
            }
            if not "items" in sidebar_items[-1]["items"][-1]["items"][-1]["items"][-1]:
                sidebar_items[-1]["items"][-1]["items"][-1]["items"][-1]["items"] = []
            sidebar_items[-1]["items"][-1]["items"][-1]["items"][-1]["items"].append(item)
    sidebar = {
        "items": sidebar_items
    }
    return sidebar

def update_config(old, update, level = 0, ignore=[]):
    '''
        update config by new config, merge a new config
        if value of key is list and item is dict, new config will append,
        but if dict has "id" key, it will be update, e.g.
        ```
            "g": [
                {
                    "id": "id0",
                    "h": 123
                },
                {
                    "h": 123
                }
            ]
        ```
        update with
        ```
            "g":[
                {
                    "id": "id0",
                    "h": 789
                },
                {
                    "h": 234
                }
            ]
        ```
        will be 
        ```
            'g': [
                {
                   'id': 'id0',
                   'h': 789
                }, {
                   'h': 123
                }, {
                   'h': 234
                }
            ]
        ```
    '''
    new = old.copy()
    for key in update.keys():
        if key in ignore:
            continue
        if not key in old:
            new[key] = update[key]
            continue
        if type(update[key]) == dict:
            new[key] = update_config(old[key], update[key], level + 1)
        elif type(update[key]) == list and len(update[key]) > 0 and type(update[key][0]) == dict:
            # some dict in list, add item, or replace if exist id
            # convert list to OrderedDict
            old_list_item = OrderedDict()
            for i, item in enumerate(old[key]):
                if "id" in item:
                    old_list_item[item["id"]] = item
                else:
                    old_list_item[str(i)] = item
            # update item
            for i, item in enumerate(update[key]):
                if "id" in item:
                    if type(old_list_item[item["id"]]) == dict:
                        old_list_item[item["id"]] = update_config(old_list_item[item["id"]], item, level + 1)
                    else:
                        old_list_item[item["id"]] = item
                else:
                    old_list_item["n{}".format(i)] = item
            # convert back to list
            items = []
            for id in old_list_item:
                items.append(old_list_item[id])
            new[key] = items
        else:
            new[key] = update[key]
    return new


def check_sidebar_diff(a, b, urla, urlb, dira, dirb, doc_root, log):
    '''
        @a {
            "file_path": {
                "curr": (url, label),     # e.g. ('/get_started/zh/index.html', 'teedoc 简介')
                "previous": (url, label),
                "next": (url, label),
            }
        }
        @b {
            "file_path": {
                "file": "sidebar file item",  # e.g. install/README.md
                "curr": (url, label),         # e.g. ('/get_started/zh/index.html', 'teedoc 简介')
                "previous": (url, label),
                "next": (url, label),
            }
        }
        @urla, urlb e.g. "/get_started/zh/", "/get_started/en/"
    '''
    for f in a:
        w = False
        itema = a[f]
        k = f.replace(dira, dirb)
        if not k in b:
            w = True
        else:
            itemb = b[k]
            if itema["file"] != itemb["file"]:
                w = True
        if w:
            log.w(f'doc <{dira.replace(doc_root, "")}> and translate <{dirb.replace(doc_root, "")}> sidebar item [{itema["file"]}-"{itema["curr"][1]}"] different')


def get_url_by_file_rel(file_path, doc_url = "", rel = False):
    '''
        @rel relative url
    '''
    url = os.path.splitext(file_path)[0]
    tmp = os.path.split(url)
    if tmp[1].lower() == "readme":
        url = "{}/index".format(tmp[0])
        if url.startswith("/"):
            url = url[1:]
    url = url + ".html"
    if rel:
        return url
    if(doc_url.endswith("/")):
        url = "{}{}".format(doc_url, url)
    else:
        url = "{}/{}".format(doc_url, url)
    return url

def get_file_path_by_url(url, doc_root, route, translate):
    if not url.startswith("/"):
        url = "/" + url
    map = {}
    for k, v in route.items():
        if type(v) != dict:
            raise Exception(f"site_config error, route {k}'s value should be dict")
        for _url, _path in v.items():
            map[_url] = _path
    for k, v in translate.items():
        for _url, trans in v.items():
            for item in trans:
                map[item["url"]] = item["src"]
    def find_url_dir(url, map):
        # /, /, /soft/maixpy3/, /soft/maixpy3/api/
        url_dir = "/".join(url[:-1].split("/")[:-1]) + "/" # map: /, /, /soft/maixpy3/, /soft/maixpy3/
        if url_dir in map:
            return url_dir
        if url_dir == "/":
            raise Exception("site_config route no url '/' item")
        url_dir = find_url_dir(url_dir, map)
        return url_dir
    
    def get_src_file_path(base_name, dir):
        suportted_ext = ["md", "ipynb"] # TODO: this should be update by plugins
        path = None
        for ext in suportted_ext:
            _path = os.path.join(dir, base_name) + "." + ext
            if os.path.exists(_path):
                path = _path
                break
        if not path: # find other ext files with same file name
            file_name = os.path.basename(base_name)
            for name in os.listdir(os.path.dirname(os.path.join(dir, base_name))):
                if name.lower().startswith(file_name.lower()):
                    base_name_dir = os.path.dirname(base_name)
                    if base_name_dir:
                        base_name = base_name_dir + "/" + name
                    else:
                        base_name = name
                    path = os.path.join(dir, base_name)
                    break
        if path:
            path = path.replace("\\", "/")
        return path

    if url in map: # /, /maixpy/, /soft/maixpy3/
        path = get_src_file_path("index", map[url][1])
        if not path:
            path = get_src_file_path("readme", map[url][1])
    else: # /index.html, /maixpy, /soft/maixpy3/start.html, /soft/maixpy3/api/start.html
        url_dir = find_url_dir(url, map)
        dir = map[url_dir][1]
        base_name = url.replace(url_dir, "") # index.html, maixpy, start.html, api/start.html
        base_name = os.path.splitext(base_name)[0]
        path = get_src_file_path(base_name, dir)
    return path


def convert_file_tag_items(items, out_dir, plugin_name):
    '''
        @items list, abs path or str, or dict:{
                    "path": "/home/abc/test.js",
                    "options": ["async"]
                }
        @out_dir copy items to `save_dir/plugin_name/`
    '''
    new = []
    save_dir = os.path.join(out_dir, plugin_name)
    os.makedirs(save_dir, exist_ok=True)
    for item in items:
        options = []
        if type(item) == dict:
            path = item["path"]
            options = item["options"]
        else:
            path = item
        if os.path.exists(path):
            name = os.path.basename(path)
            url = f'/{plugin_name}/{name}'
            shutil.copyfile(path, os.path.join(save_dir, name))
            file_type = os.path.splitext(name)[1][1:]
            if file_type == "js":
                item = f'<script src="{url}"'
                for opt in options:
                    item += f' {opt}'
                item += '></script>'
            elif file_type == "css":
                item = f'<link rel="stylesheet" href="{url}"'
                for opt in options:
                    item += f' {opt}'
                item += 'type="text/css"/>'
        new.append(item)
    return new

def download_file(url, save_path):
    '''
        @url download url
        @save_path save file to `save_path`
    '''
    if not os.path.exists(save_path):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        res = requests.get(url)
        if res.status_code != 200:
            raise Exception("Download file: {} failed".format(url))
        f.write(res.content)

def get_file_last_modify_time(file_path, git=True):
    last_edit_time = None
    if has_git and git:
        cmd = ["git", "log", "-1", "--format=%cd", "--date", "iso8601-strict", f"{file_path}"]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        output, err = p.communicate()
        if p.returncode == 0:
            date_str = output.decode("utf-8").strip()
            if date_str:
                last_edit_time = datetime.fromisoformat(date_str)
    if not last_edit_time: # this time is not accurate, just for outside of git repository's file
        last_edit_time = datetime.fromtimestamp(os.stat(file_path).st_mtime)
    return last_edit_time

def check_git():
    global has_git
    cmd = ["git", "--version"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    output, err = p.communicate()
    if p.returncode != 0:
        has_git = False
        return False
    has_git = True
    return True

if __name__ == "__main__":
    a = {
        "a": 1,
        "b": 2,
        "c": {
            "d": 3,
            "e": {
                "f": 4
            }
        },
        "g": [
            {
                "id": "id0",
                "h": 123
            },
            {
                "h": 123
            }
        ]
    }

    b = {
        "c": {
            "e": 5
        },
        "a": [1, 2, 3],
        "g":[
            {
                "id": "id0",
                "h": 789
            },
            {
                "h": 234
            }
        ]
    }
    c = update_config(a, b)
    print(c)

