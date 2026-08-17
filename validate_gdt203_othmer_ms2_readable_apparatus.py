#!/usr/bin/env python3
"""Validate the frozen GDT203 source audit and exact-homolog decision."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
RESULT = R / "gdt203_result.json"
MAN = R / "gdt203_othmer_ms2_source_manifest.tsv"
OUT = R / "gdt203_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                      separators=(",", ":")).encode()).hexdigest()


def main():
    result = json.loads(RESULT.read_text())
    with MAN.open(encoding="utf8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    checks = []

    def ck(name, condition):
        checks.append((name, bool(condition)))

    ck("schema", result["schema"] == "GDT203_OTHMER_MS2_READABLE_APPARATUS_RESULT_V1")
    ck("status", result["status"] == "READABLE_TWO_TOOL_LEGEND_FOUND_EXACT_F77_HOMOLOG_ABSENT")
    ck("two_sources", len(rows) == 2)
    ck("institutional", all("INSTITUTIONAL" in row["source_kind"] for row in rows))
    ck("same_object", all(row["shelfmark"] == "Othmer MS 2" and row["folio"] == "41r" for row in rows))
    ck("date_place", rows[0]["date"] == "1450-1475" and rows[0]["place"] == "Northern Italy")
    ck("two_labels", rows[0]["readable_labels"] == "Sublimatoria vasa; furnus sublimatorum")
    ck("two_tools", rows[0]["states_or_tools"] == "2")
    ck("no_relations", rows[0]["ordered_relations"] == "0")
    ck("no_topology", rows[0]["four_output_one_hold"] == "0")
    ck("zero_homolog", sum(row["exact_f77_homolog"] == "1" for row in rows) == result["counts"]["exact_f77_homologs"] == 0)
    ck("counts", result["counts"] == {"institutional_source_records": 2, "readable_external_labels": 2, "documented_tools": 2, "exact_f77_homologs": 0})
    ck("no_f84", not any(result["f84r"].values()) and not any("f84" in " ".join(row.values()).lower() for row in rows))
    for section in ("inputs", "implementation", "documents"):
        for name, digest in result[section].items():
            ck("hash:" + name, sha(R / name) == digest)
    content = dict(result)
    stored = content.pop("result_content_sha256")
    ck("content_hash", csha(content) == stored)
    bad = [name for name, passed in checks if not passed]
    validation = {"schema": "GDT203_VALIDATION_V1", "status": "PASS" if not bad else "FAIL", "checks_passed": sum(p for _, p in checks), "checks_total": len(checks), "failed": bad, "result_sha256": sha(RESULT), "scope": "Independent manifest, readable-label, topology-gate, seal-flag, and hash validation; no Voynich label is decoded."}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps(validation, sort_keys=True))
    raise SystemExit(bool(bad))


if __name__ == "__main__":
    main()
