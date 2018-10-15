# -*- coding: utf-8 -*-
from __future__ import unicode_literals  #让py2使用py3的数据定义语法
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.db import models
from django.core.files import File
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import os
import sys
sys.path.append("..")

# contrib.auth自动维护用户表

#上传之前动态生成路径 两个固定参数：instance调取当前对象，filename获取上传文件名
def get_filePathAndName(instance, filename):
    return 'app_user_pan/'+str(instance.username)+'/'+str(instance.userpath)+'/'+str(filename)

# 用户上传文件表。文件域由三部分组成，映射到唯一url：[sysmediaroot]/username/userpath/filename
@python_2_unicode_compatible
class PanFile(models.Model):
    username = models.ForeignKey('auth.User',editable=False,blank=True,null=True,verbose_name='所属用户')
    userpath = models.CharField('用户自定义路径',max_length=256,)
    filename = models.CharField('文件名称',max_length=256,)
    #路径需要把Unicode字符转化为纯字符串
    file = models.FileField('文件实体',\
        upload_to=get_filePathAndName,)

    upload_time = models.DateTimeField('上传时间', auto_now_add=True, editable=True)

    class Meta:
        verbose_name = '文件'
        get_latest_by = 'upload_time'
        ordering = ['-upload_time']

    def __str__(self):
        return self.filename

#对模型进行删除时，文件系统同步删除，不然会越积越多（文件夹仍保留）
@receiver(pre_delete, sender=PanFile)
def file_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
