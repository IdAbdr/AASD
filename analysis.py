"""Deterministic whole-image descriptors; these are not disease predictions."""
from PIL import Image, ImageOps, ImageStat

ANALYSIS_VERSION = 'whole-image-v1'
MAX_PIXELS = 20_000_000


def extract_features(source):
    """Decode JPEG/PNG and summarize RGB and grayscale pixels after EXIF rotation."""
    with Image.open(source) as image:
        if image.format not in {'JPEG', 'PNG'}:
            raise ValueError('Only decoded JPEG and PNG images are accepted.')
        if image.width * image.height > MAX_PIXELS:
            raise ValueError('Image exceeds the 20 megapixel limit.')
        image.load()
        rgb = ImageOps.exif_transpose(image).convert('RGB')
        color = ImageStat.Stat(rgb)
        gray = ImageStat.Stat(rgb.convert('L'))
        return {
            'analysis_version': ANALYSIS_VERSION,
            'width': rgb.width,
            'height': rgb.height,
            'mean_red': round(color.mean[0], 4),
            'mean_green': round(color.mean[1], 4),
            'mean_blue': round(color.mean[2], 4),
            'brightness': round(gray.mean[0], 4),
            'contrast': round(gray.stddev[0], 4),
        }
