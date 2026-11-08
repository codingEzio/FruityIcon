"""Serve only the public demo's bounded, symlink-free startup snapshot."""
import os
from pathlib import Path
import stat
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote_to_bytes

ROOT = Path(__file__).resolve().parent.parent
FILES = {
    'demo/index.html': 'text/html; charset=utf-8',
    'demo/app.js': 'text/javascript; charset=utf-8',
    'demo/demo.css': 'text/css; charset=utf-8',
    'demo/icons.css': 'text/css; charset=utf-8',
    'examples/actions-light.png': 'image/png',
    'examples/actions-dark.png': 'image/png',
    'examples/provenance.json': 'application/json',
    'README.md': 'text/plain; charset=utf-8',
    'LICENSE': 'text/plain; charset=utf-8',
}
MAX_FILE = 8 * 1024 * 1024
MAX_TOTAL = 16 * 1024 * 1024


def snapshot(root):
    """Open each component without following links and retain bounded bytes."""
    result = {}
    total = 0
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for path in FILES:
            parts = path.split('/')
            directory = os.dup(root_fd)
            try:
                for part in parts[:-1]:
                    child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                    os.close(directory)
                    directory = child
                fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
                try:
                    info = os.fstat(fd)
                    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE:
                        raise ValueError(f'Invalid demo file: {path}')
                    with os.fdopen(fd, 'rb', closefd=False) as file:
                        data = file.read(MAX_FILE + 1)
                    if len(data) > MAX_FILE:
                        raise ValueError(f'Demo file too large: {path}')
                finally:
                    os.close(fd)
            finally:
                os.close(directory)
            total += len(data)
            if total > MAX_TOTAL:
                raise ValueError('Demo snapshot too large')
            result['/' + path] = (data, FILES[path])
    finally:
        os.close(root_fd)
    result['/demo/'] = result['/demo/index.html']
    return result


def handler_for(files, port):
    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.respond(False)

        def do_GET(self):
            self.respond(True)

        def respond(self, body):
            hosts = self.headers.get_all('Host', [])
            if len(hosts) != 1 or hosts[0].lower() not in {
                'localhost', f'localhost:{port}', '127.0.0.1', f'127.0.0.1:{port}',
            }:
                self.send_error(400)
                return
            try:
                raw = self.path.split('?', 1)[0]
                path = unquote_to_bytes(raw).decode('utf-8', 'strict')
            except (UnicodeDecodeError, ValueError):
                self.send_error(400)
                return
            if ('\\' in path or any(part in ('.', '..') for part in path.split('/'))
                    or path not in files):
                self.send_error(404)
                return
            data, content_type = files[path]
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            if body:
                self.wfile.write(data)
    return Handler


if __name__ == '__main__':
    files = snapshot(ROOT)
    with ThreadingHTTPServer(('127.0.0.1', 18210), handler_for(files, 18210)) as server:
        print('Demo: http://127.0.0.1:18210/demo/', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
