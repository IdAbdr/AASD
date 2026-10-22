import http.client
import json
import threading
import unittest

from service.server import MAX_UPLOAD_BYTES, make_server
from tests.helpers import picture


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(port=0, revision="test-commit")
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, method, path, body=None, headers=None, raw=False):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        if raw:
            connection.putrequest(method, path)
            for key, value in (headers or {}).items():
                connection.putheader(key, value)
            connection.endheaders()
            if body:
                connection.send(body)
        else:
            connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        content = response.read()
        result = (response.status, dict(response.getheaders()), content)
        connection.close()
        return result

    def test_health_returns_revision(self):
        status, _, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["revision"], "test-commit")

    def test_version_records_runtime(self):
        _, _, body = self.request("GET", "/version")
        result = json.loads(body)
        self.assertTrue(result["python"])
        self.assertTrue(result["pillow"])
        self.assertEqual(result["analysis_version"], "whole-image-v1")

    def test_home_explains_scope(self):
        status, headers, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn(b"Disease classification is outside", body)

    def test_unknown_path_returns_404(self):
        self.assertEqual(self.request("GET", "/missing")[0], 404)

    def test_png_upload_returns_features(self):
        status, _, body = self.request("POST", "/api/features", picture(), {"Content-Type": "image/png"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["mean_green"], 80)

    def test_jpeg_upload_accepted(self):
        self.assertEqual(self.request("POST", "/api/features", picture(fmt="JPEG"),
                                      {"Content-Type": "image/jpeg"})[0], 200)

    def test_corrupt_upload_rejected(self):
        self.assertEqual(self.request("POST", "/api/features", b"bad", {"Content-Type": "image/png"})[0], 400)

    def test_false_png_label_does_not_accept_gif(self):
        self.assertEqual(self.request("POST", "/api/features", picture(fmt="GIF"),
                                      {"Content-Type": "image/png"})[0], 400)

    def test_empty_upload_rejected(self):
        self.assertEqual(self.request("POST", "/api/features", b"", {"Content-Type": "image/png"})[0], 400)

    def test_unsupported_content_type_rejected(self):
        self.assertEqual(self.request("POST", "/api/features", b"text", {"Content-Type": "text/plain"})[0], 415)

    def test_missing_length_rejected(self):
        self.assertEqual(self.request("POST", "/api/features", raw=True)[0], 411)

    def test_invalid_length_rejected(self):
        self.assertEqual(self.request("POST", "/api/features", headers={"Content-Length": "abc"}, raw=True)[0], 400)

    def test_negative_length_rejected(self):
        self.assertEqual(self.request("POST", "/api/features", headers={"Content-Length": "-2"}, raw=True)[0], 400)

    def test_oversized_upload_rejected_before_read(self):
        self.assertEqual(self.request("POST", "/api/features", headers={"Content-Length": str(MAX_UPLOAD_BYTES + 1)}, raw=True)[0], 413)

    def test_post_unknown_path_rejected(self):
        self.assertEqual(self.request("POST", "/missing", b"test")[0], 404)

    def test_responses_are_not_cached(self):
        _, headers, _ = self.request("GET", "/health")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
