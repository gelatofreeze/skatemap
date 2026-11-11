"""Mesh collection and geometric primitives. Z is up, units are metres."""
import numpy as np
from math import pi, sin, cos, tau

Z = np.array([0.0, 0.0, 1.0])


def unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1, n)


def smoothstep(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def rotz(a):
    c, s = cos(a), sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


class Scene:
    """Collects geometry as (object name, material) buckets.

    Object name prefixes tell the person tagging the map in ReSkate Studio
    what each object is for:
      SK_  skateable surface      GR_  grindable edge or rail
      SC_  solid scenery          NC_  decoration with no collision
    """

    def __init__(self):
        self.parts = {}
        self.empties = []
        self.grinds = []
        self.xf = [(np.eye(3), np.zeros(3))]

    # -- transform stack: place pieces authored in local space ------------
    def push(self, pos=(0, 0, 0), yaw=0.0):
        R0, t0 = self.xf[-1]
        R = rotz(yaw)
        self.xf.append((R0 @ R, t0 + R0 @ np.asarray(pos, float)))

    def pop(self):
        self.xf.pop()

    def world(self, V):
        R, t = self.xf[-1]
        return np.asarray(V, float).reshape(-1, 3) @ R.T + t

    def add(self, name, mat, V, F, uv=None):
        V = self.world(V)
        d = self.parts.setdefault((name, mat), dict(V=[], F=[], UV=[], n=0))
        off = d["n"]
        d["V"].append(V)
        d["F"].extend(tuple(int(i) + off for i in f) for f in F)
        d["UV"].append(np.asarray(uv, float).reshape(-1, 2) if uv is not None
                       else V[:, :2] * 0.25)
        d["n"] += len(V)

    def empty(self, name, pos, yaw=0.0):
        R, t = self.xf[-1]
        self.empties.append((name, tuple(R @ np.asarray(pos, float) + t), yaw))

    def grind(self, pts):
        """Record a grindable line (local points) for the Blender scene."""
        self.grinds.append(self.world(pts))

    def sweep_var(self, name, mat, path, sections, up=Z, flip=False):
        """Sweep where the section changes along the path.
        sections has shape (len(path), k, 2)."""
        path = np.asarray(path, float)
        T, N, R = frames(path, up)
        sec = np.asarray(sections, float)
        P = (path[:, None, :] + sec[:, :, 0, None] * R[:, None, :]
             + sec[:, :, 1, None] * N[:, None, :])
        self.grid(name, mat, P, flip=not flip)
        return P

    # -- primitives -------------------------------------------------------
    def grid(self, name, mat, P, cu=False, cv=False, flip=False, uv=None):
        """Quad surface from an (nu, nv, 3) array. Normal is dP/du x dP/dv."""
        P = np.asarray(P, float)
        nu, nv = P.shape[:2]
        idx = np.arange(nu * nv).reshape(nu, nv)
        iu = np.arange(nu if cu else nu - 1)
        iv = np.arange(nv if cv else nv - 1)
        a = idx[np.ix_(iu, iv)]
        b = idx[np.ix_((iu + 1) % nu, iv)]
        c = idx[np.ix_((iu + 1) % nu, (iv + 1) % nv)]
        d = idx[np.ix_(iu, (iv + 1) % nv)]
        F = np.stack([a, b, c, d], -1).reshape(-1, 4)
        if flip:
            F = F[:, ::-1]
        if isinstance(uv, str):            # "grid": u, v run 0..1 across the patch
            uu, vv = np.meshgrid(np.linspace(0, 1, nu), np.linspace(0, 1, nv), indexing="ij")
            uv = np.stack([uu, vv], -1).reshape(-1, 2)
        self.add(name, mat, P.reshape(-1, 3), F.tolist(), uv)

    def box(self, name, mat, lo, hi, mats=None):
        """Axis-aligned box in local space. mats may override the top face."""
        (x0, y0, z0), (x1, y1, z1) = lo, hi
        v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                      [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
        sides = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (3, 2, 1, 0)]
        top = [(4, 5, 6, 7)]
        if mats and "top" in mats:
            self.add(name, mat, v, sides)
            self.add(name, mats["top"], v, top)
        else:
            self.add(name, mat, v, sides + top)

    def lathe(self, name, mat, prof, n=32, a0=0.0, a1=tau, flip=False, uv=None):
        """Surface of revolution about Z. prof is [(r, z), ...] bottom to top."""
        prof = np.asarray(prof, float)
        full = abs(a1 - a0 - tau) < 1e-6 and uv is None
        ang = np.linspace(a0, a1, n, endpoint=not full)
        P = np.stack([np.outer(np.cos(ang), prof[:, 0]),
                      np.outer(np.sin(ang), prof[:, 0]),
                      np.tile(prof[:, 1], (len(ang), 1))], -1)
        self.grid(name, mat, P, cu=full, flip=flip, uv=uv)

    def sphere(self, name, mat, c, r, n=24, squash=1.0, uv=None):
        t = np.linspace(-pi / 2, pi / 2, n // 2 + 1)
        prof = np.stack([r * np.cos(t), r * squash * np.sin(t)], -1)
        self.push(c)
        self.lathe(name, mat, prof, n, uv=uv)
        self.pop()

    def disc(self, name, mat, c, r, n=48, r0=0.0, flip=False):
        ang = np.linspace(0, tau, n, endpoint=False)
        rr = np.array([r0, r])
        P = np.stack([np.outer(np.cos(ang), rr) + c[0],
                      np.outer(np.sin(ang), rr) + c[1],
                      np.full((n, 2), c[2])], -1)
        self.grid(name, mat, P, cu=True, flip=not flip)

    def tube(self, name, mat, path, r, n=10, closed=False, up=Z, caps=True):
        """Round tube along a 3D polyline. r may be a per-point array."""
        path = np.asarray(path, float)
        T, N, R = frames(path, up, closed)
        ang = np.linspace(0, tau, n, endpoint=False)
        rr = np.broadcast_to(np.asarray(r, float), (len(path),))[:, None, None]
        P = path[:, None, :] + rr * (np.cos(ang)[None, :, None] * R[:, None, :]
                                     + np.sin(ang)[None, :, None] * N[:, None, :])
        self.grid(name, mat, P, cu=closed, cv=True)
        if caps and not closed:
            for i, fl in ((0, False), (-1, True)):
                ring = P[i]
                V = np.vstack([ring, path[i]])
                F = [(n, (k + 1) % n, k) if not fl else (n, k, (k + 1) % n)
                     for k in range(n)]
                self.add(name, mat, V, F)

    def sweep(self, name, mat, path, section, up=Z, closed=False, flip=False,
              bank=None):
        """Sweep a 2D section [(right, up), ...] along a 3D path. A section
        running left to right faces up; closed sections run clockwise seen
        from behind."""
        path = np.asarray(path, float)
        T, N, R = frames(path, up, closed)
        if bank is not None:
            b = np.asarray(bank, float)[:, None]
            N, R = N * np.cos(b) + R * np.sin(b), R * np.cos(b) - N * np.sin(b)
        sec = np.asarray(section, float)
        P = (path[:, None, :] + sec[None, :, 0, None] * R[:, None, :]
             + sec[None, :, 1, None] * N[:, None, :])
        self.grid(name, mat, P, cu=closed, flip=not flip)
        return P


def frames(path, up=Z, closed=False):
    """Tangent, normal (up-ish) and right vectors along a path, with the
    normal carried forward so loops and corkscrews do not twist."""
    P = np.asarray(path, float)
    if closed:
        T = unit(np.roll(P, -1, 0) - np.roll(P, 1, 0))
    else:
        T = unit(np.gradient(P, axis=0))
    N = np.zeros_like(P)
    n = np.asarray(up, float)
    for i in range(len(P)):
        n = n - np.dot(n, T[i]) * T[i]
        if np.linalg.norm(n) < 1e-6:
            n = np.cross(T[i], [1, 0, 0])
        n = n / np.linalg.norm(n)
        N[i] = n
    return T, N, np.cross(T, N)


def arc_pts(c, r, a0, a1, n, z=0.0):
    a = np.linspace(a0, a1, n)
    return np.stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a), np.full(n, z)], -1)


def resample(P, step):
    """Resample a polyline to roughly even spacing."""
    P = np.asarray(P, float)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    n = max(2, int(d[-1] / step) + 1)
    s = np.linspace(0, d[-1], n)
    return np.stack([np.interp(s, d, P[:, k]) for k in range(3)], -1)


def smooth_path(pts, step=1.0, it=4):
    """Round the corners of a control polyline (Chaikin), then resample."""
    P = np.asarray(pts, float)
    for _ in range(it):
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]):
            Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        Q.append(P[-1])
        P = np.array(Q)
    return resample(P, step)
