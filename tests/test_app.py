import csv
import io
import tempfile
import unittest
from pathlib import Path
from app import create_app
from test_analysis import image_bytes


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.app = create_app({'TESTING': True, 'DATABASE': str(Path(self.temp.name) / 'test.db')})
        self.client = self.app.test_client()

    def upload(self, name='sample.png'):
        return self.client.post('/upload', data={'image': (image_bytes(), name)})

    def test_home_and_empty_history(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertIn(b'No analyses yet', self.client.get('/history').data)

    def test_upload_result_history_and_csv(self):
        response = self.upload()
        self.assertEqual(response.status_code, 302)
        result = self.client.get(response.location)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'mean_red', result.data)
        self.assertIn(b'255.0', result.data)
        self.assertIn(b'Open', self.client.get('/history').data)
        rows = list(csv.DictReader(io.StringIO(self.client.get('/export.csv').text)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(float(rows[0]['mean_red']), 255)

    def test_missing_image(self):
        self.assertEqual(self.client.post('/upload').status_code, 400)

    def test_empty_filename(self):
        self.assertEqual(self.client.post('/upload', data={'image': (image_bytes(), '')}).status_code, 400)

    def test_fake_png(self):
        response = self.client.post('/upload', data={'image': (io.BytesIO(b'fake'), 'fake.png')})
        self.assertEqual(response.status_code, 400)

    def test_body_limit(self):
        self.app.config['MAX_CONTENT_LENGTH'] = 10
        self.assertEqual(self.upload().status_code, 413)

    def test_unknown_result(self):
        self.assertEqual(self.client.get('/result/unknown').status_code, 404)

    def test_repeated_filename_preserves_two_records(self):
        self.upload()
        self.upload()
        rows = list(csv.DictReader(io.StringIO(self.client.get('/export.csv').text)))
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0]['id'], rows[1]['id'])

    def test_filename_not_saved(self):
        self.assertEqual(self.upload('../../escape.png').status_code, 302)
        self.assertFalse((Path(self.temp.name) / 'escape.png').exists())

    def test_separate_databases_are_isolated(self):
        self.upload()
        other = create_app({'TESTING': True, 'DATABASE': str(Path(self.temp.name) / 'other.db')})
        self.assertIn(b'No analyses yet', other.test_client().get('/history').data)

    def test_empty_csv_has_header(self):
        response = self.client.get('/export.csv')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.text.startswith('id,created_at,analysis_version'))

