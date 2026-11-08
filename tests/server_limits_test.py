import http.client
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import socket
import subprocess
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent


class ServerLimitsTest(unittest.TestCase):
    def test_concurrent_public_assets_load(self):
        for script in ('public-server.py', 'gallery-server.py'):
            with self.subTest(script=script):
                proc = subprocess.Popen(['python3', str(ROOT / 'scripts' / script), '--port', '0'],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                try:
                    line = proc.stdout.readline()
                    port = int(re.search(r'127\.0\.0\.1:(\d+)', line).group(1))
                    def get(path):
                        conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
                        conn.request('GET', path)
                        response = conn.getresponse()
                        status = response.status
                        response.read()
                        conn.close()
                        return status
                    paths = ['/demo/', '/demo/app.js', '/demo/demo.css', '/demo/icons.css',
                             '/examples/actions-light.png', '/examples/actions-dark.png']
                    with ThreadPoolExecutor(max_workers=6) as pool:
                        self.assertEqual(list(pool.map(get, paths)), [200] * len(paths))
                finally:
                    proc.terminate()
                    proc.wait(timeout=5)
                    proc.stdout.close()
                    proc.stderr.close()

    def test_both_servers_bound_slow_requests_and_recover(self):
        for script in ('public-server.py', 'gallery-server.py'):
            with self.subTest(script=script):
                proc = subprocess.Popen(['python3', str(ROOT / 'scripts' / script), '--port', '0',
                                         '--connections', '2', '--timeout', '0.5'],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                clients = []
                try:
                    line = proc.stdout.readline()
                    self.assertTrue(line, proc.stderr.read() if proc.poll() is not None else 'no startup line')
                    port = int(re.search(r'127\.0\.0\.1:(\d+)', line).group(1))
                    for _ in range(2):
                        s = socket.create_connection(('127.0.0.1', port), timeout=2)
                        s.sendall(b'GET /demo/ HTTP/1.1\r\nHost: localhost\r\nX-Test: ')
                        clients.append(s)
                    extra = socket.create_connection(('127.0.0.1', port), timeout=2)
                    try:
                        extra.settimeout(1)
                        extra.sendall(b'GET /demo/ HTTP/1.1\r\nHost: localhost\r\n\r\n')
                        try:
                            self.assertEqual(extra.recv(1), b'')
                        except ConnectionResetError:
                            pass
                    finally:
                        extra.close()
                    # Each byte arrives within the idle timeout; total request lifetime remains bounded.
                    deadline = time.monotonic() + 0.9
                    while time.monotonic() < deadline:
                        for client in clients:
                            try:
                                client.sendall(b'x')
                            except OSError:
                                pass
                        time.sleep(0.1)
                    for client in clients:
                        client.settimeout(1)
                        try:
                            self.assertEqual(client.recv(1), b'')
                        except ConnectionResetError:
                            pass
                    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=2)
                    conn.request('GET', '/demo/')
                    response = conn.getresponse()
                    self.assertEqual(response.status, 200)
                    response.read()
                    conn.close()
                finally:
                    for client in clients:
                        client.close()
                    proc.terminate()
                    proc.wait(timeout=5)
                    proc.stdout.close()
                    proc.stderr.close()


if __name__ == '__main__':
    unittest.main()
