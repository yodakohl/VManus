#!/usr/bin/env python3
"""Validate official f17r/f116v source bindings, not visual interpretation."""

from __future__ import annotations

import hashlib
import json
import urllib.request


MANIFEST = "https://collections.library.yale.edu/manifests/2002046"
EXPECTED = {
    "17r": {
        "canvas": "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006106",
        "image": "https://collections.library.yale.edu/iiif/2/1006106/full/full/0/default.jpg",
        "width": 2649,
        "height": 3743,
        "sha256": "9ed091881b24f31504a5daa064c131f06b0bce10e8346f3dbe20de6cdaf2452f",
    },
    "116v": {
        "canvas": "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006277",
        "image": "https://collections.library.yale.edu/iiif/2/1006277/full/full/0/default.jpg",
        "width": 2686,
        "height": 3697,
        "sha256": "0f2e8691a66f255159b28f3fc2984633016f96c30c6d4d89cff6396708e5bb17",
    },
}


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


manifest = json.loads(fetch(MANIFEST))
digests = {}
for label, expected in EXPECTED.items():
    matching = [item for item in manifest["items"] if item.get("id") == expected["canvas"]]
    assert len(matching) == 1
    canvas = matching[0]
    assert canvas["label"] == {"none": [label]}
    assert canvas["width"] == expected["width"] and canvas["height"] == expected["height"]
    body = canvas["items"][0]["items"][0]["body"]
    assert body["id"] == expected["image"]
    assert body["width"] == expected["width"] and body["height"] == expected["height"]
    digest = hashlib.sha256(fetch(expected["image"])).hexdigest()
    assert digest == expected["sha256"]
    digests[label] = digest

print(json.dumps({
    "source_binding": "PASS",
    "image_sha256s": digests,
    "visual_interpretation_independently_validated": False,
}, sort_keys=True))
