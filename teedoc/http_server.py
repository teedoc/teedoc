
from http.server import HTTPServer
import sys

class HTTP_Server(HTTPServer):
    def __init__(self, host, handler):
        super(HTTPServer, self).__init__(host, handler)

    def handle_error(self, request, client_address):
        """Handle an error gracefully.  May be overridden.

        The default is to print a traceback and continue.

        """
        err_type = sys.exc_info()[0]
        if err_type == ConnectionAbortedError or err_type == BrokenPipeError or err_type == ConnectionResetError:
            return
        print('-'*40, file=sys.stderr)
        print('Exception occurred during processing of request from',
            client_address, file=sys.stderr)
        import traceback
        traceback.print_exc()
        print('-'*40, file=sys.stderr)



