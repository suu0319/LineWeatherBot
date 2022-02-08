# -*- coding: utf-8 -*-
#載入Python、LineBot所需要的套件
from cgitb import text
import os,json,requests
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from linebot import LineBotApi
from linebot.models import TextSendMessage

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('Channel Access Token')
# 必須放上自己的Channel Secret
handler = WebhookHandler('Channel Secret')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

 
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#縣市名稱
cities = ['基隆市','嘉義市','臺北市','嘉義縣','新北市','臺南市','桃園市','高雄市','新竹市','屏東縣','新竹縣','臺東縣','苗栗縣','花蓮縣','臺中市','宜蘭縣','彰化縣','澎湖縣','南投縣','金門縣','雲林縣','連江縣']

#訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
# 基本上程式編輯都在這個function
@handler.add(MessageEvent)
def handle_message(event):
    ##取得即時氣象資料
    #token
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=token'
    Data = requests.get(url)
    Data = (json.loads(Data.text))['records']['location'][0]['weatherElement']

    #氣象字串
    #時間
    startTime = [str(Data[0]['time'][0]['startTime']),str(Data[0]['time'][1]['startTime']),str(Data[0]['time'][2]['startTime'])]
    endTime = [str(Data[0]['time'][0]['endTime']),str(Data[0]['time'][1]['endTime']),str(Data[0]['time'][2]['endTime'])]
    #天氣狀況
    weather = [str(Data[0]['time'][0]['parameter']['parameterName']),str(Data[0]['time'][1]['parameter']['parameterName']),str(Data[0]['time'][2]['parameter']['parameterName'])]
    #降雨機率
    rainPersent = [str(Data[1]['time'][0]['parameter']['parameterName']),str(Data[1]['time'][1]['parameter']['parameterName']),str(Data[1]['time'][2]['parameter']['parameterName'])]
    #最低溫度
    minTemp = [str(Data[2]['time'][0]['parameter']['parameterName']),str(Data[2]['time'][1]['parameter']['parameterName']),str(Data[2]['time'][2]['parameter']['parameterName'])]
    #最高溫度
    maxTemp = [str(Data[4]['time'][0]['parameter']['parameterName']),str(Data[4]['time'][1]['parameter']['parameterName']),str(Data[4]['time'][2]['parameter']['parameterName'])]
    #舒適度
    comfort = [str(Data[3]['time'][0]['parameter']['parameterName']),str(Data[3]['time'][1]['parameter']['parameterName']),str(Data[3]['time'][2]['parameter']['parameterName'])]

    #回覆設定
    reply_token = event.reply_token
    message = event.message.text
    
    #文字判斷
    if (message[:2] == '天氣'):
        city = message[3:]
        city = city.replace('台','臺')
        if(not (city in cities)):
            line_bot_api.reply_message(reply_token,TextSendMessage(text='查詢格式為: 天氣 縣市'))
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(
            text = 
            city + '未來36小時的天氣預測:\n\n' + 
            '{} ~ {}\n天氣狀況:{}\n降雨機率:{}\n溫度:{} ~ {}\n舒適度:{}\n\n'.format(startTime[0],endTime[0],weather[0],rainPersent[0],minTemp[0],maxTemp[0],comfort[0]) +
            '{} ~ {}\n天氣狀況:{}\n降雨機率:{}\n溫度:{} ~ {}\n舒適度:{}\n\n'.format(startTime[1],endTime[1],weather[1],rainPersent[1],minTemp[1],maxTemp[1],comfort[1]) +
            '{} ~ {}\n天氣狀況:{}\n降雨機率:{}\n溫度:{} ~ {}\n舒適度:{}\n\n'.format(startTime[2],endTime[2],weather[2],rainPersent[2],minTemp[2],maxTemp[2],comfort[2]) 
            ))   
    elif (message == 'help'):
        line_bot_api.reply_message(reply_token, TextSendMessage(text= '指令如下:\n\nhelp => 查詢指令\n\n氣象相關:\n天氣 縣市 => 查詢當地天氣狀況\n\n圖片相關:\n新年快樂 => 新年快樂賀圖'))
    elif (message == '新年快樂'):
        image_message = ImageSendMessage(
        original_content_url='https://i.imgur.com/Py3EsSH.png',
        preview_image_url='https://i.imgur.com/Py3EsSH.png'
        )
        line_bot_api.reply_message(reply_token,image_message)
    elif (message == 'line://nv/recommendOA/@722uomez'):
        line_bot_api.reply_message(reply_token, TextSendMessage(text= '您要介紹我給別人認識嗎?\nso happyヽ(*´∀`)ﾉ'))
    elif (message == '常見問題'):
        line_bot_api.reply_message(reply_token,TextSendMessage(text= '目前機器人伺服器為免費版難免會有lag的情況喔(*’ｰ’*)\n查詢指令請輸入: help(｡A｡)'))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=message))


# 主動推播訊息
line_bot_api.push_message('LintToken', 
                          TextSendMessage(text='安安您好！我是氣象專家Nico(*‘ v`*)\n我目前擁有的指令如下輸入:\n\nhelp => 查詢指令\n天氣 縣市 => 查看當地天氣狀況\n新年快樂 => 新年快樂賀圖\n\n其他指令開發中 敬請期待(⁰▿⁰)'))

#主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)