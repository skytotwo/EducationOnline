# _*_ coding: utf-8 _*_
from django.shortcuts import render
from django.views.generic import View
# Create your views here.

from .models import CourseOrg, CityDict, Teacher
from .forms import UserAskForm
from courses.models import Course
from operation.models import UserFavorite
from courses.models import Course

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q


class OrgView(View):
    """
    课程机构列表功能
    """
    def get(self, request):
        all_orgs = CourseOrg.objects.all() #取出所有数据(机构)
        hot_orgs = all_orgs.order_by("-click_nums")[:3] #按照点击数，取出前三的课程机构排名
        all_citys = CityDict.objects.all() #取出所有城市

        # 机构搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:  # Q表示sql的或操作
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))  # __icontains表示模糊匹配，像sql中的like查询，i表示不区分大小写

        # 取出筛选城市——前端页面点击城市
        city_id = request.GET.get('city', "")
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        #对课程机构类型进行取出
        category = request.GET.get('ct', "")
        if category:
            all_orgs = all_orgs.filter(category=category)

        #根据学习人数和课程数排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        org_nums = all_orgs.count()  # 取出机构数量
        #对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Provide Paginator with the request object for complete querystring generation

        p = Paginator(all_orgs, 5,  request=request)

        orgs = p.page(page)

        return render(request, "org-list.html", {
            "all_orgs":orgs,
            "all_citys":all_citys,
            "org_nums": org_nums,
            "city_id":city_id,
            "category":category,
            "hot_orgs":hot_orgs,
            "sort":sort
        })


class AddUserAskView(View):
    """
    用户添加咨询
    """
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)  #这里调用modelform，和原来调用form验证的区别是可以直接利用model保存
            return HttpResponse('{"status":"success"}', content_type='application/json') # 不是跳转，而是类似ajax的原页面异步刷新
        else:
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


class OrgHomeView(View):
    """
    机构首页
    """
    def get(self, request, org_id):
        current_page = "home"
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        has_fav = False #用于返回机构页面的收藏标识，因为页面初始化加载的时候需要判断是否已经收藏
        if request.user.is_authenticated():# 判断用户是否登陆
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):#数据库是否有数据
                has_fav = True
        all_courses = course_org.course_set.all()[:3] #利用机构外键 ，通过model_set方法来反向获取所有机构内的课程
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html', {
            'all_courses' : all_courses,
            'all_teachers' : all_teachers,
            'course_org' : course_org,
            'current_page' :current_page,
            'has_fav' : has_fav
        })


class OrgCourseView(View):
    """
    机构课程列表页
    """
    def get(self, request, org_id):
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False  # 用于返回机构页面的收藏标识，因为页面初始化加载的时候需要判断是否已经收藏
        if request.user.is_authenticated():  # 判断用户是否登陆
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):  # 数据库是否有数据
                has_fav = True
        all_courses = course_org.course_set.all() #利用机构外键 ，通过model_set方法来反向获取所有机构内的课程
        return render(request, 'org-detail-course.html', {
            'all_courses' : all_courses,
            'course_org' : course_org,
            'current_page' :current_page,
            'has_fav': has_fav
        })


class OrgDescView(View):
    """
    机构介绍
    """
    def get(self, request, org_id):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False  # 用于返回机构页面的收藏标识，因为页面初始化加载的时候需要判断是否已经收藏
        if request.user.is_authenticated():  # 判断用户是否登陆
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):  # 数据库是否有数据
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            'course_org' : course_org,
            'current_page' :current_page,
            'has_fav': has_fav
        })


class OrgTeacherView(View):
    """
    机构教师页
    """
    def get(self, request, org_id):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False  # 用于返回机构页面的收藏标识，因为页面初始化加载的时候需要判断是否已经收藏
        if request.user.is_authenticated():  # 判断用户是否登陆
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):  # 数据库是否有数据
                has_fav = True
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {
            'all_teachers' : all_teachers,
            'course_org' : course_org,
            'current_page' :current_page,
            'has_fav': has_fav
        })


class AddFavView(View):
    """
    用户收藏,以及用户取消收藏
    """
    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        if not request.user.is_authenticated(): #判断用户是否登录
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')


        exits_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exits_records:
            #记录已经存在则表示用户取消收藏，也就是删除这条记录
            exits_records.delete()
            #取消收藏后 收藏数减1
            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0: #如果收藏数小于0 则收藏数等于0
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()

            return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
        else:
            #记录不存在就是往数据库中添加数据
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0: #这里就是说两者都存在的时候
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()

                # 取消收藏后 收藏数加1
                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()

                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')


class TeacherListView(View):
    """
    课程讲师列表页
    """
    def get(self, request):
        all_teachers = Teacher.objects.all()

        # 讲师搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:  # Q表示sql的或操作
            all_teachers = all_teachers.filter(
                Q(name__icontains=search_keywords) | Q(work_company__icontains=search_keywords) | Q(
                    work_position__icontains=search_keywords))  # __icontains表示模糊匹配，像sql中的like查询，i表示不区分大小写

        sort = request.GET.get('sort', "")
        #让讲师按人气排序，点击排序后
        if sort:
            if sort == "hot":
                all_teachers = all_teachers.order_by("-click_nums")

        #排行榜讲师排序
        sorted_teachers = Teacher.objects.all().order_by("-click_nums")[:3]

        # 对课程教师进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Provide Paginator with the request object for complete querystring generation

        p = Paginator(all_teachers, 1, request=request)

        teachers = p.page(page)

        return render(request, "teachers-list.html", {
            "all_teachers" : teachers,
            "sorted_teachers" : sorted_teachers,
            "sort" : sort
        })


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id)) #返回这个老师的所有信息
        teacher.click_nums += 1
        teacher.save()
        all_courses = Course.objects.filter(teacher=teacher) #返回这个老师的所有课程
        # 排行榜讲师排序
        sorted_teachers = Teacher.objects.all().order_by("-click_nums")[:3]

        has_fav_teacher = False
        has_fav_org = False

        if request.user.is_authenticated():  # 判断用户是否登陆
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.id, fav_type=3):  # 数据库是否有数据
                has_fav_teacher = True
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.org.id, fav_type=2):  # 数据库是否有数据
                has_fav_org = True

        return render(request, "teacher-detail.html", {
            "teacher" : teacher,
            "all_courses" : all_courses,
            "sorted_teachers" : sorted_teachers,
            "has_fav_teacher" : has_fav_teacher,
            "has_fav_org" : has_fav_org
        })