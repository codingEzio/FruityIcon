# FruityIcon 幾何工具

量測 PNG 精靈邊界並產生 CSS，包含六個幾何範例；不含原插畫或字型。使用 Pixel
時，請選擇有權使用的字型檔；檔案只在本機讀取、不上傳，重新載入後須再選一次。載入前畫面顯示提示並使用系統字型。

執行
`deno task check`、`deno task test`、`deno task build`、`deno task demo`，開啟
`http://127.0.0.1:18210/demo/`，按 Ctrl-C 停止。需 Deno 2.8+ 與 Python
3.10+；`python3 scripts/generate-examples.py`
可重建範例。替換圖片須自備權利並符合 RGBA PNG 網格格式。

程式與基本範例採 MIT，文件圖示另採 CC BY 4.0。見
[授權範圍](LICENSE-SCOPE.json)、[依賴](DEPENDENCIES.md)與[範例來源](examples/provenance.json)。

附帶的淺色／深色圖表是 1536 × 1024、8 位元 RGBA PNG，以 3 × 2 排列 512 px
格子。解析器接受非交錯 PNG，上限為編碼 16 MiB、解碼 64 MiB。`deno task setup`
檢查已安裝工具且不改 hook；`deno task public:tool` 匯出清單並讀回雜湊與
mode。`python3 scripts/measure-icons.py --check` 檢查產生的 CSS 與校準資料。
