#!/usr/bin/env python3
"""Validate the official f68r source binding, not the visual interpretation."""

from __future__ import annotations

import hashlib
import json
import urllib.request


MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
CANVAS_ID = "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006196"
IMAGE_URL = "https://collections.library.yale.edu/iiif/2/1006196/full/full/0/default.jpg"
IMAGE_SHA256 = "4b0f31d1e08b8f026886aa599232b7dfcd33417b1eef43a44e619c3ebd21faa5"
WIDTH = 7993
HEIGHT = 3828


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


manifest = json.loads(fetch(MANIFEST_URL))
canvases = [item for item in manifest["items"] if item.get("id") == CANVAS_ID]
assert len(canvases) == 1
canvas = canvases[0]
assert canvas["label"] == {"none": ["68r"]}
assert canvas["width"] == WIDTH
assert canvas["height"] == HEIGHT
body = canvas["items"][0]["items"][0]["body"]
assert body["id"] == IMAGE_URL
assert body["width"] == WIDTH
assert body["height"] == HEIGHT
image = fetch(IMAGE_URL)
assert hashlib.sha256(image).hexdigest() == IMAGE_SHA256
print(
    json.dumps(
        {
            "canvas_label": "68r",
            "height": HEIGHT,
            "image_sha256": IMAGE_SHA256,
            "source_binding": "PASS",
            "visual_interpretation_independently_validated": False,
            "width": WIDTH,
        },
        sort_keys=True,
    )
)
