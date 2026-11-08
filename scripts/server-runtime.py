"""Bound loopback server connections and per-request idle time."""
import socket
import threading
from http.server import ThreadingHTTPServer

DEFAULT_CONNECTIONS = 16
DEFAULT_TIMEOUT = 5.0


class BoundedHTTPServer(ThreadingHTTPServer):
    def __init__(self, address, handler, *, connections=DEFAULT_CONNECTIONS, timeout=DEFAULT_TIMEOUT):
        self.slots = threading.BoundedSemaphore(connections)
        self.request_timeout = timeout
        super().__init__(address, handler)

    def get_request(self):
        request, address = super().get_request()
        request.settimeout(self.request_timeout)
        return request, address

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        def expire():
            try:
                request.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        deadline = threading.Timer(self.request_timeout, expire)
        deadline.daemon = True
        deadline.start()
        try:
            super().process_request_thread(request, client_address)
        finally:
            deadline.cancel()
            self.slots.release()


def add_limits(parser):
    parser.add_argument('--port', type=int, default=18210)
    parser.add_argument('--connections', type=int, default=DEFAULT_CONNECTIONS)
    parser.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT)


def validate_limits(args):
    if not 0 <= args.port <= 65535 or not 1 <= args.connections <= 128 or not 0.1 <= args.timeout <= 120:
        raise ValueError('Invalid port, connection limit or timeout')
