#!/usr/bin/env python3
"""Freeze held-folio IGR002 targets and a type-blinded inspection worklist."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
METHOD = HERE / "IGR002_IMAGE_GROUNDED_GRAPHEME_ATLAS_METHOD.md"
GROUPS = RES / "source_sta_family_consensus_groups.tsv"
IGR1_SELECTION = RES / "igr001_image_grounded_grapheme_selection.json"
IGR1_RESULT = RES / "igr001_image_grounded_grapheme_result.json"
IGR1_VALIDATION = RES / "igr001_image_grounded_grapheme_result_validation.json"
OUT = RES / "igr002_image_grounded_grapheme_atlas_selection.json"
BLIND = HERE / "igr002_image_grounded_grapheme_blinded_worklist.tsv"
REPORT = RES / "igr002_image_grounded_grapheme_atlas_selection_report.md"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
# Logical foldout parts that cannot be resolved uniquely from the broad Yale
# canvas label. These are source-geometry bindings, fixed before target access.
FOLDOUT_CANVAS = {
    "f67v2": ("1006195", 5059, 3753, "67v"),
    "f68r1": ("1006196", 7993, 3828, "68r"),
    "f70v1": ("1006201", 2979, 3700, "70v (part)"),
    "f72v2": ("1006204", 5976, 3794, "72v (part)"),
    "f85r2": ("1006229", 7754, 3890, "85r (part) 86v (part) (part of 85-86 foldout)"),
    "f86v6": ("1006229", 7754, 3890, "85r (part) 86v (part) (part of 85-86 foldout)"),
    "f89r2": ("1006233", 9078, 3777, "88v and 89r"),
    "f89v1": ("1006234", 4204, 3809, "89v (part)"),
}
REGISTRATION_NONCE = "445624b17549d3f5b5673667d41aafd59623dafef60279d496c53a726f8bca71"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def folio(page: str) -> str:
    return re.match(r"^(f(?:Ros|[0-9]+))", page, re.I).group(1).lower()

def rank(key: tuple[str, str, str, str], locus: str, index: int) -> str:
    return hashlib.sha256(("IGR002_ATLAS_V1|" + "|".join(key) + f"|{locus}|{index}").encode()).hexdigest()

def main() -> None:
    if OUT.exists() or BLIND.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    old = json.loads(IGR1_SELECTION.read_text())
    result = json.loads(IGR1_RESULT.read_text())
    validation = json.loads(IGR1_VALIDATION.read_text())
    if not result["status"].startswith("PASS_") or not validation["status"].startswith("PASS_"):
        raise SystemExit("IGR001 capacity is not validated")
    keys = []
    prototypes = {}
    for type_index in range(1, 9):
        selected = next(x for x in old["targets"] if x["type_index"] == type_index)
        keys.append((selected["family"], selected["zl_code"], selected["it_code"], selected["rf_code"]))
        prototypes[type_index] = result["type_summaries"][type_index - 1]["modal_complete_signature"]
    excluded = {x["physical_folio"] for x in old["targets"]}
    occurrences = defaultdict(list)
    for row in csv.DictReader(GROUPS.open(newline=""), delimiter="\t"):
        if row["strict_zero_alternative"] != "1" or folio(row["page"]) in excluded:
            continue
        codes = [row[name].split() for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        for index, (family, zl, it, rf) in enumerate(zip(row["family_surface"], *codes), 1):
            key = (family, zl, it, rf)
            if key not in keys:
                continue
            occurrences[key].append({
                "page": row["page"], "physical_folio": folio(row["page"]), "locus": row["locus"],
                "symbol_index_1based": index, "group_symbol_count": int(row["symbol_count"]),
                "consensus_group_index": int(row["consensus_group_index"]),
                "consensus_group_count": int(row["consensus_group_count"]),
                "selection_rank_sha256": rank(key, row["locus"], index),
            })
    manifest_raw = urllib.request.urlopen(MANIFEST_URL, timeout=30).read()
    if hashlib.sha256(manifest_raw).hexdigest() != MANIFEST_SHA:
        raise SystemExit("official Yale manifest drift")
    manifest = json.loads(manifest_raw)
    canvases = {}
    for canvas in manifest["items"]:
        labels = canvas["label"]["none"]
        if len(labels) == 1:
            canvases[labels[0].lower()] = (canvas["id"].rsplit("/", 1)[-1], int(canvas["width"]), int(canvas["height"]), labels[0])
    targets = []
    for type_index, key in enumerate(keys, 1):
        chosen, used = [], set()
        for row in sorted(occurrences[key], key=lambda x: x["selection_rank_sha256"]):
            if row["physical_folio"] in used:
                continue
            chosen.append(row); used.add(row["physical_folio"])
            if len(chosen) == 4:
                break
        if len(chosen) != 4:
            raise SystemExit(f"type {type_index}: fewer than four new folios")
        for occurrence_index, row in enumerate(chosen, 1):
            label_key = row["page"][1:].lower()
            canvas = FOLDOUT_CANVAS.get(row["page"], canvases.get(label_key))
            if canvas is None:
                matches = [v for label, v in canvases.items() if label_key in label.replace(" ", "").lower()]
                if len(matches) != 1:
                    raise SystemExit(f"canvas resolution failure {row['page']}")
                canvas = matches[0]
            canvas_id, width, height, canvas_label = canvas
            opaque = "IGR2" + hashlib.sha256((REGISTRATION_NONCE + "|" + row["locus"] + "|" + str(row["symbol_index_1based"])).encode()).hexdigest()[:14].upper()
            targets.append({
                "opaque_id": opaque, "type_index": type_index, "occurrence_index": occurrence_index,
                "family": key[0], "zl_code": key[1], "it_code": key[2], "rf_code": key[3],
                "prototype_signature": prototypes[type_index], "primary_prediction_target": type_index != 6,
                **row, "canvas_id": canvas_id, "canvas_label": canvas_label,
                "official_dimensions": [width, height],
                "official_full_image_url": f"https://collections.library.yale.edu/iiif/2/{canvas_id}/full/full/0/default.jpg",
                "target_image_opened": False,
            })
    blind_rows = sorted(targets, key=lambda x: hashlib.sha256(("IGR002_BLIND_ORDER_V1|" + x["opaque_id"]).encode()).hexdigest())
    fields = ["opaque_id", "page", "physical_folio", "locus", "symbol_index_1based", "group_symbol_count", "consensus_group_index", "consensus_group_count", "canvas_id", "official_full_image_url", "image_width", "image_height"]
    with BLIND.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for x in blind_rows:
            writer.writerow({**{k: x[k] for k in fields if k not in {"image_width", "image_height"}}, "image_width": x["official_dimensions"][0], "image_height": x["official_dimensions"][1]})
    output = {
        "experiment": "IGR002_IMAGE_GROUNDED_GRAPHEME_ATLAS_SELECTION", "schema": "IGR002_SELECTION_V1",
        "status": "FROZEN_32_NEW_FOLIO_TARGETS_BEFORE_IMAGE_ACCESS", "decision": "AUTHORIZE_TYPE_BLINDED_NATIVE_VISUAL_INSPECTION",
        "targets": targets, "blinded_order": [x["opaque_id"] for x in blind_rows], "private_registration_nonce": REGISTRATION_NONCE,
        "counts": {"types": 8, "targets": 32, "primary_targets": 28, "diagnostic_type6_targets": 4, "new_physical_folios": len({x["physical_folio"] for x in targets}), "excluded_igr001_folios": len(excluded)},
        "gates": {"localized_primary_targets": 24, "exact_signature_matches": 20, "types_with_at_least_three_of_four_matches": 6},
        "inputs": {str(p.relative_to(HERE.parents[1])): sha(p) for p in (METHOD, GROUPS, IGR1_SELECTION, IGR1_RESULT, IGR1_VALIDATION)} | {"yale_manifest_2002046_sha256": MANIFEST_SHA},
        "access": {"target_image_bodies_opened": False, "blinded_worklist_exposes_type_or_prototype": False, "crop_only_shape_review_required": True, "source_localizer_forbidden_to_score_shape": True, "shape_reviewer_forbidden_selection_or_igr001_access": True, "prior_full_canvas_exposure_possible": True, "ocr_clip_embedding_or_automated_classifier_used": False},
        "claim_ceiling": "A pass can establish held-folio recurrence of anonymous visible shape classes only; it cannot select a reading or establish allography sound alphabet word language cipher plaintext meaning or translation.",
    }
    OUT.write_text(json.dumps(output, sort_keys=True, indent=2) + "\n")
    REPORT.write_text(f"# IGR002 held-folio grapheme-atlas selection\n\nStatus: **{output['status']}**.\n\nFrozen 32 targets on {output['counts']['new_physical_folios']} new physical folios after excluding all {len(excluded)} IGR001 folios. The type-blinded inspection worklist exposes no type, reading code, prototype signature, or prior result.\n")
    print(json.dumps(output["counts"], sort_keys=True))

if __name__ == "__main__": main()
