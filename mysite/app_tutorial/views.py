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
import shutil
from app_tutorial.models import Column,Tutorial,APP_FILE_ROOT,APP_TEMPLETE_ROOT
from app_blog.models import PostClass


# 网站首页
# /
def index(request):
    columns = Column.objects.all()
    post_classes = PostClass.objects.all()
    return HttpResponse(render(request, 'common/base.html', {\
        'title':'知道驿站',\
        'list':columns,\
        'list2':post_classes,\
        }))


# 文档首页
# 左侧列出所有栏目（可切换选定项），中间列出选定栏目的所有文档（需注意关键词列表），右侧显示选定栏目的信息
# /tutorial
def tutorial(request):
    columns = Column.objects.all()
    active = request.GET.get('active',None)#进入文档首页必须指定活动栏目
    if active is None:
        active = columns[0].slug
        return HttpResponseRedirect(reverse('app_tutorial')+'?active='+active)
    active_column = Column.objects.filter(slug=active)[0]
    docs = Tutorial.objects.filter(column__slug=active).order_by("publish_time")#选定栏目内的所有文档
    for doc in docs:
        tmp_keywords = []
        if str(doc.keywords):
            for keyword in str(doc.keywords).split(';'):
                tmp_keywords.append(keyword)
            doc.keywords=tmp_keywords
        else:
            doc.keywords = []
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html', {\
        'title':'文档',\
        'active':active,\
        'active_column':active_column,\
        'left_list':columns,\
        'content_list':docs,\
        }))


# 编辑器页，文档仅限管理员操作。可直接访问，也可通过iframe嵌入。新建文档、编辑文档的实际执行者
# /tutorial/editmd
def editmd(request):
    if request.method == 'GET':
        #返回编辑器页面
        arg_path = request.GET.get('path',None)
        arg_name = request.GET.get('name',None)
        arg_title = request.GET.get('title',None)
        html_name = arg_name.split('.')[0]+'.html'
        try:
            return HttpResponse(render(request,'common/editmd.html',{\
                'path':arg_path,\
                'name':arg_name,\
                'html_name':html_name,\
                'title':arg_title,\
                }))
        except:
            messages.error(request,'无效文档信息！')
            return HttpResponseRedirect(reverse('app_tutorial')+'doc/'+str(arg_path))


# 栏目页，与栏目文档页内容完全一致，通用一个模板，只不过显示的是默认index文档且url是栏目名
# /tutorial/doc/colslug
def column(request,column_slug):
    return doc(request=request,column_slug=column_slug,doc_slug='index')#交由doc()处理


# 栏目文档页
# 左侧列出本栏目所有文档（可切换文档），中间显示文档（需注意请求的是实体文件），右侧显示中间的文档对应的信息（需注意关键词列表）
# /tutorial/doc/colslug/docslug
def doc(request, column_slug, doc_slug):
    #POST操作文档域
    if request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        if purpose and request.user.is_superuser:
            try:
                #表单提交处理：新建文档，对文件主体的操作转到编辑器页面进行，为防止重复创建同名记录，需在模型设置column+slug组成联合主键
                if purpose == 'new':
                    column = Column.objects.filter(slug=column_slug)[0]
                    new_slug = request.POST.get('slug',None)
                    new_title = request.POST.get('title',None)
                    new_keywords = request.POST.get('keywords',None)
                    new_description = request.POST.get('description',None)
                    upload_file = request.FILES.get('file',None)
                    new_docfile = upload_file
                    if upload_file is None:
                        f = open(APP_FILE_ROOT+str(new_slug)+'.md','w+')  # 打开临时文件
                        new_docfile = File(f)
                        new_docfile.write('')
                        new_docfile.name = new_slug+'.md'
                        new_doc = Tutorial.objects.create(column=column,slug=new_slug,title=new_title,keywords=new_keywords,description=new_description,content=new_docfile)
                        new_doc.save()
                        f.close()
                        os.remove(APP_FILE_ROOT+str(new_slug)+'.md')  # 通过ORM会自动存储文件，此临时文件立即删除
                    else:
                        new_docfile.name = new_slug+'.md'
                        new_doc = Tutorial.objects.create(column=column,slug=new_slug,title=new_title,keywords=new_keywords,description=new_description,content=new_docfile)
                        new_doc.save()
                    return HttpResponseRedirect(reverse('app_tutorial_editmd')+'?path=tutorial/doc/'+column_slug+'/'+new_slug+'&name='+new_slug+'.md'+'&title='+new_title)
                #表单提交处理：修改当前文档，对文件主体的操作转到编辑器页面进行
                elif purpose == 'edit':
                    new_title = request.POST.get('title',None)
                    new_keywords = request.POST.get('keywords',None)
                    new_description = request.POST.get('description',None)
                    doc = Tutorial.objects.filter(column__slug=column_slug,slug=doc_slug)[0]
                    doc.title=new_title #更新数据直接赋值即可
                    doc.keywords=new_keywords
                    doc.description=new_description
                    doc.save()
                    return HttpResponseRedirect(reverse('app_tutorial_editmd')+'?path=tutorial/doc/'+column_slug+'/'+doc_slug+'&name='+doc_slug+'.md'+'&title='+new_title)
                #表单提交处理：删除当前文档及其文件目录，成功后返回到栏目页
                elif purpose == 'delete':
                    content_doc = Tutorial.objects.get(column__slug=column_slug, slug=doc_slug)
                    content_doc.delete()
                    shutil.rmtree(APP_FILE_ROOT+str(column_slug)+'/'+str(doc_slug))  # ORM自动删除文件后会遗留空文件夹，需要手动删除空文件夹
                    return HttpResponseRedirect(reverse('app_tutorial')+'doc/'+column_slug)
                #表单提交处理：由editmd提交，保存修改，保存完成后仍然留在editmd页面
                elif purpose == 'save':
                    arg_path = request.POST.get('path',None)
                    arg_column = arg_path.split('/')[-2]
                    arg_slug = arg_path.split('/')[-1]
                    text_md = request.POST.get('editormd-markdown-textarea',None)
                    text_html = request.POST.get('editormd-html-textarea',None)
                    doc = Tutorial.objects.filter(column__slug=arg_column, slug=arg_slug)[0]

                    # md file
                    f1 = open(APP_FILE_ROOT+str(arg_slug)+'.md','w+')  # 在文件系统中打开临时文件暂存
                    new_docfile = File(f1)
                    new_docfile.write(text_md)
                    new_docfile.name = str(arg_slug)+'.md'
                    doc.content.delete()  # 必须先删除旧文件再保存，否则django会自动另存为新文件并添加随机后缀
                    doc.content=new_docfile

                    # html file
                    f2 = open(APP_FILE_ROOT+str(arg_slug)+'.html','w+')  # 在文件系统中打开临时文件暂存
                    new_docfile_html = File(f2)
                    new_docfile_html.write(text_html)
                    new_docfile_html.name = str(arg_slug)+'.html'
                    if doc.content_html is not None:
                        doc.content_html.delete()  # 必须先删除旧文件再保存，否则django会自动另存为新文件并添加随机后缀
                    doc.content_html=new_docfile_html

                    doc.save()
                    f1.close()
                    f2.close()
                    os.remove(APP_FILE_ROOT+str(arg_slug)+'.md')  # 删除临时文件
                    os.remove(APP_FILE_ROOT+str(arg_slug)+'.html')  # 删除临时文件
                    return HttpResponse(str(arg_slug)+".md：保存成功！")
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
            if Tutorial.objects.filter(column__slug=column_slug, slug=doc_slug):
                content_doc = Tutorial.objects.filter(column__slug=column_slug, slug=doc_slug)[0]
            else:
                f = open(APP_FILE_ROOT+'index.md','w+')
                new_docfile = File(f)
                new_docfile.write('')
                new_docfile.name = doc_slug+'.md'
                index = Tutorial.objects.create(column=column,slug=doc_slug,title=doc_slug,content=new_docfile)
                index.save()
                f.close()
                os.remove(APP_FILE_ROOT+str(doc_slug)+'.md')  # 删除临时文件
                content_doc = Tutorial.objects.filter(column__slug=column_slug, slug=doc_slug)[0]
        else:
            if Tutorial.objects.filter(column__slug=column_slug, slug=doc_slug):
                content_doc = Tutorial.objects.filter(column__slug=column_slug, slug=doc_slug)[0]
            else:
                html_404 = '<h1>Not Found</h1><p>The requested URL %s was not found on this server.</p>' %request.path
                return HttpResponseNotFound(html_404)
        #2.尝试读取文档对应的文件，若没有则默认为空
        content_doc_file = ''
        if content_doc.content:
            content_doc_file = content_doc.content.read()
        return HttpResponse(render(request, APP_TEMPLETE_ROOT+'doc.html',{\
            'title':content_doc.title,\
            'column':column,\
            'left_list':docs,\
            'content_doc':content_doc,\
            'content_doc_file':content_doc_file,\
            }))


# 导出文件操作，无对应模板
# /tutorial/doc/colslug/docslug/docname
def filed(request,column_slug,doc_slug,doc_name):
    if column_slug is not None and doc_slug is not None and doc_name is not None:
        #返回文档实体文件.html内容
        if doc_name.split('.')[1] == 'md':
            doc = Tutorial.objects.get(column__slug=column_slug, slug=doc_slug)
            response = HttpResponse(doc.content)
            response['Content-Type'] = 'application/octet-stream' #设置为二进制流
            response['Content-Disposition'] = 'attachment;filename=' + doc_name #强制浏览器下载而不是查看流
            return response
        #返回文档实体文件.md内容
        elif doc_name.split('.')[1] == 'html':
            doc = Tutorial.objects.get(column__slug=column_slug, slug=doc_slug)
            response = HttpResponse(doc.content_html)
            response['Content-Type'] = 'application/octet-stream' #设置为二进制流
            response['Content-Disposition'] = 'attachment;filename=' + doc_name #强制浏览器下载而不是查看流
            return response
    else:
        return HttpResponse('None')


# 图片操作，无对应模板
# /tutorial/doc/colslug/docslug/image
# /tutorial/doc/colslug/docslug/image/imagename
@csrf_exempt  #插件的模板无法添加POST{% csrf_token %}，需要对此视图函数使用此装饰器
def image(request,column_slug,doc_slug,image_name):
    if column_slug is not None and doc_slug is not None:
        #在editmd页面里的图片上传处理
        if request.method == 'POST' and request.user.is_superuser:
            try:
                upload_image = request.FILES.get('editormd-image-file',None)
                with open(APP_FILE_ROOT+str(column_slug)+'/'+str(doc_slug)+'/'+str(upload_image.name),'wb+') as f:
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
                with open(APP_FILE_ROOT+str(column_slug)+'/'+str(doc_slug)+'/'+str(image_name) , 'rb') as f:
                    image = f.read()
                    response = HttpResponse(image)
                    response['Content-Type'] = 'image/'+image_name.split('.')[-1] #要设置具体格式才能在浏览器自动打开
                    return response
            else:
                return HttpResponse('')
