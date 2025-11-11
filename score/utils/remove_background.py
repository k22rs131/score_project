# score_app/utils/background_remove.py
import os
import io
from rembg import remove, new_session
from PIL import Image

# モデルディレクトリを指定
MODEL_DIR = os.path.dirname(__file__)
os.environ["U2NET_HOME"] = MODEL_DIR

# 軽量モデルu2netpを利用
SESSION = new_session("u2netp")

def remove_background(pil_image: Image.Image) -> Image.Image:
    """背景除去（u2netp同梱版）"""
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    result = remove(buf.getvalue(), session=SESSION)
    return Image.open(io.BytesIO(result))
