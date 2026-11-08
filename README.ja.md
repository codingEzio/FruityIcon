# FruityIcon 幾何学ツール

PNG スプライトの境界を測り CSS を生成します。6
個の図形サンプルを含み、元のイラストやフォントは含みません。Pixel
には使用権のあるフォントファイルを選択してください。ファイルはローカルでのみ読み込み、送信しません。再読み込み後は再選択が必要です。読み込み前は通知とシステムフォントを表示します。

`deno task check`、`deno task test`、`deno task build`、`deno task demo`
を実行し、`http://127.0.0.1:18210/demo/` を開きます。Ctrl-C で停止します。Deno
2.8+ と Python 3.10+ が必要です。`python3 scripts/generate-examples.py`
でサンプルを再生成できます。差し替え画像の権利と RGBA PNG
グリッド形式は利用者が確認してください。

コードと図形は MIT、文書アイコンは CC BY 4.0
です。[ライセンス](LICENSE-SCOPE.json)・[依存](DEPENDENCIES.md)・[出典](examples/provenance.json)。

付属のライト／ダーク画像は 1536 × 1024、8 ビット RGBA PNG で、512 px のセルを 3
× 2 に配置しています。パーサーは非インターレース PNG に対応し、上限は圧縮 16
MiB、展開 64 MiB です。`deno task setup` はツールを確認し hook
を変更しません。`deno task public:tool` は選定ファイルを書き出してハッシュと
mode を検証します。`python3 scripts/measure-icons.py --check` は生成 CSS
と校正値を確認します。
