# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from app_tutorial.models import Column,Tutorial

# Register your models here.
@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'slug', 'info',)
    search_fields = ('name', 'slug',)

@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'slug', 'title', 'column','content','content_html','publish_time', 'update_time')
    search_fields = ('title', 'slug', 'content',)
    list_filter = ('column',)