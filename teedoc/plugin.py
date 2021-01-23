from logger import Fake_Logger

class Plugin_Base:
    name = "markdown-plugin"
    desc = "markdown plugin for teedoc"
    defautl_config = {
    }

    def __init__(self, config = {}, doc_src_path = ".", logger = None):
        '''
            @config a dict object
            @logger teedoc.logger.Logger object
        '''
        self.logger = Fake_Logger() if not logger else logger
        self.doc_src_path = doc_src_path
        

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
                                    "body": html
                                 }
            }
        '''
        return None
    
    def on_parse_pages(self, pages):
        return None
    
    def on_add_html_header_items(self):
        return []
    
    def on_add_navbar_items(self):
        '''
            @return list items(navbar item, e.g. "<a href=></a>")
        '''
        return ["<a>sassss</a>"]

