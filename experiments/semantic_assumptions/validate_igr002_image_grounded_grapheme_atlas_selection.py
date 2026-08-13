#!/usr/bin/env python3
"""Independent reconstruction of the IGR002 held-folio selection."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RES = HERE / "results"
METHOD = HERE / "IGR002_IMAGE_GROUNDED_GRAPHEME_ATLAS_METHOD.md"
GROUPS = RES / "source_sta_family_consensus_groups.tsv"
OLD = RES / "igr001_image_grounded_grapheme_selection.json"
IGR1_RESULT = RES / "igr001_image_grounded_grapheme_result.json"
IGR1_VALIDATION = RES / "igr001_image_grounded_grapheme_result_validation.json"
RESULT = RES / "igr002_image_grounded_grapheme_atlas_selection.json"
BLIND = HERE / "igr002_image_grounded_grapheme_blinded_worklist.tsv"
OUT = RES / "igr002_image_grounded_grapheme_atlas_selection_validation.json"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
FOLDOUT_PAGE_TO_CANVAS = {
    "f67v2": "1006195", "f68r1": "1006196", "f70v1": "1006201", "f72v2": "1006204",
    "f85r2": "1006229", "f86v6": "1006229", "f89r2": "1006233", "f89v1": "1006234",
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def folio(page: str) -> str:
    return re.match(r"^(f(?:Ros|[0-9]+))", page, re.I).group(1).lower()

def rank(key: tuple[str, str, str, str], locus: str, index: int) -> str:
    return hashlib.sha256(("IGR002_ATLAS_V1|" + "|".join(key) + f"|{locus}|{index}").encode()).hexdigest()

def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text())
    old = json.loads(OLD.read_text())
    igr1 = json.loads(IGR1_RESULT.read_text())
    igr1v = json.loads(IGR1_VALIDATION.read_text())
    checks: dict[str, bool] = {}
    manifest_raw = urllib.request.urlopen(MANIFEST_URL, timeout=30).read()
    checks["official_manifest_hash"] = hashlib.sha256(manifest_raw).hexdigest() == MANIFEST_SHA
    manifest = json.loads(manifest_raw)
    by_id = {x["id"].rsplit("/", 1)[-1]: x for x in manifest["items"]}
    labels = {}
    for canvas_id, canvas in by_id.items():
        if len(canvas["label"]["none"]) == 1:
            labels[canvas["label"]["none"][0].lower()] = canvas_id

    keys, prototypes = [], {}
    for type_index in range(1, 9):
        old_target = next(x for x in old["targets"] if x["type_index"] == type_index)
        keys.append((old_target["family"], old_target["zl_code"], old_target["it_code"], old_target["rf_code"]))
        prototypes[type_index] = igr1["type_summaries"][type_index - 1]["modal_complete_signature"]
    excluded = {x["physical_folio"] for x in old["targets"]}
    occurrences = defaultdict(list)
    source_rows = list(csv.DictReader(GROUPS.open(newline=""), delimiter="\t"))
    for row in source_rows:
        if row["strict_zero_alternative"] != "1" or folio(row["page"]) in excluded:
            continue
        codes = [row[name].split() for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        for index, (family, zl, it, rf) in enumerate(zip(row["family_surface"], *codes), 1):
            key = (family, zl, it, rf)
            if key in keys:
                occurrences[key].append((rank(key, row["locus"], index), folio(row["page"]), row["locus"], index))
    expected = []
    for type_index, key in enumerate(keys, 1):
        used = set()
        for digest, physical, locus, index in sorted(occurrences[key]):
            if physical in used:
                continue
            expected.append((type_index, key, physical, locus, index, digest)); used.add(physical)
            if len(used) == 4:
                break
    observed = [(x["type_index"], (x["family"], x["zl_code"], x["it_code"], x["rf_code"]), x["physical_folio"], x["locus"], x["symbol_index_1based"], x["selection_rank_sha256"]) for x in result["targets"]]
    checks["exact_source_only_ranked_selection"] = observed == expected
    checks["four_distinct_new_folios_per_type"] = all(len({x["physical_folio"] for x in result["targets"] if x["type_index"] == i}) == 4 for i in range(1, 9))
    checks["zero_igr001_folio_overlap"] = not ({x["physical_folio"] for x in result["targets"]} & excluded)
    checks["igr001_result_and_validation_pass"] = igr1["status"].startswith("PASS_") and igr1v["status"].startswith("PASS_")
    checks["all_prototypes_and_primary_flags_reconstructed"] = all(x["prototype_signature"] == prototypes[x["type_index"]] and x["primary_prediction_target"] == (x["type_index"] != 6) for x in result["targets"])
    nonce = result["private_registration_nonce"]
    checks["registration_nonce_is_256_bit_hex"] = bool(re.fullmatch(r"[0-9a-f]{64}", nonce))
    checks["all_opaque_ids_reconstructed"] = all(x["opaque_id"] == "IGR2" + hashlib.sha256((nonce + "|" + x["locus"] + "|" + str(x["symbol_index_1based"])).encode()).hexdigest()[:14].upper() for x in result["targets"])
    expected_order = [x["opaque_id"] for x in sorted(result["targets"], key=lambda x: hashlib.sha256(("IGR002_BLIND_ORDER_V1|" + x["opaque_id"]).encode()).hexdigest())]
    checks["blinded_order_reconstructed"] = result["blinded_order"] == expected_order

    canvas_checks = []
    for target in result["targets"]:
        page = target["page"]
        canvas_id = FOLDOUT_PAGE_TO_CANVAS.get(page)
        if canvas_id is None:
            canvas_id = labels.get(page[1:].lower())
        canvas = by_id.get(canvas_id or "")
        canvas_checks.append(
            canvas is not None and target["canvas_id"] == canvas_id
            and target["official_dimensions"] == [int(canvas["width"]), int(canvas["height"])]
            and target["canvas_label"] == canvas["label"]["none"][0]
            and target["official_full_image_url"] == f"https://collections.library.yale.edu/iiif/2/{canvas_id}/full/full/0/default.jpg"
        )
    checks["all_canvas_ids_dimensions_labels_urls_reconstructed"] = all(canvas_checks)

    blind = list(csv.DictReader(BLIND.open(), delimiter="\t"))
    checks["blind_worklist_exact_order"] = [x["opaque_id"] for x in blind] == expected_order
    forbidden = {"type_index", "family", "zl_code", "it_code", "rf_code", "prototype_signature", "primary_prediction_target", "private_registration_nonce"}
    checks["blind_worklist_omits_type_codes_prototype_nonce"] = not (forbidden & set(blind[0]))
    targets_by_id = {x["opaque_id"]: x for x in result["targets"]}
    checks["blind_worklist_complete_payload_reconstructed"] = all(
        row == {
            "opaque_id": target["opaque_id"], "page": target["page"], "physical_folio": target["physical_folio"], "locus": target["locus"],
            "symbol_index_1based": str(target["symbol_index_1based"]), "group_symbol_count": str(target["group_symbol_count"]),
            "consensus_group_index": str(target["consensus_group_index"]), "consensus_group_count": str(target["consensus_group_count"]),
            "canvas_id": target["canvas_id"], "official_full_image_url": target["official_full_image_url"],
            "image_width": str(target["official_dimensions"][0]), "image_height": str(target["official_dimensions"][1]),
        }
        for row in blind for target in [targets_by_id[row["opaque_id"]]]
    )
    expected_counts = {"types": 8, "targets": 32, "primary_targets": 28, "diagnostic_type6_targets": 4, "new_physical_folios": len({x["physical_folio"] for x in result["targets"]}), "excluded_igr001_folios": len(excluded)}
    checks["complete_counts"] = result["counts"] == expected_counts
    checks["frozen_gates"] = result["gates"] == {"localized_primary_targets": 24, "exact_signature_matches": 20, "types_with_at_least_three_of_four_matches": 6}
    expected_inputs = {str(p.relative_to(ROOT)): sha(p) for p in (METHOD, GROUPS, OLD, IGR1_RESULT, IGR1_VALIDATION)} | {"yale_manifest_2002046_sha256": MANIFEST_SHA}
    checks["all_input_hashes"] = result["inputs"] == expected_inputs
    checks["status_decision_access"] = result["status"] == "FROZEN_32_NEW_FOLIO_TARGETS_BEFORE_IMAGE_ACCESS" and result["decision"] == "AUTHORIZE_TYPE_BLINDED_NATIVE_VISUAL_INSPECTION" and result["access"] == {"target_image_bodies_opened": False, "blinded_worklist_exposes_type_or_prototype": False, "crop_only_shape_review_required": True, "source_localizer_forbidden_to_score_shape": True, "shape_reviewer_forbidden_selection_or_igr001_access": True, "prior_full_canvas_exposure_possible": True, "ocr_clip_embedding_or_automated_classifier_used": False}
    checks["canonical_result"] = RESULT.read_bytes() == (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    if not all(checks.values()):
        raise SystemExit({k: v for k, v in checks.items() if not v})
    validation = {"status": f"PASS_{len(checks)}_CHECK_INDEPENDENT_IGR002_SELECTION_RECONSTRUCTION", "check_count": len(checks), "checks": list(checks), "result_sha256": sha(RESULT), "blind_worklist_sha256": sha(BLIND)}
    OUT.write_text(json.dumps(validation, sort_keys=True, indent=2) + "\n")
    print(json.dumps(validation, sort_keys=True))

if __name__ == "__main__": main()
