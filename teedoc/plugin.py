from .logger import Fake_Logger
import os
from collections import OrderedDict

class Plugin_Base:
    '''
        call sequence:
            __init__
            on_init
                (for parse in docs/pages/blog)
                on_parse_start
                on_add_html_header_items
                on_add_html_footer_js_items
                on_html_template
                on_html_template_i18n_dir
                    (new multiprocess or threads)
                    on_new_process_init (only multiprocess)
                    on_parse_files / on_parse_pages / on_parse_blog
                    on_add_navbar_items
                    on_render_vars
                    on_new_process_del (only multiprocess)
                on_parse_end
            on_htmls
            on_copy_files
            on_del
            __del__
    '''
    name = "markdown-plugin"
    desc = "markdown plugin for teedoc"
    defautl_config = {
    }

    def __init__(self, config, doc_src_path, site_config, logger = None, multiprocess = True, **kw_args):
        '''
            @attention DO NOT overwrite this function, if have to, please call super().__init__() first
            @config a dict object
            @logger teedoc.logger.Logger object
            @multiprocess multiple process mode is enabled or not,
                          in multiple process mode, all vars have a copy,
                          but thread mode them share the memory, so, be careful to use variables in new threads or new process
        '''
        self._pid = os.getpid()
        self.on_init(config, doc_src_path, site_config, logger, multiprocess = multiprocess, **kw_args)

    def on_init(self, config, doc_src_path, site_config, logger, multiprocess = True, **kw_args):
        '''
            @config a dict object
            @logger teedoc.logger.Logger object
            @multiprocess multiple process mode is enabled or not,
                          in multiple process mode, all vars have a copy,
                          but thread mode them share the memory, so, be careful to use variables in new threads or new process
        '''
        pass

    def on_parse_start(self, type_name, url, dirs, doc_config, new_config):
        '''
            call when start parse one doc
            @type_name canbe "doc" "page" "blog"
            #url doc url, e.g. /get_started/zh/
            @doc_config config of doc, get from config.json or config.yaml
            @new_config this plugin's config from doc_config
        '''
        # can update plugin config from site_config with new_config by teedoc.utils.update_config
        # self.new_config = copy.deepcopy(self.config)
        # self.new_config = update_config(self.new_config, new_config)
        pass

    def on_parse_end(self):
        pass

    def on_copy_files(self):
        '''
            copy file to out directory, when file changes, it also will be called
            @return dict object, keyword is url, value is file path
                    {
                        "/static/css/theme-default.css": "{}/theme-default.css".format(assets_abs_path)
                    }
                    how to get assets_abs_path see teedoc-plugin-theme-default
        '''
        return {}

    def on_htmls(self, htmls_files, htmls_pages, htmls_blog=None):
        '''
            update htmls, may not all html, just partially, DO NOT change params' value, read only, or will lead to other plugins error
            htmls_files: {
                "/get_started/zh":{
                    "url":{
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html,
                                "url": "",
                                "raw": ""
                          }
                }
            }
            htmls_blog: {
                "/blog/":{
                    "url":{
                                "title": "",
                                "desc": "",
                                "keywords": [],
                                "body": html,
                                "tags": [],
                                "url": "",
                                "raw": "",
                                "date": date,
                                "ts": 12344566,
                                "author": author,
                                "brief": "",
                                "metadata": {}
                          }
                }
            }
        '''
        return True

    def __del__(self):
        # DO NOT implement this function, use on_end() instead !!!!!! this functioin may be called multi times
        if os.getpid() == self._pid:
            self.on_del()

    def on_del(self):
        pass

    def on_html_template(self, type_name):
        '''
            call when render html
            @type_name canbe "doc" "page" "blog"
            @return None or template file abs path,
                    and teedoc will auto search templates in the dir of this file
        '''
        return None

    def on_add_html_header_items(self, type_name):
        '''
            add js(/or other tags) items to head tag, should be a html tag, e.g.
                <link rel="stylesheet" href="..." type="text/css"/>
                <script src="..."></script>
            @type_name canbe "doc" "page" "blog"
        '''
        return []
    
    def on_add_html_footer_js_items(self, type_name):
        '''
            add js(/or other tags) items to end of body, should be a html tag, e.g.
                <script src="..."></script>
            @type_name canbe "doc" "page" "blog"
        '''
        return []

    def on_html_template_i18n_dir(self, type_name):
        '''
            html template's i18n dir, dir generated by:
              * babel(http://babel.pocoo.org/en/latest/cmdline.html)
              * gettext tool like official https://www.gnu.org/software/gettext/
              * others like powdit(https://github.com/vslavik/poedit)
            dir structure should be like:
            ```
                locales
                    ├── messages.pot
                    ├── zh_CN
                    │   └── LC_MESSAGES
                    │       └── messages.po
                    └── zh_TW
                        └── LC_MESSAGES
                            └── messages.po
            ```
            generate by babel for example:
            ```
                mkdir -p locales
                pybabel extract -F babel.cfg -o locales/messages.pot ./
                pybabel init -i locales/messages.pot -d locales -l zh_CN
                pybabel compile -d locales -l zh_CN
            ```
            babel.cfg:
            ```
                [python: **.py]

                [jinja2: **.html]
                extensions=jinja2.ext.i18n
            ```
            @type_name canbe "doc" "page" "blog"
            @return i18n translate dir, default locales relative to plugin dir
        '''
        return os.path.join(self.module_path, "locales") # self.module_path set when object created


    ############### run in new process start ######################

    def on_new_process_init(self):
        '''
            for multiple processing, for below func, will be called in new process,
            every time create a new process, this func will be invoke
            @attention only call in multiple process mode on, thread mode not call this func
                        in multiple process mode, all vars have a copy, but thread mode them share the memory, so, be careful
        '''
        pass

    def on_new_process_del(self):
        '''
            for multiple processing, for below func, will be called in new process,
            every time exit a new process, this func will be invoke
            @attention only call in multiple process mode on, thread mode not call this func
                        in multiple process mode, all vars have a copy, but thread mode them share the memory, so, be careful
        '''
        pass
        

    def on_parse_files(self, files):
        '''
            result = {
                "ok": False,
                "msg": "",
                "htmls": {
                    "file1_path": {
                                    "title": "",
                                    "desc": "",
                                    "keywords": [],
                                    "tags": [],
                                    "body": "",
                                    "toc": "", # just empty, toc generated by js but not python
                                    "metadata": {
                                        "title":"",
                                        "keywords": "1, 2, 3",
                                        "desc": "",
                                        "tags": "1, 2, 3",
                                        "id": "",
                                        "class": ", , , ",
                                        "show_source": "true"
                                        },
                                    "raw": content
                                 }
            }
        '''
        # result = {
        #     "ok": False,
        #     "msg": "",
        #     "htmls": OrderedDict()
        # }
        return None
    
    def on_parse_pages(self, pages):
        return None

    def on_parse_blog(self, pages):
        return None

    def on_add_navbar_items(self):
        '''
            @return list items(navbar item, e.g. "<a href=></a>")
        '''
        return []

    def on_render_vars(self, vars : dict):
        '''
            call when render html page by jinja2
            @vars  dict object, you can add variables or change variables in this callback
            @return dict object
        '''
        return vars

    ############### run in new process end ######################

    ####################### utils ###############################
    def update_file_var(self, files, vars, temp_dir):
        for url, path in files.items():
            with open(path, encoding='utf-8') as f:
                content = f.read()
                for k, v in vars.items():
                    content = content.replace("${}{}{}".format("{", k.strip(), "}"), v)
                temp_path = os.path.join(temp_dir, os.path.basename(path))
                with open(temp_path, "w", encoding='utf-8') as fw:
                    fw.write(content)
                files[url] = temp_path
        return files

