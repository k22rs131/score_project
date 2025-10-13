from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import img2pdf
import requests
import time


# ===== カテゴリ定義 =====
CATEGORY = (
    ('課題曲', '課題曲'),
    ('クラシック', 'クラシック'),
    ('ポップス', 'ポップス'),
    ('アンサンブル', 'アンサンブル'),
)


# ===== 安定したリクエスト関数（Cloudinary画像取得時に使用） =====
def safe_request(url, retries=3, delay=2):
    """
    Cloudinary上のファイルを安定して取得するための簡易リトライ関数
    """
    for i in range(retries):
        try:
            r = requests.get(url, stream=True, timeout=10)
            if r.status_code == 200:
                return r
        except requests.RequestException:
            pass
        time.sleep(delay)
    print(f"[WARN] Failed to fetch URL after {retries} tries: {url}")
    return None


# ===== メインのScoreモデル =====
class Score(models.Model):
    title = models.CharField(max_length=100, verbose_name="曲名")
    comp = models.CharField(max_length=100, verbose_name="作曲者")
    arr = models.CharField(max_length=100, blank=True, verbose_name="編曲者")
    category = models.CharField(max_length=100, choices=CATEGORY, verbose_name="カテゴリ")

    # Cloudinary 上に格納されるファイル
    image_file = CloudinaryField('image', folder='scores/images', blank=True, null=True)
    pdf_file = CloudinaryField('pdf', folder='scores/pdfs', resource_type='raw', blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        楽譜画像アップロード時の自動処理:
        1️⃣ Cloudinary上の画像を取得
        2️⃣ OpenCVでトリミング
        3️⃣ ScoreFileの複数画像も含めてPDF化
        4️⃣ Cloudinaryへアップロード
        """
        super().save(*args, **kwargs)

        from cloudinary.uploader import upload

        try:
            image_bytes_list = []

            # --- メイン画像がある場合 ---
            if self.image_file:
                response = safe_request(self.image_file.url)
                if response:
                    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if img is not None:
                        # トリミング
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        blur = cv2.GaussianBlur(gray, (5, 5), 0)
                        edged = cv2.Canny(blur, 50, 200)
                        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        if contours:
                            x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
                            img = img[y:y+h, x:x+w]
                        # JPEGバイト化
                        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                        buf = BytesIO()
                        pil_img.save(buf, format="JPEG")
                        buf.seek(0)
                        image_bytes_list.append(buf.read())

            # --- ScoreFile 経由で追加アップロードされたファイルもPDFに含める ---
            for f in self.files.all():
                if f.file:
                    response = safe_request(f.file.url)
                    if response:
                        image_bytes_list.append(response.content)

            # --- PDF結合＆Cloudinaryアップロード ---
            if image_bytes_list:
                pdf_bytes = BytesIO()
                pdf_bytes.write(img2pdf.convert(image_bytes_list))
                pdf_bytes.seek(0)

                upload_result = upload(
                    pdf_bytes.getvalue(),
                    folder="scores/pdfs",
                    resource_type="raw",
                    public_id=f"score_{self.id}"
                )
                self.pdf_file = upload_result["secure_url"]
                super().save(update_fields=["pdf_file"])

        except Exception as e:
            print("[ERROR] PDF生成エラー:", e)


# ===== 投稿スケジュールなど別機能用 =====
class Post(models.Model):
    name = models.CharField(max_length=100)
    scheduled_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ===== Scoreに紐づく複数ファイルを保持するモデル =====
class ScoreFile(models.Model):
    score = models.ForeignKey(Score, on_delete=models.CASCADE, related_name="files")
    file = CloudinaryField('file', folder='scores/files', resource_type='raw')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.score.title} のファイル ({self.id})"
