"""Bake a PBR set for objects that share one material, then pack ORM.

Assumptions (adjust per scene):
- The objects already have a non-overlapping UV layer to bake into (`uv_name`).
- Texture nodes in the material pin their own UV map by name, so changing the
  active UV for baking does not change what they sample.
- The material has a node named "PBR_Metal" whose first output is the metallic value
  (a Value node, or the Math node that drives Principled Metallic).
- Originals overlapping the bake copies are hidden from render, or AO is blocked.

4K bakes can outlast the MCP call ("No data received"); Blender keeps going.
Check the images afterwards instead of re-running.
"""
import bpy
import numpy as np


def setup_cycles(samples=16):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    try:
        sc.cycles.device = "GPU"
    except Exception:
        pass
    sc.cycles.samples = samples
    sc.render.bake.margin = 16
    sc.render.bake.use_selected_to_active = False
    sc.render.bake.target = "IMAGE_TEXTURES"


def bake_group(prefix, material, objs, res, uv_name):
    """Returns {pass_name: image}. Passes: BaseColor, Roughness, Normal, AO, Metallic, Position."""
    nt = material.node_tree
    N, L = nt.nodes, nt.links
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
    surface = out.inputs["Surface"].links[0].from_socket
    target = N.get("BAKE_TARGET") or N.new("ShaderNodeTexImage")
    target.name = "BAKE_TARGET"
    N.active = target

    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
        o.data.uv_layers.active = o.data.uv_layers[uv_name]
    bpy.context.view_layer.objects.active = objs[0]

    images = {}

    def new_image(name, color, float_buffer=False):
        full = f"{prefix}_{name}"
        old = bpy.data.images.get(full)
        if old:
            bpy.data.images.remove(old)
        im = bpy.data.images.new(full, res, res, alpha=False, float_buffer=float_buffer)
        im.colorspace_settings.name = "sRGB" if color else "Non-Color"
        target.image = im
        images[name] = im
        return im

    new_image("BaseColor", True)
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"})
    new_image("Roughness", False)
    bpy.ops.object.bake(type="ROUGHNESS")
    new_image("Normal", False, True)
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")
    new_image("AO", False)
    bpy.ops.object.bake(type="AO")

    emission = N.new("ShaderNodeEmission")
    L.new(emission.outputs[0], out.inputs["Surface"])
    L.new(N["PBR_Metal"].outputs[0], emission.inputs["Color"])
    new_image("Metallic", False)
    bpy.ops.object.bake(type="EMIT")
    geo = N.new("ShaderNodeNewGeometry")
    L.new(geo.outputs["Position"], emission.inputs["Color"])
    new_image("Position", False, True)
    bpy.ops.object.bake(type="EMIT")

    N.remove(geo)
    N.remove(emission)
    N.remove(target)
    L.new(surface, out.inputs["Surface"])
    return images


def _pixels(im):
    w, h = im.size
    a = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(a)
    return a.reshape(h, w, 4)


def save_pbr_set(images, folder, prefix):
    """Writes <prefix>_BaseColor.png, _Normal.png, _ORM.png (R=AO, G=Roughness, B=Metallic)."""
    bc = images["BaseColor"]
    bc.filepath_raw = f"{folder}/{prefix}_BaseColor.png"
    bc.file_format = "PNG"
    bc.save()

    def write(name, arr):
        h, w, _ = arr.shape
        im = bpy.data.images.new(f"{prefix}_{name}_out", w, h)
        im.colorspace_settings.name = "Non-Color"
        im.pixels.foreach_set(np.ascontiguousarray(arr, dtype=np.float32).ravel())
        im.filepath_raw = f"{folder}/{prefix}_{name}.png"
        im.file_format = "PNG"
        im.save()
        bpy.data.images.remove(im)

    write("Normal", _pixels(images["Normal"]))
    ao, rough, metal = (_pixels(images[k]) for k in ("AO", "Roughness", "Metallic"))
    orm = np.ones_like(ao)
    orm[..., 0], orm[..., 1], orm[..., 2] = ao[..., 0], rough[..., 0], metal[..., 0]
    write("ORM", orm)
