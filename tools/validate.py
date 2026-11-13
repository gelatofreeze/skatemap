"""Collision checks on the generated map. Run: python3 tools/validate.py

1. Terrain must sit below every skate surface, so no invisible ground
   pokes through a ramp or deck.
2. Nothing solid (SC_) may be scattered inside a skate surface's airspace:
   palm trunks, rocks and lamp posts are tested against every SK_ vertex.
"""
import os, sys
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frutiger import layout

W = layout.build()
S, T = W.S, W.T
bad = 0
sk_pts = []
for (name, mat), d in S.parts.items():
    if not name.startswith("SK_"):
        continue
    V = np.vstack(d["V"])
    # only vertices of upward-facing faces are ride surface
    up = np.zeros(len(V), bool)
    for f in d["F"]:
        a, b, c = V[f[0]], V[f[1]], V[f[2]]
        nrm = np.cross(b - a, c - a)
        ln = np.linalg.norm(nrm)
        if ln > 0 and nrm[2] / ln > 0.3:
            up[list(f)] = True
    V = V[up]
    if not len(V):
        continue
    sk_pts.append(V)
    h = T.height(V[:, 0], V[:, 1])
    over = h - V[:, 2]
    worst = over.max()
    if worst > -0.02:
        n = int((over > -0.02).sum())
        bad += 1
        print("TERRAIN  %-28s %-12s %5d verts within 2 cm of terrain, worst %+.2f m" % (name, mat, n, worst))
sk_pts = np.vstack(sk_pts)
tree = cKDTree(sk_pts[:, :2])
for group in ("SC_palm_trunks", "SC_rocks", "SC_orb_lamps"):
    for (name, mat), d in S.parts.items():
        if name != group:
            continue
        V = np.vstack(d["V"])
        dist, idx = tree.query(V[:, :2])
        hit = (dist < 0.6) & (V[:, 2] > sk_pts[idx, 2] - 0.2) & (V[:, 2] < sk_pts[idx, 2] + 3.0)
        if hit.any():
            bad += 1
            print("INTRUDES %-28s %5d verts inside the space above a skate surface" % (name, int(hit.sum())))
            for c in np.unique(np.round(V[hit][:, :2] / 6).astype(int), axis=0)[:8]:
                print("         near x=%d y=%d" % (c[0] * 6, c[1] * 6))
print("checks failed:" if bad else "all checks passed", bad if bad else "")
