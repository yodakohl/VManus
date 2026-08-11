#!/usr/bin/env python3
"""Validate only the official source binding for the f57v visual pilot."""

from __future__ import annotations

import hashlib
import json
import urllib.request


MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
CANVAS_ID = "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006187"
IMAGE_URL = "https://collections.library.yale.edu/iiif/2/1006187/full/full/0/default.jpg"
IMAGE_SHA256 = "2bf46dbeaaaab4a97075f46f503582da0eef2b352eb92277d7a3b6db1a3a0b8c"
WIDTH = 3028
HEIGHT = 3769
OPPOSITE_CANVAS_ID = "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006186"
OPPOSITE_IMAGE_URL = "https://collections.library.yale.edu/iiif/2/1006186/full/full/0/default.jpg"
OPPOSITE_IMAGE_SHA256 = "473727b2ea1dd000a4a15eaa57302a48c410d4f6e670abdd607cd7c7461ff98c"
OPPOSITE_WIDTH = 2823
OPPOSITE_HEIGHT = 3733


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


manifest = json.loads(fetch(MANIFEST_URL))
canvases = [item for item in manifest["items"] if item.get("id") == CANVAS_ID]
assert len(canvases) == 1
canvas = canvases[0]
assert canvas["width"] == WIDTH
assert canvas["height"] == HEIGHT
body = canvas["items"][0]["items"][0]["body"]
assert body["id"] == IMAGE_URL
assert body["width"] == WIDTH
assert body["height"] == HEIGHT
image = fetch(IMAGE_URL)
assert hashlib.sha256(image).hexdigest() == IMAGE_SHA256
opposite_canvases = [item for item in manifest["items"] if item.get("id") == OPPOSITE_CANVAS_ID]
assert len(opposite_canvases) == 1
opposite_canvas = opposite_canvases[0]
assert opposite_canvas["width"] == OPPOSITE_WIDTH
assert opposite_canvas["height"] == OPPOSITE_HEIGHT
opposite_body = opposite_canvas["items"][0]["items"][0]["body"]
assert opposite_body["id"] == OPPOSITE_IMAGE_URL
assert opposite_body["width"] == OPPOSITE_WIDTH
assert opposite_body["height"] == OPPOSITE_HEIGHT
opposite_image = fetch(OPPOSITE_IMAGE_URL)
assert hashlib.sha256(opposite_image).hexdigest() == OPPOSITE_IMAGE_SHA256
print(
    json.dumps(
        {
            "canvas_count": 2,
            "height": HEIGHT,
            "image_sha256": IMAGE_SHA256,
            "opposite_height": OPPOSITE_HEIGHT,
            "opposite_image_sha256": OPPOSITE_IMAGE_SHA256,
            "opposite_width": OPPOSITE_WIDTH,
            "source_binding": "PASS",
            "visual_interpretation_independently_validated": False,
            "width": WIDTH,
        },
        sort_keys=True,
    )
)
