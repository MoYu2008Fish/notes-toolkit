# HyperOS / ColorOS Notes Toolkit

**English** · **[简体中文](README.zh-CN.md)** · **[繁體中文](README.zh-TW.md)** · **[日本語](README.ja.md)**

Extract notes from Xiaomi and OPPO-family phones locally, or migrate them between the two systems. No root, no account login, no cloud.

| Tool | Purpose |
| --- | --- |
| `hyperos_notes_extract.py` | HyperOS / MIUI notes → Markdown + images / recordings |
| `coloros_notes_extract.py` | ColorOS / realme UI notes → Markdown + images / recordings |
| `hyperos_to_coloros_import.py` | Import a HyperOS export into ColorOS Notes |
| `notes_gui.py` | GUI (English / 日本語 / 繁體中文 / 简体中文) wrapping the three tools |

> Everything reads and writes only local files and talks to the phone via adb. Nothing goes online and no data is uploaded.

## Requirements

- Python 3.8+ (with tkinter for the GUI)
- `adb` (Android platform-tools) on your `PATH`
- "USB debugging" enabled on the phone, with this computer authorized

## Quick start (GUI)

Complete workflow:

1. **Install prerequisites**: Python 3.8+ with tkinter, and `adb`.
2. **Get the tool**: `git clone https://github.com/MoYu2008Fish/notes-toolkit.git && cd notes-toolkit`
3. **Prepare the phone**: enable *Developer options → USB debugging*, connect via USB and accept the authorization prompt. `adb devices` should list the phone as `device`.
4. **Create a local backup on the phone** containing only Notes — see section 1 (Xiaomi) or 2 (ColorOS) below.
5. **Launch the GUI**: `python3 notes_gui.py` (or `notes-toolkit-gui` if installed).
6. **Export**: open the *HyperOS → Markdown* or *ColorOS → Markdown* tab. Leave "Backup" empty to pull the newest backup from the phone automatically, or pick an existing backup. Choose an output folder and press **Run**. When the log says it finished, press **Open output folder** to see the Markdown files and attachments.
7. **Migrate to ColorOS (optional)**: switch to the *HyperOS → ColorOS* tab, choose the HyperOS export folder from step 6, tick "Push and restore automatically" and press **Run**. Restoring *appends* notes — don't run it twice.
8. **Clean up**: once you've verified the export, delete the backup on the phone (backups are unencrypted).

The language can be switched at the top right (defaults to your system language). **Stop** cancels a running job.

> Missing tkinter? macOS (Homebrew): `brew install python-tk`. Debian/Ubuntu: `sudo apt install python3-tk`. The official Windows installer includes it.

## 1. HyperOS / MIUI notes → Markdown

### Why not `adb backup`

Since Android 13, `adb backup` is restricted for non-debuggable apps, so Xiaomi Notes yields an empty backup. This tool uses Xiaomi's built-in "local backup" instead, which calls the app's own `NoteBackupAgent` and returns complete data.

### Phone preparation

> Xiaomi backup selects many categories by default. **Deselect everything first and keep only "Notes".**

1. Open `Settings → More settings → Backup & restore → Phone backup & restore → Backup`
2. Deselect all categories until none shows a selected count
3. Expand "Other system app data" and tick only "Notes" — you should see something like `500MB 1/25 items`
4. Tap "Back up now" → "Continue" → "Got it"
5. On the progress page confirm the queue contains **only "Notes"**; cancel immediately if other apps appear

The backup lives at:

```
/sdcard/MIUI/backup/AllBackup/<timestamp>/
/sdcard/MIUI/backup/AllBackup/<timestamp>.zip
```

### CLI usage

```bash
# Pull the newest backup from the phone and export it
python3 hyperos_notes_extract.py

# Choose the output folder
python3 hyperos_notes_extract.py -o ~/Documents/Notes

# Parse an existing backup (zip or .bak)
python3 hyperos_notes_extract.py --from-backup ~/Downloads/<timestamp>.zip
```

Extra options: `--keep-backup` (keep the pulled backup), `--delete-device-backup` (delete the phone's copy afterwards, irreversible), `--debug`.

### Output layout

```
notes_export/
├── notes/
│   ├── Title.md
│   └── Folder/
│       └── Title.md
├── assets/
│   ├── <sha1>.jpg
│   └── <sha1>.mp3
└── notes.json
```

Each Markdown file has a YAML header (title, created, modified, folder); images and recordings use local relative paths.

### Limitations

- Private notes and dual-app data are not part of the local backup
- To-do lists are not exported yet
- Attachments are named by SHA1
- Completely empty notes are skipped

## 2. ColorOS / realme UI notes → Markdown

ColorOS local backups are plain data: `rich_note` is JSON and attachments are in `files/file_backup.zip`.

### Phone preparation

1. Open `Settings → Account & backup → Backup & migration → Local backup → New backup`
2. Deselect all categories, tick only "System preferences → Notes"
3. Start the backup and confirm the queue contains only "Notes"

The backup lives at:

```
/sdcard/Android/data/com.coloros.backuprestore/Backup/Data/<timestamp>/
```

### CLI usage

```bash
# Pull the newest Notes backup from the phone and export it
python3 coloros_notes_extract.py

# Parse an already pulled backup folder (containing Note/)
python3 coloros_notes_extract.py --from-backup <backup-dir>

# Choose the output folder
python3 coloros_notes_extract.py -o ~/Documents/ColorOSNotes
```

### Output layout

```
coloros_notes_export/
├── notes/
│   ├── Title.md
│   └── Folder/
│       └── Title.md
├── assets/
│   └── <note-id>/
│       ├── <attachment-id>.png
│       └── <attachment-id>.mp3
└── notes.json
```

### Limitations

- ColorOS local backups only keep `_thumb.png` thumbnails of images, not the originals
- Private notes and dual-app data are not included
- Recordings and handwriting files are exported as well

## 3. HyperOS → ColorOS migration

Converts a `notes_export` from section 1 into a ColorOS local backup, which you then import with ColorOS's own "Local backup → Restore".

### Prerequisites

- A finished HyperOS export (`notes_export/notes.json` + `assets/`)
- A ColorOS Notes local backup on the phone to use as a template (the tool also pulls the newest one automatically)

### CLI usage

```bash
python3 hyperos_to_coloros_import.py \
  --export ./notes_export \
  --out ./coloros_import_backup \
  --push --restore
```

| Option | Description |
| --- | --- |
| `--export` | HyperOS export folder |
| `--template` | ColorOS backup template folder; pulled from the phone if omitted |
| `--out` | Folder for the generated ColorOS backup |
| `--push` | Push the backup to the phone after generating |
| `--restore` | After pushing, open the backup UI and restore automatically |
| `--limit N` | Import only the first N notes (for testing) |
| `--skip N` | Skip the first N notes (resume an import) |
| `--debug` | Print conversion info per note |

### How it works

1. Reads `notes_export/notes.json` and `assets/`
2. Converts Markdown to ColorOS rich-text HTML (headings, bold, lists, checkboxes, images)
3. Builds `Note/rich_note` and `Note/files/file_backup.zip` keyed by `localId/attachmentId`
4. Copies the ColorOS backup config and template into a complete backup folder
5. Pushes it with adb and uses ColorOS's restore function to write into the Notes database

### Limitations

- **Recordings are not imported**: the ColorOS audio attachment format differs from Xiaomi's. The transcript is kept in the note body with an "original HyperOS recording not imported" marker
- ColorOS shows the import time as the modified time; the original creation time is preserved
- Restore *appends*; running it twice duplicates notes. Use `--skip` for batches, or clean up on the phone first
- Hundreds of notes / images produce a backup of hundreds of MB and take minutes to restore

## Install as commands

```bash
pipx install git+https://github.com/MoYu2008Fish/notes-toolkit.git

notes-toolkit-gui      # GUI
hyperos-notes --help
coloros-notes --help
hyperos-to-coloros --help
```

You can also just download the scripts; they only need the Python standard library.

## Privacy & security

- No script or GUI window connects to the internet or uploads data
- `notes_export/`, `coloros_notes_export/` and `coloros_import_backup/` are in `.gitignore` and won't be committed
- Xiaomi / ColorOS local backups are **unencrypted** — keep backups and exports safe
- Delete the local backup on the phone after exporting, or use the delete-device-backup option
- This repository contains no personal notes, accounts, phone numbers or device identifiers

## Development

```bash
python3 -m py_compile hyperos_notes_extract.py coloros_notes_extract.py hyperos_to_coloros_import.py notes_gui.py
```

Contributions are welcome — please open an issue or pull request. To add a GUI language, add an entry to `LANGS` and `STRINGS` in `notes_gui.py`.

## Related projects

- [mi-note-export](https://github.com/ceynri/mi-note-export): exports via Xiaomi Cloud (unmaintained)
- [mi-note-cli](https://github.com/ceynri/mi-note-cli): via Xiaomi Cloud, two-way sync

This project works from local backups and needs no account or cloud service — ideal for moving the full contents of your phone's notes to your computer.

## License

[MIT](LICENSE)
