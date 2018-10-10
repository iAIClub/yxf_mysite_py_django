# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function

from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render
import sys
sys.path.append("..")
from .models import Column,Tutorial

# Create your views here.
def index(request):
    #这个是整个网站的主页，不可更改
    columns = Column.objects.all()
    return HttpResponse(render(request, 'common/index.html', {\
        'title':'菲菲的技术网站',\
        'list':columns,\
        }))

def tutorial(request):
    columns = Column.objects.all()
    docs = Tutorial.objects.all().order_by("-publish_time")
    return HttpResponse(render(request, 'app_tutorial/index.html', {\
        'title':'菲菲的技术网站 - 文档',\
        'left_list':columns,\
        'content_list':docs,\
        'view':'tutorial',\
        }))

def column(request,column_slug):
    column = Column.objects.get(slug=column_slug)
    docs = Tutorial.objects.filter(column__slug=column_slug).order_by("-publish_time")
    content_doc = docs[0]
    content = content_doc.content
    return HttpResponse(render(request, 'app_tutorial/index.html',{\
        'title':column.name,\
        'column':column,\
        'left_list':docs,\
        'content':content,\
        'view':'column',\
        }))

def doc(request, column_slug, doc_slug):
    list_all = Tutorial.objects.all()
    return HttpResponse('string is:'+ suburl)

def editmd(request):
    return HttpResponse(render(request,'common/editmd.html',{\
        'title':'文档代码编辑器',\
        }))
