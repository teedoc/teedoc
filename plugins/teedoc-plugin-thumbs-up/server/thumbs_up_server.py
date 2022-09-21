'''
    Simple HTTP Server example for teedoc-plugin-thumbs-up plugin
    run by:
        FEISHU_BOT_TOKEN=xxx python3 thumbs_up_server.py
'''

import flask
from flask_cors import CORS
import datetime
import json
import os
import glob
import time
import argparse
import signal
import sys
try:
    from .feishu import send_msg
except:
    from feishu import send_msg

argparser = argparse.ArgumentParser()
argparser.add_argument("-d", "--save-dir", default="logs", help="save thumbs up data dir")
argparser.add_argument("-m", "--max-num", default=10000, type=int, help="max record num, page num more than this num will report as error")
argparser.add_argument("-t", "--interval", default=60*60*24, type=int, help="interval time to save record data, unit is second") 
argparser.add_argument("-p", "--port", default=5000, type=int, help="server port")
argparser.add_argument("-H", "--host", default="0.0.0.0", help="server host")
argparser.add_argument("--feishu", default=None, help="feishu webhook url or token")

args = argparser.parse_args()

save_dir = args.save_dir
save_interval = args.interval
max_record_num = args.max_num

app = flask.Flask(__name__)

# Allow CORS
CORS(app, supports_credentials=True)

class Thumbs_Up:
    def __init__(self, up_callback=lambda path,url:None, down_callback=lambda path, msg, url:None, mem_full_callback=lambda :None):
        self.data = {
            # "path": {
            #     "up": 0,
            #     "down": 0
            # }
        }
        self.on_mem_full_error = mem_full_callback
        self.on_up = up_callback
        self.on_down = down_callback
        self.load_latest(save_dir)
        self.last_save_time = time.time()

    def get(self, path):
        if path not in self.data:
            if len(self.data) > max_record_num:
                self.on_mem_full_error()
                return None
            self.data[path] = {
                "up": 0,
                "down": 0,
                "advices": []
            }
        return self.data[path]

    def up(self, path, url):
        data = self.get(path)
        if not data:
            return None
        data["up"] += 1
        print("-- up", path, data)
        self.on_up(path, url)
        return data

    def down(self, path, msg, url):
        data = self.get(path)
        if not data:
            return None
        data["down"] += 1
        data["advices"].append(msg)
        print("-- down", path, data)
        self.on_down(path, msg, url)
        return data

    def save(self, save_dir, save_now=False):
        if not save_now:
            if time.time() - self.last_save_time < save_interval:
                return
        if time.time() - self.last_save_time < 5: # for multiple save in short time, like signal trigger
            return
        datetime_now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, f"thumbs_up_{datetime_now_str}.json")
        print("-- save, data num:", len(self.data))
        with open(path, "w",) as f:
            json.dump(self.data, f, ensure_ascii=False)
        self.last_save_time = time.time()

    def load_latest(self, save_dir):
        files = glob.glob(os.path.join(save_dir, "thumbs_up_*.json"))
        if len(files) == 0:
            return
        files.sort()
        latest_file = files[-1]
        print("-- open latest log file:", latest_file)
        with open(latest_file, "r",) as f:
            self.data = json.load(f)
            print("-- load data:", self.data)

def on_up(path, url):
    print("-- on_up", path)
    msg = f'Thumbs up: {url}'
    try:
        send_msg(msg, args.feishu)
    except:
        print("-- send msg error")

def on_down(path, msg, url):
    print("-- on_down", path)
    msg = f'Thumbs down: {url}\n{msg}'
    try:
        send_msg(msg, args.feishu)
    except:
        print("-- send msg error")

def on_mem_full_error():
    print("-- on_mem_full_error")
    msg = "Fatal error, reach max record num, check if have attack or too much pages"
    try:
        send_msg(msg, args.feishu)
    except:
        print("-- send msg error")

thumbs_up_recorder = Thumbs_Up(on_up, on_down, on_mem_full_error)

def check_path(path):
    '''
        convert different path but the same page to the same path
        e.g.
            /get_started/zh/ -> /get_started/zh/index.html
            /get_started/zh/write -> /get_started/zh/write.html
    '''
    if not path:
        return path
    if path.endswith("/"):
        path = path + "index.html"
    elif len(path.split("/")[-1].split(".")) == 1:
        path = path + ".html"
    return path

def check_msg_valid(msg):
    if len(msg) < 10 or len(msg) > 256:
        return None
    return msg

@app.route('/api/thumbs_up', methods=['POST'])
def thumbs_up():
    data = flask.request.get_json()
    path = check_path(data.get("path"))
    url = data.get("url")
    if not path:
        return flask.jsonify({
            "code": 1,
            "msg": "path is required"
        })
    data = thumbs_up_recorder.up(path, url)
    if not data:
        return flask.jsonify({
            "code": 2,
            "msg": "too many records"
        })
    up_count = data["up"]
    down_count = data["down"]
    thumbs_up_recorder.save(save_dir)
    return flask.jsonify({'status': 'ok', "up_count": up_count, "down_count": down_count})

@app.route('/api/thumbs_down', methods=['POST'])
def thumbs_down():
    data = flask.request.get_json()
    path = check_path(data.get("path"))
    url = data.get("url")
    if not path:
        return flask.jsonify({
            "code": 1,
            "msg": "path is required"
        })
    msg = check_msg_valid(data.get("msg"))
    if not msg:
        return flask.jsonify({
            "code": 1,
            "msg": "msg not valid"
        })
    data = thumbs_up_recorder.down(path, msg, url)
    if not data:
        return flask.jsonify({
            "code": 2,
            "msg": "too many records"
        })
    up_count = data["up"]
    down_count = data["down"]
    thumbs_up_recorder.save(save_dir)
    return flask.jsonify({'status': 'ok', "up_count": up_count, "down_count": down_count})

@app.route('/api/thumbs_count', methods=['POST'])
def thumbs_count():
    data = flask.request.get_json()
    path = check_path(data.get("path"))
    if not path:
        return flask.jsonify({
            "code": 1,
            "msg": "path is required"
        })
    data = thumbs_up_recorder.get(path)
    if not data:
        return flask.jsonify({
            "code": 2,
            "msg": "too many records"
        })
    up_count = data["up"]
    down_count = data["down"]
    thumbs_up_recorder.save(save_dir)
    return flask.jsonify({'status': 'ok', "up_count": up_count, "down_count": down_count})


def signalTrap():
    def before_exit(signum, stack):
        print("before_exit")
        # TODO: this maybe called twice
        thumbs_up_recorder.save(save_dir, save_now=True)
        sys.exit(0)

    signal.signal(signal.SIGALRM, before_exit)
    signal.signal(signal.SIGINT, before_exit)

def main():
    signalTrap()
    app.run(host=args.host, port=args.port, debug=True)

if __name__ == '__main__':
    main()

