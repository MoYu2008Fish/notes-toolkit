#!/usr/bin/env python3
"""图形界面 / GUI / グラフィカル UI —— HyperOS / ColorOS notes toolkit.

A thin tkinter front end for the three command-line tools. It builds the
command line from the form, runs the tool in a subprocess and streams its
output into the log pane. Nothing is sent over the network.

Languages: English, 日本語, 繁體中文, 简体中文.
"""

import locale
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

__version__ = "0.1.0"

HERE = os.path.dirname(os.path.abspath(__file__))

LANGS = [
    ("en", "English"),
    ("ja", "日本語"),
    ("zh_TW", "繁體中文"),
    ("zh_CN", "简体中文"),
]

STRINGS = {
    "en": {
        "title": "Notes Toolkit",
        "language": "Language",
        "tab_hyperos": "HyperOS → Markdown",
        "tab_coloros": "ColorOS → Markdown",
        "tab_import": "HyperOS → ColorOS",
        "desc_hyperos": "Export Xiaomi HyperOS / MIUI notes from a local backup. "
                        "Leave the backup field empty to pull the newest backup from the phone over adb.",
        "desc_coloros": "Export ColorOS / realme UI notes from a local backup. "
                        "Leave the backup field empty to pull the newest backup from the phone over adb.",
        "desc_import": "Convert a HyperOS export into a ColorOS local backup and (optionally) restore it on the phone.",
        "output": "Output folder",
        "from_backup": "Backup (optional)",
        "export_dir": "HyperOS export folder",
        "template": "ColorOS template (optional)",
        "out_dir": "Generated backup folder",
        "keep_backup": "Keep the backup pulled to this computer",
        "delete_device_backup": "Delete the backup on the phone afterwards (cannot be undone)",
        "debug": "Verbose debug output",
        "push": "Push the backup to the phone",
        "restore": "Push and restore automatically",
        "limit": "Import only the first N notes",
        "skip": "Skip the first N notes",
        "browse": "Browse…",
        "folder": "Folder…",
        "file": "File…",
        "run": "Run",
        "stop": "Stop",
        "clear": "Clear log",
        "open_output": "Open output folder",
        "log": "Log",
        "running": "Running…",
        "ready": "Ready",
        "done": "Finished successfully",
        "failed": "Failed (exit code {code})",
        "stopped": "Stopped",
        "cmd": "Command",
        "need_export": "Please choose the HyperOS export folder.",
        "need_int": "“{field}” must be a non-negative integer.",
        "confirm_delete": "This will permanently delete the backup stored on your phone after exporting.\n\nContinue?",
        "confirm_restore": "Restoring appends the notes to the phone. Running it twice creates duplicates.\n\nContinue?",
        "error": "Error",
        "warning": "Warning",
        "hint_adb": "Requires adb and USB debugging when no backup is given.",
    },
    "ja": {
        "title": "ノートツールキット",
        "language": "言語",
        "tab_hyperos": "HyperOS → Markdown",
        "tab_coloros": "ColorOS → Markdown",
        "tab_import": "HyperOS → ColorOS",
        "desc_hyperos": "Xiaomi HyperOS / MIUI のメモをローカルバックアップから書き出します。"
                        "バックアップ欄が空の場合は、adb 経由で端末の最新バックアップを取得します。",
        "desc_coloros": "ColorOS / realme UI のメモをローカルバックアップから書き出します。"
                        "バックアップ欄が空の場合は、adb 経由で端末の最新バックアップを取得します。",
        "desc_import": "HyperOS の書き出し結果を ColorOS のローカルバックアップに変換し、必要に応じて端末で復元します。",
        "output": "出力フォルダ",
        "from_backup": "バックアップ（任意）",
        "export_dir": "HyperOS 書き出しフォルダ",
        "template": "ColorOS テンプレート（任意）",
        "out_dir": "生成するバックアップフォルダ",
        "keep_backup": "このコンピュータに取得したバックアップを残す",
        "delete_device_backup": "完了後に端末上のバックアップを削除する（元に戻せません）",
        "debug": "詳細なデバッグ出力",
        "push": "バックアップを端末に送信する",
        "restore": "送信後に自動で復元する",
        "limit": "先頭 N 件のみ取り込む",
        "skip": "先頭 N 件をスキップ",
        "browse": "参照…",
        "folder": "フォルダ…",
        "file": "ファイル…",
        "run": "実行",
        "stop": "停止",
        "clear": "ログを消去",
        "open_output": "出力フォルダを開く",
        "log": "ログ",
        "running": "実行中…",
        "ready": "準備完了",
        "done": "正常に完了しました",
        "failed": "失敗しました（終了コード {code}）",
        "stopped": "停止しました",
        "cmd": "コマンド",
        "need_export": "HyperOS の書き出しフォルダを選択してください。",
        "need_int": "「{field}」には 0 以上の整数を入力してください。",
        "confirm_delete": "書き出し後、端末に保存されているバックアップを完全に削除します。\n\n続行しますか？",
        "confirm_restore": "復元は端末にメモを追加します。2 回実行すると重複します。\n\n続行しますか？",
        "error": "エラー",
        "warning": "警告",
        "hint_adb": "バックアップを指定しない場合は adb と USB デバッグが必要です。",
    },
    "zh_TW": {
        "title": "便籤工具箱",
        "language": "語言",
        "tab_hyperos": "HyperOS → Markdown",
        "tab_coloros": "ColorOS → Markdown",
        "tab_import": "HyperOS → ColorOS",
        "desc_hyperos": "從本機備份匯出小米 HyperOS / MIUI 便籤。"
                        "備份欄位留空時，會透過 adb 從手機拉取最新備份。",
        "desc_coloros": "從本機備份匯出 ColorOS / realme UI 便籤。"
                        "備份欄位留空時，會透過 adb 從手機拉取最新備份。",
        "desc_import": "將 HyperOS 匯出結果轉換為 ColorOS 本機備份，並可選擇在手機上還原。",
        "output": "輸出資料夾",
        "from_backup": "備份（可選）",
        "export_dir": "HyperOS 匯出資料夾",
        "template": "ColorOS 範本（可選）",
        "out_dir": "產生的備份資料夾",
        "keep_backup": "保留拉取到本機的備份",
        "delete_device_backup": "完成後刪除手機上的備份（無法復原）",
        "debug": "顯示詳細除錯資訊",
        "push": "將備份推送到手機",
        "restore": "推送後自動還原",
        "limit": "只匯入前 N 筆",
        "skip": "跳過前 N 筆",
        "browse": "瀏覽…",
        "folder": "資料夾…",
        "file": "檔案…",
        "run": "執行",
        "stop": "停止",
        "clear": "清除記錄",
        "open_output": "開啟輸出資料夾",
        "log": "記錄",
        "running": "執行中…",
        "ready": "就緒",
        "done": "已成功完成",
        "failed": "失敗（結束代碼 {code}）",
        "stopped": "已停止",
        "cmd": "指令",
        "need_export": "請選擇 HyperOS 匯出資料夾。",
        "need_int": "「{field}」必須是非負整數。",
        "confirm_delete": "匯出後將永久刪除手機上的這份備份。\n\n是否繼續？",
        "confirm_restore": "還原會把便籤追加到手機，重複執行會產生重複便籤。\n\n是否繼續？",
        "error": "錯誤",
        "warning": "警告",
        "hint_adb": "未指定備份時，需要 adb 並開啟 USB 偵錯。",
    },
    "zh_CN": {
        "title": "便签工具箱",
        "language": "语言",
        "tab_hyperos": "HyperOS → Markdown",
        "tab_coloros": "ColorOS → Markdown",
        "tab_import": "HyperOS → ColorOS",
        "desc_hyperos": "从本地备份导出小米 HyperOS / MIUI 便签。"
                        "备份栏留空时，会通过 adb 从手机拉取最新备份。",
        "desc_coloros": "从本地备份导出 ColorOS / realme UI 便签。"
                        "备份栏留空时，会通过 adb 从手机拉取最新备份。",
        "desc_import": "把 HyperOS 导出结果转换为 ColorOS 本地备份，并可选择在手机上恢复。",
        "output": "输出目录",
        "from_backup": "备份（可选）",
        "export_dir": "HyperOS 导出目录",
        "template": "ColorOS 模板（可选）",
        "out_dir": "生成的备份目录",
        "keep_backup": "保留拉取到本机的备份",
        "delete_device_backup": "完成后删除手机上的备份（不可恢复）",
        "debug": "显示详细调试信息",
        "push": "把备份推送到手机",
        "restore": "推送后自动恢复",
        "limit": "只导入前 N 条",
        "skip": "跳过前 N 条",
        "browse": "浏览…",
        "folder": "目录…",
        "file": "文件…",
        "run": "运行",
        "stop": "停止",
        "clear": "清空日志",
        "open_output": "打开输出目录",
        "log": "日志",
        "running": "运行中…",
        "ready": "就绪",
        "done": "已成功完成",
        "failed": "失败（退出码 {code}）",
        "stopped": "已停止",
        "cmd": "命令",
        "need_export": "请选择 HyperOS 导出目录。",
        "need_int": "“{field}”必须是非负整数。",
        "confirm_delete": "导出后将永久删除手机上的这份备份。\n\n是否继续？",
        "confirm_restore": "恢复会把便签追加到手机，重复执行会产生重复便签。\n\n是否继续？",
        "error": "错误",
        "warning": "警告",
        "hint_adb": "未指定备份时，需要 adb 并开启 USB 调试。",
    },
}


def default_lang():
    try:
        code = (locale.getdefaultlocale()[0] or "").lower()
    except Exception:
        code = ""
    if code.startswith("ja"):
        return "ja"
    if code.startswith("zh"):
        return "zh_TW" if any(k in code for k in ("tw", "hk", "mo", "hant")) else "zh_CN"
    return "en"


# Field kinds: path-dir, path-file, path-any (folder or file), bool, int.
# Each field: (key, kind, flag, default)
TOOLS = [
    {
        "id": "hyperos",
        "module": "hyperos_notes_extract",
        "tab": "tab_hyperos",
        "desc": "desc_hyperos",
        "output_key": "output",
        "fields": [
            ("from_backup", "any", "--from-backup", ""),
            ("output", "dir", "-o", "notes_export"),
            ("keep_backup", "bool", "--keep-backup", False),
            ("delete_device_backup", "bool", "--delete-device-backup", False),
            ("debug", "bool", "--debug", False),
        ],
    },
    {
        "id": "coloros",
        "module": "coloros_notes_extract",
        "tab": "tab_coloros",
        "desc": "desc_coloros",
        "output_key": "output",
        "fields": [
            ("from_backup", "dir", "--from-backup", ""),
            ("output", "dir", "-o", "coloros_notes_export"),
            ("keep_backup", "bool", "--keep-backup", False),
            ("delete_device_backup", "bool", "--delete-device-backup", False),
            ("debug", "bool", "--debug", False),
        ],
    },
    {
        "id": "import",
        "module": "hyperos_to_coloros_import",
        "tab": "tab_import",
        "desc": "desc_import",
        "output_key": "out_dir",
        "fields": [
            ("export_dir", "dir", "--export", ""),
            ("template", "dir", "--template", ""),
            ("out_dir", "dir", "--out", "coloros_import_backup"),
            ("push", "bool", "--push", False),
            ("restore", "bool", "--restore", False),
            ("limit", "int", "--limit", ""),
            ("skip", "int", "--skip", ""),
            ("debug", "bool", "--debug", False),
        ],
    },
]


class ToolFrame(ttk.Frame):
    def __init__(self, master, spec, app):
        super().__init__(master, padding=10)
        self.spec = spec
        self.app = app
        self.vars = {}
        self.labels = {}
        self.buttons = {}
        self.columnconfigure(1, weight=1)

        self.desc = ttk.Label(self, justify="left")
        self.desc.grid(row=0, column=0, columnspan=4, sticky="we", pady=(0, 8))
        self.bind("<Configure>", lambda e: self.desc.configure(wraplength=max(e.width - 24, 200)))

        row = 1
        for key, kind, flag, default in spec["fields"]:
            if kind == "bool":
                var = tk.BooleanVar(value=default)
                w = ttk.Checkbutton(self, variable=var)
                w.grid(row=row, column=0, columnspan=4, sticky="w", pady=2)
                self.labels[key] = w
            else:
                var = tk.StringVar(value=default)
                lab = ttk.Label(self)
                lab.grid(row=row, column=0, sticky="w", padx=(0, 8), pady=3)
                self.labels[key] = lab
                if kind == "int":
                    ttk.Entry(self, textvariable=var, width=10).grid(row=row, column=1, sticky="w", pady=3)
                else:
                    ttk.Entry(self, textvariable=var).grid(row=row, column=1, sticky="we", pady=3)
                    if kind == "any":
                        b1 = ttk.Button(self, command=lambda v=var: self.pick_dir(v))
                        b2 = ttk.Button(self, command=lambda v=var: self.pick_file(v))
                        b1.grid(row=row, column=2, padx=(6, 0))
                        b2.grid(row=row, column=3, padx=(4, 0))
                        self.buttons[key] = (b1, b2)
                    else:
                        b = ttk.Button(self, command=lambda v=var: self.pick_dir(v))
                        b.grid(row=row, column=2, padx=(6, 0))
                        self.buttons[key] = (b,)
            self.vars[key] = var
            row += 1

    def pick_dir(self, var):
        path = filedialog.askdirectory(initialdir=var.get() or os.path.expanduser("~"))
        if path:
            var.set(path)

    def pick_file(self, var):
        path = filedialog.askopenfilename(initialdir=os.path.dirname(var.get()) or os.path.expanduser("~"))
        if path:
            var.set(path)

    def retranslate(self, t):
        self.desc.configure(text=t[self.spec["desc"]])
        for key, widget in self.labels.items():
            widget.configure(text=t[key])
        for key, btns in self.buttons.items():
            if len(btns) == 2:
                btns[0].configure(text=t["folder"])
                btns[1].configure(text=t["file"])
            else:
                btns[0].configure(text=t["browse"])

    def build_args(self, t):
        """Return the CLI arguments, or raise ValueError(message)."""
        args = []
        for key, kind, flag, _ in self.spec["fields"]:
            val = self.vars[key].get()
            if kind == "bool":
                if val:
                    args.append(flag)
                continue
            val = val.strip()
            if self.spec["id"] == "import" and key == "export_dir" and not val:
                raise ValueError(t["need_export"])
            if not val:
                continue
            if kind == "int" and not val.isdigit():
                raise ValueError(t["need_int"].format(field=t[key]))
            args += [flag, val]
        return args

    def output_path(self):
        return self.vars[self.spec["output_key"]].get().strip()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("780x640")
        self.minsize(640, 520)
        self.lang = default_lang()
        self.proc = None
        self.stopped = False
        self.q = queue.Queue()
        self.running_frame = None

        top = ttk.Frame(self, padding=(10, 8, 10, 0))
        top.pack(fill="x")
        self.lang_box = ttk.Combobox(top, state="readonly", width=12, values=[n for _, n in LANGS])
        self.lang_box.current([c for c, _ in LANGS].index(self.lang))
        self.lang_box.bind("<<ComboboxSelected>>", self.on_lang)
        self.lang_box.pack(side="right")
        self.lang_label = ttk.Label(top)
        self.lang_label.pack(side="right", padx=(0, 6))

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="x", padx=10, pady=8)
        self.frames = []
        for spec in TOOLS:
            f = ToolFrame(self.nb, spec, self)
            self.nb.add(f, text=spec["id"])
            self.frames.append(f)

        bar = ttk.Frame(self, padding=(10, 0))
        bar.pack(fill="x")
        self.run_btn = ttk.Button(bar, command=self.run)
        self.run_btn.pack(side="left")
        self.stop_btn = ttk.Button(bar, command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=6)
        self.open_btn = ttk.Button(bar, command=self.open_output)
        self.open_btn.pack(side="left")
        self.clear_btn = ttk.Button(bar, command=lambda: self.log.delete("1.0", "end"))
        self.clear_btn.pack(side="right")
        self.progress = ttk.Progressbar(bar, mode="indeterminate", length=120)
        self.progress.pack(side="right", padx=8)

        self.log_frame = ttk.LabelFrame(self, padding=4)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=8)
        self.log = tk.Text(self.log_frame, height=14, wrap="word", state="normal")
        sb = ttk.Scrollbar(self.log_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True)

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status, anchor="w", relief="sunken", padding=(6, 2)).pack(fill="x")

        self.status_key = "ready"
        self.status_fmt = {}
        self.retranslate()
        self.after(100, self.pump)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    @property
    def t(self):
        return STRINGS[self.lang]

    def on_lang(self, _event=None):
        self.lang = LANGS[self.lang_box.current()][0]
        self.retranslate()

    def retranslate(self):
        t = self.t
        self.title(t["title"])
        self.lang_label.configure(text=t["language"])
        for i, f in enumerate(self.frames):
            self.nb.tab(i, text=t[f.spec["tab"]])
            f.retranslate(t)
        self.run_btn.configure(text=t["run"])
        self.stop_btn.configure(text=t["stop"])
        self.open_btn.configure(text=t["open_output"])
        self.clear_btn.configure(text=t["clear"])
        self.log_frame.configure(text=t["log"])
        self.set_status(self.status_key, **self.status_fmt)

    def set_status(self, key, **fmt):
        self.status_key, self.status_fmt = key, fmt
        self.status.set(self.t[key].format(**fmt))

    def current_frame(self):
        return self.frames[self.nb.index(self.nb.select())]

    def append(self, text):
        self.log.insert("end", text)
        self.log.see("end")

    def run(self):
        frame = self.current_frame()
        t = self.t
        try:
            args = frame.build_args(t)
        except ValueError as e:
            messagebox.showerror(t["error"], str(e))
            return
        if "--delete-device-backup" in args and not messagebox.askyesno(t["warning"], t["confirm_delete"]):
            return
        if "--restore" in args and not messagebox.askyesno(t["warning"], t["confirm_restore"]):
            return

        cmd = [sys.executable, "-u", "-m", frame.spec["module"]] + args
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
        env["PYTHONPATH"] = HERE + os.pathsep + env.get("PYTHONPATH", "")
        self.append("$ %s\n" % " ".join(a if " " not in a else '"%s"' % a for a in cmd[3:]))
        try:
            self.proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except OSError as e:
            messagebox.showerror(t["error"], str(e))
            return
        self.stopped = False
        self.running_frame = frame
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress.start(12)
        self.set_status("running")
        threading.Thread(target=self.reader, args=(self.proc,), daemon=True).start()

    def reader(self, proc):
        for raw in iter(proc.stdout.readline, b""):
            self.q.put(("line", raw.decode("utf-8", errors="replace")))
        proc.wait()
        self.q.put(("exit", proc.returncode))

    def pump(self):
        try:
            while True:
                kind, val = self.q.get_nowait()
                if kind == "line":
                    self.append(val)
                else:
                    self.finish(val)
        except queue.Empty:
            pass
        self.after(100, self.pump)

    def finish(self, code):
        self.progress.stop()
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.proc = None
        if self.stopped:
            self.set_status("stopped")
        elif code == 0:
            self.set_status("done")
        else:
            self.set_status("failed", code=code)

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.stopped = True
            self.proc.terminate()

    def open_output(self):
        path = self.current_frame().output_path()
        path = os.path.abspath(path or ".")
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
        elif sys.platform.startswith("win"):
            os.startfile(path)  # noqa: F821 (Windows only)
        else:
            subprocess.Popen(["xdg-open", path])

    def on_close(self):
        self.stop()
        self.destroy()


def main():
    # Launched from a desktop icon the cwd may be "/" or read-only; relative
    # output folders should land somewhere writable.
    if not os.access(os.getcwd(), os.W_OK):
        os.chdir(os.path.expanduser("~"))
    App().mainloop()


if __name__ == "__main__":
    main()
