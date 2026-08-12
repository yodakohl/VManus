#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions/results"
PANEL = BASE / "lm002_leaf_margin_cho_che_capacity_panel.tsv"
RESULT = BASE / "lm002_leaf_margin_cho_che_capacity.json"
OUT = BASE / "lm002_leaf_margin_cho_che_capacity_validation.json"


def reconstruct(rows: list[dict[str, str]], field: str) -> tuple[int, int, int]:
    cells = defaultdict(list)
    for row in rows: cells[row[field]].append(row)
    mobile = [values for values in cells.values() if len({row["leaf_margin_state"] for row in values}) == 2]
    orbit = math.prod(math.comb(len(values), sum(row["leaf_margin_state"] == "TOOTHED" for row in values)) for values in mobile)
    return len(mobile), sum(map(len, mobile)), orbit


def main() -> None:
    checks = []
    rows = list(csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t"))
    assert len(rows) == 42 and len({row["physical_folio"] for row in rows}) == 42
    checks.append("exact_42_unique_physical_folios")
    assert Counter(row["leaf_margin_state"] for row in rows) == {"SMOOTH": 29, "TOOTHED": 13}
    checks.append("exact_visual_state_counts")
    for row in rows:
        assert row["page_side"] == row["page"][-1]
        assert row["phase_quartile_side_cell"] == "|".join(row[key] for key in ("source_phase", "currier", "hand", "folio_rank_quartile", "page_side"))
        assert row["phase_quire_cell"] == "|".join(row[key] for key in ("source_phase", "currier", "hand", "quire"))
    checks.append("exact_nuisance_cell_derivation")
    assert reconstruct(rows, "phase_quartile_side_cell") == (5, 13, 108)
    checks.append("primary_exact_orbit")
    assert reconstruct(rows, "phase_quire_cell") == (5, 16, 324)
    checks.append("quire_exact_orbit")
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert stored["status"] == "PASS_TARGET_BLIND_TWO_EXACT_VIEW_CAPACITY"
    assert stored["decision"] == "AUTHORIZE_SYNTHETIC_CALIBRATION_ONLY_FORMAL_TARGET_SEALED"
    assert stored["panel_sha256"] == hashlib.sha256(PANEL.read_bytes()).hexdigest()
    assert all(stored["gates"].values())
    checks.append("canonical_capacity_decision_and_binding")
    assert stored["target_binding"]["file_opened_by_capacity_builder"] is False
    assert stored["access"] == {"formal_target_rows_accessed": False, "formal_target_scores_computed": False, "literal_or_family_candidates_accessed": False}
    checks.append("formal_target_access_seal")
    assert stored["unscored_diagnostics"]["PHASE_QUIRE_QUARTILE_SIDE"]["assignments"] == 36
    assert stored["unscored_diagnostics"]["PHASE_QUIRE_QUARTILE_SIDE"]["minimum_inclusive_p"] > .01
    checks.append("strict_joint_partition_correctly_unscored")
    out = {
        "experiment": "LM002_LEAF_MARGIN_CHO_CHE_REGIME_CAPACITY_VALIDATION",
        "status": "PASS_8_CHECK_INDEPENDENT_TARGET_BLIND_RECONSTRUCTION",
        "check_count": len(checks), "checks": checks,
        "validated_result_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(),
        "formal_target_table_opened_by_validator": False,
        "claim_ceiling": stored["claim_ceiling"],
    }
    OUT.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
