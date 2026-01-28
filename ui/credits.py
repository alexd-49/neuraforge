from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import time
from typing import Callable, Optional

from src.core.utils import clamp


class CreditsOverlay(tk.Toplevel):
    """
    Fullscreen-ish overlay with animated credits.
    Reveals Author First/Last by design (OSINT challenge).
    """
    def __init__(
        self,
        master: tk.Tk,
        theme,
        company_name: str,
        author_first: str,
        author_last: str,
        reveal_delay_ms: int,
        on_close: Callable[[], None],
    ):
        super().__init__(master)
        self.theme = theme
        self.company_name = company_name
        self.author_first = author_first
        self.author_last = author_last
        self.reveal_delay_ms = reveal_delay_ms
        self.on_close_cb = on_close

        self.withdraw()
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Fill master
        self.geometry(self._master_geometry(master))
        self.configure(bg=self.theme.colors.bg)

        # Canvas for animation
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=self.theme.colors.bg)
        self.canvas.pack(fill="both", expand=True)

        self._running = False
        self._t0 = 0.0
        self._job: Optional[str] = None

        # text elements
        self._title_id = None
        self._sub_id = None
        self._scroll_ids = []

        # close bindings
        self.bind("<Escape>", lambda _e: self.close())
        self.bind("<Button-1>", lambda _e: self.close())

    def show(self) -> None:
        self.deiconify()
        self.grab_set()
        self._running = True
        self._t0 = time.time()
        self._setup_scene()
        self._loop()

    def close(self) -> None:
        if not self._running:
            return
        self._running = False
        try:
            if self._job:
                self.after_cancel(self._job)
        except Exception:
            pass
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
        self.on_close_cb()

    # -----------------
    # Scene / Animation
    # -----------------
    def _setup_scene(self) -> None:
        self.canvas.delete("all")
        w = max(1, self.winfo_width())
        h = max(1, self.winfo_height())

        # title
        self._title_id = self.canvas.create_text(
            w // 2,
            int(h * 0.18),
            text=self.company_name,
            fill=self.theme.colors.text,
            font=("Segoe UI Semibold", 42),
        )
        self._sub_id = self.canvas.create_text(
            w // 2,
            int(h * 0.18) + 54,
            text="credits sequence • click or press ESC to close",
            fill=self.theme.colors.muted,
            font=("Segoe UI", 12),
        )

        # scrolling credits block (start below screen)
        lines = self._credits_lines()
        start_y = h + 120
        x = w // 2
        self._scroll_ids = []
        dy = 30
        for i, line in enumerate(lines):
            cid = self.canvas.create_text(
                x,
                start_y + i * dy,
                text=line,
                fill=self.theme.colors.muted,
                font=("Segoe UI", 14),
            )
            self._scroll_ids.append(cid)

    def _credits_lines(self):
        # Author line is revealed later (see _loop)
        return [
            "neuraforge — internal demo build",
            "",
            "Design: Modern Tk",
            "UI: ttk + canvas",
            "Effects: particles + glow pulses",
            "Challenge: OSINT pivot",
            "",
            "Special thanks:",
            "• public corporate website",
            "• naming conventions",
            "• curious investigators",
            "",
            "Author: [REDACTED]",
            "",
            "— end —",
        ]

    def _loop(self) -> None:
        if not self._running:
            return

        t = (time.time() - self._t0)
        w = max(1, self.winfo_width())
        h = max(1, self.winfo_height())

        # subtle background gradient bands
        self._paint_background(w, h, t)

        # animate title “breathing”
        self._animate_title(w, h, t)

        # scroll credits
        self._scroll_credits(w, h, t)

        # reveal author after delay
        self._reveal_author_if_needed(t)

        self._job = self.after(16, self._loop)

    def _paint_background(self, w: int, h: int, t: float) -> None:
        self.canvas.delete("bg")
        bands = 14
        for i in range(bands):
            y0 = int(i * h / bands)
            y1 = int((i + 1) * h / bands)
            k = 0.08 + 0.06 * (1 + __import__("math").sin(t * 0.9 + i * 0.6)) / 2
            c = self._mix_hex(self.theme.colors.bg, self.theme.colors.bg2, k)
            self.canvas.create_rectangle(0, y0, w, y1, fill=c, outline="", tags="bg")

	# ✅ IMPORTANT : place le fond derrière le texte
        self.canvas.tag_lower("bg")

    def _animate_title(self, w: int, h: int, t: float) -> None:
        import math

        if self._title_id is None:
            return
        y = int(h * 0.18 + math.sin(t * 1.2) * 6)
        self.canvas.coords(self._title_id, w // 2, y)

        if self._sub_id is not None:
            self.canvas.coords(self._sub_id, w // 2, y + 54)

    def _scroll_credits(self, w: int, h: int, t: float) -> None:
        # Scroll speed
        speed = 46  # px/sec
        base = h + 120 - (t * speed)

        # reposition all credit lines
        dy = 30
        for i, cid in enumerate(self._scroll_ids):
            self.canvas.coords(cid, w // 2, base + i * dy)

        # fade out when reaching top
        for cid in self._scroll_ids:
            x, y = self.canvas.coords(cid)
            # 0..1 alpha proxy based on y position
            k = clamp((y - 40) / 220, 0.0, 1.0)
            col = self._mix_hex(self.theme.colors.bg, self.theme.colors.muted, k)
            self.canvas.itemconfigure(cid, fill=col)

    def _reveal_author_if_needed(self, t: float) -> None:
        # Replace "[REDACTED]" with actual author after delay
        if t * 1000 < self.reveal_delay_ms:
            return

        # Find the line that currently is "Author: [REDACTED]" and swap it once.
        for cid in self._scroll_ids:
            text = self.canvas.itemcget(cid, "text")
            if text.strip() == "Author: [REDACTED]":
                self.canvas.itemconfigure(cid, text=f"Author: {self.author_first} {self.author_last}")
                break

    # -----------------
    # Helpers
    # -----------------
    def _master_geometry(self, master: tk.Tk) -> str:
        master.update_idletasks()
        x = master.winfo_rootx()
        y = master.winfo_rooty()
        w = master.winfo_width()
        h = master.winfo_height()
        return f"{w}x{h}+{x}+{y}"

    def _mix_hex(self, a: str, b: str, t: float) -> str:
        # a and b are "#rrggbb"
        t = clamp(t, 0.0, 1.0)
        ar, ag, ab = int(a[1:3], 16), int(a[3:5], 16), int(a[5:7], 16)
        br, bg, bb = int(b[1:3], 16), int(b[3:5], 16), int(b[5:7], 16)
        rr = int(ar + (br - ar) * t)
        gg = int(ag + (bg - ag) * t)
        bb2 = int(ab + (bb - ab) * t)
        return f"#{rr:02x}{gg:02x}{bb2:02x}"
