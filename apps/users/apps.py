# _*_ coding: utf-8 _*_
from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = u"用户信息" #设置app显示为中文
