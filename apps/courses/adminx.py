# -*- coding:utf-8 -*-
__author__ = 'jolly'
__date__ = '2017/11/25 上午12:02'

import xadmin

from .models import Course, Lesson, Video, CourseResource, BannerCourse


#一般外键关联数据在xadmin只能通过在列表选择对应外键数据跳转再去编辑，但是想在详情编辑中，可以直接编辑（只能一层嵌套）
class LessonInline(object):
    model = Lesson
    extra = 0


class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums', 'get_zj_nums', 'go_to', 'add_time']#默认显示
    search_fields = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums']#查询
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums', 'add_time']#过滤筛选
    ordering = ['-click_nums'] #此处为自定义排序，也可以直接在xadmin上点击进行排序
    readonly_fields = ['click_nums'] #设置xadmin后台字段为只读，不能修改
    exclude = ['fav_nums'] # 指定某个字段不可见
    list_editable = ['degree', 'desc'] #表示可以直接在列表页编辑
    # 一般外键关联数据在xadmin只能通过在列表选择对应外键数据跳转再去编辑，但是想在详情编辑中，可以直接编辑（只能一层嵌套）
    inlines = [LessonInline] #是一个数组，可以放多个，但只能一对多，不能一个接一个嵌套，只能嵌套一层
    refresh_times = [3, 5] #页面定时刷新，3-5可选范围
    #给course中的详情加入ueditor插件样式
    style_fields = {'detail': 'ueditor'}
    import_excel = True

    def queryset(self):
        qs = super(CourseAdmin, self).queryset() #获取到父类的数据
        qs = qs.filter(is_banner=False) #过滤出is_banner为false的数据
        return qs #返回过滤完的数据


    def save_models(self):
        #在保存课程的时候统计课程机构的课程数，这里是重载了保存方法
        obj = self.new_obj #获取一个新的课程
        obj.save() #先保存这个课程
        if obj.course_org is not None:
            course_org = obj.course_org #获取课程所在的课程机构
            course_org.course_nums = Course.objects.filter(course_org=course_org).count() #计算属于这个机构的课程数量
            course_org.save() #保存课程


    #用于在课程页面导入excel页面后，对导入的excel做后台逻辑
    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            pass
        return super(CourseAdmin, self).post(request, args, kwargs) #最后一定要调用父类CourseAdmin的post方法返回


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums', 'add_time']#默认显示
    search_fields = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums']#查询
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums', 'add_time']#过滤筛选
    ordering = ['-click_nums'] #此处为自定义排序，也可以直接在xadmin上点击进行排序
    readonly_fields = ['click_nums'] #设置xadmin后台字段为只读，不能修改
    exclude = ['fav_nums'] # 指定某个字段不可见
    # 一般外键关联数据在xadmin只能通过在列表选择对应外键数据跳转再去编辑，但是想在详情编辑中，可以直接编辑（只能一层嵌套）
    inlines = [LessonInline] #是一个数组，可以放多个，但只能一对多，不能一个接一个嵌套，只能嵌套一层

    def queryset(self):
        qs = super(BannerCourseAdmin, self).queryset() #获取到父类的数据
        qs = qs.filter(is_banner=True) #过滤出is_banner为true的数据
        return qs #返回过滤完的数据


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']  # 默认显示
    search_fields = ['course', 'name']  # 查询
    list_filter = ['course__name', 'name', 'add_time']  # 过滤筛选


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']#默认显示
    search_fields = ['lesson', 'name']#查询
    list_filter = ['lesson__name', 'name', 'add_time']#过滤筛选


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']  # 默认显示
    search_fields = ['course', 'name', 'download']  # 查询
    list_filter = ['course__name', 'name', 'download', 'add_time']  # 过滤筛选


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)