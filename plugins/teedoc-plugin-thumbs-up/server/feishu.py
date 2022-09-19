'''
    get token from env variable FEISHU_BOT_TOKEN
    e.g.
        FEISHU_BOT_TOKEN=***-***-***-***-**** python feishu.py
'''
import os
import requests

def send_msg(msg):
    print("send_msg")
    url = "https://open.feishu.cn/open-apis/bot/v2/hook/{}".format(
        os.environ["FEISHU_BOT_TOKEN"])
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "msg_type": "text",
        "content": {
            "text": msg
        }
    }
    print(url)
    requests.post(url, headers=headers, json=data)

if __name__  == "__main__":
    send_msg("msg test")
