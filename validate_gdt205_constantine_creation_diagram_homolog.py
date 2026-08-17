#!/usr/bin/env python3
"""Validate GDT205 source facts, topology decision, seal, and bindings."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt205_result.json"
MANIFEST = ROOT / "gdt205_constantine_creation_diagram.tsv"
OUT = ROOT / "gdt205_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def main():
    result = json.loads(RESULT.read_text(encoding="utf8"))
    with MANIFEST.open(encoding="utf8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    checks = []

    def check(name, condition):
        checks.append((name, bool(condition)))

    check("schema", result["schema"] == "GDT205_CONSTANTINE_CREATION_DIAGRAM_HOMOLOG_RESULT_V1")
    check("status", result["status"] == "READABLE_SIX_DAY_METAL_CREATION_ANALOGY_FOUND_EXACT_F77_HOMOLOG_ABSENT")
    check("three_source_records", len(rows) == 3)
    check("unique_ids", {row["record_id"] for row in rows} == {"CP01", "CP02", "CP03"})
    check("scholarly_source", all(row["scholarly_source_url"] == "https://www.hyle.org/journal/issues/9-2/obrist.htm" for row in rows))
    check("primary_witness", any("Ferguson 104" in row["witness"] and row["folio"] == "45v" and row["witness_date"] == "1361" for row in rows))
    check("adaptation_witness", any("MS 2372" in row["witness"] and row["folio"] == "46vb-47ra" for row in rows))
    check("seven_not_six", "seven planet/metal circle segments" in rows[0]["source_bound_structure"] and rows[0]["six_state_diagram"] == "0")
    check("zero_exact", not any(row["exact_f77_homolog"] == "1" for row in rows))
    check("zero_five_relations", not any(row["five_adjacent_relations"] == "1" for row in rows))
    check("zero_output_mask", not any(row["four_active_one_hold"] == "1" for row in rows))
    check("counts", result["counts"] == {"source_records": 3, "independent_textual_traditions": 1, "manuscript_witnesses": 2, "six_day_metal_creation_claims": 1, "six_state_diagrams": 0, "exact_f77_homologs": 0})
    check("critical_distinction", result["critical_distinction"]["rendered_primary_topology"].startswith("SEVEN_PLANET_METAL_SEGMENTS"))
    check("no_f84_flags", not any(result["f84"].values()))
    check("no_f84_rows", not any("f84" in " ".join(row.values()).lower() for row in rows))
    for section in ("inputs", "implementation", "documents"):
        for filename, digest in result[section].items():
            check("hash:" + filename, sha(ROOT / filename) == digest)
    body = dict(result)
    stored = body.pop("result_content_sha256")
    check("content_hash", content_sha(body) == stored)
    failed = [name for name, passed in checks if not passed]
    validation = {
        "schema": "GDT205_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(passed for _, passed in checks),
        "checks_total": len(checks),
        "failed": failed,
        "result_sha256": sha(RESULT),
        "scope": "Independent retained-row, witness, rendered-topology, exact-gate, seal-flag, and hash validation; no Voynich value is inferred.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps(validation, sort_keys=True))
    raise SystemExit(bool(failed))


if __name__ == "__main__":
    main()
