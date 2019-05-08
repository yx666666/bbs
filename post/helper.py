# -*- coding: utf-8 -*-
from django.core.cache import cache

# from common import rds
from post.models import Post
from common import rds


def page_cache(timeout):
    '''页面缓存'''
    def deco(view_func):
        def wrapper(request):
            #request.get_full_path()获取完整的url包含参数，不包括ip地址和端口
            #request.session.session_key，获取到的是session_id,这两个拼接，获取到唯一标识
            key = 'PageCache-%s-%s' % (request.session.session_key, request.get_full_path())
            response = cache.get(key)

            print('get from cache: %s' % response)
            if response is None:
                response = view_func(request)
                print('get from view: %s' % response)
                cache.set(key, response, timeout)
                print('set to cache')
            return response
        return wrapper
    return deco

#链接redis，变成一个通用的。
def read_counter(read_view):
    '''帖子阅读计数装饰器'''
    def wrapper(request):
        response = read_view(request)
        # 状态码为 200 时进行计数，状态码在response里边。
        if response.status_code == 200:
            post_id = int(request.GET.get('post_id'))
            rds.zincrby('ReadRank', post_id)
        return response
    return wrapper

#使用数据库的方式，排行，不如redis效率高
#如果不用redis也可以实现，可以在models中再建一个表，只用于记录点击次数最多的十条数据，
#在 post上表加一个字段，count,当count当大于表中的count时，把他加进去。

def get_top_n(num):
    '''获取排行前 N 的数据'''
    # ori_data = [
    #     (b'38', 369.0),
    #     (b'37', 216.0),
    #     (b'40', 52.0),
    # ]
    ori_data = rds.zrevrange('ReadRank', 0, num - 1, withscores=True)

    # 数据清洗
    # cleaned = [
    #     [38, 369],
    #     [37, 216],
    #     [40, 52],
    # ]
    cleaned = [[int(post_id), int(count)] for post_id, count in ori_data]

    # 方法一：循环操作数据库，性能差
    #循环遍历出postid，根据他找到post对象，然后把对象放到第一个位置。
    # for item in cleaned:
    #     post = Post.objects.get(pk=item[0])
    #     item[0] = post

    # 方法二
    #下划线也可以作为变量名，一般取一些不得不取，但又不重要的值的时候使用。下面的下划线仅仅是一个变量。
    post_id_list = [post_id for post_id, _ in cleaned]  # 取出 post id 列表
    posts = Post.objects.filter(id__in=post_id_list)   # 根据 id 批量获取 post
    #按照下标顺序排序
    posts = sorted(posts, key=lambda post: post_id_list.index(post.id))  # 根据 id 位置排序
    for post, item in zip(posts, cleaned):
        item[0] = post  # 逐个替换 post

    #通俗写法
    # for i in xrange(len(cleaned)):
    #     cleaned[i][0] =  posts[i]
    # print cleaned

    # 方法三
    # post_id_list = [post_id for post_id, _ in cleaned]  # 取出 post id 列表
    # # posts = {
    # #     1: <Post: Post object>,
    # #     4: <Post: Post object>,
    # #     6: <Post: Post object>,
    # # }
    # posts = Post.objects.in_bulk(post_id_list)  # 批量获取 post
    # for item in cleaned:
    #     item[0] = posts[item[0]]

    return cleaned
