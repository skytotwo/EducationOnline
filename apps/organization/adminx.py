# -*- coding:utf-8 -*-
__author__ = 'jolly'
__date__ = '2017/11/25 上午12:22'

import xadmin

from .models import CityDict, CourseOrg, Teacher


class CityDictAdmin(object):
    list_display = ['name', 'desc', 'add_time']  # 默认显示
    search_fields = ['name', 'desc']  # 查询
    list_filter = ['name', 'desc', 'add_time']  # 过滤筛选


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'fav_nums', 'image', 'address', 'city', 'add_time']  # 默认显示
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums', 'image', 'address', 'city']  # 查询
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums', 'image', 'address', 'city__name', 'add_time']  # 过滤筛选
    #relfield_style = 'fk-ajax' #指的是作为外键加载在其他model上的时候，是以ajax的形式展现，就是下拉筛选改为搜索


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company', 'work_position', 'points', 'click_nums', 'fav_nums', 'add_time']  # 默认显示
    search_fields = ['org', 'name', 'work_years', 'work_company', 'work_position', 'points', 'click_nums', 'fav_nums']  # 查询
    list_filter = ['org__name', 'name', 'work_years', 'work_company', 'work_position', 'points', 'click_nums', 'fav_nums', 'add_time']  # 过滤筛选


xadmin.site.register(CityDict, CityDictAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(Teacher, TeacherAdmin)
