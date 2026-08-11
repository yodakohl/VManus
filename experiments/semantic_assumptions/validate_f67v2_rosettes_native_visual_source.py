#!/usr/bin/env python3
"""Validate official Yale image bindings, not native visual interpretation."""

from __future__ import annotations

import hashlib
import json
import urllib.request


MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
CANVASES = (
    {
        "id": "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006195",
        "label": "67v",
        "width": 5059,
        "height": 3753,
        "image": "https://collections.library.yale.edu/iiif/2/1006195/full/full/0/default.jpg",
        "sha256": "4799e8ebd8d968ea28dae919cfb86065566662b4e77c8b429d12e3e6e685638b",
    },
    {
        "id": "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006231",
        "label": "85v and 86r (foldout)",
        "width": 7925,
        "height": 7268,
        "image": "https://collections.library.yale.edu/iiif/2/1006231/full/full/0/default.jpg",
        "sha256": "4b08afeee514691b0a511099ca299aed544d6fd1782b7dee8df163dfc06354ed",
    },
)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()


manifest = json.loads(fetch(MANIFEST_URL))
source_hashes = []
for expected in CANVASES:
    matched = [item for item in manifest["items"] if item.get("id") == expected["id"]]
    assert len(matched) == 1
    canvas = matched[0]
    assert canvas["label"] == {"none": [expected["label"]]}
    assert canvas["width"] == expected["width"]
    assert canvas["height"] == expected["height"]
    body = canvas["items"][0]["items"][0]["body"]
    assert body["id"] == expected["image"]
    assert body["width"] == expected["width"]
    assert body["height"] == expected["height"]
    image = fetch(expected["image"])
    assert image.startswith(b"\xff\xd8") and image.endswith(b"\xff\xd9")
    digest = hashlib.sha256(image).hexdigest()
    assert digest == expected["sha256"]
    source_hashes.append(digest)

print(
    json.dumps(
        {
            "canvas_labels": [item["label"] for item in CANVASES],
            "image_sha256s": source_hashes,
            "source_binding": "PASS",
            "visual_interpretation_independently_validated": False,
        },
        sort_keys=True,
    )
)
