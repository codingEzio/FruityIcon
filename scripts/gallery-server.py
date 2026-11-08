#!/usr/bin/env python3
"""Add an optional data-only gallery to the hardened public snapshot server."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
from http.server import ThreadingHTTPServer

ROOT = Path(__file__).resolve().parent.parent

def secure_read(path, limit):
    """Open each path component without following symlinks; return bounded bytes."""
    path = Path(os.path.abspath(path))
    parts = path.parts
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts[1:-1]:
            newfd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = newfd
        filefd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
        try:
            with os.fdopen(filefd, 'rb') as f:
                data = f.read(limit + 1)
            if len(data) > limit:
                raise ValueError('overlay file too large')
            return data
        finally:
            pass
    finally:
        os.close(fd)


def load_overlay(path):
    spec = importlib.util.spec_from_file_location('overlay_validator', ROOT / 'scripts/validate-overlay.py')
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    # Reject symlinks in any directory component before the validator reads data.
    catalog_bytes = secure_read(path / 'catalog.json', validator.MAX_JSON)
    data, dimensions = validator.validate(path)
    if json.loads(catalog_bytes) != data:
        raise ValueError('catalog changed during validation')
    for item in data['items']:
        item['dimensions'] = {theme: dimensions[asset] for theme, asset in item['assets'].items()}
    result = {'/overlay/catalog.json': (json.dumps(data).encode(), 'application/json; charset=utf-8')}
    total = len(catalog_bytes)
    for asset in dimensions:
        payload = secure_read(path / 'assets' / (asset + '.png'), validator.MAX_ASSET)
        total += len(payload)
        if total > 64 * 1024 * 1024:
            raise ValueError('overlay exceeds cache limit')
        result['/overlay/assets/' + asset + '.png'] = (payload, 'image/png')
    font = path / 'font.woff2'
    if font.exists():
        payload = secure_read(font, validator.MAX_ASSET)
        total += len(payload)
        if total > 64 * 1024 * 1024:
            raise ValueError('overlay exceeds cache limit')
        result['/overlay/font.woff2'] = (payload, 'font/woff2')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=18210)
    parser.add_argument('--overlay', type=Path, help='explicit local data directory')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('demo_server', ROOT / 'scripts/demo-server.py')
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)
    demo.FILES.update({'gallery/index.html': 'text/html; charset=utf-8',
                       'gallery/gallery.css': 'text/css; charset=utf-8',
                       'gallery/gallery.js': 'text/javascript; charset=utf-8'})
    files = demo.snapshot(ROOT)
    files['/gallery/'] = files['/gallery/index.html']
    if args.overlay:
        files.update(load_overlay(args.overlay))
    with ThreadingHTTPServer(('127.0.0.1', args.port), demo.handler_for(files, args.port)) as server:
        # Tests may use port zero; host validation needs the selected port.
        server.RequestHandlerClass = demo.handler_for(files, server.server_port)
        print(f'Demo: http://127.0.0.1:{server.server_port}/gallery/; overlay: {bool(args.overlay)}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
