#!/usr/bin/env python3
"""Compact reconstruction of DRI002 recorded judgments and stop arithmetic."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
PRODUCER = BASE / "audit_dri002_discordant_cell_role_capacity_result.py"
SELECTION = RES / "dri002_discordant_cell_role_capacity_selection.json"
RESULT = RES / "dri002_discordant_cell_role_capacity_result.json"
REPORT = RES / "dri002_discordant_cell_role_capacity_result_report.md"
OUT = RES / "dri002_discordant_cell_role_capacity_result_validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    r = json.loads(RESULT.read_text())
    selection = json.loads(SELECTION.read_text())
    obs = r["observations"]
    cells = {x["cell_id"]: x for x in r["cells"]}
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "exact_selected_order": [x["page"] for x in obs] == [x["page"] for x in selection["rows"]] == ["f77r", "f78r", "f82v", "f76v", "f78v", "f79r", "f79v", "f81r", "f84v"],
        "all_image_hashes_bound": all(len(x["review_image_sha256"]) == 64 for x in obs),
        "one_eight_role_partition": Counter(x["role"] for x in obs) == Counter({"OBJECT_WITH_PROSE": 8, "PROSE_DOMINANT": 1}) == Counter({k: v for k, v in r["new_role_counts"].items() if v}),
        "all_low_uncertainty": all(x["uncertainty"] == "LOW" for x in obs),
        "drc02_exact_support": cells["DRC02"]["physical_folios_by_role"] == {"OBJECT_WITH_PROSE": ["f77", "f78", "f82"], "REPEATED_OWNED_RECORDS": ["f84"]} and cells["DRC02"]["passes_role_mobility_gate"] is False,
        "drc03_exact_support": cells["DRC03"]["physical_folios_by_role"] == {"OBJECT_WITH_PROSE": ["f75", "f78", "f79", "f81", "f84"], "PROSE_DOMINANT": ["f76", "f80"]} and cells["DRC03"]["passes_role_mobility_gate"] is True,
        "both_cell_gate_stops": r["gates"] == {"DRC02_replicated_role_mobility": False, "DRC03_replicated_role_mobility": True, "both_cells_pass": False},
        "formal_access_and_scoring_sealed": r["access"]["transcription_identity_or_formal_features_opened_after_selection"] is False and r["access"]["structural_or_semantic_association_scored"] is False,
        "stored_stop_and_ceiling": r["status"] == "STOP_ONE_OF_TWO_CELLS_LACKS_REPLICATED_ROLE_MOBILITY" and r["decision"] == "DO_NOT_OPEN_OR_SCORE_FORMAL_ROLE_ASSOCIATION" and "translation" in r["claim_ceiling"],
        "report_exact_summary": REPORT.is_file() and "DRC02 fails" in REPORT.read_text() and "DRC03 passes" in REPORT.read_text(),
    }
    if not all(checks.values()):
        raise SystemExit({k: v for k, v in checks.items() if not v})
    out = {
        "experiment": "DRI002_DISCORDANT_CELL_ROLE_CAPACITY_RESULT_VALIDATION",
        "schema": "DRI002_RESULT_VALIDATION_V1",
        "status": "PASS_11_CHECK_VISUAL_BINDING_AND_STOP_RECONSTRUCTION",
        "check_count": len(checks), "checks": list(checks),
        "producer_sha256": sha256(PRODUCER), "validated_result_sha256": sha256(RESULT),
        "reconstructed": {"new_roles": {"PROSE_DOMINANT": 1, "OBJECT_WITH_PROSE": 8}, "DRC02_pass": False, "DRC03_pass": True, "both_pass": False},
        "visual_judgments_independently_reperformed": False,
        "claim_ceiling": "Validation reconstructs recorded native-visual judgments and capacity arithmetic; it supplies no text association word meaning plaintext or translation.",
    }
    OUT.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
