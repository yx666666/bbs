# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=64)
    #auto_now,每保存一次修改一次，auto_now_add，仅创建时修改
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
