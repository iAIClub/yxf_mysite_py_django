# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

APP_FILE_ROOT = 'media/app_metaphysics/'
APP_TEMPLETE_ROOT = 'app_metaphysics/'
if not os.path.isdir(APP_FILE_ROOT):
    os.mkdir(APP_FILE_ROOT.rstrip('/'))
