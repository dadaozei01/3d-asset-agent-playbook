import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "blender", "scripts"))
import texture_ops as T  # noqa: E402
import dust_from_position as D  # noqa: E402


def noise_image(h=128, w=128, seed=0):
    rng = np.random.default_rng(seed)
    a = np.ones((h, w, 4), np.float32)
    # a non-tiling gradient plus noise: left/right and top/bottom edges differ
    yy, xx = np.mgrid[0:h, 0:w]
    a[..., 0] = xx / w
    a[..., 1] = yy / h
    a[..., 2] = rng.random((h, w)) * 0.1
    return a


def wrap_jump(a, axis):
    first = np.take(a, 0, axis=axis)
    last = np.take(a, -1, axis=axis)
    return float(np.abs(first - last)[..., :3].mean())


class SeamlessTest(unittest.TestCase):
    def test_both_axes_tile(self):
        a = noise_image()
        self.assertGreater(wrap_jump(a, 1), 0.25)
        b = T.seamless(a)
        self.assertLess(wrap_jump(b, 1), 0.05)
        self.assertLess(wrap_jump(b, 0), 0.05)

    def test_single_axis_leaves_other_alone(self):
        a = noise_image()
        b = T.seamless_axis(a, 1)
        self.assertLess(wrap_jump(b, 1), 0.05)
        self.assertGreater(wrap_jump(b, 0), 0.25)


class PaintOutTest(unittest.TestCase):
    def test_dark_spot_removed_within_band(self):
        a = np.full((200, 400, 4), 0.6, np.float32)
        a[95:105, 95:105, :3] = 0.05
        spots = T.find_dark_blobs(a, 1, radius=4, min_dist=50)
        (y, x, _), = spots
        self.assertTrue(90 <= y <= 110 and 90 <= x <= 110)
        b = T.paint_out(a, [(y, x)], band_edges=[0, 200], radius=40, offset=150)
        self.assertGreater(b[95:105, 95:105, :3].min(), 0.55)

    def test_source_window_outside_image_is_rejected(self):
        a = np.zeros((50, 100, 4), np.float32)
        with self.assertRaises(ValueError):
            T.paint_out(a, [(25, 50)], radius=40, offset=60)


class FlattenDarksTest(unittest.TestCase):
    def test_darks_lifted_lights_kept(self):
        a = np.full((10, 10, 4), 0.6, np.float32)
        a[0, :, :3] = 0.1
        a[1, :, :3] = 0.95
        b = T.flatten_darks(a, percentile=50, keep=0.15)
        self.assertGreater(b[0, 0, 0], 0.5)
        self.assertAlmostEqual(float(b[1, 0, 0]), 0.95, places=4)


class DustTest(unittest.TestCase):
    def test_ring_falloff_and_plane_filter(self):
        pos = np.array([[0, 0, 0], [0.5, 0, 0], [2, 0, 0], [0, 0.3, 0]], np.float32)
        alpha = D.dust_alpha(pos, [(0, 0, 0)], [1.0])
        self.assertAlmostEqual(float(alpha[0]), 0.48, places=5)  # centre: full strength
        self.assertTrue(0 < alpha[1] < alpha[0])                 # partway out
        self.assertEqual(float(alpha[2]), 0.0)                   # beyond radius
        self.assertEqual(float(alpha[3]), 0.0)                   # different surface plane

    def test_apply_darkens(self):
        bc = np.ones((1, 4), np.float32)
        ao = np.ones((1, 4), np.float32)
        D.apply_dust(bc, ao, np.array([0.5], np.float32))
        self.assertLess(bc[0, 0], 1.0)
        self.assertAlmostEqual(float(ao[0, 0]), 0.75, places=5)


if __name__ == "__main__":
    unittest.main()
