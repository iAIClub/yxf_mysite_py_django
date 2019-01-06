#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function
import time
import json
import requests
from mysite.settings import TULING
__tuling_url = TULING['url']
__tuling_ak = TULING['ak']
__tuling_id = TULING['id']

'''
1.wechat官方文档的标准化编解码类
2.tuling123
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


class R_Msg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text


class R_TextMsg(R_Msg):
    def __init__(self, xmlData):
        R_Msg.__init__(self, xmlData)
        self.Content = xmlData.find('Content').text.encode("utf-8")


class R_ImageMsg(R_Msg):
    def __init__(self, xmlData):
        R_Msg.__init__(self, xmlData)
        self.PicUrl = xmlData.find('PicUrl').text
        self.MediaId = xmlData.find('MediaId').text


class S_Msg(object):
    def __init__(self):
        pass

    def send(self):
        return "success"


class S_TextMsg(S_Msg):
    def __init__(self, toUserName, fromUserName, content):
        S_Msg.__init__(self)
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = content

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        return XmlForm.format(**self.__dict)


class S_ImageMsg(S_Msg):
    def __init__(self, toUserName, fromUserName, mediaId):
        S_Msg.__init__(self)
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['MediaId'] = mediaId

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <Image>
        <MediaId><![CDATA[{MediaId}]]></MediaId>
        </Image>
        </xml>
        """
        return XmlForm.format(**self.__dict)
