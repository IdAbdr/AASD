"""Deterministic descriptors, versioned independently from future ML models."""
import hashlib
import io
import warnings

from PIL import Image, ImageOps, ImageStat

ANALYSIS_VERSION = "whole-image-v1"
MAX_PIXELS = 20_000_000


def extract_features(raw):
    """Decode JPEG/PNG, apply EXIF orientation, and describe RGB/gray pixels."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(raw)) as image:
            if image.format not in {"JPEG", "PNG"}:
                raise ValueError("Use a decoded JPEG or PNG image.")
            if image.width * image.height > MAX_PIXELS:
                raise ValueError("Image exceeds 20 megapixels.")
            image.load()
            rgb = ImageOps.exif_transpose(image).convert("RGB")
            color = ImageStat.Stat(rgb)
            gray = ImageStat.Stat(rgb.convert("L"))
            return {
                "analysis_version": ANALYSIS_VERSION,
                "image_sha256": hashlib.sha256(raw).hexdigest(),
                "width": rgb.width,
                "height": rgb.height,
                "mean_red": round(color.mean[0], 4),
                "mean_green": round(color.mean[1], 4),
                "mean_blue": round(color.mean[2], 4),
                "brightness": round(gray.mean[0], 4),
                "contrast": round(gray.stddev[0], 4),
            }
