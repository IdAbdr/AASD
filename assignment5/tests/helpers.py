import io
from PIL import Image


def picture(mode="RGB", color=(20, 80, 140), size=(12, 8), fmt="PNG", **kwargs):
    buffer = io.BytesIO()
    Image.new(mode, size, color).save(buffer, format=fmt, **kwargs)
    return buffer.getvalue()
