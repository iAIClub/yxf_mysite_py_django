# -*- coding: utf-8 -*-
from __future__ import unicode_literals #使用python3的数据定义语法，完美支持Unicode
from django.utils.encoding import python_2_unicode_compatible #向后兼容
from django.utils import timezone
from django.db import models
import sys
sys.path.append("..")
from mysite_conf.settings_cfg import DOMAIN

#Create your models here.
# 栏目表
class Column(models.Model):
    slug = models.CharField('栏目域', max_length=256, db_index=True,default='', )#自然主键
    name = models.CharField('栏目名称', max_length=256)
    info = models.TextField('栏目简介', default='', help_text='栏目简介，栏目自定义导航等用途')

    class Meta:
        verbose_name = '栏目'
        ordering = ['name']

    def __unicode__(self):
        return self.name

# 文档表
class Tutorial(models.Model):
    column = models.ForeignKey(Column,null=True,blank=True,verbose_name='归属栏目')
    author = models.ForeignKey('auth.User',blank=True,null=True,editable=False,verbose_name='作者')

    slug = models.CharField('文档域',max_length=256, db_index=True,default='', )#自然主键
    title = models.CharField('标题',max_length=256)
    keywords = models.CharField('关键词',max_length=256, null=True,blank=True, default='',help_text='不写默认为标题')
    description = models.TextField('描述',null=True,blank=True, help_text='不写默认为内容前160字')
    #content:文档正文，最好能够直接上传并通过editmd编辑
    # content = UEditorField('内容',height=300,width=1000,
    #     default='',imagePath="uploads/images/",
    #     toolbars='besttome',filePath='uploads/files/',blank=True)
    content = models.TextField('内容',null=True,blank=True, help_text='文档正文内容',default='正在编写中……')

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

    class Meta:
        verbose_name = '文档'
        get_latest_by = 'update_time'
        ordering = ['-update_time'] #-表示反转排序顺序

    def __unicode__(self):
        return self.title
