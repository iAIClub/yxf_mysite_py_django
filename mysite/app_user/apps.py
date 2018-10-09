# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class AppUserConfig(AppConfig):
    name = get_current_app_name(__file__)
    verbose_name = '自主用户系统'
