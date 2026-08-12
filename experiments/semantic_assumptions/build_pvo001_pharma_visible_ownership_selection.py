#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "PVO001_PHARMA_VISIBLE_OWNERSHIP_CENSUS_METHOD.md"
ANN = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
OUT_TSV = RESULTS / "pvo001_pharma_visible_ownership_selection.tsv"
OUT_JSON = RESULTS / "pvo001_pharma_visible_ownership_selection.json"
OUT_MD = RESULTS / "pvo001_pharma_visible_ownership_selection_report.md"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA256 = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
CANVASES = (
    ("1037112", "88r", "q15", "f88r", "f88"),
    ("1006233", "88v and 89r", "q15", "f88v;f89r1;f89r2", "f88;f89"),
    ("1006234", "89v (part)", "q15", "f89v1", "f89"),
    ("1006235", "89v (part) and 90r", "q15", "f89v2", "f89"),
    ("1006246", "99r", "q19", "f99r", "f99"),
    ("1006247", "99v", "q19", "f99v", "f99"),
    ("1006248", "100r", "q19", "f100r", "f100"),
    ("1006249", "100v and 101r", "q19", "f100v;f101r", "f100;f101"),
    ("1006250", "101v (part)", "q19", "f101v", "f101"),
    ("1006251", "101v (part) and 102r", "q19", "f101v;f102r1;f102r2", "f101;f102"),
    ("1006252", "102v (part)", "q19", "f102v1", "f102"),
    ("1006253", "102v (part)", "q19", "f102v2", "f102"),
)
FIELDS = ("opaque_id", "canvas_unit_index", "source_pages", "source_folios", "outside_prior_mixed_folios", "quire", "canvas_id", "canvas_label", "image_width", "image_height", "review_image_url")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def main() -> None:
    pharma = set()
    for row in csv.DictReader(ANN.open(encoding="utf-8"), delimiter="\t"):
        if "SOURCE_PHARMACEUTICAL_PAGE" in row["source_tags"]:
            pharma.add(row["page"])
    assert pharma == {page for _, _, _, pages, _ in CANVASES for page in pages.split(";")}
    request = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "VManus-PVO001/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response: raw = response.read()
    assert sha_bytes(raw) == MANIFEST_SHA256
    manifest = json.loads(raw.decode("utf-8"))
    by_label = {}
    for canvas in manifest["items"]: by_label.setdefault(canvas["label"].get("none", [""])[0], []).append(canvas)
    rows = []
    for unit_index, (expected_id, label, quire, source_pages, source_folios) in enumerate(CANVASES, 1):
        hits = [canvas for canvas in by_label.get(label, []) if canvas["id"].rsplit("/", 1)[-1] == expected_id]
        assert len(hits) == 1
        canvas = hits[0]; body = canvas["items"][0]["items"][0]["body"]
        canvas_id = canvas["id"].rsplit("/", 1)[-1]
        assert canvas_id == expected_id
        outside = not ({"f89", "f102"} & set(source_folios.split(";")))
        rows.append({"opaque_id": "PV" + sha_bytes(f"PVO001_OPAQUE|{canvas_id}".encode())[:8].upper(), "canvas_unit_index": unit_index, "source_pages": source_pages, "source_folios": source_folios, "outside_prior_mixed_folios": int(outside), "quire": quire, "canvas_id": canvas_id, "canvas_label": label, "image_width": body["width"], "image_height": body["height"], "review_image_url": body["service"][0]["@id"] + "/full/1600,/0/default.jpg"})
    rows.sort(key=lambda row: row["opaque_id"])
    out = io.StringIO(newline=""); writer = csv.DictWriter(out, fieldnames=FIELDS, delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows); OUT_TSV.write_text(out.getvalue(), encoding="utf-8")
    result = {"experiment": "PVO001_PHARMA_VISIBLE_OWNERSHIP_SELECTION", "schema": "PVO001_SELECTION_V1", "status": "FROZEN_COMPLETE_12_CANVAS_PANEL_BEFORE_IMAGE_INSPECTION", "decision": "AUTHORIZE_ONE_PASS_NATIVE_VISIBLE_OWNERSHIP_CENSUS", "counts": {"canvases": 12, "logical_source_parts": len(pharma), "q15": 4, "q19": 8}, "gates": {"exact_complete_pharmaceutical_logical_source_parts": pharma == {page for _, _, _, pages, _ in CANVASES for page in pages.split(";")}, "exact_12_unique_official_canvases": len({row["canvas_id"] for row in rows}) == 12, "exact_bound_manifest_ids_and_labels": {(row["canvas_id"], row["canvas_label"]) for row in rows} == {(item[0], item[1]) for item in CANVASES}, "no_sampling_or_visual_selection": True, "selected_image_bodies_not_opened": True, "voynich_text_or_label_identity_not_opened": True}, "inputs": {str(METHOD.relative_to(ROOT)): sha(METHOD), str(ANN.relative_to(ROOT)): sha(ANN), "yale_manifest_2002046_sha256": MANIFEST_SHA256}, "panel_sha256": sha(OUT_TSV), "access": {"selected_image_bodies_opened": False, "voynich_transcription_opened": False, "label_identity_or_formal_feature_opened": False}, "claim_ceiling": "This freezes the complete 12-canvas pharmaceutical panel for a source-only visible-ownership census. It supplies no owner finding, label meaning, ROOT or LEAF word, plant identity, plaintext, or translation."}
    assert all(result["gates"].values())
    OUT_JSON.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_MD.write_text("# PVO001 pharmaceutical visible-ownership selection\n\nStatus: **FROZEN_COMPLETE_12_CANVAS_PANEL_BEFORE_IMAGE_INSPECTION**.\n\nThe public source atlas and official Yale manifest fix all 12 author-visible pharmaceutical canvases covering all 16 logical source page parts: four canvases in q15 and eight in q19. Several canvases combine adjacent logical pages and several logical pages span two canvases, so the official manifest canvas is the frozen visual unit. No sampling, ranking, or visual selection occurred, and none of the selected image bodies was opened by the builder.\n\nInspect once in opaque-ID order under the frozen singular visible-owner rubric. No Voynich transcription or label identity may be opened. This selection supplies no owner finding, plant-part word, meaning, plaintext, or translation.\n", encoding="utf-8")


if __name__ == "__main__": main()
