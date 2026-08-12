#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions/results"
METHOD = ROOT / "experiments/semantic_assumptions/LM002_LEAF_MARGIN_CHO_CHE_REGIME_METHOD.md"
SELECTIONS = [
    (BASE / "lm001_herbal_leaf_margin_visual_selection.tsv", "LM001_HELD"),
    (BASE / "lm001x_currier_a_leaf_margin_extension_selection.tsv", "LM001X"),
    (BASE / "lm001y_final_residual_leaf_margin_census_selection.tsv", "LM001Y"),
]
OBSERVATIONS = [
    BASE / "lm001_leaf_margin_visual_held.tsv",
    BASE / "lm001x_currier_a_leaf_margin_extension_result.tsv",
    BASE / "lm001y_final_residual_leaf_margin_census_result.tsv",
]
TARGET = BASE / "parisel_cho_che_folio_states.tsv"
TARGET_SHA256 = "4c713c379b33d04985c0efbf9dd4025cb810a9c1006975f7855ed6cc52ff381c"
OUT_TSV = BASE / "lm002_leaf_margin_cho_che_capacity_panel.tsv"
OUT_JSON = BASE / "lm002_leaf_margin_cho_che_capacity.json"
OUT_MD = BASE / "lm002_leaf_margin_cho_che_capacity_report.md"

FIELDS = ["opaque_id", "page", "physical_folio", "leaf_margin_state", "source_phase", "currier", "hand", "quire", "folio_rank_quartile", "page_side", "phase_quartile_side_cell", "phase_quire_cell"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_tsv(rows: list[dict[str, str]]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    return out.getvalue().encode()


def capacity(rows: list[dict[str, str]], field: str) -> dict:
    cells: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        cells[row[field]].append(row)
    mobile = {key: values for key, values in cells.items() if len({row["leaf_margin_state"] for row in values}) == 2}
    orbit = math.prod(math.comb(len(values), sum(row["leaf_margin_state"] == "TOOTHED" for row in values)) for values in mobile.values())
    return {
        "all_cells": len(cells),
        "mobile_cells": len(mobile),
        "mobile_folios": sum(len(values) for values in mobile.values()),
        "mobile_toothed": sum(row["leaf_margin_state"] == "TOOTHED" for values in mobile.values() for row in values),
        "assignments": orbit,
        "minimum_inclusive_p": 1 / orbit,
        "cell_state_counts": {
            key: dict(sorted(Counter(row["leaf_margin_state"] for row in values).items()))
            for key, values in sorted(mobile.items())
        },
    }


def main() -> None:
    metadata = {}
    phases = {}
    for path, phase in SELECTIONS:
        for row in csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"):
            assert row["opaque_id"] not in metadata
            metadata[row["opaque_id"]] = row
            phases[row["opaque_id"]] = phase
    rows = []
    excluded = []
    for path in OBSERVATIONS:
        for obs in csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"):
            source = metadata[obs["opaque_id"]]
            if obs["leaf_margin_state"] == "UNCERTAIN":
                excluded.append(obs["opaque_id"])
                continue
            row = {
                "opaque_id": obs["opaque_id"], "page": source["page"],
                "physical_folio": source["physical_folio"], "leaf_margin_state": obs["leaf_margin_state"],
                "source_phase": phases[obs["opaque_id"]], "currier": obs["currier"], "hand": source["hand"],
                "quire": obs["quire"], "folio_rank_quartile": obs["folio_rank_quartile"],
                "page_side": source["page"][-1],
            }
            row["phase_quartile_side_cell"] = "|".join(row[key] for key in ("source_phase", "currier", "hand", "folio_rank_quartile", "page_side"))
            row["phase_quire_cell"] = "|".join(row[key] for key in ("source_phase", "currier", "hand", "quire"))
            rows.append(row)
    rows.sort(key=lambda row: row["opaque_id"])
    assert len(rows) == 42 and len({row["physical_folio"] for row in rows}) == 42
    assert Counter(row["leaf_margin_state"] for row in rows) == {"SMOOTH": 29, "TOOTHED": 13}
    assert len(excluded) == 2
    OUT_TSV.write_bytes(canonical_tsv(rows))
    primary = capacity(rows, "phase_quartile_side_cell")
    quire = capacity(rows, "phase_quire_cell")

    # Capacity-only diagnostics; target rows are never opened.
    def diagnostic(keys: tuple[str, ...]) -> dict:
        cells = defaultdict(list)
        for row in rows: cells[tuple(row[key] for key in keys)].append(row)
        mobile = [values for values in cells.values() if len({row["leaf_margin_state"] for row in values}) == 2]
        orbit = math.prod(math.comb(len(values), sum(row["leaf_margin_state"] == "TOOTHED" for row in values)) for values in mobile)
        return {"mobile_cells": len(mobile), "mobile_folios": sum(map(len, mobile)), "assignments": orbit, "minimum_inclusive_p": 1 / orbit}

    gates = {
        "exact_42_admitted_unique_physical_folios": len(rows) == len({row["physical_folio"] for row in rows}) == 42,
        "exact_29_smooth_13_toothed": Counter(row["leaf_margin_state"] for row in rows) == {"SMOOTH": 29, "TOOTHED": 13},
        "exact_two_uncertain_excluded_before_target": len(excluded) == 2,
        "primary_exact_5_cells_13_folios_108_assignments": (primary["mobile_cells"], primary["mobile_folios"], primary["assignments"]) == (5, 13, 108),
        "quire_exact_5_cells_16_folios_324_assignments": (quire["mobile_cells"], quire["mobile_folios"], quire["assignments"]) == (5, 16, 324),
        "both_inferential_views_can_reach_point01": primary["minimum_inclusive_p"] <= .01 and quire["minimum_inclusive_p"] <= .01,
        "formal_target_table_not_opened_or_parsed": True,
        "no_literal_root_role_family_member_or_gloss": True,
    }
    result = {
        "experiment": "LM002_LEAF_MARGIN_CHO_CHE_REGIME_CAPACITY",
        "schema": "LM002_CAPACITY_V1",
        "status": "PASS_TARGET_BLIND_TWO_EXACT_VIEW_CAPACITY",
        "decision": "AUTHORIZE_SYNTHETIC_CALIBRATION_ONLY_FORMAL_TARGET_SEALED",
        "panel_counts": {"admitted": len(rows), "SMOOTH": 29, "TOOTHED": 13, "excluded_UNCERTAIN": len(excluded)},
        "excluded_opaque_ids": sorted(excluded),
        "exact_views": {"PHASE_QUARTILE_SIDE": primary, "PHASE_QUIRE": quire},
        "unscored_diagnostics": {
            "PHASE_QUARTILE": diagnostic(("source_phase", "currier", "hand", "folio_rank_quartile")),
            "PHASE_QUIRE_QUARTILE_SIDE": diagnostic(("source_phase", "currier", "hand", "quire", "folio_rank_quartile", "page_side")),
        },
        "gates": gates,
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path, _ in SELECTIONS} | {str(path.relative_to(ROOT)): sha(path) for path in OBSERVATIONS} | {str(METHOD.relative_to(ROOT)): sha(METHOD)},
        "target_binding": {"path": str(TARGET.relative_to(ROOT)), "published_sha256": TARGET_SHA256, "file_opened_by_capacity_builder": False},
        "panel_sha256": sha(OUT_TSV),
        "access": {"formal_target_rows_accessed": False, "formal_target_scores_computed": False, "literal_or_family_candidates_accessed": False},
        "claim_ceiling": "The admitted visual panel has finite exact capacity under two prespecified nuisance partitions for one already confirmed binary formal regime. This is target-free geometry only and supplies no association, leaf word, plant identity, meaning, plaintext, or translation.",
    }
    assert all(gates.values())
    OUT_JSON.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# LM002 leaf-margin / `cho-che` regime capacity\n\n"
        "Status: **PASS_TARGET_BLIND_TWO_EXACT_VIEW_CAPACITY**.\n\n"
        "After excluding the two prospectively marked `UNCERTAIN` folios, the frozen source-bound panel contains 42 unique physical folios: 29 smooth and 13 toothed. The exact phase × Currier × hand × quartile × page-side partition retains five mobile cells and 13 folios with 108 assignments (`p_min=1/108`). The independent phase × Currier × hand × quire partition retains five mobile cells and 16 folios with 324 assignments (`p_min=1/324`). Both can reach the frozen `.01` tail. The stricter joint quire/quartile/page-side diagnostic has only 36 assignments and is explicitly unscored.\n\n"
        "The formal target table was not opened or parsed. No `cho/che` outcome, rate, count, score, literal form, root, family, or gloss entered this build. This authorizes target-free synthetic calibration only and supplies no association, leaf word, plant identity, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
