# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,HttpResponseNotFound
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import os
import shutil
from app_blog.models import PostClass,Post,APP_FILE_ROOT,APP_TEMPLETE_ROOT


# 博客首页
# /blog
def blog(request):
    if request.method == 'GET':
        post_classes = PostClass.objects.all()
        active = request.GET.get('active',None)
        if active is None:  # 按分类展示
            active = post_classes[0].name
            return HttpResponseRedirect(reverse('app_blog')+'?active='+active)
        active_post_class = PostClass.objects.filter(name=active)[0]
        posts = Post.objects.filter(post_class__name=active).order_by("publish_time")
        for post in posts:
            tmp_keywords = []
            if str(post.keywords):
                for keyword in str(post.keywords).split(';'):
                    tmp_keywords.append(keyword)
                post.keywords = tmp_keywords
            else:
                post.keywords = []
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
                post_class_id = request.POST.get('postclass',None)
                post_class = PostClass.objects.get(id=int(post_class_id))
                new_title = request.POST.get('title',None)
                new_keywords = request.POST.get('keywords',None)
                new_description = request.POST.get('description',None)
                new_post = Post.objects.create(post_class=post_class,user=user,title=new_title,keywords=new_keywords,description=new_description)
                new_post.save()
                new_post_id = new_post.id
                upload_file = request.FILES.get('file',None)
                new_postfile = upload_file
                if upload_file is None:
                    f = open(APP_FILE_ROOT+str(new_post_id)+'.md','w+')
                    new_postfile = File(f)
                    new_postfile.write('')
                    new_postfile.name = str(new_post_id)+'.md'
                    new_post.content = new_postfile
                    new_post.save()
                    f.close()
                    os.remove(APP_FILE_ROOT+str(new_post_id)+'.md')
                else:
                    new_postfile.name = str(new_post_id)+'.md'
                    new_post.content = new_postfile
                    new_post.save()
                return HttpResponseRedirect(reverse('app_blog_editmd')+'?path=blog/post/'+str(new_post_id)+'&name='+str(new_post_id)+'.md'+'&title='+new_title)
            except:
                messages.error(request,'操作失败！')
                return HttpResponseRedirect(request.path)


# 编辑器页。可直接访问，也可通过iframe嵌入。新建文档、编辑文档的实际执行者
# /blog/editmd
def editmd(request):
    if request.method == 'GET':
        #返回编辑器页面
        arg_path = request.GET.get('path', None)
        arg_name = request.GET.get('name', None)
        html_name = arg_name.split('.')[0]+'.html'
        arg_title = request.GET.get('title',None)
        try:
            return HttpResponse(render(request,'common/editmd.html',{\
                'path': arg_path,\
                'name': arg_name,\
                'html_name': html_name,\
                'title':arg_title,\
                }))
        except:
            messages.error(request,'无效文档信息！')
            return HttpResponseRedirect(reverse('app_blog')+'post/')


# 文章页
# 不显示左侧，内容+右侧信息
# /blog/post/postid
def post(request, post_id):
    #GET直接请求网页
    if request.method == 'GET':
        post_classes = PostClass.objects.all()
        content_post = []
        #1.尝试读取选定的文章
        try:
            content_post = Post.objects.filter(id=post_id)[0]
        except:
            html_404 = '<h1>Not Found</h1><p>The requested URL %s was not found on this server.</p>' %request.path
            return HttpResponseNotFound(html_404)
        #2.尝试读取文档对应的文件，若没有则默认为空
        content_post_file = ''
        try:
            content_post_file = content_post.content.read()
        except:
            pass
        return HttpResponse(render(request, 'app_blog/post.html',{\
            'title':content_post.title,\
            'left_list':post_classes,\
            'content_post':content_post,\
            'content_post_file':content_post_file,\
            }))
    #POST操作文档域
    elif request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        content_post = Post.objects.filter(id=post_id)[0]
        if purpose is not None and request.user.is_authenticated and request.user.username == content_post.user.username:
            try:
               #表单提交处理：修改当前文档，对文件主体的操作转到编辑器页面进行
                if purpose == 'edit':
                    new_title = request.POST.get('title',None)
                    new_keywords = request.POST.get('keywords',None)
                    new_description = request.POST.get('description',None)
                    content_post.title=new_title #更新数据直接赋值即可
                    content_post.keywords=new_keywords
                    content_post.description=new_description
                    content_post.save()
                    return HttpResponseRedirect(reverse('app_blog_editmd')+'?path=blog/post/'+str(post_id)+'&name='+str(post_id)+'.md'+'&title='+new_title)
                #表单提交处理：删除当前文档及其文件目录，成功后返回到栏目页
                elif purpose == 'delete':
                    content_post.delete()
                    shutil.rmtree(APP_FILE_ROOT+str(post_id))
                    return HttpResponseRedirect(reverse('app_blog'))
                # 表单提交处理：由editmd提交，保存修改，保存完成后仍然留在editmd页面
                elif purpose == 'save':
                    arg_path = request.POST.get('path', None)
                    arg_id = arg_path.split('/')[-1]
                    text_md = request.POST.get('editormd-markdown-textarea', None)
                    text_html = request.POST.get('editormd-html-textarea', None)

                    # md file
                    f1 = open(APP_FILE_ROOT + str(arg_id) + '.md', 'w+')  # 在文件系统中打开临时文件暂存
                    new_docfile = File(f1)
                    new_docfile.write(text_md)
                    new_docfile.name = str(arg_id) + '.md'
                    content_post.content.delete()  # 必须先删除旧文件再保存，否则django会自动另存为新文件并添加随机后缀
                    content_post.content = new_docfile

                    # html file
                    f2 = open(APP_FILE_ROOT + str(arg_id) + '.html', 'w+')  # 在文件系统中打开临时文件暂存
                    new_docfile_html = File(f2)
                    new_docfile_html.write(text_html)
                    new_docfile_html.name = str(arg_id) + '.html'
                    if content_post.content_html is not None:
                        content_post.content_html.delete()  # 必须先删除旧文件再保存，否则django会自动另存为新文件并添加随机后缀
                    content_post.content_html = new_docfile_html

                    content_post.save()
                    f1.close()
                    f2.close()
                    os.remove(APP_FILE_ROOT + str(arg_id) + '.md')  # 删除临时文件
                    os.remove(APP_FILE_ROOT + str(arg_id) + '.html')  # 删除临时文件
                    return HttpResponse(str(arg_id) + ".md：保存成功！")
            except:
                messages.error(request,'操作失败！')
        return HttpResponseRedirect(request.path)


# 在editmd页面里的导出文件操作，无对应模板
# /blog/post/postid/postname
def filed(request,post_id,post_name):
    if post_id is not None and post_name is not None:
        #返回文档实体文件.html内容。此处的GET参数由前端生成，需要编解码
        if post_name.split('.')[1] == 'md':
            post = Post.objects.get(id=post_id)
            response = HttpResponse(post.content)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename=' + post_name
            return response
        #返回文档实体文件.md内容。此处的GET参数由前端生成，需要编解码
        elif post_name.split('.')[1] == 'html':
            post = Post.objects.get(id=post_id)
            response = HttpResponse(post.content_html)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename=' + post_name
            return response
    else:
        return HttpResponse('None')


# 图片操作，无对应模板
# /blog/post/postid/image
# /blog/post/postid/image/imagename
@csrf_exempt  #插件的模板无法添加POST{% csrf_token %}，需要对此视图函数使用此装饰器
def image(request,post_id,image_name):
    if post_id is not None:
        #在editmd页面里的图片上传处理
        if request.method == 'POST' and request.user.is_authenticated:
            try:
                upload_image = request.FILES.get('editormd-image-file',None)
                with open(APP_FILE_ROOT+str(post_id)+'/'+str(upload_image.name),'wb+') as f:
                    f.write(upload_image.read())
                return JsonResponse({\
                    "success":1,\
                    "message":"success",\
                    "url":'http://'+request.get_host()+request.path +'/'+str(upload_image.name)\
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
                with open(APP_FILE_ROOT+str(post_id)+'/'+str(image_name), 'rb') as f:
                    image = f.read()
                    response = HttpResponse(image)
                    response['Content-Type'] = 'image/' + image_name.split('.')[-1]
                    return response
            else:
                return HttpResponse('')
