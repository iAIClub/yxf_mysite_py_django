# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from app_spider.models import APP_API,APP_TEMPLETE_ROOT


def index(request):
    return HttpResponse(render(request, 'app_spider/index.html'))

