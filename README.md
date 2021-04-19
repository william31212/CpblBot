# CpblBot

> [TOC]

## Demo

* ![](https://i.imgur.com/HGdtzlH.png)

## Link

* https://t.me/cpblbot

## Requisites

* Requests, Bs4
* Python-flask
* Python-flask apscheduler

## How to Build

* Install Pipenv
    * `pip3 install pipenv`

* Create `config.ini`

```
[TELEGRAM]
ACCESS_TOKEN = <your_token>
[WEBHOOK]
URL = <your_bot_webhook>
```

* Run
```bash
pipenv shell 
python bot.py
```

## Telegram Bot Command

* 查詢今日賽事
    * [x] `/today`
* 日期查詢功能
    * [x] `/date: 20xx-0x-xx`

