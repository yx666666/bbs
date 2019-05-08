# -*- coding: utf-8 -*-
from redis import Redis
from django.conf import settings

#写到__init__.py，有道云中有详细介绍。自查
#这里redis是一个单例，任何一个模块都可以使用它
rds = Redis(**settings.REDIS)
