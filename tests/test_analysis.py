import io
import unittest
from PIL import Image
from analysis import extract_features


def image_bytes(color=(255, 0, 0), size=(3, 2), image_format='PNG'):
    stream = io.BytesIO()
    Image.new('RGB', size, color).save(stream, format=image_format)
    stream.seek(0)
    return stream


class FeatureTests(unittest.TestCase):
    def test_known_rgb_means(self):
        data = extract_features(image_bytes())
        self.assertEqual((data['width'], data['height']), (3, 2))
        self.assertEqual(data['mean_red'], 255)
        self.assertEqual(data['mean_green'], 0)
        self.assertEqual(data['mean_blue'], 0)
        self.assertEqual(data['contrast'], 0)

    def test_black_and_white_values(self):
        for value in (0, 255):
            data = extract_features(image_bytes((value, value, value)))
            self.assertEqual(data['brightness'], value)
            self.assertEqual(data['contrast'], 0)

    def test_nonuniform_population_contrast(self):
        image = Image.new('RGB', (2, 1))
        image.putdata([(0, 0, 0), (255, 255, 255)])
        stream = io.BytesIO()
        image.save(stream, format='PNG')
        stream.seek(0)
        data = extract_features(stream)
        self.assertEqual(data['brightness'], 127.5)
        self.assertEqual(data['contrast'], 127.5)

    def test_repeatable(self):
        self.assertEqual(extract_features(image_bytes()), extract_features(image_bytes()))

    def test_jpeg_supported(self):
        self.assertEqual(extract_features(image_bytes(image_format='JPEG'))['width'], 3)

    def test_bad_bytes_rejected(self):
        with self.assertRaises(OSError):
            extract_features(io.BytesIO(b'not an image'))

    def test_gif_rejected(self):
        with self.assertRaises(ValueError):
            extract_features(image_bytes(image_format='GIF'))

    def test_pixel_limit(self):
        from unittest.mock import patch
        with patch('analysis.MAX_PIXELS', 1):
            with self.assertRaises(ValueError):
                extract_features(image_bytes())

    def test_exif_orientation(self):
        stream = io.BytesIO()
        image = Image.new('RGB', (3, 2))
        exif = Image.Exif()
        exif[274] = 6
        image.save(stream, format='JPEG', exif=exif)
        stream.seek(0)
        data = extract_features(stream)
        self.assertEqual((data['width'], data['height']), (2, 3))

