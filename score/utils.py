import cv2
import img2pdf
from PIL import Image
from io import BytesIO
import numpy as np

def detect_and_split_pages(image_path):
    """
    背景除去なしで輪郭トリミング＋PDF化
    """
    img = cv2.imread(image_path)
    if img is None:
        print("画像が読み込めませんでした")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 50, 200)

    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        cropped = img[y:y+h, x:x+w]
    else:
        cropped = img

    pil_img = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
    buf = BytesIO()
    pil_img.save(buf, format="JPEG")
    buf.seek(0)
    return BytesIO(img2pdf.convert(buf.read()))
