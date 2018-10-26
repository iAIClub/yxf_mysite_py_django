# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse
from app_visual.models import APP_FILE_ROOT,APP_TEMPLETE_ROOT

def index(request):
    return HttpResponseRedirect(reverse('app_visual_dsvisual'))

def dsvisual(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'可视化数据结构与算法',\
        'display':'dsvisual',\
        }))

def picture(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'图像处理',\
        'display':'picture',\
        }))

def paint(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'画图',\
        'display':'paint',\
        }))

def tetris(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'俄罗斯方块',\
        'display':'tetris',\
        }))

def charvideo(request,suburl):
    if suburl:
        #内部函数：分批流式读取大文件
        def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
            #chunk_size=8192:片段长度8M
            #offset=0起始位置
            #lenth=None:未到最终片段不设置，到最终片段设置为小于等于chunk_size的值
            with open('media/'+APP_FILE_ROOT+suburl,'rb') as f:
                f.seek(offset, os.SEEK_SET)#找到起始位置
                remaining = length#
                while True:
                    bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
                    data = f.read(bytes_length)
                    if not data:
                        break
                    if remaining:
                        remaining -= len(data)
                    yield data
    else:
        return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
            'title':'字符视频',\
            'display':'charvideo',\
            'avroot':'/static/av/',\
            }))
