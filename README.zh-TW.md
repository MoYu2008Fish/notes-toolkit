# HyperOS / ColorOS 便籤工具箱

**[English](README.md)** · **[简体中文](README.zh-CN.md)** · **繁體中文** · **[日本語](README.ja.md)**

在本機匯出小米、OPPO 系手機的便籤，或在兩個系統之間遷移。無需 root、無需登入帳號、不經過雲端。

| 工具 | 用途 |
| --- | --- |
| `hyperos_notes_extract.py` | HyperOS / MIUI 便籤 → Markdown + 圖片 / 錄音 |
| `coloros_notes_extract.py` | ColorOS / realme UI 便籤 → Markdown + 圖片 / 錄音 |
| `hyperos_to_coloros_import.py` | 將 HyperOS 匯出結果匯入 ColorOS 便籤 |
| `notes_gui.py` | 圖形介面（English / 日本語 / 繁體中文 / 简体中文），封裝以上三個工具 |

> 所有工具只讀寫本機檔案並透過 adb 與手機通訊，不連網、不上傳任何資料。

## 環境需求

- Python 3.8+（圖形介面需要 tkinter）
- `adb`（Android platform-tools），並加入 `PATH`
- 手機開啟「USB 偵錯」，並允許目前這台電腦

## 快速上手（圖形介面）

完整流程：

1. **安裝相依項目**：Python 3.8+（含 tkinter）與 `adb`。
2. **取得工具**：`git clone https://github.com/MoYu2008Fish/notes-toolkit.git && cd notes-toolkit`
3. **手機端**：開啟「開發人員選項 → USB 偵錯」，以傳輸線連接電腦並允許偵錯授權；`adb devices` 應顯示 `device`。
4. **在手機上建立本機備份**，只備份便籤：請見下方第一或第二節。
5. **啟動介面**：`python3 notes_gui.py`（安裝後也可執行 `notes-toolkit-gui`）。
6. **匯出**：選擇「HyperOS → Markdown」或「ColorOS → Markdown」分頁。備份欄留空會自動從手機拉取最新備份，也可選擇現有備份；設定輸出資料夾後按「執行」。記錄顯示完成後，按「開啟輸出資料夾」即可查看 Markdown 與附件。
7. **遷移到 ColorOS（可選）**：切換到「HyperOS → ColorOS」分頁，選擇第 6 步的 HyperOS 匯出資料夾，勾選「推送後自動還原」，按「執行」。還原是追加操作，請勿重複執行。
8. **清理**：確認匯出無誤後，刪除手機上的備份（備份未加密）。

介面右上角可切換語言（預設跟隨系統語言）。執行中可按「停止」。

> 缺少 tkinter？macOS（Homebrew）：`brew install python-tk`；Debian/Ubuntu：`sudo apt install python3-tk`；Windows 官方安裝程式已內建。

## 一、HyperOS / MIUI 便籤 → Markdown

### 為什麼不用 `adb backup`

自 Android 13 起，系統限制非 debuggable 應用使用 `adb backup`，小米便籤只會得到空備份。因此改用小米內建的「本機備份」通道，它會呼叫便籤自身的 `NoteBackupAgent`，可取得完整資料。

### 手機端準備

> 小米備份預設會勾選多個類別，**務必先取消所有類別，只保留「筆記」**。

1. 開啟 `設定 → 更多設定 → 備份與還原 → 手機備份還原 → 備份`
2. 取消所有已勾選的類別，直到每個類別都不再顯示已選數量
3. 展開「其他系統應用資料」，只勾選「筆記」，確認顯示類似 `500MB 1/25項`
4. 點「立即備份」→「繼續備份」→「我知道了」
5. 在進度頁確認佇列裡**只有「筆記」**；若出現其他 App，立即取消

備份位於：

```
/sdcard/MIUI/backup/AllBackup/<時間>/
/sdcard/MIUI/backup/AllBackup/<時間>.zip
```

### 指令列用法

```bash
# 自動拉取手機上最新的備份並匯出
python3 hyperos_notes_extract.py

# 指定輸出資料夾
python3 hyperos_notes_extract.py -o ~/Documents/Notes

# 解析現有備份（zip 或 .bak）
python3 hyperos_notes_extract.py --from-backup ~/Downloads/<備份時間>.zip
```

其他選項：`--keep-backup`（保留拉取到本機的備份）、`--delete-device-backup`（完成後刪除手機上的備份，無法復原）、`--debug`。

### 輸出結構

```
notes_export/
├── notes/
│   ├── 標題.md
│   └── 資料夾/
│       └── 標題.md
├── assets/
│   ├── <sha1>.jpg
│   └── <sha1>.mp3
└── notes.json
```

Markdown 帶 YAML 標頭（標題、建立時間、修改時間、資料夾），圖片與錄音已改為本機相對路徑。

### 限制

- 私密便籤、雙開應用資料不在本機備份範圍內
- 待辦清單尚未匯出
- 附件以 SHA1 命名
- 完全空白的便籤會被略過

## 二、ColorOS / realme UI 便籤 → Markdown

ColorOS 的本機備份同樣是明文資料：`rich_note` 是 JSON，附件在 `files/file_backup.zip`。

### 手機端準備

1. 開啟 `設定 → 帳號與備份 → 備份與遷移 → 本機備份 → 新建備份`
2. 取消所有類別，只勾選「系統偏好設定 → 便籤」
3. 開始備份，確認佇列裡只有「便籤」

備份位於：

```
/sdcard/Android/data/com.coloros.backuprestore/Backup/Data/<時間>/
```

### 指令列用法

```bash
# 自動拉取手機上最新的便籤備份並匯出
python3 coloros_notes_extract.py

# 解析已拉取的備份資料夾（包含 Note/）
python3 coloros_notes_extract.py --from-backup <備份資料夾>

# 指定輸出資料夾
python3 coloros_notes_extract.py -o ~/Documents/ColorOSNotes
```

### 輸出結構

```
coloros_notes_export/
├── notes/
│   ├── 標題.md
│   └── 資料夾/
│       └── 標題.md
├── assets/
│   └── <note-id>/
│       ├── <attachment-id>.png
│       └── <attachment-id>.mp3
└── notes.json
```

### 限制

- ColorOS 本機備份只保存圖片的 `_thumb.png` 縮圖，不含原圖
- 私密便籤、雙開應用資料不在備份範圍內
- 錄音、手寫檔案會一併匯出

## 三、HyperOS → ColorOS 遷移

將「一」匯出的 `notes_export` 轉換成 ColorOS 本機備份，再用 ColorOS 內建的「本機備份 → 還原」匯入。

### 前置條件

- 已完成 HyperOS 匯出（`notes_export/notes.json` + `assets/`）
- 手機上有一份 ColorOS 便籤本機備份作為範本（工具也會自動拉取最新備份作為範本）

### 指令列用法

```bash
python3 hyperos_to_coloros_import.py \
  --export ./notes_export \
  --out ./coloros_import_backup \
  --push --restore
```

| 參數 | 說明 |
| --- | --- |
| `--export` | HyperOS 匯出資料夾 |
| `--template` | ColorOS 備份範本資料夾；省略時自動從手機拉取 |
| `--out` | 產生的 ColorOS 備份資料夾 |
| `--push` | 產生後推送到手機 |
| `--restore` | 推送後自動開啟備份介面並執行還原 |
| `--limit N` | 只匯入前 N 筆（測試用） |
| `--skip N` | 跳過前 N 筆（斷點續匯） |
| `--debug` | 列印每筆便籤的轉換資訊 |

### 運作方式

1. 讀取 `notes_export/notes.json` 與 `assets/`
2. 將 Markdown 轉成 ColorOS 的富文字 HTML（標題、粗體、清單、核取方塊、圖片）
3. 依 `localId/attachmentId` 產生 `Note/rich_note` 與 `Note/files/file_backup.zip`
4. 複製 ColorOS 備份的設定檔與範本，產生完整備份資料夾
5. 透過 adb 推送，並用 ColorOS 的還原功能寫入便籤資料庫

### 限制

- **錄音不匯入**：ColorOS 錄音附件格式與小米不同，內文會保留轉寫文字，並標註「原 HyperOS 錄音未匯入」
- ColorOS 的修改時間會顯示為匯入時間，原始建立時間會保留
- 還原是「追加」操作，重複執行會產生重複便籤；可用 `--skip` 分批，或先在手機上清理
- 大量便籤（數百筆、數百張圖）會產生數百 MB 的備份，還原需要數分鐘

## 安裝為指令

```bash
pipx install git+https://github.com/MoYu2008Fish/notes-toolkit.git

notes-toolkit-gui      # 圖形介面
hyperos-notes --help
coloros-notes --help
hyperos-to-coloros --help
```

也可以直接下載腳本執行，只依賴 Python 標準函式庫。

## 隱私與安全

- 所有腳本與圖形介面都不連網、不上傳資料
- 匯出的 `notes_export/`、`coloros_notes_export/`、`coloros_import_backup/` 已加入 `.gitignore`，不會被提交
- 小米 / ColorOS 的本機備份都是**未加密**的，備份與匯出檔案請妥善保管
- 匯出完成後建議刪除手機上的本機備份，或使用刪除手機備份的選項
- 儲存庫中不含任何個人便籤、帳號、電話號碼或裝置識別碼

## 開發

```bash
python3 -m py_compile hyperos_notes_extract.py coloros_notes_extract.py hyperos_to_coloros_import.py notes_gui.py
```

歡迎貢獻，請開 issue 或 pull request。要新增圖形介面語言，請在 `notes_gui.py` 的 `LANGS` 與 `STRINGS` 中加入對應項目。

## 相關專案

- [mi-note-export](https://github.com/ceynri/mi-note-export)：走小米雲端匯出（已停止維護）
- [mi-note-cli](https://github.com/ceynri/mi-note-cli)：走小米雲端，支援雙向同步

本專案走本機備份，不依賴帳號與雲端服務，適合把手機裡的便籤完整搬到本機。

## 授權

[MIT](LICENSE)
