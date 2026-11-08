"""Rebuild six basic geometric RGBA samples; no reference images or packages."""
from pathlib import Path
import hashlib
import json
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


def generate():
    assets = []
    for theme, color in [('light', (36, 85, 125)), ('dark', (153, 210, 247))]:
        rows = bytearray()
        for y in range(1024):
            rows.append(0)
            for x in range(1536):
                cell = (y // 512) * 3 + x // 512
                dx, dy = x % 512 - 256, y % 512 - 256
                ax, ay = abs(dx), abs(dy)
                inside = [dx * dx + dy * dy <= 140 ** 2,
                          max(ax, ay) <= 130,
                          ax + ay <= 180,
                          -145 <= dy <= 145 and ax <= (dy + 145) / 2,
                          max(ax, ay) <= 155 and min(ax, ay) <= 42,
                          100 ** 2 <= dx * dx + dy * dy <= 150 ** 2][cell]
                rows.extend((*color, 255) if inside else (0, 0, 0, 0))
        data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1536, 1024, 8, 6, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))
        name = f'examples/actions-{theme}.png'
        (ROOT / name).write_bytes(data)
        assets.append({'file': name, 'sha256': hashlib.sha256(data).hexdigest()})
    (ROOT / 'examples/provenance.json').write_text(json.dumps({
        'schemaVersion': 1, 'method': 'Deterministic integer-coordinate geometric predicates; source scripts/generate-examples.py.',
        'referenceImages': [], 'license': 'MIT', 'metadata': 'Only PNG IHDR, IDAT and IEND chunks; no original-image bytes or metadata used.',
        'assets': assets}, indent=2) + '\n')


if __name__ == '__main__':
    generate()
