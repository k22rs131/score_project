from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField

CATEGORY = (
    ('課題曲', '課題曲'),
    ('クラシック', 'クラシック'),
    ('ポップス', 'ポップス'),
    ('アンサンブル', 'アンサンブル'),
)


class Score(models.Model):
    title = models.CharField(max_length=100, verbose_name="曲名")
    comp = models.CharField(max_length=100, verbose_name="作曲者")
    arr = models.CharField(max_length=100, blank=True, verbose_name="編曲者")
    category = models.CharField(max_length=100, choices=CATEGORY, verbose_name="ジャンル")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class ScoreFile(models.Model):
    score = models.ForeignKey(Score, on_delete=models.CASCADE)
    file_url = models.URLField(max_length=500, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.score.title} - {self.file_type}"
