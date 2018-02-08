# _*_ coding:utf-8 _*_
import xadmin
from xadmin.plugins.auth import UserAdmin

from .models import EmailVerifyRecord
from .models import Banner, UserProfile
from xadmin import views


# class UserProfileAdmin(UserAdmin):
#     pass


class BaseSetting(object):
    enable_themes = True #设置主题可见
    use_bootswatch = True


class GlobalSetting(object):
    site_title = "慕学后台管理系统" #设置页头标贴
    site_footer = "慕学在线网"  #设置页脚标注
    menu_style = "accordion" #设置后台app节点折叠


class EmailVerifyRecordAdmin(object):
    list_display = ['code', 'email', 'send_type', 'send_time']#默认显示
    search_fields = ['code', 'email', 'send_type']#查询
    list_filter = ['code', 'email', 'send_type', 'send_time']#过滤筛选
    model_icon = 'fa fa-address-book-o'


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time']  # 默认显示
    search_fields = ['title', 'image', 'url', 'index']  # 查询
    list_filter = ['title', 'image', 'url', 'index', 'add_time']  # 过滤筛选
    model_icon = 'fa fa - desktop'


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
# xadmin.site.register(UserProfile, UserProfileAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSetting)