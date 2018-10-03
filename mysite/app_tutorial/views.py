# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
def index(request):
	return HttpResponse(render(request, 'common/index.html', {'title':'菲菲的技术网站'}))

def tutorial(request):
	return HttpResponseRedirect(reverse('index'))

def tutorial_doc(request,docname=None):
	return HttpResponse('sting is:'+ docname)