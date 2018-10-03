# -*- coding: utf-8 -*-
"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

# [导入APP视图代码]
from app_tutorial import views as app_tutorial_views
from app_user import views as app_user_views
from app_blog import views as app_blog_views
from app_webtrans import views as app_webtrans_views
from app_wechat import views as app_wechat_views
from app_visual import views as app_visual_views
from app_metaphysics import views as app_metaphysics_views
from app_spider import views as app_spider_views

urlpatterns = [
    # url预处理：1.自动截去了http://domain/；2.若同一位置出现重复斜杠如//、///，则自动变为单个/
    # 匹配无任何后缀的首页
    url(r'^$', app_tutorial_views.index, name="index"),
    url(r'^tutorial/$', include(tutorial_urlpatterns)),
    url(r'^blog/(?!post/).{0,}', app_blog_views.index, name="app-blog"),
    url(r'^blog/post/(?P<postname>.{0,}$', app_blog_views.index, name="app-blog-post"),

    url(r'^user/(?P<suburl>[^/]{0,})$', app_user_views.index, name="app-user"),

    url(r'^webtrans/(?!api/).{0,}', app_webtrans_views.index, name="app-webtrans"),
    url(r'^webtrans/api/(?P<args>.{0,}$', app_webtrans_views.index, name="app-webtrans-api"),

    url(r'^wechat/', app_wechat_views.index, name="app-wechat"),

    url(r'^visual/', app_visual_views.index, name="app-visual"),

    url(r'^metaphysics/', app_metaphysics_views.index, name="app-metaphysics"),

    url(r'^spider/(?!api/).{0,}', app_spider_views.index, name="app-spider"),
    url(r'^spider/api/(?P<args>).{0,}$', app_spider_views.index, name="app-spider-api"),

    url(r'^admin/', admin.site.urls, name="sys-admin"),
]

tutorial_urlpatterns = ([
    # 匹配任意属于tutorial/但不属于tutorial/doc/的路径
    url(r'^tutorial/(?!doc/).{0,}', app_tutorial_views.tutorial, name="app-tutorial"),
    # 匹配任意属于tutorial/doc/的路径，获取doc/后面的子串
    url(r'^tutorial/doc/(?P<docname>.{0,})$', app_tutorial_views.tutorial_doc, name="app-tutorial-doc"),
],"tutorial"
)
