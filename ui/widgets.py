from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable, Optional


class Spacer(ttk.Frame):
    def __init__(self, master, h: int = 10, **kw):
        super().__init__(master, style="App.TFrame", **kw)
        self.configure(height=h)
        self.pack_propagate(False)


class NeonButton(ttk.Frame):
    """
    A modern-ish button made with a Frame + Label to emulate neon accent.
    Still pure Tkinter/ttk.
    """
    def __init__(self, master, text: str, command: Callable[[], None], width: int = 14):
        super().__init__(master, style="App.TFrame")
        self.command = command

        self.btn = tk.Label(
            self,
            text=text,
            cursor="hand2",
            padx=14,
            pady=9,
            font=("Segoe UI Semibold", 10),
            fg="#0b0f17",
            bg="#6ee7ff",
        )
        self.btn.pack()

        self.btn.bind("<Button-1>", lambda _e: self.command())
        self.btn.bind("<Enter>", self._on_enter)
        self.btn.bind("<Leave>", self._on_leave)

        self._base_bg = "#6ee7ff"
        self._hover_bg = "#a78bfa"

    def _on_enter(self, _e):
        self.btn.configure(bg=self._hover_bg)

    def _on_leave(self, _e):
        self.btn.configure(bg=self._base_bg)


class Topbar(ttk.Frame):
    def __init__(self, master, app_name: str, tagline: str, version: str):
        super().__init__(master, style="App.TFrame", padding=(16, 12, 16, 10))
        self.columnconfigure(0, weight=1)

        left = ttk.Frame(self, style="App.TFrame")
        left.grid(row=0, column=0, sticky="w")

        self.logo = ttk.Label(left, text=app_name, style="TLabel", font=("Segoe UI Semibold", 14))
        self.logo.grid(row=0, column=0, sticky="w")

        self.tag = ttk.Label(left, text=tagline, style="TLabel", foreground="#9fb0c6")
        self.tag.grid(row=1, column=0, sticky="w")

        right = ttk.Frame(self, style="App.TFrame")
        right.grid(row=0, column=1, sticky="e")

        self.ver = ttk.Label(right, text=f"v{version}", style="TLabel", foreground="#9fb0c6")
        self.ver.grid(row=0, column=0, sticky="e")

        sep = ttk.Separator(master, orient="horizontal")
        sep.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(52, 0))


class Sidebar(ttk.Frame):
    def __init__(self, master, on_nav: Callable[[str], None], on_run: Callable[[], None], on_credits: Callable[[], None]):
        super().__init__(master, style="Card.TFrame", padding=(14, 14, 14, 14))
        self.on_nav = on_nav
        self.on_run = on_run
        self.on_credits = on_credits

        self.configure(width=240)
        self.grid_propagate(False)

        title = ttk.Label(self, text="menu", style="CardTitle.TLabel")
        title.grid(row=0, column=0, sticky="w")

        ttk.Label(self, text="Navigate", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 4))

        self._nav_btn("Dashboard", "dashboard", row=2)
        self._nav_btn("Telemetry", "telemetry", row=3)
        self._nav_btn("About", "about", row=4)

        ttk.Separator(self, orient="horizontal").grid(row=5, column=0, sticky="ew", pady=(14, 14))

        ttk.Label(self, text="Actions", style="Muted.TLabel").grid(row=6, column=0, sticky="w", pady=(0, 6))

        btn_run = ttk.Button(self, text="Run Demo", command=self.on_run)
        btn_run.grid(row=7, column=0, sticky="ew")

        btn_credits = ttk.Button(self, text="Run Credits", command=self.on_credits)
        btn_credits.grid(row=8, column=0, sticky="ew", pady=(10, 0))

        ttk.Separator(self, orient="horizontal").grid(row=9, column=0, sticky="ew", pady=(16, 12))

        ttk.Label(self, text="Hint", style="Muted.TLabel").grid(row=10, column=0, sticky="w")

        hint = (
            "In real OSINT, identities are often\n"
            "pivoted from public profiles to\n"
            "company websites and naming patterns."
        )
        ttk.Label(self, text=hint, style="Muted.TLabel", justify="left").grid(row=11, column=0, sticky="w", pady=(6, 0))

    def _nav_btn(self, label: str, key: str, row: int) -> None:
        b = ttk.Button(self, text=label, command=lambda: self.on_nav(key))
        b.grid(row=row, column=0, sticky="ew", pady=(6, 0))


class StatCard(ttk.Frame):
    def __init__(self, master, title: str, value: str, hint: str):
        super().__init__(master, style="Card.TFrame", padding=(14, 12, 14, 12))
        self.columnconfigure(0, weight=1)

        self.lbl_title = ttk.Label(self, text=title, style="Muted.TLabel")
        self.lbl_title.grid(row=0, column=0, sticky="w")

        self.lbl_value = ttk.Label(self, text=value, style="TLabel", font=("Segoe UI Semibold", 16))
        self.lbl_value.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.lbl_hint = ttk.Label(self, text=hint, style="Muted.TLabel")
        self.lbl_hint.grid(row=2, column=0, sticky="w", pady=(6, 0))

    def set_value(self, v: str) -> None:
        self.lbl_value.configure(text=v)


class LogConsole(ttk.Frame):
    def __init__(self, master, title: str = "log"):
        super().__init__(master, style="Card.TFrame", padding=(14, 12, 14, 12))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text=title, style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        self.text = tk.Text(
            self,
            height=10,
            bg="#0e1420",
            fg="#e7edf7",
            insertbackground="#e7edf7",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#1f2a3f",
            highlightcolor="#1f2a3f",
            font=("Consolas", 10),
        )
        self.text.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.text.configure(state="disabled")

    def log(self, msg: str) -> None:
        self.text.configure(state="normal")
        self.text.insert("end", msg + "\n")
        self.text.see("end")
        self.text.configure(state="disabled")
