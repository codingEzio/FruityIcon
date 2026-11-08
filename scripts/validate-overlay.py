#!/usr/bin/env python3
"""Validate a bounded data-only gallery overlay."""
import argparse
import json
import re
import struct
from pathlib import Path

MAX_JSON = 256 * 1024
MAX_ASSET = 16 * 1024 * 1024
MAX_ITEMS = 1000
IDENTIFIER = re.compile(r'^[a-z0-9][a-z0-9_-]{0,63}$')
LANGUAGES = ('en', 'zh-Hans', 'zh-Hant')


def checked_file(root, name):
    if not isinstance(name, str) or not IDENTIFIER.fullmatch(name):
        raise ValueError('invalid asset identifier')
    path = root / 'assets' / (name + '.png')
    if root.is_symlink() or (root / 'assets').is_symlink() or path.is_symlink():
        raise ValueError('symlinks are not accepted')
    if not path.is_file() or path.stat().st_size > MAX_ASSET:
        raise ValueError('asset missing or too large')
    with path.open('rb') as f:
        header = f.read(24)
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
    path = root / 'catalog.json'
    if root.is_symlink() or path.is_symlink() or path.stat().st_size > MAX_JSON:
        raise ValueError('invalid catalog file')
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'version', 'categories', 'items'} or data['version'] != 1:
        raise ValueError('invalid catalog schema')
    categories, items = data['categories'], data['items']
    if not isinstance(categories, dict) or len(categories) > 100 or any(
        not IDENTIFIER.fullmatch(k) or not labels(v) for k, v in categories.items()
    ):
        raise ValueError('invalid categories')
    if not isinstance(items, list) or len(items) > MAX_ITEMS:
        raise ValueError('invalid item count')
    seen, dimensions = set(), {}
    for item in items:
        if not isinstance(item, dict) or set(item) != {'id', 'labels', 'category', 'assets', 'rect', 'cell', 'monochrome', 'description'}:
            raise ValueError('invalid item fields')
        ident, name, category, assets, rect = (item[k] for k in ('id', 'labels', 'category', 'assets', 'rect'))
        if not isinstance(ident, str) or not IDENTIFIER.fullmatch(ident) or ident in seen:
            raise ValueError('invalid or duplicate item identifier')
        seen.add(ident)
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
                dimensions[asset] = checked_file(root, asset)
            image_width, image_height = dimensions[asset]
            if x + width > image_width or y + height > image_height:
                raise ValueError('rectangle exceeds asset')
            cell = item['cell']
            if not isinstance(cell, list) or len(cell) != 4 or any(type(v) is not int for v in cell):
                raise ValueError('invalid cell')
            cx, cy, cw, ch = cell
            if min(cx, cy) < 0 or min(cw, ch) < 1 or cx + cw > image_width or cy + ch > image_height:
                raise ValueError('cell exceeds asset')
    font = root / 'font.woff2'
    if font.is_symlink() or (font.exists() and (not font.is_file() or font.stat().st_size > MAX_ASSET)):
        raise ValueError('invalid font')
    return data, dimensions


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('overlay', type=Path)
    args = parser.parse_args()
    try:
        data, dimensions = validate(args.overlay)
    except (ValueError, OSError, UnicodeError, TypeError) as exc:
        parser.exit(1, f'Invalid overlay: {exc}\n')
    print(f"Valid overlay: {len(data['items'])} items, {len(dimensions)} assets")
