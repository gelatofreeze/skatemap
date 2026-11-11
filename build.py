"""Build Frutiger Air.

    python3 build.py            # dist/FrutigerAir.blend + preview GLBs
    python3 build.py --preview  # preview GLBs only (faster)

Needs: pip install bpy numpy
"""
import os
import sys
import json
import numpy as np
from frutiger import layout, export

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
PREVIEW = os.path.join(ROOT, "viewer", "assets")


def globe_texture(w=1024, h=512):
    """Stylised Earth: glossy blue ocean, green land, white caps."""
    lon = np.linspace(0, 2 * np.pi, w)[:, None]
    lat = np.linspace(-np.pi / 2, np.pi / 2, h)[None, :]
    x, y, z = np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat) + 0 * lon
    n = (np.sin(3.1 * x + 1.7 * y) * np.cos(2.3 * y - 2.9 * z) + 0.6 * np.sin(5.3 * z + 4.1 * x + 1.0)
         + 0.35 * np.sin(9.7 * x - 7.3 * y + 3 * z) + 0.2 * np.sin(17 * y + 13 * z))
    land = np.clip((n - 0.25) * 6, 0, 1)[..., None]
    ocean = np.array([0.05, 0.45, 0.95]) + (np.array([0.2, 0.75, 1.0]) - np.array([0.05, 0.45, 0.95])) * np.clip(n + 0.6, 0, 1)[..., None] * 0.6
    green = np.array([0.35, 0.85, 0.2]) + 0 * land
    c = ocean * (1 - land) + green * land
    ice = np.clip((np.abs(z) - 0.86) * 12, 0, 1)[..., None]
    return np.clip(c * (1 - ice) + ice, 0, 1)


def main():
    preview_only = "--preview" in sys.argv
    os.makedirs(DIST, exist_ok=True)
    os.makedirs(PREVIEW, exist_ok=True)
    W = layout.build()
    S = W.S
    import bpy
    export.build_scene(S, {"terrain": W.T.texture(2048), "globe": globe_texture()}, DIST)

    groups = {"terrain": dict(names={"SC_terrain", "NC_seabed", "NC_water"}),
              "skate": dict(prefixes={"SK", "GR"}),
              "scenery": dict(prefixes={"SC"}),
              "palms": dict(names={"NC_palm_fronds_a", "NC_palm_nuts", "NC_bushes"}),
              "deco": dict(prefixes={"NC", "OP"})}
    taken = set()
    manifest = []
    for g, sel in groups.items():
        names = set(sel.get("names", ()))
        for ob in bpy.context.scene.objects:
            if ob.type == "MESH" and ob.name not in taken and ob.name[:2] in sel.get("prefixes", ()):
                names.add(ob.name)
        names -= taken
        taken |= names
        path = os.path.join(PREVIEW, g + ".glb")
        export.export_glb(path, names=names)
        manifest.append(g + ".glb")
        print("%-10s %3d objects %6.1f MB" % (g, len(names), os.path.getsize(path) / 1e6))
    info = dict(files=manifest, spawn=[list(e[1]) for e in S.empties],
                notes={k: {a: (float(b) if np.isscalar(b) else b) for a, b in v.items()} for k, v in W.notes.items()})
    json.dump(info, open(os.path.join(PREVIEW, "manifest.json"), "w"), indent=1)
    if not preview_only:
        export.save_blend(os.path.join(DIST, "FrutigerAir.blend"))
        print("blend %.1f MB" % (os.path.getsize(os.path.join(DIST, "FrutigerAir.blend")) / 1e6))
    for f in ("terrain.png", "globe.png"):
        p = os.path.join(DIST, f)
        if os.path.exists(p):
            os.remove(p)                       # packed into the .blend; not needed loose


if __name__ == "__main__":
    main()
