# -*- coding: utf-8 -*-

import os
import sys
import json
import pymysql
import requests
import redis

from flask import Flask, request, abort
from flask_api import status
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import ( # 使用するモデル(イベント, メッセージ, アクションなど)を列挙
    FollowEvent, UnfollowEvent, MessageEvent, PostbackEvent,
    TextMessage, TextSendMessage, TemplateSendMessage,
    ButtonsTemplate, CarouselTemplate, CarouselColumn,
    PostbackTemplateAction, LocationMessage
)

app = Flask(__name__)

ABS_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
with open(ABS_PATH+'/conf.json', 'r') as f:
    CONF_DATA = json.load(f)

CHANNEL_SECRET = CONF_DATA['CHANNEL_SECRET']
CHANNEL_ACCESS_TOKEN = CONF_DATA['CHANNEL_ACCESS_TOKEN']
REMOTE_HOST = CONF_DATA['REMOTE_HOST']
REMOTE_DB_NAME = CONF_DATA['REMOTE_DB_NAME']
REMOTE_DB_USER = CONF_DATA['REMOTE_DB_USER']
REMOTE_DB_PASS = CONF_DATA['REMOTE_DB_PASS']
REMOTE_DB_TB = CONF_DATA['REMOTE_DB_TB']
STATION_API_URL = 'http://express.heartrails.com/api/json?method=getStations&x={}&y={}'

if CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET.')
    sys.exit(1)
if CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN.')
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

redis = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/', methods=['POST'])
def index():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return '',status.HTTP_200_OK

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    uid = event.source.user_id
    h = redis.hgetall(uid)
    token = event.reply_token

    if h:
        lat, long = h['lat'.encode()].decode(), h['long'.encode()].decode()
    else:
        send_message(token, '位置情報を送信して下さい！')
        return

    stations = get_stations(lat, long)
    if  not stations:
        send_message(token, "エラーが発生しました。やり直して下さい。")
        return

    
    # send_message(token, '{}:{}:{}'.format(stations[0],stations[1],stations[2]))

@handler.add(MessageEvent, message=LocationMessage)
def message_location(event):
    lat = event.message.latitude
    long = event.message.longitude
    uid = event.source.user_id
    station = get_station(lat, long)
    token = event.reply_token

    if station:
        redis.hset(uid, 'lat', lat)
        redis.hset(uid, 'long', long)
        redis.expire(uid, 1800)
        message = '{}駅周辺のラーメン屋をお探しします！\nあなたの今の気分を教えて下さい\n（例）あっさりした醬油ラーメン'.format(station)
        send_message(token, message)
    else:
        send_message(token, "エラーが発生しました。やり直して下さい。")

def send_message(token, message):
    line_bot_api.reply_message(
        token,
        TextSendMessage(text=message)
    )


def get_station(lat, long):
    station = http_request(STATION_API_URL.format(long, lat))
    if station:
        return station['response']['station'][0]['name']
    else:
        return ''

def get_stations(lat, long):
    stations = http_request(STATION_API_URL.format(long, lat))
    if stations:
        return [
            stations['response']['station'][0]['name'],
            stations['response']['station'][0]['prev'],
            stations['response']['station'][0]['next']
            ]
    else:
        return ''

def http_request(url):
    res = requests.get(url)
    
    if res.status_code != status.HTTP_200_OK:
        return ''

    result_json = res.json()
    return result_json


@app.route('/test')
def test():
    return '',status.HTTP_200_OK

if __name__ == "__main__":
    app.run()