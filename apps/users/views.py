# _*_ encoding:utf-8 _*_
import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password #对密码明文加密
from users.utils.email_send import send_register_email
from django.http import HttpResponse, HttpResponseRedirect
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse

from .models import UserProfile
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from .models import EmailVerifyRecord
from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Course
from .models import Banner


#自定义用户认证
class CustomBackend(ModelBackend):#会先进自定义的验证方法，这里可以定义用户是否可以用邮箱登陆等
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))#Q代表sql后台多条件查询
            if user.check_password(password):
                return user
        except Exception as e:
            return None


#点击邮箱验证链接，激活用户
class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code) #用过滤器过滤出active_code,根据code找出用户信息
        if all_records: #如果code存在
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:# 如果用户不存在，则返回链接失效页面，也可以说是code有误
            return render(request, "active_fail.html")
        return render(request, "login.html")


#用户注册
class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {'register_form' : register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")  # 从POST中获取用户名和密码
            if UserProfile.objects.filter(email=user_name): #往后台查找注册的用户是否存在，如果存在就return
                return render(request, "register.html", {"register_form" : register_form, "msg": "用户已经存在"})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False #表示用户还没有激活，用户需要点击链接才能激活
            user_profile.password = make_password(pass_word)
            user_profile.save() #保存用户信息

            usernessage = UserMessage()
            usernessage.user = UserProfile.id
            usernessage.message = u"欢迎注册慕学在线网！"
            usernessage.save()

            send_register_email(user_name, 'register')
            return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form" : register_form})


#登出功能
class LogoutView(View):
    """
    用户登出
    """
    def get(self, request):
        logout(request) #调用auth的登出方法
        from django.core.urlresolvers import reverse #用于反解url地址，直接传入url的name即可
        return HttpResponseRedirect(reverse("index"))


#用户登录
class LoginView(View):#django自带的view类
    def get(self, request):
        return render(request, "login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST) #实例化自定义的form，传入request.POST数据进行数据验证，验证逻辑在forms.py里，满足则往下走，不满足直接报错
        if login_form.is_valid():#看验证是否成功
            user_name = request.POST.get("username", "")  # 从POST中获取用户名和密码
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)  # 使用authenticate方法进后台认证，如果认证成功则返回user model对象，否则返回noll
            if user is not None:  # 如果不是空则表示数据可以中有这个用户
                if user.is_active:
                    login(request, user)  # 调用login方法登录（具体登录将会在session和cookie中讲解）
                    return HttpResponseRedirect(reverse("index"))  # 将request和user注册至index页面
                else:
                    return render(request, "login.html", {"msg": "用户未激活"})
            else:
                return render(request, "login.html", {"msg": "用户名或密码错误"})#验证成功但是用户名密码校验错误
        else:
            return render(request, "login.html", {"login_form":login_form})#验证失败则返回错误信息


#登录页面点击忘记密码
class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html", {"forget_form" : forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", "")  # 从POST中获取用户名
            send_register_email(email, 'forget') #发送忘记密码类型邮件，注册链接重置
            return render(request, "send_success.html")
        else:# 如果验证表单失败，还是返回找回密码的页面
            return render(request, "forgetpwd.html", {"forget_form": forget_form})


#点击邮箱验证链接，重置用户密码
class ResetView(View):
    #验证code，再进行跳转
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code) #用过滤器过滤出active_code,根据code找出用户信息
        if all_records: #如果code存在,就直接返回到重置密码页面，并回填一个用户邮箱
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email" : email})
        else:# 如果用户不存在，则返回链接失效页面，也可以说是code有误
            return render(request, "active_fail.html")
        return render(request, "login.html")


    #点击重置密码，提交表单
class ModifyPwdView(View):
    """
    修改用户密码
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST) #做表单验证
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2: #如果两个密码不相等
                return render(request, "password_reset.html", {"email": email, "msg" : "密码不一致"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()

            #密码修改成功，返回登录页面
            return render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email": email, "modify_form": modify_form})


class UserinfoView(LoginRequiredMixin, View):
    """
    用户个人信息
    """
    def get(self, request):
        return render(request, 'usercenter-info.html', {})

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')



class UploadImageView(LoginRequiredMixin, View):
    """
    用户修改头像
    """
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user) #文件是存储在request的files中的，需要取出来
        if image_form.is_valid():
            image_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')



    #点击重置密码，提交表单
class UpdatePwdView(View):
    """
    个人中心修改用户密码
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST) #做表单验证
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2: #如果两个密码不相等
                return HttpResponse('{"status":"fail", "msg" : "密码不一致"}', content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()

            #密码修改成功，返回登录页面
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


#个人中心修改邮箱验证码
class SendEmailCodeView(LoginRequiredMixin, View):
    """
    发送邮箱验证码
    """
    def get(self, request):
        email = request.GET.get('email', '') #从request中取出email
        #判断邮箱是否注册过
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已经存在"}', content_type='application/json')
        send_register_email(email, 'update_email')
        return HttpResponse('{"status":"success"}', content_type='application/json')


#用户点击邮箱验证码，后台验证
class UpdateEmailView(LoginRequiredMixin, View):
    """
    修改个人邮箱
    """
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')
        #判断记录是否存在
        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type= 'update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码出错"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    """
    个人中心，我的课程
    """
    def get(self, request):
        user_courses = UserCourse.objects.filter(name=request.user)
        return render(request, 'usercenter-mycourse.html', {
            "user_courses" : user_courses
        })


class MyFavOrgView(LoginRequiredMixin, View):
    """
    个人中心，我收藏的课程机构
    """
    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        # 找出的只是所有收藏机构的对象，还需要遍历找出id，然后用机构id找出机构，存放list中返回
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html', {
            "org_list" : org_list
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    """
    个人中心，我收藏的授课讲师
    """
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        # 找出的只是所有收藏讲师的对象，还需要遍历找出id，然后用机构id找出机构，存放list中返回
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html', {
            "teacher_list" : teacher_list
        })


class MyFavCourseView(LoginRequiredMixin, View):
    """
    个人中心，我收藏的课程
    """
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        # 找出的只是所有收藏课程的对象，还需要遍历找出id，然后用课程id找出机构，存放list中返回
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter-fav-course.html', {
            "course_list" : course_list
        })


class MyMessageView(LoginRequiredMixin, View):
    """
    个人中心，我的消息
    """
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)
        #用户进入个人消息后，找出所有未读的消息，改成已读
        all_unread_messages = UserMessage.objects.filter(has_read = False, user=request.user.id)
        for unread_messages in all_unread_messages:
            unread_messages.has_read = True
            unread_messages.save()
        # 我的消息分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Provide Paginator with the request object for complete querystring generation

        p = Paginator(all_messages, 1, request=request)

        messages = p.page(page)
        return render(request, 'usercenter-message.html', {
            "all_messages" : messages
        })


class IndexView(View):
    #慕学在线网 首页
    def get(self, request):
        #取出轮播图
        all_banners = Banner.objects.all().order_by('index') #所有轮播图
        courses = Course.objects.filter(is_banner=False)[:6] #取出课程，非轮播图
        banner_courses = Course.objects.filter(is_banner=True)[:3] #取出课程，轮播图
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            'all_banners' : all_banners,
            'courses' : courses,
            'banner_courses' : banner_courses,
            'course_orgs' : course_orgs
        })


#用于返回404等页面
def page_not_found(request):
    from django.shortcuts import render_to_response
    response = render_to_response('404.html')
    response.status_code = 404
    return response


#用于返回500等页面
def page_error(request):
    from django.shortcuts import render_to_response
    response = render_to_response('500.html')
    response.status_code = 500
    return response