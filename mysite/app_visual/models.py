# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

APP_FILE_ROOT = 'app_visual_file/'
APP_TEMPLETE_ROOT = 'app_visual/'
if not os.path.isdir('media/'+APP_FILE_ROOT):
    os.mkdir('media/'+APP_FILE_ROOT.rstrip('/'))
if not os.path.isdir('media/'+APP_FILE_ROOT+'av/'):
    os.mkdir('media/'+APP_FILE_ROOT+'av')
if not os.path.isdir('media/'+APP_FILE_ROOT+'image/'):
    os.mkdir('media/'+APP_FILE_ROOT+'image')
