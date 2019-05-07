# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#django 默认配置在django.conf
# from django.conf import settings
from yonghu.helper import get_access_token,get_wb_user_info
from bbs import settings
from django.shortcuts import render,redirect
from yonghu.forms import RegisterForm
from yonghu.models import User
from django.contrib.auth.hashers import make_password,check_password

# Create your views here.
def register(request):
    if request.method == 'POST':
        #将request.POST的各字段接收，并创建对象form,request.FILES是上传
        #头像是要用的。
        form = RegisterForm(request.POST, request.FILES)
        #如果验证是有效的。
        if form.is_valid():
            #创建用户对象，但是并不向数据库保存。commit=False，
            #这里的user可以直接使用user.password.等。
            #form 中的值不能使用form.password取，只能用字典的形式。
            user = form.save(commit=False)
            user.password = make_password(user.password)
            user.save()

            #注册完直接登陆。session本质上是一个字典。

            # 记录登陆状态
            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname
            request.session['avatar'] = user.avatar
            return redirect('/user/info/')
        else:
            return render(request, 'register.html', {'error': form.errors})
    else:
        return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        nickname = request.POST.get("nickname")
        password = request.POST.get("password")
        print settings.WB_AUTH_URL
        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return render(request, 'login.html',
                          {'error': '用户不存在', 'auth_url': settings.WB_AUTH_URL})

        if check_password(password, user.password):
            # 记录登陆状态
            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname
            request.session['avatar'] = user.avatar
            return redirect('/user/info/')
        else:
            return render(request, 'login.html',
                          {'error': '用户密码错误', 'auth_url': settings.WB_AUTH_URL})
    else:
        return render(request, 'login.html', {'auth_url': settings.WB_AUTH_URL})


def logout(request):
    request.session.flush()
    return redirect('/user/login/')

# # @login_required
def user_info(request):
    uid = request.session.get('uid')
    user = User.objects.get(id=uid)
    return render(request, 'user_info.html', {'user': user})

def weibo_callback(request):
    code = request.GET.get('code')
    # 获取 access token
    access_token, uid = get_access_token(code) #函数有两个返回值
    if access_token is not None:
        # 获取微博用户信息
        nickname, plt_icon = get_wb_user_info(access_token, uid)

        if nickname is not None:
            user, created = User.objects.get_or_create(nickname=nickname)#获取或者创建，有两个返回值
            #created,如果时get出来的，就是false,如果时创建的，就是true
            if created:
                user.plt_icon = plt_icon
                user.save()
            # 记录登陆状态
            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname
            request.session['avatar'] = user.avatar
            return redirect('/user/info/')
    return render(request, 'login.html',
                  {'error': '微博访问异常', 'auth_url': settings.WB_AUTH_URL})
