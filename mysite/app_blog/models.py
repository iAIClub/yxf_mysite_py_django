# -*- coding: utf-8 -*-
from __future__ import unicode_literals  #让py2使用py3的数据定义语法
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.db import models
from django.db.models.signals import pre_delete,pre_save
from django.dispatch.dispatcher import receiver
import os

APP_FILE_ROOT = 'media/app_blog/'
APP_TEMPLETE_ROOT = 'app_blog/'
if not os.path.isdir(APP_FILE_ROOT):
    os.mkdir(APP_FILE_ROOT.rstrip('/'))


# 上传文件之前动态生成路径
def get_postFilePath(instance, filename):
    return 'app_blog/'+str(instance.id)+'/'+str(filename)


# 分类表
@python_2_unicode_compatible
class PostClass(models.Model):
    name = models.CharField('分类名称', max_length=256)
    info = models.TextField('分类简介', default='')

    class Meta:
        verbose_name = '分类'
        ordering = ['name']

    def __str__(self):
        return self.name


# 文章表
@python_2_unicode_compatible
class Post(models.Model):
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,blank=False,null=False,editable=False,verbose_name='所属用户')
    post_class = models.ForeignKey(PostClass,on_delete=models.CASCADE,null=True,blank=True,verbose_name='所属分类')

    title = models.CharField('标题',max_length=256)
    keywords = models.CharField('关键词',max_length=256,null=True,blank=True)
    description = models.TextField('描述',null=True,blank=True)
    content = models.FileField('内容',upload_to=get_postFilePath,null=True,blank=True, help_text='文章对应的实体文件')
    content_html = models.FileField('内容转码',upload_to=get_postFilePath,null=True,blank=True, help_text='文章对应的html文件')

    publish_time = models.DateTimeField('发表时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间',auto_now=True, null=True)

    class Meta:
        verbose_name = '文章'
        get_latest_by = 'update_time'
        ordering = ['-update_time'] #-表示反转排序顺序

    def __str__(self):
        return self.title


# 对模型进行删除时，文件系统同步删除所有文件字段对应的文件，不然会越积越多（文件夹仍保留）
@receiver(pre_delete, sender=Post)
def file_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.content.delete(False)
