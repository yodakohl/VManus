#!/usr/bin/env python3
"""Validate GDT206 visual provenance, bridge decision, and bindings."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "gdt206_arched_channel_visual_inventory.tsv"
RESULT = ROOT / "gdt206_result.json"
OUT = ROOT / "gdt206_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main():
    result = json.loads(RESULT.read_text(encoding="utf8"))
    with MANIFEST.open(encoding="utf8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    checks = []

    def check(name, condition):
        checks.append((name, bool(condition)))

    check("schema", result["schema"] == "GDT206_ARCHED_CHANNEL_REFERENT_AUDIT_RESULT_V1")
    check("status", result["status"] == "ARCHED_CHANNEL_MOTIF_RECURS_SINGULAR_REFERENT_BRIDGE_ABSENT")
    check("two_rows", len(rows) == 2)
    check("pages", {row["page"] for row in rows} == {"f82v", "f83r"})
    check("folios", {row["physical_folio"] for row in rows} == {"f82", "f83"})
    check("official_canvases", {(row["page"], row["canvas_id"]) for row in rows} == {("f82v", "1006223"), ("f83r", "1006224")})
    check("official_urls", all(row["official_iiif_url"].startswith("https://collections.library.yale.edu/iiif/2/") for row in rows))
    check("digest_shape", all(len(row["inspected_derivative_sha256"]) == 64 for row in rows))
    check("direct_provenance", all("AI_DIRECT_VISUAL_OBSERVATION" in row["provenance"] for row in rows))
    check("different_component_counts", {row["component_count"] for row in rows} == {"1", "2"})
    check("different_endpoint_structures", len({row["endpoint_structure"] for row in rows}) == 2)
    check("zero_owner", not any(row["singular_text_owner"] == "1" for row in rows))
    check("zero_eligible", not any(row["bridge_eligible"] == "1" for row in rows))
    check("formal_unqueried", not any(result["formal_payload"].values()))
    check("no_f84", not any(result["f84"].values()) and not any("f84" in " ".join(row.values()).lower() for row in rows))
    check("counts", result["counts"] == {"physical_folios": 2, "direct_visual_observations": 2, "broad_motif_recurrences": 1, "singular_text_owners": 0, "bridge_eligible_occurrences": 0})
    for section in ("inputs", "implementation", "documents"):
        for filename, digest in result[section].items():
            check("hash:" + filename, sha(ROOT / filename) == digest)
    body = dict(result)
    stored = body.pop("result_content_sha256")
    check("content_hash", content_sha(body) == stored)
    failed = [name for name, passed in checks if not passed]
    validation = {
        "schema": "GDT206_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(passed for _, passed in checks),
        "checks_total": len(checks),
        "failed": failed,
        "result_sha256": sha(RESULT),
        "scope": "Independent retained-row, page/canvas, geometry-class, bridge-gate, formal-access, seal, and hash validation; visual judgments remain AI direct observations.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps(validation, sort_keys=True))
    raise SystemExit(bool(failed))


if __name__ == "__main__":
    main()
