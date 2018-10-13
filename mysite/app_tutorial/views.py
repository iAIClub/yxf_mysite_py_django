# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function

from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseNotFound
from django.shortcuts import render
from django.core.files import File
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
import sys
sys.path.append("..")
from .models import Column,Tutorial

#网站首页
def index(request):
    columns = Column.objects.all()
    return HttpResponse(render(request, 'common/index.html', {\
        'title':'菲菲的技术网站',\
        'list':columns,\
        }))

#文档首页
#左侧列出所有栏目（可切换选定项），中间列出选定栏目的所有文档（需注意关键词列表），右侧显示选定栏目的信息
#/tutorial
def tutorial(request):
    columns = Column.objects.all()
    active = request.GET.get('active',None)#进入文档首页必须指定活动栏目
    if active is None:
        active = columns[0].slug
        return HttpResponseRedirect(reverse('app_tutorial_index')+'?active='+active)
    active_column = Column.objects.get(slug=active)
    docs = Tutorial.objects.filter(column__slug=active).order_by("publish_time")#选定栏目内的所有文档
    for doc in docs:
        try:
            tmp_keywords = []
            for keyword in doc.keywords.split(';'):
                tmp_keywords.append(keyword)
            doc.keywords=tmp_keywords
        except:
            doc.keywords=[]
    return HttpResponse(render(request, 'app_tutorial/index.html', {\
        'title':'菲菲的技术网站 - 文档',\
        'active':active,\
        'active_column':active_column,\
        'left_list':columns,\
        'content_list':docs,\
        'view':'tutorial',\
        }))

#栏目页，与文档首页通用一组模板，与栏目文档页内容完全一致，只不过显示的是默认index文档且url是栏目名
#/tutorial/doc/colname
def column(request,column_slug):
    if request.method == 'GET':
        return doc(request=request,column_slug=column_slug,doc_slug='index')#交由doc()处理

#栏目文档页
##左侧列出本栏目所有文档（可切换文档），中间显示文档（需注意请求的是实体文件），右侧显示中间的文档对应的信息（需注意关键词列表）
#/tutorial/doc/colname/docname
def doc(request, column_slug, doc_slug):
    #POST操作文档域
    if request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        if purpose is not None and request.user.is_authenticated:
            try:
                #表单提交处理：新建文档，对文件主体的操作转到编辑器页面进行，为防止重复创建同名记录，需在模型设置column+slug组成联合主键
                if purpose == 'new':
                    column = Column.objects.get(slug=column_slug)
                    new_slug = request.POST.get('slug',None)
                    new_title = request.POST.get('title',None)
                    new_keywords = request.POST.get('keywords',None)
                    new_description = request.POST.get('description',None)
                    new_docfile = request.FILES.get('file',None)
                    new_docfile.name = new_slug+'.md'
                    new_doc = Tutorial.objects.create(column=column,author=request.user,slug=new_slug,title=new_title,keywords=new_keywords,description=new_description,content=new_docfile)
                    new_doc.save()
                    fileurl = column_slug+'/'
                    return HttpResponseRedirect(reverse('app_tutorial_editmd')+'?title='+new_title+'&fileurl='+fileurl)
                #表单提交处理：修改当前文档，对文件主体的操作转到编辑器页面进行
                elif purpose == 'edit':
                    column = Column.objects.get(slug=column_slug)
                    new_title = request.POST.get('title',None)
                    new_keywords = request.POST.get('keywords',None)
                    new_description = request.POST.get('description',None)
                    doc = Tutorial.objects.filter(column__slug=column_slug,slug=doc_slug)[0]
                    doc.title=new_title #更新数据直接赋值即可
                    doc.keywords=new_keywords
                    doc.description=new_description
                    doc.save()
                    fileurl = doc.content.url
                    return HttpResponseRedirect(reverse('app_tutorial_editmd')+'?title='+new_title+'&fileurl='+fileurl)
                #表单提交处理：删除当前文档，成功后返回到栏目页
                elif purpose == 'delete':
                    content_doc = Tutorial.objects.get(column__slug=column_slug, slug=doc_slug)#文档
                    content_doc.delete()
                    return HttpResponseRedirect(reverse('app_tutorial_index')+'doc/'+column_slug)
            except:
                messages.error(request,'操作失败！')
        return HttpResponseRedirect(request.path)
    #GET直接请求网页
    elif request.method == 'GET':
        column = Column.objects.get(slug=column_slug)
        docs = Tutorial.objects.filter(column__slug=column_slug).order_by("publish_time")#用于在左侧显示文档列表
        content_doc = []
        #1.尝试读取选定的文档。index页若没有则自动新建，其他文档若没有则返回404
        if doc_slug=='index':
            try:
                content_doc = Tutorial.objects.get(column__slug=column_slug, slug=doc_slug)#文档
            except:
                index = Tutorial.objects.create(column=column,author=request.user,slug=doc_slug,title='index_autocreated')
                index.save()
                content_doc = Tutorial.objects.get(column__slug=column_slug, slug=doc_slug)
        else:
            try:
                content_doc = Tutorial.objects.get(column__slug=column_slug, slug=doc_slug)#文档
            except:
                html_404 = '<h1>Not Found</h1><p>The requested URL %s was not found on this server.</p>' %request.path
                return HttpResponseNotFound(html_404)
        #2.尝试读取关键词，若没有则设置为空列表
        try:
            tmp_keywords = []
            for keyword in content_doc.keywords.split(';'):
                tmp_keywords.append(keyword)
            content_doc.keywords=tmp_keywords
        except:
            content_doc.keywords=[]
        #3.尝试读取文档对应的文件，若没有则默认为空
        content_doc_file = ''
        try:
            content_doc_file = content_doc.content.read()
        except:
            pass
        return HttpResponse(render(request, 'app_tutorial/index.html',{\
        'title':column.name,\
        'column':column,\
        'left_list':docs,\
        'content_doc':content_doc,\
        'content_doc_file':content_doc_file,\
        'view':'doc',\
        }))

@login_required(login_url='/user/login')
#编辑器页，文档仅限管理员操作。可直接访问，也可通过iframe嵌入。新建文档、编辑文档的实际执行者
def editmd(request, column_slug, doc_slug, doc_name):
    if request.method == 'GET':
        #返回编辑器页面
        if doc_name is None:
            arg_title = request.GET.get('title',None)
            arg_fileurl = request.GET.get('fileurl',None)
            if arg_fileurl is not None:
                return HttpResponse(render(request,'app_tutorial/editmd.html',{\
                    'title':arg_title,\
                    'arg_fileurl':arg_fileurl,\
                    }))
            else:
                messages.error(request,'无效文档信息！')
                return HttpResponseRedirect(request.path)
        #返回文档实体文件内容
        else:
            doc = Tutorial.objects.get(column__slug=column_slug, slug=doc_slug)
            response = HttpResponse(doc.content)
            response['Content-Type'] = 'application/octet-stream' #设置为二进制流
            response['Content-Disposition'] = 'attachment;filename=' + doc_name #强制浏览器下载而不是查看流
            return response
    #通过editmd模板提交的操作
    elif request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        #图片上传处理
        if purpose == 'image_upload':
            pass
        #保存处理
        elif purpose == 'file_save':
            pass


#文档全窗口预览页?