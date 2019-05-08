# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#修改被除数带小数点，防止两数相除默认取整
from __future__ import division
from django.shortcuts import render,redirect
from post.models import Post
from math import ceil
from post.helper import page_cache,read_counter,get_top_n

# Create your views here.

#缓存时间
@page_cache(5)
def post_list(request):
    #分页
    page = int(request.GET.get('page',1))#获取页码，默认值为1
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    posts = Post.objects.all()[start:end]
    tatal = Post.objects.count() #总的帖子数。
    pages = int(ceil(tatal / per_page))#总页数

    return render(request,'post_list.html',{'posts':posts,'pages':xrange(pages)})

def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        post = Post.objects.create(title=title,content=content)
        return redirect('/post/read/?post_id=%s' % post.id)
    return render(request,'create_post.html',{})

def edit_post(request):
    if request.method == 'POST':
        post_id = int(request.POST.get('post_id'))
        post = Post.objects.get(pk=post_id)
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()
        return redirect('/post/read/?post_id=%s' % post.id)
    else:
        post_id = int(request.GET.get('post_id'))
        post = Post.objects.get(pk=post_id)
        return render(request, 'edit_post.html', {'post':post})
#先计数，然后缓存，
@read_counter
@page_cache(2)
def read_post(request):
    post_id = int(request.GET.get('post_id'))
    post = Post.objects.get(pk=post_id)
    return render(request,'read_post.html',{'post':post})

def delete_post(request):
    post_id = int(request.GET.get('post_id'))
    Post.objects.get(pk=post_id).delete()
    return redirect('/')

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