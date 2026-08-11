#!/usr/bin/env python3
"""Validate official source/target image bindings, not visual interpretation."""

from __future__ import annotations

import hashlib
import json
import urllib.request


SOURCE_IMAGES = (
    {
        "info": "https://iiif.irht.cnrs.fr/iiif/ark:/63955/valzmintsb2k/info.json",
        "id": "https://iiif.irht.cnrs.fr/iiif/VOLUME1/France/Paris/B751052116/DEPOT/IRHT_027615_2",
        "width": 2480,
        "height": 1760,
        "sha256": "dd26b017be608ce4118b89dba00656f05bb267db89a64fe10ccecc64e7ab2315",
    },
    {
        "info": "https://iiif.irht.cnrs.fr/iiif/ark:/63955/ve9vs2s5k6e7/info.json",
        "id": "https://iiif.irht.cnrs.fr/iiif/VOLUME1/France/Paris/B751052116/DEPOT/IRHT_027616_2",
        "width": 2656,
        "height": 1800,
        "sha256": "581b07157f8e03b49093cffdd3e98e59a967d517ee9a212d7104741c9b9f2f53",
    },
)
YALE_MANIFEST = "https://collections.library.yale.edu/manifests/2002046"
YALE_CANVAS = "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006195"
YALE_IMAGE = "https://collections.library.yale.edu/iiif/2/1006195/full/full/0/default.jpg"
YALE_WIDTH = 5059
YALE_HEIGHT = 3753
YALE_SHA256 = "4799e8ebd8d968ea28dae919cfb86065566662b4e77c8b429d12e3e6e685638b"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


source_hashes = []
for expected in SOURCE_IMAGES:
    info = json.loads(fetch(expected["info"]))
    assert info["@id"] == expected["id"]
    assert info["width"] == expected["width"]
    assert info["height"] == expected["height"]
    image_url = f'{expected["id"]}/full/full/0/native.jpg'
    image = fetch(image_url)
    digest = hashlib.sha256(image).hexdigest()
    assert digest == expected["sha256"]
    source_hashes.append(digest)

manifest = json.loads(fetch(YALE_MANIFEST))
canvases = [item for item in manifest["items"] if item.get("id") == YALE_CANVAS]
assert len(canvases) == 1
canvas = canvases[0]
assert canvas["label"] == {"none": ["67v"]}
assert canvas["width"] == YALE_WIDTH
assert canvas["height"] == YALE_HEIGHT
body = canvas["items"][0]["items"][0]["body"]
assert body["id"] == YALE_IMAGE
assert body["width"] == YALE_WIDTH
assert body["height"] == YALE_HEIGHT
yale_image = fetch(YALE_IMAGE)
assert hashlib.sha256(yale_image).hexdigest() == YALE_SHA256
print(
    json.dumps(
        {
            "source_binding": "PASS",
            "source_image_sha256s": source_hashes,
            "target_canvas_label": "67v",
            "target_image_sha256": YALE_SHA256,
            "visual_interpretation_independently_validated": False,
        },
        sort_keys=True,
    )
)
