# _*_ coding: utf-8 _*_
"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
import xadmin
from django.views.static import serve


from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView, LogoutView, IndexView
from organization.views import OrgView
from MxOnline.settings import MEDIA_ROOT

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url('^$', IndexView.as_view(), name="index"),
    url('^login/$', LoginView.as_view(), name="login"),
    url('^logout/$', LogoutView.as_view(), name="logout"),
    url('^register/$', RegisterView.as_view(), name="register"),
    url(r'^captcha/', include('captcha.urls')),#验证码库，生成注册页面所需要的验证码
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name="user_active"),  #用于提取用户点击邮箱验证码链接的code，返回时候提取
    url('^forget/$', ForgetPwdView.as_view(), name="forget_pwd"),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset_pwd"),
    url('^modify_pwd/$', ModifyPwdView.as_view(), name="modify_pwd"),#修改密码因为如果重用reset路径的话就必须传activecode，所以还是另写一个

    #课程机构url配置
    url(r'^org/', include('organization.urls', namespace="org")),

    #课程相关url配置
    url(r'^course/', include('courses.urls', namespace="course")),

    #配置上传文件的访问处理函数
    url(r'^media/(?P<path>.*)$', serve, {"document_root":MEDIA_ROOT}), #serve是处理静态文件访问的方法，“document是默认参数，指的是访问的路径”

    # url(r'^static/(?P<path>.*)$', serve, {"document_root":STATIC_ROOT}),

    # 课程相关url配置
    url(r'^users/', include('users.urls', namespace="users")),

    #富文本相关url(用于上传文件等)
    url(r'^ueditor/', include('DjangoUeditor.urls')),
]


#全局404页面配置(handler404为django固定写法，写在url页面，用于找到404页面)
handler404 = 'users.views.page_not_found'

#全局500页面配置
handler500 = 'users.views.page_error'
