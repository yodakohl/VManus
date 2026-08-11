#!/usr/bin/env python3
"""Validate f2r.15 source bindings, not the native visual interpretation."""

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
PANEL = BASE / "results" / "translation_anchor_human_review_panel_v1.tsv"
PANEL_SHA256 = "20134182f439a742a3de825858aae4f879faab8f5f17f28a676f48b318a7d563"
RESULT = BASE / "results" / "f2r15_native_visual_ownership_correction.json"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
CANVAS_ID = "https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006078"
IMAGE_URL = "https://collections.library.yale.edu/iiif/2/1006078/full/full/0/default.jpg"
IMAGE_SHA256 = "826533a0760798acf5a4caa01ac29fe95eb1ed13a9fb26ac82900a8aea11d53f"
IMAGE_WIDTH = 2691
IMAGE_HEIGHT = 3770
DETAIL_URL = (
    "https://collections.library.yale.edu/iiif/2/1006078/"
    "1750,900,900,900/1800,/0/default.jpg"
)
DETAIL_SHA256 = "636335ce1c65c614a78578bbbcf571fcd78f2403d9624dacdd86d6b4c342914c"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


annotation_bytes = ANNOTATIONS.read_bytes()
assert sha256(annotation_bytes) == ANNOTATIONS_SHA256
annotations = list(csv.DictReader(io.StringIO(annotation_bytes.decode("utf-8")), delimiter="\t"))
target_annotations = [row for row in annotations if row["locus"] == "f2r.15"]
assert len(target_annotations) == 1
annotation = target_annotations[0]
assert annotation["local_comment"] == "Within leaf."
assert annotation["local_relation_tags"] == "REL_ENCLOSURE"
assert annotation["certainty"] == "UNHEDGED"

panel_bytes = PANEL.read_bytes()
assert sha256(panel_bytes) == PANEL_SHA256
panel = list(csv.DictReader(io.StringIO(panel_bytes.decode("utf-8")), delimiter="\t"))
target_panel = [row for row in panel if row["physical_locus"] == "f2r.15"]
assert len(target_panel) == 1
target = target_panel[0]
assert target["relation_grade"] == "DIRECT_ENCLOSURE_UNDER_PAINT"
assert target["ZL3b_raw"] == "ios.an.on"
assert target["IT2a_raw"] == "ABSENT"
assert target["RF1b_raw"] == "ios.an.on"

manifest = json.loads(fetch(MANIFEST_URL))
canvases = [item for item in manifest["items"] if item.get("id") == CANVAS_ID]
assert len(canvases) == 1
canvas = canvases[0]
assert canvas["label"] == {"none": ["2r"]}
assert canvas["width"] == IMAGE_WIDTH and canvas["height"] == IMAGE_HEIGHT
body = canvas["items"][0]["items"][0]["body"]
assert body["id"] == IMAGE_URL
assert body["width"] == IMAGE_WIDTH and body["height"] == IMAGE_HEIGHT
assert sha256(fetch(IMAGE_URL)) == IMAGE_SHA256
detail = fetch(DETAIL_URL)
assert sha256(detail) == DETAIL_SHA256
assert detail.startswith(b"\xff\xd8") and detail.endswith(b"\xff\xd9")

result = json.loads(RESULT.read_text(encoding="utf-8"))
assert result["decision"] == "CORRECT_F2R15_TO_BOUNDARY_OVERLAP_LAYER_ORDER_UNRESOLVED"
assert result["revised_relation_grade"] == "BOUNDARY_OVERLAP_LAYER_ORDER_UNRESOLVED"
assert result["relation_gates"] == {
    "complete_record_wholly_inside_leaf": False,
    "ink_before_paint_established": False,
    "local_leaf_boundary_association_supported": True,
    "ordinary_light_layer_order_resolved": False,
    "record_continues_onto_bare_parchment": True,
    "record_partly_overlaps_pale_green_leaf_tip": True,
    "second_readable_colour_value_supplied": False,
    "second_voynich_colour_record_supplied": False,
}

print(
    json.dumps(
        {
            "human_annotation_binding": "PASS",
            "locus": "f2r.15",
            "manual_transcription_binding": "PASS",
            "official_detail_sha256": DETAIL_SHA256,
            "official_image_sha256": IMAGE_SHA256,
            "source_binding": "PASS",
            "visual_interpretation_independently_validated": False,
        },
        sort_keys=True,
    )
)
