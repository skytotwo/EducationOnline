# -*- coding:utf-8 -*-
__author__ = 'jolly'
__date__ = '2017/12/9 下午10:16'
import re
from django import forms

from operation.models import UserAsk


class UserAskForm(forms.ModelForm): #直接将model转换成form，直接用其中字段进行表单验证，也可以验证完直接调用model保存
    class Meta:
        model = UserAsk #指定model
        fields = ['name', 'mobile', 'course_name']

    def clean_mobile(self): #此处必须是clean开头，clean方法就是对指定字段进行进一步是封装，然后返回该字段
        """
        验证手机号码是否合法
        """
        mobile = self.cleaned_data['mobile']
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        p = re.compile(REGEX_MOBILE)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError(u"手机号码非法", code="mobile_invalid")