#!/usr/bin/env python3
"""ECC Dashboard — desktop GUI for the Everything Claude Code harness."""

import json
import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

CLAUDE_DIR = Path.home() / ".claude"


def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default if default is not None else {}


def count_items(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(1 for _ in directory.iterdir())


class ECCDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ECC Dashboard")
        self.geometry("800x600")
        self.configure(bg="#1e1e2e")
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        # Header
        header = tk.Label(
            self, text="Everything Claude Code", font=("SF Pro", 18, "bold"),
            bg="#1e1e2e", fg="#cdd6f4",
        )
        header.pack(pady=(20, 4))

        version_label = tk.Label(
            self, text="v1.10.0 Harness", font=("SF Pro", 11),
            bg="#1e1e2e", fg="#6c7086",
        )
        version_label.pack()

        # Stats frame
        stats_frame = tk.Frame(self, bg="#1e1e2e")
        stats_frame.pack(pady=20, fill=tk.X, padx=40)

        self._stat_widgets = {}
        stats_config = [
            ("agents", "Agents", "#cba6f7"),
            ("skills", "Skills", "#89b4fa"),
            ("commands", "Commands", "#a6e3a1"),
            ("rules", "Rule Files", "#f9e2af"),
        ]
        for key, label, color in stats_config:
            frame = tk.Frame(stats_frame, bg="#313244", padx=20, pady=16)
            frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=8)
            val = tk.Label(frame, text="…", font=("SF Pro", 28, "bold"), bg="#313244", fg=color)
            val.pack()
            tk.Label(frame, text=label, font=("SF Pro", 11), bg="#313244", fg="#cdd6f4").pack()
            self._stat_widgets[key] = val

        # Instincts panel
        inst_frame = tk.LabelFrame(
            self, text="Pending Instincts", font=("SF Pro", 12),
            bg="#1e1e2e", fg="#cdd6f4", padx=16, pady=12,
        )
        inst_frame.pack(fill=tk.X, padx=40, pady=(0, 16))

        self._instinct_list = tk.Listbox(
            inst_frame, bg="#181825", fg="#cdd6f4", selectbackground="#45475a",
            font=("SF Mono", 10), height=6,
        )
        self._instinct_list.pack(fill=tk.BOTH, expand=True)

        # Buttons
        btn_frame = tk.Frame(self, bg="#1e1e2e")
        btn_frame.pack(pady=8)

        for label, cmd in [
            ("Refresh", self._refresh),
            ("Open ~/.claude", self._open_dir),
            ("Run Tests", self._run_tests),
        ]:
            tk.Button(
                btn_frame, text=label, command=cmd,
                bg="#313244", fg="#cdd6f4", activebackground="#45475a",
                relief=tk.FLAT, padx=20, pady=8, font=("SF Pro", 11),
            ).pack(side=tk.LEFT, padx=6)

    def _refresh(self):
        dirs = {
            "agents": CLAUDE_DIR / "agents",
            "skills": CLAUDE_DIR / "skills",
            "commands": CLAUDE_DIR / "commands",
        }
        rules_dir = CLAUDE_DIR / "rules"
        rule_count = sum(
            1 for p in rules_dir.rglob("*.md")
            if p.is_file()
        ) if rules_dir.exists() else 0

        for key, path in dirs.items():
            self._stat_widgets[key].config(text=str(count_items(path)))
        self._stat_widgets["rules"].config(text=str(rule_count))

        # Load pending instincts
        instincts_path = CLAUDE_DIR / "instincts" / "pending.json"
        data = load_json(instincts_path, {"pending": []})
        self._instinct_list.delete(0, tk.END)
        for item in data.get("pending", []):
            title = item.get("title") or item.get("summary") or str(item)
            self._instinct_list.insert(tk.END, f"  {title}")

        if not data.get("pending"):
            self._instinct_list.insert(tk.END, "  No pending instincts.")

    def _open_dir(self):
        os.system(f"open '{CLAUDE_DIR}'")

    def _run_tests(self):
        test_script = CLAUDE_DIR / "tests" / "run-all.js"
        if not test_script.exists():
            messagebox.showinfo("Tests", "tests/run-all.js not found.")
            return
        result = os.popen(f"node '{test_script}' 2>&1").read()
        win = tk.Toplevel(self)
        win.title("Test Results")
        win.configure(bg="#1e1e2e")
        text = tk.Text(win, bg="#181825", fg="#cdd6f4", font=("SF Mono", 11), padx=12, pady=12)
        text.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        text.insert("1.0", result)
        text.config(state=tk.DISABLED)


if __name__ == "__main__":
    ECCDashboard().mainloop()
