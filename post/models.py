# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from yonghu.models import User

# Create your models here.
class Post(models.Model):
    #创建帖子时，绑定uid,根据帖子查询用户信息时使用。
    uid = models.IntegerField()
    title = models.CharField(max_length=64)
    #auto_now,每保存一次修改一次，auto_now_add，仅创建时修改
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    @property
    def auth(self):
        if not hasattr(self,'_auth'):
            self._auth = User.objects.get(id=self.uid)
        return self._auth

    def comments(self):
        '''帖子的所有评论'''
        return Comment.objects.filter(post_id=self.id).order_by('-id')

    def tags(self):
        '''帖子对应的所有 tag'''
        relations = PostTagRelation.objects.filter(post_id=self.id).only('tag_id')  # 取出与post与tag的关系
        tag_id_list = [r.tag_id for r in relations]  # 取出对应的 tag id 列表
        return Tag.objects.filter(id__in=tag_id_list)  # 返回对应的 tag

    def update_tags(self, tag_names):
        '''更新 post 对应的 tag
            第三张表是posttagrelation表
            添加tag的时候，找出来当前已存在的，然后把真正新的给添加出来。
        '''
        #这里获得到的是，传入tag_names的所有tag，已有关系和没有关系的。
        updated_tags = set(Tag.ensure_tags(tag_names))
        #当前已有的tags
        current_tags = set(self.tags())

        # 找出尚未建立关联的 tag
        need_create_tags = updated_tags - current_tags
        need_create_tag_id_list = [t.id for t in need_create_tags]
        PostTagRelation.add_relations(self.id, need_create_tag_id_list)

        # 找出需要删除关联的 tag
        need_delete_tags = current_tags - updated_tags
        need_delete_tag_id_list = [t.id for t in need_delete_tags]
        PostTagRelation.del_relations(self.id, need_delete_tag_id_list)


class Comment(models.Model):
    uid = models.IntegerField()
    post_id = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    @property
    def auth(self):
        '''评论的作者'''
        if not hasattr(self, '_auth'):
            self._auth = User.objects.get(id=self.uid)
        return self._auth

    @property
    def post(self):
        '''评论对应的帖子'''
        if not hasattr(self, '_post'):
            self._post = Post.objects.get(id=self.post_id)
        return self._post



class PostTagRelation(models.Model):
    '''
    post 与 tag 的关系表

        使用Nginx做负载均衡     nginx
        使用Nginx做负载均衡     linux
        使用Nginx做负载均衡     web
        Linux部署             linux
        Linux部署             nginx
        Linux部署             django
        Python的魔术方法       python
    '''
    post_id = models.IntegerField()
    tag_id = models.IntegerField()

    @classmethod
    #一个帖子可能会有多个标签
    def add_relations(cls, post_id, tag_id_list):
        '''建立 post id 与 tags 的对应关系'''
        new_relations = [cls(post_id=post_id, tag_id=tid) for tid in tag_id_list]
        cls.objects.bulk_create(new_relations)

    @classmethod
    def del_relations(cls, post_id, tag_id_list):
        cls.objects.filter(post_id=post_id, tag_id__in=tag_id_list).delete()
#
class Tag(models.Model):
    name = models.CharField(max_length=16, unique=True)

    @classmethod
    def ensure_tags(cls, tag_names):
        '''确保传入的 tag 已存在，如果不存在直接创建出来'''
        #取出name在tag_names的对象，不能用exclude，他会把数据库中不在这里的都拿出来，而不是拿出来列表中的其他。
        exists = cls.objects.filter(name__in=tag_names)  # 当前已存在的 tag
        exist_names = set(tag.name for tag in exists)  # 已存在的 tag 的 name
        new_names = set(tag_names) - exist_names  # 待创建的 tag 的 name
        new_tags = [cls(name=n) for n in new_names]  # 待创建的 tag
        cls.objects.bulk_create(new_tags)  # 批量提交、创建
        #此时return 的是所有的传来列表的所有tag,不存在的已经创建了。
        return cls.objects.filter(name__in=tag_names)

    def posts(self):
        '''当前 tag 对应的所有 post'''
        relations = PostTagRelation.objects.filter(tag_id=self.id).only('post_id')  # 取出与tag与post的关系
        post_id_list = [r.post_id for r in relations]  # 取出对应的 post id 列表
        return Post.objects.filter(id__in=post_id_list)  # 返回对应的 post

