# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,HttpResponseBadRequest,StreamingHttpResponse
from django.contrib.auth import authenticate, login as authlogin, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.files import File
import sys
import shutil
import os
import glob
reload(sys)
sys.setdefaultencoding('utf8')
from app_user.models import PanFile,APP_FILE_ROOT,APP_TEMPLETE_ROOT,APP_TUTORIAL_ROOT
from app_tutorial.models import Column,Tutorial
from modules.docProcess.docProcess import unzip,execute_doc


#网站设置区，仅限管理员操作，使用另一套模板
#/settings
@login_required(login_url='/user/login')
def settings(request):
    if request.method == 'GET':
        if request.user.is_superuser:
            arg_status = request.GET.get('status',None)
            arg_history = request.GET.get('history',None)
            arg_doc = request.GET.get('doc', None)
            arg_data = request.GET.get('data',None)
            arg_set = request.GET.get('set',None)
            if arg_status is None and arg_history is None and arg_doc is None and arg_data is None and arg_set is None:
                return HttpResponseRedirect(reverse('settings')+'?status=1')
            else:
                return HttpResponse(render(request, APP_TEMPLETE_ROOT+'settings.html',{\
                    'title':'设置',\
                    'arg_status':arg_status,\
                    'arg_history':arg_history, \
                    'arg_doc': arg_doc, \
                    'arg_data':arg_data,\
                    'arg_set':arg_set,\
                    }))
        else:
            return HttpResponse('<script type="text/javascript">alert("您没有权限访问此页面！");window.history.back(-1);</script>')
    elif request.method == 'POST':
        if request.user.is_superuser:
            purpose = request.POST.get('purpose', None)
            if purpose == 'upload_file':
                # 上传后解压缩保存到应用目录下
                try:
                    for upload_file in request.FILES.getlist('upload-file'):
                        zipfile_name = str(upload_file.name)
                        column_slug = zipfile_name.split('.')[0]
                        # save zipfile
                        file = open(APP_TUTORIAL_ROOT+zipfile_name, 'wb+')
                        for chunk in upload_file.chunks():
                            file.write(chunk)
                        file.close()
                        # remove old doc
                        if Column.objects.filter(slug=column_slug):
                            old_column = Column.objects.filter(slug=column_slug)[0]
                            old_column.delete()  # tutorial已关联此外键，会一并删除
                        if os.path.exists(APP_TUTORIAL_ROOT+column_slug):
                            shutil.rmtree(APP_TUTORIAL_ROOT+column_slug)
                        # unzip
                        unzip(APP_TUTORIAL_ROOT, zipfile_name)
                        # deploy new doc:convert
                        for file1 in glob.glob(APP_TUTORIAL_ROOT + column_slug + '/*.docx'):
                            execute_doc(file1,do_html=False)
                        # deploy new doc:columns
                        new_column = Column.objects.create(slug=column_slug,name=column_slug)
                        new_column.save()
                        # deploy new doc:tutorials
                        column = Column.objects.filter(slug=column_slug)[0]
                        for file2 in glob.glob(APP_TUTORIAL_ROOT+column_slug+'/*.md'):
                            f = open(file2, 'r')
                            new_docfile = File(f)
                            new_docfile_slug = file2.split('.')[0].split('/')[-1]
                            new_docfile.name = new_docfile_slug + '.md'
                            new_doc = Tutorial.objects.create(column=column, slug=new_docfile_slug, title=new_docfile_slug,content=new_docfile)
                            new_doc.save()
                            f.close()
                            os.remove(file2)
                            os.remove(file2.split('.')[0]+'.docx')
                        # remove zipfile
                        os.remove(APP_TUTORIAL_ROOT + str(upload_file.name))
                    messages.success(request, '上传成功！')
                except:
                    messages.error(request, '上传失败！')
                return HttpResponseRedirect(request.path + '?doc=1')


# 直接跳转，无内容
# /user
def user(request):
    return HttpResponseRedirect(reverse('app_user_profile'))


# 对应登录模板，登录逻辑
# /user/login
def login(request):
    if request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        if purpose == 'login':
            username = request.POST.get('username',None)
            password = request.POST.get('pd',None)
            count = User.objects.filter(username=username).count()
            if count == 0:
                messages.error(request,'用户不存在！')#在请求信息中加入messages消息内容，下次请求时会被提取并清除（基于会话）
                return HttpResponse(render(request, APP_TEMPLETE_ROOT+'login.html'))
            user = authenticate(username=username, password=password)#在后台认证此用户
            if user is None:
                messages.error(request,'登录失败！')#在请求信息中加入messages消息内容，下次请求时会被提取并清除（基于会话）
                return HttpResponse(render(request, APP_TEMPLETE_ROOT+'login.html'))
            authlogin(request, user)#登录，将在session中保持登录状态
            return HttpResponseRedirect(reverse('index'))
        elif purpose == 'logout':
            authlogout(request)
            return JsonResponse({"status":"logout"})
    else:
        return HttpResponse(render(request, APP_TEMPLETE_ROOT+'login.html'))


# 对应注册模板，注册逻辑
# /user/register
def register(request):
    if request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        if purpose == 'register':
            username = request.POST.get('username',None)
            email = request.POST.get('email',None)
            password = request.POST.get('pd',None)
            if username is not None and password is not None and email is not None:
                count = User.objects.filter(username=username).count()
                if count == 0:
                    user = User.objects.create_user(username, email, password)
                    user.save()
                    return HttpResponseRedirect(reverse('app_user_login'))
                else:
                    messages.error(request,'注册失败！')
                    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'register.html'))
            else:
                messages.error(request,'注册失败！')
                return HttpResponse(render(request, APP_TEMPLETE_ROOT+'register.html'))
        elif purpose == 'check_user':
            username = request.POST.filter('username',None)
            count = User.objects.filter(username=username).count()
            return JsonResponse({"username":username,"count":count})
        else:
            return JsonResponse({"status":0})
    else:
        return HttpResponse(render(request, APP_TEMPLETE_ROOT+'register.html'))


# 用户区。左侧列出用户的所有操作项，中间输出操作内容（所属博客文档，所属网盘文件，用户信息更改和注销），右侧按需显示相关信息
# /user/profile
@login_required(login_url='/user/login')
def profile(request):
    # 页面请求处理：根据GET参数解析模板，返回对应的页面内容
    if request.method == 'GET':
        arg_pan = request.GET.get('pan', None)
        arg_config = request.GET.get('config',None)
        arg_cancel = request.GET.get('cancel',None)
        user = User.objects.get(username=request.user.username)
        model_file = PanFile.objects.filter(user=request.user).all()
        pan_list = []
        for item in model_file:
            pan_list.append({'username':user.username,'userpath':item.userpath,'filename':item.filename,'upload_time':item.upload_time})
        doc_list = []
        if arg_config is None and arg_pan is None and arg_cancel is None:
            return HttpResponseRedirect(reverse('app_user_profile')+'?pan=1')
        else:
            return HttpResponse(render(request, APP_TEMPLETE_ROOT+'profile.html',{\
                'title':'用户区',\
                'user':user,\
                'arg_config':arg_config,\
                'arg_pan':arg_pan,\
                'arg_cancel':arg_cancel,\
                'config_res':'config=1',\
                'pan_res':'pan=1',\
                'cancel_res':'cancel=1',\
                'pan_list':pan_list,\
                'doc_list':doc_list,\
                }))
    elif request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        # 表单提交处理：用户信息更改
        if purpose == 'change_config':
            username = request.POST.get('username',None)
            password_old = request.POST.get('pd_old',None)
            password_new = request.POST.get('pd_new',None)
            password_new_c = request.POST.get('pd_new_c',None)
            email = request.POST.get('email',None)
            if authenticate(username=username, password=password_old) is not None and (password_new == password_new_c):
                try:
                    user = User.objects.get(username=username)
                    user.set_password(password_new_c)#安全的修改密码的方法
                    user.email = email
                    user.save()
                    messages.success(request,'操作成功，请使用新的用户信息登录！')
                except:
                    messages.error(request,'操作失败！')
            else:
                messages.error(request,'密码验证失败！')
            return HttpResponseRedirect(request.path+'?config=1')
        # 表单提交处理：上传文件
        elif purpose == 'upload_file':
            username = request.user
            user = User.objects.get(username=username)
            userpath = request.POST.get('filepath',None)
            try:
                for upload_file in request.FILES.getlist('upload-file'):#<input type="file" name="upload-file">
                    filename = upload_file.name
                    # upload_file.size #文件大小    做文件上传大小限制
                    # upload_file.content_type #文件类型  做文件上传类型限制
                    model_file = PanFile.objects.create(user=user,userpath=str(userpath),filename=str(filename),file=upload_file)
                    model_file.save()
                messages.success(request,'上传成功！')
                # 另一种方法：直接调用文件系统创建文件，不经过框架模型类（缺点：不能通过数据库监视）
                # destination = open(filepath+'/'+filename,'wb+')#打开文件进行二进制的写操作
                # for chunk in upload_file.chunks(): #分块写入文件
                #     destination.write(chunk)
                # destination.close()
            except:
                messages.error(request,'上传失败！')
            return HttpResponseRedirect(request.path+'?pan=1')
        # 表单提交处理：删除文件
        elif purpose == 'delete_file':
            username = request.user
            userpath = request.POST.get('userpath',None)
            filename = request.POST.get('filename',None)
            if PanFile.objects.filter(user__username=username,userpath=userpath,filename=filename):
                model_file = PanFile.objects.filter(user__username=username,userpath=userpath,filename=filename)[0]
                model_file.delete()
                messages.success(request,'删除成功！')
                return JsonResponse({"status":"ok"})
            else:
                return JsonResponse({"status":0})
        # 表单提交处理：注销用户
        elif purpose == 'cancel_user':
            username = request.POST.get('username',None)
            password = request.POST.get('pd',None)
            password_c = request.POST.get('pd_c',None)
            email = request.POST.get('email',None)
            if authenticate(username=username, password=password_c) is not None and (password == password_c) and email is not None:
                if User.objects.filter(username=username,email=email):
                    user = User.objects.filter(username=username,email=email)[0]
                    user.delete()
                    messages.success(request,'注销成功！')
                    return HttpResponseRedirect(reverse('index'))
                else:
                    messages.error(request,'注销失败！')
                    return HttpResponseRedirect(request.path+'?cancel=1')
            else:
                messages.error(request,'密码验证失败！')
                return HttpResponseRedirect(request.path+'?cancel=1')
        else:
            return JsonResponse({"status":0})
    else:
        return JsonResponse({"status":0})


# 对应文件下载链接，无模板，直接返回文件。链接是翻译后的虚拟文件路径，并非实际路径
# /user/download/..
@login_required(login_url='/user/login')
def download(request, suburl):
    filename = suburl.split('/')[-1]
    model_file = PanFile.objects.filter(file=APP_FILE_ROOT+suburl)[0] #FileField其实就是个存储了文件路径的char字符串
    response = HttpResponse(model_file.file)
    response['Content-Type'] = 'application/octet-stream' #设置为二进制流
    response['Content-Disposition'] = 'attachment;filename=' + filename #强制浏览器下载而不是查看流
    return response
