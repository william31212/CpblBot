# for setting Log
import configparser
import logging

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, make_response
import json
import datetime
import enum

from scratchData import *

# Flask init
app = Flask(__name__)

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# TODO: 定時推播
# sched = BackgroundScheduler(daemon=True)
# sched.add_job(autoNotify
# sched.start()

class Option(enum.IntEnum):
    TODAY = 1
    CUSTOM_DAY = 2

# TODO: 純文字排版漂亮
def outputData(options, year=date.today().strftime("%Y"), month=str(date.today().strftime("%m")).lstrip('0'), day=date.today().strftime("%d")):
    outputStringData = ''
    
    # 爬取中職最新資料
    if options == Option.TODAY:
        todayInfo = getTodayInformation()
    elif options == Option.CUSTOM_DAY:
        todayInfo = getDayOfCpblSchedule(year, month, day)

    # 輸出字串更新
    if todayInfo == '日期格式錯誤':
        outputStringData = '日期格式錯誤'
    elif todayInfo == '今日無比賽':
        outputStringData = '今日無比賽'
    else:
        outputStringData = "日期：{}\n" \
            "有 {} 場比賽\n".format(todayInfo.date, todayInfo.competitionCount)
        for obj in todayInfo.competition:   
            outputStringData += "`例行賽編號：{}`\n" \
            "地點：{}\n" \
            "對戰陣容：{} v.s. {}\n".format(obj.number, obj.location, obj.teamA, obj.teamB)
        
            if obj.now:
                outputStringData += '現在局數： {}\n'.format(obj.now)
            if obj.teamAScore:
                outputStringData += '比數 {} ： {}\n'.format(obj.teamAScore, obj.teamBScore)
            if obj.playBallTime:
                outputStringData += '開打時間：{}\n'.format(obj.playBallTime)
            if obj.cancelDescription:
                outputStringData += '取消比賽原因：{}\n'.format(obj.cancelDescription)

    return outputStringData


def sendInformation(options, year=date.today().strftime("%Y"), month=str(date.today().strftime("%m")).lstrip('0'), day=date.today().strftime("%d")):
    # init 
    outputString = ''
    lastScratchTime = ''
    if options == Option.TODAY:
        outputString = outputData(options)
    elif options == Option.CUSTOM_DAY:
        outputString = outputData(options, year, month, day)

    return outputString


# TODO Conndition Limit
# https://blog.bearer.sh/consume-webhooks-with-python/
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    msg = ''
    if request.method == "POST":
        post_data = request.data
        json_data = json.loads(post_data)


        chat_id = json_data['message']['from']['id']
        user_input = json_data['message']['text']

        if user_input == '/today':
            # Try Get the Message
            msg = sendInformation(Option.TODAY)
            # Send Message
            requests.post(url='https://api.telegram.org/bot{token}/sendMessage?&parse_mode=Markdown'.format(token=config['TELEGRAM']['ACCESS_TOKEN']),
                              params={'chat_id': chat_id, 'text': msg})
            return make_response('OK', 200)
        elif str(user_input)[0:5] == '/date':
            # Check Input
            if re.match('/date:( |)([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))', user_input):
                # Try Get Custom day
                dateSelected = user_input.split(":")[1]
                msg = sendInformation(Option.CUSTOM_DAY, int(dateSelected.split("-")[0]), int(dateSelected.split("-")[1]), int(dateSelected.split("-")[2]))

                # Send Message
                requests.post(url='https://api.telegram.org/bot{token}/sendMessage?&parse_mode=Markdown'.format(token=config['TELEGRAM']['ACCESS_TOKEN']),
                              params={'chat_id': chat_id, 'text': msg})
                return make_response('OK', 200)
            else:
                # Date Format Error
                requests.post(url='https://api.telegram.org/bot{token}/sendMessage'.format(token=config['TELEGRAM']['ACCESS_TOKEN']),
                              params={'chat_id': chat_id, 'text': '日期格式錯誤'})
                return make_response('Invaild Date Format', 200)
        else:
            requests.post(url='https://api.telegram.org/bot{token}/sendMessage'.format(token=config['TELEGRAM']['ACCESS_TOKEN']),
                              params={'chat_id': chat_id, 'text': '未支援此指令'})
            return make_response('No this command', 200)
    else:
        return make_response('Method is not allow', 200)  

# TODO: 多人對列，限制請求次數

if __name__ == '__main__':
    # Webhook 設定
    r = requests.get('https://api.telegram.org/bot{token}/setWebhook?url={url}/webhook'.format(token=config['TELEGRAM']['ACCESS_TOKEN'], url=config['WEBHOOK']['URL']))
    
    # 測試日期查詢功能
    # print(sendInformation(Option.CUSTOM_DAY, 2021, 4, 9))
    
    # Flask app 執行
    app.run()
