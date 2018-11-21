#!/usr/bin/env python
# -*- coding: utf-8 -*-

tuling_url = 'http://openapi.tuling123.com/openapi/api/v2'
tuling_ak = 'ec1c97e388e44c6ba7bb03c3c6c9e701'

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

