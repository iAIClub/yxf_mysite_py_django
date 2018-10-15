# -*- coding: utf-8 -*-
from __future__ import unicode_literals  #让py2使用py3的数据定义语法
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.db import models
from django.db.models.signals import pre_delete,pre_save
from django.dispatch.dispatcher import receiver
from django.core.files.storage import FileSystemStorage
import os
import sys
sys.path.append("..")
from mysite_conf.settings_cfg import DOMAIN

#上传文件之前动态生成路径
def get_tutorialFilePath(instance, filename):
    return 'app_tutorial_doc/'+str(instance.column.slug)+'/'+str(instance.slug)+'/'+str(filename)

# 栏目表。注意：slug域直接映射到url，不能重名。解决方法其实很简单：slug设置唯一约束
@python_2_unicode_compatible
class Column(models.Model):
    slug = models.CharField('栏目域', max_length=256, db_index=True,unique=True)
    name = models.CharField('栏目名称', max_length=256)
    info = models.TextField('栏目简介', default='')

    class Meta:
        verbose_name = '栏目'
        ordering = ['name']

    def __str__(self):
        return self.name

# 文档表。注意：slug域直接映射到url，不能重名。解决方法其实很简单：column+slug组成联合主键
@python_2_unicode_compatible
class Tutorial(models.Model):
    column = models.ForeignKey(Column,null=False,blank=True,verbose_name='归属栏目')
    author = models.ForeignKey('auth.User',blank=True,null=True,editable=False,verbose_name='作者')

    slug = models.CharField('文档域',max_length=256, db_index=True)
    title = models.CharField('标题',max_length=256)
    keywords = models.CharField('关键词',max_length=256,null=True,blank=True)
    description = models.TextField('描述',null=True,blank=True)
    content = models.FileField('内容',\
        upload_to=get_tutorialFilePath,null=True,blank=True, help_text='文档对应的实体文件')
    content_html = models.FileField('内容转码',\
        upload_to=get_tutorialFilePath,null=True,blank=True, help_text='文档对应的html文件')

    publish_time = models.DateTimeField('发表时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间',auto_now=True, null=True)

    class Meta:
        unique_together=("column","slug")#如果不知道字段名可连接到数据库查看
        verbose_name = '文档'
        get_latest_by = 'update_time'
        ordering = ['-update_time'] #-表示反转排序顺序

    def __str__(self):
        return self.title

#对模型进行删除时，文件系统同步删除所有文件字段对应的文件，不然会越积越多（文件夹仍保留）
@receiver(pre_delete, sender=Tutorial)
def file_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.content.delete(False)
