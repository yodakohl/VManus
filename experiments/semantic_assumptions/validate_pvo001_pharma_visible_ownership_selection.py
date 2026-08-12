#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions/results"
PANEL = BASE / "pvo001_pharma_visible_ownership_selection.tsv"
RESULT = BASE / "pvo001_pharma_visible_ownership_selection.json"
OUT = BASE / "pvo001_pharma_visible_ownership_selection_validation.json"
URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"


def main() -> None:
    checks = []
    rows = list(csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t"))
    assert len(rows) == 12 and len({row["canvas_id"] for row in rows}) == 12
    checks.append("exact_12_unique_official_canvas_units")
    source_parts = {page for row in rows for page in row["source_pages"].split(";")}
    assert source_parts == {"f88r", "f88v", "f89r1", "f89r2", "f89v1", "f89v2", "f99r", "f99v", "f100r", "f100v", "f101r", "f101v", "f102r1", "f102r2", "f102v1", "f102v2"}
    checks.append("exact_complete_16_logical_source_parts")
    request = urllib.request.Request(URL, headers={"User-Agent": "VManus-PVO001-selection-validator/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response: raw = response.read()
    assert hashlib.sha256(raw).hexdigest() == MANIFEST_SHA
    manifest = json.loads(raw.decode("utf-8"))
    actual = {}
    for canvas in manifest["items"]:
        canvas_id = canvas["id"].rsplit("/", 1)[-1]
        body = canvas["items"][0]["items"][0]["body"]
        actual[canvas_id] = (canvas["label"].get("none", [""])[0], str(body["width"]), str(body["height"]), body["service"][0]["@id"] + "/full/1600,/0/default.jpg")
    assert all(actual[row["canvas_id"]] == (row["canvas_label"], row["image_width"], row["image_height"], row["review_image_url"]) for row in rows)
    checks.append("live_manifest_id_label_geometry_url_bindings")
    assert sum(row["quire"] == "q15" for row in rows) == 4 and sum(row["quire"] == "q19" for row in rows) == 8
    checks.append("exact_quire_counts")
    assert sum(row["outside_prior_mixed_folios"] == "1" for row in rows) == 6
    checks.append("outside_prior_mixed_folio_flag")
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert stored["status"] == "FROZEN_COMPLETE_12_CANVAS_PANEL_BEFORE_IMAGE_INSPECTION"
    assert stored["panel_sha256"] == hashlib.sha256(PANEL.read_bytes()).hexdigest() and all(stored["gates"].values())
    checks.append("canonical_frozen_selection_and_binding")
    assert stored["access"] == {"label_identity_or_formal_feature_opened": False, "selected_image_bodies_opened": False, "voynich_transcription_opened": False}
    checks.append("image_and_text_access_seal")
    value = {"experiment": "PVO001_PHARMA_VISIBLE_OWNERSHIP_SELECTION_VALIDATION", "status": "PASS_7_CHECK_COMPLETE_CANVAS_RECONSTRUCTION", "check_count": len(checks), "checks": checks, "validated_result_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(), "selected_image_bodies_opened_by_validator": False, "claim_ceiling": stored["claim_ceiling"]}
    OUT.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
