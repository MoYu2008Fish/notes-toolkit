# HyperOS / ColorOS ノートツールキット

**[English](README.md)** · **[简体中文](README.zh-CN.md)** · **[繁體中文](README.zh-TW.md)** · **日本語**

Xiaomi・OPPO 系スマートフォンのメモをローカルで書き出したり、両システム間で移行したりするツールです。root 不要、アカウントログイン不要、クラウド経由なし。

| ツール | 用途 |
| --- | --- |
| `hyperos_notes_extract.py` | HyperOS / MIUI のメモ → Markdown + 画像 / 録音 |
| `coloros_notes_extract.py` | ColorOS / realme UI のメモ → Markdown + 画像 / 録音 |
| `hyperos_to_coloros_import.py` | HyperOS の書き出し結果を ColorOS のメモに取り込む |
| `notes_gui.py` | 上記 3 つをまとめた GUI（English / 日本語 / 繁體中文 / 简体中文） |

> すべてのツールはローカルファイルの読み書きと adb 通信のみを行います。ネットワーク接続やデータのアップロードは一切ありません。

## 動作環境

- Python 3.8 以上（GUI には tkinter が必要）
- `adb`（Android platform-tools）が `PATH` に通っていること
- 端末で「USB デバッグ」を有効にし、このコンピュータを許可していること

## クイックスタート（GUI）

全体の流れ：

1. **前提のインストール**：tkinter 付きの Python 3.8 以上と `adb`。
2. **ツールの入手**：`git clone https://github.com/MoYu2008Fish/notes-toolkit.git && cd notes-toolkit`
3. **端末の準備**：「開発者向けオプション → USB デバッグ」を有効にし、USB で接続して許可ダイアログを承認します。`adb devices` に `device` と表示されれば OK です。
4. **端末でローカルバックアップを作成**（メモのみ）：下の第 1 章（Xiaomi）または第 2 章（ColorOS）を参照。
5. **GUI を起動**：`python3 notes_gui.py`（インストール済みなら `notes-toolkit-gui`）。
6. **書き出し**：「HyperOS → Markdown」または「ColorOS → Markdown」タブを開きます。「バックアップ」欄を空にすると端末から最新のバックアップを自動取得します。既存のバックアップを指定することもできます。出力フォルダを決めて **実行** を押し、ログに完了と表示されたら **出力フォルダを開く** で Markdown と添付ファイルを確認します。
7. **ColorOS へ移行（任意）**：「HyperOS → ColorOS」タブに切り替え、手順 6 の HyperOS 書き出しフォルダを選び、「送信後に自動で復元する」にチェックして **実行** を押します。復元は追加動作なので、二重に実行しないでください。
8. **後片付け**：書き出し内容を確認したら、端末上のバックアップを削除します（バックアップは暗号化されていません）。

言語は右上で切り替えられます（初期値はシステム言語）。実行中は **停止** で中断できます。

> tkinter がない場合：macOS（Homebrew）は `brew install python-tk`、Debian/Ubuntu は `sudo apt install python3-tk`。Windows の公式インストーラには同梱されています。

## 1. HyperOS / MIUI のメモ → Markdown

### `adb backup` を使わない理由

Android 13 以降、debuggable でないアプリでは `adb backup` が制限され、Xiaomi メモは空のバックアップになります。そこで Xiaomi 標準の「ローカルバックアップ」を利用します。メモアプリ自身の `NoteBackupAgent` を呼び出すため、完全なデータが得られます。

### 端末側の準備

> Xiaomi のバックアップは初期状態で多くのカテゴリが選択されています。**まずすべて解除し、「メモ」だけを残してください。**

1. `設定 → その他の設定 → バックアップと復元 → 端末のバックアップと復元 → バックアップ` を開く
2. 選択済みのカテゴリをすべて解除し、選択数がどこにも表示されない状態にする
3. 「その他のシステムアプリデータ」を展開し、「メモ」だけにチェック。`500MB 1/25項目` のような表示になることを確認
4. 「今すぐバックアップ」→「続行」→「了解」をタップ
5. 進行画面のキューに**「メモ」だけ**があることを確認。他のアプリが出たらすぐキャンセル

バックアップの場所：

```
/sdcard/MIUI/backup/AllBackup/<日時>/
/sdcard/MIUI/backup/AllBackup/<日時>.zip
```

### コマンドライン

```bash
# 端末の最新バックアップを取得して書き出す
python3 hyperos_notes_extract.py

# 出力フォルダを指定
python3 hyperos_notes_extract.py -o ~/Documents/Notes

# 既存のバックアップ（zip または .bak）を解析
python3 hyperos_notes_extract.py --from-backup ~/Downloads/<日時>.zip
```

その他のオプション：`--keep-backup`（取得したバックアップを残す）、`--delete-device-backup`（完了後に端末側のバックアップを削除、元に戻せません）、`--debug`。

### 出力構成

```
notes_export/
├── notes/
│   ├── タイトル.md
│   └── フォルダ/
│       └── タイトル.md
├── assets/
│   ├── <sha1>.jpg
│   └── <sha1>.mp3
└── notes.json
```

Markdown には YAML ヘッダ（タイトル、作成日時、更新日時、フォルダ）が付き、画像と録音はローカルの相対パスになります。

### 制限事項

- プライベートメモ、デュアルアプリのデータはローカルバックアップの対象外
- ToDo リストは未対応
- 添付ファイルは SHA1 で命名
- 完全に空のメモはスキップ

## 2. ColorOS / realme UI のメモ → Markdown

ColorOS のローカルバックアップも平文です。`rich_note` は JSON で、添付ファイルは `files/file_backup.zip` に入っています。

### 端末側の準備

1. `設定 → アカウントとバックアップ → バックアップと移行 → ローカルバックアップ → 新規バックアップ` を開く
2. すべてのカテゴリを解除し、「システム設定 → メモ」だけにチェック
3. バックアップを開始し、キューに「メモ」だけがあることを確認

バックアップの場所：

```
/sdcard/Android/data/com.coloros.backuprestore/Backup/Data/<日時>/
```

### コマンドライン

```bash
# 端末の最新メモバックアップを取得して書き出す
python3 coloros_notes_extract.py

# 取得済みのバックアップフォルダ（Note/ を含む）を解析
python3 coloros_notes_extract.py --from-backup <バックアップフォルダ>

# 出力フォルダを指定
python3 coloros_notes_extract.py -o ~/Documents/ColorOSNotes
```

### 出力構成

```
coloros_notes_export/
├── notes/
│   ├── タイトル.md
│   └── フォルダ/
│       └── タイトル.md
├── assets/
│   └── <note-id>/
│       ├── <attachment-id>.png
│       └── <attachment-id>.mp3
└── notes.json
```

### 制限事項

- ColorOS のローカルバックアップには画像の `_thumb.png` サムネイルのみが保存され、元画像は含まれません
- プライベートメモ、デュアルアプリのデータは対象外
- 録音と手書きファイルも一緒に書き出されます

## 3. HyperOS → ColorOS 移行

第 1 章で書き出した `notes_export` を ColorOS のローカルバックアップに変換し、ColorOS 標準の「ローカルバックアップ → 復元」で取り込みます。

### 前提条件

- HyperOS の書き出しが完了していること（`notes_export/notes.json` + `assets/`）
- テンプレートとして使う ColorOS メモのローカルバックアップが端末にあること（ツールが最新のものを自動取得することもできます）

### コマンドライン

```bash
python3 hyperos_to_coloros_import.py \
  --export ./notes_export \
  --out ./coloros_import_backup \
  --push --restore
```

| オプション | 説明 |
| --- | --- |
| `--export` | HyperOS の書き出しフォルダ |
| `--template` | ColorOS バックアップのテンプレートフォルダ。省略時は端末から自動取得 |
| `--out` | 生成する ColorOS バックアップのフォルダ |
| `--push` | 生成後に端末へ送信 |
| `--restore` | 送信後にバックアップ画面を開き自動で復元 |
| `--limit N` | 先頭 N 件のみ取り込み（テスト用） |
| `--skip N` | 先頭 N 件をスキップ（途中再開用） |
| `--debug` | メモごとの変換情報を表示 |

### 仕組み

1. `notes_export/notes.json` と `assets/` を読み込む
2. Markdown を ColorOS のリッチテキスト HTML（見出し、太字、リスト、チェックボックス、画像）に変換
3. `localId/attachmentId` をキーに `Note/rich_note` と `Note/files/file_backup.zip` を生成
4. ColorOS バックアップの設定ファイルとテンプレートをコピーして完全なバックアップフォルダを作成
5. adb で送信し、ColorOS の復元機能でメモのデータベースに書き込む

### 制限事項

- **録音は取り込まれません**：ColorOS の録音添付は Xiaomi と形式が異なります。本文には文字起こしが残り、「元の HyperOS 録音は未取り込み」と注記されます
- ColorOS の更新日時は取り込み時刻になります（作成日時は保持）
- 復元は「追加」動作のため、繰り返すとメモが重複します。`--skip` で分割するか、先に端末側を整理してください
- 数百件のメモ・画像は数百 MB のバックアップになり、復元には数分かかります

## コマンドとしてインストール

```bash
pipx install git+https://github.com/MoYu2008Fish/notes-toolkit.git

notes-toolkit-gui      # GUI
hyperos-notes --help
coloros-notes --help
hyperos-to-coloros --help
```

スクリプトを直接ダウンロードして実行することもできます（Python 標準ライブラリのみ使用）。

## プライバシーとセキュリティ

- どのスクリプトも GUI もネットワークに接続せず、データをアップロードしません
- 書き出し先の `notes_export/`、`coloros_notes_export/`、`coloros_import_backup/` は `.gitignore` に入っており、コミットされません
- Xiaomi / ColorOS のローカルバックアップは**暗号化されていません**。バックアップと書き出しファイルは大切に保管してください
- 書き出し後は端末上のローカルバックアップを削除するか、端末バックアップ削除オプションを使うことをおすすめします
- このリポジトリには個人のメモ、アカウント、電話番号、端末識別子は含まれていません

## 開発

```bash
python3 -m py_compile hyperos_notes_extract.py coloros_notes_extract.py hyperos_to_coloros_import.py notes_gui.py
```

コントリビュート歓迎です。issue または pull request をお送りください。GUI の言語を追加するには、`notes_gui.py` の `LANGS` と `STRINGS` に項目を追加します。

## 関連プロジェクト

- [mi-note-export](https://github.com/ceynri/mi-note-export)：Xiaomi クラウド経由の書き出し（メンテナンス終了）
- [mi-note-cli](https://github.com/ceynri/mi-note-cli)：Xiaomi クラウド経由、双方向同期に対応

本プロジェクトはローカルバックアップを使うため、アカウントやクラウドサービスに依存せず、端末のメモを丸ごとコンピュータへ移したい場合に向いています。

## ライセンス

[MIT](LICENSE)
