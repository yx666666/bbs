# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-05-07 06:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yonghu', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='plt_icon',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]