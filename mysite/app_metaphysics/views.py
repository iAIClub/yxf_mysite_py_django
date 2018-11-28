# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from app_metaphysics.models import APP_TEMPLETE_ROOT
from mysite.settings import HOST


def index(request):
    opt = request.GET.get('op', None)
    if opt is None:
        return HttpResponseRedirect(reverse('app_metaphysics')+'?op=wannianli')
    else:
        return HttpResponse(render(request, 'app_metaphysics/index.html', {\
            'title':'数术',\
            'op':opt,\
            'host':HOST,\
            }))
