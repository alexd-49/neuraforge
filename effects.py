from __future__ import annotations

import random
import math
from dataclasses import dataclass
from typing import List, Tuple, Sequence

from .utils import clamp


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    r: float
    alpha: float
    hue_idx: int
    item: int = -1


class ParticleField:
    """
    Lightweight particle field for a modern “signal” feel.
    Works on a tkinter Canvas; draws small circles with motion and fade.
    """
    def __init__(self, canvas, palette: Sequence[str]) -> None:
        self.canvas = canvas
        self.palette = list(palette)
        self._rng = random.Random(1337)

        self.particles: List[Particle] = []
        self._boost = 0
        self.count = 0

        self._spawn(42)

    def boost(self, amt: int = 16) -> None:
        self._boost += max(0, amt)

    def _spawn(self, n: int) -> None:
        w = max(1, int(self.canvas.winfo_width()))
        h = max(1, int(self.canvas.winfo_height()))
        for _ in range(n):
            x = self._rng.random() * w
            y = self._rng.random() * h
            a = 0.25 + self._rng.random() * 0.75
            r = 1.2 + self._rng.random() * 2.6
            vx = (self._rng.random() - 0.5) * 0.9
            vy = (self._rng.random() - 0.5) * 0.6
            idx = self._rng.randrange(0, len(self.palette))
            p = Particle(x=x, y=y, vx=vx, vy=vy, r=r, alpha=a, hue_idx=idx)
            self.particles.append(p)

    def step(self) -> None:
        w = max(1, int(self.canvas.winfo_width()))
        h = max(1, int(self.canvas.winfo_height()))

        if self._boost > 0:
            add = min(8, self._boost)
            self._boost -= add
            self._spawn(add)

        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vx += (self._rng.random() - 0.5) * 0.02
            p.vy += (self._rng.random() - 0.5) * 0.02
            p.vx = clamp(p.vx, -1.2, 1.2)
            p.vy = clamp(p.vy, -0.9, 0.9)

            if p.x < 0 or p.x > w:
                p.vx *= -0.9
                p.x = clamp(p.x, 0, w)
            if p.y < 0 or p.y > h:
                p.vy *= -0.9
                p.y = clamp(p.y, 0, h)

            p.alpha += (self._rng.random() - 0.45) * 0.03
            p.alpha = clamp(p.alpha, 0.18, 1.0)

        self._render()
        self.count = len(self.particles)

        if len(self.particles) > 160:
            for _ in range(len(self.particles) - 160):
                old = self.particles.pop(0)
                if old.item != -1:
                    try:
                        self.canvas.delete(old.item)
                    except Exception:
                        pass

    def _render(self) -> None:
        for p in self.particles:
            c = self.palette[p.hue_idx % len(self.palette)]
            r = p.r

            x0, y0 = p.x - r, p.y - r
            x1, y1 = p.x + r, p.y + r

            if p.item == -1:
                p.item = self.canvas.create_oval(x0, y0, x1, y1, fill=c, outline="")
            else:
                self.canvas.coords(p.item, x0, y0, x1, y1)
                if p.alpha > 0.9 and self._rng.random() < 0.05:
                    p.hue_idx = (p.hue_idx + 1) % len(self.palette)
                    c = self.palette[p.hue_idx]
                self.canvas.itemconfigure(p.item, fill=c)


@dataclass
class Pulse:
    cx: float
    cy: float
    r: float
    vr: float
    life: float
    item: int = -1


class GlowPulse:
    """
    Expanding rings to mimic a modern glow pulse.
    """
    def __init__(self, canvas, palette: Sequence[str]) -> None:
        self.canvas = canvas
        self.palette = list(palette)
        self._rng = random.Random(2024)
        self.pulses: List[Pulse] = []
        self._kick = 0.0

        self.kick(0.35)

    def kick(self, strength: float = 0.5) -> None:
        self._kick = max(self._kick, strength)

    def step(self) -> None:
        w = max(1, int(self.canvas.winfo_width()))
        h = max(1, int(self.canvas.winfo_height()))

        if self._kick > 0 and self._rng.random() < 0.20:
            self._spawn(w, h, self._kick)
            self._kick *= 0.85
        elif self._rng.random() < 0.01:
            self._spawn(w, h, 0.22)

        alive: List[Pulse] = []
        for p in self.pulses:
            p.r += p.vr
            p.life -= 0.02
            if p.life > 0:
                alive.append(p)
        self.pulses = alive

        self._render()

        if len(self.pulses) > 8:
            for extra in self.pulses[:-8]:
                if extra.item != -1:
                    try:
                        self.canvas.delete(extra.item)
                    except Exception:
                        pass
            self.pulses = self.pulses[-8:]

    def _spawn(self, w: int, h: int, strength: float) -> None:
        cx = w * (0.22 + self._rng.random() * 0.56)
        cy = h * (0.28 + self._rng.random() * 0.44)
        r0 = 6 + self._rng.random() * 22
        vr = 1.6 + strength * 3.2
        life = 0.65 + strength * 0.8
        self.pulses.append(Pulse(cx=cx, cy=cy, r=r0, vr=vr, life=life))

    def _render(self) -> None:
        for i, p in enumerate(self.pulses):
            c = self.palette[i % len(self.palette)]
            x0, y0 = p.cx - p.r, p.cy - p.r
            x1, y1 = p.cx + p.r, p.cy + p.r
            if p.item == -1:
                p.item = self.canvas.create_oval(x0, y0, x1, y1, outline=c, width=2)
            else:
                self.canvas.coords(p.item, x0, y0, x1, y1)
                self.canvas.itemconfigure(p.item, outline=c)
