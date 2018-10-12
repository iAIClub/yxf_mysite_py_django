# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function

from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseNotFound
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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

#文档首页。左侧列出所有栏目（可切换选定项），中间列出选定栏目的所有文档，右侧显示选定栏目的信息
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
        tmp_keywords = []
        for keyword in doc.keywords.split(';'):
            tmp_keywords.append(keyword)
        doc.keywords=tmp_keywords
    return HttpResponse(render(request, 'app_tutorial/index.html', {\
        'title':'菲菲的技术网站 - 文档',\
        'active':active,\
        'active_column':active_column,\
        'left_list':columns,\
        'content_list':docs,\
        'view':'tutorial',\
        }))

#栏目页，与文档首页通用一组模板。左侧列出本栏目所有文档（可切换文档），中间显示栏目默认index文档，右侧显示中间的文档对应的信息
#/tutorial/doc/colname
def column(request,column_slug):
    column = Column.objects.get(slug=column_slug)
    docs = Tutorial.objects.filter(column__slug=column_slug).order_by("publish_time")#用于在左侧显示文档列表
    content_doc = []
    try:
        content_doc = Tutorial.objects.get(column__slug=column_slug, slug='index')#默认显示的index文档，没有则自动新建一个
    except:
        index = Tutorial.objects.create(column=column,author=request.user,slug='index',title='index_autocreated')
        index.save()
        content_doc = Tutorial.objects.get(column__slug=column_slug, slug='index')
    tmp_keywords = []
    for keyword in content_doc.keywords.split(';'):
        tmp_keywords.append(keyword)
    content_doc.keywords=tmp_keywords
    return HttpResponse(render(request, 'app_tutorial/index.html',{\
        'title':column.name,\
        'column':column,\
        'left_list':docs,\
        'content_doc':content_doc,\
        'view':'column',\
        }))

#栏目文档页，与文档首页通用一组模板，与栏目页内容相同。唯一的区别是中间不是栏目的默认index文档，url形式不同
#/tutorial/doc/colname/docname
def doc(request, column_slug, doc_slug):
    if request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        if purpose is not None and request.user.is_authenticated:
            try:
                #表单提交处理：新建文档，对文件主体的操作转到编辑器页面进行
                if purpose == 'new':
                    column = Column.objects.get(slug=column_slug)
                    new_slug = request.POST.get('slug',None)
                    new_title = request.POST.get('title',None)
                    new_keywords = request.POST.get('keywords',None)
                    new_description = request.POST.get('description',None)
                    new_doc = Tutorial.objects.create(column=column,author=request.user,slug=new_slug,title=new_title,keywords=new_keywords,description=new_description)
                    new_doc.save()
                    return HttpResponseRedirect(reverse('app_tutorial_editmd')+'?purpose='+purpose+'&column='+column.slug+'&slug='+new_slug+'&title='+new_title)
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
                    return HttpResponseRedirect(reverse('app_tutorial_editmd')+'?purpose='+purpose+'&column='+column_slug+'&slug='+doc_slug+'&title='+new_title)
                #表单提交处理：删除当前文档，成功后返回到栏目页
                elif purpose == 'delete':
                    content_doc = Tutorial.objects.get(column__slug=column_slug, slug=doc_slug)#文档
                    content_doc.delete()
                    return HttpResponseRedirect(reverse('app_tutorial_index')+'doc/'+column_slug)
            except:
                messages.error(request,'操作失败！')
        return HttpResponseRedirect(request.path)
    #GET直接请求网页
    else:
        column = Column.objects.get(slug=column_slug)
        docs = Tutorial.objects.filter(column__slug=column_slug).order_by("publish_time")#用于在左侧显示文档列表
        try:
            content_doc = Tutorial.objects.get(column__slug=column_slug, slug=doc_slug)#文档
            return HttpResponse(render(request, 'app_tutorial/index.html',{\
            'title':column.name,\
            'column':column,\
            'left_list':docs,\
            'content_doc':content_doc,\
            'view':'doc',\
            }))
        except:
            html_404 = '<h1>Not Found</h1><p>The requested URL %s was not found on this server.</p>' %request.path
            return HttpResponseNotFound(html_404)

@login_required(login_url='/user/login')
#编辑器页，文档仅限管理员操作。可直接访问，也可通过iframe嵌入。新建文档、编辑文档的实际执行者
def editmd(request):
    #返回编辑器页面
    if request.method == 'GET':
        arg_column = request.GET.get('column',None)
        arg_op = request.GET.get('op',None)
        arg_doc = request.GET.get('doc',None)
        #把所有参数直接传递给模板处理
        return HttpResponse(render(request,'app_tutorial/editmd.html',{\
            'title':'文档代码编辑器',\
            'arg_path':arg_column,\
            'arg_op':arg_op,\
            'arg_file':arg_doc,\
            }))
    elif request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        #图片上传处理
        if purpose == 'image_upload':
            pass
        #保存
        elif purpose == 'file_save':
            pass


#文档全窗口预览页?