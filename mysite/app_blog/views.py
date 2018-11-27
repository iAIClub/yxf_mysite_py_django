# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,HttpResponseNotFound
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import os
import shutil
from app_blog.models import PostClass,Post,APP_FILE_ROOT,APP_TEMPLETE_ROOT

#博客首页，对所有人开放。左侧博文分类，中间所有用户的博文列表，右侧最新、最热、评论
#/blog
def blog(request):
    if request.method == 'GET':
        post_classes = PostClass.objects.all()
        active = request.GET.get('active',None)#进入文档首页必须指定活动栏目
        if active is None:
            active = post_classes[0].name
            return HttpResponseRedirect(reverse('app_blog')+'?active='+active)
        active_post_class = PostClass.objects.get(name=active)
        posts = Post.objects.filter(post_class__name=active).order_by("publish_time")#选定栏目内的所有博文
        for post in posts:
            try:
                tmp_keywords = []
                for keyword in post.keywords.split(';'):
                    tmp_keywords.append(keyword)
                post.keywords=tmp_keywords
            except:
                post.keywords=[]
        return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html', {\
            'title':'博客',\
            'active':active,\
            'active_post_class':active_post_class,\
            'left_list':post_classes,\
            'content_list':posts,\
            }))
    elif request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        if purpose == 'new' and request.user.is_authenticated:
            try:
                #表单提交处理：新建文档，对文件主体的操作转到编辑器页面进行
                user = User.objects.filter(username=request.user.username)[0]
                post_class_name = request.POST.get('postclass',None)
                post_class = PostClass.objects.get(name=post_class_name)
                new_title = request.POST.get('title',None)
                new_keywords = request.POST.get('keywords',None)
                new_description = request.POST.get('description',None)
                new_post = Post.objects.create(post_class=post_class,user=user,itle=new_title,keywords=new_keywords,description=new_description)
                new_post.save()
                new_post_id = new_post.id
                upload_file = request.FILES.get('file',None)
                new_postfile = upload_file
                if upload_file is None:
                    f = open('media/'+APP_FILE_ROOT+str(new_post_id)+'.md','w+')
                    new_postfile = File(f)
                    new_postfile.write('')
                    new_postfile.name = str(new_post_id)+'.md'
                    new_post.save()
                    f.close()
                    os.remove('media/'+APP_FILE_ROOT+str(new_post_id)+'.md')
                else:
                    new_postfile.name = str(new_post_id)+'.md'
                    new_post.save()
                return HttpResponseRedirect(reverse('app_blog_editmd')+'?path=blog/post/'+user.username+'/'+str(new_post_id)+'&name='+str(new_post_id)+'.md'+'&title='+new_title)
            except Exception as e:
                raise e
                messages.error(request,'操作失败！')
                return HttpResponseRedirect(request.path)

#编辑器页。可直接访问，也可通过iframe嵌入。新建文档、编辑文档的实际执行者
#/blog/editmd
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
                return HttpResponseRedirect(reverse('app_blog')+'post/'+str(request.user)+'/'+str(arg_slug))
        #返回文档实体文件.md内容。此处的GET参数由前端生成，需要编解码
        elif arg_getfile == 'md':
            arg_slug = request.GET.get('slug'.encode('utf-8'),None)
            post = Post.objects.get(user=request.user, slug=arg_slug)
            response = HttpResponse(post.content)
            response['Content-Type'] = 'application/octet-stream' #设置为二进制流
            response['Content-Disposition'] = 'attachment;filename=' + arg_slug+'.md' #强制浏览器下载而不是查看流
            return response

#用户文章列表页
#/blog/post/user
def user(request,user_name):
    post_classes = PostClass.objects.all()
    count = Post.objects.filter(user__username=user_nae).count()
    posts = Post.objects.filter(user__username=user_name).order_by("publish_time")
    for post in posts:
        try:
            tmp_keywords = []
            for keyword in doc.keywords.split(';'):
                tmp_keywords.append(keyword)
            post.keywords=tmp_keywords
        except:
            post.keywords=[]
    return HttpResponse(render(request, 'app_blog/index.html',{\
        'title':user+' - 所有文章',\
        'user':user,\
        'left_list':post_classes,\
        'count':count,\
        'content_list':posts,\
        }))

#文章页
#不显示左侧，内容+右侧信息
#/blog/post/user/postname
def post(request, user_name, post_id):
    author = user_name
    #GET直接请求网页
    if request.method == 'GET':
        post_classes = PostClass.objects.all()
        content_post = []
        #1.尝试读取选定的文章
        try:
            content_post = Post.objects.filter(user__username=author, slug=post)[0]
        except:
            html_404 = '<h1>Not Found</h1><p>The requested URL %s was not found on this server.</p>' %request.path
            return HttpResponseNotFound(html_404)
        #2.使用独立的新变量尝试读取关键词，若没有则设置为空列表
        content_post_keywords = []
        try:
            for keyword in content_post.keywords.split(';'):
                content_post_keywords.append(keyword)
        except:
            pass
        #3.尝试读取文档对应的文件，若没有则默认为空
        content_post_file = ''
        try:
            content_post_file = content_post.content.read()
        except:
            pass
        return HttpResponse(render(request, 'app_blog/post.html',{\
            'title':content_post.title,\
            'author':author,\
            'left_list':post_classes,\
            'content_post':content_post,\
            'content_post_keywords':content_post_keywords,\
            'content_post_file':content_post_file,\
            }))
    #POST操作文档域
    elif request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        if purpose is not None and request.user.is_authenticated and request.user.username == author:
            try:
               #表单提交处理：修改当前文档，对文件主体的操作转到编辑器页面进行
                if purpose == 'edit':
                    new_title = request.POST.get('title',None)
                    new_keywords = request.POST.get('keywords',None)
                    new_description = request.POST.get('description',None)
                    content_post = Post.objects.filter(user=request.user,slug=post)[0]
                    content_post.title=new_title #更新数据直接赋值即可
                    content_post.keywords=new_keywords
                    content_post.description=new_description
                    content_post.save()
                    return HttpResponseRedirect(reverse('app_blog_editmd')+'?user='+str(author)+'&slug='+post+'&title='+new_title)
                #表单提交处理：删除当前文档及其文件目录，成功后返回到栏目页
                elif purpose == 'delete':
                    content_post = Post.objects.get(user=request.user, slug=post)#文档
                    content_post.delete()
                    shutil.rmtree('media/app_blog_post/'+str(author)+'/'+str(post))
                    return HttpResponseRedirect(reverse('app_blog'))
            except Exception as e:
                raise e
                messages.error(request,'操作失败！')
        return HttpResponseRedirect(request.path)

#在editmd页面里的导出文件操作，无对应模板
def filed(request,user_name,post_id,post_name):
    if post is not None and post_name is not None:
        #返回文档实体文件.html内容。此处的GET参数由前端生成，需要编解码
        if post_name.split('.')[1] == 'md':
            post = Post.objects.get(user=request.user, slug=post)
            response = HttpResponse(post.content)
            response['Content-Type'] = 'application/octet-stream' #设置为二进制流
            response['Content-Disposition'] = 'attachment;filename=' + post_name #强制浏览器下载而不是查看流
            return response
        #返回文档实体文件.md内容。此处的GET参数由前端生成，需要编解码
        elif post_name.split('.')[1] == 'html':
            post = Post.objects.get(user=request.user, slug=post)
            response = HttpResponse(post.content_html)
            response['Content-Type'] = 'application/octet-stream' #设置为二进制流
            response['Content-Disposition'] = 'attachment;filename=' + post_name #强制浏览器下载而不是查看流
            return response
    else:
        return HttpResponse('None')

#图片操作，无对应模板
@csrf_exempt  #插件的模板无法添加POST{% csrf_token %}，需要对此视图函数使用此装饰器
def image(request,user_name,post_id,image_name):
    if post is not None:
        #在editmd页面里的图片上传处理
        if request.user.is_authenticated and request.method == 'POST':
            try:
                upload_image = request.FILES.get('editormd-image-file',None)
                with open('media/app_blog_post/'+str(request.user)+'/'+str(post)+'/'+str(upload_image.name),'wb+') as f:
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
                with open('media/app_blog_post/'+str(user)+'/'+str(post)+'/'+str(image_name) , 'rb') as f:
                    image = f.read()
                    response = HttpResponse(image)
                    response['Content-Type'] = 'image/*'
                    response['Content-Disposition'] = 'inline;filename=' + image_name
                    return response
            else:
                return HttpResponse('')

