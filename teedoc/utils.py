import re
from collections import OrderedDict


def sidebar_summary2dict(content):
    '''
        convert gitbook summary.md to dict
    '''
    def parse_line(line):
        match = re.findall(r"\[(.*)\]\((.*)\)", line, flags=re.M)
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
            if line.startswith("\t* "):
                level_mark = "\t"
            elif line.startswith(" * "):
                level_mark = " "
            elif line.startswith("  * "):
                level_mark = "  "
            elif line.startswith("    * "):
                level_mark = "    "
            if not level_mark is None:
                print("level symbol--{}--".format(level_mark))
        if line.startswith("## "): # label
            item = {
                "label": line.strip()[3:]
            }
            sidebar_items.append(item)
        elif line.startswith("* "): # link
            label, url, url_type = parse_line(line)
            item = {
                "label": label
            }
            item[url_type] = url
            sidebar_items.append(item)
        elif line.startswith("{}* ".format(level_mark)): # level 2 label
            label, url, url_type = parse_line(line)
            item = {
                "label": label,
                url_type: url
            }
            if not "items" in sidebar_items[-1]:
                sidebar_items[-1]["items"] = []
            sidebar_items[-1]["items"].append(item)
        elif line.startswith("{}{}* ".format(level_mark, level_mark)): # level 3 label
            label, url, url_type = parse_line(line)
            item = {
                "label": label,
                url_type: url
            }
            if not "items" in sidebar_items[-1]["items"][-1]:
                sidebar_items[-1]["items"][-1]["items"] = []
            sidebar_items[-1]["items"][-1]["items"].append(item)
        elif line.startswith("{}{}{}* ".format(level_mark, level_mark, level_mark)): # level 4 label
            label, url, url_type = parse_line(line)
            item = {
                "label": label,
                url_type: url
            }
            if not "items" in sidebar_items[-1]["items"][-1]["items"][-1]:
                sidebar_items[-1]["items"][-1]["items"][-1]["items"] = []
            sidebar_items[-1]["items"][-1]["items"][-1]["items"].append(item)
        elif line.startswith("{}{}{}{}* ".format(level_mark, level_mark, level_mark, level_mark)): # level 5 label
            label, url, url_type = parse_line(line)
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

