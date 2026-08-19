#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt363_leaf_margin_formal_atlas"
R = ROOT / "experiments/semantic_assumptions/results"
SOURCES = [
    ("LM001_HELD", R / "lm001_herbal_leaf_margin_visual_selection.tsv", R / "lm001_leaf_margin_visual_held.tsv"),
    ("LM001X", R / "lm001x_currier_a_leaf_margin_extension_selection.tsv", R / "lm001x_currier_a_leaf_margin_extension_result.tsv"),
    ("LM001Y", R / "lm001y_final_residual_leaf_margin_census_selection.tsv", R / "lm001y_final_residual_leaf_margin_census_result.tsv"),
]
OUT_TSV = BASE / "artifacts/gdt363_panel.tsv"
OUT_JSON = BASE / "artifacts/gdt363_freeze.json"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def main() -> None:
    rows = []
    for phase, selection_path, result_path in SOURCES:
        selection = list(GuardedTSV(selection_path, selector_column="page",
                                    forbidden_prefixes=("f84",), forbidden_action="error"))
        if phase == "LM001_HELD": selection = [r for r in selection if r["phase"] == "HELD"]
        result = {r["opaque_id"]: r for r in read(result_path)}
        assert set(result) == {r["opaque_id"] for r in selection}
        for s in selection:
            state = result[s["opaque_id"]]["leaf_margin_state"]
            page = s["page"]
            rows.append({
                "opaque_id": s["opaque_id"], "phase": phase, "page": page,
                "physical_folio": s["physical_folio"], "currier": s["currier"],
                "hand": s["hand"], "quire": s["quire"],
                "folio_rank_quartile": s["folio_rank_quartile"],
                "page_side": page[-1], "canvas_id": s["canvas_id"],
                "leaf_margin_state": state, "score_eligible": "1" if state in {"SMOOTH", "TOOTHED"} else "0",
                "visual_provenance": "FROZEN_AI_DIRECT_VISUAL_OBSERVATION_FROM_LM001_SERIES",
            })
    rows.sort(key=lambda r: (int(r["physical_folio"][1:]), r["page"]))
    assert len(rows) == 44 == len({r["physical_folio"] for r in rows})
    assert Counter(r["leaf_margin_state"] for r in rows) == Counter(SMOOTH=29, TOOTHED=13, UNCERTAIN=2)
    assert Counter((r["currier"], r["leaf_margin_state"]) for r in rows if r["score_eligible"] == "1") == Counter({("A", "SMOOTH"):25, ("A", "TOOTHED"):9, ("B", "SMOOTH"):4, ("B", "TOOTHED"):4})
    fields = list(rows[0])
    with OUT_TSV.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)
    payload = {
        "schema": "GDT363_FREEZE_V1", "status": "FROZEN_BEFORE_GDT363_FORMAL_AGGREGATION",
        "counts": {"pages": 44, "physical_folios": 44, "eligible": 42,
                   "SMOOTH": 29, "TOOTHED": 13, "UNCERTAIN": 2,
                   "A_smooth": 25, "A_toothed": 9, "B_smooth": 4, "B_toothed": 4},
        "formal_library": {
            "source": "ALL_READING_FAMILY_CONSENSUS_GROUPS",
            "allowed": ["family_components", "within_group_family_bigrams_trigrams", "first_prefix_1_3", "last_suffix_1_3", "counts", "boundary_classes"],
            "forbidden": ["surface", "EVA", "member_identity", "root", "PAGE_HOST_substring", "joint_tuple_identity", "meaning", "exact_family_expression"],
            "page_support_min": 5, "page_absence_min": 5,
        },
        "analysis": {"lofo": True, "ridge_lambda": 4.0, "permutation_worlds": 4096,
                     "permutation_strata": "CURRIER_X_FOLIO_RANK_QUARTILE", "maxT": True},
        "access": {"new_images_opened": False, "formal_source_opened_by_freezer": False, "f84_accessed": False},
        "inputs": {str(p.relative_to(ROOT)): sha256_file(p) for _, a, b in SOURCES for p in (a, b)} | {
            "experiments/yolo/gdt363_leaf_margin_formal_atlas/METHOD.md": sha256_file(BASE / "METHOD.md"),
            "experiments/yolo/gdt363_leaf_margin_formal_atlas/src/freeze.py": sha256_file(Path(__file__)),
        },
        "outputs": {str(OUT_TSV.relative_to(ROOT)): sha256_file(OUT_TSV)},
        "claim_ceiling": "EXPLORATORY_PAGE_LEVEL_ANONYMOUS_FORMAL_ASSOCIATION_ONLY_NO_LEXICAL_OR_SEMANTIC_CLAIM",
    }
    OUT_JSON.write_bytes(canonical_json_bytes(payload))


if __name__ == "__main__": main()
