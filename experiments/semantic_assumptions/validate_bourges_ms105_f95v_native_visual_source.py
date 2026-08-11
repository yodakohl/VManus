#!/usr/bin/env python3
"""Validate Bourges source bindings, not the native visual interpretation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.request


BASE = Path(__file__).resolve().parent
PRIOR_FILES = {
    "results/biblissima_f67_f68_metadata_worth.json":
        "a05cd5d3c1c973dade178a370fadfbdef64ad39a1b845e4e2edc743894b9895f",
    "results/initiale_f67v2_cardinal_wind_ownership.json":
        "377c793f414757c7a3891164ad7db57f1d955431d7973e084b93d8925d9315e3",
    "results/sg1029_f135_f67v2_native_visual_topology.json":
        "8767c9f371d2e5c7637fe42c2c9c53e75eb8566217ed7c741252057a00421d0b",
}
INFO_URL = "https://iiif.irht.cnrs.fr/iiif/ark:/63955/v91mnwqetgqf/info.json"
IIIF_ID = (
    "https://iiif.irht.cnrs.fr/iiif/VOLUME1/France/Bourges/"
    "B180336101/DEPOT/IRHT_146793_2"
)
IMAGE_URL = f"{IIIF_ID}/full/full/0/native.jpg"
INFO_SHA256 = "180c2aa59b20e79acb9678146ef9b346c0a498d5b62836beaea4b1aab0124540"
IMAGE_SHA256 = "1f3936fd922c3470c60ba453983b123b928d342b3ecfc9f23882db315fe4ec9c"
WIDTH = 2000
HEIGHT = 2944


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


for relative_path, expected_sha256 in PRIOR_FILES.items():
    assert sha256((BASE / relative_path).read_bytes()) == expected_sha256

info_bytes = fetch(INFO_URL)
assert sha256(info_bytes) == INFO_SHA256
info = json.loads(info_bytes)
assert info["@id"] == IIIF_ID
assert info["width"] == WIDTH
assert info["height"] == HEIGHT
profiles = info["profile"]
assert profiles[0] == "http://iiif.io/api/image/2/level2.json"
assert "jpg" in profiles[1]["formats"]

image = fetch(IMAGE_URL)
assert image.startswith(b"\xff\xd8") and image.endswith(b"\xff\xd9")
assert sha256(image) == IMAGE_SHA256

print(
    json.dumps(
        {
            "image_sha256": IMAGE_SHA256,
            "prior_bindings": "PASS",
            "source_binding": "PASS",
            "source_dimensions": [WIDTH, HEIGHT],
            "visual_interpretation_independently_validated": False,
        },
        sort_keys=True,
    )
)
