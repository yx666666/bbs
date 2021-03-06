# -*- coding: utf-8 -*-
import time


from django.core.cache import cache
from django.shortcuts import render

class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

#中间件其实就是一个装饰器。多个中间件就是多个装饰器，相当于套在函数头上。
# def simple_middleware(view):
#     def wrapper(request):
#         print(111)
#         response = view(request)
#         print(2222)
#         return response
#     return wrapper


class BlockSpiderMiddleware(MiddlewareMixin):
    '''
    限制访问频率的中间件: 最高频率为 3 次/秒

        1.  1535500000.00
        ------------------------
        2.  1535500000.01
        3.  1535500000.02
        4.  1535500001.00
        ------------------------
        5.  1535500001.17        now
        ------------------------
        6.  1535500001.99
        7.  1535500002.55
    '''
    def process_request(self, request):
        #获取到访问的用户的ip
        user_ip = request.META['REMOTE_ADDR']
        request_key = 'Request-%s' % user_ip  # 用户请求时间的 key
        block_key = 'Block-%s' % user_ip      # 被封禁用户的 key

        # 检查用户 IP 是否被封禁
        if cache.get(block_key):
            print('你已被封禁')
            return render(request, 'blockers.html')

        # 取出当前时间，及历史访问时间
        now = time.time()
        #获取不到key，给个默认值，如果时限制每秒五次，改这个默认值为五个，或者其他个即可。
        # cache.delete(request_key)
        request_history = cache.get(request_key, [0] * 10)

        # 检查与最早访问时间的间隔
        #这里弹出一个数据，request_history会少一个，但是如果不重新设置request_key
        #的话，不会影响缓存中列表的长度，所以，不会减少。
        if now - request_history.pop(0) >= 1:
            # print('更新访问时间')
            request_history.append(now)              # 滚动更新时间
            cache.set(request_key, request_history,86400)  # 将时间存入缓存
            return
        else:
            # 访问超过限制，将用户 IP 加入缓存
            print('访问频率超过限制')
            cache.set(block_key, True, 3)  # 封禁用户 24 小时

            return render(request, 'blockers.html')
