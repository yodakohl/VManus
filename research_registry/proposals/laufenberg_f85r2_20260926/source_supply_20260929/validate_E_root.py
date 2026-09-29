#!/usr/bin/env python3
"""Check complete-context bookkeeping, never historical meaning."""
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main():
    result = json.loads((HERE / "E_ROOT_RESULT.json").read_text())
    expected = []
    for item, key in zip(result["sources"], ("groups", "units")):
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
        for unit in json.loads(path.read_text())[key]:
            assert unit["locus"].split(".")[0] in {"f68r2", "f89v1"}
            for index, group in enumerate(unit["groups"], 1):
                expected.append({
                    "edition": unit["edition"], "locus": unit["locus"],
                    "group_index": str(index), "raw_group": group,
                    "sky_candidate": "SUN (hypothesis)" if group == "okoaiin" else "UNRESOLVED",
                    "metal_candidate": "SOL/GOLD (hypothesis)" if group == "okoaiin" else "UNRESOLVED",
                    "bound_relation": "NONE",
                })
    with (ROOT / result["table"]).open() as stream:
        actual = list(csv.DictReader(stream, delimiter="\t"))
    assert actual == expected
    assert len(actual) == result["row_count"] == 288
    assert sum(r["raw_group"] == "okoaiin" for r in actual) == result["conditional_named_positions"] == 6
    assert result["unresolved_positions"] == 282
    assert result["complete_candidate_readings"] == result["meaning_discriminating_target_relations"] == 0
    profile = json.loads((HERE / "E_WORD_PROFILES.json").read_text())
    assert profile["source_receipt"]["inputs"]["selector_count"] == 179
    assert not any(s.startswith("f84") for s in profile["source_receipt"]["inputs"]["selectors"])
    counts = {p["form"]: [p["editions"][e]["count"] for e in ("ZL3b", "IT2a", "RF1b")] for p in profile["profiles"]}
    assert counts["okoaiin"] == [1, 1, 1]
    assert counts["okar"] == [118, 113, 109]
    assert counts["okor"] == [24, 25, 18]
    out = {"status": "PASS", "rows_replayed": len(actual), "meaning_validated": False,
           "scope": "same-author separate executable checks saved source identity, all groups, profile scope and candidate accounting"}
    (HERE / "E_ROOT_VALIDATION.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
