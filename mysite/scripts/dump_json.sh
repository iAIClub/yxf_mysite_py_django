#!/bin/sh

#goto project root
cd /opt/yxf_mysite_py_django/mysite

#dump postgresql sql
python manage.py dumpdata > ./media/mysite.json
exit 0
