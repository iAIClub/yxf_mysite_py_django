# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from app_blog.models import PostClass,Post

# Register your models here.
@admin.register(PostClass)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'info',)
    search_fields = ('name', )

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'title','user','post_class','content','content_html','publish_time', 'update_time', )
    search_fields = ('title', 'post_class', 'content',)
    list_filter = ('user', 'post_class',)
