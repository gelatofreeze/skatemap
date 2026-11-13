"""Frutiger Air: the island layout. Everything is placed here."""
import numpy as np
from math import sin, cos, pi, tau, radians, atan2, hypot
from .mesh import Scene, Z, smooth_path, resample, smoothstep, unit, frames
from .terrain import Terrain, sd_circle, sd_box, sd_path
from .mega import Prof, ribbon, pylons
from . import skate as sk, scenery as sc
from . import v2
from .v2 import MID_R

DECK_Z = 45.0        # top of the Spire, where every mega line starts
HILL_Z = 12.3
BW_Z = 2.0           # boardwalk level
SEA_Z = 0.0
RING_R = 52.0        # inner ring path


def ring_z(th):
    return 5.6 + 1.2 * np.cos(th)


def bw_r(th):
    return Terrain.coast(th) - 22.0


def polar(r, deg, z=0.0):
    a = radians(deg)
    return np.array([r * cos(a), r * sin(a), z])


class World:
    def __init__(self):
        self.S = Scene()
        self.T = Terrain()
        self.late = []          # work that needs the finished terrain
        self.keepout = []       # elevated paths that scenery must avoid
        self.wall_gaps = []     # boardwalk seawall openings (deg, half-width deg)
        self.notes = {}
        self.i2_keep = []       # obstacles on the second island that pylons must miss
        self.flow_path = flow_path


# ------------------------------------------------------------------ hub ---
def hub(W):
    S, T = W.S, W.T
    T.pad(sd_circle((0, 0), 19), HILL_Z, 16)
    S.disc("SK_hub_plaza", "pave_blue", (0, 0, HILL_Z), 19.5, n=96)
    S.disc("NC_decals", "gel_white", (0, 0, HILL_Z + 0.012), 19.5, n=96, r0=18.7)
    S.disc("NC_decals", "gel_cyan", (0, 0, HILL_Z + 0.012), 10.2, n=96, r0=9.6)
    S.lathe("SC_hub_plaza", "shell_white", [(19.5, HILL_Z - 3), (19.5, HILL_Z)], n=96)
    H = DECK_Z - HILL_Z
    S.push((0, 0, HILL_Z))
    zs = np.linspace(0, 1, 40)
    shaft_r = lambda u: 4.7 - 1.3 * np.sin(pi * np.clip(u / 0.8, 0, 1)) ** 0.8 + 8.6 * smoothstep(0.72, 1.0, u) ** 2.2
    S.lathe("SC_spire", "glass_blue", np.c_[shaft_r(zs), zs * (H - 0.45)], n=64)
    S.lathe("SC_spire", "shell_white", [(6.4, 0), (5.7, 0.6), (5.0, 1.5), (4.72, 1.6)], n=64)
    for k in range(3):
        u = np.linspace(0, 1, 90)
        a = k * tau / 3 + u * tau * 1.2
        rr = shaft_r(u) + 0.16
        S.tube("SC_spire_ribs", "shell_white", np.c_[rr * np.cos(a), rr * np.sin(a), u * (H - 0.5)], 0.2, n=8, caps=False)
    S.disc("SK_spire_deck", "gel_white", (0, 0, H), 13.0, n=120)
    S.disc("NC_decals", "gel_cyan", (0, 0, H + 0.012), 6.6, n=120, r0=6.0)
    S.disc("NC_decals", "gel_lime", (0, 0, H + 0.012), 2.2, n=60)
    S.lathe("SC_spire", "shell_white", [(13.0, H - 0.45), (13.2, H - 0.22), (13.0, H)], n=120)
    S.pop()
    for a0, a1 in ((161, 199), (251, 289), (341, 424)):
        S.lathe("SC_spire_rail", "glass_frost", [(12.85, DECK_Z), (12.85, DECK_Z + 1.1)], n=28, a0=radians(a0), a1=radians(a1))
        arc = [(12.85 * cos(t), 12.85 * sin(t), DECK_Z + 1.12) for t in np.linspace(radians(a0), radians(a1), 28)]
        S.tube("GR_spire_rail", "chrome", arc, 0.05, n=8)
        S.grind(arc)
    # halo and orb floating above the deck
    sc.torus(S, "NC_spire_halo", "gel_white", (0, 0, DECK_Z + 12), 9.0, 0.38)
    sc.torus(S, "NC_spire_halo", "glow_cyan", (0, 0, DECK_Z + 12), 9.0, 0.12, m=8)
    S.sphere("NC_spire_orb", "orb", (0, 0, DECK_Z + 12), 3.3, n=48)
    for deg in (0, 180, 270):
        u = np.linspace(0, 1, 20)
        a = radians(deg)
        rr = 12.7 - 3.7 * u ** 1.6
        S.tube("NC_spire_halo", "shell_white", np.c_[rr * cos(a), rr * sin(a), DECK_Z + 12 * u ** 0.7], 0.16 - 0.08 * u, n=8)
    S.empty("spawn", (0, 0, DECK_Z + 0.15), yaw=radians(90))


# ---------------------------------------------------------- flow paths ---
def flow_path(W, name, ctrl, width=6.0, mat="path_aqua", pad=True, step=1.0):
    """Ground-level smooth concrete path through control points."""
    path = smooth_path(ctrl, step)
    ribbon(W.S, name, path, width, mat, thick=1.6, edge=0.35)
    if pad:
        sdf = sd_path(path, width / 2 + 0.5)
        zz = path[:, 2].copy()
        W.T.pad(sdf, lambda x, y: zz[sdf(x, y, True)[1]], 5)
    return path


def ring_and_spurs(W):
    S, T = W.S, W.T
    th = np.linspace(0, tau, 260, endpoint=False)
    path = np.c_[RING_R * np.cos(th), RING_R * np.sin(th), ring_z(th)]
    T.pad(lambda x, y: np.abs(np.hypot(x, y) - RING_R) - 3.6,
          lambda x, y: ring_z(np.arctan2(y, x)), 5)
    S.sweep("SK_ring", "path_aqua", path, [(-2.65, 0), (2.65, 0)], closed=True)
    S.sweep("SK_ring", "gel_white", path, [(-3.0, 0), (-2.65, 0)], closed=True)
    S.sweep("SK_ring", "gel_white", path, [(2.65, 0), (3.0, 0)], closed=True)
    S.sweep("SC_ring", "shell_white", path, [(3.0, 0), (3.0, -0.6)], closed=True)
    S.sweep("SC_ring", "shell_white", path, [(-3.0, -0.6), (-3.0, 0)], closed=True)
    # hill runs: hilltop down to the ring
    for deg in (0, 45, 180, 270):
        a = radians(deg)
        flow_path(W, "hillrun_%d" % deg,
                  [polar(30.5, deg, HILL_Z), polar(36, deg, HILL_Z - 0.8), polar(44, deg, float(ring_z(a)) + 1.4),
                   polar(49.5, deg, float(ring_z(a)))], width=5.0, mat="gel_lime")


# -------------------------------------------------------------- megas ---
def build_mega(W, name, prof, deg, width, mat, pad_from=None, pad_z=None, skip=()):
    S, T = W.S, W.T
    pts = prof.points((0, 0, 0), radians(deg))
    ribbon(S, name, pts, width, mat, breaks=prof.breaks)
    okp = lambda x, y: hypot(x, y) > 33 and bool(T.clear_of_pads(np.array([x]), np.array([y]), 0.8)[0])
    W.late.append(lambda: pylons(S, T, name, pts, skip=skip, ok=okp if pad_from is None else None))
    W.keepout.append(sd_path(pts[::3], width / 2 + 3))
    if pad_from is not None:
        T.pad(sd_path(pts[pad_from:], width / 2 + 2.5), pad_z, 6)
    W.notes[name] = dict(gap=getattr(prof, "last_gap", 0), end_r=prof.x, end_z=prof.z)
    return pts


def end_quarter(W, name, pts, width, deck=3.0):
    """Deck and coping on top of a quarter pipe that ends a mega line."""
    S = W.S
    e = pts[-1]
    d = unit(np.array([pts[-1][0] - pts[-6][0], pts[-1][1] - pts[-6][1], 0]))
    yaw = atan2(d[1], d[0])
    S.push(e, yaw)
    S.box("SK_" + name + "_deck", "shell_white", (0, -width / 2, -e[2] - 1), (deck, width / 2, 0.0), mats={"top": "gel_white"})
    sk.coping(S, name + "_lip", (0, -width / 2, 0.02), (0, width / 2, 0.02), r=0.06)
    S.pop()


def bliss_drop(W):
    R = 24.0
    lip = 11.5
    low = lip - R * (1 - cos(radians(24)))
    p = Prof(MID_R, DECK_Z).line(2.0).to_heading(8, -48)
    p.line_to_z(low + R * (1 - cos(radians(48)))).to_heading(R, 24)
    p.gap(-30)
    p.down_to(3.2, 14)
    g = len(p.p) - 12
    p.line(8).to_heading(9.5, 78)
    pts = build_mega(W, "bliss_drop", p, 225, 10.0, "gel_lime", pad_from=g, pad_z=3.2)
    end_quarter(W, "bliss_drop", pts, 10.0)


def aurora_loop(W):
    S = W.S
    R = 26.0
    p = Prof(MID_R, DECK_Z).line(2.0).to_heading(8, -45)
    p.line_to_z(14.5 + R * (1 - cos(radians(45)))).to_heading(R, 0).line(3)
    i0 = len(p.p)
    p.arc(13, radians(60), lat=1.8).arc(6.5, radians(240), lat=5.6).arc(13, radians(60), lat=1.8)
    i1 = len(p.p)
    p.h -= tau
    Rk = 22.0
    low = 9.0 - Rk * (1 - cos(radians(22)))
    p.line(5).to_heading(60, -10).line_to_z(low + Rk * (1 - cos(radians(10)))).to_heading(Rk, 22)
    p.gap(-30)
    fl = p.flight
    p.down_to(1.7, 14).line(16).to_heading(8, 76)
    pts = build_mega(W, "aurora_loop", p, 135, 8.0, "gel_violet", skip=[(i0 - 4, i1 + 4)])
    end_quarter(W, "aurora_loop", pts, 8.0)
    # white hoop frame around the loop, and a glowing ring to jump through
    d = np.array([cos(radians(135)), sin(radians(135)), 0])
    left = np.array([-d[1], d[0], 0])
    x0, z0, vx, vz, t, lat = fl
    for k, (frac, Rr, mat) in enumerate(((0.5, 7.5, "glow_magenta"), (0.3, 6.5, "glow_cyan"), (0.7, 6.5, "glow_lime"))):
        tt = t * frac
        c = d * (x0 + vx * tt) + Z * (z0 + vz * tt - 4.905 * tt * tt + 1.0) + left * lat
        sc.torus(S, "NC_aurora_rings", mat, c, Rr, 0.22, axis_yaw=radians(135), m=10)
        sc.torus(S, "NC_aurora_rings", "gel_white", c, Rr + 0.5, 0.3, axis_yaw=radians(135), m=10)
    W.notes["aurora_loop"]["ring"] = (d * (x0 + vx * t / 2)).round(1).tolist()


def splash(W):
    S, T = W.S, W.T
    R = 30.0
    p = Prof(MID_R, DECK_Z).line(2.0).to_heading(8, -42)
    p.line_to_z(17 + R * (cos(radians(4)) - cos(radians(42)))).to_heading(R, -4)
    p.line((166 - p.x) / cos(radians(4)), step=1.5)
    Rk = 22.0
    low = 7.0 - Rk * (1 - cos(radians(20)))
    p.to_heading(75, -14).line_to_z(low + Rk * (1 - cos(radians(14)))).to_heading(Rk, 20)
    p.gap(-28)
    p.down_to(1.4, 14).line(16).to_heading(7, 74)
    pts = build_mega(W, "splash", p, 90, 9.0, "gel_orange")
    end_quarter(W, "splash", pts, 9.0)
    return pts


def splash_pad_and_return(W, pts):
    S = W.S
    c = np.array([pts[-30][0], pts[-30][1], 0.0])
    S.push(c)
    S.lathe("SC_splash_pad", "shell_white", [(4.0, -1.2), (13.5, 0.2), (15.2, 0.9), (15.2, 1.32)], n=72)
    S.disc("SK_splash_pad", "gel_lime", (0, 0, 1.32), 15.2, n=72)
    S.disc("SK_splash_pad", "gel_white", (0, 0, 1.33), 15.2, n=72, r0=14.4)
    S.pop()
    # reef walk: floating bridge from the pad back to the boardwalk
    a_end = radians(58)
    end = np.array([(bw_r(a_end) + 5.2) * cos(a_end), (bw_r(a_end) + 5.2) * sin(a_end), BW_Z])
    ctrl = [c + [14, -4, 1.34], c + [40, -18, 1.5], c + [70, -50, 1.5], end + [30, 26, 1.6 - BW_Z], end + [8, 6, 0], end]
    path = smooth_path(ctrl, 1.0)
    path[:, 2] += 0.45 * np.sin(np.linspace(0, 9 * tau, len(path))) ** 2 * smoothstep(0, 12, np.minimum(np.arange(len(path)), len(path) - 1 - np.arange(len(path))))
    ribbon(S, "reef_walk", path, 4.0, "gel_aqua", thick=0.4, edge=0.3)
    W.late.append(lambda: pylons(S, W.T, "reef_walk", path, every=9, r=0.3, min_h=0.3))
    W.wall_gaps.append((58, 3.0))
    W.keepout.append(sd_path(path[::4], 6))


def aqueduct(W):
    S, T = W.S, W.T
    R = 20.0
    p = Prof(MID_R, DECK_Z).line(2.0).to_heading(8, -50)
    p.line_to_z(13.5 + R * (cos(radians(3)) - cos(radians(50)))).to_heading(R, -3)
    i_flat = len(p.p) - 1
    p.line(52, step=0.8)
    pts = p.points((0, 0, 0), radians(-45))
    roll = pts[:i_flat + 1]
    ribbon(S, "aqueduct_rollin", roll, 8.0, "gel_aqua")
    W.late.append(lambda: pylons(S, T, "aqueduct", roll))
    W.keepout.append(sd_path(pts[::3], 8))
    E = pts[-1]
    f = np.array([cos(radians(-45)), sin(radians(-45)), 0])
    r_ = np.array([f[1], -f[0], 0])
    ctrl2 = [(0, 0), (8, 0), (17, 7), (18, 19), (8, 27), (3, 38), (9, 50), (17, 60), (22, 70), (24, 80)]
    snake = np.array([E + f * a + r_ * b for a, b in ctrl2])
    snake = smooth_path(snake, 0.8)[1:]
    path = resample(np.vstack([pts[i_flat:], snake]), 0.8)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path[:, :2], axis=0), axis=1))]
    Ltot = s[-1]
    z_end = BW_Z + 0.004
    path[:, 2] = np.where(s < 52, path[0, 2] - s * np.tan(radians(3)),
                          (path[0, 2] - 52 * np.tan(radians(3))) + (z_end - (path[0, 2] - 52 * np.tan(radians(3))))
                          * smoothstep(52, Ltot - 10, s) ** 0.9)
    # section: an arc of angle alpha about the bottom; flat -> U -> full pipe
    def alpha(u):
        if u < 10: return 0.1 + (pi - 0.1) * smoothstep(0, 10, u)
        if u < 16: return pi + (tau - 0.03 - pi) * smoothstep(10, 16, u)
        if u < 42: return tau - 0.03
        if u < 50: return tau - 0.03 + (2.2 - tau + 0.03) * smoothstep(42, 50, u)
        if u < Ltot - 14: return 2.2
        return 2.2 + (0.1 - 2.2) * smoothstep(Ltot - 14, Ltot - 1, u)
    K = 41
    secs = np.zeros((len(path), K, 2))
    outs = np.zeros((len(path), K, 2))
    for i, u in enumerate(s):
        al = alpha(u)
        chord = 8.0 if u < 30 else 7.13
        rr = 4.0 if al >= pi else min((chord / 2) / sin(al / 2), 4000.0)
        if u >= 50: rr = max(4.0, (7.13 / 2) / sin(al / 2)) if al < 2.2 else 4.0
        ph = np.linspace(-al / 2, al / 2, K)
        secs[i] = np.c_[rr * np.sin(ph), rr * (1 - np.cos(ph))]
        outs[i] = np.c_[(rr + 0.28) * np.sin(ph), rr - (rr + 0.28) * np.cos(ph)]
    a, b = int(np.searchsorted(s, 16)), int(np.searchsorted(s, 42))
    S.sweep_var("SK_aqueduct", "gel_aqua", path[:a + 1], secs[:a + 1])
    S.sweep_var("SK_aqueduct_pipe", "glass_pipe", path[a:b + 1], secs[a:b + 1])
    S.sweep_var("SK_aqueduct", "gel_aqua", path[b:], secs[b:])
    out = outs
    for i0, i1 in ((0, a + 1), (b, len(path))):
        S.sweep_var("SC_aqueduct_shell", "shell_white", path[i0:i1], out[i0:i1], flip=True)
        for e in (0, -1):
            rim = np.stack([secs[i0:i1, e], out[i0:i1, e]], 1)
            S.sweep_var("SC_aqueduct_shell", "gel_white", path[i0:i1], rim if e == 0 else rim[:, ::-1], flip=True)
    # copings along the open channel edges
    T_, N_, R_ = frames(path)
    for e in (0, -1):
        edge = path + secs[:, e, 0, None] * R_ + (secs[:, e, 1, None] - 0.05) * N_
        m = int(np.searchsorted(s, 50))
        S.tube("NC_coping", "chrome", edge[m:-8], 0.06, n=8)
        S.grind(edge[m:-8])
    low = path[int(np.searchsorted(s, 50)):]
    sdf = sd_path(low, 5.2)
    zz = low[:, 2] - 0.45
    T.cap(sdf, lambda x, y: zz[sdf(x, y, True)[1]], 6)
    W.keepout.append(sd_path(path[::4], 8))
    W.late.append(lambda: pylons(S, T, "aqueduct", path[:int(np.searchsorted(s, 95))] - np.array([0, 0, 0.5]), every=9, min_h=1.0,
                                 skip=[(a - 6, b + 6)]))
    # aquarium around the glass pipe
    mid = path[(a + b) // 2]
    S.push((mid[0], mid[1], 0), radians(-45))
    z0, z1 = mid[2] - 3.0, mid[2] + 11.0
    S.box("SC_aquarium", "tank_water", (-12, -8, z0), (12, 8, z1))
    S.box("SC_aquarium_frame", "shell_white", (-12.6, -8.6, z0 - 0.8), (12.6, 8.6, z0))
    S.box("SC_aquarium_frame", "shell_white", (-12.6, -8.6, z1), (12.6, 8.6, z1 + 0.7))
    for x in (-12.3, 12.3):
        for y in (-8.3, 8.3):
            S.tube("SC_aquarium_frame", "shell_white", [(x, y, z0), (x, y, z1)], 0.3, n=8, caps=False)
    for x in (-9, 9):
        for y in (-5.5, 5.5):
            S.push((x, y, 0))
            S.lathe("SC_aquarium_frame", "shell_white", [(1.6, -1), (1.1, 1.5), (0.9, z0 - 2.4), (1.7, z0 - 0.8)], n=16)
            S.pop()
    rng = np.random.default_rng(11)
    S.box("NC_aquarium_sand", "sand", (-11.9, -7.9, z0 + 0.02), (11.9, 7.9, z0 + 0.35))
    for k in range(70):
        x, y, z = rng.uniform(-10.5, 10.5), rng.uniform(-6.8, 6.8), rng.uniform(z0 + 1.2, z1 - 0.8)
        if hypot(y, z - (mid[2] + 4.0)) < 5.0:
            continue
        v2.real_fish(S, (x, y, z), rng.uniform(0.7, 1.5), rng.choice([0, pi]) + rng.uniform(-0.5, 0.5), kind="clown")
    for k in range(16):
        x, y = rng.uniform(-10.5, 10.5), rng.choice([-1, 1]) * rng.uniform(5.3, 7.0)
        if k % 3:
            v2.anemone(S, (x, y, z0 + 0.3), rng.uniform(0.7, 1.3), rng, mat=("anemone", "glow_magenta", "gel_violet")[k % 3] if k % 5 else "anemone")
        else:
            v2.coral(S, (x, y, z0 + 0.3), rng.uniform(1.6, 2.8), rng)
    for k in range(14):
        x, y = rng.uniform(-10, 10), rng.choice([-1, 1]) * rng.uniform(5.2, 7)
        S.sphere("NC_aquarium_bubbles", "bubble", (x, y, rng.uniform(z0 + 1, z1 - 1)), rng.uniform(0.12, 0.4), n=10)
    S.pop()


# ---------------------------------------------------------- boardwalk ---
def boardwalk(W):
    S, T = W.S, W.T
    th = np.linspace(0, tau, 520, endpoint=False)
    rb = bw_r(th)
    path = np.c_[rb * np.cos(th), rb * np.sin(th), np.full_like(th, BW_Z)]
    T.pad(lambda x, y: np.abs(np.hypot(x, y) - bw_r(np.arctan2(y, x))) - 6.0, BW_Z, 5)
    S.sweep("SK_boardwalk", "boardwalk", path, [(-4.1, 0), (4.5, 0)], closed=True)
    S.sweep("SK_boardwalk", "gel_white", path, [(-4.6, 0), (-4.1, 0)], closed=True)
    S.sweep("SC_boardwalk", "marble", path, [(-4.6, -2.2), (-4.6, 0)], closed=True)
    S.sweep("SC_boardwalk", "marble", path, [(4.5, 0), (4.5, -2.6)], closed=True)
    # seawall ledge on the outer edge, opened where bridges leave
    deg = np.degrees(th)
    keep = np.ones(len(th), bool)
    for g, hw in W.wall_gaps:
        keep &= np.abs((deg - g + 180) % 360 - 180) > hw
    idx = np.where(keep)[0]
    runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
    if len(runs) > 1 and runs[0][0] == 0 and runs[-1][-1] == len(th) - 1:
        runs = [np.r_[runs[-1], runs[0]]] + runs[1:-1]
    from .mesh import frames
    for run in runs:
        seg = path[run]
        S.sweep("SK_seawall", "marble", seg, [(4.0, 0), (4.0, 0.42)])
        S.sweep("SK_seawall", "glass_frost", seg, [(4.0, 0.42), (4.5, 0.42)])
        S.sweep("SK_seawall", "marble", seg, [(4.5, 0.42), (4.5, 0)])
        S.sweep("NC_seawall_glow", "glow_cyan", seg, [(3.985, 0.30), (3.985, 0.34)])
        Tn, Nn, Rn = frames(seg)
        for off in (4.0, 4.5):
            S.grind(seg + Rn * off + Z * 0.42)


# -------------------------------------------------------------- plaza ---
def plaza(W):
    S, T = W.S, W.T
    X0 = 56.0
    W_ = 36.0
    L0 = BW_Z - 0.004 + 3 * sk.RISE
    L1 = L0 + 5 * sk.RISE
    L2 = L1 + 8 * sk.RISE
    L3 = L2 + 12 * sk.RISE
    xs = [0.0, 28.0, 52.0, 70.0, 82.0, 116.0]      # terrace front edges (local x)
    lv = [L3, L2, L1, L0, BW_Z - 0.004]
    T.pad(sd_box((X0 + 58, 0), (56, W_ - 1)), BW_Z - 0.1, 4, deck=True)
    S.push((X0, 0, 0))
    for i in range(5):
        mat = "pave_blue" if i % 2 == 0 else "pave_white"
        S.box("SK_plaza_L%d" % (3 - i) if i < 4 else "SK_plaza_beach", "marble",
              (xs[i], -W_, -1.0), (xs[i + 1] + (0.0 if i < 4 else 0), W_, lv[i]), mats={"top": mat})
    # white inlay bands and edge trim
    for i in range(4):
        S.box("NC_decals", "gel_white", (xs[i + 1] - 0.5, -W_, lv[i]), (xs[i + 1], W_, lv[i] + 0.012))

    def drop(i, n, items):
        """Furnish the drop from terrace i down n stairs."""
        x = xs[i + 1]
        for kind, y0, y1, *opt in items:
            S.push((x, (y0 + y1) / 2, lv[i + 1]))
            w = y1 - y0
            nm = "plaza_d%d" % i
            if kind == "stairs":
                sk.stairs(S, nm + "_stairs", n, w, rails=opt[0] if opt else (), hubbas=opt[1] if len(opt) > 1 else ())
            elif kind == "bank":
                H = n * sk.RISE
                Lb = opt[1] if len(opt) > 1 else H / 0.42
                S.push((Lb, 0, 0), pi)
                sk.bank(S, nm + "_bank", w, H, Lb, mat=opt[0])
                S.pop()
            elif kind == "qp":
                H = n * sk.RISE
                Rq = opt[1]
                xe = sk.trans_profile(H, Rq)[-1][0]
                S.push((xe, 0, 0), pi)
                sk.extrude(S, "SK_" + nm + "_trans", opt[0], sk.trans_profile(H, Rq), w, "shell_white")
                S.pop()
                sk.coping(S, nm + "_trans", (0, -w / 2, H + 0.01), (0, w / 2, H + 0.01))
            S.pop()

    drop(0, 12, [("bank", -34, -22, "gel_yellow"), ("stairs", -18, -8, (0.0,), (-5.3, 5.3)),
                 ("qp", -6, 6, "gel_cyan", 2.6), ("stairs", 8, 18, (-2.5, 2.5)), ("bank", 22, 34, "gel_magenta")])
    drop(1, 8, [("qp", -34, -24, "gel_orange", 2.2), ("stairs", -14, -4, (0.0,)), ("bank", -2, 2, "gel_lime", 6.0),
                ("stairs", 4, 14, (), (-5.3, 5.3)), ("bank", 22, 34, "gel_violet")])
    drop(2, 5, [("bank", -34, -24, "gel_cyan"), ("stairs", -20, 20, (-10.0, 0.0, 10.0)), ("bank", 24, 34, "gel_yellow")])
    drop(3, 3, [("bank", -34, -30, "gel_lime", 3.0), ("stairs", -30, 30), ("bank", 30, 34, "gel_lime", 3.0)])

    # L3: globe fountain, ledges, planters
    S.push((14, 0, L3))
    S.lathe("SK_plaza_fountain", "marble", [(5.2, 0), (5.2, 0.45), (4.6, 0.45), (4.6, 0.12)], n=72)
    S.disc("NC_plaza_fountain_water", "water", (0, 0, 0.3), 4.6, n=48)
    for rr in (4.6, 5.2):
        S.grind([(rr * cos(a), rr * sin(a), 0.45) for a in np.linspace(0, tau, 73)])
    S.lathe("NC_plaza_fountain_jet", "glass_pipe", [(1.1, 0.3), (0.5, 1.6), (0.35, 3.0), (1.3, 3.9)], n=24)
    S.sphere("NC_plaza_globe", "globe", (0, 0, 6.2), 2.6, n=64, uv="grid")
    sc.torus(S, "NC_plaza_globe_ring", "gel_white", (0, 0, 6.2), 3.6, 0.12, m=8)
    S.pop()
    for y in (-22, 22):
        S.push((6, y - 6, L3), pi / 2)
        sk.ledge(S, "plaza_ledge", 12.0, 0.6, 0.45, glow="glow_cyan")
        S.pop()
        S.push((18, y - 3, L3), pi / 2)
        sk.manual_pad(S, "plaza_pad", 6.0, 2.4, 0.22)
        S.pop()
    for (x, y) in ((4, -31), (4, 31), (24, -31), (24, 31)):
        planter(W, (x, y, L3), 4.0)
    # L2: funbox, ledges, rails
    S.push((40, 0, L2))
    sk.pyramid(S, "plaza_funbox", 8.0, 3.0, 0.9, mat="gel_violet")
    S.pop()
    S.push((34, -22, L2), 0.35)
    sk.ledge(S, "plaza_ledge", 9.0, 0.55, 0.5, glow="glow_lime")
    S.pop()
    S.push((34, 22, L2), -0.35)
    sk.ledge(S, "plaza_ledge", 9.0, 0.55, 0.36, glow="glow_magenta")
    S.pop()
    S.push((36, 12, L2))
    sk.rail(S, "plaza_flatbar", [(0, 0, 0.38), (8, 0, 0.38)])
    S.pop()
    S.push((36, -12, L2))
    sk.rail(S, "plaza_kinkrail", [(0, 0, 0.5), (3, 0, 0.5), (6, 0, 0.3), (9, 0, 0.3)])
    S.pop()
    planter(W, (47, -30, L2), 3.5)
    planter(W, (47, 30, L2), 3.5)
    # L1: water gap, curved ledge
    S.push((59, 0, L1))
    S.box("SK_plaza_watergap", "marble", (-1.4, -7, 0), (1.4, 7, 0.32))
    S.box("NC_plaza_watergap", "water", (-1.2, -6.8, 0.2), (1.2, 6.8, 0.3))
    S.push((-4.6, 0, 0))
    sk.kicker(S, "plaza_watergap_kicker", 6.0, 0.55, 3.2, mat="gel_orange")
    S.pop()
    S.push((4.8, 0, 0), pi)
    sk.bank(S, "plaza_watergap_land", 6.0, 0.4, 2.2, mat="gel_orange")
    S.pop()
    S.pop()
    arc = [(56 + 9 * cos(a), 22 + 9 * sin(a) * 0.9, 0) for a in np.linspace(-1.2, 1.2, 24)]
    curved_ledge(S, "plaza_curve_ledge", np.array(arc) + [0, 0, L1], 0.55, 0.45)
    arc = [(56 + 9 * cos(a), -22 + 9 * sin(a) * 0.9, 0) for a in np.linspace(-1.2, 1.2, 24)]
    curved_ledge(S, "plaza_curve_ledge", np.array(arc) + [0, 0, L1], 0.55, 0.45)
    # L0 and beach plaza
    for y in (-24, -8, 8, 24):
        S.push((75, y - 3, L0), pi / 2)
        sk.ledge(S, "plaza_bench", 6.0, 0.55, 0.42)
        S.pop()
    for (x, y) in ((92, -26), (92, 26), (106, -12), (106, 12)):
        planter(W, (x, y, BW_Z - 0.004), 4.5)
    S.push((96, 0, BW_Z - 0.004))
    sk.spine(S, "plaza_beach_spine", 8.0, 0.9, 2.0, mat="gel_cyan")
    S.pop()
    for y in (-18, 18):
        S.push((90, y, BW_Z - 0.004))
        sk.manual_pad(S, "plaza_beach_pad", 10.0, 2.0, 0.25, top="gel_lime")
        S.pop()
    S.pop()
    # the Aurora rail: one long glowing rail from the top terrace to the beach plaza
    pts = [(X0 + 20, -20.0, L3 + 0.45), (X0 + 28, -20, L3 + 0.45), (X0 + 33.5, -20.0, L2 + 0.42), (X0 + 52, -20.6, L2 + 0.42),
           (X0 + 55.5, -20.6, L1 + 0.4), (X0 + 70, -21.2, L1 + 0.4), (X0 + 72.4, -21.2, L0 + 0.4), (X0 + 82, -21.6, L0 + 0.4),
           (X0 + 83.6, -21.6, BW_Z + 0.36), (X0 + 96, -22, BW_Z + 0.36)]
    lvl = lambda p: float(np.interp(p[0] - X0, [0, 28, 28.01, 52, 52.01, 70, 70.01, 82, 82.01, 120],
                                    [L3, L3, L2, L2, L1, L1, L0, L0, BW_Z, BW_Z]))
    sk.rail(S, "plaza_aurora_rail", pts, r=0.05, post=2.0, ground=lvl)


def planter(W, pos, size):
    S = W.S
    h = 0.5
    S.push(pos)
    S.box("SK_planters", "marble", (-size / 2, -size / 2, 0), (size / 2, size / 2, h), mats={"top": "lawn"})
    for a, b in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
        S.grind([(a[0] * size / 2, a[1] * size / 2, h), (b[0] * size / 2, b[1] * size / 2, h)])
    R, t = S.xf[-1]
    wp = R @ np.array([0, 0, h]) + t
    S.pop()
    rng = np.random.default_rng(int(abs(wp[0] * 13 + wp[1] * 7)) % 9999)
    saved = S.xf
    S.xf = [(np.eye(3), np.zeros(3))]
    sc.palm(S, wp, h=rng.uniform(7, 10), lean=rng.uniform(0.05, 0.25), yaw=rng.uniform(0, tau), rng=rng, trunk="SC_planter_palms")
    S.xf = saved


def curved_ledge(S, name, path, w, h):
    path = np.asarray(path, float)
    S.sweep("SK_" + name, "marble", path, [(-w / 2, 0), (-w / 2, h)])
    S.sweep("SK_" + name, "glass_frost", path, [(-w / 2, h), (w / 2, h)])
    S.sweep("SK_" + name, "marble", path, [(w / 2, h), (w / 2, 0)])
    from .mesh import frames
    Tn, Nn, Rn = frames(path)
    for sg in (-1, 1):
        S.grind(path + Rn * sg * w / 2 + Z * h)
    for i, fl in ((0, False), (-1, True)):
        c, r = path[i], Rn[i] * w / 2
        q = [c - r, c + r, c + r + Z * h, c - r + Z * h]
        S.add("SK_" + name, "marble", q, [(0, 1, 2, 3) if not fl else (3, 2, 1, 0)])


# -------------------------------------------------------------- bowls ---
def deck_with_holes(S, name, mat, R, rings, n=160):
    """Flat round deck at local z=0. rings are closed outlines (the outer
    edge of each bowl's apron); the deck is triangulated to meet them
    vertex for vertex, so there is no overlap and no seam."""
    import mapbox_earcut as earcut
    a = np.linspace(0, tau, n, endpoint=False)
    loops = [np.c_[R * np.cos(a), R * np.sin(a)]] + [np.asarray(r)[::-1, :2] for r in rings]
    V = np.vstack(loops)
    ends = np.cumsum([len(x) for x in loops]).astype(np.uint32)
    tri = earcut.triangulate_float64(V, ends).reshape(-1, 3)
    p = V[tri]
    e1, e2 = p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]
    area = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
    tri[area < 0] = tri[area < 0][:, ::-1]
    S.add(name, mat, np.c_[V, np.zeros(len(V))], tri.tolist())
    S.disc("NC_decals", "gel_white", (0, 0, 0.012), R, n=n, r0=R - 1.8)
    S.lathe(name.replace("SK_", "SC_"), "shell_white", [(R, -3.0), (R, 0.0)], n=n)


def bowls(W):
    S, T = W.S, W.T
    C = np.array([-96.0, 10.0])
    Zd = 4.4
    R = 40.0
    T.pad(sd_circle(C, R + 0.6), Zd, 7, deck=True)
    specs = [  # centre, outline, depth, transition radius, colour
        ((-13.0, 15.0), lambda t: 9.0, 2.2, 2.6, "gel_cyan"),
        ((13.0, 13.0), lambda t: 10.5 * (1 + 0.17 * cos(3 * t)), 3.0, 3.0, "gel_magenta"),
        ((-6.0, -13.0), lambda t: 8.6 * (1 + 0.20 * cos(2 * t + 0.6)), 1.7, 2.1, "gel_yellow"),
        ((-28.0, -4.0), lambda t: 5.0, 1.2, 1.5, "gel_lime"),
    ]
    holes = []
    S.push((C[0], C[1], Zd))
    for k, (c, out, depth, Rt, mat) in enumerate(specs):
        S.push((c[0], c[1], 0.0))
        ring = sk.bowl(S, "bowl_%d" % k, out, depth, Rt, mat=mat)
        S.pop()
        holes.append(ring + np.array([c[0], c[1], 0.0]))
        rmax = max(out(t) for t in np.linspace(0, tau, 60))
        T.dig(sd_circle((C[0] + c[0], C[1] + c[1]), rmax + 1.0), depth + 1.5, 4)
    deck_with_holes(S, "SK_bowls_deck", "pave_white", R, holes)
    # vert ramp with the waterfall wall behind it
    S.push((19.0, -17.0, 0), radians(-25))
    ext = sk.halfpipe(S, "vert_ramp", 15.0, 4.0, 3.4, flat=5.0, mat="gel_cyan")
    S.box("SC_vert_wall", "shell_white", (ext, -9.5, 0), (ext + 1.0, 9.5, 10.5))
    wf = np.array([[[ext - 0.06, y, z] for y in np.linspace(-8.5, 8.5, 12)] for z in np.linspace(10.3, 4.05, 10)])
    S.grid("NC_vert_waterfall", "water_fall", wf)
    S.box("NC_vert_waterfall", "glow_cyan", (ext - 0.3, -9.5, 10.5), (ext + 1.3, 9.5, 10.75))
    S.pop()
    S.push((-27.0, 16.0, 0), radians(60))
    sk.spine(S, "bowls_spine", 9.0, 1.5, 2.4, mat="gel_orange")
    S.pop()
    S.push((30.0, -2.0, 0), radians(180))
    sk.quarter(S, "bowls_qp", 10.0, 1.8, 2.6, mat="gel_violet")
    S.pop()
    S.pop()
    # links: ring -> deck, deck -> boardwalk
    a = radians(172)
    flow_path(W, "bowls_in", [polar(RING_R + 2.5, 172, float(ring_z(a))), (C[0] + R - 6, C[1] - 2, Zd + 0.004), (C[0] + R - 12, C[1] - 2, Zd + 0.004)], 6.0)
    a2 = radians(176)
    flow_path(W, "bowls_out", [(C[0] - R + 4, C[1], Zd + 0.004), (C[0] - R - 6, C[1], Zd - 0.8), polar(float(bw_r(a2)) - 3.0, 176, BW_Z + 0.004)], 6.0)


# -------------------------------------------------------------- minis ---
def minis(W):
    S, T = W.S, W.T
    C = np.array([5.0, -100.0])
    Zd = 3.5
    R = 38.0
    T.pad(sd_circle(C, R + 0.6), Zd, 7, deck=True)
    S.push((C[0], C[1], Zd))
    S.disc("SK_minis_deck", "pave_white", (0, 0, 0), R, n=120)
    S.disc("NC_decals", "gel_white", (0, 0, 0.012), R, n=120, r0=R - 1.8)
    S.disc("NC_decals", "gel_lime", (0, 0, 0.012), 20.6, n=120, r0=20.0)
    S.lathe("SC_minis_deck", "shell_white", [(R, -3.0), (R, 0.012)], n=120)
    S.push((-18, 12, 0), radians(20))
    sk.halfpipe(S, "mini_a", 7.0, 1.2, 2.2, flat=3.6, mat="gel_cyan")
    S.pop()
    S.push((17, 10, 0), radians(-15))
    sk.halfpipe(S, "mini_b", 8.0, 1.5, 2.5, flat=15.0, mat="gel_magenta")
    sk.spine(S, "mini_b_spine", 8.0, 1.5, 2.5, mat="gel_yellow")
    S.pop()
    S.push((-2, 2, 0), radians(45))
    sk.pyramid(S, "mini_pyramid", 8.5, 2.6, 1.0, mat="gel_orange")
    S.pop()
    for deg, w, h, Rq, mat in ((195, 9, 1.0, 2.0, "gel_violet"), (225, 10, 1.4, 2.4, "gel_cyan"), (315, 9, 1.8, 2.8, "gel_lime"),
                               (345, 8, 1.2, 2.2, "gel_yellow")):
        a = radians(deg)
        xe = sk.trans_profile(h, Rq)[-1][0]
        S.push(((R - 3.6 - xe) * cos(a), (R - 3.6 - xe) * sin(a), 0), a)
        sk.quarter(S, "mini_qp_%d" % deg, w, h, Rq, mat=mat)
        S.pop()
    # grass-green gel bumps (the Bliss hills, rideable)
    for (x, y, r, h) in ((-24, -5, 3.6, 0.7), (-17, -14, 2.8, 0.55), (23, -8, 3.4, 0.6)):
        S.push((x, y, 0))
        u = np.linspace(0, 1, 14)
        S.lathe("SK_mini_bumps", "gel_lime", np.c_[r * (1 - u), h * 0.5 * (1 - np.cos(pi * u))], n=40)
        S.pop()
    S.push((-10, 24, 0), radians(10))
    sk.rail(S, "mini_flatbar", [(0, 0, 0.3), (7, 0, 0.3)])
    S.pop()
    S.push((6, 22, 0), radians(-20))
    sk.ledge(S, "mini_ledge", 7.0, 0.6, 0.3, glow="glow_lime")
    S.pop()
    S.push((-31, -2, 0), radians(90))
    sk.manual_pad(S, "mini_pad", 7.0, 2.2, 0.18, top="gel_cyan")
    S.pop()
    # pump track: closed loop of rollers with banked ends
    n = 220
    u = np.linspace(0, tau, n, endpoint=False)
    px, py = 11.0 * np.cos(u), 4.6 * np.sin(u) + 1.2 * np.sin(2 * u)
    turn = np.abs(np.cos(u)) ** 3
    pz = 0.38 * (1 - np.cos(u * 9)) * (1 - turn) + 0.75 * turn + 0.05
    bankv = -0.62 * turn
    S.push((0, -21, 0), radians(5))
    pump = np.c_[px, py, pz]
    S.sweep("SK_pump_track", "gel_lime", pump, [(-1.3, 0), (1.3, 0)], closed=True, bank=bankv)
    S.sweep("SK_pump_track", "gel_white", pump, [(-1.6, 0), (-1.3, 0)], closed=True, bank=bankv)
    S.sweep("SK_pump_track", "gel_white", pump, [(1.3, 0), (1.6, 0)], closed=True, bank=bankv)
    S.sweep("SC_pump_track", "shell_white", pump, [(1.6, 0), (2.2, -1.6)], closed=True, bank=bankv)
    S.sweep("SC_pump_track", "shell_white", pump, [(-2.2, -1.6), (-1.6, 0)], closed=True, bank=bankv)
    S.pop()
    S.pop()
    a = radians(273)
    flow_path(W, "minis_in", [polar(RING_R + 2.5, 273, float(ring_z(a))), (C[0], C[1] + R - 6, Zd + 0.004), (C[0], C[1] + R - 12, Zd + 0.004)], 6.0, mat="gel_cyan")
    a2 = radians(272)
    flow_path(W, "minis_out", [(C[0], C[1] - R + 4, Zd + 0.004), (C[0] + 0.5, C[1] - R - 5, Zd - 0.6), polar(float(bw_r(a2)) - 3.0, 272, BW_Z + 0.004)], 6.0, mat="gel_cyan")


# ------------------------------------------------------------ gardens ---
def gardens(W):
    S, T = W.S, W.T
    C = np.array([76.0, 76.0])
    Zd = 3.2
    T.pad(sd_circle(C, 27.6), Zd, 8, deck=True)
    T.dig(sd_circle(C, 13.5), 1.6, 3)
    S.push((C[0], C[1], Zd))
    S.disc("SK_garden_deck", "pave_white", (0, 0, 0), 27, n=96, r0=14.0)
    S.disc("NC_decals", "gel_white", (0, 0, 0.012), 27, n=96, r0=25.6)
    S.lathe("SK_garden_pool", "marble", [(14.0, 0), (14.0, 0.4), (13.4, 0.4), (13.4, -1.8)], n=96)
    for rr in (14.0, 13.4):
        S.grind([(rr * cos(a), rr * sin(a), 0.4) for a in np.linspace(0, tau, 97)])
    S.disc("NC_garden_water", "water", (0, 0, -0.15), 13.4, n=64)
    # lily pads: a line of floating manual pads across the pool
    for k, (x, y, r) in enumerate(((-9, -3, 2.2), (-4.5, 1.5, 1.8), (0, -1.5, 2.4), (4.6, 2, 1.8), (9, -2, 2.2))):
        S.push((x, y, 0))
        S.lathe("SK_lily_pads", "gel_lime", [(0.25, -1.9), (0.3, 0.1), (r, 0.3), (r, 0.42)], n=36)
        S.disc("SK_lily_pads", "gel_lime", (0, 0, 0.42), r, n=36)
        S.disc("NC_decals", "gel_white", (0, 0, 0.432), r, n=36, r0=r - 0.25)
        S.pop()
    # crescent wall with a waterfall
    a0, a1 = radians(20), radians(110)
    S.lathe("SC_garden_wall", "shell_white", [(17.2, 0), (17.4, 9.0), (17.0, 9.6), (15.8, 9.0), (15.0, 6), (15.2, 0)], n=40, a0=a0, a1=a1)
    aa = np.linspace(a0 + 0.12, a1 - 0.12, 30)
    wf = np.array([[[rr * cos(a), rr * sin(a), z] for a in aa] for rr, z in ((15.7, 8.9), (14.9, 7.5), (14.3, 4.5), (13.9, 1.5), (13.7, -0.15))])
    S.grid("NC_garden_waterfall", "water_fall", wf)
    S.pop()
    for (x, y, r, nm) in ((104, 62, 9.0, "dome_a"), (60, 108, 7.5, "dome_b"), (112, 86, 6.0, "dome_c")):
        W.late.append(lambda x=x, y=y, r=r, nm=nm: sc.dome(S, (x, y, T.h1(x, y) + 0.2), r, name=nm))
    for (x, y, h, r, acc) in ((96, 100, 26, 5.0, "gel_cyan"), (84, 114, 18, 4.0, "gel_lime"), (118, 70, 14, 3.6, "gel_magenta")):
        W.late.append(lambda x=x, y=y, h=h, r=r, acc=acc: sc.pod_tower(S, (x, y, T.h1(x, y) - 0.5), h, r, name="pod_tower", accent=acc))
        T.pad(sd_circle((x, y), r + 1), lambda xx, yy: T.base(xx, yy) + 0.15, 3)
    for (x, y, r) in ((104, 62, 10.5), (60, 108, 9), (112, 86, 7.5)):
        T.pad(sd_circle((x, y), r), lambda xx, yy, x=x, y=y: T.base(np.array([x]), np.array([y]))[0] + 0.35, 4)
    a = radians(45)
    flow_path(W, "garden_in", [polar(RING_R + 2.5, 45, float(ring_z(a))), polar(70, 45, 4.2), (C[0] - 19.5, C[1] - 19.5, Zd + 0.004)], 6.0, mat="gel_cyan")
    a2 = radians(44)
    flow_path(W, "garden_out", [(C[0] + 18, C[1] + 18.5, Zd + 0.004), polar(138, 45, 2.6), polar(float(bw_r(a2)) - 3.0, 44, BW_Z + 0.004)], 6.0, mat="gel_cyan")


# -------------------------------------------------------------- islet ---
def islet(W):
    S, T = W.S, W.T
    ic = np.array(T.ISLET)
    a = atan2(ic[1], ic[0])
    start = np.array([(bw_r(a) + 4.6) * cos(a), (bw_r(a) + 4.6) * sin(a), BW_Z])
    d = unit(np.r_[ic - start[:2], 0])
    Lb = float(np.linalg.norm(ic - start[:2])) - 13
    u = np.linspace(0, 1, 60)
    path = start + np.outer(u * Lb, d)
    path[:, 2] = BW_Z + (3.4 - BW_Z) * u - 1.5 * np.sin(pi * u)
    S.sweep("SK_rope_bridge", "wood", path, [(-1.4, 0), (1.4, 0)])
    S.sweep("SC_rope_bridge", "wood", path, [(1.4, 0), (1.4, -0.12), (-1.4, -0.12), (-1.4, 0)])
    from .mesh import frames
    Tn, Nn, Rn = frames(path)
    for sg in (-1, 1):
        rope = path + Rn * sg * 1.45 + Z * (1.0 + 0.25 * np.cos(u * tau * 6))[:, None]
        S.tube("NC_rope_bridge", "rope", rope, 0.035, n=6)
        for i in range(0, 60, 5):
            S.tube("NC_rope_bridge", "rope", [path[i] + Rn[i] * sg * 1.42, rope[i]], 0.02, n=5, caps=False)
        for i in (0, -1):
            b = path[i] + Rn[i] * sg * 1.5
            S.tube("SC_rope_bridge", "wood", [b - Z * 3, b + Z * 1.5], 0.16, n=8)
    W.wall_gaps.append((float(np.degrees(a)) % 360, 1.4))
    W.keepout.append(sd_path(path[::3], 5))
    T.pad(sd_circle(ic, 9), 3.4, 6)
    S.push((ic[0], ic[1], 3.4))
    S.disc("SK_islet_deck", "gel_cyan", (0, 0, 0), 9, n=64)
    S.disc("NC_decals", "gel_white", (0, 0, 0.012), 9, n=64, r0=8.2)
    u2 = np.linspace(0, 1, 16)
    S.lathe("SK_islet_volcano", "gel_magenta", np.c_[4.2 * (1 - u2) + 0.9 * u2, 1.5 * 0.5 * (1 - np.cos(pi * u2))], n=48)
    S.disc("SK_islet_volcano", "gel_white", (0, 0, 1.5), 0.9, n=24)
    S.sphere("NC_islet_orb", "orb", (0, 0, 4.2), 1.1, n=32)
    S.pop()


# -------------------------------------------------------------- water ---
def water(W):
    S = W.S
    f = 2600.0
    S.add("NC_water", "water", [[-f, -f, SEA_Z], [f, -f, SEA_Z], [f, f, SEA_Z], [-f, f, SEA_Z]], [(0, 1, 2, 3)],
          uv=[[0, 0], [1, 0], [1, 1], [0, 1]])


# ------------------------------------------------------------ scatter ---
def scatter(W):
    S, T = W.S, W.T
    rng = np.random.default_rng(42)

    def free(x, y, margin):
        if not T.clear_of_pads(np.array([x]), np.array([y]), margin)[0]:
            return False
        return all(k(np.array([x]), np.array([y]))[0] > 0 for k in W.keepout)

    # palms: dense along the beach, scattered on the lawns
    placed = []
    tries = 0
    while len(placed) < 210 and tries < 9000:
        tries += 1
        a = rng.uniform(0, tau)
        coast = float(T.coast(a))
        if rng.random() < 0.55:
            r = coast - rng.uniform(4, 15)
        else:
            r = rng.uniform(24, coast - 30)
        x, y = r * cos(a), r * sin(a)
        if not free(x, y, 2.5) or any(hypot(x - px, y - py) < 4.5 for px, py in placed):
            continue
        h = T.h1(x, y)
        if h < 0.9:
            continue
        placed.append((x, y))
        beach = r > coast - 16
        sc.palm(S, (x, y, h - 0.25), h=rng.uniform(7.5, 13.0), lean=rng.uniform(0.1, 0.45) if beach else rng.uniform(0.0, 0.2),
                yaw=(a if beach else rng.uniform(0, tau)) + rng.uniform(-0.6, 0.6), rng=rng, group="ab"[len(placed) % 2])
    ic = np.array(T.ISLET)
    for k in range(7):
        a = k * tau / 7 + 0.3
        x, y = ic[0] + 12.5 * cos(a), ic[1] + 12.5 * sin(a)
        if abs((a - atan2(-ic[1], -ic[0]) + pi) % tau - pi) < 0.6:
            continue                      # keep the bridge landing clear
        sc.palm(S, (x, y, T.h1(x, y) - 0.25), h=rng.uniform(8, 12), lean=rng.uniform(0.2, 0.5), yaw=a, rng=rng)
    # rocks at the waterline, bushes inland
    for k in range(70):
        a = rng.uniform(0, tau)
        r = float(T.coast(a)) + rng.uniform(-3, 6)
        x, y = r * cos(a), r * sin(a)
        if not free(x, y, 1.5):
            continue
        sc.rock(S, (x, y, T.h1(x, y) + 0.1), rng.uniform(0.5, 2.0), rng)
    n = 0
    while n < 150:
        a = rng.uniform(0, tau)
        r = rng.uniform(22, float(T.coast(a)) - 28)
        x, y = r * cos(a), r * sin(a)
        if free(x, y, 1.5):
            sc.bush(S, (x, y, T.h1(x, y)), rng.uniform(0.6, 1.5), rng)
            n += 1
    # bubbles drifting over everything
    for k in range(90):
        a, r = rng.uniform(0, tau), rng.uniform(10, 230) * rng.random() ** 0.5
        z = rng.uniform(5, 70)
        S.sphere("NC_bubbles", "bubble", (r * cos(a), r * sin(a), max(z, T.h1(r * cos(a), r * sin(a)) + 4)),
                 rng.choice([0.5, 0.8, 1.2, 1.8, 2.6, 4.0], p=[0.25, 0.25, 0.2, 0.15, 0.1, 0.05]), n=24)
    # wind farm, boats, dolphins in the lagoon
    for k, (deg, r) in enumerate(((120, 300), (150, 310), (170, 300), (210, 310), (296, 310), (318, 300), (336, 290))):
        p = polar(r, deg, 0)
        sc.turbine(S, (p[0], p[1], 0), h=rng.uniform(38, 46), yaw=radians(200), phase=rng.uniform(0, 2))
    for (deg, r, yaw) in ((150, 250, 0.6), (285, 262, 2.4), (350, 250, 4.0), (200, 300, 1.2), (75, 300, 5.2)):
        p = polar(r, deg, 0)
        sc.sailboat(S, (p[0], p[1], -0.25), yaw, L=rng.uniform(8, 12))
    for (deg, r, yaw) in ((104, 232, 1.2), (107, 238, 1.3), (112, 228, 1.0), (300, 232, 3.0), (303, 238, 3.2)):
        p = polar(r, deg, 0)
        sc.dolphin(S, (p[0], p[1], 0.2), yaw)
    # aurora ribbons high above the island
    for k, (z, amp, mat, ph) in enumerate(((78, 60, "aurora_cyan", 0.0), (92, 85, "aurora_lime", 1.9), (106, 70, "aurora_magenta", 3.7))):
        u = np.linspace(-1, 1, 160)
        path = np.c_[u * 330, amp * np.sin(u * 2.6 + ph) + 30 * np.sin(u * 6.1 + ph), z + 9 * np.cos(u * 3.3 + ph)]
        S.push((0, 0, 0), radians(25 + 50 * k))
        S.sweep("OP_aurora", mat, path, [(0, -3 - k), (0, 0), (0, 3 + k)])
        S.pop()


def build():
    W = World()
    v2.spire(W)
    ring_and_spurs(W)
    plaza(W)
    bowls(W)
    minis(W)
    gardens(W)
    bliss_drop(W)
    aurora_loop(W)
    pts = splash(W)
    splash_pad_and_return(W, pts)
    aqueduct(W)
    v2.drain(W)
    v2.island2(W)
    v2.highway(W)
    islet(W)
    v2.scatter_spots(W)
    v2.more_bowl_spots(W)
    v2.pool_life(W)
    boardwalk(W)
    for f in W.late:
        f()
    scatter(W)
    water(W)
    W.T.build(W.S)
    return W
