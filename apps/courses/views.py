# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic import View

# Create your views here.
from .models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q


class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by("-add_time")
        hot_courses = all_courses.order_by("-click_nums")[:3]  # 按照点击数，取出前三的课程机构排名

        #课程搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:#Q表示sql的或操作
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(detail__icontains=search_keywords)) #__icontains表示模糊匹配，像sql中的like查询，i表示不区分大小写

        #按照参与人数排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_courses = all_courses.order_by("-students")
            elif sort == "hot":
                all_courses = all_courses.order_by("-click_nums")

        #课程分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Provide Paginator with the request object for complete querystring generation

        p = Paginator(all_courses, 7,  request=request)

        courses = p.page(page)

        return render(request, 'course-list.html', {
            "all_courses" : courses,
            "hot_courses" : hot_courses
        })


class VideoPlayView(View):
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course #通过lesson外键获取课程信息返回
        course.students += 1
        course.save()
        # 查询用户是否关联了该课程
        user_courses = UserCourse.objects.filter(name=request.user, course=course)
        if not user_courses:  # 如果未关联则是将该用户和课程关联
            user_course = UserCourse(name=request.user, course=course)
            user_course.save()

        user_courses = UserCourse.objects.filter(course=course)  # 获取学过这门课的所有学生信息
        user_ids = [user_course.name.id for user_course in user_courses]  # 遍历获取所有学过这门课的学生的id
        all_user_courses = UserCourse.objects.filter(
            name_id__in=user_ids)  # django特有的name参数id在user_ids中的就返回，就是获取这个id数组所在的所有用户

        # 去除所有课程id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        # 获取学过该课程的其他用户学过的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-add_time")[:5]

        all_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-play.html", {
            "course": course,
            "all_resources": all_resources,
            "relate_courses": relate_courses,
            "video" : video
        })


class CourseDetailView(View):
    """
    课程详情页
    """
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        #增加课程点击数
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated():# 判断用户是否登陆
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):#数据库是否有数据
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):#数据库是否有数据
                has_fav_org = True

        #加入一个tag进行关联查找出相关的课程
        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:1]
        else:
            relate_courses = [] #如果查询为空的话，就返回一个空的数组
        return render(request, "course-detail.html", {
            "course" : course,
            "relate_courses" : relate_courses,
            "has_fav_course" : has_fav_course,
            "has_fav_org" : has_fav_org
        })


class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息
    """
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.students += 1
        course.save()

        #查询用户是否关联了该课程
        user_courses = UserCourse.objects.filter(name=request.user, course=course)
        if not user_courses:# 如果未关联则是将该用户和课程关联
            user_course = UserCourse(name=request.user, course=course)
            user_course.save()

        user_courses = UserCourse.objects.filter(course=course) #获取学过这门课的所有学生信息
        user_ids = [user_course.name.id for user_course in user_courses] #遍历获取所有学过这门课的学生的id
        all_user_courses = UserCourse.objects.filter(name_id__in=user_ids) #django特有的name参数id在user_ids中的就返回，就是获取这个id数组所在的所有用户

        #去除所有课程id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        #获取学过该课程的其他用户学过的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-add_time")[:5]

        all_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-video.html", {
            "course": course,
            "all_resources" : all_resources,
            "relate_courses" : relate_courses
        })


class CommentView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        user_courses = UserCourse.objects.filter(course=course)  # 获取学过这门课的所有学生信息
        user_ids = [user_course.name.id for user_course in user_courses]  # 遍历获取所有学过这门课的学生的id
        all_user_courses = UserCourse.objects.filter(
            name_id__in=user_ids)  # django特有的name参数id在user_ids中的就返回，就是获取这个id数组所在的所有用户

        # 去除所有课程id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        # 获取学过该课程的其他用户学过的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-add_time")[:5]

        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all()
        return render(request, "course-comment.html", {
            "course": course,
            "all_resources": all_resources,
            "all_comments" : all_comments,
            "relate_courses": relate_courses
        })


class AddCommentView(View):
    """
    用户评论
    """
    def post(self, request):
        if not request.user.is_authenticated(): #判断用户是否登录
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", "") #get只能取出一条数据，如果取出多条数据则会抛出异常,没有数据也会抛出异常
        if int(course_id) > 0 and comments:
            course_comments = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.name = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')