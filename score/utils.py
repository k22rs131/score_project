def detect_and_split_pages(image_path):
    import cv2, img2pdf, io
    from PIL import Image
    import numpy as np
    from rembg import remove

    #画像を読み込む
    img = cv2.imread(image_path)
    if img is None:
        print("DEBUG: cv2.imread failed, path:", image_path)
        return None

    # rembg で背景除去
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    no_bg = remove(pil_img)

    # OpenCV 形式に戻す
    img = cv2.cvtColor(np.array(no_bg), cv2.COLOR_RGBA2BGR)

    # --- 輪郭抽出をコメントアウト ---
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray, (5,5), 0)
    # edged = cv2.Canny(blur, 50, 200)

    # contours = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    # result = []
    # for pt in contours:
    #     x,y,w,h = cv2.boundingRect(pt)
    #     if not(500 < w < 800): continue
    #     result.append([x, y, w, h])

    # result = sorted(result, key=lambda x: x[0])

    # result2 = []
    # lastx = -100
    # for x, y, w, h in result:
    #     if (x - lastx)< 10: continue
    #     result2.append([x, y, w, h])
    #     lastx = x

    # 仮に画像全体を対象とする
    h, w = img.shape[:2]
    x, y = 0, 0

    cropped = img[y:y+h, x:x+w]

    aspect_ratio = w / float(h)
    pages = []

    if aspect_ratio > 1.3:
        mid_x = w // 2
        pages = [cropped[:, :mid_x], cropped[:, mid_x:]]
    else:
        pages = [cropped]

    image_bytes = []
    for page in pages:
        pil_img = Image.fromarray(cv2.cvtColor(page, cv2.COLOR_BGR2RGB))
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG")
        buf.seek(0)
        image_bytes.append(buf.read())

    pdf_bytes = io.BytesIO()
    pdf_bytes.write(img2pdf.convert(image_bytes))
    pdf_bytes.seek(0)

    return pdf_bytes