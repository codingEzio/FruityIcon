#!/usr/bin/env python3
"""Validate a bounded data-only gallery overlay."""
import argparse
import json
import math
import os
import stat
import re
import struct
from pathlib import Path

MAX_JSON = 256 * 1024
MAX_ASSET = 16 * 1024 * 1024
MAX_ITEMS = 1000
IDENTIFIER = re.compile(r'^[a-z0-9][a-z0-9_-]{0,63}$')
LANGUAGES = ('en', 'zh-Hans', 'zh-Hant')


def secure_read(path, limit):
    """Read one regular file without following any path symlink."""
    parts = Path(os.path.abspath(path)).parts
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
                raise ValueError('overlay entry is not a bounded regular file')
            with os.fdopen(fd, 'rb', closefd=False) as f:
                payload = f.read(limit + 1)
            if len(payload) > limit:
                raise ValueError('overlay entry exceeds size limit')
            return payload
        finally:
            os.close(fd)
    finally:
        os.close(directory)


def checked_file(payload):
    header = payload[:24]
    if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError('asset is not a PNG')
    width, height = struct.unpack('>II', header[16:24])
    if not width or not height or width > 4096 or height > 4096:
        raise ValueError('invalid image dimensions')
    return width, height


def labels(value):
    return isinstance(value, dict) and set(value) == set(LANGUAGES) and all(
        isinstance(v, str) and v.strip() and len(v) <= 128 for v in value.values()
    )


def validate(root):
    root = Path(root)
    catalog_bytes = secure_read(root / 'catalog.json', MAX_JSON)
    data = json.loads(catalog_bytes)
    if not isinstance(data, dict) or set(data) not in ({'version', 'categories', 'items'}, {'version', 'categories', 'items', 'toolbar'}) or data['version'] != 1:
        raise ValueError('invalid catalog schema')
    data.setdefault('toolbar', {})
    categories, items = data['categories'], data['items']
    if not isinstance(categories, dict) or len(categories) > 100 or any(
        not IDENTIFIER.fullmatch(k) or not labels(v) for k, v in categories.items()
    ):
        raise ValueError('invalid categories')
    if not isinstance(items, list) or len(items) > MAX_ITEMS:
        raise ValueError('invalid item count')
    seen, dimensions, blobs = set(), {}, {}
    aliases = set()
    total = len(catalog_bytes)
    for item in items:
        required = {'id', 'labels', 'category', 'assets', 'rect', 'cell', 'monochrome', 'description', 'optical', 'symbol'}
        if not isinstance(item, dict) or set(item) not in (required, required | {'aliases'}):
            raise ValueError('invalid item fields')
        ident, name, category, assets, rect = (item[k] for k in ('id', 'labels', 'category', 'assets', 'rect'))
        if not isinstance(ident, str) or not IDENTIFIER.fullmatch(ident) or ident in seen:
            raise ValueError('invalid or duplicate item identifier')
        seen.add(ident)
        names = item.get('aliases', [])
        if (not isinstance(names, list) or len(names) > 20 or
                any(not isinstance(a, str) or not IDENTIFIER.fullmatch(a) for a in names) or
                len(names) != len(set(names)) or aliases.intersection(names)):
            raise ValueError('invalid or duplicate link aliases')
        aliases.update(names)
        optical = item['optical']
        if (not isinstance(optical, list) or len(optical) != 8 or
                any(type(v) not in (int, float) or not math.isfinite(v) or abs(v) > 100 for v in optical) or
                min(optical[:2]) <= 0 or any(v < 0 or v > 1 for v in optical[4:]) or
                optical[4] + optical[6] >= 1 or optical[5] + optical[7] >= 1):
            raise ValueError('invalid optical geometry')
        if item['symbol'] is not None and item['symbol'] not in tuple(str(i) for i in range(1, 13)):
            raise ValueError('invalid comparison symbol')
        if type(item['monochrome']) is not bool:
            raise ValueError('invalid monochrome flag')
        if not labels(name) or not labels(item['description']) or category not in categories:
            raise ValueError('invalid labels or category')
        if not isinstance(assets, dict) or set(assets) != {'light', 'dark'}:
            raise ValueError('invalid asset variants')
        if not isinstance(rect, list) or len(rect) != 4 or any(type(v) is not int for v in rect):
            raise ValueError('invalid rectangle')
        x, y, width, height = rect
        if min(x, y) < 0 or min(width, height) < 1:
            raise ValueError('invalid rectangle')
        for asset in assets.values():
            if not isinstance(asset, str) or not IDENTIFIER.fullmatch(asset):
                raise ValueError('invalid asset identifier')
            if asset not in dimensions:
                blob = secure_read(root / 'assets' / (asset + '.png'), MAX_ASSET)
                total += len(blob)
                if total > 64 * 1024 * 1024:
                    raise ValueError('overlay exceeds cache limit')
                dimensions[asset] = checked_file(blob)
                blobs[asset] = blob
            image_width, image_height = dimensions[asset]
            if x + width > image_width or y + height > image_height:
                raise ValueError('rectangle exceeds asset')
            cell = item['cell']
            if not isinstance(cell, list) or len(cell) != 4 or any(type(v) is not int for v in cell):
                raise ValueError('invalid cell')
            cx, cy, cw, ch = cell
            if min(cx, cy) < 0 or min(cw, ch) < 1 or cx + cw > image_width or cy + ch > image_height:
                raise ValueError('cell exceeds asset')
    if seen.intersection(aliases):
        raise ValueError('link alias conflicts with an item id')
    toolbar = data['toolbar']
    roles = {'search', 'add', 'favorite', 'upload', 'download', 'settings'}
    if not isinstance(toolbar, dict) or set(toolbar) not in (set(), roles) or any(
        not isinstance(value, str) or value not in seen for value in toolbar.values()
    ):
        raise ValueError('invalid toolbar mapping')
    try:
        font = secure_read(root / 'font.woff2', MAX_ASSET)
    except FileNotFoundError:
        font = None
    if font is not None and total + len(font) > 64 * 1024 * 1024:
        raise ValueError('overlay exceeds cache limit')
    return data, dimensions, blobs, font


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('overlay', type=Path)
    args = parser.parse_args()
    try:
        data, dimensions, _, _ = validate(args.overlay)
    except (ValueError, OSError, UnicodeError, TypeError) as exc:
        parser.exit(1, f'Invalid overlay: {exc}\n')
    print(f"Valid overlay: {len(data['items'])} items, {len(dimensions)} assets")
