#!/usr/bin/env python3
"""Evaluate the frozen Othmer MS 2 catalogue record as an f77 homolog."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
MAN = R / "gdt203_othmer_ms2_source_manifest.tsv"
PARENT = R / "gdt202_result.json"
METHOD = R / "GDT203_OTHMER_MS2_READABLE_APPARATUS_METHOD.md"
AUDIT = R / "GDT203_OTHMER_MS2_SOURCE_AUDIT.md"
REPORT = R / "GDT203_OTHMER_MS2_READABLE_APPARATUS_REPORT.md"
RESULT = R / "gdt203_result.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                      separators=(",", ":")).encode()).hexdigest()


def main():
    with MAN.open(encoding="utf8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 2
    assert all(row["shelfmark"] == "Othmer MS 2" and row["folio"] == "41r" for row in rows)
    exact = sum(row["exact_f77_homolog"] == "1" for row in rows)
    labels = rows[0]["readable_labels"].split("; ")
    assert labels == ["Sublimatoria vasa", "furnus sublimatorum"]
    assert rows[0]["states_or_tools"] == "2" and exact == 0
    status = "READABLE_TWO_TOOL_LEGEND_FOUND_EXACT_F77_HOMOLOG_ABSENT"
    report = f'''# GDT203 — readable apparatus context, not an f77 key

Status: **{status}**.

The institutional catalogue supplies two readable labels on Othmer MS 2,
fol. 41r: `Sublimatoria vasa` and `furnus sublimatorum`.  The manuscript is a
northern Italian alchemical miscellany dated 1450–1475 and includes practical
recipes.

This strengthens the broad historical prior that near-contemporary practical
alchemy could combine readable apparatus drawings, rubrics, and recipes.  It
does **not** satisfy any exact f77-homolog gate beyond being readable technical
apparatus: two tools are documented, versus the required six states, five
relations, and four-output/one-hold topology.  Exact homolog count: **{exact}**.

No Latin label is mapped to a Voynich group or drawing.  This source therefore
adds no word, process value, plaintext, or translation.  No Voynich
transcription, image, or f84r material was accessed.
'''
    REPORT.write_text(report, encoding="utf8")
    result = {
        "schema": "GDT203_OTHMER_MS2_READABLE_APPARATUS_RESULT_V1",
        "status": status,
        "counts": {"institutional_source_records": 2, "readable_external_labels": 2, "documented_tools": 2, "exact_f77_homologs": 0},
        "external_labels": labels,
        "interpretation": "Near-contemporary readable alchemical apparatus context without the f77 ordered topology.",
        "claim_ceiling": "External source-family context only; no Voynich label value, process state, word, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "inputs": {MAN.name: sha(MAN), PARENT.name: sha(PARENT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "documents": {METHOD.name: sha(METHOD), AUDIT.name: sha(AUDIT), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
