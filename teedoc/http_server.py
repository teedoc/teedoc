
import os
from flask import Flask, send_file, Response, request
import logging


class HTTP_Server:
    def __init__(self, host, port, serve_dir, visit_callback=lambda x:None):
        self.app = Flask("teedoc", static_folder=os.path.join(serve_dir, "static"))
        self.host = host
        self.port = port
        self.root = serve_dir
        self.on_visit = visit_callback
        self.app.add_url_rule("/", view_func=self.view_root)
        self.app.add_url_rule("/<path:path>", view_func=self.view_root)
        # disable logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        # self.app.logger.disabled = True
        # log.disabled = True


    def view_root(self, path="/"):
        if request.method == "GET":
            self.on_visit(path)
        if path.endswith("/"):
            path = f'{path}index.html'
        if path.startswith("/"):
            path = path[1:]
        path = os.path.abspath(os.path.join(self.root, path)).replace("\\", "/")
        if not path.startswith(self.root):
            return Response(status=403)
        if not os.path.exists(path):
            if not path.endswith(".html"):
                path = path + ".html"
            if not os.path.exists(path):
                page_404 = os.path.join(self.root, "404.html")
                content_404 = ""
                if not os.path.exists(page_404):
                    self.on_visit("/404.html")
                if os.path.exists(page_404):
                    with open(page_404, encoding="utf-8") as f:
                        content_404 = f.read()
                return Response(content_404, status=404)
        return send_file(path)

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=False)


