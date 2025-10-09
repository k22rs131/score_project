from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import img2pdf
import requests

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
    category = models.CharField(max_length=100, choices=CATEGORY, verbose_name="カテゴリ")

    # Cloudinary 上に格納されるファイル
    image_file = CloudinaryField('image', folder='scores/images', blank=True, null=True)
    pdf_file = CloudinaryField('pdf', folder='scores/pdfs', blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        楽譜画像アップロード時に:
        1️⃣ Cloudinaryに画像を保存
        2️⃣ URLから取得してOpenCVでトリミング
        3️⃣ PDF化してCloudinaryへ再アップロード
        """
        super().save(*args, **kwargs)

        if self.image_file and not self.pdf_file:
            try:
                # --- Cloudinary上の画像を取得 ---
                response = requests.get(self.image_file.url, stream=True)
                if response.status_code != 200:
                    print("画像の取得に失敗しました")
                    return

                # --- OpenCVで読み込み ---
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                if img is None:
                    print("cv2.imdecode failed")
                    return

                # --- トリミング処理 ---
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                edged = cv2.Canny(blur, 50, 200)
                contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    contours = sorted(contours, key=cv2.contourArea, reverse=True)
                    x, y, w, h = cv2.boundingRect(contours[0])
                    cropped = img[y:y+h, x:x+w]
                else:
                    cropped = img  # 失敗した場合は元画像

                # --- PDF化 ---
                pil_img = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
                buf = BytesIO()
                pil_img.save(buf, format="JPEG")
                buf.seek(0)
                pdf_bytes = BytesIO(img2pdf.convert(buf.read()))

                # --- CloudinaryにPDFアップロード ---
                from cloudinary.uploader import upload
                upload_result = upload(
                    pdf_bytes.getvalue(),
                    folder="scores/pdfs",
                    resource_type="raw",
                    public_id=f"score_{self.id}"
                )

                # --- モデルにURL保存 ---
                self.pdf_file = upload_result["secure_url"]
                super().save(update_fields=["pdf_file"])

            except Exception as e:
                print("PDF生成エラー:", e)


class Post(models.Model):
    name = models.CharField(max_length=100)
    scheduled_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
