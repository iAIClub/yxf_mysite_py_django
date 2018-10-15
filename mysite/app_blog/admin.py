# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Post

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_per_page = 20
    raw_id_fields = ('user', )
    list_display = ('id', 'slug', 'title','user','content','content_html','publish_time', 'update_time', )
    search_fields = ('title', 'slug', 'content',)
    list_filter = ('user',)
