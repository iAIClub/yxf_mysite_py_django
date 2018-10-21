# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from app_user.models import PanFile

# Register your models here.
@admin.register(PanFile)
class PanFileAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'user', 'userpath', 'filename','file','upload_time',)
    search_fields = ('user', 'userpath', 'filename',)
    list_filter = ('user',)
