"""Small local HTTP research service; uploads are processed in memory."""
import json
import os
import platform
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image, UnidentifiedImageError, __version__ as pillow_version
from service.features import ANALYSIS_VERSION, extract_features

MAX_UPLOAD_BYTES = 8 * 1024 * 1024
INDEX = Path(__file__).with_name("index.html").read_bytes()


class ResearchServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def get_request(self):
        sock, address = super().get_request()
        sock.settimeout(15)
        return sock, address


class Handler(BaseHTTPRequestHandler):
    server_version = "SkinResearch/1.0"

    def reply(self, status, payload, content_type="application/json"):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            self.reply(200, INDEX, "text/html; charset=utf-8")
        elif path == "/health":
            self.reply(200, {"status": "ok", "revision": self.server.revision,
                             "analysis_version": ANALYSIS_VERSION})
        elif path == "/version":
            self.reply(200, {"revision": self.server.revision,
                             "analysis_version": ANALYSIS_VERSION,
                             "python": platform.python_version(), "pillow": pillow_version})
        else:
            self.reply(404, {"error": "Endpoint not found."})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/features":
            self.reply(404, {"error": "Endpoint not found."})
            return
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or self.headers.get("Transfer-Encoding"):
            self.reply(411, {"error": "Send one Content-Length header."})
            return
        try:
            length = int(lengths[0])
        except ValueError:
            self.reply(400, {"error": "Invalid content length."})
            return
        if length <= 0:
            self.reply(400, {"error": "Image body is empty or has invalid length."})
            return
        if length > MAX_UPLOAD_BYTES:
            self.reply(413, {"error": "Upload exceeds 8 MiB."})
            return
        media = self.headers.get("Content-Type", "").split(";", 1)[0].lower()
        if media not in {"image/jpeg", "image/png", "application/octet-stream"}:
            self.reply(415, {"error": "Send JPEG or PNG image bytes."})
            return
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError("Incomplete image upload.")
            result = extract_features(raw)
        except (ValueError, OSError, UnidentifiedImageError,
                Image.DecompressionBombWarning, Image.DecompressionBombError):
            self.reply(400, {"error": "Invalid image. Use JPEG/PNG up to 20 megapixels."})
            return
        self.reply(200, result)


def make_server(host="127.0.0.1", port=8000, revision=None):
    server = ResearchServer((host, port), Handler)
    server.revision = revision or os.environ.get("APP_REVISION", "local-development")
    return server


def main():
    server = make_server(os.environ.get("APP_HOST", "0.0.0.0"),
                         int(os.environ.get("PORT", "8000")))
    print(f"Research service ready on port {server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
