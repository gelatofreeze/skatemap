"""Mega-ramp construction: a side-profile 'turtle', ballistic gap maths,
and the ribbon builder that turns a 3D centreline into a ramp."""
import numpy as np
from math import sin, cos, atan2, sqrt, radians, pi
from .mesh import frames, Z, smoothstep

import json, os
_PHYS = json.load(open(os.path.join(os.path.dirname(__file__), "physics.json")))
G = _PHYS["gravity"]            # measured in game when available (tools/calibrate.py)
KEEP = _PHYS["speed_keep"]      # share of drop energy still held at a lip


class Prof:
    """Side profile of a ramp line in (x = distance, z = height).
    Tracks speed by energy so gaps can be sized. eff is the fraction of
    potential energy kept (friction, pumping losses); tune after play-test."""

    def __init__(self, x=0.0, z=0.0, h=0.0, z_start=None, eff=None):
        self.p = [(x, z)]
        self.lat = [0.0]
        self.h = h
        self.z0 = z if z_start is None else z_start
        self.eff = KEEP if eff is None else eff
        self.marks = {}
        self._lat = 0.0
        self.breaks = []          # indices where the ribbon is cut (gaps)

    @property
    def x(self): return self.p[-1][0]
    @property
    def z(self): return self.p[-1][1]

    def speed(self):
        return sqrt(max(0.0, 2 * G * (self.z0 - self.z) * self.eff))

    def _to(self, x, z):
        self.p.append((x, z))
        self.lat.append(self._lat)

    def line(self, L, step=1.0):
        n = max(1, int(L / step))
        for _ in range(n):
            self._to(self.x + cos(self.h) * L / n, self.z + sin(self.h) * L / n)
        return self

    def arc(self, R, dh, step=0.35, lat=0.0):
        """Turn by dh radians (positive curves upward) on radius R. lat is a
        sideways shift spread over the arc, used to let loops clear themselves."""
        n = max(2, int(abs(dh) * R / step))
        d = dh / n
        chord = 2 * R * sin(abs(d) / 2)
        l0 = self._lat
        for i in range(n):
            a = self.h + d / 2
            self._lat = l0 + lat * smoothstep(0, 1, (i + 1) / n)
            self._to(self.x + cos(a) * chord, self.z + sin(a) * chord)
            self.h += d
        return self

    def to_heading(self, R, deg):
        return self.arc(R, radians(deg) - self.h)

    def line_to_z(self, z):
        return self.line((z - self.z) / sin(self.h))

    def down_to(self, z, R, slope_deg=None):
        """Straight slope then a transition of radius R that ends flat at z."""
        drop = R * (1 - cos(self.h))
        if self.z - drop > z + 0.2:
            self.line_to_z(z + drop)
        return self.to_heading(R, 0)

    def mark(self, name):
        self.marks[name] = len(self.p) - 1
        return self

    def gap(self, land_deg=-28.0, knuckle=None, min_d=8.0):
        """Launch from the current point and start a landing ramp where the
        flight path has steepened to land_deg. The landing slope is tangent
        to the flight path and starts early, so short jumps still land."""
        v, h = self.speed(), self.h
        vx, vz = v * cos(h), v * sin(h)
        t = max((vz - vx * np.tan(radians(land_deg))) / G, min_d / vx)
        D = vx * t
        zl = self.z + vz * t - 0.5 * G * t * t
        hl = atan2(vz - G * t, vx)
        kn = 0.3 * D if knuckle is None else knuckle
        self.breaks.append(len(self.p))
        x0 = self.x
        Rk = 5.0
        kx, kz = Rk * sin(-hl), -Rk * (1 - cos(hl))        # knuckle arc offset
        self.h = 0.0
        self._to(x0 + D - kn * cos(hl) - kx - 1.5, zl - 0.3 - kn * sin(hl) - kz)
        self.line(1.5).arc(Rk, hl).line(kn)
        self.last_gap = D
        self.flight = (x0, zl - vz * t + 0.5 * G * t * t, vx, vz, t, self._lat)
        return self

    def points(self, origin, direction):
        """3D centreline. direction is a horizontal angle in radians."""
        d = np.array([cos(direction), sin(direction), 0.0])
        s = np.array([-sin(direction), cos(direction), 0.0])       # left
        p = np.array(self.p)
        lat = np.array(self.lat)
        return (np.asarray(origin, float) + p[:, :1] * d + p[:, 1:2] * Z + lat[:, None] * s)


def ribbon(S, name, path, width, mat, breaks=(), thick=0.45, edge=0.45,
           rim="gel_white", body="shell_white", curb=0.0, bank=None):
    """A ramp deck along a centreline: coloured riding surface, white edge
    stripes, white underside. Returns nothing; pylons are added separately."""
    path = np.asarray(path, float)
    cuts = [0, *breaks, len(path)]
    w = width / 2
    for a, b in zip(cuts[:-1], cuts[1:]):
        seg = path[a:b]
        if len(seg) < 2:
            continue
        bk = None if bank is None else np.asarray(bank)[a:b]
        S.sweep("SK_" + name, mat, seg, [(-w + edge, 0), (w - edge, 0)], bank=bk)
        S.sweep("SK_" + name, rim, seg, [(-w, curb), (-w + edge, 0)], bank=bk)
        S.sweep("SK_" + name, rim, seg, [(w - edge, 0), (w, curb)], bank=bk)
        S.sweep("SC_" + name, body, seg,
                [(w, curb), (w + 0.05, -thick * 0.5), (w - 0.6, -thick), (-w + 0.6, -thick),
                 (-w - 0.05, -thick * 0.5), (-w, curb)], bank=bk)
        # end caps
        T, N, R = frames(seg)
        for i, fl in ((0, True), (-1, False)):
            c = seg[i]
            q = [c + R[i] * w, c + R[i] * (w - 0.6) - N[i] * thick,
                 c - R[i] * (w - 0.6) - N[i] * thick, c - R[i] * w]
            S.add("SC_" + name, body, q, [(0, 1, 2, 3) if fl else (3, 2, 1, 0)])


def pylons(S, T, name, path, every=11.0, r=0.55, max_slope=0.9, min_h=1.2,
           mat="shell_white", skip=(), ok=None):
    """White tapered columns from the underside of a ramp to the ground."""
    path = np.asarray(path, float)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    tang = np.gradient(path, axis=0)
    nxt = every * 0.5
    for i in range(len(path)):
        if d[i] < nxt:
            continue
        nxt = d[i] + every
        t = tang[i] / (np.linalg.norm(tang[i]) + 1e-9)
        if abs(t[2]) > max_slope or any(a <= i < b for a, b in skip):
            continue
        x, y, z = path[i]
        if ok is not None and not ok(float(x), float(y)):
            continue
        g = max(T.h1(x, y), -6.0) - 0.5
        slope = abs(t[2]) / max(1e-3, (1 - t[2] ** 2) ** 0.5)
        top = z - 0.5 - r * 3.2 * slope
        if top - g < min_h:
            continue
        hgt = top - g
        r0, r = r, r * (1 + hgt / 45.0)        # taller columns are thicker
        prof = [(r * 1.5, 0), (r * 1.15, 0.5), (r * 0.8, hgt * 0.55), (r, hgt - 0.6), (r * 1.9, hgt)]
        S.push((x, y, g))
        S.lathe("SC_" + name + "_pylons", mat, prof, n=14)
        S.disc("SC_" + name + "_pylons", mat, (0, 0, hgt), r * 1.9, n=14)
        S.pop()
        r = r0
