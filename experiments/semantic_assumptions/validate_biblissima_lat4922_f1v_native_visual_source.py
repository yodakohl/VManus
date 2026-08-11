#!/usr/bin/env python3
"""Validate the Gallica source binding, not the visual interpretation."""

from __future__ import annotations

import hashlib
import json
import urllib.request


MANIFEST_URL = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066969x/manifest.json"
CANVAS_ID = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066969x/canvas/f2"
IMAGE_URL = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066969x/f2/full/full/0/native.jpg"
IMAGE_SHA256 = "ffc92bbaccc70a75c46dfa6bfcd552d9569209423cf6bfda3a10cc46300ec81e"
WIDTH = 7423
HEIGHT = 5155


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


manifest = json.loads(fetch(MANIFEST_URL))
canvases = manifest["sequences"][0]["canvases"]
assert len(canvases) == 199
assert canvases[0]["@id"].endswith("/canvas/f1")
canvas = [item for item in canvases if item.get("@id") == CANVAS_ID]
assert len(canvas) == 1
canvas = canvas[0]
assert canvas["width"] == WIDTH
assert canvas["height"] == HEIGHT
body = canvas["images"][0]["resource"]
assert body["@id"] == IMAGE_URL
image = fetch(IMAGE_URL)
assert hashlib.sha256(image).hexdigest() == IMAGE_SHA256
print(
    json.dumps(
        {
            "canvas_count": 199,
            "candidate_canvas": "f2",
            "height": HEIGHT,
            "image_sha256": IMAGE_SHA256,
            "source_binding": "PASS",
            "visual_interpretation_independently_validated": False,
            "width": WIDTH,
        },
        sort_keys=True,
    )
)
