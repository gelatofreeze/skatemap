"""Skatepark pieces, authored in local space and placed with S.push().
Convention: +x is the direction you ride into the piece, y is its width."""
import numpy as np
from math import sin, cos, pi, tau, sqrt, acos, asin, radians
from .mesh import Z, frames, smoothstep

RISE, RUN = 0.17, 0.36           # stair step


def trans_profile(h, R, n=None, x0=0.0, z0=0.0):
    """Transition arc rising along +x from (x0, z0) to height h. If h > R the
    top is vertical ('vert')."""
    a_max = pi / 2 if h >= R else acos(1 - h / R)
    n = n or max(8, int(a_max * R / 0.12))
    a = np.linspace(0, a_max, n)
    pts = [(x0 + R * sin(t), z0 + R * (1 - cos(t))) for t in a]
    if h > R:
        pts += [(x0 + R, z0 + R + (h - R) * k / 3) for k in (1, 2, 3)]
    return pts


def extrude(S, name, mat, prof, w, side=None, y0=None, base=0.0, uvs=None):
    """Extrude a height profile [(x, z), ...] across width w (along y).
    Top is the riding surface; sides and ends are closed down to base."""
    prof = np.asarray(prof, float)
    side = side or mat
    ya = -w / 2 if y0 is None else y0
    yb = ya + w
    n = len(prof)
    top = np.zeros((n, 2, 3))
    top[:, 0] = np.c_[prof[:, 0], np.full(n, ya), prof[:, 1]]
    top[:, 1] = np.c_[prof[:, 0], np.full(n, yb), prof[:, 1]]
    S.grid(name, mat, top)
    for y, fl in ((ya, False), (yb, True)):
        cap = np.zeros((n, 2, 3))
        cap[:, 0] = np.c_[prof[:, 0], np.full(n, y), np.full(n, base)]
        cap[:, 1] = np.c_[prof[:, 0], np.full(n, y), prof[:, 1]]
        S.grid(name, side, cap, flip=fl)
    for i, fl in ((0, False), (-1, True)):
        x, z = prof[i]
        if z - base > 1e-3:
            q = [[x, ya, base], [x, yb, base], [x, yb, z], [x, ya, z]]
            S.add(name, side, q, [(3, 2, 1, 0) if not fl else (0, 1, 2, 3)])


def coping(S, name, a, b, r=0.045):
    """Steel coping / rail edge between two local points. Also records a
    grind line for the Blender scene."""
    # Visual only, sunk flush with the deck: protruding coping trips the board
    # in this game. The lip itself is the smooth edge of the ramp mesh.
    dz = np.array([0, 0, -r - 0.004])
    a, b = np.asarray(a, float) + dz, np.asarray(b, float) + dz
    S.tube("NC_coping", "chrome", [a, b], r, n=8)
    S.grind([a, b])


def quarter(S, name, w, h, R, mat="gel_cyan", deck=1.6, side="shell_white"):
    p = trans_profile(h, R)
    xe = p[-1][0]
    extrude(S, "SK_" + name, mat, p, w, side)
    extrude(S, "SK_" + name, "gel_white", [(xe, h), (xe + deck, h)], w, side)
    coping(S, name, (xe, -w / 2, h + 0.01), (xe, w / 2, h + 0.01))
    return xe + deck


def halfpipe(S, name, w, h, R, flat=4.0, mat="gel_cyan", deck=1.6, side="shell_white"):
    """Centred on the origin, riding along x."""
    p = trans_profile(h, R)
    xe = p[-1][0]
    half = flat / 2
    right = [(half + x, z) for x, z in p]
    left = [(-half - x, z) for x, z in reversed(p)]
    extrude(S, "SK_" + name, mat, left + right, w, side)
    for sgn in (-1, 1):
        a, b = sgn * (half + xe), sgn * (half + xe + deck)
        extrude(S, "SK_" + name, "gel_white", [(min(a, b), h), (max(a, b), h)], w, side)
        coping(S, name, (a, -w / 2, h + 0.01), (a, w / 2, h + 0.01))
    return half + xe + deck


def spine(S, name, w, h, R, mat="gel_magenta", side="shell_white"):
    p = trans_profile(h, R)
    xe = p[-1][0]
    prof = [(x - xe, z) for x, z in p] + [(xe - x, z) for x, z in reversed(p)][1:]
    extrude(S, "SK_" + name, mat, prof, w, side)
    coping(S, name, (0, -w / 2, h + 0.01), (0, w / 2, h + 0.01))


def bank(S, name, w, h, L, mat="gel_yellow", deck=0.0, side="shell_white", round_top=0.0):
    prof = [(0, 0), (L, h)]
    if deck:
        prof.append((L + deck, h))
    extrude(S, "SK_" + name, mat, prof, w, side)


def kicker(S, name, w, h, R, mat="gel_orange", side="shell_white"):
    extrude(S, "SK_" + name, mat, trans_profile(h, R), w, side)


def pyramid(S, name, base, top, h, mat="gel_violet", topmat="gel_white"):
    b, t = base / 2, top / 2
    lo = np.array([[-b, -b, 0], [b, -b, 0], [b, b, 0], [-b, b, 0]], float)
    hi = np.array([[-t, -t, h], [t, -t, h], [t, t, h], [-t, t, h]], float)
    for i in range(4):
        j = (i + 1) % 4
        S.add("SK_" + name, mat, [lo[i], lo[j], hi[j], hi[i]], [(0, 1, 2, 3)])
    S.add("SK_" + name, topmat, hi, [(0, 1, 2, 3)])
    for i in range(4):
        S.grind([hi[i], hi[(i + 1) % 4]])


def ledge(S, name, L, w=0.5, h=0.45, mat="marble", top="glass_frost", glow=None):
    """Ledge along x from 0 to L, centred on y."""
    S.box("SK_" + name, mat, (0, -w / 2, 0), (L, w / 2, h), mats={"top": top})
    if glow:
        S.box("NC_" + name + "_glow", glow, (0.05, -w / 2 - 0.012, h - 0.09), (L - 0.05, w / 2 + 0.012, h - 0.05))
    for y in (-w / 2, w / 2):
        S.grind([(0, y, h), (L, y, h)])


def manual_pad(S, name, L, w, h=0.22, mat="marble", top="gel_white"):
    S.box("SK_" + name, mat, (0, -w / 2, 0), (L, w / 2, h), mats={"top": top})
    for y in (-w / 2, w / 2):
        S.grind([(0, y, h), (L, y, h)])


def rail(S, name, pts, h=0.0, r=0.04, post=1.6, mat="chrome_glow", ground=None):
    """Round rail through local points (already at rail height + h)."""
    P = np.asarray(pts, float) + np.array([0, 0, h])
    S.tube("GR_" + name, mat, P, r, n=10)
    S.grind(P)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    for s in np.arange(0.15, d[-1], post):
        p = np.array([np.interp(s, d, P[:, k]) for k in range(3)])
        g = ground(p) if ground else 0.0
        if p[2] - g > 0.05:
            S.tube("SC_" + name + "_posts", "chrome", [(p[0], p[1], g), (p[0], p[1], p[2] - r * 0.5)], r * 0.8, n=6, caps=False)


def stairs(S, name, n, w, mat="marble", rails=(), hubbas=(), rail_h=0.75):
    """Stair set descending along +x from z = n*RISE at x=0 to z=0.
    rails / hubbas are y offsets."""
    H, L = n * RISE, n * RUN
    prof = []
    for i in range(n):
        prof += [(i * RUN, H - i * RISE), (i * RUN, H - (i + 1) * RISE)] if i else [(0, H), (0, H - RISE)]
        prof += [((i + 1) * RUN, H - (i + 1) * RISE)]
    extrude(S, "SK_" + name, mat, prof, w)
    for y in rails:
        rail(S, name + "_rail", [(-0.2, y, H + rail_h), (L + 0.3, y, rail_h - 0.02)], post=1.2,
             ground=lambda p: float(np.clip(H - p[0] / RUN * RISE, 0, H)))
    for y in hubbas:
        hubba(S, name + "_hubba", n, y)
    return L, H


def hubba(S, name, n, y, w=0.55, h=0.5, mat="marble", top="glass_frost"):
    """Ledge that runs down beside a stair set."""
    H, L = n * RISE, n * RUN
    path = [(-0.9, y, H), (0, y, H), (L + 0.4, y, RISE * 0.2), (L + 1.4, y, 0)]
    top_l = [(x, y - w / 2, z + h) for x, _, z in path]
    top_r = [(x, y + w / 2, z + h) for x, _, z in path]
    bot_l = [(x, y - w / 2, 0) for x, _, z in path]
    bot_r = [(x, y + w / 2, 0) for x, _, z in path]
    S.grid("SK_" + name, top, np.array([top_l, top_r]).transpose(1, 0, 2))
    S.grid("SK_" + name, mat, np.array([bot_l, top_l]).transpose(1, 0, 2))
    S.grid("SK_" + name, mat, np.array([top_r, bot_r]).transpose(1, 0, 2))
    S.add("SK_" + name, mat, [bot_l[0], bot_r[0], top_r[0], top_l[0]], [(3, 2, 1, 0)])
    S.add("SK_" + name, mat, [bot_l[-1], bot_r[-1], top_r[-1], top_l[-1]], [(0, 1, 2, 3)])
    S.grind(top_l[1:3]); S.grind(top_r[1:3])


def bowl(S, name, outline, depth, R, mat="gel_cyan", n=120, apron=1.3,
         tile="tile_aqua", apron_mat="gel_white"):
    """Sunken bowl. outline(theta) -> radius, star-shaped about the origin.
    Lip is at z=0; the terrain underneath must be dug out."""
    th = np.linspace(0, tau, n, endpoint=False)
    r = np.array([outline(t) for t in th])
    O = np.stack([r * np.cos(th), r * np.sin(th)], -1)
    tang = np.roll(O, -1, 0) - np.roll(O, 1, 0)
    tang /= np.linalg.norm(tang, axis=1)[:, None]
    inward = np.stack([-tang[:, 1], tang[:, 0]], -1)
    a_max = pi / 2 if depth >= R else acos(1 - depth / R)
    lip_d = R * (1 - sin(a_max))
    rows = []
    vert = max(0.0, depth - R)
    tile_rows = 0
    if vert > 0:
        for k in range(3):
            rows.append((0.0, -vert * k / 3))
    for a in np.linspace(a_max, 0, max(10, int(a_max * R / 0.14))):
        rows.append((R * (1 - sin(a)) - lip_d, -depth + R * (1 - cos(a))))
    d_in = rows[-1][0]
    # flat floor: shrink the inner contour toward the centre
    inner = O + inward * d_in
    cen = inner.mean(0)
    P = np.zeros((n, len(rows) + 9, 3))
    for k, (d, z) in enumerate(rows):
        P[:, k, :2] = O + inward * d
        P[:, k, 2] = z
    for j in range(9):
        s = 1 - (j + 1) / 9.0 * 0.985
        P[:, len(rows) + j, :2] = cen + (inner - cen) * s
        P[:, len(rows) + j, 2] = -depth
    # split the first 0.35 m of wall into a tile band
    zs = np.array([z for _, z in rows])
    kt = int(np.searchsorted(-zs, 0.35)) + 1
    S.grid("SK_" + name, tile, P[:, :kt + 1], cu=True)
    S.grid("SK_" + name, mat, P[:, kt:], cu=True)
    last = P[:, -1]
    S.add("SK_" + name, mat, np.vstack([last, [cen[0], cen[1], -depth]]),
          [(i, (i + 1) % n, n) for i in range(n)])
    ap = np.zeros((n, 2, 3))
    ap[:, 0, :2] = O
    ap[:, 1, :2] = O - inward * apron
    S.grid("SK_" + name, apron_mat, ap, cu=True, flip=True)
    lip = np.c_[O, np.full(n, -0.054)]
    S.tube("NC_coping", "chrome", lip, 0.05, n=8, closed=True)
    S.grind(np.vstack([lip, lip[:1]]))
    return np.c_[O - inward * apron, np.zeros(n)]      # apron's outer ring, for the deck to meet
