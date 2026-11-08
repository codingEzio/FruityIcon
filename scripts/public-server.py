"""Run the reviewed public snapshot through bounded loopback serving."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


if __name__ == '__main__':
    demo = module('demo_server', ROOT / 'scripts/demo-server.py')
    runtime = module('server_runtime', ROOT / 'scripts/server-runtime.py')
    parser = argparse.ArgumentParser()
    runtime.add_limits(parser)
    args = parser.parse_args()
    runtime.validate_limits(args)
    files = demo.snapshot(ROOT)
    with runtime.BoundedHTTPServer(('127.0.0.1', args.port), demo.handler_for(files, args.port),
                                   connections=args.connections, timeout=args.timeout) as server:
        server.RequestHandlerClass = demo.handler_for(files, server.server_port)
        print(f'Demo: http://127.0.0.1:{server.server_port}/demo/', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
