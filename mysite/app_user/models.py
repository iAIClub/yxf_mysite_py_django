# -*- coding: utf-8 -*-
from __future__ import unicode_literals #使用python3的数据定义语法，完美支持Unicode
from django.utils.encoding import python_2_unicode_compatible #向后兼容
from django.utils import timezone
from django.db import models
from django.core.files import File
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import os
import sys
sys.path.append("..")
from mysite_conf.settings_cfg import DOMAIN


# Create your models here.
#上传之前动态生成路径 两个固定参数：instance调取当前对象，filename获取上传文件名
def get_filePathAndName(instance, filename):
    return 'app_user_pan/'+str(instance.username)+'/'+str(instance.userpath)+'/'+str(filename)

# 用户上传文件表
class PanFile(models.Model):
    username = models.ForeignKey('auth.User',blank=True,null=True,editable=False,verbose_name='所属用户')
    userpath = models.CharField('用户自定义路径',max_length=256, default='')
    filename = models.CharField('文件名称',max_length=256, default='')
    #路径需要把Unicode字符转化为纯字符串
    file = models.FileField('文件实体',\
        upload_to=get_filePathAndName,\
        null=True,blank=True)

    upload_time = models.DateTimeField('上传时间', auto_now_add=True, editable=True)

    def get_absolute_url(self):
        return reverse('app_user_profile', args=(self.username,self.userpath,self.filename))

    class Meta:
        verbose_name = '文件服务'
        get_latest_by = 'upload_time'
        ordering = ['-upload_time']

    def __unicode__(self):
        return self.filename

#对模型进行删除时，文件系统同步删除，不然会越积越多（文件夹仍保留）
@receiver(pre_delete, sender=PanFile)
def file_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
