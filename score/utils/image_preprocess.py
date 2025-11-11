# score_app/utils/image_preprocess.py
import cv2
import numpy as np
from PIL import Image

def deskew_image_to_a3(pil_image):
    """
    背景除去済み画像を入力として
    四隅を検出 → 傾き補正 → A3比率(横長)に変換
    """
    img = np.array(pil_image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("⚠️ 輪郭なし→通常deskew")
        return pil_image

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    h, w = gray.shape
    found = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(approx) > 0.3 * w * h:
            found = approx
            break
    if found is None:
        print("⚠️ 四角形なし→通常deskew")
        return pil_image

    # 四隅整形
    pts = found.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]      # 左上
    rect[2] = pts[np.argmax(s)]      # 右下
    rect[1] = pts[np.argmin(diff)]   # 右上
    rect[3] = pts[np.argmax(diff)]   # 左下

    # A3出力サイズ（横長）
    a3_w, a3_h = 2970, int(2970 / 1.414)

    # 入力が縦長なら、座標の対応を調整
    if h > w:
        rect = np.array([rect[3], rect[0], rect[1], rect[2]], dtype="float32")

    dst = np.array([
        [0, 0],
        [a3_w - 1, 0],
        [a3_w - 1, a3_h - 1],
        [0, a3_h - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (a3_w, a3_h))

    print("✅ A3補正＆傾き補正完了")
    return Image.fromarray(warped)
