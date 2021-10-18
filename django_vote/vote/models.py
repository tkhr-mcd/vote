from django.db import models
from django.conf import settings
from django.db.models.fields import DateTimeField
# Create your models here.

class Vote(models.Model):
    words = models.TextField('検索ワード', blank=True)
    created_at = models.DateTimeField('投稿日', auto_now_add=True)
    def __str__(self):
        return self.words

class Area(models.Model):
    prefecture = models.CharField(max_length = 100)
    constituency = models.CharField(max_length= 100)

class Member(models.Model):
    member_id = models.AutoField(primary_key = True)
    name = models.CharField(max_length= 100)
    constituency = models.CharField(max_length= 100)
    twitter_id = models.CharField(max_length= 100)

class Comment(models.Model):
    member_id = models.IntegerField(null = False, blank= False)
    sentence_id = models.IntegerField(null = True, blank= True)
    sentence = models.TextField()
    comment_id = models.IntegerField(null = True, blank= True)
    comment = models.TextField()
    comment_datetime = models.DateTimeField()

class Image(models.Model):
    image_id = models.AutoField(primary_key = True)
    image = models.ImageField(upload_to = '')
    comment_id = models.IntegerField(null = True, blank= True)

class User(models.Model):
    user_id = models.AutoField(primary_key = True)
    constituency = models.CharField(max_length= 100)
    query = models.TextField()
    search_datetime = DateTimeField(auto_now_add = True)
