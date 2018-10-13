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
import importlib
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from app_tutorial import views as app_tutorial_views
from app_user import views as app_user_views
from app_blog import views as app_blog_views
from app_metaphysics import views as app_metaphysics_views
from app_spider import views as app_spider_views
from app_visual import views as app_visual_views
from app_webtrans import views as app_webtrans_views

# [反射（根据参数名自动加载应用）]
# def reflection(request, **kwargs):
#     appname = 'app_'+kwargs.get('appname', None)
#     try:
#         appViewObj = importlib.import_module(appname+'.views')
#         return appViewObj.index(request, **kwargs)
#     except:
#         kwargs['appname'] = 'invalid'
#         return app_tutorial_views.index(request, **kwargs)

user_urlpatterns = [
    url(r'^download/(?P<suburl>.+)', app_user_views.download,name='app_user_download_url'),
    url(r'^download/$', app_user_views.download,{'suburl':None},name='app_user_download'),
    url(r'^login/$', app_user_views.login,name='app_user_login'),
    url(r'^register/$', app_user_views.register,name='app_user_register'),
    url(r'^profile/$', app_user_views.profile,name='app_user_profile'),
    url(r'^settings/$', app_user_views.settings,name='app_user_settings'),
    url(r'^ajax/$', app_user_views.ajax,name='app_user_ajax'),
]

tutorial_urlpatterns = [
    url(r'^editmd/(?P<column_slug>[^/]+)/(?P<doc_slug>[^/]+)/(?P<doc_name>[^/]+)', app_tutorial_views.editmd,name='app_tutorial_editmd_doc'),
    url(r'^editmd/$', app_tutorial_views.editmd,{'column_slug':None,'doc_slug':None,'doc_name':None},name='app_tutorial_editmd'),
    url(r'^doc/(?P<column_slug>[^/]+)/(?P<doc_slug>[^/]+)$', app_tutorial_views.doc,name='app_tutorial_doc'),
    url(r'^doc/(?P<column_slug>[^/]+)$', app_tutorial_views.column,name='app_tutorial_column'),
    url(r'^$', app_tutorial_views.tutorial,name='app_tutorial_index'),
]

blog_urlpatterns = [
    url(r'^editmd/$', app_blog_views.editmd,name='app_blog_editmd'),
    url(r'^post/(?P<user>[^/]+)/(?P<post>[^/]+)$', app_blog_views.post,name='app_blog_post'),
    url(r'^post/(?P<user>[^/]+)$', app_blog_views.user,name='app_blog_user'),
    url(r'^$', app_blog_views.index,name='app_blog_index'),
]

spider_urlpatterns = [
    url(r'^$', app_spider_views.index,name='app_spider_index'),
]

visual_urlpatterns = [
    url(r'^map/$', app_visual_views.map,name='app_visual_map'),
    url(r'^game/$', app_visual_views.game,name='app_visual_game'),
    url(r'^$', app_visual_views.index,name='app_visual_index'),
]

webtrans_urlpatterns = [
    url(r'^$', app_webtrans_views.index,name='app_webtrans_index'),
]

metaphysics_urlpatterns = [
    url(r'^$', app_metaphysics_views.index,name='app_metaphysics_index'),
]

urlpatterns = [
    url(r'^$', app_tutorial_views.index,name='index'),#首页交给tutorial应用处理
    url(r'^search/$', app_user_views.search,name='search'),#站内搜索页交给user应用处理
    url(r'^admin/', admin.site.urls),#所有内容仅对超级管理员开放，不可对外
    url(r'^user/', include(user_urlpatterns)),#对外开放的用户管理体系
    url(r'^tutorial/', include(tutorial_urlpatterns)),
    url(r'^blog/', include(blog_urlpatterns)),
    url(r'^spider/', include(spider_urlpatterns)),
    url(r'^visual/', include(visual_urlpatterns)),
    url(r'^webtrans/', include(webtrans_urlpatterns)),
    url(r'^metaphysics/', include(metaphysics_urlpatterns)),
]
