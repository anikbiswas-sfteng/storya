#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse


DATA_FILE = Path(__file__).with_name("stories.json")
BASE_DIR = Path(__file__).resolve().parent
STATIC_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
}


def load_stories():
    if not DATA_FILE.exists():
        return [
            {
                "title": "First Rain Together",
                "content": "We got caught in the rain and laughed all the way home.",
            }
        ]
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_stories(stories):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(stories, file, ensure_ascii=True, indent=2)


stories = load_stories()


class StoryHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _write_json(self, status, payload):
        self._set_headers(status, "application/json; charset=utf-8")
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _serve_static(self, request_path):
        path = urlparse(request_path).path
        if path == "/":
            file_path = BASE_DIR / "index.html"
        else:
            normalized = path.lstrip("/")
            file_path = (BASE_DIR / normalized).resolve()

        if BASE_DIR not in file_path.parents and file_path != BASE_DIR:
            self._write_json(403, {"error": "Forbidden"})
            return

        if not file_path.exists() or not file_path.is_file():
            self._write_json(404, {"error": "Not found"})
            return

        content_type = STATIC_TYPES.get(file_path.suffix.lower(), "application/octet-stream")
        self._set_headers(200, content_type)
        with file_path.open("rb") as file:
            self.wfile.write(file.read())

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/story":
            self._set_headers(200)
            self.wfile.write(json.dumps(stories).encode("utf-8"))
            return

        self._serve_static(self.path)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/story":
            self._write_json(404, {"error": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._write_json(400, {"error": "Invalid JSON"})
            return

        title = str(payload.get("title", "")).strip()
        content = str(payload.get("content", "")).strip()
        if not title or not content:
            self._write_json(400, {"error": "title and content are required"})
            return

        words = len(content.split())
        if words > 5000:
            self._write_json(400, {"error": "Story must be 5000 words or fewer"})
            return

        stories.append({"title": title, "content": content})
        try:
            save_stories(stories)
        except OSError:
            self._write_json(500, {"error": "Failed to save"})
            return

        self._write_json(201, {"message": "Story saved"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    server = HTTPServer(("0.0.0.0", port), StoryHandler)
    print(f"Story API running on http://localhost:{port}")
    server.serve_forever()
