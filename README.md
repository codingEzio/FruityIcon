# FruityIcon geometry tools

Measure PNG sprite bounds and generate CSS using the six included geometric
examples. The original illustrations and all fonts are excluded. Pixel display
requires a font file you have rights to use: select Pixel, then choose the file.
It is read locally, is not uploaded, and must be selected again after reload.
Until it loads, the page shows a status and uses the system font.

Run `deno task check`, `deno task test`, `deno task build`, and
`deno task demo`; open `http://127.0.0.1:18210/demo/`. Stop the server with
Ctrl-C. Deno 2.8+ and Python 3.10+ are required.
`python3 scripts/generate-examples.py` regenerates the examples.
`sprite-sources.json` selects the examples used by the measurement tool. When
replacing images, supply your own rights and the documented RGBA PNG grid
format.

The code and basic examples use MIT; the documentation icon has its own CC BY
4.0 grant. See [LICENSE-SCOPE.json](LICENSE-SCOPE.json),
[DEPENDENCIES.md](DEPENDENCIES.md) and
[example provenance](examples/provenance.json).

The supplied light/dark sheets are 1536 × 1024, 8-bit RGBA PNGs, arranged as a 3
× 2 grid of 512 px cells. The parser accepts non-interlaced PNG and limits
inputs to 16 MiB encoded and 64 MiB decoded. `deno task setup` checks installed
tools without changing hooks; `deno task public:tool` exports the allowlist with
hash and mode readback. `python3 scripts/measure-icons.py --check` checks
generated CSS and calibration.
