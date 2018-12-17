# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from app_webtrans.models import APP_FILE_ROOT,APP_TEMPLETE_ROOT
from mysite.settings import BAIDUMAP

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
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'微信应用',\
        'display':'wechat',\
        }))

def map(request):
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
        # return JsonResponse({'status':200})
    else:
        return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
            'title':'代理访问',\
            'display':'proxy',\
            }))
