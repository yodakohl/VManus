#!/usr/bin/env python3
"""Independent retained-artifact validation for GDT212."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

R = Path(__file__).resolve().parent
RESULT = R / "gdt212_result.json"
VALIDATION = R / "gdt212_validation.json"
VISUAL = R / "gdt212_morgan_visual_role_inventory.tsv"
TEXT = R / "gdt211_de_balneis_entry_inventory.tsv"
SCORES = R / "gdt212_visual_text_role_scores.tsv"
COUNTER = R / "gdt212_counterexamples.tsv"
PAIRS = (
    ("ACCESS_OR_SETTING", "access_or_setting", "LOCATION_ACCESS", "location_access"),
    ("NON_GENERIC_WATER_SYSTEM", "non_generic_water_system", "HYDRAULIC_PHYSICAL", "hydraulic_physical"),
    ("SPECIFIC_USE_ACTION", "specific_use_action", "PROCEDURE_CAUTION", "procedure_caution"),
    ("BED_OR_DEPARTURE_NARRATIVE", "bed_or_departure_narrative", "OUTCOME_TESTIMONY", "outcome_testimony"),
)
checks: list[str] = []


def ok(name: str, value: bool) -> None:
    assert value, name
    checks.append(name)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def fisher_positive(a: int, b: int, c: int, d: int) -> float:
    n = a + b + c + d
    row = a + b
    col = a + c
    denominator = math.comb(n, row)
    return sum(math.comb(col, x) * math.comb(n - col, row - x) / denominator for x in range(a, min(row, col) + 1))


result = json.loads(RESULT.read_text(encoding="utf-8"))
content = result.pop("result_content_sha256")
ok("content_hash", csha(result) == content)
result["result_content_sha256"] = content
ok("status", result["status"] == "SETTING_HYDRAULICS_WEAKLY_VISUALLY_GROUNDED_INDICATION_FIELDS_NOT_RECOVERED")
ok("voynich_not_scored", result["voynich_scored"] is False and result["semantic_mapping"] == "NONE")
ok("f84", not any(result["f84"].values()))
for group in ("inputs", "outputs", "documents", "implementation"):
    for name, digest in result[group].items():
        ok(f"{group}:{name}", sha(R / name) == digest)

visual = read(VISUAL)
text = {int(row["entry_number"]): row for row in read(TEXT) if row["record_class"] == "BATH_RECORD"}
ok("visual_rows", len(visual) == 32)
ok("text_rows", len(text) == 32)
ok("exact_entry_join", {int(row["entry_number"]) for row in visual} == set(text))
ok("unique_folios", len({row["morgan_folio"] for row in visual}) == 32)
ok("human_provenance", all(row["annotation_provenance"] == "EXISTING_HUMAN_ANNOTATION_NORMALIZED" for row in visual))
ok("official_urls", all(row["catalogue_url"] == f"https://ica.themorgan.org/manuscript/page/{n}/77063" for row, n in zip(visual, list(range(1, 31)) + [32, 36])))
ok("no_f84_strings", not any("f84" in value for row in visual for value in row.values()))
joined = [{**row, **text[int(row["entry_number"])]} for row in visual]

published = {(row["visual_feature"], row["text_role"]): row for row in read(SCORES)}
ok("score_rows", len(published) == 4)
reconstructed = {}
for visual_name, feature, role_name, role in PAIRS:
    a = sum(int(row[feature]) and int(row[role]) for row in joined)
    b = sum(int(row[feature]) and not int(row[role]) for row in joined)
    c = sum(not int(row[feature]) and int(row[role]) for row in joined)
    d = sum(not int(row[feature]) and not int(row[role]) for row in joined)
    risk = a / (a + b) - c / (c + d)
    p = fisher_positive(a, b, c, d)
    row = published[visual_name, role_name]
    ok(f"table:{visual_name}", [int(row[key]) for key in ("feature_and_role", "feature_without_role", "no_feature_with_role", "neither")] == [a, b, c, d])
    ok(f"risk:{visual_name}", abs(float(row["risk_difference"]) - risk) < 1e-11)
    ok(f"p:{visual_name}", abs(float(row["one_sided_fisher_p"]) - p) < 1e-11)
    ok(f"adjusted:{visual_name}", abs(float(row["bonferroni_four_p"]) - min(1.0, 4 * p)) < 1e-11)
    reconstructed[visual_name] = {"a": a, "b": b, "c": c, "d": d, "risk": risk, "p": p}

ok("visual_counts", result["visual_feature_counts"] == {feature.upper(): sum(int(row[feature]) for row in joined) for feature in ("access_or_setting", "non_generic_water_system", "specific_use_action", "body_condition_cue", "bed_or_departure_narrative")})
ok("text_counts", result["text_role_counts"] == {role.upper(): sum(int(row[role]) for row in joined) for role in ("location_access", "hydraulic_physical", "indication", "procedure_caution", "outcome_testimony")})
ok("indication_capacity", result["text_role_counts"]["INDICATION"] == 32 and result["visual_feature_counts"]["BODY_CONDITION_CUE"] == 14)
ok("counterexamples", len(read(COUNTER)) == 6)

validation = {
    "schema": "GDT212_DE_BALNEIS_VISUAL_TEXT_GROUNDING_VALIDATION_V1",
    "status": "PASS",
    "checks_passed": len(checks),
    "checks": checks,
    "reconstructed_pairs": reconstructed,
    "result_sha256": sha(RESULT),
    "result_content_sha256": content,
    "validator_sha256": sha(Path(__file__)),
    "voynich_scored": False,
    "f84_accessed": False,
}
VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": "PASS", "checks": len(checks), "rows": len(visual)}, sort_keys=True))
