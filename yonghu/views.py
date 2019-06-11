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
from yonghu.helper import login_required
from yonghu.models import UserRoleRelation,Role
from django.http import JsonResponse

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
            #给默认注册的用户添加user权限。
            user_role = Role.objects.get(name='user')
            UserRoleRelation.add_relation(user.id,user_role.id)


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
        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return render(request, 'login.html',
                          {'error': '用户不存在', 'auth_url': settings.WB_AUTH_URL})

        if check_password(password, user.password):
            # 记录登陆状态
            request.session['user'] = user
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

@login_required
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
            request.session['user'] = user
            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname
            request.session['avatar'] = user.avatar
            return redirect('/user/info/')
    return render(request, 'login.html',
                  {'error': '微博访问异常', 'auth_url': settings.WB_AUTH_URL})

#admin用户管理用户模块。
@login_required
def user_gl(request):
    name = request.POST.get('name')
    uid = request.session.get('uid')
    user = User.objects.get(id=uid)
    return render(request, 'user_gl.html', {'user': user})

#查询使用ajax
def query_role(request):
    name = request.GET.get('name')
    #如果用户存在，那么返回用户信息。并展示已拥有权限和可添加权限。
    data = {
    }
    try:
        name = User.objects.get(nickname=name)
        role_list = [ i[1] for i in name.roles().values_list()]
        role_all =[ i for i in ['user', 'admin', 'manager']]
        no_list = [i for i in role_all if i not in role_list]
        data = {
            'role_list':role_list,
            'no_list':no_list,
            'fuck': 1,
        }
    except:
        data = {
            'message':'用户名不存在,请重新输入,请等待页面刷新。'
        }
    return JsonResponse(data)


def change_role(request):
    name = request.GET.get('name')
    juese = request.GET.get('juese')
    #如果用户存在，那么返回用户信息。并展示已拥有权限和可添加权限。
    data = {
    }
    try:
        name = User.objects.get(nickname=name)
        juese_id = Role.objects.get(name=juese).id

        role_list = [ i[1] for i in name.roles().values_list()]
        role_all =[ i for i in ['user', 'admin', 'manager']]
        no_list = [i for i in role_all if i not in role_list]
        #如果输入的是已有的，表示要删除的。
        if juese in role_list:
            role_list.remove(juese)
            no_list.append(juese)
            data = {
                'role_list': role_list,
                'no_list': no_list,
                'fuck': 1,
            }

            UserRoleRelation.del_relation(name.id,juese_id)

        #表示要添加
        elif juese in no_list:
            no_list.remove(juese)
            role_list.append(juese)
            data = {
                'role_list': role_list,
                'no_list': no_list,
                'fuck': 2,
            }
            UserRoleRelation.add_relation(name.id, juese_id)
    #如果输入的角色不存在，说明输入错误。
    except:
        data = {
            'message':'您输入的角色名不存在。',
            'fuck':3
        }

    return JsonResponse(data)

def del_role(request):
    name = request.GET.get('name')
    User.objects.get(nickname=name).delete()
    data = {
        'message':'删除用户成功。'
    }
    return JsonResponse(data)
