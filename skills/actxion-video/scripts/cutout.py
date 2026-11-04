#!/usr/bin/env python3
"""Pass 02 (cut-out): photo -> soft-edged PNG of the main person only, for "text behind the player".

    python3 cutout.py photo.jpg out.png [--keep 1] [--at 0.3,0.4]

- rembg (isnet-general-use) makes the matte.
- Only the largest connected subject is kept (--keep N keeps the N largest), so watermarks,
  broadcaster logos and team-mates in the background are dropped. When the person you want
  is not the biggest shape, pass --at x,y (0-1 fractions of the photo, roughly their chest):
  the subject nearest that point is kept. ALWAYS look at the result before using it.
- Holes inside the body are filled, the edge gets a light blur (soft edge, no outline, no glow).
- The result is trimmed to the subject with a small margin.
Prints {"path", "box": [x0, y0, x1, y1], "face_y": <0-1 guess of where the head is>}.
Needs: pip install "rembg[cpu]" pillow numpy scipy
"""
import json
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


def main():
    args = sys.argv[1:]
    keep = 1
    at = None
    if "--at" in args:
        i = args.index("--at")
        at = [float(v) for v in args[i + 1].split(",")]
        del args[i:i + 2]
    if "--keep" in args:
        i = args.index("--keep")
        keep = int(args[i + 1])
        del args[i:i + 2]
    src, out = args[0], args[1]
    from rembg import new_session, remove

    im = Image.open(src).convert("RGB")
    # matte at up to 2x for hair detail on small photos
    scale = 2 if max(im.size) < 1000 else 1
    work = im.resize((im.width * scale, im.height * scale), Image.LANCZOS) if scale > 1 else im
    rgba = remove(work, session=new_session("isnet-general-use"), post_process_mask=True)
    a = np.array(rgba.split()[-1]).astype(np.float32) / 255.0

    solid = a > 0.5
    lab, n = ndimage.label(solid)
    if n == 0:
        print(json.dumps({"path": None, "error": "no subject"}))
        sys.exit(1)
    sizes = ndimage.sum(solid, lab, range(1, n + 1))
    order = np.argsort(sizes)[::-1][:keep]
    if at:
        # nearest component (by distance transform) to the hint point, among shapes >= 3% of the biggest
        px, py = int(at[0] * a.shape[1]), int(at[1] * a.shape[0])
        best, bestd = None, 1e18
        for k in range(n):
            if sizes[k] < 0.03 * sizes.max():
                continue
            yy, xx = np.where(lab == k + 1)
            d = ((xx - px) ** 2 + (yy - py) ** 2).min()
            if d < bestd:
                best, bestd = k, d
        order = np.array([best])
    mask = np.isin(lab, order + 1)
    mask = ndimage.binary_fill_holes(mask)
    # keep the soft matte values only near the kept subject
    near = ndimage.binary_dilation(mask, iterations=6)
    alpha = np.where(near, np.maximum(a, mask * 1.0), 0.0)
    alpha[mask] = np.maximum(alpha[mask], 0.98)
    am = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2 * scale))
    rgba.putalpha(am)

    ys, xs = np.where(mask)
    pad = 12 * scale
    box = [max(0, xs.min() - pad), max(0, ys.min() - pad), min(rgba.width, xs.max() + pad), min(rgba.height, ys.max() + pad)]
    cut = rgba.crop(box)
    if scale > 1:
        cut = cut.resize((cut.width // scale, cut.height // scale), Image.LANCZOS)
    cut.save(out)
    # the head is the top ~18% of the subject
    print(json.dumps({"path": out, "size": cut.size, "box": [int(b) // scale for b in box],
                      "face_y": round(0.12, 2)}))


if __name__ == "__main__":
    main()
