# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
from app_spider.models import APP_API,APP_TEMPLETE_ROOT


'''
app_spider将使用rest子框架
'''


def index(request):
    opt = request.GET.get('op', None)
    if opt is None:
        return HttpResponseRedirect(reverse('app_spider') + '?op=all')
    else:
        return HttpResponse(render(request, 'app_spider/index.html',{ \
            'title': '爬虫', \
            'op': opt, \
        }))
