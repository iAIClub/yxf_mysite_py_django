# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import PanFile

# Register your models here.
@admin.register(PanFile)
class PanFileAdmin(admin.ModelAdmin):
    list_per_page = 20
    raw_id_fields = ('username', )
    list_display = ('id', 'username', 'userpath', 'filename','upload_time',)
    search_fields = ('username', 'userpath', 'filename',)
    list_filter = ('username',)
