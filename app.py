from __future__ import annotations

import os
import sys
import time
import math
import random
import platform
from dataclasses import dataclass
from typing import Callable, Optional

import tkinter as tk
from tkinter import ttk

from src.ui.theme import Theme
from src.ui.widgets import Sidebar, Topbar, StatCard, NeonButton, LogConsole, Spacer
from src.ui.credits import CreditsOverlay
from src.core.effects import ParticleField, GlowPulse
from src.core.utils import clamp, fmt_bytes, fmt_uptime, rolling_hash


APP_NAME = "neuraforge"
APP_TAGLINE = "signal • synth • secure"
APP_VERSION = "1.0.0"

AUTHOR_FIRST = "Alex"
AUTHOR_LAST = "Dubois"

CREDITS_REVEAL_DELAY_MS = 50



@dataclass
class AppState:
    start_time: float
    runs: int = 0
    pulses: int = 0
    particles: int = 0
    bytes_processed: int = 0
    last_action: str = "idle"


class NeuraForgeApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title(f"{APP_NAME} • desktop")
        self.geometry("1120x680")
        self.minsize(980, 620)

        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self.theme = Theme()
        self.theme.apply(self)

        self.state = AppState(start_time=time.time())

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.topbar = Topbar(self, app_name=APP_NAME, tagline=APP_TAGLINE, version=APP_VERSION)
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.sidebar = Sidebar(
            self,
            on_nav=self._on_nav,
            on_run=self._on_run_demo,
            on_credits=self._on_show_credits,
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew")

        self.main = ttk.Frame(self, style="App.TFrame", padding=(18, 18, 18, 18))
        self.main.grid(row=1, column=1, sticky="nsew")
        self.main.rowconfigure(3, weight=1)
        self.main.columnconfigure(0, weight=1)

        self.hero = ttk.Frame(self.main, style="Card.TFrame", padding=(18, 16, 18, 16))
        self.hero.grid(row=0, column=0, sticky="ew")
        self.hero.columnconfigure(0, weight=1)

        self.hero_title = ttk.Label(
            self.hero,
            text="neuraforge console",
            style="Hero.TLabel",
        )
        self.hero_title.grid(row=0, column=0, sticky="w")

        self.hero_sub = ttk.Label(
            self.hero,
            text="A small interactive UI demo with animated credits for your OSINT challenge.",
            style="Subhero.TLabel",
        )
        self.hero_sub.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.hero_actions = ttk.Frame(self.hero, style="Card.TFrame")
        self.hero_actions.grid(row=0, column=1, rowspan=2, sticky="e")

        self.btn_run = NeonButton(self.hero_actions, text="Run Demo", command=self._on_run_demo)
        self.btn_run.grid(row=0, column=0, padx=(0, 10))

        self.btn_credits = NeonButton(self.hero_actions, text="Run Credits", command=self._on_show_credits)
        self.btn_credits.grid(row=0, column=1)

        self.stats = ttk.Frame(self.main, style="App.TFrame")
        self.stats.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        for i in range(4):
            self.stats.columnconfigure(i, weight=1)

        self.card_uptime = StatCard(self.stats, title="Uptime", value="0s", hint="Session runtime")
        self.card_uptime.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self.card_runs = StatCard(self.stats, title="Runs", value="0", hint="Demo executions")
        self.card_runs.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        self.card_particles = StatCard(self.stats, title="Particles", value="0", hint="Field intensity")
        self.card_particles.grid(row=0, column=2, sticky="ew", padx=(0, 12))

        self.card_bytes = StatCard(self.stats, title="Processed", value="0 B", hint="Fake workload")
        self.card_bytes.grid(row=0, column=3, sticky="ew")

        self.canvas_wrap = ttk.Frame(self.main, style="Card.TFrame", padding=(12, 12, 12, 12))
        self.canvas_wrap.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        self.canvas_wrap.columnconfigure(0, weight=1)

        self.canvas_title = ttk.Label(self.canvas_wrap, text="signal field", style="CardTitle.TLabel")
        self.canvas_title.grid(row=0, column=0, sticky="w")

        self.canvas = tk.Canvas(
            self.canvas_wrap,
            height=190,
            highlightthickness=0,
            bd=0,
            bg=self.theme.colors.bg_card,
        )
        self.canvas.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        self.particles = ParticleField(self.canvas, palette=self.theme.colors.particle_palette)
        self.pulse = GlowPulse(self.canvas, palette=self.theme.colors.pulse_palette)

        self.console = LogConsole(self.main, title="activity log")
        self.console.grid(row=3, column=0, sticky="nsew", pady=(14, 0))

        self.credits: Optional[CreditsOverlay] = None

        self._tick_job: Optional[str] = None
        self._fx_job: Optional[str] = None

        self._schedule_ticks()
        self._schedule_fx()

        self._log_env_banner()
        self.console.log("Ready. Use 'Run Demo' or 'Run Credits'.")

        self.bind("<Configure>", self._on_resize)

    def _on_nav(self, key: str) -> None:
        self.state.last_action = f"nav:{key}"
        self.console.log(f"Navigation → {key}")

        if key == "dashboard":
            self.hero_title.configure(text="neuraforge console")
            self.hero_sub.configure(text="A small interactive UI demo with animated credits for your OSINT challenge.")
        elif key == "telemetry":
            self.hero_title.configure(text="telemetry")
            self.hero_sub.configure(text="Fake metrics, pulses and particles. Nothing sensitive is exposed here.")
        elif key == "about":
            self.hero_title.configure(text="about neuraforge")
            self.hero_sub.configure(
                text="A fictional company UI demo. The credits reveal the author's name by design."
            )

    def _on_run_demo(self) -> None:
        self.state.runs += 1
        self.state.last_action = "run_demo"
        self.console.log("Run Demo → starting synthetic workload…")

        seed = int(time.time()) ^ (self.state.runs << 8)
        rng = random.Random(seed)

        total = 0
        payload = bytearray()
        for _ in range(120):
            x = rng.getrandbits(32)
            total ^= rolling_hash(x)
            payload.extend(x.to_bytes(4, "little"))

        processed = len(payload)
        self.state.bytes_processed += processed

        self.particles.boost(amt=24 + (self.state.runs % 8) * 4)
        self.pulse.kick(strength=0.6 + (self.state.runs % 3) * 0.12)

        self.console.log(f"Workload done → checksum=0x{total:08x}, processed={processed} bytes")
        self._sync_stats()

    def _on_show_credits(self) -> None:
        self.state.last_action = "credits"
        self.console.log("Run Credits → launching overlay…")

        if self.credits is not None:
            try:
                self.credits.destroy()
            except Exception:
                pass
            self.credits = None

        self.credits = CreditsOverlay(
            master=self,
            theme=self.theme,
            company_name=APP_NAME,
            author_first=AUTHOR_FIRST,
            author_last=AUTHOR_LAST,
            reveal_delay_ms=CREDITS_REVEAL_DELAY_MS,
            on_close=self._on_credits_close,
        )
        self.credits.show()

    def _on_credits_close(self) -> None:
        self.console.log("Credits closed.")
        self.state.last_action = "idle"

    def _schedule_ticks(self) -> None:
        if self._tick_job is not None:
            self.after_cancel(self._tick_job)

        def tick() -> None:
            self._sync_stats()
            self._tick_job = self.after(250, tick)

        self._tick_job = self.after(250, tick)

    def _schedule_fx(self) -> None:
        if self._fx_job is not None:
            self.after_cancel(self._fx_job)

        def frame() -> None:
            self.particles.step()
            self.pulse.step()
            self._fx_job = self.after(16, frame)  # ~60 fps

        self._fx_job = self.after(16, frame)

    def _sync_stats(self) -> None:
        up = time.time() - self.state.start_time
        self.card_uptime.set_value(fmt_uptime(up))
        self.card_runs.set_value(str(self.state.runs))
        self.card_particles.set_value(str(self.particles.count))
        self.card_bytes.set_value(fmt_bytes(self.state.bytes_processed))

    def _on_resize(self, _evt: tk.Event) -> None:
        try:
            self.canvas.configure(bg=self.theme.colors.bg_card)
        except Exception:
            pass

    def _log_env_banner(self) -> None:
        py = sys.version.split()[0]
        os_name = platform.system()
        os_ver = platform.version()
        self.console.log(f"{APP_NAME} v{APP_VERSION} • python {py} • {os_name}")
        self.console.log(f"Environment → {os_name} {os_ver}")

    def on_close(self) -> None:
        self.console.log("Shutting down…")
        try:
            if self._tick_job:
                self.after_cancel(self._tick_job)
            if self._fx_job:
                self.after_cancel(self._fx_job)
        except Exception:
            pass
        self.destroy()


def main() -> None:
    app = NeuraForgeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
