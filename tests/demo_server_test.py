import http.client
import importlib.util
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer

spec = importlib.util.spec_from_file_location('demo_server', Path(__file__).resolve().parents[1] / 'scripts/demo-server.py')
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class DemoServerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for path in demo.FILES:
            file = self.root / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(('public:' + path).encode())
        for path in ('.git/synthetic-marker', 'Local/synthetic-marker'):
            file = self.root / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('private')

    def tearDown(self):
        self.temp.cleanup()

    def test_http_snapshot_and_boundaries(self):
        files = demo.snapshot(self.root)
        (self.root / 'demo/app.js').unlink()
        (self.root / 'demo/app.js').symlink_to(self.root / 'Local/synthetic-marker')
        server = ThreadingHTTPServer(('127.0.0.1', 0), demo.handler_for(files, 0))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            def get(path, host='localhost'):
                conn = http.client.HTTPConnection('127.0.0.1', server.server_port)
                conn.request('GET', path, headers={'Host': host})
                response = conn.getresponse()
                result = response.status, response.read()
                conn.close()
                return result
            for path in ('/demo/', *('/' + p for p in demo.FILES)):
                self.assertEqual(get(path)[0], 200, path)
            self.assertEqual(get('/demo/app.js')[1], b'public:demo/app.js')
            for path in ('/.git/synthetic-marker', '/Local/synthetic-marker',
                         '/demo/%2e%2e/Local/synthetic-marker', '/demo/%2e%2e%2fLocal/synthetic-marker'):
                self.assertEqual(get(path)[0], 404, path)
            for host in ('attacker.example', 'localhost.attacker.example', '127.0.0.1.attacker.example'):
                self.assertEqual(get('/demo/', host)[0], 400, host)
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

    def test_symlink_and_oversized_file_rejected_at_startup(self):
        path = self.root / 'demo/app.js'
        path.unlink()
        path.symlink_to(self.root / 'Local/synthetic-marker')
        with self.assertRaises(OSError):
            demo.snapshot(self.root)
        path.unlink()
        with path.open('wb') as file:
            file.truncate(demo.MAX_FILE + 1)
        with self.assertRaises(ValueError):
            demo.snapshot(self.root)
        path.unlink()
        path.write_text('safe')
        (self.root / 'examples').rename(self.root / 'moved')
        (self.root / 'examples').symlink_to(self.root / 'moved', target_is_directory=True)
        with self.assertRaises(OSError):
            demo.snapshot(self.root)


if __name__ == '__main__':
    unittest.main()
