#!/usr/bin/env python3
"""Add an optional data-only gallery to the hardened public snapshot server."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load_overlay(path):
    spec = importlib.util.spec_from_file_location('overlay_validator', ROOT / 'scripts/validate-overlay.py')
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    data, dimensions, blobs, font = validator.validate(path)
    for item in data['items']:
        item['dimensions'] = {theme: dimensions[asset] for theme, asset in item['assets'].items()}
    result = {'/overlay/catalog.json': (json.dumps(data).encode(), 'application/json; charset=utf-8')}
    for asset, payload in blobs.items():
        result['/overlay/assets/' + asset + '.png'] = (payload, 'image/png')
    if font is not None:
        result['/overlay/font.woff2'] = (font, 'font/woff2')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    spec = importlib.util.spec_from_file_location('server_runtime', ROOT / 'scripts/server-runtime.py')
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    runtime.add_limits(parser)
    parser.add_argument('--overlay', type=Path, help='explicit local data directory')
    args = parser.parse_args()
    runtime.validate_limits(args)
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
    with runtime.BoundedHTTPServer(('127.0.0.1', args.port), demo.handler_for(files, args.port),
                                   connections=args.connections, timeout=args.timeout) as server:
        # Tests may use port zero; host validation needs the selected port.
        server.RequestHandlerClass = demo.handler_for(files, server.server_port)
        print(f'Demo: http://127.0.0.1:{server.server_port}/gallery/; overlay: {bool(args.overlay)}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
