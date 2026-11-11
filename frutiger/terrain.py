"""Island heightfield: coastline, hill, beach, sea bed, and flat pads that
park slabs sit on. Slabs are built 0.15 m above their pad so the terrain
never pokes through a skate surface."""
import numpy as np
from scipy.spatial import cKDTree
from .mesh import smoothstep

EXTENT = 340.0      # half-size of the terrain grid
CLEAR = 0.15        # how far terrain sits below a slab


def sd_circle(c, r):
    return lambda x, y: np.hypot(x - c[0], y - c[1]) - r


def sd_box(c, half, yaw=0.0, rnd=0.0):
    cs, sn = np.cos(-yaw), np.sin(-yaw)

    def f(x, y):
        dx, dy = x - c[0], y - c[1]
        u = np.abs(dx * cs - dy * sn) - (half[0] - rnd)
        v = np.abs(dx * sn + dy * cs) - (half[1] - rnd)
        return (np.hypot(np.maximum(u, 0), np.maximum(v, 0))
                + np.minimum(np.maximum(u, v), 0) - rnd)
    return f


def sd_path(path, r):
    """Distance to a polyline (sampled finely), minus r. With
    want_index=True also returns the nearest original point index."""
    P = np.asarray(path, float)[:, :2]
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    reps = np.maximum(1, np.ceil(seg / 0.5).astype(int))
    dense, owner = [], []
    for i, k in enumerate(reps):
        t = np.arange(k)[:, None] / k
        dense.append(P[i] + t * (P[i + 1] - P[i]))
        owner.append(np.where(t[:, 0] < 0.5, i, i + 1))
    dense.append(P[-1:])
    owner.append(np.array([len(P) - 1]))
    tree = cKDTree(np.vstack(dense))
    owner = np.concatenate(owner)

    def f(x, y, want_index=False):
        shp = np.shape(x)
        d, i = tree.query(np.stack([np.ravel(x), np.ravel(y)], -1))
        if want_index:
            return (d - r).reshape(shp), owner[i].reshape(shp)
        return (d - r).reshape(shp)
    return f


class Terrain:
    def __init__(self):
        self.pads = []

    @staticmethod
    def coast(th):
        return 185 + 8 * np.sin(2 * th + 0.5) + 5 * np.sin(3 * th + 1.7) + 3 * np.sin(5 * th)

    ISLET = (-236.0, -72.0)

    def base(self, x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        r = np.hypot(x, y)
        sd = self.coast(np.arctan2(y, x)) - r          # distance inland
        sea = -7.0 * (1 - np.exp(np.minimum(sd, 0) / 40.0))
        land = 2.2 * (1 - np.exp(-np.maximum(sd, 0) / 9.0))
        hill = 10.0 * np.exp(-(r / 50.0) ** 2)
        roll = (0.45 * np.sin(x * 0.11 + 1.3) * np.cos(y * 0.09 - 0.4)
                + 0.25 * np.sin(x * 0.23 - y * 0.19)) * smoothstep(20, 45, sd)
        h = np.where(sd < 0, sea, land + hill + roll)
        di = np.hypot(x - self.ISLET[0], y - self.ISLET[1])
        h = h + 9.0 * np.exp(-(di / 17.0) ** 2)
        # sand bar that the pier pads rest near, and a soft reef ring
        h = h + 1.2 * np.exp(-((r - 300) / 14.0) ** 2) * (sd < 0)
        return h

    def pad(self, sdf, z, blend=8.0):
        """Flatten terrain to z (number or f(x, y)) where sdf < 0."""
        self.pads.append(("flat", sdf, z, blend))

    def dig(self, sdf, depth, blend=5.0):
        """Lower terrain by depth where sdf < 0 (for sunken bowls, pools)."""
        self.pads.append(("dig", sdf, depth, blend))

    def cap(self, sdf, z, blend=6.0):
        """Keep terrain at or below z (number or f(x, y)) where sdf < 0."""
        self.pads.append(("cap", sdf, z, blend))

    def height(self, x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        h = self.base(x, y)
        for mode, sdf, z, blend in self.pads:
            d = sdf(x, y)
            w = 1 - smoothstep(0, blend, d)
            if mode == "dig":
                h = h - z * w
                continue
            zt = (z(x, y) if callable(z) else z) - CLEAR
            if mode == "cap":
                zt = np.minimum(h, zt)
            h = h + (zt - h) * w
        return h

    def clear_of_pads(self, x, y, margin=3.0):
        """True where no pad is within margin (used to scatter scenery)."""
        ok = np.ones(np.shape(x), bool)
        for mode, sdf, z, blend in self.pads:
            ok &= sdf(x, y) > margin
        return ok

    def h1(self, x, y):
        return float(self.height(np.array([x]), np.array([y]))[0])

    # -- mesh and texture -------------------------------------------------
    def build(self, S, step=2.0):
        n = int(2 * EXTENT / step) + 1
        ax = np.linspace(-EXTENT, EXTENT, n)
        X, Y = np.meshgrid(ax, ax, indexing="ij")
        H = self.height(X, Y)
        P = np.stack([X, Y, H], -1)
        uv = np.stack([(X + EXTENT) / (2 * EXTENT), (Y + EXTENT) / (2 * EXTENT)], -1)
        S.grid("SC_terrain", "terrain", P, uv=uv.reshape(-1, 2))
        # far sea bed so the horizon is never empty
        e, f = EXTENT, 2600.0
        for (x0, x1, y0, y1) in ((-f, f, e, f), (-f, f, -f, -e), (-f, -e, -e, e), (e, f, -e, e)):
            S.add("NC_seabed", "seabed", [[x0, y0, -7], [x1, y0, -7], [x1, y1, -7], [x0, y1, -7]],
                  [(0, 1, 2, 3)])

    def texture(self, res=2048):
        """Albedo map: sand, wet sand, lawn, sea-bed, with painted variation."""
        ax = np.linspace(-EXTENT, EXTENT, res)
        X, Y = np.meshgrid(ax, ax, indexing="ij")
        H = self.height(X, Y)
        gx, gy = np.gradient(H, ax, ax)
        slope = np.hypot(gx, gy)
        rng = np.random.default_rng(7)
        grain = rng.random((res, res))
        blot = (np.sin(X * 0.21 + 2 * np.sin(Y * 0.05)) * np.sin(Y * 0.17 + 1.5 * np.cos(X * 0.07))
                + 0.5 * np.sin(X * 0.63 + Y * 0.41))
        col = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) / 255
        sand, wet = col("#FBEBC0"), col("#E6CF96")
        lawn_a, lawn_b, lawn_c = col("#4CC417"), col("#7BE02C"), col("#2FA312")
        bed_a, bed_b, bed_c = col("#D9F7E4"), col("#35D9D2"), col("#0F7FD6")
        rock = col("#B9B3A6")

        def mix(a, b, t):
            return a + (b - a) * t[..., None]

        ones = np.ones_like(H)[..., None]
        c = mix(sand * ones, wet * ones, smoothstep(0.7, 0.0, H))
        stripes = 0.5 + 0.5 * np.sin((X + Y) * 0.9)          # mown-lawn stripes
        lawn = mix(lawn_a * ones, lawn_b * ones, np.clip(0.5 + 0.35 * blot + 0.15 * (stripes - 0.5), 0, 1))
        lawn = mix(lawn, lawn_c * ones, smoothstep(0.4, 1.0, -blot) * 0.6)
        g = smoothstep(1.5, 2.3, H + 0.25 * blot)
        c = mix(c, lawn, g)
        c = mix(c, rock * ones, smoothstep(0.75, 1.2, slope) * g)
        bed = mix(bed_a * ones, bed_b * ones, smoothstep(-0.2, -2.6, H))
        bed = mix(bed, bed_c * ones, smoothstep(-2.6, -6.6, H))
        ripples = 0.5 + 0.5 * np.sin(X * 1.3 + 3 * np.sin(Y * 0.31)) * np.sin(Y * 1.1 + 2 * np.cos(X * 0.27))
        bed = bed * (0.93 + 0.07 * ripples[..., None])
        c = mix(c, bed, smoothstep(0.0, -0.4, H))
        c = c * (0.94 + 0.06 * grain[..., None])
        return np.clip(c, 0, 1)
