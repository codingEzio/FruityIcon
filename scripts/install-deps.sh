#!/bin/sh
set -eu
# Check only; never install packages, change Git configuration or contact a host.
command -v deno >/dev/null 2>&1 || { printf '%s\n' 'Deno 2.8+ required: brew install deno (macOS)' >&2; exit 69; }
command -v python3 >/dev/null 2>&1 || { printf '%s\n' 'Python 3.10+ required: brew install python (macOS)' >&2; exit 69; }
deno eval 'const [major, minor] = Deno.version.deno.split(".").map(Number); if (major < 2 || (major === 2 && minor < 8)) throw Error("Deno 2.8+ required"); console.log(`Deno ${Deno.version.deno}`)'
python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"; print("Python " + sys.version.split()[0])'
printf '%s\n' 'No packages or credentials downloaded. Optional version control: git init.'
