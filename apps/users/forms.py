# -*- coding:utf-8 -*-
__author__ = 'jolly'
__date__ = '2017/11/25 下午6:58'
from django import forms
from captcha.fields import CaptchaField

from .models import UserProfile


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={"invalid" : u"验证码错误"})# 返回一段html代码


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={"invalid" : u"验证码错误"})# 返回一段html代码


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile #指定model
        fields = ['image']


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile #指定model
        fields = ['nick_name', 'gender', 'birthday', 'address', 'mobile']