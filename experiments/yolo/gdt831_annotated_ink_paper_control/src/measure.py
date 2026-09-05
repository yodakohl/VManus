"""Fixed local contrast support classifier; this is not ink photometry."""
import numpy as np
from PIL import Image, ImageFilter

HALO = 16


def score_rgb(rgb):
    native = np.asarray(rgb, dtype=np.uint8)
    gray = np.rint(native.astype(np.float32).mean(axis=2)).astype(np.uint8)
    smooth = Image.fromarray(gray).filter(ImageFilter.MedianFilter(3))
    background = smooth.filter(ImageFilter.MedianFilter(31))
    s = np.asarray(smooth, dtype=np.float32)
    b = np.asarray(background, dtype=np.float32)
    return (b - s) / np.maximum(b, 1.0)


def tile_scores(image, tile):
    x, y, w, h = (tile[k] for k in ('x0', 'y0', 'width', 'height'))
    assert x >= HALO and y >= HALO
    assert x + w + HALO <= image.width and y + h + HALO <= image.height
    rgb = image.crop((x-HALO, y-HALO, x+w+HALO, y+h+HALO)).convert('RGB')
    return score_rgb(rgb)[HALO:-HALO, HALO:-HALO]
