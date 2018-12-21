# -*- coding: utf-8 -*-
import os
import sys
import ConfigParser
# ---------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'ugre0j(jzu16=93yklv#9-0)96q)gsp*ugygc@(b&u!vv96#gg'
ALLOWED_HOSTS = ['*']

#LANGUAGE_CODE = 'en-us'
#TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True # use internationalization
USE_L10N = False # don't use localization
USE_TZ = False # don't use system timezone

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# ---------------------------------------
# [解析外部纯文本配置文件，放置敏感信息和多变的信息]
cf = ConfigParser.ConfigParser()
cf.read("settings.cfg")

DEBUG = cf.getboolean("meta", "debug")
REMOTE = cf.getboolean("meta", "remote")
HOST = cf.get("meta","host")
BAIDUMAP = {
    'url':cf.get('baidumap','url'),
    'ak':cf.get('baidumap','ak'),
}
WECHAT = {
    'token':cf.get('wechat','token'),
}
DATABASES = {
    'default': {
        'ENGINE': cf.get("db", "engine"),
        'NAME': cf.get("db", "name"),
        'USER': cf.get("db", "user"),
        'PASSWORD': cf.get("db", "password"),
        'HOST': cf.get("db", "host"),
        'PORT': cf.get("db", "port"),
    }
}
if cf.getboolean("meta","logger") is True:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': os.path.join(os.path.join(BASE_DIR, 'log'),'django.log'),
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'ERROR',
                'propagate': True,
            },
        },
    }
else:
    pass
# ---------------------------------------------
ROOT_URLCONF = 'mysite.urls'
WSGI_APPLICATION = 'mysite.wsgi.application'
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'app_tutorial',
    'app_user',
    'app_blog',
    'app_webtrans',
    'app_visual',
    'app_metaphysics',
    'app_spider',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',#安全
    'django.contrib.sessions.middleware.SessionMiddleware',#会话
    'django.middleware.common.CommonMiddleware',#阻挡非法UA；url补全
    'django.middleware.csrf.CsrfViewMiddleware',#CSRF防火墙
    'django.contrib.auth.middleware.AuthenticationMiddleware',#用户认证
    'django.contrib.messages.middleware.MessageMiddleware',#表单处理信息反馈
    'django.middleware.clickjacking.XFrameOptionsMiddleware',#clickjacking防火墙
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # [使用唯一的统一路径]
        'DIRS': [os.path.join(BASE_DIR, 'templetes')],
        #'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# ---------------------------------------------
