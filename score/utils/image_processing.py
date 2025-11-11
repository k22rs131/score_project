import cv2, numpy as np, io, img2pdf, os
from PIL import Image
from rembg import remove

# --- 背景除去 ---
def remove_background(pil_image):
    return remove(pil_image)

# --- 傾き補正 ---
def deskew_image(pil_image):
    img = np.array(pil_image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) == 0:
        return pil_image
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    (h, w) = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB))

# --- 見開き(A3) or 片面(A4)判定 ---
def is_double_page(pil_image):
    w, h = pil_image.size
    aspect_ratio = w / h
    return aspect_ratio > 1.2  # 横長なら見開きと判定

# --- 見開きA3生成 ---
def convert_to_a3_pdf(pil_image):
    a3_size = (3508, 4961)
    resized = pil_image.resize(a3_size, Image.LANCZOS)
    pdf_bytes = io.BytesIO()
    resized.convert("RGB").save(pdf_bytes, format="PDF", resolution=300.0)
    pdf_bytes.seek(0)
    return pdf_bytes

# --- 片面A4生成 ---
def convert_to_a4_pdf(pil_image):
    a4_size = (2480, 3508)
    resized = pil_image.resize(a4_size, Image.LANCZOS)
    pdf_bytes = io.BytesIO()
    resized.convert("RGB").save(pdf_bytes, format="PDF", resolution=300.0)
    pdf_bytes.seek(0)
    return pdf_bytes

# --- 総合処理 ---
def process_and_convert(input_file):
    pil_img = Image.open(input_file)
    no_bg = remove_background(pil_img)
    corrected = deskew_image(no_bg)

    if is_double_page(corrected):
        print("📘 見開き(A3)モードで処理します")
        return convert_to_a3_pdf(corrected), "A3"
    else:
        print("📗 片面(A4)モードで処理します")
        return convert_to_a4_pdf(corrected), "A4"
