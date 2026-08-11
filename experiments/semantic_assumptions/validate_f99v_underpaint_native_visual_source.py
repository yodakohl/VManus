#!/usr/bin/env python3
"""Validate f99v source bindings, not the native visual interpretation."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import urllib.request


BASE = Path(__file__).resolve().parent
ANNOTATIONS = BASE / "results" / "existing_human_exact_locus_annotations.tsv"
ANNOTATIONS_SHA256 = "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
CANVAS_ID = "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006247"
YALE_IMAGE_URL = "https://collections.library.yale.edu/iiif/2/1006247/full/full/0/default.jpg"
YALE_IMAGE_SHA256 = "111f6dfc34b8ecb9230cb5a0d144afef4cbd788048ddda2f440108941c91d5e5"
YALE_WIDTH = 2802
YALE_HEIGHT = 3697
VIEWER_URL = "https://www.jasondavies.com/voynich/"
VIEWER_SHA256 = "86fdbb7668148109226796d671e8054f75d238ec662f18bf095d8d4deefb8923"
TILE_URL = "https://voynich.jasondavies.com/f99v/5/11/14.jpg"
TILE_SHA256 = "d8b0f8a88560a384f89c62d008a71cf6b79a936d1e4b30df940b5fd512f0da3c"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


annotation_bytes = ANNOTATIONS.read_bytes()
assert sha256(annotation_bytes) == ANNOTATIONS_SHA256
rows = list(csv.DictReader(io.StringIO(annotation_bytes.decode("utf-8")), delimiter="\t"))
target = [row for row in rows if row["locus"] == "f99v.45"]
assert len(target) == 1
assert target[0]["old_locus"] == "f99v.L3.4a"
assert target[0]["certainty"] == "HEDGED"
assert target[0]["local_comment"] == (
    "Apparent letters on West tuber of plant <f99v>[3,4]. "
    "Tiny, but visible in BLI04 under the reddish paint. Is it real?"
)

manifest = json.loads(fetch(MANIFEST_URL))
canvases = [item for item in manifest["items"] if item.get("id") == CANVAS_ID]
assert len(canvases) == 1
canvas = canvases[0]
assert canvas["label"] == {"none": ["99v"]}
assert canvas["width"] == YALE_WIDTH and canvas["height"] == YALE_HEIGHT
body = canvas["items"][0]["items"][0]["body"]
assert body["id"] == YALE_IMAGE_URL
assert body["width"] == YALE_WIDTH and body["height"] == YALE_HEIGHT
assert sha256(fetch(YALE_IMAGE_URL)) == YALE_IMAGE_SHA256

viewer = fetch(VIEWER_URL)
assert sha256(viewer) == VIEWER_SHA256
assert b"All images courtesy of" in viewer
assert b"Beinecke Rare Book and Manuscript Library" in viewer
tile = fetch(TILE_URL)
assert sha256(tile) == TILE_SHA256
assert tile.startswith(b"\xff\xd8") and tile.endswith(b"\xff\xd9")

print(
    json.dumps(
        {
            "human_annotation_binding": "PASS",
            "locus": "f99v.45",
            "public_2004_tile_sha256": TILE_SHA256,
            "source_binding": "PASS",
            "visual_interpretation_independently_validated": False,
            "yale_2014_image_sha256": YALE_IMAGE_SHA256,
        },
        sort_keys=True,
    )
)
