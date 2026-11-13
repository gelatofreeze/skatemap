"""Turn the collected geometry into a Blender scene, then save .blend / .glb."""
import os
from math import radians
import numpy as np
import bpy
import bmesh

# name: (base colour, roughness, metallic, alpha, emission strength, clearcoat)
MATERIALS = {
    "terrain":      ("#FFFFFF", 0.85, 0.0, 1.0, 0.0, 0.0),
    "seabed":       ("#0F7FD6", 0.9, 0.0, 1.0, 0.0, 0.0),
    "water":        ("#2ED3E6", 0.04, 0.0, 0.45, 0.0, 1.0),
    "water_fall":   ("#C8F6FF", 0.08, 0.0, 0.55, 0.25, 1.0),
    "tank_water":   ("#1E9BF0", 0.03, 0.0, 0.30, 0.0, 1.0),
    "gel_cyan":     ("#00B7F4", 0.10, 0.0, 1.0, 0.0, 1.0),
    "gel_aqua":     ("#17E0CE", 0.10, 0.0, 1.0, 0.0, 1.0),
    "gel_lime":     ("#8FE01E", 0.10, 0.0, 1.0, 0.0, 1.0),
    "gel_yellow":   ("#FFD60A", 0.10, 0.0, 1.0, 0.0, 1.0),
    "gel_orange":   ("#FF8A00", 0.10, 0.0, 1.0, 0.0, 1.0),
    "gel_magenta":  ("#FF2D95", 0.10, 0.0, 1.0, 0.0, 1.0),
    "gel_violet":   ("#7A4DFF", 0.10, 0.0, 1.0, 0.0, 1.0),
    "gel_white":    ("#FAFDFF", 0.12, 0.0, 1.0, 0.0, 1.0),
    "path_aqua":    ("#5FE0EE", 0.2, 0.0, 1.0, 0.0, 0.6),
    "shell_white":  ("#F4F8FB", 0.28, 0.0, 1.0, 0.0, 0.5),
    "marble":       ("#E9EEF2", 0.30, 0.0, 1.0, 0.0, 0.3),
    "pave_white":   ("#F2F7FA", 0.35, 0.0, 1.0, 0.0, 0.3),
    "pave_blue":    ("#6CCBF5", 0.25, 0.0, 1.0, 0.0, 0.4),
    "boardwalk":    ("#F3DBA0", 0.45, 0.0, 1.0, 0.0, 0.0),
    "tile_aqua":    ("#35D6E8", 0.08, 0.0, 1.0, 0.0, 1.0),
    "lawn":         ("#55C81C", 0.9, 0.0, 1.0, 0.0, 0.0),
    "glass_blue":   ("#7FD0FF", 0.03, 0.0, 0.5, 0.0, 1.0),
    "glass_frost":  ("#DDF6FF", 0.25, 0.0, 0.72, 0.0, 1.0),
    "glass_pipe":   ("#7FE9FF", 0.03, 0.0, 0.34, 0.0, 1.0),
    "bubble":       ("#E4FAFF", 0.02, 0.0, 0.22, 0.0, 1.0),
    "orb":          ("#2FB8FF", 0.03, 0.2, 1.0, 0.15, 1.0),
    "chrome":       ("#E8EEF2", 0.12, 1.0, 1.0, 0.0, 0.0),
    "chrome_glow":  ("#9FF3FF", 0.15, 0.6, 1.0, 1.2, 0.0),
    "glow_cyan":    ("#35E6FF", 0.3, 0.0, 1.0, 4.0, 0.0),
    "glow_lime":    ("#A6FF3D", 0.3, 0.0, 1.0, 4.0, 0.0),
    "glow_magenta": ("#FF4DB2", 0.3, 0.0, 1.0, 4.0, 0.0),
    "aurora_cyan":  ("#4DF0FF", 0.5, 0.0, 0.10, 2.0, 0.0),
    "aurora_lime":  ("#9DFF6A", 0.5, 0.0, 0.09, 2.0, 0.0),
    "aurora_magenta": ("#FF7AD9", 0.5, 0.0, 0.08, 2.0, 0.0),
    "palm_trunk":   ("#B08A5E", 0.8, 0.0, 1.0, 0.0, 0.0),
    "palm_leaf":    ("#2FB52A", 0.45, 0.0, 1.0, 0.0, 0.3),
    "coconut":      ("#6B4A2A", 0.7, 0.0, 1.0, 0.0, 0.0),
    "bush":         ("#3FBF2E", 0.7, 0.0, 1.0, 0.0, 0.0),
    "rock":         ("#B7B2A8", 0.85, 0.0, 1.0, 0.0, 0.0),
    "wood":         ("#C99A63", 0.7, 0.0, 1.0, 0.0, 0.0),
    "rope":         ("#E6D3A8", 0.9, 0.0, 1.0, 0.0, 0.0),
    "sail":         ("#FFFFFF", 0.6, 0.0, 1.0, 0.0, 0.0),
    "solar":        ("#123A8C", 0.08, 0.5, 1.0, 0.0, 1.0),
    "globe":        ("#FFFFFF", 0.12, 0.0, 1.0, 0.0, 1.0),
    "fish_orange":  ("#FF7A1A", 0.3, 0.0, 1.0, 0.0, 0.5),
    "fish_blue":    ("#2D6BFF", 0.3, 0.0, 1.0, 0.0, 0.5),
    "fish_yellow":  ("#FFE02E", 0.3, 0.0, 1.0, 0.0, 0.5),
    "fish_white":   ("#FFFFFF", 0.3, 0.0, 1.0, 0.0, 0.5),
    "dolphin":      ("#7FA6C9", 0.25, 0.0, 1.0, 0.0, 0.8),
    # retro-desktop set and textured surfaces (see TEXTURE_FILES)
    "ink":          ("#101418", 0.4, 0.0, 1.0, 0.0, 0.3),
    "win_grey":     ("#C3C7CB", 0.45, 0.0, 1.0, 0.0, 0.2),
    "ui_paint":     ("#FFFFFF", 0.18, 0.0, 1.0, 0.0, 0.8),
    "ui_pool":      ("#FFFFFF", 0.18, 0.0, 1.0, 0.0, 0.8),
    "ui_error":     ("#FFFFFF", 0.22, 0.0, 1.0, 0.0, 0.6),
    "ui_taskbar":   ("#FFFFFF", 0.25, 0.0, 1.0, 0.0, 0.6),
    "ui_progress":  ("#FFFFFF", 0.2, 0.0, 1.0, 0.0, 0.8),
    "ui_player":    ("#FFFFFF", 0.12, 0.0, 1.0, 0.0, 1.0),
    "ui_wallpaper": ("#FFFFFF", 0.18, 0.0, 1.0, 0.0, 0.8),
    "ui_cd":        ("#FFFFFF", 0.06, 0.6, 1.0, 0.0, 1.0),
    "pool_floor":   ("#FFFFFF", 0.15, 0.0, 1.0, 0.0, 1.0),
    "fish_clown":   ("#FFFFFF", 0.3, 0.0, 1.0, 0.0, 0.6),
    "fish_gold":    ("#FFFFFF", 0.3, 0.0, 1.0, 0.0, 0.6),
    "fin_orange":   ("#FF7A10", 0.4, 0.0, 0.85, 0.0, 0.3),
    "anemone":      ("#FF8FC8", 0.5, 0.0, 1.0, 0.3, 0.3),
    "coral":        ("#FF6F61", 0.7, 0.0, 1.0, 0.0, 0.0),
    "duck":         ("#FFD21A", 0.2, 0.0, 1.0, 0.0, 1.0),
    "duck_beak":    ("#FF8A00", 0.3, 0.0, 1.0, 0.0, 0.6),
    "sand":         ("#F4E2B0", 0.9, 0.0, 1.0, 0.0, 0.0),
    "rainbow_r":    ("#FF4D4D", 0.2, 0.0, 0.8, 0.6, 0.5),
    "rainbow_y":    ("#FFE14D", 0.2, 0.0, 0.8, 0.6, 0.5),
    "rainbow_g":    ("#6BEA4B", 0.2, 0.0, 0.8, 0.6, 0.5),
    "rainbow_b":    ("#3FC8FF", 0.2, 0.0, 0.8, 0.6, 0.5),
    "rainbow_v":    ("#9C6BFF", 0.2, 0.0, 0.8, 0.6, 0.5),
}
# material -> image file in frutiger/textures
TEXTURE_FILES = {"boardwalk": "planks", "wood": "planks", "pave_white": "tiles", "ui_paint": "win_paint",
                 "ui_pool": "win_pool", "ui_error": "win_error", "ui_taskbar": "taskbar", "ui_progress": "progress",
                 "ui_player": "player", "ui_wallpaper": "wallpaper", "ui_cd": "cd", "pool_floor": "caustics",
                 "fish_clown": "clownfish", "fish_gold": "goldfish"}
DOUBLE_SIDED = {"palm_leaf", "sail", "water_fall", "aurora_cyan", "aurora_lime", "aurora_magenta", "fin_orange", "rainbow_r", "rainbow_y", "rainbow_g", "rainbow_b", "rainbow_v",
                "glass_blue", "glass_frost", "glass_pipe", "tank_water", "bubble", "solar", "fish_white", "dolphin"}


def rgb(h):
    c = np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0
    return tuple(np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)) + (1.0,)   # sRGB -> linear


def make_image(name, arr, outdir):
    """arr is (w, h, 3) indexed [x, y], values 0..1 sRGB."""
    w, h = arr.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=False)
    px = np.ones((h, w, 4), np.float32)
    lin = arr.transpose(1, 0, 2)
    px[..., :3] = np.where(lin <= 0.04045, lin / 12.92, ((lin + 0.055) / 1.055) ** 2.4)
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = os.path.join(outdir, name + ".png")
    img.file_format = "PNG"
    img.save()
    img.pack()
    return img


def make_materials(textures):
    out = {}
    for name, (col, rough, metal, alpha, emit, coat) in MATERIALS.items():
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = rgb(col)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        b.inputs["Alpha"].default_value = alpha
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.04
        if emit:
            b.inputs["Emission Color"].default_value = rgb(col)
            b.inputs["Emission Strength"].default_value = emit
        if name in textures:
            t = m.node_tree.nodes.new("ShaderNodeTexImage")
            t.image = textures[name]
            m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
        if alpha < 1:
            if hasattr(m, "surface_render_method"):
                m.surface_render_method = "BLENDED"
            if hasattr(m, "blend_method"):
                m.blend_method = "BLEND"
        m.use_backface_culling = name not in DOUBLE_SIDED
        m.diffuse_color = rgb(col)[:3] + (alpha,)
        out[name] = m
    return out


COLLECTIONS = {"SK": "Skate surfaces", "GR": "Grind rails and coping", "SC": "Solid scenery", "NC": "Decoration (no collision)",
               "OP": "Optional (delete if it looks wrong in game)"}


def build_scene(S, texture_arrays, outdir, title="FrutigerAir"):
    """texture_arrays maps material name -> (w, h, 3) sRGB array."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = title
    scene.unit_settings.system = "METRIC"
    images = {k: make_image(k, v, outdir) for k, v in texture_arrays.items()}
    tex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")
    for mat, fname in TEXTURE_FILES.items():
        img = bpy.data.images.load(os.path.join(tex_dir, fname + ".png"), check_existing=True)
        img.pack()
        images[mat] = img
    mats = make_materials(images)
    cols = {}
    for k, label in COLLECTIONS.items():
        c = bpy.data.collections.new(label)
        scene.collection.children.link(c)
        cols[k] = c
    by_obj = {}
    for (name, mat), d in S.parts.items():
        by_obj.setdefault(name, []).append((mat, d))
    for name in sorted(by_obj):
        V, F, UV, MI, slots = [], [], [], [], []
        off = 0
        for mat, d in by_obj[name]:
            v = np.vstack(d["V"])
            V.append(v)
            UV.append(np.vstack(d["UV"]))
            F.extend(tuple(i + off for i in f) for f in d["F"])
            MI.extend([len(slots)] * len(d["F"]))
            slots.append(mat)
            off += len(v)
        V, UV = np.vstack(V), np.vstack(UV)
        me = bpy.data.meshes.new(name)
        me.from_pydata(V.tolist(), [], F)
        for s in slots:
            me.materials.append(mats[s])
        me.polygons.foreach_set("material_index", MI)
        me.polygons.foreach_set("use_smooth", [True] * len(F))
        li = np.zeros(len(me.loops), np.int32)
        me.loops.foreach_get("vertex_index", li)
        uvl = me.uv_layers.new(name="UVMap")
        uvl.data.foreach_set("uv", UV[li].astype(np.float32).ravel())
        me.update()
        if name[:2] in ("SK", "GR", "SC") and name != "SC_terrain":
            # weld coincident vertices so ride surfaces are continuous, with no cracks to catch a wheel
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
            bm.to_mesh(me)
            bm.free()
            me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        if hasattr(me, "set_sharp_from_angle"):
            me.set_sharp_from_angle(angle=radians(38))
        ob = bpy.data.objects.new(name, me)
        cols.get(name[:2], cols["SC"]).objects.link(ob)
    # spawn points
    for name, pos, yaw in S.empties:
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = "ARROWS"
        e.empty_display_size = 2.0
        e.location = pos
        e.rotation_euler = (0, 0, yaw)
        scene.collection.objects.link(e)
    # grind lines as curves, for reference when tagging grinds
    gc = bpy.data.collections.new("Grind lines (reference curves)")
    scene.collection.children.link(gc)
    for i, pts in enumerate(S.grinds):
        cu = bpy.data.curves.new("GRIND_%03d" % i, "CURVE")
        cu.dimensions = "3D"
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        sp.points.foreach_set("co", np.c_[pts, np.ones(len(pts))].ravel())
        gc.objects.link(bpy.data.objects.new("GRIND_%03d" % i, cu))
    return scene


def export_glb(path, prefixes=None, names=None, jpeg=True):
    bpy.ops.object.select_all(action="DESELECT")
    n = 0
    for ob in bpy.context.scene.objects:
        if ob.type != "MESH":
            continue
        if (names and ob.name in names) or (prefixes and ob.name[:2] in prefixes) or (not names and not prefixes):
            ob.select_set(True)
            n += 1
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_yup=True,
                              export_apply=False, export_image_format="JPEG" if jpeg else "AUTO",
                              export_jpeg_quality=88, export_cameras=False, export_lights=False,
                              export_animations=False)
    return n


def save_blend(path):
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(path), compress=True)
