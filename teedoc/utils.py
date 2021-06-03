import re


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


