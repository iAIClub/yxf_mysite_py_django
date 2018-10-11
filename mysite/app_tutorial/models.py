# -*- coding: utf-8 -*-
from __future__ import unicode_literals #使用python3的数据定义语法，完美支持Unicode
from django.utils.encoding import python_2_unicode_compatible #向后兼容
from django.utils import timezone
from django.db import models
from django.core.files import File
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import sys
sys.path.append("..")
from mysite_conf.settings_cfg import DOMAIN

#上传文件之前动态生成路径
def get_tutorialFilePath(instance, filename):
    return 'app_tutorial_doc/'+str(instance.column.slug)+'/'+str(instance.slug)+'/'+str(filename)

# 栏目表。注意：slug域直接映射到url，不能重名
class Column(models.Model):
    slug = models.CharField('栏目域', max_length=256, db_index=True)#自然主键
    name = models.CharField('栏目名称', max_length=256)
    info = models.TextField('栏目简介', default='')

    class Meta:
        verbose_name = '栏目'
        ordering = ['name']

    def __unicode__(self):
        return self.name

# 文档表。注意：slug域直接映射到url，不能重名
class Tutorial(models.Model):
    column = models.ForeignKey(Column,null=True,blank=True,verbose_name='归属栏目')
    author = models.ForeignKey('auth.User',blank=True,null=True,editable=False,verbose_name='作者')

    slug = models.CharField('文档域',max_length=256, db_index=True)#自然主键
    title = models.CharField('标题',max_length=256)
    keywords = models.CharField('关键词',max_length=256, null=True,blank=True, default='',help_text='不写默认为标题')
    description = models.TextField('描述',null=True,blank=True, help_text='不写默认为内容前160字')
    content = models.FileField('内容',\
        upload_to=get_tutorialFilePath,null=True,blank=True, help_text='文档对应的实体文件')

    publish_time = models.DateTimeField('发表时间', auto_now_add=True, editable=True)
    update_time = models.DateTimeField('更新时间',auto_now=True, null=True)

    def get_title(self):
        return title

    def get_keywords(self):
        if self.keywords and self.keywords.strip():#移除头尾的空白字符
            return self.keywords
        return self.title

    def get_description(self):
        if self.description and self.description.strip():
            return self.description
        if len(self.content) >= 160:
            return self.content[:160]
        else:
            return self.content

    def get_absolute_url(self):
        return reverse('artical', args=(self.slug,))

    class Meta:
        verbose_name = '文档'
        get_latest_by = 'update_time'
        ordering = ['-update_time'] #-表示反转排序顺序

    def __unicode__(self):
        return self.title

#对模型进行删除时，文件系统同步删除，不然会越积越多（文件夹仍保留）
@receiver(pre_delete, sender=Tutorial)
def file_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.content.delete(False)
