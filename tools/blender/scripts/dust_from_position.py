"""Bake dust rings around fasteners (rivets, bolts) into an already baked texture set.

Transparent decals sitting on a surface are not captured by a normal bake. Instead,
bake a world-space Position map with the same UVs (see bake_pbr.py), then darken every
texel by its distance to the nearest fastener lying in the same surface plane.
"""
import numpy as np


def dust_alpha(position, centres, radii, plane_axis=1, plane_tol=0.004,
               inner=0.3, outer=0.95, strength=0.48):
    """position: (n, 3) world positions per texel. centres: list of (x, y, z).
    radii: per-centre ring radius in metres. plane_axis: axis normal to the surface
    the fasteners sit on (1 = Y for a door facing -Y). Returns alpha per texel."""
    position = np.asarray(position, np.float32)
    alpha = np.zeros(len(position), np.float32)
    u_axis, v_axis = [a for a in range(3) if a != plane_axis]
    planes = {}
    for c, r in zip(centres, radii):
        planes.setdefault(round(c[plane_axis], 4), []).append((c, r))
    for depth, items in planes.items():
        idx = np.nonzero(np.abs(position[:, plane_axis] - depth) < plane_tol)[0]
        p = position[idx]
        for c, r in items:
            du = p[:, u_axis] - c[u_axis]
            dv = p[:, v_axis] - c[v_axis]
            near = (np.abs(du) < r) & (np.abs(dv) < r)
            if not near.any():
                continue
            t = np.sqrt(du[near] ** 2 + dv[near] ** 2) / r
            a = np.clip(strength * (outer - t) / (outer - inner), 0, strength)
            j = idx[near]
            alpha[j] = np.maximum(alpha[j], a)
    return alpha


def apply_dust(base_color, ao, alpha, tint=(0.38, 0.33, 0.28), ao_strength=0.5):
    """base_color, ao: (n, 4) float arrays, modified in place."""
    a = alpha[:, None]
    base_color[:, :3] *= (1 - a) + a * np.asarray(tint, np.float32)
    ao[:, :3] *= 1 - ao_strength * a


def apply_dust_blender(position_image, base_color_image, ao_image, fasteners, ring_scale=2.6, **kw):
    """fasteners: objects whose location is the fastener centre on the surface and whose
    scale.x is its radius."""
    def pixels(im):
        w, h = im.size
        arr = np.empty(w * h * 4, np.float32)
        im.pixels.foreach_get(arr)
        return arr.reshape(-1, 4)

    pos = pixels(position_image)[:, :3]
    bc, ao = pixels(base_color_image), pixels(ao_image)
    centres = [tuple(o.matrix_world.translation) for o in fasteners]
    radii = [o.scale.x * ring_scale for o in fasteners]
    apply_dust(bc, ao, dust_alpha(pos, centres, radii, **kw))
    base_color_image.pixels.foreach_set(bc.ravel())
    ao_image.pixels.foreach_set(ao.ravel())
