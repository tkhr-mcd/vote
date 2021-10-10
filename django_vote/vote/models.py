from django.db import models
from django.conf import settings
# Create your models here.

class Vote(models.Model):
    words = models.TextField('検索ワード', blank=True)
    created_at = models.DateTimeField('投稿日', auto_now_add=True)
    def __str__(self):
        return self.words
