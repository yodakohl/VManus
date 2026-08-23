#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_SEVENTEENTH_116_LAYERED_STATEMENTS.tsv", "TWO_HUNDRED_SEVENTEENTH_395_LAYERED_ASTRO_GROUPS.tsv", "TWO_HUNDRED_SEVENTEENTH_142_LAYERED_ASTRO_LOCI.tsv", "TWO_HUNDRED_SEVENTEENTH_READABLE_TEN_PAGES.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    statements = read("TWO_HUNDRED_SEVENTEENTH_116_LAYERED_STATEMENTS.tsv")
    groups = read("TWO_HUNDRED_SEVENTEENTH_395_LAYERED_ASTRO_GROUPS.tsv")
    loci = read("TWO_HUNDRED_SEVENTEENTH_142_LAYERED_ASTRO_LOCI.tsv")
    readable = (OUT / "TWO_HUNDRED_SEVENTEENTH_READABLE_TEN_PAGES.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "116_statements": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "381_prose_events": summary["prose_events"] == 381,
        "395_astro_groups": len(groups) == 395 and len({row["source_id"] for row in groups}) == 395,
        "142_astro_loci": len(loci) == 142,
        "11_plus_3_units": summary["records"] == 11 and summary["astro_units"] == 3,
        "every_statement_annotated": all(row["layered_card_reading"] and row["fluent_owner_expansion_de"] for row in statements),
        "every_astro_group_annotated": all(row["layered_group_reading"] and row["local_owner_expansion_de"] for row in groups),
        "all_legend_classes_present": all(label in readable for label in ("[KERN:", "[ACHSE:", "[PROSA:", "[GANZKARTE:", "[ASTRO-HOMOGRAPH:", "[EXEMPLAR:")),
        "all_units_in_readable": all(f"## {unit}" in readable for unit in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3")),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in readable.lower() and not any("f84" in value.lower() for rows in (statements, groups, loci) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_seventeenth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
