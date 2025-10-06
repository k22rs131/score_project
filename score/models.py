from django.db import models
from django.utils import timezone
from django.urls import reverse

CATEGORY = (('課題曲', '課題曲'), ('クラシック','クラシック'), ('ポップス','ポップス'),('アンサンブル','アンサンブル'))
#PART = (
#    ('Piccolo','picc'),
#    ('Flute 1',)
#    )

class Score(models.Model):
    title = models.CharField(max_length=100)#曲名
    comp = models.CharField(max_length=100)#作曲者
    arr = models.CharField(max_length=100, blank=True)#編曲者

    category = models.CharField(
        max_length = 100,
        choices = CATEGORY
    )

    image_file = models.ImageField(upload_to="scores/images/", blank=True, null=True)
    pdf_file = models.FileField(upload_to="scores/pdf/", blank=True, null=True)



    def __str__(self) :
        return self.title


class Post(models.Model):
    name = models.CharField(max_length=100)
    scheduled_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)  # 自動的に作成日時を保存
    updated_at = models.DateTimeField(auto_now=True) 