from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk


@dataclass(frozen=True)
class Colors:
    bg: str = "#0b0f17"
    bg2: str = "#0e1420"
    bg_card: str = "#121a2a"
    border: str = "#1f2a3f"
    text: str = "#e7edf7"
    muted: str = "#9fb0c6"
    accent: str = "#6ee7ff"
    accent2: str = "#a78bfa"
    danger: str = "#ff6b8b"
    ok: str = "#6cffb5"

    particle_palette = ("#6ee7ff", "#a78bfa", "#6cffb5", "#ffd166")
    pulse_palette = ("#6ee7ff", "#a78bfa", "#ffd166")


class Theme:
    def __init__(self) -> None:
        self.colors = Colors()

    def apply(self, root: tk.Tk) -> None:
        root.configure(bg=self.colors.bg)

        style = ttk.Style(root)
        # Use default theme then customize colors.
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("App.TFrame", background=self.colors.bg)
        style.configure("Card.TFrame", background=self.colors.bg_card, relief="flat")

        style.configure(
            "TLabel",
            background=self.colors.bg,
            foreground=self.colors.text,
            font=("Segoe UI", 10),
        )

        style.configure(
            "Hero.TLabel",
            background=self.colors.bg_card,
            foreground=self.colors.text,
            font=("Segoe UI Semibold", 18),
        )
        style.configure(
            "Subhero.TLabel",
            background=self.colors.bg_card,
            foreground=self.colors.muted,
            font=("Segoe UI", 10),
        )
        style.configure(
            "CardTitle.TLabel",
            background=self.colors.bg_card,
            foreground=self.colors.text,
            font=("Segoe UI Semibold", 11),
        )
        style.configure(
            "Muted.TLabel",
            background=self.colors.bg_card,
            foreground=self.colors.muted,
            font=("Segoe UI", 9),
        )

        style.configure(
            "TSeparator",
            background=self.colors.border,
        )

        style.configure(
            "TScrollbar",
            background=self.colors.bg_card,
            troughcolor=self.colors.bg2,
            bordercolor=self.colors.border,
            arrowcolor=self.colors.muted,
            relief="flat",
        )

        style.configure(
            "TEntry",
            fieldbackground=self.colors.bg2,
            foreground=self.colors.text,
            bordercolor=self.colors.border,
            insertcolor=self.colors.text,
        )

        style.configure(
            "TFrame",
            background=self.colors.bg,
        )

        # Buttons (ttk)
        style.configure(
            "TButton",
            background=self.colors.bg2,
            foreground=self.colors.text,
            bordercolor=self.colors.border,
            focusthickness=0,
            focuscolor=self.colors.border,
            padding=(12, 8),
            font=("Segoe UI Semibold", 10),
        )
        style.map(
            "TButton",
            background=[("active", self.colors.border)],
            foreground=[("active", self.colors.text)],
        )
