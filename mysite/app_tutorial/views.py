# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render
import sys
sys.path.append("..")
from mysite.settings_cfg import SUPERUSER
from .models import Column,Tutorial

# Create your views here.
def index(request):
    return HttpResponse(render(request, 'common/index.html', {\
        'title':'菲菲的技术网站',\
        'superuser':SUPERUSER['name'],\
        'content_title':'网站内容列表'\
        }))

def column(request,column_slug):
    list_all = Column.objects.all()
    content = Tutorial.objects.filter(column__slug=column_slug).order_by("publish_time")[0]
    content_title = content.title
    return HttpResponse(render(request, 'app_tutorial/index.html',{\
        'title':content_title,\
        'content_title':content_title,\
        'left':list_all,\
        'content':content,\
        'right':'',\
        }))

def doc(request, column_slug, doc_slug):
    list_all = Tutorial.objects.all()
    return HttpResponse('string is:'+ suburl)

def editmd(request):
    return HttpResponse(render(request,'common/editmd.html'))