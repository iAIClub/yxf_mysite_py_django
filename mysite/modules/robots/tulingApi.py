#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import requests
import os
import sys
import configparser
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
cf = configparser.ConfigParser()
cf.read(os.path.join(BASE_DIR,"settings.cfg"))

__tuling_url = cf.get("tuling","url")
__tuling_ak = cf.get("tuling","ak")
__tuling_id = str(cf.get("tuling","id"))

'''
https://www.kancloud.cn/turing/www-tuling123-com/718227

Request example:
{
    "reqType":0,                   #输入类型:0-文本(默认)、1-图片、2-音频
    "perception": {                #输入信息
        "inputText": {
            "text": "附近的酒店"
        },
        "inputImage": {
            "url": "imageUrl"
        },
        "selfInfo": {
            "location": {
                "city": "北京",
                "province": "北京",
                "street": "信息路"
            }
        }
    },
    "userInfo": {                  #用户认证
        "apiKey": "",
        "userId": ""
    }
}

Response example:

  {
    "intent": {                     #机器人理解到的请求意图
        "code": 10005,
        "intentName": "",
        "actionName": "",
        "parameters": {
            "nearby_place": "酒店"
        }
    },
    "results": [                    #输出结果集
        {
            "groupType": 1,
            "resultType": "url",    #resultType:文本(text);连接(url);音频(voice);视频(video);图片(image);图文(news)
            "values": {
                "url": "http://m.elong.com/hotel/0101/nlist/#indate=2016-12-10&outdate=2016-12-11&keywords=%E4%BF%A1%E6%81%AF%E8%B7%AF"
            }
        },
        {
            "groupType": 1,
            "resultType": "text",
            "values": {
                "text": "亲，已帮你找到相关酒店信息"
            }
        }
    ]
}
'''


def __tuling_result(response):  # response type:str
    # print(type(response))
    res_json = json.loads(response,encoding='utf-8')
    result = []
    try:
        for i in res_json['results']:
            if i['resultType'] == 'url':
                result.append(i['values']['url'])
            if i['resultType'] == 'text':
                result.append(i['values']['text'])
    except:
        result.append('机器人接口出错！')
    return result  # result type:str


def tuling_request(request):
    request_str = '''
    {
        "reqType":0,
        "perception": {
            "inputText": {
    '''
    request_str += '"text": "{}"'.format(request)
    request_str += '''
            },
            "selfInfo": {
            }
        },
        "userInfo": {
    '''
    request_str += '"apiKey": "{}",'.format(__tuling_ak)+'"userId": "{}"'.format(__tuling_id)
    request_str += '''
            }
        }
    '''
    response = requests.post(__tuling_url,data=request_str.encode('utf-8'))
    result = __tuling_result(response.text)
    return result  # text list
