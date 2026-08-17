#!/usr/bin/env python3
"""Summarize the source-frozen Constantine creation-diagram homolog audit."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "gdt205_constantine_creation_diagram.tsv"
PARENT = ROOT / "gdt204_result.json"
METHOD = ROOT / "GDT205_CONSTANTINE_CREATION_DIAGRAM_HOMOLOG_METHOD.md"
REPORT = ROOT / "GDT205_CONSTANTINE_CREATION_DIAGRAM_HOMOLOG_REPORT.md"
RESULT = ROOT / "gdt205_result.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def main():
    with MANIFEST.open(encoding="utf8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 3
    assert {row["record_id"] for row in rows} == {"CP01", "CP02", "CP03"}
    exact = sum(row["exact_f77_homolog"] == "1" for row in rows)
    six_cell = sum(row["six_state_diagram"] == "1" for row in rows)
    assert exact == 0 and six_cell == 0
    status = "READABLE_SIX_DAY_METAL_CREATION_ANALOGY_FOUND_EXACT_F77_HOMOLOG_ABSENT"
    result = {
        "schema": "GDT205_CONSTANTINE_CREATION_DIAGRAM_HOMOLOG_RESULT_V1",
        "status": status,
        "counts": {
            "source_records": len(rows),
            "independent_textual_traditions": 1,
            "manuscript_witnesses": 2,
            "six_day_metal_creation_claims": 1,
            "six_state_diagrams": six_cell,
            "exact_f77_homologs": exact,
        },
        "critical_distinction": {
            "conceptual_count": "SIX_METALS_IN_SIX_CREATION_DAYS",
            "rendered_primary_topology": "SEVEN_PLANET_METAL_SEGMENTS_PLUS_LOWER_COSMOLOGICAL_SEGMENTS",
            "direct_transfer": "REJECTED",
        },
        "interpretation": "A readable medieval alchemical source uses ordered labelled diagrams and tables, but its six-day explanatory count is not the diagram's cell count and cannot key f77.",
        "claim_ceiling": "Historical architecture/source-family prior only; no Voynich group, metal, planet, day, process, word, plaintext, meaning, or translation.",
        "f84": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "inputs": {MANIFEST.name: sha(MANIFEST), PARENT.name: sha(PARENT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = content_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
