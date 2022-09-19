'''
    get token from env variable FEISHU_BOT_TOKEN
    e.g.
        FEISHU_BOT_TOKEN=***-***-***-***-**** python feishu.py
'''
import os
import requests

def send_msg(msg, url_or_token = None):
    if url_or_token is None:
        token = os.environ.get("FEISHU_BOT_TOKEN")
        if token:
            url_or_token = token
    if not url_or_token:
        return
    if url_or_token.startswith("http"):
        url = url_or_token
    else:
        url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{url_or_token}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "msg_type": "text",
        "content": {
            "text": msg
        }
    }
    requests.post(url, headers=headers, json=data)

if __name__  == "__main__":
    send_msg("msg test")
