# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
import requests
import logging
import xml.etree.ElementTree as et
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from app_webtrans.models import APP_FILE_ROOT,APP_TEMPLETE_ROOT
from mysite.settings import BAIDUMAP,WECHAT
import modules.robots.wechatApi as wechatApi

def index(request):
    return HttpResponseRedirect(reverse('app_webtrans_tcptrans'))

def websocket(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'对话机器',\
        'display':'websocket',\
        }))

def tcptrans(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'即时通信',\
        'display':'tcptrans',\
        }))

def nat(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'内网穿透',\
        'display':'nat',\
        }))

def wechat(request):
    if request.method == 'GET':
        signature = request.GET.get('signature',None)  # 数字指纹
        timestamp = request.GET.get('timestamp',None)  # 时间戳
        nonce = request.GET.get('nonce',None)  # 随机数
        echostr = request.GET.get('echostr',None)  # 随机字符串
        token = WECHAT['token']  # 请按照公众平台官网\基本配置中信息填写
        if not signature:  # 访问网页
            return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
                'title':'微信应用',\
                'display':'wechat',\
                }))
        else:  # 微信验证
            li = [token, timestamp, nonce]  # 字典序排序后再加密，与消息中的指纹对照，相同则证明是正确的消息
            li.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, li)
            hashcode = sha1.hexdigest()
            if hashcode == signature:
                return HttpResponse(echostr)
            else:
                return HttpResponse("")
    elif request.method == 'POST':  # 微信API,微信消息为XML格式，回复也是XML
        if len(request.raw_data) == 0:
            return HttpResponse("")
        xmlData = et.fromstring(request.raw_data)
        msg_type = xmlData.find('MsgType').text
        if msg_type == 'text':
            recMsg = wechatApi.R_TextMsg(xmlData)
        elif msg_type == 'image':
            recMsg = wechatApi.R_ImageMsg(xmlData)
        else:
            recMsg = None
        if isinstance(recMsg, wechatApi.R_Msg) and recMsg.MsgType == 'text':
            toUser = recMsg.FromUserName
            fromUser = recMsg.ToUserName
            content = "test"
            replyMsg = wechatApi.S_TextMsg(toUser, fromUser, content)
            return HttpResponse(replyMsg.send())
        else:
            return HttpResponse("success")


def mapa(request):  # 与内置函数名有冲突，要改名
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'地图应用',\
        'display':'map',\
        }))

def map_content(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'map.html',{\
        'url':BAIDUMAP['url'],\
        'ak':BAIDUMAP['ak'],\
        }))

def proxy(request):
    url = request.GET.get('url', None)
    if url:
        try:
            headers = {
                'Connection': 'keep-alive',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'en',
                'Host': url.split('/')[2]
            }
            res=requests.get(url,headers=headers)
            return HttpResponse(res)
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
            'title':'代理访问',\
            'display':'proxy',\
            }))
