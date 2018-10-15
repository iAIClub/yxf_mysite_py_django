# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,HttpResponseNotFound
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
import os
import sys
import shutil
sys.path.append("..")
from .models import Post

#博客首页，对所有人开放。左侧博文分类，中间所有用户的博文列表，右侧最新、最热、评论
#/blog
def blog(request):
    return HttpResponse(render(request, 'app_blog/index.html'))

#用户文章列表页，嵌入到/user/profile中，通过用户区访问
#/blog/post/user
@login_required(login_url='/user/login')
def user(request,user):
    posts = Post.objects.filter(user=request.user).order_by("publish_time")
    for post in posts:
        try:
            tmp_keywords = []
            for keyword in doc.keywords.split(';'):
                tmp_keywords.append(keyword)
            post.keywords=tmp_keywords
        except:
            post.keywords=[]
    return HttpResponse(render(request, 'app_blog/post.html',{\
        'title':request.user+' - 所有文章',\
        'content_list':posts,\
        }))

#文章页
#不显示左侧，内容+右侧信息
#/blog/post/user/postname
def post(request, user, post):
    #POST操作文档域
    if request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        if purpose is not None and request.user.is_authenticated:
            try:
                #表单提交处理：新建文档，对文件主体的操作转到编辑器页面进行，为防止重复创建同名记录，需在模型设置column+slug组成联合主键
                if purpose == 'new':
                    new_slug = request.POST.get('slug',None)
                    new_title = request.POST.get('title',None)
                    new_keywords = request.POST.get('keywords',None)
                    new_description = request.POST.get('description',None)
                    upload_file = request.FILES.get('file',None)
                    new_docfile = upload_file
                    if upload_file is None:
                        f = file('media/app_blog_doc/'+str(new_slug)+'.md','w+')
                        new_docfile = File(f)
                        new_docfile.write('')
                        new_docfile.name = new_slug+'.md'
                        new_doc = blog.objects.create(column=column,author=request.user,slug=new_slug,title=new_title,keywords=new_keywords,description=new_description,content=new_docfile)
                        new_doc.save()
                        f.close()
                        os.remove('media/app_blog_doc/'+str(new_slug)+'.md')
                    else:
                        new_docfile.name = new_slug+'.md'
                        new_doc = blog.objects.create(column=column,author=request.user,slug=new_slug,title=new_title,keywords=new_keywords,description=new_description,content=new_docfile)
                        new_doc.save()
                    return HttpResponseRedirect(reverse('app_blog_editmd')+'?column='+column_slug+'&slug='+new_slug+'&title='+new_title)
                #表单提交处理：修改当前文档，对文件主体的操作转到编辑器页面进行
                elif purpose == 'edit':
                    new_title = request.POST.get('title',None)
                    new_keywords = request.POST.get('keywords',None)
                    new_description = request.POST.get('description',None)
                    doc = blog.objects.filter(column__slug=column_slug,slug=doc_slug)[0]
                    doc.title=new_title #更新数据直接赋值即可
                    doc.keywords=new_keywords
                    doc.description=new_description
                    doc.save()
                    return HttpResponseRedirect(reverse('app_blog_editmd')+'?column='+column_slug+'&slug='+doc_slug+'&title='+new_title)
                #表单提交处理：删除当前文档及其文件目录，成功后返回到栏目页
                elif purpose == 'delete':
                    content_doc = blog.objects.get(column__slug=column_slug, slug=doc_slug)#文档
                    content_doc.delete()
                    shutil.rmtree('media/app_blog_doc/'+str(column_slug)+'/'+str(doc_slug))
                    return HttpResponseRedirect(reverse('app_blog_index')+'doc/'+column_slug)
            except Exception as e:
                raise e
                messages.error(request,'操作失败！')
        return HttpResponseRedirect(request.path)
    #GET直接请求网页
    elif request.method == 'GET':
        column = Column.objects.get(slug=column_slug)
        docs = blog.objects.filter(column__slug=column_slug).order_by("publish_time")#用于在左侧显示文档列表
        content_doc = []
        #1.尝试读取选定的文档。index页若没有则自动新建，其他文档若没有则返回404
        if doc_slug=='index':
            try:
                content_doc = blog.objects.get(column__slug=column_slug, slug=doc_slug)#文档
            except:
                f = file('media/app_blog_doc/index.md','w+')
                new_docfile = File(f)
                new_docfile.write('')
                new_docfile.name = doc_slug+'.md'
                index = blog.objects.create(column=column,author=request.user,slug=doc_slug,title=doc_slug,content=new_docfile)
                index.save()
                f.close()
                os.remove('media/app_blog_doc/'+str(doc_slug)+'.md')
                content_doc = blog.objects.get(column__slug=column_slug, slug=doc_slug)
        else:
            try:
                content_doc = blog.objects.get(column__slug=column_slug, slug=doc_slug)#文档
            except:
                html_404 = '<h1>Not Found</h1><p>The requested URL %s was not found on this server.</p>' %request.path
                return HttpResponseNotFound(html_404)
        #2.使用独立的新变量尝试读取关键词，若没有则设置为空列表
        content_doc_keywords = []
        try:
            for keyword in content_doc.keywords.split(';'):
                content_doc_keywords.append(keyword)
        except:
            pass
        #3.尝试读取文档对应的文件，若没有则默认为空
        content_doc_file = ''
        try:
            content_doc_file = content_doc.content.read()
        except:
            pass
        return HttpResponse(render(request, 'app_blog/doc.html',{\
            'title':content_doc.title,\
            'column':column,\
            'left_list':docs,\
            'content_doc':content_doc,\
            'content_doc_keywords':content_doc_keywords,\
            'content_doc_file':content_doc_file,\
            }))

#编辑器页。可直接访问，也可通过iframe嵌入。新建文档、编辑文档的实际执行者
@csrf_exempt  #插件的模板无法添加POST{% csrf_token %}，需要对此视图函数使用此装饰器
def editmd(request):
    if request.method == 'GET':
        arg_getfile = request.GET.get('getfile',None)
        #返回编辑器页面
        if arg_getfile is None:
            arg_slug = request.GET.get('slug',None)
            arg_title = request.GET.get('title',None)
            try:
                return HttpResponse(render(request,'app_blog/editmd.html',{\
                    'slug':arg_slug,\
                    'title':arg_title,\
                    }))
            except:
                messages.error(request,'无效文档信息！')
                return HttpResponseRedirect(reverse('app_blog_index')+'doc/'+str(arg_column)+'/'+str(arg_slug))
        #返回文档实体文件.md内容。此处的GET参数由前端生成，需要编解码
        elif arg_getfile == 'md':
            arg_slug = request.GET.get('slug'.encode('utf-8'),None)
            doc = Blog.objects.get(column__slug=arg_column, slug=arg_slug)
            response = HttpResponse(doc.content)
            response['Content-Type'] = 'application/octet-stream' #设置为二进制流
            response['Content-Disposition'] = 'attachment;filename=' + arg_slug+'.md' #强制浏览器下载而不是查看流
            return response
    #通过editmd模板提交的操作
    elif request.method == 'POST':
        if request.user.is_authenticated:
            purpose = request.POST.get('purpose')
            #保存处理
            if purpose == 'savepage':
                arg_slug = request.POST.get('slug',None)
                text_md = request.POST.get('editormd-markdown-textarea',None)
                text_html = request.POST.get('editormd-html-textarea',None)
                doc = Blog.objects.get(column__slug=arg_column, slug=arg_slug)

                # md file
                f1 = file('media/app_blog_doc/'+str(arg_slug)+'.md','w+')#在文件系统中打开临时文件暂存
                new_docfile = File(f1)
                new_docfile.write(text_md)
                new_docfile.name = str(arg_slug)+'.md'
                doc.content.delete()#必须先删除旧文件再保存，否则django会自动另存为新文件并添加随机后缀
                doc.content=new_docfile

                # html file
                f2 = file('media/app_blog_doc/'+str(arg_slug)+'.html','w+')#在文件系统中打开临时文件暂存
                new_docfile_html = File(f2)
                new_docfile_html.write(text_html)
                new_docfile_html.name = str(arg_slug)+'.html'
                if doc.content_html is not None:
                    doc.content_html.delete()#必须先删除旧文件再保存，否则django会自动另存为新文件并添加随机后缀
                doc.content_html=new_docfile_html

                doc.save()
                f1.close()
                f2.close()
                os.remove('media/app_blog_doc/'+str(arg_slug)+'.md')
                os.remove('media/app_blog_doc/'+str(arg_slug)+'.html')
                return HttpResponse(str(arg_slug)+".md：保存成功！")

#图片操作，无对应模板
@csrf_exempt  #插件的模板无法添加POST{% csrf_token %}，需要对此视图函数使用此装饰器
def image(request,column_slug,doc_slug,image_name):
    if column_slug is not None and doc_slug is not None:
        #在editmd页面里的图片上传处理
        if request.method == 'POST':
            try:
                upload_image = request.FILES.get('editormd-image-file',None)
                with open('media/app_blog_doc/'+str(column_slug)+'/'+str(doc_slug)+'/'+str(upload_image.name),'wb+') as f:
                    f.write(upload_image.read())
                return JsonResponse({\
                    "success":1,\
                    "message":"success",\
                    "url":request.path +'/'+str(upload_image.name)\
                    })#get_host()获取域名，path获取去掉域名的相对网址
            except:
                return JsonResponse({\
                    "success":0,\
                    "message":"上传失败！",\
                    "url":"null"\
                    })
        #图片链接
        elif request.method == 'GET':
            if image_name is not None:
                with open('media/app_blog_doc/'+str(column_slug)+'/'+str(doc_slug)+'/'+str(image_name) , 'rb') as f:
                    image = f.read()
                    response = HttpResponse(image)
                    response['Content-Type'] = 'image/*'
                    response['Content-Disposition'] = 'inline;filename=' + image_name #
                    return response
            else:
                return HttpResponse('')

#在editmd页面里的导出文件操作，无对应模板
def download(request,column_slug,doc_slug,doc_name):
    if column_slug is not None and doc_slug is not None and doc_name is not None:
        #返回文档实体文件.html内容。此处的GET参数由前端生成，需要编解码
        if doc_name.split('.')[1] == 'md':
            doc = blog.objects.get(column__slug=column_slug, slug=doc_slug)
            response = HttpResponse(doc.content)
            response['Content-Type'] = 'application/octet-stream' #设置为二进制流
            response['Content-Disposition'] = 'attachment;filename=' + doc_name #强制浏览器下载而不是查看流
            return response
        #返回文档实体文件.md内容。此处的GET参数由前端生成，需要编解码
        elif doc_name.split('.')[1] == 'html':
            doc = blog.objects.get(column__slug=column_slug, slug=doc_slug)
            response = HttpResponse(doc.content_html)
            response['Content-Type'] = 'application/octet-stream' #设置为二进制流
            response['Content-Disposition'] = 'attachment;filename=' + doc_name #强制浏览器下载而不是查看流
            return response
    else:
        return HttpResponse('None')
