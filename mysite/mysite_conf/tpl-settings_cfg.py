# -*- coding: utf-8 -*-

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '[yourdb]',
        'USER': '[yourdbuser]',
        'PASSWORD': '[yourpassword]',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

DOMAIN = {
	'adress': '[yourdomain]',
}

SUPERUSER = {
    'name': '[yoursuperuser]',
}