# -*- coding:utf-8 -*-
__author__ = 'jolly'
__date__ = '2017/11/25 上午12:39'

import xadmin

from .models import UserAsk, UserCourse, UserMessage, CourseComments, UserFavorite


class UserAskAdmin(object):
    list_display = ['name', 'mobile', 'course_name', 'add_time']  # 默认显示
    search_fields = ['name', 'mobile', 'course_name']  # 查询
    list_filter = ['name', 'mobile', 'course_name', 'add_time']  # 过滤筛选


class UserCourseAdmin(object):
    list_display = ['name', 'course', 'add_time']  # 默认显示
    search_fields = ['name', 'course']  # 查询
    list_filter = ['name', 'course__name', 'add_time']  # 过滤筛选


class UserMessageAdmin(object):
    list_display = ['user', 'message', 'add_time', 'has_read']  # 默认显示
    search_fields = ['user', 'message', 'has_read']  # 查询
    list_filter = ['user', 'message', 'add_time', 'has_read']  # 过滤筛选


class CourseCommentsAdmin(object):
    list_display = ['name', 'course', 'comments', 'add_time']  # 默认显示
    search_fields = ['name', 'course', 'comments']  # 查询
    list_filter = ['name', 'course__name', 'comments', 'add_time']  # 过滤筛选


class UserFavoriteAdmin(object):
    list_display = ['name', 'fav_id', 'fav_type', 'add_time']  # 默认显示
    search_fields = ['name', 'fav_id', 'fav_type']  # 查询
    list_filter = ['name', 'fav_id', 'fav_type', 'add_time']  # 过滤筛选


xadmin.site.register(UserAsk, UserAskAdmin)
xadmin.site.register(UserCourse, UserCourseAdmin)
xadmin.site.register(UserMessage, UserMessageAdmin)
xadmin.site.register(CourseComments, CourseCommentsAdmin)
xadmin.site.register(UserFavorite, UserFavoriteAdmin)