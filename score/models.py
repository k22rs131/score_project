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
    score = models.ForeignKey(Score, on_delete=models.CASCADE, related_name="files")
    file = CloudinaryField("file", folder="scores/files", resource_type="auto")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.score.title} - {self.file.public_id if hasattr(self.file, 'public_id') else self.file}"

    @property
    def url(self):
        """Cloudinaryの確実なURLを返す"""
        try:
            return self.file.build_url()
        except Exception:
            return None

    @property
    def is_pdf(self):
        """PDFかどうかをMIMEタイプで判定"""
        return "pdf" in getattr(self.file, "resource_type", "").lower()

    @property
    def is_image(self):
        """画像ファイルかどうかをMIMEタイプで判定"""
        return "image" in getattr(self.file, "resource_type", "").lower()
