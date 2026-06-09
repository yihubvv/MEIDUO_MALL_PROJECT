#!/usr/bin/env python3
import argparse
import mimetypes
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_ROOT = os.path.join(PROJECT_ROOT, "front_end_pc")


class HTTPSFrontendProxy(BaseHTTPRequestHandler):
    backend = "http://127.0.0.1:8000"

    def do_GET(self):
        if self.serve_static_file():
            return
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def do_PUT(self):
        self.proxy_request()

    def do_DELETE(self):
        self.proxy_request()

    def serve_static_file(self):
        parsed = urllib.parse.urlsplit(self.path)
        request_path = urllib.parse.unquote(parsed.path)

        if request_path in ("", "/", "/index/"):
            request_path = "/index.html"

        file_path = os.path.normpath(os.path.join(FRONTEND_ROOT, request_path.lstrip("/")))
        if not file_path.startswith(FRONTEND_ROOT + os.sep):
            self.send_error(403)
            return True

        if not os.path.isfile(file_path):
            return False

        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        with open(file_path, "rb") as fp:
            content = fp.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
        return True

    def proxy_request(self):
        body = None
        if self.command in ("POST", "PUT", "PATCH"):
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length else None

        target = self.backend + self.path
        headers = {
            key: value
            for key, value in self.headers.items()
            if key.lower() not in ("host", "content-length")
        }
        headers["Host"] = self.headers.get("Host", "www.meiduo.site:8080")
        headers["X-Forwarded-Proto"] = "https"

        request = urllib.request.Request(target, data=body, headers=headers, method=self.command)

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                self.send_response(response.status)
                self.copy_response_headers(response.headers)
                self.wfile.write(response.read())
        except urllib.error.HTTPError as error:
            self.send_response(error.code)
            self.copy_response_headers(error.headers)
            self.wfile.write(error.read())
        except urllib.error.URLError as error:
            self.send_error(502, "Backend unavailable: %s" % error.reason)

    def copy_response_headers(self, headers):
        skip = {"server", "date", "transfer-encoding"}
        for key, value in headers.items():
            if key.lower() not in skip:
                self.send_header(key, value)
        self.end_headers()

    def log_message(self, fmt, *args):
        print("%s - - %s" % (self.address_string(), fmt % args))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--cert", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--backend", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    HTTPSFrontendProxy.backend = args.backend.rstrip("/")
    server = ThreadingHTTPServer((args.host, args.port), HTTPSFrontendProxy)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(args.cert, args.key)
    server.socket = context.wrap_socket(server.socket, server_side=True)

    print("Serving HTTPS frontend on https://%s:%s" % (args.host, args.port))
    print("Proxying API requests to %s" % HTTPSFrontendProxy.backend)
    server.serve_forever()


if __name__ == "__main__":
    main()
