import os
import markdown2

class Fake_Logger:
    '''
        use logging module to record log to console or file
    '''
    def __init__(self, level="d", file_path=None, fmt = '%(asctime)s - [%(levelname)s]: %(message)s'):
        pass

    def d(self, *args):
        print(*args)

    def i(self, *args):
        print(*args)

    def w(self, *args):
        print(*args)

    def e(self, *args):
        print(*args)


class Plugin:
    name = "markdown-parser"
    desc = "markdown parser plugin for teedoc"
    defautl_config = {
        "parse_files": ["md"]
    }

    def __init__(self, config = {}, doc_src_path = ".", logger = None):
        '''
            @config a dict object
            @logger teedoc.logger.Logger object
        '''
        self.logger = Fake_Logger() if not logger else logger
        self.doc_src_path = doc_src_path
        self.config = Plugin.defautl_config
        self.config.update(config)
        self.logger.i("-- plugin <{}> init".format(self.name))
        self.logger.i("config: {}".format(self.config))
        

    def parse_files(self, files):
        # result, format must be this
        result = {
            "ok": False,
            "msg": "",
            "htmls": {}
        }
        # function parse md file is disabled
        if not "md" in self.config["parse_files"]:
            result["msg"] = "disabled markdown parse, but only support markdown"
            return result
        self.logger.d("-- plugin <{}> parse files".format(self.name))
        self.logger.d("files: {}".format(files))
        markdown = markdown2.Markdown()
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            print("---", ext)
            if ext.endswith("md"):
                with open(file, encoding="utf-8") as f:
                    html = markdown.convert(f.read())
                    result["htmls"][file] = html
            else:
                result["htmls"][file] = None
        return result

if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)
    res = plug.parse_files(["md_files/basic.md"])
    print(res)
    if not os.path.exists("out"):
        os.makedirs("out")
    for file, html in res["htmls"].items():
        if html:
            file = "{}.html".format(os.path.dirname(file))
            with open(os.path.join("out", file), "w") as f:
                f.write(html)

