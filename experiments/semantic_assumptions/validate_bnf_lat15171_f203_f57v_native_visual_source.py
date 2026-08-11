#!/usr/bin/env python3
"""Validate official catalogue and image bindings, not visual interpretation."""

from __future__ import annotations

import hashlib
import json
import urllib.request


BIBLISSIMA_ICON = "https://portail.biblissima.fr/en/ark:/43093/ifdatac1a34e54c5d7ff4ba6931e88aa1cc7ceda4d7b29"
BIBLISSIMA_MS = "https://portail.biblissima.fr/en/ark:/43093/mdatab7e7701bf453c5fbfeb076cf47b62de5e715eaf4"
GALLICA_MANIFEST = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066788k/manifest.json"
GALLICA_SERVICE = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066788k/f206"
GALLICA_IMAGE = GALLICA_SERVICE + "/full/full/0/native.jpg"
GALLICA_MANIFEST_SHA = "6a22354bc70e7a59c36238a43cc37ca782b51ac1b6fa7890412e503e1a00b6ae"
GALLICA_IMAGE_SHA = "85119aa99ce333590aed4a1fddc057e188a97d55af3be7763a4b71c3aae26910"
YALE_MANIFEST = "https://collections.library.yale.edu/manifests/2002046"
YALE_CANVAS = "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006187"
YALE_IMAGE = "https://collections.library.yale.edu/iiif/2/1006187/full/full/0/default.jpg"
YALE_SHA = "2bf46dbeaaaab4a97075f46f503582da0eef2b352eb92277d7a3b6db1a3a0b8c"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


icon = fetch(BIBLISSIMA_ICON).decode("utf-8")
assert "Saisons et humeurs" in icon
assert "Latin 15171 f.203" in icon

manuscript = fetch(BIBLISSIMA_MS).decode("utf-8")
assert GALLICA_MANIFEST in manuscript
assert "Latin 15171" in manuscript

manifest_bytes = fetch(GALLICA_MANIFEST)
assert hashlib.sha256(manifest_bytes).hexdigest() == GALLICA_MANIFEST_SHA
manifest = json.loads(manifest_bytes)
canvases = manifest["sequences"][0]["canvases"]
matching = []
for canvas in canvases:
    body = canvas["images"][0]["resource"]
    service = body["service"]["@id"]
    if service == GALLICA_SERVICE:
        matching.append((canvas, body))
assert len(matching) == 1
canvas, body = matching[0]
assert canvas["width"] == 6175 and canvas["height"] == 4337
assert body["width"] == 6175 and body["height"] == 4337
assert hashlib.sha256(fetch(GALLICA_IMAGE)).hexdigest() == GALLICA_IMAGE_SHA

yale = json.loads(fetch(YALE_MANIFEST))
target = [item for item in yale["items"] if item.get("id") == YALE_CANVAS]
assert len(target) == 1
target_canvas = target[0]
assert target_canvas["label"] == {"none": ["57v"]}
assert target_canvas["width"] == 3028 and target_canvas["height"] == 3769
target_body = target_canvas["items"][0]["items"][0]["body"]
assert target_body["id"] == YALE_IMAGE
assert hashlib.sha256(fetch(YALE_IMAGE)).hexdigest() == YALE_SHA

print(json.dumps({
    "catalogue_binding": "PASS",
    "source_canvas_dimensions": [6175, 4337],
    "source_image_sha256": GALLICA_IMAGE_SHA,
    "target_canvas_label": "57v",
    "target_image_sha256": YALE_SHA,
    "visual_interpretation_independently_validated": False,
}, sort_keys=True))
