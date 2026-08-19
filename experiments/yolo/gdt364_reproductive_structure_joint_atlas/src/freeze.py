#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt364_reproductive_structure_joint_atlas"
ART = EXP / "artifacts"
SOURCE = ROOT / "experiments/semantic_assumptions/results/existing_human_page_annotations.tsv"
BERRY = ROOT / "experiments/semantic_assumptions/berry_explicit_contrast/TARGET_RESULT.json"
FLOWER = ROOT / "experiments/semantic_assumptions/flower_explicit_contrast/TARGET_RESULT.json"
PANEL = ART / "gdt364_panel.tsv"
FREEZE = ART / "gdt364_freeze.json"
PHRASES = {
    "FLOWER_SIDE": "α: flower(s) seen from the side",
    "BERRY_NO_CIRCLES": "α: berries that have no added circles",
    "NO_FRUIT_OR_FLOWER": "α: no fruits or flowers",
}


def write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    reader = GuardedTSV(SOURCE, selector_column="page", forbidden_prefixes=("f84",), forbidden_action="skip")
    rows = []
    for source in reader:
        hits = [state for state, phrase in PHRASES.items() if phrase in source["illustrations"]]
        if not hits:
            continue
        if len(hits) != 1:
            raise AssertionError((source["page"], hits))
        match = re.match(r"^(f\d+)", source["page"])
        if not match:
            raise AssertionError(source["page"])
        rows.append({
            "page": source["page"], "physical_folio": match.group(1), "quire": source["quire"],
            "visual_state": hits[0], "exact_source_phrase": PHRASES[hits[0]],
            "provenance": "EXISTING_HUMAN_ANNOTATION", "annotation_source": source["source_url"],
            "postexposure_status": "PREVIOUS_BINARY_FORMAL_TARGETS_EXIST",
        })
    rows.sort(key=lambda row: (int(row["physical_folio"][1:]), row["page"]))
    counts = Counter(row["visual_state"] for row in rows)
    assert len(rows) == 34 and len({row["page"] for row in rows}) == 34
    assert len({row["physical_folio"] for row in rows}) == 29
    assert counts == Counter(FLOWER_SIDE=19, BERRY_NO_CIRCLES=8, NO_FRUIT_OR_FLOWER=7)
    assert not any(row["page"].startswith("f84") for row in rows)
    write(PANEL, rows)
    payload = {
        "schema": "GDT364_FREEZE_V1", "status": "POSTEXPOSURE_PANEL_FROZEN_BEFORE_JOINT_SOURCE_FAMILY_AGGREGATION",
        "counts": {"pages": 34, "physical_folios": 29, **dict(sorted(counts.items()))},
        "states": PHRASES, "old_results": {
            "BERRY001": json.loads(BERRY.read_text())["status"],
            "FLOWER001": json.loads(FLOWER.read_text())["status"],
            "rewritten": False,
        },
        "formal_library": {"state_blind": True, "support_min": 5, "absence_min": 5,
                           "exact_family_surface_member_root_host_tuple_forbidden": True},
        "null": {"worlds": 4096, "unit": "WHOLE_PHYSICAL_FOLIO_STATE_VECTOR",
                 "strata": "QUIRE_X_PAGES_PER_PHYSICAL_FOLIO"},
        "access": {"new_images_opened": False, "formal_source_opened": False,
                   "f84_rows_skipped_before_nonselector_parse": reader.stats.skipped_forbidden, "f84_accessed": False},
        "inputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in (SOURCE, BERRY, FLOWER, EXP / "METHOD.md")},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__))},
        "outputs": {str(PANEL.relative_to(ROOT)): sha256_file(PANEL)},
        "claim_ceiling": "POSTEXPOSURE_EXPLORATORY_THREE_CLASS_PAGE_ASSOCIATION_ONLY_NO_LEXICAL_OR_SEMANTIC_CLAIM",
    }
    payload["content_hash"] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    FREEZE.write_bytes(canonical_json_bytes(payload))


if __name__ == "__main__": main()
