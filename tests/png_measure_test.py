"""PNG measurement acceptance plan (declared before implementation).

Verify RGBA pixels for PNG filters 0-4, split IDAT and ancillary chunks;
reject signature/CRC/truncation, duplicate or out-of-order structural chunks,
unsupported color/depth/interlace, invalid dimensions/filter, malformed or
oversized zlib streams and trailing bytes. Check alpha threshold boundaries,
empty sprite rejection, semantic saved JSON and formatted CSS equivalence;
--check must never modify files and must detect changed saved geometry.
"""

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("measure_icons", ROOT / "scripts/measure-icons.py")
MEASURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MEASURE)


def chunk(kind, payload=b""):
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)


def header(width=3, height=2, depth=8, color=6, interlace=0):
    return chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, depth, color, 0, 0, interlace))


def png(raw, width=3, height=2):
    return MEASURE.PNG_SIGNATURE + header(width, height) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND")


def paeth(left, above, diagonal):
    estimate = left + above - diagonal
    distances = [abs(estimate - value) for value in (left, above, diagonal)]
    return (left, above, diagonal)[distances.index(min(distances))]


def filtered(pixels, width, height, filter_type):
    stride = width * 4
    result = bytearray()
    for y in range(height):
        result.append(filter_type)
        for x in range(stride):
            left = pixels[y * stride + x - 4] if x >= 4 else 0
            above = pixels[(y - 1) * stride + x] if y else 0
            diagonal = pixels[(y - 1) * stride + x - 4] if y and x >= 4 else 0
            predictor = (0, left, above, (left + above) // 2, paeth(left, above, diagonal))[filter_type]
            result.append((pixels[y * stride + x] - predictor) & 255)
    return result


class PngDecoderTest(unittest.TestCase):
    def decode(self, data):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.png"
            path.write_bytes(data)
            return MEASURE.read_rgba_png(path)

    def test_all_filters_preserve_rgba(self):
        pixels = bytes([255, 0, 3, 31, 11, 240, 9, 32, 0, 1, 255, 255,
                        250, 5, 4, 0, 10, 249, 7, 128, 250, 249, 0, 254])
        for filter_type in range(5):
            with self.subTest(filter=filter_type):
                self.assertEqual(self.decode(png(filtered(pixels, 3, 2, filter_type))), (3, 2, pixels))

    def test_split_idat_and_ancillary(self):
        raw = b"\0" + bytes(range(12)) + b"\0" + bytes(range(12, 24))
        compressed = zlib.compress(raw)
        data = (MEASURE.PNG_SIGNATURE + header() + chunk(b"tEXt", b"key\0value")
                + chunk(b"PLTE", b"\0\0\0") + chunk(b"IDAT", compressed[:4])
                + chunk(b"IDAT", compressed[4:]) + chunk(b"tEXt", b"after\0yes") + chunk(b"IEND"))
        self.assertEqual(self.decode(data)[2], bytes(range(24)))

    def test_reject_corrupt_signature_crc_and_truncation(self):
        valid = png(bytes(26))
        bad_crc = bytearray(valid)
        bad_crc[29] ^= 1
        for data in (b"bad" + valid[3:], bytes(bad_crc), valid[:-1], valid[:20], valid[:9]):
            with self.subTest(data=data[:16]), self.assertRaises(ValueError):
                self.decode(data)

    def test_reject_structure_errors(self):
        signature = MEASURE.PNG_SIGNATURE
        data_chunk = chunk(b"IDAT", zlib.compress(bytes(26)))
        for chunks in (
            data_chunk + header() + chunk(b"IEND"),
            header() + header() + data_chunk + chunk(b"IEND"),
            header() + data_chunk,
            header() + chunk(b"IEND"),
            header() + data_chunk + chunk(b"IEND", b"bad"),
            header() + data_chunk + chunk(b"IEND") + b"trailing",
            header() + data_chunk + chunk(b"tEXt") + data_chunk + chunk(b"IEND"),
            header() + chunk(b"ABCD") + data_chunk + chunk(b"IEND"),
            header() + chunk(b"abca") + data_chunk + chunk(b"IEND"),
            header() + chunk(b"tRNS") + data_chunk + chunk(b"IEND"),
            header() + chunk(b"PLTE", b"xx") + data_chunk + chunk(b"IEND"),
            header() + data_chunk + chunk(b"PLTE", bytes(3)) + chunk(b"IEND"),
        ):
            with self.subTest(chunks=chunks[:35]), self.assertRaises(ValueError):
                self.decode(signature + chunks)

    def test_reject_formats_and_dimensions(self):
        for options in ({"width": 0}, {"height": 0}, {"width": 0x80000000},
                        {"width": 100000, "height": 100000}, {"depth": 16},
                        {"color": 2}, {"interlace": 1}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.decode(MEASURE.PNG_SIGNATURE + header(**options) + chunk(b"IDAT") + chunk(b"IEND"))

    def test_reject_invalid_filter_or_stream_length(self):
        for raw in (b"\5" + bytes(25), bytes(25), bytes(27), bytes(4096)):
            with self.subTest(length=len(raw)), self.assertRaises(ValueError):
                self.decode(png(raw))
        for compressed in (b"invalid", zlib.compress(bytes(26))[:-1],
                           zlib.compress(bytes(26)) + b"trailing", zlib.compress(bytes(26)) * 2):
            with self.subTest(compressed=compressed), self.assertRaises(ValueError):
                self.decode(MEASURE.PNG_SIGNATURE + header() + chunk(b"IDAT", compressed) + chunk(b"IEND"))

    def test_file_limit(self):
        with patch.object(MEASURE, "MAX_PNG_BYTES", 16):
            with self.assertRaisesRegex(ValueError, "file size"):
                self.decode(png(bytes(26)))

    def test_alpha_threshold_cell_boundaries(self):
        width, height = 1536, 1024
        pixels = bytearray(width * height * 4)
        expected = []
        for i in range(6):
            x, y = (i % 3) * 512, (i // 3) * 512
            pixels[(y * width + x) * 4 + 3] = 31
            pixels[((y + 1) * width + x + 2) * 4 + 3] = 32
            pixels[((y + 511) * width + x + 511) * 4 + 3] = 255
            expected.append([x + 2, y + 1, x + 512, y + 512])
        with patch.object(MEASURE, "read_rgba_png", return_value=(width, height, pixels)):
            self.assertEqual(MEASURE.bounds("unused", "unused.png"), expected)
        with patch.object(MEASURE, "read_rgba_png", return_value=(width, height, bytes(len(pixels)))):
            with self.assertRaisesRegex(ValueError, "Empty sprite"):
                MEASURE.bounds("unused", "unused.png")
        with patch.object(MEASURE, "read_rgba_png", return_value=(1, 1, bytes(4))):
            with self.assertRaisesRegex(ValueError, "1536"):
                MEASURE.bounds("unused", "unused.png")


class GeometryCommandTest(unittest.TestCase):
    def test_explicit_sprite_manifest_requires_six_safe_cells(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = root / "sprite-sources.json"
            group = ["action", ["circle", "square", "diamond", "triangle", "cross", "ring"], "examples"]
            with patch.object(MEASURE, "ROOT", root):
                with self.assertRaisesRegex(FileNotFoundError, "Missing sprite-sources.json"):
                    MEASURE.source_groups()
                config.write_text(json.dumps({"groups": [group]}))
                self.assertEqual(MEASURE.source_groups(), [group])
                for invalid in (["action", group[1][:5], "examples"],
                                ["action", ["circle"] * 6, "examples"],
                                ["action", group[1], "../outside"],
                                ["action", group[1][:-1] + ['bad"selector'], "examples"]):
                    config.write_text(json.dumps({"groups": [invalid]}))
                    with self.assertRaises(ValueError):
                        MEASURE.source_groups()

    def test_real_sources_match_saved_geometry_and_check_writes_nothing(self):
        paths = [ROOT / "demo/icons.css", ROOT / "demo/calibration.json"]
        manifest = json.loads(paths[1].read_text())
        for source in manifest["sources"]:
            paths.append(ROOT / source)
        before = [(path.read_bytes(), path.stat().st_mtime_ns) for path in paths]
        result = subprocess.run([sys.executable, str(ROOT / "scripts/measure-icons.py"), "--check"],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No files changed", result.stdout)
        self.assertEqual(before, [(path.read_bytes(), path.stat().st_mtime_ns) for path in paths])
        for path in paths[2:]:
            key = str(path.relative_to(ROOT))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), manifest["sources"][key])

    def test_check_accepts_formatted_json_rejects_changed_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "demo").mkdir()
            css_path, json_path = root / "demo/icons.css", root / "demo/calibration.json"
            css_path.write_text("fixture CSS\n")
            json_path.write_text('{\n  "value":\n    1\n}\n')
            with patch.object(MEASURE, "ROOT", root), patch.object(MEASURE, "measure", return_value=("fixture CSS\n", {"value": 1})), patch.object(sys, "argv", ["measure", "--check"]):
                before = [p.read_bytes() for p in (css_path, json_path)]
                with contextlib.redirect_stdout(io.StringIO()):
                    MEASURE.main()
                self.assertEqual(before, [p.read_bytes() for p in (css_path, json_path)])
                for path, bad in ((css_path, "changed"), (json_path, '{"value": 2}')):
                    original = path.read_bytes()
                    path.write_text(bad)
                    with self.assertRaisesRegex(ValueError, "differs"):
                        MEASURE.main()
                    self.assertEqual(path.read_text(), bad)
                    path.write_bytes(original)

    def test_default_regenerates_both_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "demo").mkdir()
            with patch.object(MEASURE, "ROOT", root), patch.object(MEASURE, "measure", return_value=("fixture CSS\n", {"value": 1})), patch.object(sys, "argv", ["measure"]), contextlib.redirect_stdout(io.StringIO()):
                MEASURE.main()
            self.assertEqual((root / "demo/icons.css").read_text(), "fixture CSS\n")
            self.assertEqual(json.loads((root / "demo/calibration.json").read_text()), {"value": 1})


if __name__ == "__main__":
    unittest.main()
