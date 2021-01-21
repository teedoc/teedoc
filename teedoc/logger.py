'''
    logger wrapper based oh logging

    @author neucrack
    @license MIT © 2020-2021 neucrack CZD666666@gmail.com
'''



import logging


class Logger():
    '''
        use logging module to record log to console or file
    '''
    def __init__(self, level="d", file_path=None, fmt = '%(asctime)s - [%(levelname)s]: %(message)s'):
        self.log = logging.getLogger("logger")
        formatter=logging.Formatter(fmt=fmt)
        level_ = logging.DEBUG
        if level == "i":
            level_ = logging.INFO
        elif level == "w":
            level_ = logging.WARNING
        elif level == "e":
            level_ = logging.ERROR
        # terminal output
        self.log.setLevel(level_)
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(level_)
        self.log.addHandler(sh)
        # file output
        if file_path:
            fh = logging.FileHandler(file_path, mode="a", encoding="utf-8")#默认mode 为a模式，默认编码方式为utf-8
            fh.setFormatter(formatter)
            fh.setLevel(level_)
            self.log.addHandler(fh)

    def d(self, *args):
        out = ""
        for arg in args:
            out += " " + str(arg)
        self.log.debug(out)

    def i(self, *args):
        out = ""
        for arg in args:
            out += " " + str(arg)
        self.log.info(out)

    def w(self, *args):
        out = ""
        for arg in args:
            out += " " + str(arg)
        self.log.warning(out)

    def e(self, *args):
        out = ""
        for arg in args:
            out += " " + str(arg)
        self.log.error(out)

class Fake_Logger():
    '''
        use logging module to record log to console or file
    '''
    def __init__(self, level="d", file_path=None, fmt = '%(asctime)s - [%(levelname)s]: %(message)s'):
        pass

    def d(self, *args):
        pass

    def i(self, *args):
        pass

    def w(self, *args):
        pass

    def e(self, *args):
        pass


if __name__ == "__main__":
    import os
    log = Logger(file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.log"))
    log.d("debug", "hello")
    log.i("info:", 1)
    log.w("warning")
    log.e("error")



