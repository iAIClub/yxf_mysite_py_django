# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

APP_FILE_ROOT = 'app_metaphysics_file/'
APP_TEMPLETE_ROOT = 'app_metaphysics/'
if not os.path.isdir('media/'+APP_FILE_ROOT):
    os.mkdir('media/'+APP_FILE_ROOT.rstrip('/'))
