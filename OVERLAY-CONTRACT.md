# Local gallery data

The optional gallery reads data only; it does not execute code from the overlay.
The public geometry tool works without it. Start with no overlay to see the
empty state, or pass a local directory explicitly:

```sh
python3 scripts/validate-overlay.py /path/to/overlay
python3 -B scripts/gallery-server.py --port 18210 --overlay /path/to/overlay
```

Open `http://127.0.0.1:18210/gallery/`. The server binds loopback and accepts
only localhost Host headers. It caches the selected overlay in memory at start;
restart after editing it. Only the validated catalog, referenced PNG sheets and
optional `font.woff2` are exposed. Avoid using an overlay with untrusted local
writers. Keep private data outside Git and retain the original source/history.

The directory contains `catalog.json`, `assets/<id>.png`, and optional
`font.woff2`. Version 1 catalog fields are `version`, `categories`, `items`.
Categories map ASCII identifiers to labels for `en`, `zh-Hans`, `zh-Hant`. Each
item has a unique `id`, `labels` in those three languages, a `category`,
`description` in the same three languages, `assets` with `light` and `dark` PNG
identifiers, `rect` and `cell` with integer x, y, width, height in pixels, and a
boolean `monochrome` flag. The fit control switches between rect and cell. IDs
contain lowercase ASCII letters, digits, hyphens and underscores. The validator
enforces size limits, PNG header and bounds; it does not prove full image
integrity, rights or font validity.

# 本機圖庫資料

圖庫選用資料目錄；公開幾何工具不依賴素材。以上命令會先驗證資料，
再以本機伺服器開啟圖庫。`catalog.json` 保存三語名稱、分類、淺深色 素材 ID
與裁切座標；PNG 放在 `assets/`，字型為選用的 `font.woff2`。 私人資料保留於 Git
以外，原始資料及歷史也需保留。

# 本地图集数据

图集使用可选数据目录；公开几何工具不依赖素材。以上命令先验证数据，
再以本机服务器打开图集。`catalog.json` 保存三语名称、分类、浅深色 素材 ID
和裁切坐标；PNG 放在 `assets/`，字体为可选的 `font.woff2`。 私人数据保留在 Git
以外，也需保留原始数据和历史。

## Preferences and comparisons

The gallery can import the earlier demo preferences from the same browser origin
without deleting them. For a different origin, export that origin's
`fruity.demo.preferences.v1` localStorage value as a JSON file and choose it in
the gallery. Import is explicit and validates the file before changing gallery
preferences; export creates a JSON download. Samples and favorites reset on
reload. Overlay items also carry eight optical geometry values and an optional
comparison symbol ID (1–12); symbols are generic authored SVG geometry.

偏好可由相同瀏覽器來源明確匯入；不同來源可先匯出舊版
`fruity.demo.preferences.v1` 為 JSON，再選取檔案。舊偏好不會刪除。

偏好可从相同浏览器来源明确导入；不同来源可先导出旧版
`fruity.demo.preferences.v1` 为 JSON，再选择文件。旧偏好不会删除。
