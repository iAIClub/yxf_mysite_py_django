# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-14 19:39
from __future__ import unicode_literals

import app_tutorial.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_tutorial', '0004_auto_20181014_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='content',
            field=models.FileField(blank=True, help_text='\u6587\u6863\u5bf9\u5e94\u7684\u5b9e\u4f53\u6587\u4ef6', null=True, upload_to=app_tutorial.models.get_tutorialFilePath, verbose_name='\u5185\u5bb9'),
        ),
    ]