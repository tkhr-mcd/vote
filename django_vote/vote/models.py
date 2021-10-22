from django.db import models
from django.conf import settings
from django.db.models.fields import DateTimeField
# Create your models here.

class Vote(models.Model):
    words = models.TextField('検索ワード', blank=True)
    created_at = models.DateTimeField('投稿日', auto_now_add=True)
    def __str__(self):
        return self.words

class Comment(models.Model):
    member_id = models.IntegerField(primary_key=True)
    sentence_id = models.IntegerField(blank=True, null=True)
    sentence = models.TextField(blank=True, null=True)
    comment_id = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    comment_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comment'

class Image(models.Model):
    image_id = models.IntegerField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    comment_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'image'


class Member(models.Model):
    member_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=15, blank=True, null=True)
    party = models.CharField(max_length=15, blank=True, null=True)
    prefecture = models.CharField(max_length=15, blank=True, null=True)
    constituency = models.IntegerField(blank=True, null=True)
    twitter_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member'

class User(models.Model):
    user_id = models.AutoField(primary_key = True)
    constituency = models.CharField(max_length= 100)
    query = models.TextField()
    search_datetime = DateTimeField(auto_now_add = True)
