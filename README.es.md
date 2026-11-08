# Herramientas geométricas FruityIcon

Mide límites de sprites PNG y genera CSS con seis ejemplos geométricos. No
incluye ilustraciones originales ni fuentes. Para Pixel, seleccione una fuente
que tenga derecho a usar. El archivo se lee localmente y no se sube; debe
seleccionarse de nuevo al recargar. Hasta que se cargue se muestra un aviso y se
usa la fuente del sistema.

Ejecute `deno task check`, `deno task test`, `deno task build` y
`deno task demo`; abra `http://127.0.0.1:18210/demo/` y detenga con Ctrl-C. Se
necesitan Deno 2.8+ y Python 3.10+. `python3 scripts/generate-examples.py`
regenera los ejemplos. Las imágenes de reemplazo requieren derechos propios y el
formato de cuadrícula PNG RGBA.

La demo local solo sirve los archivos públicos necesarios leídos al iniciar.

El código y los ejemplos básicos usan MIT; el icono de documentación usa CC BY
4.0. Consulte [licencia](LICENSE-SCOPE.json), [dependencias](DEPENDENCIES.md) y
[origen](examples/provenance.json).

Las hojas clara y oscura son PNG RGBA de 8 bits, 1536 × 1024, con una cuadrícula
de 3 × 2 celdas de 512 px. El parser acepta PNG no entrelazado y limita la
entrada a 16 MiB codificados y 64 MiB decodificados. `deno task setup` comprueba
las herramientas sin cambiar hooks; `deno task public:tool` exporta la lista y
verifica hash y mode. `python3 scripts/measure-icons.py --check` comprueba CSS y
calibración generados.
