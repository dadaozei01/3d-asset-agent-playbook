"""Texture clean-up helpers for AI-generated or scanned textures.

The array functions only need numpy (images as float32 arrays shaped (h, w, 4),
row 0 at the bottom as Blender stores them), so they port to any DCC.
The load/save helpers at the end use bpy.
"""
import numpy as np


def _smoothstep(x):
    return x * x * (3 - 2 * x)


def seamless_axis(a, axis, edge=0.18):
    """Make `a` tile along one axis: blend with a half-shifted copy near the borders."""
    n = a.shape[axis]
    x = (np.arange(n) + 0.5) / n
    wt = _smoothstep(np.clip(np.minimum(x, 1 - x) / edge, 0, 1)).astype(np.float32)
    shape = [1, 1, 1]
    shape[axis] = n
    wt = wt.reshape(shape)
    return (a * wt + np.roll(a, n // 2, axis=axis) * (1 - wt)).astype(np.float32)


def seamless(a, axes=(1, 0), edge=0.18):
    """Tile in both directions. Axes are blended one after another; blending them
    together leaves a faint cross seam at the tile centre."""
    for ax in axes:
        a = seamless_axis(a, ax, edge)
    return a


def find_dark_blobs(a, count, radius=25, min_dist=220, exclude_rows=()):
    """Locate the darkest blob centres (e.g. wood knots). Returns [(row, col, value)].
    `exclude_rows` are (row, half_width) bands to skip, such as plank seams."""
    lum = a[..., :3] @ np.array([.3, .59, .11], np.float32)
    k = radius
    c = np.cumsum(np.pad(lum, ((k, k), (k, k)), mode="wrap"), 0)
    c = c[2 * k:] - c[:-2 * k]
    c = np.cumsum(c, 1)
    c = (c[:, 2 * k:] - c[:, :-2 * k]) / (2 * k) ** 2
    for row, half in exclude_rows:
        c[max(0, row - half):row + half, :] = np.inf
    h, w = c.shape
    found = []
    for idx in np.argsort(c, axis=None):
        y, x = divmod(int(idx), w)
        if not np.isfinite(c[y, x]):
            break
        if all((y - fy) ** 2 + (x - fx) ** 2 > min_dist ** 2 for fy, fx, _ in found):
            found.append((y, x, float(c[y, x])))
            if len(found) == count:
                break
    return found


def paint_out(a, spots, band_edges=None, radius=430, offset=760, feather=0.45):
    """Cover each (row, col) spot with texture from `offset` px further along the same row band.

    Use this on the *original* (not yet seamless) image and pick the offset sign so the
    source window stays inside the image; crossing the image border copies a seam in.
    `band_edges` (sorted row indices incl. 0 and h) keeps the patch inside one plank/strip.
    """
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    for ky, kx in spots:
        off = offset if kx < w / 2 else -offset
        if not (0 <= kx + off - radius and kx + off + radius < w):
            raise ValueError(f"source window for spot {(ky, kx)} leaves the image; reduce radius/offset")
        fx = _smoothstep(np.clip((1.0 - np.abs(xx - kx) / radius) / feather, 0, 1))
        if band_edges is not None:
            lo = max(s for s in band_edges if s <= ky)
            hi = min(s for s in band_edges if s > ky)
            fy = ((yy >= lo + 5) & (yy < hi - 5)).astype(np.float32)
        else:
            fy = _smoothstep(np.clip((1.0 - np.abs(yy - ky) / radius) / feather, 0, 1))
        m = (fx * fy)[..., None].astype(np.float32)
        a = a * (1 - m) + np.roll(a, -off, axis=1) * m
    return a.astype(np.float32)


def flatten_darks(a, percentile=60, keep=0.15):
    """Squash everything darker than the given luminance percentile towards it.
    Removes large dark grime strokes while keeping light scratches and highlights."""
    rgb = a[..., :3]
    lum = rgb @ np.array([.3, .59, .11], np.float32)
    m = np.percentile(lum, percentile)
    new = np.where(lum < m, m - (m - lum) * keep, lum)
    out = a.copy()
    out[..., :3] = rgb * (new / np.maximum(lum, 1e-4))[..., None]
    return out.astype(np.float32)


def tile_preview(a, reps=(2, 2), step=4):
    """Downsampled repeat for eyeballing seams."""
    return np.ascontiguousarray(np.tile(a[::step, ::step], (reps[0], reps[1], 1)), dtype=np.float32)


# ---- Blender I/O -----------------------------------------------------------

def load_pixels(path):
    import bpy
    im = bpy.data.images.load(path, check_existing=False)
    w, h = im.size
    a = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    return a.reshape(h, w, 4)


def save_pixels(a, path, name="tmp_save", colorspace="sRGB"):
    import bpy
    h, w, _ = a.shape
    im = bpy.data.images.new(name, w, h)
    im.colorspace_settings.name = colorspace
    im.pixels.foreach_set(np.ascontiguousarray(a, dtype=np.float32).ravel())
    im.filepath_raw = path
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)
