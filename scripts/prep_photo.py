#!/usr/bin/env python3
"""Prep a photo for ASCII conversion.

Pipeline:
  1. Remove the background with rembg so the subject is isolated.
  2. Boost local contrast with OpenCV CLAHE (flat faces/objects gain
     real highlights and shadows).
  3. Composite onto pure white so the background maps to the blank end
     of the ASCII ramp (white -> spaces).

Output: grayscale source-prepped.png. Run once per photo:
    python scripts/prep_photo.py source-photo.jpg

The heavy libraries (rembg, opencv) are only needed here, locally, when
you change your photo. Each step degrades gracefully if a library is
missing so you still get a usable result.
"""
import sys

import numpy as np
from PIL import Image

OUT = "source-prepped.png"


def remove_background(img: Image.Image) -> Image.Image:
    try:
        from rembg import remove
    except Exception as exc:  # noqa: BLE001
        print(f"[prep] rembg unavailable ({exc}); keeping original background")
        return img.convert("RGBA")
    print("[prep] removing background with rembg ...")
    return remove(img).convert("RGBA")


def composite_on_white(img: Image.Image) -> Image.Image:
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    return Image.alpha_composite(white, img).convert("L")


def boost_contrast(arr: np.ndarray) -> np.ndarray:
    try:
        import cv2
    except Exception as exc:  # noqa: BLE001
        print(f"[prep] opencv unavailable ({exc}); skipping CLAHE")
        return arr
    print("[prep] boosting local contrast with CLAHE ...")
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    return clahe.apply(arr)


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    print(f"[prep] loading {src}")
    img = Image.open(src).convert("RGBA")

    img = remove_background(img)
    gray = composite_on_white(img)
    arr = boost_contrast(np.array(gray))

    Image.fromarray(arr).save(OUT)
    print(f"[prep] wrote {OUT} ({arr.shape[1]}x{arr.shape[0]})")


if __name__ == "__main__":
    main()
