import http.client
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class GalleryServerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.path.realpath(tempfile.gettempdir()))
        self.root = Path(self.temp.name)
        (self.root / 'assets').mkdir()
        shutil.copyfile(ROOT / 'examples/actions-light.png', self.root / 'assets/sheet.png')
        labels = {'en': 'Example', 'zh-Hans': '示例', 'zh-Hant': '範例'}
        data = {'version': 1, 'categories': {'sample': labels}, 'items': [
            {'id': 'item', 'labels': labels, 'category': 'sample',
             'assets': {'light': 'sheet', 'dark': 'sheet'}, 'rect': [0, 0, 100, 100], 'cell': [0, 0, 100, 100], 'monochrome': True, 'description': labels, 'optical': [3, 2, 0, 0, 0, 0, 0, 0], 'symbol': '1'}]}
        data['items'] = [dict(data['items'][0], id=f'item-{i}') for i in range(18)]
        data['items'][1]['aliases'] = ['old-example']
        data['toolbar'] = {role: f'item-{i}' for i, role in enumerate(('search', 'add', 'favorite', 'upload', 'download', 'settings'))}
        (self.root / 'catalog.json').write_text(json.dumps(data))
        self.proc = None

    def tearDown(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=5)
            self.proc.stdout.close()
            self.proc.stderr.close()
        self.temp.cleanup()

    def start(self, *args):
        self.proc = subprocess.Popen(['python3', str(ROOT / 'scripts/gallery-server.py'), '--port', '0', *args],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        line = self.proc.stdout.readline()
        if not line:
            raise AssertionError(self.proc.stderr.read())
        return int(re.search(r'127\.0\.0\.1:(\d+)', line).group(1))

    def request(self, port, path, host=None):
        conn = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
        conn.request('GET', path, headers={'Host': host or f'127.0.0.1:{port}'})
        response = conn.getresponse()
        result = response.status, response.read()
        conn.close()
        return result

    def test_default_server_does_not_expose_private_data(self):
        port = self.start()
        self.assertEqual(self.request(port, '/gallery/')[0], 200)
        self.assertEqual(self.request(port, '/')[0], 200)
        self.assertEqual(self.request(port, '/index.html')[0], 200)
        self.assertEqual(self.request(port, '/gallery.js')[0], 200)
        self.assertEqual(self.request(port, '/health')[0], 200)
        self.assertEqual(self.request(port, '/overlay/catalog.json')[0], 404)
        self.assertEqual(self.request(port, '/.git/config')[0], 404)
        self.assertEqual(self.request(port, '/gallery/', f'attacker.example:{port}')[0], 400)

    def test_overlay_and_host_restriction(self):
        port = self.start('--overlay', str(self.root))
        status, body = self.request(port, '/overlay/catalog.json')
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(body)['items']), 18)
        self.assertEqual(self.request(port, '/overlay/assets/sheet.png')[0], 200)
        self.assertEqual(self.request(port, '/overlay/catalog.json', f'attacker.example:{port}')[0], 400)
        self.assertEqual(self.request(port, '/overlay/assets/%2e%2e/catalog.json')[0], 404)

    def test_rejects_asset_symlink(self):
        target = self.root / 'assets/sheet.png'
        target.unlink()
        target.symlink_to(ROOT / 'examples/actions-light.png')
        p = subprocess.run(['python3', str(ROOT / 'scripts/gallery-server.py'), '--port', '0', '--overlay', str(self.root)],
                           capture_output=True, text=True, timeout=5)
        self.assertNotEqual(p.returncode, 0)

    def test_previous_catalog_without_toolbar_remains_supported(self):
        path = self.root / 'catalog.json'
        data = json.loads(path.read_text())
        del data['toolbar']
        path.write_text(json.dumps(data))
        port = self.start('--overlay', str(self.root))
        status, body = self.request(port, '/overlay/catalog.json')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['toolbar'], {})

    def test_duplicate_legacy_alias_rejected(self):
        path = self.root / 'catalog.json'
        data = json.loads(path.read_text())
        data['items'][2]['aliases'] = ['old-example']
        path.write_text(json.dumps(data))
        p = subprocess.run(['python3', str(ROOT / 'scripts/gallery-server.py'), '--port', '0', '--overlay', str(self.root)],
                           capture_output=True, text=True, timeout=5)
        self.assertNotEqual(p.returncode, 0)

    def test_alias_cannot_shadow_current_id(self):
        path = self.root / 'catalog.json'
        data = json.loads(path.read_text())
        data['items'][1]['aliases'] = ['item-0']
        path.write_text(json.dumps(data))
        p = subprocess.run(['python3', str(ROOT / 'scripts/gallery-server.py'), '--port', '0', '--overlay', str(self.root)],
                           capture_output=True, text=True, timeout=5)
        self.assertNotEqual(p.returncode, 0)

    def test_unknown_toolbar_item_rejected(self):
        path = self.root / 'catalog.json'
        data = json.loads(path.read_text())
        data['toolbar']['download'] = 'not-in-catalog'
        path.write_text(json.dumps(data))
        p = subprocess.run(['python3', str(ROOT / 'scripts/gallery-server.py'), '--port', '0', '--overlay', str(self.root)],
                           capture_output=True, text=True, timeout=5)
        self.assertNotEqual(p.returncode, 0)

    def test_invalid_optical_geometry_rejected(self):
        path = self.root / 'catalog.json'
        data = json.loads(path.read_text())
        data['items'][0]['optical'][4:8] = [0, 0.6, 0, 0.6]
        path.write_text(json.dumps(data))
        p = subprocess.run(['python3', str(ROOT / 'scripts/gallery-server.py'), '--port', '0', '--overlay', str(self.root)],
                           capture_output=True, text=True, timeout=5)
        self.assertNotEqual(p.returncode, 0)

    def test_rejects_fifo_without_blocking(self):
        for relative in ('catalog.json', 'assets/sheet.png', 'font.woff2'):
            with self.subTest(relative=relative):
                path = self.root / relative
                if path.exists():
                    original = path.read_bytes()
                    path.unlink()
                else:
                    original = None
                os.mkfifo(path)
                try:
                    p = subprocess.run(['python3', str(ROOT / 'scripts/gallery-server.py'), '--port', '0', '--overlay', str(self.root)],
                                       capture_output=True, text=True, timeout=5)
                    self.assertNotEqual(p.returncode, 0)
                finally:
                    path.unlink()
                    if original is not None:
                        path.write_bytes(original)

    def test_serves_validated_snapshot_after_disk_change(self):
        port = self.start('--overlay', str(self.root))
        status, original = self.request(port, '/overlay/assets/sheet.png')
        self.assertEqual(status, 200)
        (self.root / 'assets/sheet.png').write_bytes(b'changed')
        self.assertEqual(self.request(port, '/overlay/assets/sheet.png')[1], original)

    def test_rejects_ancestor_symlink(self):
        link = self.root.parent / (self.root.name + '-link')
        link.symlink_to(self.root, target_is_directory=True)
        try:
            p = subprocess.run(['python3', str(ROOT / 'scripts/gallery-server.py'), '--port', '0', '--overlay', str(link)],
                               capture_output=True, text=True, timeout=5)
            self.assertNotEqual(p.returncode, 0)
        finally:
            link.unlink()


if __name__ == '__main__':
    unittest.main()
