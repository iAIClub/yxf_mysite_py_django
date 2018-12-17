# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.contrib import admin
from app_tutorial import views as app_tutorial_views
from app_user import views as app_user_views
from app_blog import views as app_blog_views
from app_metaphysics import views as app_metaphysics_views
from app_spider import views as app_spider_views
from app_visual import views as app_visual_views
from app_webtrans import views as app_webtrans_views

tutorial_urlpatterns = [
    url(r'^doc/(?P<column_slug>[^/]+)/(?P<doc_slug>[^/]+)/image/(?P<image_name>[^/]+)$', app_tutorial_views.image,name='app_tutorial_image_url'),#文件路径
    url(r'^doc/(?P<column_slug>[^/]+)/(?P<doc_slug>[^/]+)/image$', app_tutorial_views.image,{'image_name':None},name='app_tutorial_image_upload'),#editmd的图片上传路径
    url(r'^doc/(?P<column_slug>[^/]+)/(?P<doc_slug>[^/]+)/(?P<doc_name>[^/]+)$', app_tutorial_views.filed,name='app_tutorial_file_url'),#文件路径
    url(r'^doc/(?P<column_slug>[^/]+)/(?P<doc_slug>[^/]+)$', app_tutorial_views.doc,name='app_tutorial_doc'),
    url(r'^doc/(?P<column_slug>[^/]+)$', app_tutorial_views.column,name='app_tutorial_column'),
    url(r'^editmd/$', app_tutorial_views.editmd,name='app_tutorial_editmd'),
    url(r'^$', app_tutorial_views.tutorial,name='app_tutorial'),
]

blog_urlpatterns = [
    url(r'^post/(?P<post_id>[^/]+)/image/(?P<image_name>[^/]+)$', app_blog_views.image,name='app_blog_image_url'),
    url(r'^post/(?P<post_id>[^/]+)/image$', app_blog_views.image,{'image_name':None},name='app_blog_image_upload'),
    url(r'^post/(?P<post_id>[^/]+)/(?P<post_name>[^/]+)$', app_blog_views.filed,name='app_blog_file_url'),
    url(r'^post/(?P<post_id>[^/]+)$', app_blog_views.post,name='app_blog_post'),
    url(r'^editmd/$', app_blog_views.editmd,name='app_blog_editmd'),
    url(r'^$', app_blog_views.blog,name='app_blog'),
]

user_urlpatterns = [
    url(r'^download/(?P<suburl>.+)$', app_user_views.download,name='app_user_download_url'),
    url(r'^login/$', app_user_views.login,name='app_user_login'),
    url(r'^register/$', app_user_views.register,name='app_user_register'),
    url(r'^profile/$', app_user_views.profile,name='app_user_profile'),
    url(r'^$', app_user_views.user,name='app_user'),
]

visual_urlpatterns = [
    url(r'^charvideo/$', app_visual_views.charvideo,name='app_visual_charvideo'),
    url(r'^dsvisual/$', app_visual_views.dsvisual,name='app_visual_dsvisual'),
    url(r'^picture/$', app_visual_views.picture,name='app_visual_picture'),
    url(r'^paint/$', app_visual_views.paint,name='app_visual_paint'),
    url(r'^tetris/$', app_visual_views.tetris,name='app_visual_tetris'),
    url(r'^$', app_visual_views.index,name='app_visual'),
]

webtrans_urlpatterns = [
    url(r'^websocket/$', app_webtrans_views.websocket,name='app_webtrans_websocket'),
    url(r'^tcptrans/$', app_webtrans_views.tcptrans,name='app_webtrans_tcptrans'),
    url(r'^nat/$', app_webtrans_views.nat,name='app_webtrans_nat'),
    url(r'^wechat/$', app_webtrans_views.wechat,name='app_webtrans_wechat'),
    url(r'^map/content$', app_webtrans_views.map_content,name='app_webtrans_map_content'),
    url(r'^map/$', app_webtrans_views.map,name='app_webtrans_map'),
    url(r'^proxy/$', app_webtrans_views.proxy,name='app_webtrans_proxy'),
    url(r'^$', app_webtrans_views.index,name='app_webtrans'),
]

spider_urlpatterns = [
    url(r'^$', app_spider_views.index,name='app_spider'),
]

metaphysics_urlpatterns = [
    url(r'^$', app_metaphysics_views.index,name='app_metaphysics'),
]

urlpatterns = [
    url(r'^$', app_tutorial_views.index,name='index'),#首页交给tutorial应用处理
    url(r'^settings/$', app_user_views.settings,name='settings'),#网站管理页交给user应用处理
    url(r'^admin/', admin.site.urls),#所有内容仅对超级管理员开放，不可对外
    url(r'^tutorial/', include(tutorial_urlpatterns)),#最重要的应用，构造网站主体
    url(r'^user/', include(user_urlpatterns)),#对外开放的用户管理体系，其中settings页面只对管理员开放
    url(r'^blog/', include(blog_urlpatterns)),#模仿tutorial应用的副本应用
    url(r'^spider/', include(spider_urlpatterns)),
    url(r'^visual/', include(visual_urlpatterns)),
    url(r'^webtrans/', include(webtrans_urlpatterns)),
    url(r'^metaphysics/', include(metaphysics_urlpatterns)),
]
