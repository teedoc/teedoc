import os
import gettext
import babel
from collections import OrderedDict

babel_cfg_default = """
# format see https://babel.pocoo.org/en/latest/messages.html

[python: **.py]

[jinja2: **.html]
extensions=jinja2.ext.i18n

"""

locales_cfg_default = """
locales=["zh", "en"]
"""

root_dir = os.path.abspath(os.path.dirname(__file__))
locale = "en"

tr = lambda x:x

def _(text):
    return tr(text)

def set_locale(locale_in):
    global locale, tr, root_dir
    print("-- set locale to", locale_in)
    locale = locale_in
    locales_path = os.path.join(root_dir, 'locales')
    if not os.path.exists(locales_path): # for pyinstaller pack
        locales_path = os.path.join(os.path.dirname(root_dir), 'locales')
    # check translate binary file
    mo_path = os.path.join(locales_path, "en", "LC_MESSAGES", "messages.mo")
    if not os.path.exists(mo_path):
        main("finish")
    lang = gettext.translation('messages', localedir=locales_path, languages=[locale])
    tr = lang.gettext

def get_languages(locales):
    languages = OrderedDict()
    for locale in locales:
        obj = babel.Locale.parse(locale)
        languages[locale] = obj.language_name + (" " + obj.script_name if obj.script_name else "")
    return languages

def extract(src_path, config_file_path, out_path):
    from babel.messages.frontend import extract_messages
    cmdinst = extract_messages()
    cmdinst.initialize_options()
    cmdinst.mapping_file = config_file_path
    cmdinst.output_file = out_path
    cmdinst.input_paths = src_path
    cmdinst.omit_header = True
    cmdinst.header_comment = "#"
    try:
        cmdinst.ensure_finalized()
        cmdinst.run()
    except Exception as err:
        raise err

def init(template_path, out_dir, locale, domain="messages"):
    from babel.messages.frontend import init_catalog
    cmdinst = init_catalog()
    cmdinst.initialize_options()
    cmdinst.input_file = template_path
    cmdinst.output_dir = out_dir
    cmdinst.locale = locale
    cmdinst.domain = domain
    try:
        cmdinst.ensure_finalized()
        cmdinst.run()
    except Exception as err:
        raise err

def update(template_path, out_dir, locale, domain="messages"):
    from babel.messages.frontend import update_catalog
    cmdinst = update_catalog()
    cmdinst.initialize_options()
    cmdinst.input_file = template_path
    cmdinst.output_dir = out_dir
    cmdinst.omit_header = True
    cmdinst.locale = locale
    cmdinst.domain = domain
    try:
        cmdinst.ensure_finalized()
        cmdinst.run()
    except Exception as err:
        raise err

def compile(translate_dir, locale, domain="messages"):
    from babel.messages.frontend import compile_catalog
    cmdinst = compile_catalog()
    cmdinst.initialize_options()
    cmdinst.directory = translate_dir
    cmdinst.locale = locale
    cmdinst.domain = domain
    try:
        cmdinst.ensure_finalized()
        cmdinst.run()
    except Exception as err:
        raise err


def rm_po_meta(po_path):
    with open(po_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(po_path, "w", encoding="utf-8") as f:
        start_line = 0
        start = False
        for i, line in enumerate(lines):
            if line.startswith("msgid"):
                start = True
                continue
            if start and line.startswith('#'):
                start_line = i
                break
        lines = lines[start_line:]
        lines.insert(0, '#\nmsgid ""\nmsgstr ""\n\n')
        f.writelines(lines)


def main(cmd, root_dir, cfg_path=None, locales_path=None, locales=None, rm_meta=False):
    ret = 0
    root_dir = os.path.abspath(root_dir)
    if not os.path.exists(root_dir):
        print("path {} not exists".format(root_dir))
        return -1
    cfg_path_final = cfg_path if cfg_path else os.path.join(root_dir, "i18n_babel.cfg")
    locales_path_final = locales_path if locales_path else os.path.join(root_dir, "i18n_locales.cfg")
    if not os.path.exists(cfg_path_final):
        print("cfg path {} not exists".format(cfg_path_final))
        return -1
    if not os.path.exists(locales_path_final):
        print("locales path {} not exists".format(locales_path_final))
        return -1
    # read locales config(locales variable in locales_path_final file)
    if not locales:
        locales = []
        with open(locales_path_final, "r", encoding="utf-8") as f:
            g = {}
            exec(f.read(), g)
            locales = g["locales"]

    cwd = os.getcwd()
    os.chdir(root_dir)
    if cmd == "prepare":
        print("-- translate locales: {}".format(locales))
        print("-- extract keys from files")
        if not os.path.exists("locales"):
            os.makedirs("locales")
        # os.system("pybabel extract -F babel.cfg -o locales/messages.pot ./")
        extract("./", cfg_path_final, "locales/messages.pot")
        print("-- extract keys from files done")
        for locale in locales:
            print("-- generate {} po files from pot files".format(locale))
            if os.path.exists('locales/{}/LC_MESSAGES/messages.po'.format(locale)):
                print("-- file already exits, only update")
                # "pybabel update -i locales/messages.pot -d locales -l {}".format(locale)
                update("locales/messages.pot", "locales", locale)
            else:
                print("-- file not exits, now create")
                # "pybabel init -i locales/messages.pot -d locales -l {}".format(locale)
                init("locales/messages.pot", "locales", locale)
            # remove meta info from header first msgid to charactor "#"
            if rm_meta:
                rm_po_meta("locales/{}/LC_MESSAGES/messages.po".format(locale))
            print("-- generate {} po files done".format(locale))
    elif cmd == "finish":
        print("-- translate locales: {}".format(locales))
        for locale in locales:
            print("-- generate {} mo file from po files".format(locale))
            # "pybabel compile -d locales -l {}".format(locale)
            compile("locales", locale)
        print("-- generate mo files done")
    elif cmd == "all":
        ret = main("prepare", root_dir, cfg_path, locales_path, locales=locales, rm_meta=rm_meta)
        if ret == 0:
            ret = main("finish", root_dir, cfg_path, locales_path, locales=locales, rm_meta=rm_meta)
            if ret != 0:
                print("finish failed")
        else:
            print("prepare failed")
    os.chdir(cwd)
    return ret


def cli_main():
    import argparse
    parser = argparse.ArgumentParser("tranlate tool")
    parser.add_argument("-p", "--path", default="", help="path to the root translation directory, locales dir will be created in this path")
    parser.add_argument("-c", "--cfg", default="", help="path to the babel config file, by default will create i18n_babel.cfg in the root path")
    parser.add_argument("-l", "--locales", default="", help="path to the locales config file, by default will create i18n_locales.cfg in the root path")
    parser.add_argument("--rm_meta", action="store_true", help="remove meta info in the po file")
    parser.add_argument("cmd", type=str, choices=["prepare", "finish", "all"], default="all")
    args = parser.parse_args()
    main(args.cmd, args.path, args.cfg, args.locales, rm_meta = args.rm_meta)

if __name__ == "__main__":
    cli_main()
