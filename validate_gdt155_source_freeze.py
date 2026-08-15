#!/usr/bin/env python3
"""Independent structural validator for the GDT155 blinded source freeze."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LINES = ROOT / "gdt155_blinded_diplomatic.tsv"
SITES = ROOT / "gdt155_blinded_abbreviation_sites.tsv"
RESULT = ROOT / "gdt155_source_freeze.json"
OUT = ROOT / "gdt155_source_freeze_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"check": name, "pass": bool(condition), "detail": detail})
    assert condition, (name, detail)


result = json.loads(RESULT.read_text(encoding="utf-8"))
lines = read(LINES)
sites = read(SITES)
line_ids = {row["line_id"] for row in lines}
site_ids = {row["site_id"] for row in sites}
records = {(row["corpus"], row["record_id"]) for row in lines}
counts = result["counts"]
check("schema", result["schema"] == "GDT155_BLIND_SOURCE_FREEZE_V1", result["schema"])
check("status", result["status"] == "BLINDED_DIPLOMATIC_SURFACE_FROZEN_BEFORE_FULL_UNBLIND", result["status"])
check("line_count", len(lines) == counts["lines"], len(lines))
check("site_count", len(sites) == counts["abbreviation_sites"], len(sites))
check("record_count", len(records) == counts["records"], len(records))
check("unique_lines", len(line_ids) == len(lines), len(line_ids))
check("unique_sites", len(site_ids) == len(sites), len(site_ids))
check("site_line_join", all(row["line_id"] in line_ids for row in sites), sum(row["line_id"] in line_ids for row in sites))
check("site_record_join", all((row["corpus"], row["record_id"]) in records for row in sites), len(sites))
check("line_site_arithmetic", sum(int(row["abbreviation_site_count"]) for row in lines) == len(sites), len(sites))
check("ste1_sites", sum(row["corpus"] == "STE1" for row in sites) == 33, sum(row["corpus"] == "STE1" for row in sites))
check("nuremberg_records", len({row["record_id"] for row in lines if row["corpus"] == "NUREMBERG"}) == 3176, len({row["record_id"] for row in lines if row["corpus"] == "NUREMBERG"}))
check("no_expansion_columns", not any("expan" in key or key in {"regularized", "meaning", "gloss"} for key in lines[0] for key in [key.lower()]), list(lines[0]))
check("no_tei_expansion_markup", not any("<ex" in row["diplomatic_bare"] or "<ex" in row["diplomatic_marked"] for row in lines), len(lines))
check("markers_match_counts", all(row["diplomatic_marked"].count("¤") == int(row["abbreviation_site_count"]) for row in lines), len(lines))
check("external_corpora_only", {row["corpus"] for row in lines + sites} == {"STE1", "NUREMBERG"}, sorted({row["corpus"] for row in lines + sites}))
check("no_voynich_locator_schema", not ({"locus", "folio", "physical_folio", "voynich_page"} & set(lines[0])), list(lines[0]))
check("line_hash", sha(LINES) == result["blinded_outputs"][LINES.name], sha(LINES))
check("site_hash", sha(SITES) == result["blinded_outputs"][SITES.name], sha(SITES))
copy = dict(result); expected = copy.pop("freeze_content_sha256")
check("content_hash", csha(copy) == expected, expected)
check("truth_not_exported", result["truth_exported"] is False, result["truth_exported"])
validation = {
    "schema": "GDT155_SOURCE_FREEZE_VALIDATION_V1",
    "status": f"PASS_{len(checks)}_CHECK_BLIND_FREEZE_INTEGRITY",
    "checks": checks,
    "result_sha256": sha(RESULT),
    "note": "Validates published blind artifacts and commitments without reading the external expansion truth.",
}
OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(validation["status"])
