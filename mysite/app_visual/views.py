# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import re
import random
import base64
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse,JsonResponse
from modules.imageProcess.imageProcess import ImageProcess
from modules.imageProcess.capcha import getCapcha
from modules.imageProcess.qr import getQrcode
from app_visual.models import APP_FILE_ROOT,APP_TEMPLETE_ROOT

def index(request):
    return HttpResponseRedirect(reverse('app_visual_dsvisual'))

def dsvisual(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'数据结构与算法',\
        'display':'dsvisual',\
        }))

def picture(request):
    if request.method == 'GET':
        return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
            'title':'图像处理',\
            'display':'picture',\
            }))
    elif request.method == 'POST':
        op = request.POST.get('op',None)
        if op == 'image':
            if request.FILES.get('image1',None) is not None:
                image_path1 = APP_FILE_ROOT+'image/1_'+request.FILES['image1'].name
                with open(image_path1,'wb') as f:
                    for line in request.FILES['image1']:
                        f.write(line)
                if request.FILES.get('image2',None):
                    image_path2 = APP_FILE_ROOT + 'image/2_'+request.FILES['image2'].name
                    with open(image_path2, 'wb') as f:
                        for line in request.FILES['image2']:
                            f.write(line)
                else:
                    image_path2 = ''
                if request.FILES.get('mask', None):
                    composite_path = APP_FILE_ROOT + 'image/3_'+request.FILES['mask'].name
                    with open(composite_path, 'wb') as f:
                        for line in request.FILES['mask']:
                            f.write(line)
                else:
                    composite_path = ''
                info = False
                blend = False
                composite = False
                eval = False
                filter = False
                blend_alpha = float(request.POST.get('blend_alpha',0.5))
                eval_liangdu = int(request.POST.get('eval_liangdu',0))
                eval_fanse = request.POST.get('eval_fanse',False)
                if eval_fanse == 'false':
                    eval_fanse=False
                eval_heibai = request.POST.get('eval_heibai',False)
                if eval_heibai == 'false':
                    eval_heibai=False
                eval_erzhi = request.POST.get('eval_erzhi',False)
                if eval_erzhi == 'false':
                    eval_erzhi=False
                filter_blur = request.POST.get('filter_blur',False)
                if filter_blur == 'false':
                    filter_blur=False
                filter_contour = request.POST.get('filter_contour',False)
                if filter_contour == 'false':
                    filter_contour=False
                if image_path2:
                    blend=True
                if composite_path:
                    composite=True
                if eval_fanse or eval_erzhi or eval_heibai or eval_liangdu != 0:
                    eval=True
                if filter_contour or filter_blur:
                    filter=True
                converter = ImageProcess(image_path1)
                return_picture = converter.convert_image(image_path2,info,blend,composite,eval,filter,
                                                         blend_alpha,
                                                         composite_path,
                                                         eval_liangdu,eval_fanse,eval_heibai,eval_erzhi,
                                                         filter_blur,filter_contour)
                response = HttpResponse(base64.b64encode(return_picture))
                response['Content-Type'] = 'image/' + image_path1.split('.')[-1]
                os.remove(image_path1) if image_path1 else None
                os.remove(image_path2) if image_path2 else None
                os.remove(composite_path) if composite_path else None
                return response
            else:
                return JsonResponse({'status': '401'})
        elif op == 'capcha':
            return_picture = getCapcha()
            response = HttpResponse(base64.b64encode(return_picture))
            response['Content-Type'] = 'image/jpeg'
            return response
        elif op == 'qrcode':
            text = request.POST.get('text', None)
            if text:
                return_picture = getQrcode(text)
                response = HttpResponse(base64.b64encode(return_picture))
                response['Content-Type'] = 'image/jpeg'
                return response


def paint(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'计算机绘图',\
        'display':'paint',\
        }))

def tetris(request):
    return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
        'title':'俄罗斯方块',\
        'display':'tetris',\
        }))

def charvideo(request):
    if request.method == 'GET' and request.GET.get('av',None):
        av = request.GET['av']
        file = APP_FILE_ROOT+'av/'+av+'.mp4'
        #内部函数：分批流式读取大文件
        def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
            #chunk_size=8192:片段长度8M
            #offset=0起始位置
            #lenth=None:未到最终片段不设置，到最终片段设置为小于等于chunk_size的值
            with open(file,'rb') as f:
                f.seek(offset, os.SEEK_SET)#找到起始位置
                remaining = length#
                while True:
                    bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
                    data = f.read(bytes_length)
                    if not data:
                        break
                    if remaining:
                        remaining -= len(data)
                    yield data
        #将视频文件以流媒体的方式响应
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
        range_match = range_re.match(range_header)
        size = os.path.getsize(file)
        content_type = 'video/mp4'
        first_byte = None
        if range_match:
            first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = first_byte + 1024 * 1024 * 8    # 8M 每片,响应体最大体积
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        response = StreamingHttpResponse(file_iterator(file, offset=first_byte, length=length), status=206, content_type=content_type)
        response['Content-Length'] = str(length)
        response['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Disposition'] = 'filename='+str(random.randint(100,999))+'.mp4'
        return response
    else:
        return HttpResponse(render(request, APP_TEMPLETE_ROOT+'index.html',{\
            'title':'字符视频',\
            'display':'charvideo',\
            }))
