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

#上传文件之前动态生成路径
def get_postFilePath(instance, filename):
    return 'app_blog_post/'+str(instance.user.slug)+'/'+str(instance.slug)+'/'+str(filename)

# 文档表。注意：slug域直接映射到url，不能重名。解决方法其实很简单：column+slug组成联合主键
@python_2_unicode_compatible
class Post(models.Model):
    user = models.ForeignKey('auth.User',blank=False,null=False,editable=False,verbose_name='作者')

    slug = models.CharField('文章域',max_length=256, db_index=True)
    title = models.CharField('标题',max_length=256)
    keywords = models.CharField('关键词',max_length=256,null=True,blank=True)
    description = models.TextField('描述',null=True,blank=True)
    content = models.FileField('内容',\
        upload_to=get_postFilePath,null=True,blank=True, help_text='文章对应的实体文件')
    content_html = models.FileField('内容转码',\
        upload_to=get_postFilePath,null=True,blank=True, help_text='文章对应的html文件')

    publish_time = models.DateTimeField('发表时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间',auto_now=True, null=True)

    class Meta:
        unique_together=("user","slug")#如果不知道字段名可连接到数据库查看
        verbose_name = '文章'
        get_latest_by = 'update_time'
        ordering = ['-update_time'] #-表示反转排序顺序

    def __str__(self):
        return self.title

#对模型进行删除时，文件系统同步删除所有文件字段对应的文件，不然会越积越多（文件夹仍保留）
@receiver(pre_delete, sender=Post)
def file_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.content.delete(False)
