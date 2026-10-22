import hashlib
import unittest
from unittest.mock import patch
from PIL import Image, UnidentifiedImageError

from service.features import ANALYSIS_VERSION, extract_features
from tests.helpers import picture


class FeatureTests(unittest.TestCase):
    def test_uniform_colour_means_and_zero_contrast(self):
        result = extract_features(picture())
        self.assertEqual((result["mean_red"], result["mean_green"], result["mean_blue"]), (20, 80, 140))
        self.assertEqual(result["contrast"], 0)

    def test_dimensions_preserved(self):
        result = extract_features(picture(size=(13, 7)))
        self.assertEqual((result["width"], result["height"]), (13, 7))

    def test_grayscale_is_converted_consistently(self):
        result = extract_features(picture(mode="L", color=85))
        self.assertEqual([result[key] for key in ("mean_red", "mean_green", "mean_blue", "brightness")], [85] * 4)

    def test_same_bytes_same_result(self):
        raw = picture()
        self.assertEqual(extract_features(raw), extract_features(raw))

    def test_sha256_records_exact_input(self):
        raw = picture()
        self.assertEqual(extract_features(raw)["image_sha256"], hashlib.sha256(raw).hexdigest())

    def test_changed_image_changes_fingerprint(self):
        self.assertNotEqual(extract_features(picture())["image_sha256"],
                            extract_features(picture(color=(21, 80, 140)))["image_sha256"])

    def test_algorithm_version_exposed(self):
        self.assertEqual(extract_features(picture())["analysis_version"], ANALYSIS_VERSION)

    def test_real_jpeg_accepted(self):
        result = extract_features(picture(fmt="JPEG"))
        self.assertEqual(result["width"], 12)

    def test_exif_orientation_is_applied(self):
        exif = Image.Exif()
        exif[274] = 6
        result = extract_features(picture(size=(12, 8), fmt="JPEG", exif=exif))
        self.assertEqual((result["width"], result["height"]), (8, 12))

    def test_gif_is_rejected_after_decoding(self):
        with self.assertRaises(ValueError):
            extract_features(picture(fmt="GIF"))

    def test_invalid_bytes_rejected(self):
        with self.assertRaises((UnidentifiedImageError, OSError)):
            extract_features(b"not an image")

    def test_pixel_limit_is_enforced(self):
        with patch("service.features.MAX_PIXELS", 95):
            with self.assertRaises(ValueError):
                extract_features(picture(size=(12, 8)))

    def test_pixel_limit_boundary_accepted(self):
        with patch("service.features.MAX_PIXELS", 96):
            self.assertEqual(extract_features(picture(size=(12, 8)))["width"], 12)
