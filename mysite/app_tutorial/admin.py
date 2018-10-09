# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Column,Tutorial

# Register your models here.
@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'slug', 'info',)
    search_fields = ('name', 'slug',)

@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_per_page = 20
    raw_id_fields = ('column', )
    list_display = ('id', 'title', 'slug', 'column','author','publish_time', 'update_time', )
    search_fields = ('title', 'slug', 'content',)
    list_filter = ('column', 'author',)

    #对父类方法的重写，在管理界面点击保存时的动作
    def save_model(self, request, obj, form, change):
        #your code
        super(TutorialAdmin, self).save_model(request, obj, form, change)

    #对父类方法的重写，在管理界面点击删除时的动作
    def delete_model(request, obj):
        #your code
        super(TutorialAdmin, self).delete_model(request, obj)
