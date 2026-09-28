#!/usr/bin/env python3
"""Validate packet completeness and decision logic, not human visual truth."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def main() -> int:
    obs = json.loads((BASE / "src/OBSERVATIONS.json").read_text())
    source = json.loads((BASE / "src/SOURCE.json").read_text())
    result = json.loads((BASE / "artifacts/RESULT.json").read_text())
    outer = obs["outer_text_sectors_clockwise_from_top"]
    assert [x["slot"] for x in outer] == list(range(16))
    assert obs["radial_text_loci_from_prior_GDT1068"]["locus_numbers"] == list(range(21, 43))
    assert obs["radial_text_loci_from_prior_GDT1068"]["all_panel_regions_inspected"]
    assert obs["colored_spokes"]["count"] == 12
    assert result["outer_sectors_inspected"] == 16
    assert result["radial_loci_accounted_for"] == 22
    assert result["painted_spokes"] == 12
    assert result["outer_direct_leaders"] == sum(x["unique_ink_leader_to_wind"] for x in outer)
    assert result["decision"] == ("BOTH_GATES_VISIBLE" if result["orientation_gate"] and result["singular_owner_gate"] else "NO_LEXICAL_REOPENING")
    assert source["method_sha256_before_pixels"] == hashlib.sha256((BASE / "METHOD.md").read_bytes()).hexdigest()
    assert source["admission_sha256_before_pixels"] == hashlib.sha256((BASE / "src/PAGE_ADMISSIONS.tsv").read_bytes()).hexdigest()
    assert source["canvas_label"] == "69r" and "1006198" in source["canvas_id"]
    runtime_names = {"full_image": "f69r_1006198.jpg", "panel_detail": "f69r_panel_detail.jpg", "center_detail": "f69r_center_detail.jpg"}
    for stem, filename in runtime_names.items():
        path = BASE / "runtime" / filename
        if path.exists():
            assert hashlib.sha256(path.read_bytes()).hexdigest() == source[f"{stem}_sha256"]
    out = {"status": "PASS", "scope": "completeness, hash and decision logic only; visual truth not machine-validated", "decision": result["decision"]}
    (BASE / "artifacts/VALIDATION.json").write_text(json.dumps(out, indent=2) + "\n")
    print(out["status"])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
