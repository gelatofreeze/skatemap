"""Second-pass content: the hollow Spire and its drop, the mega highway,
the second island with its retro-desktop obstacles, street-spot scatter,
and the heavier Frutiger Aero dressing."""
import numpy as np
from math import sin, cos, pi, tau, radians, atan2, hypot
from .mesh import Z, smooth_path, resample, smoothstep, unit, frames
from .terrain import Terrain, sd_circle, sd_path
from .mega import Prof, ribbon, pylons, G
from . import skate as sk, scenery as sc

HILL_Z = 12.3
MID_Z = 45.0          # mid deck: Bliss Drop, Aurora Loop, Splash, Aqueduct
MID_R = 16.9          # where those lines leave the mid deck
CROWN_Z = 85.0        # crown deck: the Drain and the highway
BW_Z = 2.0
I2 = np.array(Terrain.ISLAND2)
I2_Z = 2.6
GELS = ["gel_aqua", "gel_lime", "gel_yellow", "gel_orange", "gel_magenta", "gel_violet", "gel_cyan"]


def polar(r, deg, z=0.0):
    a = radians(deg)
    return np.array([r * cos(a), r * sin(a), z])


def shell_r(z):
    """Outer radius of the Spire's glass shell at height z."""
    u = np.clip((np.asarray(z, float) - HILL_Z) / (CROWN_Z - HILL_Z), 0, 1)
    return 9.0 + 18.0 * (1 - u) ** 3 + 4.0 * smoothstep(0.86, 1.0, u)


def deck_ring(S, name, mat, z, r_out, cut=None, r_in=0.0, n=120):
    """Round deck, optionally with a rectangular opening (x0, x1, half-width)
    rotated by cut[3] radians, or as an annulus."""
    import mapbox_earcut as earcut
    a = np.linspace(0, tau, n, endpoint=False)
    loops = [np.c_[r_out * np.cos(a), r_out * np.sin(a)]]
    if r_in:
        loops.append(np.c_[r_in * np.cos(a), r_in * np.sin(a)][::-1])
    if cut:
        x0, x1, hw, yaw = cut
        q = np.array([[x0, -hw], [x1, -hw], [x1, hw], [x0, hw]])
        c, s = cos(yaw), sin(yaw)
        loops.append((q @ np.array([[c, s], [-s, c]]))[::-1])
    V = np.vstack(loops)
    tri = earcut.triangulate_float64(V, np.cumsum([len(l) for l in loops]).astype(np.uint32)).reshape(-1, 3)
    p = V[tri]
    e1, e2 = p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]
    bad = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0] < 0
    tri[bad] = tri[bad][:, ::-1]
    S.add(name, mat, np.c_[V, np.full(len(V), z)], tri.tolist())


# ------------------------------------------------------------- spire ---
def spire(W):
    S, T = W.S, W.T
    T.pad(sd_circle((0, 0), 32), HILL_Z, 14, deck=True)
    S.disc("SK_hub_plaza", "pave_blue", (0, 0, HILL_Z), 31.5, n=120)
    S.disc("NC_decals", "gel_white", (0, 0, HILL_Z + 0.012), 31.5, n=120, r0=30.6)
    S.lathe("SC_hub_plaza", "shell_white", [(31.5, HILL_Z - 3), (31.5, HILL_Z)], n=120)
    # glass shell: starts 7 m up on a ring of legs, so the base is an open colonnade
    z0 = HILL_Z + 7.0
    zz = np.linspace(z0, CROWN_Z - 0.45, 60)
    S.lathe("SC_spire_shell", "glass_blue", np.c_[shell_r(zz), zz], n=72)
    S.lathe("SC_spire_shell", "shell_white", [(shell_r(z0) + 0.25, z0 - 0.5), (shell_r(z0) + 0.35, z0 + 0.3), (shell_r(z0), z0 + 0.5)], n=72)
    for k in range(8):
        a = radians(244 + 22.5 + k * 45)
        u = np.linspace(0, 1, 16)
        rr = 28.5 + (shell_r(z0) + 0.3 - 28.5) * u ** 0.6
        S.tube("SC_spire_legs", "shell_white", np.c_[rr * cos(a), rr * sin(a), HILL_Z + 7.0 * u ** 1.6 - 0.2 * (1 - u)], 0.7 - 0.3 * u, n=10)
    for k in range(4):
        u = np.linspace(0, 1, 140)
        a = k * tau / 4 + u * tau * 1.5
        zh = z0 + u * (CROWN_Z - 1 - z0)
        rr = shell_r(zh) + 0.2
        S.tube("SC_spire_ribs", "shell_white", np.c_[rr * np.cos(a), rr * np.sin(a), zh], 0.22, n=8, caps=False)
    for zr in (30, 58, 71):
        sc.torus(S, "SC_spire_ribs", "shell_white", (0, 0, zr), float(shell_r(zr)) + 0.2, 0.2, m=8, n=72)
    # mid deck: an annulus round the shell
    ri = float(shell_r(MID_Z)) + 0.1
    deck_ring(S, "SK_spire_mid_deck", "gel_white", MID_Z, MID_R + 0.6, r_in=ri)
    S.lathe("SC_spire_mid_deck", "shell_white", [(ri, MID_Z - 1.4), (MID_R + 0.6, MID_Z - 0.4), (MID_R + 0.75, MID_Z - 0.2), (MID_R + 0.6, MID_Z)], n=120)
    for a0, a1 in ((161, 199), (251, 289), (341, 424)):
        S.lathe("SC_spire_rail", "glass_frost", [(MID_R + 0.45, MID_Z), (MID_R + 0.45, MID_Z + 1.1)], n=28, a0=radians(a0), a1=radians(a1))
        arc = [((MID_R + 0.45) * cos(t), (MID_R + 0.45) * sin(t), MID_Z + 1.12) for t in np.linspace(radians(a0), radians(a1), 28)]
        S.tube("GR_spire_rail", "chrome", arc, 0.05, n=8)
        S.grind(arc)
    # crown deck with the opening the Drain drops through
    yaw = radians(244)
    deck_ring(S, "SK_spire_crown", "gel_white", CROWN_Z, 13.0, cut=(-6.5, 6.0, 3.9, yaw))
    S.lathe("SC_spire_crown", "shell_white", [(13.0, CROWN_Z - 0.45), (13.2, CROWN_Z - 0.22), (13.0, CROWN_Z)], n=120)
    for a0, a1 in ((40, 222), (266, 364)):
        S.lathe("SC_spire_rail", "glass_frost", [(12.85, CROWN_Z), (12.85, CROWN_Z + 1.1)], n=40, a0=radians(a0), a1=radians(a1))
        arc = [(12.85 * cos(t), 12.85 * sin(t), CROWN_Z + 1.12) for t in np.linspace(radians(a0), radians(a1), 40)]
        S.tube("GR_spire_rail", "chrome", arc, 0.05, n=8)
        S.grind(arc)
    # glass guard round three sides of the opening
    S.push((0, 0, CROWN_Z), yaw)
    for (xa, ya, xb, yb) in ((-6.5, 3.95, 6.05, 3.95), (6.05, 3.95, 6.05, -3.95), (6.05, -3.95, -6.5, -3.95)):
        S.add("SC_spire_rail", "glass_frost", [[xa, ya, 0], [xb, yb, 0], [xb, yb, 1.1], [xa, ya, 1.1]], [(0, 1, 2, 3)])
    S.pop()
    # halo and orb
    hz = CROWN_Z + 13
    sc.torus(S, "NC_spire_halo", "gel_white", (0, 0, hz), 10.0, 0.42)
    sc.torus(S, "NC_spire_halo", "glow_cyan", (0, 0, hz), 10.0, 0.13, m=8)
    S.sphere("NC_spire_orb", "orb", (0, 0, hz), 3.8, n=48)
    for deg in (70, 190, 310):
        u = np.linspace(0, 1, 20)
        a = radians(deg)
        rr = 12.7 - 2.7 * u ** 1.6
        S.tube("NC_spire_halo", "shell_white", np.c_[rr * cos(a), rr * sin(a), CROWN_Z + 13 * u ** 0.7], 0.17 - 0.08 * u, n=8)
    d = np.array([cos(yaw), sin(yaw), 0])
    S.empty("spawn", tuple(-d * 9.5 + Z * (CROWN_Z + 0.15)), yaw=yaw)
    S.empty("spawn_mid", (MID_R - 2.0, 0, MID_Z + 0.15), yaw=radians(90))


# ------------------------------------------------------------- drain ---
def drain(W):
    """Near-vertical drop down the inside of the Spire, out through the
    colonnade, a viaduct to the shore, a launch over the lagoon, a catch
    ramp, and a banked U-turn back to the boardwalk."""
    S, T = W.S, W.T
    deg = 244
    Rb = 24.0
    zb = HILL_Z + 0.004
    p = Prof(-6.5, CROWN_Z).line(1.0).to_heading(4, -85)
    p.line_to_z(zb + Rb * (1 - cos(radians(85)))).to_heading(Rb, 0)
    i_out = len(p.p)
    p.line(6).to_heading(140, -5).line_to_z(8.0).to_heading(200, -1)
    p.line(176 - p.x, step=1.5)
    p.to_heading(45, 22)
    p.gap(-28)
    fl = p.flight
    p.down_to(4.0, 30).line(10, step=1.0)
    pts = p.points((0, 0, 0), radians(deg))
    ribbon(S, "drain", pts, 7.0, "gel_magenta", breaks=p.breaks)
    ok = lambda x, y: hypot(x, y) > 33 and bool(T.clear_of_pads(np.array([x]), np.array([y]), 0.8)[0])
    W.late.append(lambda: pylons(S, T, "drain", pts[i_out:], ok=ok))
    W.keepout.append(sd_path(pts[i_out::3], 7))
    W.notes["drain"] = dict(gap=p.last_gap, lip_speed=float(np.sqrt(fl[2] ** 2 + fl[3] ** 2)))
    # white frame hoops down the shaft, so the drop reads from outside
    d = np.array([cos(radians(deg)), sin(radians(deg)), 0])
    left = np.array([-d[1], d[0], 0])
    # U-turn back to the island
    end = pts[-1]
    Ru = 55.0
    c = end + left * Ru
    a0 = radians(deg) - pi / 2
    arc = [c + Ru * np.array([cos(a0 + t), sin(a0 + t), 0]) for t in np.linspace(0, radians(195), 60)]
    a_bw = radians(268)
    r_bw = float(Terrain.coast(a_bw)) - 22.0
    home = np.array([(r_bw + 4.6) * cos(a_bw), (r_bw + 4.6) * sin(a_bw), 0])
    ret = resample(np.vstack([arc, [home + (arc[-1] - home) * 0.5], [home + unit(arc[-1] - home) * 14], [home]]), 1.0)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(ret[:, :2], axis=0), axis=1))]
    ret[:, 2] = 4.0 + (BW_Z + 0.004 - 4.0) * smoothstep(0, s[-1] - 12, s)
    L_arc = Ru * radians(195)
    bank = -0.62 * smoothstep(0, 18, s) * (1 - smoothstep(L_arc - 10, L_arc + 14, s))
    ribbon(S, "drain_return", ret, 7.0, "gel_magenta", bank=bank)
    W.late.append(lambda: pylons(S, T, "drain_return", ret[:-10], every=12, ok=lambda x, y: hypot(x, y) > 190))
    W.wall_gaps.append((268, 2.2))
    W.keepout.append(sd_path(ret[::4], 7))
    return pts


# ----------------------------------------------------------- highway ---
def highway(W):
    """950 m of descending ramp from the crown: out over the lagoon,
    round the second island on a banked turn, and back to the plaza beach.
    Roller sections to pump, table-top jumps that are safe to come up short on."""
    S, T = W.S, W.T
    a = radians(22)
    ctrl = [(13 * cos(a), 13 * sin(a)), (40 * cos(a), 40 * sin(a)), (100, 40), (190, 77), (300, 122), (395, 152),
            (480, 150), (540, 95), (548, 30), (512, -22), (440, -44), (330, -50), (240, -44), (196, -33), (170, -26)]
    path = smooth_path([(x, y, 0) for x, y in ctrl], 1.0, it=5)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path[:, :2], axis=0), axis=1))]
    L = s[-1]
    z = np.where(s < 70, CROWN_Z - 25 * smoothstep(0, 70, s) ** 1.0, 60 - (60 - (BW_Z + 0.02)) * np.clip((s - 70) / (L - 100), 0, 1))
    # blend the kink at s = 70 and flatten the last 30 m
    z = z - 0.0
    rollers = [(95, 175), (330, 400), (560, 640), (790, 850)]
    tables = [200, 232, 420, 452, 484, 670, 702]
    for s0, s1 in rollers:
        win = smoothstep(s0, s0 + 8, s) * (1 - smoothstep(s1 - 8, s1, s))
        z = z + 0.75 * np.sin(pi * (s - s0) / 7.0) ** 2 * win
    for t0 in tables:
        z = z + 1.9 * (smoothstep(t0, t0 + 8, s) - smoothstep(t0 + 15, t0 + 25, s))
    path[:, 2] = z
    # bank from plan curvature at a nominal 20 m/s
    Tn = unit(np.gradient(path[:, :2], axis=0))
    head = np.unwrap(np.arctan2(Tn[:, 1], Tn[:, 0]))
    k = np.gradient(head) / np.maximum(np.gradient(s), 1e-6)
    k = np.convolve(k, np.ones(15) / 15, mode="same")
    bank = -np.clip(np.arctan(20.0 ** 2 * k / G), -0.7, 0.7)
    n = len(path)
    seg = 70
    for i, i0 in enumerate(range(0, n - 1, seg)):
        i1 = min(n, i0 + seg + 1)
        ribbon(S, "highway", path[i0:i1], 9.0, GELS[i % len(GELS)], bank=bank[i0:i1])

    def ok(x, y):
        if not T.clear_of_pads(np.array([x]), np.array([y]), 1.0)[0]:
            return False
        return all(hypot(x - cx, y - cy) > r + 1.5 for cx, cy, r in W.i2_keep) and hypot(x, y) > 33
    W.late.append(lambda: pylons(S, T, "highway", path[:-30], every=14, r=0.6, ok=ok))
    W.keepout.append(sd_path(path[::4], 8))
    W.notes["highway"] = dict(length=float(L))
    return path


# ------------------------------------------------- retro-desktop pieces ---
def panel(S, name, mat, O, U, V):
    """Textured rectangle: image runs left to right along U, bottom to top along V."""
    O, U, V = (np.asarray(v, float) for v in (O, U, V))
    S.grid(name, mat, np.array([[O, O + V], [O + U, O + U + V]]), uv="grid")


def window_wall(S, name, tex, w=10.0, h=7.0, ang=62.0, R=2.6, n=28):
    """A giant program window leaning back as a wallride: a transition at
    the foot, then a flat bank. Ride at it along +x."""
    a = radians(ang)
    arc = [(R * sin(t), R * (1 - cos(t))) for t in np.linspace(0, a, 10)]
    Ls = max(0.5, (h - arc[-1][1]) / sin(a))
    prof = np.array(arc + [(arc[-1][0] + cos(a) * Ls * k / 6, arc[-1][1] + sin(a) * Ls * k / 6) for k in range(1, 7)])
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(prof, axis=0), axis=1))]
    u = np.linspace(0, d[-1], n)
    prof = np.c_[np.interp(u, d, prof[:, 0]), np.interp(u, d, prof[:, 1])]
    ys = np.linspace(w / 2, -w / 2, 12)
    P = np.array([[[x, y, z] for x, z in prof] for y in ys])
    S.grid("SK_" + name, tex, P, uv="grid")
    xe, ze = prof[-1]
    for y, fl in ((-w / 2, False), (w / 2, True)):
        cap = np.array([[[x, y, 0], [x, y, z]] for x, z in prof])
        S.grid("SC_" + name, "win_grey", cap, flip=fl)
    S.add("SC_" + name, "win_grey", [[xe, -w / 2, 0], [xe, w / 2, 0], [xe, w / 2, ze], [xe, -w / 2, ze]], [(0, 1, 2, 3)])
    sk.coping(S, name, (xe, -w / 2, ze), (xe, w / 2, ze), r=0.06)


def flat_window(S, name, tex, L, w, h, grind=True):
    """A window lying flat: a manual pad or ledge with the interface on top."""
    S.box("SK_" + name, "win_grey", (0, -w / 2, 0), (L, w / 2, h - 0.001))
    panel(S, "SK_" + name, tex, (0, -w / 2, h), (L, 0, 0), (0, w, 0))
    if grind:
        for y in (-w / 2, w / 2):
            S.grind([(0, y, h), (L, y, h)])


def cascade(S, name, n=7):
    """The cascading error dialogs, as a run of stacked ledges."""
    for k in range(n):
        S.push((k * 1.5, k * 0.9, 0))
        flat_window(S, name, "ui_error", 5.6, 2.8, 0.36 * (k + 1))
        S.pop()


def cursor_kicker(S, name, scale=0.5, rise=1.35):
    """A giant mouse pointer lying on the ground, tilted up toward its tip."""
    import mapbox_earcut as earcut
    poly = np.array([(0, 0), (0, -16), (3.6, -12.6), (6.2, -18.2), (8.4, -17.2), (5.9, -11.6), (11, -11.6)], float) * scale
    # ride from the tail (+x start) up to the tip: put the tip at +x
    ax = unit(np.array([-4.5, 14.0]))
    X = poly @ ax
    Yc = poly @ np.array([ax[1], -ax[0]])
    X = X - X.min()
    zt = rise * X / X.max()
    tri = earcut.triangulate_float64(np.c_[X, Yc], np.array([len(poly)], np.uint32)).reshape(-1, 3)
    p = np.c_[X, Yc][tri]
    e1, e2 = p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]
    bad = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0] < 0
    tri[bad] = tri[bad][:, ::-1]
    S.add("SK_" + name, "gel_white", np.c_[X, Yc, zt + 0.02], tri.tolist())
    m = len(poly)
    area = sum(X[i] * Yc[(i + 1) % m] - X[(i + 1) % m] * Yc[i] for i in range(m))
    for i in range(m):
        j = (i + 1) % m
        q = [[X[i], Yc[i], 0], [X[j], Yc[j], 0], [X[j], Yc[j], zt[j] + 0.02], [X[i], Yc[i], zt[i] + 0.02]]
        S.add("SK_" + name, "ink", q, [(0, 1, 2, 3) if area > 0 else (3, 2, 1, 0)])


def cd_pad(S, name, r=3.0, h=0.26):
    """A compact disc as a round manual pad."""
    a = np.linspace(0, tau, 73)
    rr = np.array([0.16 * r, r])
    P = np.stack([np.outer(np.cos(a), rr), np.outer(np.sin(a), rr), np.full((73, 2), h)], -1)
    uv = np.stack([0.5 + 0.5 * P[..., 0] / r, 0.5 + 0.5 * P[..., 1] / r], -1).reshape(-1, 2)
    S.grid("SK_" + name, "ui_cd", P, flip=True, uv=uv)
    S.disc("SK_" + name, "gel_white", (0, 0, h), 0.16 * r, n=36)
    S.lathe("SK_" + name, "chrome", [(r, 0), (r, h)], n=72)
    S.grind([(r * cos(t), r * sin(t), h) for t in a])


def player_wall(S, name, w=13.0):
    """Quarter pipe with the media player as its back wall."""
    xe = sk.quarter(S, name, w, 2.6, 3.0, mat="gel_cyan", deck=1.4)
    S.box("SC_" + name, "shell_white", (xe, -w / 2, 0), (xe + 0.8, w / 2, 10.4))
    panel(S, "NC_" + name + "_screen", "ui_player", (xe - 0.03, w / 2, 2.7), (0, -w, 0), (0, 0, w * 0.6))


def duck(S, pos, yaw=0.0, k=1.0):
    S.push(pos, yaw)
    S.sphere("NC_ducks", "duck", (0, 0, 0.32 * k), 0.55 * k, n=18, squash=0.68)
    S.sphere("NC_ducks", "duck", (0.36 * k, 0, 0.78 * k), 0.30 * k, n=16)
    S.sphere("NC_ducks", "duck_beak", (0.66 * k, 0, 0.74 * k), 0.13 * k, n=10, squash=0.5)
    S.sphere("NC_ducks", "ink", (0.52 * k, 0.2 * k, 0.86 * k), 0.035 * k, n=6)
    S.sphere("NC_ducks", "ink", (0.52 * k, -0.2 * k, 0.86 * k), 0.035 * k, n=6)
    S.add("NC_ducks", "duck", [[-0.45 * k, 0, 0.45 * k], [-0.78 * k, 0, 0.78 * k], [-0.4 * k, 0, 0.62 * k]], [(0, 1, 2), (0, 2, 1)])
    S.pop()


def orb_lamp(S, pos, lean_yaw=0.0, h=4.6, glow="glow_cyan"):
    S.push(pos, lean_yaw)
    u = np.linspace(0, 1, 12)
    S.tube("SC_orb_lamps", "shell_white", np.c_[0.9 * u ** 2.2, 0 * u, h * u], 0.09 - 0.03 * u, n=8)
    S.sphere("NC_orb_lamps", glow, (0.9, 0, h + 0.3), 0.34, n=14)
    S.sphere("NC_orb_lamps", "bubble", (0.9, 0, h + 0.3), 0.46, n=14)
    S.pop()


def real_fish(S, pos, L, yaw, kind="clown", pitch=0.0):
    """Textured fish: deep clownfish body or a fantail goldfish."""
    n, m = 22, 16
    s = np.linspace(0, 1, n)                       # tail root -> nose
    if kind == "clown":
        depth = 0.21 * L * np.sin(pi * np.clip(s * 0.96 + 0.04, 0, 1) ** 0.85) ** 0.7 + 0.02 * L
        width = depth * 0.42
        mat = "fish_clown"
    else:
        depth = 0.19 * L * np.sin(pi * np.clip(s * 0.95 + 0.05, 0, 1) ** 0.7) ** 0.8 + 0.02 * L
        width = depth * 0.62
        mat = "fish_gold"
    a = np.linspace(-pi / 2, 1.5 * pi, m)            # starts and ends at the belly
    P = np.stack([np.outer((s - 0.5) * L, np.ones(m)), np.outer(width, np.cos(a)), np.outer(depth, np.sin(a))], -1)
    S.push(pos, yaw)
    S.grid("NC_fish", mat, P, uv="grid")
    S.add("NC_fish", mat, np.vstack([P[-1], [[0.5 * L + 0.02 * L, 0, 0]]]), [(i, i + 1, m) for i in range(m - 1)],
          uv=np.vstack([np.c_[np.full(m, 0.99), np.linspace(0, 1, m)], [[1.0, 0.5]]]))
    x0 = -0.5 * L
    fin = "fin_orange"
    if kind == "clown":
        tail = [[x0 + 0.02 * L, 0, 0]] + [[x0 - 0.2 * L * cos(t), 0, 0.2 * L * sin(t)] for t in np.linspace(-1.25, 1.25, 9)]
        S.add("NC_fish", fin, tail, [(0, i, i + 1) for i in range(1, 9)])
    else:
        for sg in (-1, 1):
            tail = [[x0 + 0.004 * L, 0, 0]] + [[x0 - 0.42 * L * cos(t) ** 0.6, 0.05 * L * sg * sin(3 * t), sg * 0.34 * L * sin(t)] for t in np.linspace(0.05, 1.3, 9)]
            S.add("NC_fish", fin, tail, [(0, i, i + 1) for i in range(1, 9)])
    back = [(float(sv), float(dv)) for sv, dv in zip(s[5:17], depth[5:17])]
    dors = np.array([[[(sv - 0.5) * L, 0, dv * 0.96], [(sv - 0.5) * L - 0.03 * L, 0, dv + 0.09 * L * sin(pi * k / 11) + 0.01 * L]] for k, (sv, dv) in enumerate(back)])
    S.grid("NC_fish", fin, dors)
    for sg in (-1, 1):
        S.add("NC_fish", fin, [[0.16 * L, sg * width[15] * 0.9, -0.03 * L], [0.02 * L, sg * (width[15] + 0.12 * L), -0.09 * L],
                               [0.0, sg * (width[15] + 0.07 * L), 0.03 * L]], [(0, 1, 2)])
    S.add("NC_fish", fin, [[-0.1 * L, 0, -depth[8] * 0.95], [-0.24 * L, 0, -depth[8] - 0.09 * L], [-0.28 * L, 0, -depth[6] * 0.9]], [(0, 1, 2)])
    S.pop()


def anemone(S, pos, r, rng, mat="anemone"):
    sc.rock(S, np.asarray(pos) + [0, 0, r * 0.2], r * 0.7, rng, name="NC_tank_rocks")
    for k in range(int(rng.integers(14, 22))):
        a, rr = rng.uniform(0, tau), rng.uniform(0, r * 0.6)
        u = np.linspace(0, 1, 7)
        hgt = r * rng.uniform(0.9, 1.6)
        sway = rng.uniform(-0.35, 0.35, 2) * r
        path = np.c_[pos[0] + rr * cos(a) + sway[0] * u ** 2, pos[1] + rr * sin(a) + sway[1] * u ** 2, pos[2] + r * 0.5 + hgt * u]
        S.tube("NC_anemones", mat, path, 0.055 * r * (1 - 0.55 * u) + 0.01, n=6)


def coral(S, pos, r, rng):
    def branch(p, d, L, depth):
        q = p + d * L
        S.tube("NC_coral", "coral", [p, q], [0.07 * r * (0.7 ** (3 - depth)) + 0.02, 0.05 * r * (0.7 ** (3 - depth)) + 0.015], n=6)
        if depth:
            for _ in range(2):
                branch(q, unit(d + rng.normal(0, 0.55, 3) * np.array([1, 1, 0.5])), L * 0.72, depth - 1)
    branch(np.asarray(pos, float), np.array([0, 0, 1.0]), r * 0.55, 3)


def rainbow(S, a, b, name="NC_rainbow", w=1.5):
    """Five-band arch from a to b (points on the water)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    mid, half = (a + b) / 2, np.linalg.norm(b - a) / 2
    d = unit(b - a)
    for k, mat in enumerate(("rainbow_r", "rainbow_y", "rainbow_g", "rainbow_b", "rainbow_v")):
        R = half - k * w
        t = np.linspace(0, pi, 72)
        path = mid + np.outer(-np.cos(t) * R, d) + np.outer(np.sin(t) * R * 0.62, Z)
        S.sweep(name, mat, path, [(-w / 2, 0), (w / 2, 0)], up=np.cross(d, Z))


# ------------------------------------------------------------- island 2 ---
def island2(W):
    S, T = W.S, W.T
    C = I2
    R = 39.0
    F = 0.70                      # layout scale: keeps the deck dense
    T.pad(sd_circle(C, R + 2), I2_Z, 9, deck=True)
    S.push((C[0], C[1], I2_Z))
    S.disc("SK_desktop_deck", "pave_white", (0, 0, 0), R, n=160)
    S.disc("NC_decals", "gel_white", (0, 0, 0.012), R, n=160, r0=R - 1.6)
    S.disc("NC_decals", "gel_aqua", (0, 0, 0.012), 22.6, n=120, r0=22.0)
    S.lathe("SC_desktop_deck", "shell_white", [(R, -3.0), (R, 0.0)], n=160)
    keep = []

    def put(x, y, yaw_deg, r, fn):
        x, y = x * F, y * F
        S.push((x, y, 0), radians(yaw_deg))
        fn()
        S.pop()
        keep.append((C[0] + x, C[1] + y, r))

    # three program windows as wallrides, facing the middle
    put(-6, 52, 90, 9, lambda: window_wall(S, "win_paint", "ui_paint", 14, 9.5))
    put(-44, 30, 150, 9, lambda: window_wall(S, "win_pool", "ui_pool", 14, 9.5))
    put(36, 44, 45, 8, lambda: window_wall(S, "win_wallpaper", "ui_wallpaper", 13, 8, ang=55))
    # taskbar: one long ledge across the south side
    put(-28.5, -44, 0, 4, lambda: flat_window(S, "taskbar", "ui_taskbar", 40, 1.9, 0.46))
    keep.append((C[0], C[1] - 36, 4))
    keep.append((C[0] + 14, C[1] - 36, 4))
    put(-30, -8, 20, 10, lambda: cascade(S, "error_cascade"))
    put(22, -14, 180, 9, lambda: player_wall(S, "player_wall"))
    for (x, y, rr) in ((2, 14, 3.4), (-14, -20, 2.6), (30, 18, 2.6)):
        put(x, y, 0, rr + 1, lambda rr=rr: cd_pad(S, "cd_pad", rr))
    put(-22, 22, -35, 5, lambda: cursor_kicker(S, "cursor_kicker", 0.5))
    put(8, -28, 160, 5, lambda: cursor_kicker(S, "cursor_kicker", 0.42, 1.1))
    for (x, y, yw) in ((-8, 34, 10), (14, 32, -20), (40, -8, 80)):
        put(x, y, yw, 5, lambda: flat_window(S, "progress_pad", "ui_progress", 8.5, 1.6, 0.22))
    put(-48, -6, 100, 6, lambda: sk.halfpipe(S, "desktop_mini", 7, 1.4, 2.4, flat=3.6, mat="gel_lime"))
    put(46, 14, 200, 5, lambda: sk.quarter(S, "desktop_qp", 9, 1.8, 2.7, mat="gel_magenta"))
    put(4, -6, 30, 5, lambda: sk.pyramid(S, "desktop_funbox", 7, 2.4, 0.9, mat="gel_orange"))
    put(-36, 46, 120, 4, lambda: sk.rail(S, "scrollbar_rail", [(0, 0, 0.4), (9, 0, 0.4)]))
    put(20, 4, 60, 4, lambda: sk.ledge(S, "desktop_ledge", 8, 0.6, 0.42, glow="glow_cyan"))
    # caustic pool with ducks in the middle of a ring ledge
    S.push((-2, -2 + 0, 0))
    S.pop()
    S.pop()
    W.i2_keep.extend(keep)
    # atrium: a glass vault with an aquarium wall, on the east shore
    S.push((C[0] + 44, C[1] - 27, I2_Z - 0.3), radians(-31))
    t = np.linspace(0, pi, 20)
    for y in np.linspace(-11, 11, 6):
        S.tube("SC_atrium", "shell_white", np.c_[7.5 * np.cos(t), np.full(20, y), 7.5 * np.sin(t)], 0.2, n=8)
    vault = np.array([[[7.5 * cos(a), y, 7.5 * sin(a)] for y in (-11, 11)] for a in t])
    S.grid("SC_atrium", "glass_blue", vault)
    S.box("NC_atrium_tank", "tank_water", (-5.5, -10, 0.6), (-3.0, 10, 5.0))
    S.box("SC_atrium", "shell_white", (-5.8, -10.3, 0), (-2.7, 10.3, 0.6))
    S.box("NC_atrium_floor", "pool_floor", (-7.4, -11, -0.02), (7.4, 11, 0.02))
    rng = np.random.default_rng(3)
    for k in range(12):
        real_fish(S, (rng.uniform(-5.2, -3.3), rng.uniform(-9, 9), rng.uniform(1.2, 4.5)), rng.uniform(0.5, 0.9), rng.choice([pi / 2, -pi / 2]),
                  kind="gold")
    S.pop()
    W.i2_keep.append((C[0] + 44, C[1] - 27, 14))
    # shore walk round the island
    th = np.linspace(0, tau, 220, endpoint=False)
    rb = T.coast2(th) - 12
    walk = np.c_[C[0] + rb * np.cos(th), C[1] + rb * np.sin(th), np.full_like(th, I2_Z - 0.4)]
    T.pad(lambda x, y: np.abs(np.hypot(x - C[0], y - C[1]) - (T.coast2(np.arctan2(y - C[1], x - C[0])) - 12)) - 4.0, I2_Z - 0.4, 4)
    S.sweep("SK_desktop_walk", "boardwalk", walk, [(-3, 0), (3, 0)], closed=True)
    S.sweep("SC_desktop_walk", "marble", walk, [(3, 0), (3, -2.4)], closed=True)
    S.sweep("SC_desktop_walk", "marble", walk, [(-3, -2.0), (-3, 0)], closed=True)
    for k in range(4):
        a = radians(20 + k * 90)
        flow = [(C[0] + (R - 3) * cos(a), C[1] + (R - 3) * sin(a), I2_Z + 0.004), (C[0] + (R + 3) * cos(a), C[1] + (R + 3) * sin(a), I2_Z - 0.1),
                (C[0] + (float(T.coast2(a)) - 13) * cos(a), C[1] + (float(T.coast2(a)) - 13) * sin(a), I2_Z - 0.37)]
        W.flow_path(W, "desktop_link_%d" % k, flow, 5.0, mat="gel_aqua")
    # causeway from the main island
    a0 = radians(6)
    rs = float(Terrain.coast(a0)) - 22 + 4.6
    start = np.array([rs * cos(a0), rs * sin(a0), BW_Z])
    aw = radians(183)
    endp = np.array([C[0] + (float(T.coast2(aw)) - 9.5) * cos(aw), C[1] + (float(T.coast2(aw)) - 9.5) * sin(aw), I2_Z - 0.38])
    cw = smooth_path([start, start + [14, 2, 0.0], (start + endp) / 2 + [0, 6, 3.2], endp - [14, 0, 0.0], endp], 1.0)
    u = np.linspace(0, 1, len(cw))
    cw[:, 2] += 0.5 * np.sin(u * 11 * pi) ** 2 * np.sin(pi * u)
    ribbon(S, "causeway", cw, 6.0, "gel_aqua", thick=0.5, edge=0.4)
    Tn, Nn, Rn = frames(cw)
    for sg in (-1, 1):
        edge = cw + Rn * sg * 3.0
        S.sweep("SK_causeway_wall", "marble", edge, [(-0.22, 0), (-0.22, 0.4), (0.22, 0.4), (0.22, -0.3)])
        for off in (-0.22, 0.22):
            S.grind(edge + Rn * off + Z * 0.4)
    W.late.append(lambda: pylons(S, T, "causeway", cw, every=10, r=0.4, min_h=0.4, ok=lambda x, y: hypot(x, y) > 185 and hypot(x - C[0], y - C[1]) > 92))
    W.wall_gaps.append((6, 1.6))
    W.keepout.append(sd_path(cw[::4], 6))
    rainbow(S, start + [20, -40, -2], endp + [-10, -46, -2.6])


# ----------------------------------------------------- street-spot kit ---
def spot(S, kind, name):
    """One compact street spot, about 9 m long and under 3.4 m wide,
    riding along +x. Returns nothing; pieces are placed in local space."""
    k = kind % 11
    if k == 0:
        sk.ledge(S, name + "_ledge", 8.0, 0.55, 0.42, glow="glow_cyan")
    elif k == 1:
        sk.manual_pad(S, name + "_pad", 6.5, 1.8, 0.2, top="gel_lime")
        S.push((7.5, 0, 0)); sk.ledge(S, name + "_ledge", 3.0, 0.5, 0.5); S.pop()
    elif k == 2:
        sk.rail(S, name + "_bar", [(0, 0, 0.36), (7.5, 0, 0.36)])
    elif k == 3:
        sk.kicker(S, name + "_kicker", 3.0, 0.55, 3.2, mat="gel_orange")
        S.push((9.2, 0, 0), pi); sk.bank(S, name + "_lander", 3.0, 0.45, 2.4, mat="gel_orange"); S.pop()
    elif k == 4:
        sk.extrude(S, "SK_" + name + "_aframe", "gel_yellow", [(0, 0), (2.4, 0.75), (4.6, 0.75), (7.0, 0)], 3.0, "shell_white")
        sk.rail(S, name + "_aframe_rail", [(1.6, 0, 0.95), (2.4, 0, 1.15), (4.6, 0, 1.15), (5.4, 0, 0.95)], post=1.4,
                ground=lambda p: float(np.interp(p[0], [0, 2.4, 4.6, 7.0], [0, 0.75, 0.75, 0])))
    elif k == 5:
        S.push((2.6, 0, 0)); sk.pyramid(S, name + "_pyramid", 3.3, 1.2, 0.6, mat=GELS[kind % 7]); S.pop()
    elif k == 6:
        flat_window(S, name + "_progress", "ui_progress", 8.0, 1.5, 0.22)
    elif k == 7:
        S.push((0, 0.6, 0)); sk.ledge(S, name + "_ledge", 7.0, 0.5, 0.32); S.pop()
        S.push((1.5, -0.6, 0)); sk.ledge(S, name + "_ledge", 7.0, 0.5, 0.6, glow="glow_lime"); S.pop()
    elif k == 8:
        x = np.linspace(0, 7, 30)
        sk.extrude(S, "SK_" + name + "_wave", GELS[kind % 7], np.c_[x, 0.3 * (1 - np.cos(tau * x / 7))], 3.0, "shell_white")
    elif k == 9:
        S.push((2.0, 0, 0)); cd_pad(S, name + "_cd", 1.65, 0.22); S.pop()
    else:
        flat_window(S, name + "_dialog", "ui_error", 4.6, 2.3, 0.4)


def scatter_spots(W):
    """Street spots along the inner lane of the boardwalk and in pockets
    beside the ring path, so no stretch of path is empty."""
    S, T = W.S, W.T
    skip = [(0, 14), (22, 5), (44, 5), (58, 5), (90, 6), (135, 7), (176, 5), (197, 4), (225, 5), (244, 5), (268, 6), (272, 4), (288, 8), (301, 9), (6, 4)]
    n = 50
    kind = 0
    for i in range(n):
        a = i * tau / n + 0.06
        dg = np.degrees(a) % 360
        if any(abs((dg - g + 180) % 360 - 180) < hw for g, hw in skip):
            continue
        r = float(Terrain.coast(a)) - 22.0
        S.push((r * cos(a), r * sin(a), BW_Z), a + pi / 2)
        S.push((-4.5, 2.35, 0))
        spot(S, kind, "bw_spot")
        S.pop()
        S.pop()
        kind += 1
    # orb lamps on the lawn side of the boardwalk
    for i in range(64):
        a = i * tau / 64 + 0.02
        if any(abs((np.degrees(a) % 360 - g + 180) % 360 - 180) < hw + 1 for g, hw in skip):
            continue
        r = float(Terrain.coast(a)) - 22.0 - 6.3
        orb_lamp(S, (r * cos(a), r * sin(a), BW_Z - 0.3), a, glow=("glow_cyan", "glow_lime", "glow_magenta")[i % 3])
    # pockets beside the ring path
    for j, dg in enumerate((14, 66, 112, 156, 200, 251, 290, 336)):
        a = radians(dg)
        c = polar(59.5, dg)
        zc = 5.6 + 1.2 * cos(a)
        T.pad(sd_circle(c[:2], 7.0), zc, 4, deck=True)
        S.push((c[0], c[1], zc), a + pi / 2)
        S.disc("SK_ring_pockets", "pave_blue", (0, 0, 0), 6.5, n=48)
        S.lathe("SC_ring_pockets", "shell_white", [(6.5, -2.5), (6.5, 0)], n=48)
        S.push((-4.0, 1.2, 0))
        spot(S, (3, 4, 8, 0, 10, 7, 5, 1)[j], "pocket_%d" % j)
        S.pop()
        S.pop()
        W.keepout.append(sd_circle(c[:2], 7.5))


def more_bowl_spots(W):
    S = W.S
    S.push((-96.0, 10.0, 4.4))
    for (x, y, yaw, kind) in ((-4, 33, 0, 7), (-26, -27, 30, 4), (0, -33, 0, 6), (31, 16, 100, 2), (-33, 14, 80, 9), (20, 30, -30, 3)):
        S.push((x, y, 0), radians(yaw))
        spot(S, kind, "bowls_spot")
        S.pop()
    S.pop()
    S.push((5.0, -100.0, 3.5))
    for (x, y, yaw, kind) in ((24, -22, 20, 10), (-27, -19, -40, 9), (-12, 31, 0, 6), (27, 24, 70, 8), (10, -33, 0, 7)):
        S.push((x, y, 0), radians(yaw))
        spot(S, kind, "minis_spot")
        S.pop()
    S.pop()


def pool_life(W):
    """Ducks and goldfish in the garden pool, and a few drifting CDs."""
    S = W.S
    rng = np.random.default_rng(21)
    for k in range(3):
        duck(S, (76 + rng.uniform(-8, 8), 76 + rng.uniform(-8, 8), 3.0), rng.uniform(0, tau), k=rng.uniform(0.8, 1.6))
    duck(S, (118, 18, BW_Z + 4.72 + 0.34 - 0.02 + 0.0), 0.5, k=0.7)
    for k in range(9):
        real_fish(S, (76 + rng.uniform(-10, 10), 76 + rng.uniform(-10, 10), 2.55), rng.uniform(0.5, 0.9), rng.uniform(0, tau), kind="gold")
    duck(S, (-236 + 18, -72 + 14, 0.0), 2.0, k=2.4)
