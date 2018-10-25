# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
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

def charvideo(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'字符视频',\
        'display':'charvideo',\
        'avroot':'/static/av/',\
        }))
