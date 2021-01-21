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

    def __init__(self, config = None, doc_src_path = ".", logger = None):
        '''
            @param logger teedoc.logger.Logger object
        '''
        self.logger = Fake_Logger() if not logger else logger
        self.doc_src_path = doc_src_path
        self.config = config
        self.logger.i("-- plugin <{}> init".format(self.name))
        self.logger.i("config: {}".format(self.config))
        

    def build(self):
        self.logger.i("-- plugin <{}> build".format(self.name))
    
    def on_files_change(self, files):
        self.logger.i("-- plugin <{}> on_files_change".format(self.name))

if __name__ == "__main__":
    config = {
    }
    plug = Plugin(config=config)
    plug.build()
    print(plug.name)

