#!/usr/bin/env python3
"""Validate the official f66r image binding, not visual interpretation."""

from __future__ import annotations

import hashlib
import json
import urllib.request


MANIFEST = "https://collections.library.yale.edu/manifests/2002046"
CANVAS = "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006192"
IMAGE = "https://collections.library.yale.edu/iiif/2/1006192/full/full/0/default.jpg"
IMAGE_SHA256 = "47d6a239bb7dbdc8d5e1a2238f2e10cf533d8abb409338017761bd3aed0a7554"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


manifest = json.loads(fetch(MANIFEST))
matching = [item for item in manifest["items"] if item.get("id") == CANVAS]
assert len(matching) == 1
canvas = matching[0]
assert canvas["label"] == {"none": ["66r"]}
assert canvas["width"] == 2793 and canvas["height"] == 3707
body = canvas["items"][0]["items"][0]["body"]
assert body["id"] == IMAGE
assert body["width"] == 2793 and body["height"] == 3707
assert hashlib.sha256(fetch(IMAGE)).hexdigest() == IMAGE_SHA256

print(json.dumps({
    "source_binding": "PASS",
    "target_canvas_label": "66r",
    "target_dimensions": [2793, 3707],
    "target_image_sha256": IMAGE_SHA256,
    "visual_interpretation_independently_validated": False,
}, sort_keys=True))
