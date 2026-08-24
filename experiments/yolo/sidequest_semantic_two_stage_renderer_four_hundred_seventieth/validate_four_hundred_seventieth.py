#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    bodies = read("FOUR_HUNDRED_SEVENTIETH_173_PROSE_BODY_LEXICON.tsv")
    prose = read("FOUR_HUNDRED_SEVENTIETH_381_PROSE_TWO_STAGE_WRITER.tsv")
    astro = read("FOUR_HUNDRED_SEVENTIETH_395_ASTRO_NAMESPACE_RENDERER.tsv")
    exceptions = read("FOUR_HUNDRED_SEVENTIETH_RENDERER_EXCEPTIONS.tsv")
    combined = read("FOUR_HUNDRED_SEVENTIETH_776_TWO_STAGE_SURFACE_WRITER.tsv")
    prose_rules = read("FOUR_HUNDRED_SEVENTIETH_PROSE_WRAPPER_RULEBOOK.tsv")
    astro_rules = read("FOUR_HUNDRED_SEVENTIETH_ASTRO_RENDERER_RULEBOOK.tsv")
    checks = {
        "bodies_173": len(bodies) == 173,
        "prose_381": len(prose) == 381,
        "astro_395": len(astro) == 395,
        "combined_776": len(combined) == 776,
        "prose_exact_359": sum(row["exact_surface_match"] == "YES" for row in prose) == 359,
        "astro_exact_373": sum(row["exact_surface_match"] == "YES" for row in astro) == 373,
        "exceptions_44": len(exceptions) == 44,
        "combined_exact_732": sum(row["exact_without_exception"] == "YES" for row in combined) == 732,
        "exception_deck_exact_776": all(row["exact_with_exception_deck"] == "YES" for row in combined),
        "wrapper_inventory_8": {row["observed_wrapper"] for row in prose} == {"NONE", "q", "che", "d", "ch", "sh", "s", "t"},
        "body_surface_stable": len({row["body_surface"] for row in bodies}) == 173,
        "prose_event_order": [row["event_id"] for row in prose] == [f"E{n:03d}" for n in range(1, 382)],
        "combined_partition": [sum(row["domain"] == domain for row in combined) for domain in ("PROSE", "ASTRO")] == [381, 395],
        "rules_present": bool(prose_rules) and bool(astro_rules),
        "fixed_pages": {row["page"] for row in combined} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in combined),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
