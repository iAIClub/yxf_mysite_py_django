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
from django.conf.urls import url
from django.contrib import admin

# [1.import your app]
from app_index import views as app_index_views
from app_tutorial import views as app_tutorial_views
from app_user import views as app_user_views
from app_blog import views as app_blog_views
from app_webtrans import views as app_webtrans_views
from app_wechat import views as app_wechat_views
from app_visual import views as app_visual_views
from app_metaphysics import views as app_metaphysics_views
from app_spider import views as app_spider_views

urlpatterns = [
    # [2.add your url route]
    url(r'^$', app_index_views.index, name='app_index'),
    url(r'^tutorial/', app_tutorial_views.index, name='app_tutorial'),
    url(r'^user/', app_user_views.index, name='app_user'),
    url(r'^blog/', app_blog_views.index, name='app_blog'),
    url(r'^webtrans/', app_webtrans_views.index, name='app_webtrans'),
    url(r'^wechat/', app_wechat_views.index, name='app_wechat'),
    url(r'^visual/', app_visual_views.index, name='app_visual'),
    url(r'^metaphysics/', app_metaphysics_views.index, name='app_metaphysics'),
    url(r'^spider/', app_spider_views.index, name='app_spider'),
    url(r'^admin/', admin.site.urls),
]
