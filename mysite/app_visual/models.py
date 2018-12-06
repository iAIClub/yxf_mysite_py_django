# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

APP_FILE_ROOT = 'media/app_visual/'
APP_TEMPLETE_ROOT = 'app_visual/'
if not os.path.isdir(APP_FILE_ROOT):
    os.mkdir(APP_FILE_ROOT.rstrip('/'))
if not os.path.isdir(APP_FILE_ROOT+'av/'):
    os.mkdir(APP_FILE_ROOT+'av')
if not os.path.isdir(APP_FILE_ROOT+'image/'):
    os.mkdir(APP_FILE_ROOT+'image')
