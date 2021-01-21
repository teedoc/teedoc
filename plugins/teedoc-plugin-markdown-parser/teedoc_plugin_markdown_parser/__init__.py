
class Plugin:
    def __init__(self, doc_src_path, logger):
        '''
            @param logger teedoc.logger.Logger object
        '''
        self.logger = logger
        self.doc_src_path = doc_src_path
        print("-- plugin init")
    
    def build(self):
        print("-- plugin build")


