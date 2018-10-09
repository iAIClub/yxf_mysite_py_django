# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class AppTutorialConfig(AppConfig):
    name = get_current_app_name(__file__)
    verbose_name = '文档内容系统'
