"""Measure alpha bounds and emit CSS sprite geometry; never change PNG pixels."""

from pathlib import Path
import hashlib
import json
import argparse
import re
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
THRESHOLD = 32
FILL = 0.86


# Bound both file input and decoded storage; generated sheets use about 6 MiB.
MAX_PNG_BYTES = 16 * 1024 * 1024
MAX_DECODED_BYTES = 64 * 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_rgba_png(path):
    """Decode non-interlaced 8-bit RGBA PNGs without external packages.

    This is the format of the original generated sheets. Validate CRCs and
    structure before decoding; reject other formats rather than reinterpret
    their channels or silently change the measurement.
    """
    with Path(path).open("rb") as source:
        data = source.read(MAX_PNG_BYTES + 1)
    if len(data) > MAX_PNG_BYTES:
        raise ValueError("PNG exceeds file size limit")
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("Invalid PNG signature")
    offset = len(PNG_SIGNATURE)
    width = height = None
    compressed = bytearray()
    seen_idat = ended_idat = seen_plte = seen_iend = False
    while offset < len(data):
        if len(data) - offset < 12:
            raise ValueError("Truncated PNG chunk")
        length, kind = struct.unpack_from(">I4s", data, offset)
        end = offset + 12 + length
        if end > len(data):
            raise ValueError("Truncated PNG chunk payload")
        if any(not (65 <= c <= 90 or 97 <= c <= 122) for c in kind) or kind[2] & 32:
            raise ValueError("Invalid PNG chunk type")
        payload = memoryview(data)[offset + 8:end - 4]
        checksum = struct.unpack_from(">I", data, end - 4)[0]
        if zlib.crc32(payload, zlib.crc32(kind)) & 0xffffffff != checksum:
            raise ValueError("PNG chunk CRC mismatch")
        if width is None and kind != b"IHDR":
            raise ValueError("IHDR must be the first PNG chunk")
        if kind == b"IHDR":
            if width is not None or length != 13:
                raise ValueError("Invalid or duplicate PNG IHDR")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if width == 0 or height == 0 or width > 0x7fffffff or height > 0x7fffffff:
                raise ValueError("Invalid PNG dimensions")
            if (width * 4 + 1) * height > MAX_DECODED_BYTES:
                raise ValueError("PNG dimensions exceed decoded size limit")
            if (depth, color, compression, filtering, interlace) != (8, 6, 0, 0, 0):
                raise ValueError("Expected non-interlaced 8-bit RGBA PNG")
        elif kind == b"IDAT":
            if ended_idat:
                raise ValueError("PNG IDAT chunks must be consecutive")
            seen_idat = True
            compressed.extend(payload)
        elif kind == b"IEND":
            if length != 0 or not seen_idat or end != len(data):
                raise ValueError("Invalid PNG IEND or trailing data")
            seen_iend = True
            break
        elif kind == b"PLTE":
            if seen_plte or seen_idat or not 0 < length <= 768 or length % 3:
                raise ValueError("Invalid PNG palette")
            seen_plte = True
        elif kind == b"tRNS":
            raise ValueError("RGBA PNG must not contain tRNS")
        elif not kind[0] & 32:
            raise ValueError("Unknown critical PNG chunk")
        if seen_idat and kind != b"IDAT":
            ended_idat = True
        offset = end
    if not seen_iend:
        raise ValueError("Missing PNG IEND")
    stride = width * 4
    expected = (stride + 1) * height
    decoder = zlib.decompressobj()
    try:
        raw = decoder.decompress(compressed, expected + 1)
    except zlib.error as error:
        raise ValueError("Invalid PNG compressed data") from error
    if len(raw) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError("PNG decoded length or compressed stream is invalid")
    pixels = bytearray(stride * height)
    for y in range(height):
        source_start = y * (stride + 1)
        filter_type = raw[source_start]
        if filter_type > 4:
            raise ValueError("Invalid PNG row filter")
        row = bytearray(raw[source_start + 1:source_start + 1 + stride])
        previous_start = (y - 1) * stride
        if filter_type:
            for x in range(stride):
                left = row[x - 4] if x >= 4 else 0
                above = pixels[previous_start + x] if y else 0
                upper_left = pixels[previous_start + x - 4] if y and x >= 4 else 0
                if filter_type == 1:
                    predictor = left
                elif filter_type == 2:
                    predictor = above
                elif filter_type == 3:
                    predictor = (left + above) // 2
                else:
                    estimate = left + above - upper_left
                    distances = (abs(estimate - left), abs(estimate - above), abs(estimate - upper_left))
                    predictor = (left, above, upper_left)[distances.index(min(distances))]
                row[x] = (row[x] + predictor) & 255
        pixels[y * stride:(y + 1) * stride] = row
    return width, height, pixels


def bounds(batch, filename):
    width, height, pixels = read_rgba_png(ROOT / batch / filename)
    if (width, height) != (1536, 1024):
        raise ValueError("Expected 1536 x 1024 sprite sheet")
    result = []
    for i in range(6):
        x, y = (i % 3) * 512, (i // 3) * 512
        left, top, right, bottom = x + 512, y + 512, x, y
        for py in range(y, y + 512):
            for px in range(x, x + 512):
                if pixels[(py * width + px) * 4 + 3] >= THRESHOLD:
                    left, top = min(left, px), min(top, py)
                    right, bottom = max(right, px + 1), max(bottom, py + 1)
        if right <= left or bottom <= top:
            raise ValueError(f"Empty sprite cell {i} in {filename}")
        result.append([left, top, right, bottom])
    return result

def source_groups():
    config = ROOT / "sprite-sources.json"
    if not config.is_file():
        raise FileNotFoundError("Missing sprite-sources.json; restore the sprite source configuration")
    groups = json.loads(config.read_text())["groups"]
    if not isinstance(groups, list) or not groups:
        raise ValueError("Sprite source groups must be a nonempty list")
    seen = set()
    for group in groups:
        if not isinstance(group, list) or len(group) != 3:
            raise ValueError("Each sprite group needs kind, six IDs and a directory")
        kind, names, batch = group
        if kind not in ("action", "produce") or not isinstance(names, list) or len(names) != 6:
            raise ValueError("Each action/produce sheet must name six cells")
        if not isinstance(batch, str) or not batch or Path(batch).is_absolute() or any(part in (".", "..") for part in batch.split("/")) or "\\" in batch:
            raise ValueError("Sprite directory must be relative to the source root")
        if not (ROOT / batch).resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("Sprite directory resolves outside the source root")
        for name in names:
            if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", name) or (kind, name) in seen:
                raise ValueError("Sprite IDs must be unique safe CSS identifiers")
            seen.add((kind, name))
    return groups


def measure():
    css = ["/* Generated by scripts/measure-icons.py. PNG pixels are unchanged. */"]
    records = []
    sources = {}
    for kind, names, batch in source_groups():
        filenames = ["actions-light.png", "actions-dark.png"] if kind == "action" else ["produce-explorations.png"]
        boxes = bounds(batch, filenames[0])
        if kind == "action":
            dark = bounds(batch, filenames[1])
            boxes = [[min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])] for a, b in zip(boxes, dark)]
        for filename in filenames:
            key = batch + "/" + filename
            sources[key] = hashlib.sha256((ROOT / batch / filename).read_bytes()).hexdigest()
        for i, (name, box) in enumerate(zip(names, boxes)):
            left, top, right, bottom = box
            side = max(right - left, bottom - top)
            cx, cy = (left + right) / 2, (top + bottom) / 2
            values = {
                "sprite-w": 1536 / side * FILL,
                "sprite-h": 1024 / side * FILL,
                "sprite-x": 0.5 - cx / side * FILL,
                "sprite-y": 0.5 - cy / side * FILL,
                "col": i % 3,
                "row": i // 3,
                "clip-top": max(0, 0.5 + ((i // 3) * 512 - cy) / side * FILL),
                "clip-right": max(0, 0.5 - (((i % 3) + 1) * 512 - cx) / side * FILL),
                "clip-bottom": max(0, 0.5 - (((i // 3) + 1) * 512 - cy) / side * FILL),
                "clip-left": max(0, 0.5 + ((i % 3) * 512 - cx) / side * FILL),
            }
            css.append(f'.fruity[data-{kind}="{name}"] {{')
            css.extend(f"  --{key}: {value:.8f};" for key, value in values.items())
            css.append("}")
            records.append({"kind": kind, "id": name, "batch": batch, "bounds": box, "maxSide": side, "css": values})

    manifest = {
        "schemaVersion": 1,
        "alphaThreshold": THRESHOLD,
        "opticalFill": FILL,
        "decisions": {
            "alphaThreshold": "Ignore very faint edge pigment when measuring occupied shape.",
            "opticalFill": "Leave 7 percent padding on each side of the dominant dimension.",
            "themeUnion": "Use the union of both action palettes to avoid layout shifts on theme changes.",
        },
        "sources": sources,
        "items": records,
    }
    return "\n".join(css) + "\n", manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check saved geometry without writing any files")
    args = parser.parse_args()
    css, manifest = measure()
    css_path = ROOT / "demo/icons.css"
    manifest_path = ROOT / "demo/calibration.json"
    if args.check:
        # JSON formatting does not affect geometry; preserve repository formatting.
        if css_path.read_text() != css or json.loads(manifest_path.read_text()) != manifest:
            raise ValueError("Saved sprite geometry differs; run scripts/measure-icons.py to regenerate")
        print(f"Checked {len(manifest.get('items', []))} sprite shapes; saved CSS and calibration match. No files changed.")
    else:
        css_path.write_text(css)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"Measured {len(manifest.get('items', []))} sprite shapes; wrote CSS and calibration, without editing images.")


if __name__ == "__main__":
    main()
