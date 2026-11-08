# FruityIcon 几何工具

测量 PNG 精灵边界并生成 CSS，包含六个几何示例；不含原插画或字体。使用 Pixel
时，请选择有权使用的字体文件；文件只在本地读取、不上传，重新加载后须再次选择。加载前页面显示提示并使用系统字体。

运行
`deno task check`、`deno task test`、`deno task build`、`deno task demo`，打开
`http://127.0.0.1:18210/demo/`，按 Ctrl-C 停止。需 Deno 2.8+ 与 Python
3.10+；`python3 scripts/generate-examples.py`
可重建示例。替换图片须自备权利并符合 RGBA PNG 网格格式。

本地 demo 只提供启动时快照中的必要公开文件。

程序和基本示例采用 MIT，文档图标另采用 CC BY
4.0。参见[许可范围](LICENSE-SCOPE.json)、[依赖](DEPENDENCIES.md)和[示例来源](examples/provenance.json)。

随附的浅色／深色图表为 1536 × 1024、8 位 RGBA PNG，以 3 × 2 排列 512 px
单元。解析器接受非交错 PNG，上限为编码 16 MiB、解码 64 MiB。`deno task setup`
检查已安装工具且不改 hook；`deno task public:tool` 导出清单并读回哈希与
mode。`python3 scripts/measure-icons.py --check` 检查生成的 CSS 与校准数据。
