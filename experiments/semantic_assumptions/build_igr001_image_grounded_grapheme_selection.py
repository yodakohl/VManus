#!/usr/bin/env python3
"""Freeze the IGR001 recurrent-disagreement image panel before image access."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
METHOD = HERE / "IGR001_IMAGE_GROUNDED_GRAPHEME_METHOD.md"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
LTG = RESULTS / "ltg001_latent_channel_result_validation.json"
OUT = RESULTS / "igr001_image_grounded_grapheme_selection.json"
REPORT = RESULTS / "igr001_image_grounded_grapheme_selection_report.md"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"^(f(?:Ros|[0-9]+))", page, re.I)
    if not match:
        raise ValueError(page)
    return match.group(1).lower()


def rank(key: tuple[str, str, str, str], locus: str, index: int) -> str:
    return hashlib.sha256(("IGR001_PANEL_V1|" + "|".join(key) + f"|{locus}|{index}").encode()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    validation = json.loads(LTG.read_text(encoding="utf-8"))
    if validation["status"] != "PASS_INDEPENDENT_LTG001_RESULT_RECONSTRUCTION":
        raise SystemExit("LTG001 closure is not independently validated")
    source = list(csv.DictReader(GROUPS.open(encoding="utf-8", newline=""), delimiter="\t"))
    counts = Counter()
    folios = defaultdict(set)
    occurrences = defaultdict(list)
    for row in source:
        if row["strict_zero_alternative"] != "1":
            continue
        codes = [row[field].split() for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        for index, (family, zl, it, rf) in enumerate(zip(row["family_surface"], *codes), 1):
            if zl == it == rf:
                continue
            key = (family, zl, it, rf)
            pf = folio(row["page"])
            counts[key] += 1
            folios[key].add(pf)
            occurrences[key].append({
                "locus": row["locus"], "page": row["page"], "physical_folio": pf,
                "symbol_index_1based": index, "group_symbol_count": int(row["symbol_count"]),
                "group_start_symbol_1based": int(row["start_symbol_1based"]),
                "selection_rank_sha256": rank(key, row["locus"], index),
            })
    eligible = [key for key in counts if len(folios[key]) >= 35]
    selected_types = sorted(eligible, key=lambda key: (-counts[key], tuple(x.encode() for x in key)))[:8]
    if len(selected_types) != 8:
        raise SystemExit("fewer than eight eligible triplets")

    manifest_raw = urllib.request.urlopen(MANIFEST_URL, timeout=30).read()
    if hashlib.sha256(manifest_raw).hexdigest() != MANIFEST_SHA:
        raise SystemExit("official Yale manifest drift")
    manifest = json.loads(manifest_raw)
    canvases = {}
    for canvas in manifest["items"]:
        labels = canvas["label"]["none"]
        if len(labels) != 1:
            continue
        identifier = canvas["id"].rsplit("/", 1)[-1]
        canvases[labels[0].lower()] = (identifier, int(canvas["width"]), int(canvas["height"]), labels[0])

    targets = []
    for type_index, key in enumerate(selected_types, 1):
        chosen = []
        used = set()
        for row in sorted(occurrences[key], key=lambda item: item["selection_rank_sha256"]):
            if row["physical_folio"] in used:
                continue
            chosen.append(row)
            used.add(row["physical_folio"])
            if len(chosen) == 3:
                break
        if len(chosen) != 3:
            raise SystemExit("three-folio selection failure")
        for occurrence_index, row in enumerate(chosen, 1):
            label_key = row["page"][1:].lower()
            if label_key not in canvases:
                # Foldout labels can contain the logical page among other text.
                matches = [value for label, value in canvases.items() if label_key in label.replace(" ", "").lower()]
                if len(matches) != 1:
                    raise SystemExit(f"canvas resolution failure {row['page']}")
                canvas = matches[0]
            else:
                canvas = canvases[label_key]
            canvas_id, width, height, canvas_label = canvas
            targets.append({
                "opaque_id": "IGR" + hashlib.sha256((str(key) + row["locus"] + str(row["symbol_index_1based"])).encode()).hexdigest()[:10].upper(),
                "type_index": type_index, "occurrence_index": occurrence_index,
                "family": key[0], "zl_code": key[1], "it_code": key[2], "rf_code": key[3],
                "type_positions": counts[key], "type_folios": len(folios[key]),
                **row, "canvas_id": canvas_id, "canvas_label": canvas_label,
                "official_dimensions": [width, height],
                "review_image_url": f"https://collections.library.yale.edu/iiif/2/{canvas_id}/full/1800,/0/default.jpg",
                "target_image_opened": False,
            })
    result = {
        "experiment": "IGR001_IMAGE_GROUNDED_GRAPHEME_SELECTION",
        "schema": "IGR001_SELECTION_V1",
        "status": "FROZEN_EIGHT_TRIPLET_TWENTY_FOUR_TARGET_PANEL_BEFORE_IMAGE_ACCESS",
        "decision": "AUTHORIZE_ONE_BOUNDED_NATIVE_VISUAL_INSPECTION_PER_TARGET",
        "selection_rule": "top eight exact disagreement triplets with at least 35 folios; first three distinct folios by frozen SHA256 rank",
        "counts": {"triplet_types": 8, "targets": 24, "physical_folios": len({row["physical_folio"] for row in targets}), "non_dominant_types": 7},
        "targets": targets,
        "rubric_states": ["ONE_CLEAR_VISIBLE_UNIT", "LIGATED_OR_COMPOSITE_UNIT", "DAMAGED_RETRACED_OR_AMBIGUOUS", "LOCALIZATION_UNRESOLVED"],
        "shape_signature_fields": ["main_vertical_stems", "closed_loops", "left_extension", "right_extension", "descender", "separated_dot"],
        "gates": {"localized_types": 6, "matching_shape_types": 5, "non_dominant_types_meeting_both": 4},
        "inputs": {str(path.relative_to(HERE.parents[1])): sha(path) for path in (METHOD, GROUPS, LTG)} | {"yale_manifest_2002046_sha256": MANIFEST_SHA},
        "access": {"target_image_bodies_opened": False, "ocr_clip_embeddings_or_automated_classifier_used": False, "target_selection_used_image_similarity": False},
        "claim_ceiling": "A pass may establish stable visible shape classes behind recurrent manual-reading disagreements only. It cannot choose the correct transcription or establish an authorial grapheme, allography, sound, alphabet, word, language, cipher, plaintext, meaning, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# IGR001 image-grounded grapheme selection\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"The source-only rule freezes eight recurrent disagreement triplets and 24 target positions on {result['counts']['physical_folios']} physical folios. Each triplet supplies three different-folio targets; seven of eight are independent of the dominant RF convention.\n\n"
        "No target image entered selection. The next step is one bounded native-visual inspection per target under the neutral shape rubric; OCR, CLIP, embeddings, and automated glyph classification remain prohibited.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
