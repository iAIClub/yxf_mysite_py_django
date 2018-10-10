# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,HttpResponseBadRequest,StreamingHttpResponse
from django.contrib.auth import authenticate, login as authlogin, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import sys
sys.path.append("..")
reload(sys)
sys.setdefaultencoding('utf8')
from .models import PanFile

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
            return HttpResponseRedirect(request.path+'?config=True')
        elif purpose == 'upload_file':
            username = request.user
            userpath = request.POST.get('filepath',None)
            try:
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
            except:
                messages.error(request,'上传失败！')
            return HttpResponseRedirect(request.path+'?pan=True')
        elif purpose == 'delete_file':
            username = request.user
            userpath = request.POST.get('userpath',None)
            filename = request.POST.get('filename',None)
            try:
                model_file = PanFile.objects.get(username=username,userpath=userpath,filename=filename)
                model_file.delete()
                messages.success(request,'删除成功！')
                return JsonResponse({"status":"ok"})
            except:
                return JsonResponse({"status":0})
        elif purpose == 'cancel_user':
            username = request.POST.get('username',None)
            password = request.POST.get('pd',None)
            password_c = request.POST.get('pd_c',None)
            email = request.POST.get('email',None)
            logger.debug(username)
            logger.debug(password)
            logger.debug(password_c)
            logger.debug(email)
            if authenticate(username=username, password=password_c) is not None and (password == password_c) and email is not None:
                try:
                    user = User.objects.get(username=username,email=email)
                    user.delete()
                    messages.success(request,'注销成功！')
                    return HttpResponseRedirect(reverse('index'))
                except:
                    messages.error(request,'注销失败！')
                    return HttpResponseRedirect(request.path+'?cancel=True')
            else:
                messages.error(request,'密码验证失败！')
                return HttpResponseRedirect(request.path+'?cancel=True')
        else:
            return JsonResponse({"status":0})
    elif request.method == 'GET':
        arg_list = request.GET.get('list',None)
        arg_config = request.GET.get('config',None)
        arg_pan = request.GET.get('pan',None)
        arg_cancel = request.GET.get('cancel',None)
        user = User.objects.get(username=request.user)
        model_doc = None
        model_file = PanFile.objects.filter(username=request.user).all()
        pan_list = []
        for item in model_file:
            pan_list.append({'username':user.username,'userpath':item.userpath,'filename':item.filename,'upload_time':item.upload_time})
        doc_list = None
        if arg_config is None and arg_pan is None and arg_cancel is None and arg_list is None:
            return HttpResponseRedirect(reverse('app_user_profile')+'?list=True')
        else:
            return HttpResponse(render(request, 'app_user/profile.html',{\
                'title':'菲菲的技术网站',\
                'user':user,\
                'arg_list':arg_list,\
                'arg_config':arg_config,\
                'arg_pan':arg_pan,\
                'arg_cancel':arg_cancel,\
                'list_res':'list=True',\
                'config_res':'config=True',\
                'pan_res':'pan=True',\
                'cancel_res':'cancel=True',\
                'pan_list':pan_list,\
                'doc_list':doc_list,\
                }))
    else:
        return JsonResponse({"status":0})

@login_required(login_url='/user/login')
def download(request, suburl):
    filename = suburl.split('/')[-1]
    model_file = PanFile.objects.get(file='app_user_pan/'+suburl) #FileField其实就是个存储了文件路径的char字符串
    response = HttpResponse(model_file.file)
    response['Content-Type'] = 'application/octet-stream' #设置为二进制流
    response['Content-Disposition'] = 'attachment;filename=' + filename #强制浏览器下载而不是查看流
    return response

@login_required(login_url='/user/login')
def settings(request):
    return HttpResponse(render(request, 'app_user/settings.html'))
