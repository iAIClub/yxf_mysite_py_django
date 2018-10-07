# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.contrib.auth import authenticate, login as authlogin, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

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
        if username is not None and password is not None:
            user = User.objects.create_user(username, email, password)
            user.save()
            return HttpResponseRedirect(reverse('app_user_login'))
        else:
            messages.error(request,'注册失败！')
            return HttpResponse(render(request, 'app_user/register.html'))
    else:
        return HttpResponse(render(request, 'app_user/register.html'))

@login_required(login_url='/user/login')
def profile(request):
    # 以下两条语句等价于login_required装饰器
    # if not request.user.is_authenticated:
    #     return HttpResponseRedirect('%s?next=%s' % (reverse('app_user_login'), request.path))
    return HttpResponse(render(request, 'app_user/profile.html'))

@login_required(login_url='/user/login')
def settings(request):
    return HttpResponse(render(request, 'app_user/settings.html'))

def ajax(request):
    if request.method == 'POST':
        purpose = request.POST.get('purpose',None)
        username = request.POST.get('username',None)
        if purpose == 'check_user':
            count = User.objects.filter(username=username).count()
            return JsonResponse({"username":username,"count":count})
        elif purpose == 'check_login':
            pass
        elif purpose == 'logout':
            authlogout(request)
            return JsonResponse({"status":"logout"})
        else:
            return JsonResponse({"status":0})
    else:
        return JsonResponse({"status":0})