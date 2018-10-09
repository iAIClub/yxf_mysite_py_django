# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.contrib.auth import authenticate, login as authlogin, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import sys
sys.path.append("..")
reload(sys)
sys.setdefaultencoding('utf8')
from .models import PanFile

import logging
logger = logging.getLogger("django") # 为loggers中定义的名称
logger.debug('############################app_user_view debug start')

# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username',None)
        password = request.POST.get('pd',None)
        count = User.objects.filter(username=username).count()
        if count == 0:
            messages.error(request,'用户不存在！')#在请求信息中加入messages消息内容，下次请求时会被提取并清除（基于会话）
            return HttpResponse(render(request, 'app_user/login.html'))
        user = authenticate(username=username, password=password)#在后台认证此用户
        if user is None:
            messages.error(request,'登录失败！')#在请求信息中加入messages消息内容，下次请求时会被提取并清除（基于会话）
            return HttpResponse(render(request, 'app_user/login.html'))
        authlogin(request, user)#登录，将在session中保持登录状态
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponse(render(request, 'app_user/login.html'))

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username',None)
        email = request.POST.get('email',None)
        password = request.POST.get('pd',None)
        if username is not None and password is not None and email is not None:
            user = User.objects.create_user(username, email, password)
            user.save()
            return HttpResponseRedirect(reverse('app_user_login'))
        else:
            messages.error(request,'注册失败！')
            return HttpResponse(render(request, 'app_user/register.html'))
    else:
        return HttpResponse(render(request, 'app_user/register.html'))

def ajax(request):
    if request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        username = request.POST.get('username',None)
        if purpose == 'check_user':
            count = User.objects.filter(username=username).count()
            return JsonResponse({"username":username,"count":count})
        elif purpose == 'logout':
            authlogout(request)
            return JsonResponse({"status":"logout"})
        else:
            return JsonResponse({"status":0})
    else:
        return JsonResponse({"status":0})

@login_required(login_url='/user/login')
def profile(request):
    if request.method == 'POST':
        purpose = request.POST.get('purpose',None)
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
            return HttpResponseRedirect(request.path)
        elif purpose == 'upload_file':
            username = request.user
            userpath = request.POST.get('filepath',None)
            #try:
            for file in request.FILES.getlist('upload-file'):#<input type="file" name="upload-file">
                upload_file = file
                filename = upload_file.name
                # upload_file.size #文件大小    做文件上传大小限制
                # upload_file.content_type #文件类型  做文件上传类型限制
                #通用方法：上传到模型类的文件字段FileField（缺点：需要处理与文件系统同步的问题，删除模型不会删除文件）
                #文件模型类，直接把上传的文件传递给FileField字段，框架会自动调用文件系统新建对应的实体文件
                model_file = PanFile.objects.create(\
                    username=username,userpath=str(userpath),filename=str(filename),file=upload_file)
                model_file.save()
            messages.success(request,'上传成功！')
            #另一种方法：直接调用文件系统创建文件，不经过框架模型类（缺点：不能通过数据库监视）
            # destination = open(filepath+'/'+filename,'wb+')#打开文件进行二进制的写操作
            # for chunk in upload_file.chunks(): #分块写入文件
            #     destination.write(chunk)
            # destination.close()
            #except:
            #messages.error(request,'上传失败！')
            return HttpResponseRedirect(request.path)
        elif purpose == 'cancel_user':
            username = request.POST.get('username',None)
            password = request.POST.get('pd',None)
            messages.success(request,'操作成功！')
        else:
            return JsonResponse({"status":0})
    elif request.method == 'GET':
        arg_config = request.GET.get('config',None)
        arg_pan = request.GET.get('pan',None)
        arg_cancel = request.GET.get('cancel',None)
        user = User.objects.get(username=request.user)
        right = None
        return HttpResponse(render(request, 'app_user/profile.html',{\
            'title':'菲菲的技术网站',\
            'arg_config':arg_config,\
            'arg_pan':arg_pan,\
            'arg_cancel':arg_cancel,\
            'config_res':'config=True',\
            'pan_res':'pan=True',\
            'cancel_res':'cancel=True',\
            'user':user,\
            'right':right,\
            }))
    else:
        return JsonResponse({"status":0})

@login_required(login_url='/user/login')
def settings(request):
    return HttpResponse(render(request, 'app_user/settings.html'))

logger.debug('############################app_user_view debug end')