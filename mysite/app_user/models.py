# -*- coding: utf-8 -*-
from __future__ import unicode_literals  #让py2使用py3的数据定义语法
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.db import models
from django.core.files import File
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import os

APP_FILE_ROOT = 'media/app_user/'
APP_TUTORIAL_ROOT = 'media/app_tutorial/'
APP_TEMPLETE_ROOT = 'app_user/'
if not os.path.isdir(APP_FILE_ROOT):
    os.mkdir(APP_FILE_ROOT.rstrip('/'))


# 上传之前动态生成路径 两个固定参数：instance调取当前对象，filename获取上传文件名
def get_filePathAndName(instance, filename):
    return 'media/app_user'+str(instance.user.username)+'/'+str(instance.userpath)+'/'+str(filename)


# 用户上传文件表。文件域由三部分组成，映射到唯一url：UPLOAD_ROOT/username/userpath/filename
@python_2_unicode_compatible
class PanFile(models.Model):
    user = models.ForeignKey('auth.User',editable=False,blank=False,null=False,verbose_name='所属用户')
    userpath = models.CharField('用户自定义路径',max_length=256,)
    filename = models.CharField('文件名称',max_length=256,)
    file = models.FileField('文件实体',upload_to=get_filePathAndName)
    upload_time = models.DateTimeField('上传时间', auto_now_add=True, editable=True)

    class Meta:
        unique_together=("user","userpath","filename")
        verbose_name = '文件'
        get_latest_by = 'upload_time'
        ordering = ['-upload_time']

    def __str__(self):
        return self.filename


# 对模型进行删除时，文件系统同步删除，不然会越积越多（文件夹仍保留）
@receiver(pre_delete, sender=PanFile)
def file_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
