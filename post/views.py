# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#修改被除数带小数点，防止两数相除默认取整
from __future__ import division
from django.shortcuts import render,redirect
from post.models import Post, Comment, Tag
from yonghu.models import User

from math import ceil
from post.helper import page_cache,read_counter,get_top_n
from yonghu.helper import login_required,check_perm
import time
# Create your views here.

#缓存时间
@page_cache(5)
def post_list(request):
    #分页
    page = int(request.GET.get('page',1))#获取页码，默认值为1
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    #帖子id，越晚生成的，都在后边，id越大，加上-的，就是新的在前边了。
    posts = Post.objects.all().order_by('-id')[start:end]

    tatal = Post.objects.count() #总的帖子数。
    pages = int(ceil(tatal / per_page))#总页数

    #获取当前用户所有发表的帖子。
    # uid = request.session.get('uid')
    # wposts = Post.objects.filter(uid=uid)
    # cd = len(wposts.values())
    #检查如果是admin,显示出管理人员的权限按钮。
    a = request.session
    if 'user' in a:
        user = request.session['user']
        role = user.roles()
        roles = [u.name for u in role]
        if 'admin' in roles:
            print user.nickname
            return render(request, 'post_list.html', {'posts': posts, 'pages': xrange(pages),
                                                      'admin':'admin'},)

    return render(request,'post_list.html',{'posts':posts,'pages':xrange(pages)})

@login_required
@check_perm('add_post')
def create_post(request):
    if request.method == 'POST':
        uid = request.session.get('uid')
        title = request.POST.get('title')
        content = request.POST.get('content')
        post = Post.objects.create(uid=uid,title=title,content=content)
        return redirect('/post/read/?post_id=%s' % post.id)
    return render(request,'create_post.html',{})

@login_required
def edit_post(request):
    if request.method == 'POST':
        post_id = int(request.POST.get('post_id'))
        post = Post.objects.get(pk=post_id)
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()

        str_tags = request.POST.get('tags')
        #首先，str.title(),所有单词首字母大写，replace，将中文逗号替换为英文逗号，然后按照逗号切割，切s.strip()为真的情况下。
        #然后将得到的结果取出两端空格。
        #先执行if s.strip语句过滤，然后执行s.strip()
        tag_names = [s.strip()
                     for s in str_tags.title().replace('，', ',').split(',')
                     if s.strip()]
        post.update_tags(tag_names)

        return redirect('/post/read/?post_id=%s' % post.id)
    else:
        post_id = int(request.GET.get('post_id'))
        post = Post.objects.get(pk=post_id)
        #防止用户直接输入url进入。
        if request.session['uid'] == post.uid:
            str_tags = ', '.join([t.name for t in post.tags()])
            return render(request, 'edit_post.html', {'post':post,'tags': str_tags})
        else:
            return render(request,'blockers.html')
#先计数，然后缓存，
@read_counter
@page_cache(1)
def read_post(request):
    post_id = int(request.GET.get('post_id'))
    post = Post.objects.get(pk=post_id)

    #获取用户权限级别及拥有的权限,如果是没有登陆的状态，那么直接跳到阅读页。
    a = request.session
    if 'user' not in a:
        return render(request, 'read_post.html', {'post': post, 'roles': []})
    user = request.session['user']
    role = user.roles()
    roles = [u.name for u in role]

    return render(request,'read_post.html',{'post':post,'roles':roles})

@login_required
@check_perm('del_post')
def delete_post(request):
    post_id = int(request.GET.get('post_id'))
    post = Post.objects.get(pk=post_id)
    #防止用户直接输入url删除帖子。
    user = request.session['user']
    roles = user.roles()
    roles = [r.name for r in roles]

    if request.session['uid'] == post.uid or 'manager' in  roles or 'admin' in roles:
        post.delete()
        return redirect('/')
    return render(request, 'blockers.html')

def search(request):
    keyword = request.POST.get('keyword')
    posts = Post.objects.filter(content__contains=keyword) #包含
    return render(request,'search.html',{'posts':posts})

def top10(request):
    # rank_data = [
    #     [<Post(37)>,  100],
    #     [<Post(18)>,   94],
    #     [<Post(22)>,   71],
    # ]
    rank_data = get_top_n(10)
    return render(request, 'top10.html', {'rank_data': rank_data})

@login_required
@check_perm('add_comment')
def comment(request):
    uid = request.session['uid']
    post_id = request.POST.get('post_id')
    content = request.POST.get('content')
    Comment.objects.create(uid=uid, post_id=post_id, content=content)
    return redirect('/post/read/?post_id=%s' % post_id)


#前端限制了，如果帖子id与用户不一样的时候，没有删除功能
@login_required
@check_perm('del_comment')
def del_comment(request):
    comment_id = int(request.GET.get('comment_id'))
    Comment.objects.get(id=comment_id).delete()
    post_id = int(request.GET.get('post_id'))
    return redirect('/post/read/?post_id=%s' % post_id)



def tag_filter(request):
    tag_id = int(request.GET.get('tag_id'))
    tag = Tag.objects.get(id=tag_id)
    return render(request, 'tag_filter.html', {'tag': tag})