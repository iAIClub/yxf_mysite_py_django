# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,HttpResponseBadRequest,StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.contrib.auth import authenticate, login as authlogin, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.files import File
import sys
import shutil
import os
import re
import glob
import datetime
import psutil
import subprocess
import logging
reload(sys)
sys.setdefaultencoding('utf8')
from app_user.models import PanFile,APP_FILE_ROOT,APP_TEMPLETE_ROOT,APP_TUTORIAL_ROOT
from app_tutorial.models import Column,Tutorial
from modules.docProcess import docProcess
from mysite.settings import BASE_DIR


# 网站设置区，仅限管理员操作，使用另一套模板
# /settings
@login_required(login_url='/user/login')
def settings(request):
    if request.method == 'GET':
        if request.user.is_superuser:
            arg_status = request.GET.get('status',None)
            arg_history = request.GET.get('history',None)
            arg_doc = request.GET.get('doc', None)
            arg_data = request.GET.get('data',None)
            arg_set = request.GET.get('set',None)
            doc_list = []
            status_list = []
            log_list = []
            if arg_status:
                status_list.append({'CPU占用':str(psutil.cpu_count(logical=False))+'核/'+str(psutil.cpu_percent())+'%'})
                status_list.append({'内存占用':str(round(psutil.virtual_memory().used/(1024.0*1024.0*1024.0),2))+'G/'+str(round(psutil.virtual_memory().total/(1024.0*1024.0*1024.0),2))+'G='+str(psutil.virtual_memory().percent)+'%'})
                status_list.append({'硬盘占用':str(round(psutil.disk_usage('/').used/(1024.0*1024.0*1024.0),2))+'G/'+str(round(psutil.disk_usage('/').total/(1024.0*1024.0*1024.0),2))+'G='+str(psutil.disk_usage('/').percent)+'%'})
                status_list.append({'网络地址':psutil.net_if_addrs()})
                status_list.append({'网络状态':psutil.net_if_stats()})
                status_list.append({'登录信息':psutil.users()})
                status_list.append({'启动时间':datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")})
                pid_list = []
                for pid in psutil.pids():
                    p = psutil.Process(pid)
                    if p.name() in ['python','python3','java','redis-server','nginx','postmaster','sshd','uwsgi']:
                        pid_list.append({'{0}:{1}'.format(str(pid),p.name()):{
                            'pid':p.pid,
                            'name':p.name(),
                            'username':p.username(),
                            'exe':p.exe(),
                            'cwd':p.cwd(),
                            'status':p.status(),
                            'create_time':datetime.datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
                            'cpu_times':p.cpu_times(),
                            'memory_percent': p.memory_percent(),
                            'num_threads':p.num_threads(),
                        }})
                status_list.append({'进程信息':pid_list})
            if arg_doc:
                model_file = Tutorial.objects.filter().all()
                for item in model_file:
                    doc_list.append({'column': item.column.name, 'title': item.title,'update_time': item.update_time})
            if arg_history:
                with open(os.path.join(BASE_DIR,'log/nginx_error.log'),'r') as f:
                    log_list.append({'nginx_error':f.read()})
                with open(os.path.join(BASE_DIR, 'log/uwsgi.log'), 'r') as f:
                    log_list.append({'uwsgi':f.read()})
                with open(os.path.join(BASE_DIR, 'log/django.log'), 'r') as f:
                    log_list.append({'django':f.read()})
            if arg_status is None and arg_history is None and arg_doc is None and arg_data is None and arg_set is None:
                return HttpResponseRedirect(reverse('settings')+'?status=1')
            else:
                return HttpResponse(render(request, APP_TEMPLETE_ROOT+'settings.html',{\
                    'title':'设置',\
                    'arg_status':arg_status,\
                    'arg_history':arg_history, \
                    'arg_doc': arg_doc, \
                    'arg_data':arg_data,\
                    'arg_set':arg_set, \
                    'doc_list': doc_list, \
                    'status_list':status_list,\
                    'log_list':log_list,\
                    }))
        else:
            return HttpResponse('<script type="text/javascript">alert("您没有权限访问此页面！");window.history.back(-1);</script>')
    elif request.method == 'POST':
        if request.user.is_superuser:
            purpose = request.POST.get('purpose', None)
            # 更新文档内容
            if purpose == 'update_doc':
                try:
                    for upload_file in request.FILES.getlist('upload-file'):
                        zipfile_name = str(upload_file.name)
                        column_slug = zipfile_name.split('.')[0]
                        # 1.save zipfile
                        file = open(APP_TUTORIAL_ROOT+zipfile_name, 'wb+')
                        for chunk in upload_file.chunks():
                            file.write(chunk)
                        file.close()
                        # 2.remove old doc
                        if Column.objects.filter(slug=column_slug):
                            old_column = Column.objects.filter(slug=column_slug)[0]
                            old_column.delete()  # tutorial已关联此外键，会一并删除
                        if os.path.exists(APP_TUTORIAL_ROOT+column_slug):
                            shutil.rmtree(APP_TUTORIAL_ROOT+column_slug)
                        # 3.unzip
                        docProcess.unzip(APP_TUTORIAL_ROOT, zipfile_name)
                        # 4.deploy new doc:convert
                        for file1 in glob.glob(APP_TUTORIAL_ROOT + column_slug + '/*.docx'):
                            docProcess.execute_docx(file1)
                        # 5.deploy new doc:columns
                        new_column = Column.objects.create(slug=column_slug,name=column_slug)
                        new_column.save()
                        # 6.deploy new doc:tutorials
                        column = Column.objects.filter(slug=column_slug)[0]
                        for file2 in glob.glob(APP_TUTORIAL_ROOT+column_slug+'/*.md'):
                            f = open(file2, 'r')
                            new_docfile = File(f)
                            new_docfile_slug = file2.split('.')[0].split('/')[-1]
                            try:
                                new_docfile_keywords = ';'.join(re.split('[-,\+]',new_docfile_slug))
                            except:
                                new_docfile_keywords = new_docfile_slug
                            new_docfile_description = ''
                            while not new_docfile_description:  # utf-8中文字符不确定在哪个字节结束，需要尝试
                                try_num = 0
                                try:
                                    try_num += 1
                                    new_docfile_description += str(f.read(100+try_num))
                                except:
                                    try_num += 1
                                if try_num >= 5:
                                    break
                            new_docfile.name = new_docfile_slug + '.md'
                            new_doc = Tutorial.objects.create(column=column,
                                                              slug=new_docfile_slug,
                                                              title=new_docfile_slug,
                                                              keywords=new_docfile_keywords,
                                                              description=new_docfile_description,
                                                              content=new_docfile)
                            new_doc.save()
                            f.close()
                            os.remove(file2)
                        for file3 in glob.glob(APP_TUTORIAL_ROOT+column_slug+'/*.html'):
                            f = open(file3, 'r')
                            new_htmlfile = File(f)
                            new_htmlfile_slug = file3.split('.')[0].split('/')[-1]
                            new_htmlfile.name = new_htmlfile_slug + '.html'
                            doc = Tutorial.objects.filter(column=column, slug=new_htmlfile_slug)[0]
                            doc.content_html = new_htmlfile
                            doc.save()
                            f.close()
                            os.remove(file3.split('.')[0] + '.html')
                        # 7.remove zipfile
                        os.remove(APP_TUTORIAL_ROOT + str(upload_file.name))
                    messages.success(request, '上传成功！')
                except:
                    messages.error(request, '上传失败！')
                return HttpResponseRedirect(request.path + '?doc=1')
            # 数据导出
            elif purpose == 'dump_data':
                dumptype = request.POST.get('dumptype',None)
                # 打包media文件数据
                if dumptype == 'dump_data_media':
                    try:
                        if os.path.exists('media/media.zip'):
                            os.remove('media/media.zip')
                        docProcess.zip('media')
                        shutil.move('media.zip','media')
                        messages.success(request, '打包成功！')
                    except:
                        messages.error(request, '打包失败！')
                # 导出django的json数据文件
                elif dumptype == 'dump_db_json':
                    try:
                        subprocess.call('{0}/scripts/dump_json.sh'.format(BASE_DIR))
                        messages.success(request, '导出成功！')
                    except:
                        messages.error(request, '导出失败！')
                # 导出postgresql数据库SQL脚本
                elif dumptype == 'dump_db_sql':
                    try:
                        subprocess.call('{0}/scripts/dump_sql.sh'.format(BASE_DIR))
                        messages.success(request, '导出成功！')
                    except:
                        messages.error(request, '导出失败！')
                return HttpResponseRedirect(request.path + '?data=1')
            # 清空历史数据(app_webtrans的通信历史/网站日志)
            elif purpose == 'clean_log':
                logtype = request.POST.get('logtype',None)
                if logtype == 'nginx_error':
                    with open(os.path.join(BASE_DIR, 'log/nginx_error.log'), 'w') as f:
                        f.write('')
                elif logtype == 'uwsgi':
                    with open(os.path.join(BASE_DIR, 'log/uwsgi.log'), 'w') as f:
                        f.write('')
                elif logtype == 'django':
                    with open(os.path.join(BASE_DIR, 'log/django.log'), 'w') as f:
                        f.write('')
                messages.success(request, '清除成功！')
                return HttpResponseRedirect(request.path + '?history=1')
            # 核心操作
            elif purpose == 'server_set':
                settype = request.POST.get('settype',None)
                # git更新网站项目
                if settype == 'update_project':
                    try:
                        subprocess.call('~/deploy_mysite.sh')
                    except:
                        subprocess.call('/opt/yxf_utils/scripts/deploy_mysite.sh')
                    else:
                        messages.success(request, '执行成功！')
                # 重启主服务（只能关闭，无法重启，放弃）
                # elif settype == 'restart_mainserver':
                #     try:
                #         p1 = subprocess.Popen('/opt/yxf_mysite_py_django/stop_server.sh', shell=True,close_fds=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                #         p1.stdin.write('\n')
                #         p1.wait()
                #         subprocess.call('systemctl restart uwsgi',shell=True)
                #     except:
                #         messages.error(request, '执行失败！')
                # 重启辅服务
                elif settype == 'restart_subserver':
                    try:
                        p1 = subprocess.Popen('/opt/yxf_mysite_py_django/stop_server.sh',shell=True,close_fds=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
                        p1.stdin.write('\n')
                        p1.wait()
                        p2 = subprocess.Popen('/opt/yxf_mysite_py_django/start_server.sh',shell=True,close_fds=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
                        p2.stdin.write('\n')
                        p2.wait()
                        messages.success(request, '执行成功！')
                    except:
                        messages.error(request, '执行失败！')
                return HttpResponseRedirect(request.path + '?set=1')


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
        if arg_pan:
            for item in model_file:
                pan_list.append({'username':user.username,'userpath':item.userpath,'filename':item.filename,'upload_time':item.upload_time})
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
                for upload_file in request.FILES.getlist('upload-file'):
                    filename = upload_file.name
                    model_file = PanFile.objects.create(user=user,userpath=str(userpath),filename=str(filename),file=upload_file)
                    model_file.save()
                messages.success(request,'上传成功！')
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
    if suburl == 'mysite.json' or suburl == 'mysite.sql' or suburl == 'media.zip':
        if suburl == 'mysite.json':
            model_file = open(os.path.join(BASE_DIR,'media/mysite.json'),'r')
            response = HttpResponse(model_file.read())
            model_file.close()
        elif suburl == 'mysite.sql':
            model_file = open(os.path.join(BASE_DIR,'media/mysite.sql'), 'r')
            response = HttpResponse(model_file.read())
            model_file.close()
        elif suburl == 'media.zip':
            wrapper = FileWrapper(open(os.path.join(BASE_DIR,'media/media.zip'), 'rb'))  # django提供文件流的装饰器，不必自己实现
            response = StreamingHttpResponse(wrapper)
        else:
            response = HttpResponse('None')
    else:
        model_file = PanFile.objects.filter(file=APP_FILE_ROOT + suburl)[0]  # FileField其实就是个存储了文件路径的char字符串
        response = HttpResponse(model_file.file)
    response['Content-Type'] = 'application/octet-stream'  # 设置为二进制流
    response['Content-Disposition'] = 'attachment;filename=' + filename #强制浏览器下载而不是查看流
    return response
