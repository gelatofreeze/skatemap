"""Non-skate scenery: palms, rocks, eco-architecture, bubbles, sea life."""
import numpy as np
from math import sin, cos, pi, tau, radians
from .mesh import Z, unit, frames


def palm(S, pos, h=9.0, lean=0.25, yaw=0.0, rng=None, fronds=11, group="a", trunk="SC_palm_trunks"):
    rng = rng or np.random.default_rng(0)
    d = np.array([cos(yaw), sin(yaw), 0.0])
    t = np.linspace(0, 1, 14)
    trunk_path = (np.asarray(pos, float) + np.outer(t * h, Z)
             + np.outer(lean * h * t ** 2, d))
    rad = 0.30 - 0.14 * t + 0.10 * np.exp(-t * 9) + 0.015 * np.sin(t * 60)
    S.tube(trunk, "palm_trunk", trunk_path, rad, n=9, caps=False)
    top = trunk_path[-1]
    for k in range(3):
        a = k * 2.1 + yaw
        S.sphere("NC_palm_nuts", "coconut", top + np.array([0.28 * cos(a), 0.28 * sin(a), -0.25]), 0.17, n=8)
    V, F = [], []
    for f in range(fronds):
        a = yaw + f * tau / fronds + rng.uniform(-0.2, 0.2)
        L = h * rng.uniform(0.36, 0.48)
        rise = rng.uniform(0.25, 0.75)
        out = np.array([cos(a), sin(a), 0.0])
        side = np.array([-sin(a), cos(a), 0.0])
        s = np.linspace(0, 1, 18)
        rib = top + np.outer(L * s, out) + np.outer(L * (rise * s - (0.55 + rise) * s ** 2), Z)
        for i in range(1, 17):
            ll = L * 0.30 * sin(pi * (s[i] ** 0.75)) + 0.05
            a0, a1 = rib[i], rib[i] + 0.62 * (rib[i + 1] - rib[i])
            fwd = unit(rib[i + 1] - rib[i])
            for sg in (-1, 1):
                tip = sg * side * ll * 0.8 + fwd * ll * 0.45 - Z * ll * 0.5
                b = len(V)
                V += [a0, a1, a1 + tip, a0 + tip * 0.96]
                F.append((b, b + 1, b + 2, b + 3) if sg > 0 else (b + 3, b + 2, b + 1, b))
        b = len(V)                                     # the rib itself
        w = side * 0.035
        V += [rib[0] - w, rib[0] + w, rib[-1] + w * 0.2, rib[-1] - w * 0.2]
        F.append((b, b + 1, b + 2, b + 3))
    S.add("NC_palm_fronds_" + group, "palm_leaf", np.array(V), F)


def rock(S, pos, r, rng, name="SC_rocks"):
    n = 12
    th = np.linspace(0, tau, n, endpoint=False)
    ph = np.linspace(-pi / 2, pi / 2, n // 2 + 1)
    ax = r * rng.uniform(0.7, 1.3, 3) * np.array([1, 1, 0.65])
    k = rng.uniform(0, 6, 6)
    P = np.zeros((n, len(ph), 3))
    for i, t in enumerate(th):
        for j, p in enumerate(ph):
            bump = 1 + 0.16 * sin(3 * t + k[0]) * cos(2 * p + k[1]) + 0.10 * sin(5 * t + k[2] + 3 * p)
            P[i, j] = np.array(pos) + bump * ax * np.array([cos(p) * cos(t), cos(p) * sin(t), sin(p)])
    S.grid(name, "rock", P, cu=True)


def bush(S, pos, r, rng):
    for _ in range(int(rng.integers(3, 6))):
        o = rng.normal(0, r * 0.45, 3) * np.array([1, 1, 0.3])
        S.sphere("NC_bushes", "bush", np.array(pos) + o + np.array([0, 0, r * 0.3]),
                 r * rng.uniform(0.5, 0.85), n=10, squash=0.75)


def dome(S, pos, r, ribs=10, name="dome"):
    """Glass biodome with white ribs and a garden floor."""
    S.push(pos)
    t = np.linspace(0, pi / 2, 16)
    S.lathe("SC_" + name + "_glass", "glass_blue", np.c_[r * np.cos(t), r * np.sin(t)], n=48)
    S.lathe("SC_" + name + "_base", "shell_white", [(r + 0.5, -2.5), (r + 0.5, 0.5), (r - 0.1, 0.9), (r - 0.4, 0.5)], n=48)
    S.disc("SC_" + name + "_base", "lawn", (0, 0, 0.3), r)
    for k in range(ribs):
        a = k * tau / ribs
        arc = [(r * 1.005 * cos(u) * cos(a), r * 1.005 * cos(u) * sin(a), r * 1.005 * sin(u))
               for u in np.linspace(0.05, pi / 2, 14)]
        S.tube("SC_" + name + "_ribs", "shell_white", arc, 0.14, n=6, caps=False)
    for u in (0.45, 0.9, 1.25):
        ring = [(r * 1.005 * cos(u) * cos(a), r * 1.005 * cos(u) * sin(a), r * 1.005 * sin(u))
                for a in np.linspace(0, tau, 40, endpoint=False)]
        S.tube("SC_" + name + "_ribs", "shell_white", ring, 0.1, n=6, closed=True)
    S.sphere("NC_" + name + "_orb", "glow_cyan", (0, 0, r + 0.6), 0.6, n=12)
    S.pop()


def pod_tower(S, pos, h, r, name="tower", bands=5, accent="gel_cyan"):
    """White curvy tower with glass bands and a solar petal crown."""
    S.push(pos)
    zs = np.linspace(0, h, bands * 2 + 2)
    prof_r = lambda z: r * (0.72 + 0.28 * sin(pi * (z / h) ** 0.8) ** 1.0 + 0.10 * (1 - z / h))
    for i in range(len(zs) - 1):
        zz = np.linspace(zs[i], zs[i + 1], 6)
        mat = "glass_blue" if i % 2 else "shell_white"
        inset = 0.93 if i % 2 else 1.0
        S.lathe("SC_" + name, mat, [(prof_r(z) * inset, z) for z in zz], n=40)
        if i % 2 == 0:
            S.disc("SC_" + name, "shell_white", (0, 0, zs[i + 1]), prof_r(zs[i + 1]), n=40)
            S.disc("SC_" + name, "shell_white", (0, 0, zs[i]), prof_r(zs[i]), n=40, flip=True)
    rt = prof_r(h)
    S.lathe("SC_" + name, "shell_white", [(rt, h), (rt * 1.25, h + 0.6), (rt * 0.4, h + 1.6), (0.05, h + 2.0)], n=40)
    S.lathe("NC_" + name + "_ring", accent, [(rt * 1.5, h + 2.4), (rt * 1.62, h + 2.7), (rt * 1.5, h + 3.0), (rt * 1.38, h + 2.7), (rt * 1.5, h + 2.4)], n=48)
    for k in range(8):
        a = k * tau / 8
        c, s = cos(a), sin(a)
        q = np.array([[rt * 0.5, -0.9, h + 1.5], [rt * 2.1, -1.3, h + 3.6], [rt * 2.1, 1.3, h + 3.6], [rt * 0.5, 0.9, h + 1.5]])
        q = q @ np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
        S.add("NC_" + name + "_petals", "solar", q, [(0, 1, 2, 3)])
    S.pop()


def turbine(S, pos, h=42.0, blade=19.0, yaw=0.0, phase=0.0):
    S.push(pos, yaw)
    S.lathe("SC_turbines", "shell_white", [(1.5, -8), (1.35, 0), (0.95, h * 0.6), (0.7, h)], n=18)
    # nacelle along local x
    t = np.linspace(0, pi, 12)
    a = np.linspace(0, tau, 16, endpoint=False)
    P = np.stack([np.outer(np.ones(16), -3.2 * np.cos(t) + 0.4),
                  np.outer(np.cos(a), 1.15 * np.sin(t)),
                  np.outer(np.sin(a), 1.15 * np.sin(t)) + h + 0.6], -1)
    S.grid("SC_turbines", "shell_white", P, cu=True, flip=True)
    hub = np.array([3.9, 0, h + 0.6])
    S.sphere("SC_turbines", "gel_cyan", hub, 0.9, n=12)
    for k in range(3):
        ang = phase + k * tau / 3
        d = np.array([0, cos(ang), sin(ang)])
        e = np.array([0, -sin(ang), cos(ang)])
        s = np.linspace(0.04, 1, 14)
        chord = 1.7 * (1 - s) ** 0.8 + 0.25
        lead = hub + np.outer(s * blade, d) + np.outer(chord * 0.35, e)
        trail = hub + np.outer(s * blade, d) - np.outer(chord * 0.65, e)
        fr = np.array([0.22, 0, 0]) * (1 - s)[:, None]
        S.grid("NC_turbine_blades", "shell_white", np.stack([lead + fr, trail + fr * 0.2], 1), flip=True)
        S.grid("NC_turbine_blades", "shell_white", np.stack([trail - fr * 0.2, lead - fr], 1), flip=True)
    S.pop()


def fish(S, pos, L, yaw, mat="fish_orange"):
    n = 10
    t = np.linspace(0, pi, 9)
    a = np.linspace(0, tau, n, endpoint=False)
    body = np.stack([np.outer(np.ones(n), -0.5 * L * np.cos(t)),
                     np.outer(np.cos(a), 0.11 * L * np.sin(t) ** 0.8),
                     np.outer(np.sin(a), 0.24 * L * np.sin(t) ** 0.8)], -1)
    S.push(pos, yaw)
    S.grid("NC_fish", mat, body, cu=True)
    S.add("NC_fish", "fish_white", [[-0.45 * L, 0, 0], [-0.8 * L, 0, 0.26 * L], [-0.72 * L, 0, 0], [-0.8 * L, 0, -0.26 * L]],
          [(0, 1, 2, 3)])
    S.add("NC_fish", "fish_white", [[0.05 * L, 0, 0.2 * L], [-0.2 * L, 0, 0.42 * L], [-0.25 * L, 0, 0.2 * L]], [(0, 1, 2)])
    S.pop()


def dolphin(S, pos, yaw, L=2.8, arc=1.0):
    """Mid-leap dolphin: a tapered tube along an arc, plus fins."""
    S.push(pos, yaw)
    s = np.linspace(0, 1, 20)
    ang = (s - 0.5) * arc * 1.6
    R = L / (arc * 1.6)
    path = np.stack([R * np.sin(ang), np.zeros_like(s), R * np.cos(ang) - R * cos(arc * 0.8)], -1)
    rad = 0.36 * L / 2.8 * np.sin(pi * np.clip(s * 0.93 + 0.05, 0, 1)) ** 0.7 * (0.55 + 0.45 * s)
    S.tube("NC_dolphins", "dolphin", path, rad + 0.02, n=10, up=np.array([0, 1.0, 0]))
    mid = path[11]
    S.add("NC_dolphins", "dolphin", [mid + [0.25, 0, 0.3], mid + [-0.35, 0, 0.75], mid + [-0.3, 0, 0.3]], [(0, 1, 2)])
    tail = path[0]
    S.add("NC_dolphins", "dolphin", [tail, tail + [-0.35, 0.5, -0.15], tail + [-0.1, 0, -0.05], tail + [-0.35, -0.5, -0.15]],
          [(0, 1, 2, 3)])
    S.pop()


def sailboat(S, pos, yaw, L=9.0):
    S.push(pos, yaw)
    n = 14
    t = np.linspace(0, pi, 14)
    a = np.linspace(pi, tau, n)
    hull = np.stack([np.outer(np.ones(n), -0.5 * L * np.cos(t)),
                     np.outer(np.cos(a), 0.17 * L * np.sin(t) ** 0.6),
                     np.outer(np.sin(a), 0.14 * L * np.sin(t) ** 0.6) + 0.55], -1)
    S.grid("NC_boats", "shell_white", hull, flip=True)
    deck = np.stack([hull[0], hull[-1]], 0)
    S.grid("NC_boats", "wood", deck)
    S.tube("NC_boats", "chrome", [(0.4, 0, 0.5), (0.4, 0, L * 1.25)], 0.07, n=6)
    S.add("NC_boats", "sail", [[0.25, 0, 1.2], [0.25, 0, L * 1.2], [-L * 0.42, 0.25, 1.3]], [(0, 1, 2)])
    S.add("NC_boats", "sail", [[0.55, 0, 1.0], [0.55, 0, L * 1.05], [L * 0.46, -0.2, 0.9]], [(0, 2, 1)])
    S.pop()


def torus(S, name, mat, c, R, r, axis_yaw=None, n=64, m=14, tilt=0.0):
    """Ring. axis_yaw=None lies flat; otherwise it stands upright facing that yaw."""
    a = np.linspace(0, tau, n, endpoint=False)
    b = np.linspace(0, tau, m, endpoint=False)
    ca, sa = np.cos(a)[:, None], np.sin(a)[:, None]
    cb, sb = np.cos(b)[None, :], np.sin(b)[None, :]
    x, y, z = (R + r * cb) * ca, (R + r * cb) * sa, r * sb + 0 * ca
    P = np.stack([x, y, z], -1)
    if axis_yaw is not None:                      # stand it up: local z -> forward
        P = np.stack([P[..., 2], P[..., 0], P[..., 1]], -1)
        S.push(c, axis_yaw)
    else:
        S.push(c)
    S.grid(name, mat, P, cu=True, cv=True)
    S.pop()
