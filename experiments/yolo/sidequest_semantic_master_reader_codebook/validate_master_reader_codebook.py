#!/usr/bin/env python3
"""Validate the creative master-card reader and four-scribe round trip."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"
COPYSHOP = ROOT / "experiments/yolo/sidequest_semantic_four_scribe_copyshop"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    master = rows(OUT / "MASTER_173_CARD_DICTIONARY.tsv")
    surfaces = rows(OUT / "SURFACE_230_READER_KEY.tsv")
    statements = rows(OUT / "MASTER_116_STATEMENT_EDITION.tsv")
    reverse = rows(OUT / "FOUR_SCRIBE_464_REVERSE_READINGS.tsv")
    exercises = rows(OUT / "APPRENTICE_64_READER_TESTS.tsv")
    source_cards = rows(PROSE / "CLOSED_173_CARD_DICTIONARY.tsv")
    source_events = rows(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    source_phrases = rows(PROSE / "CLOSED_116_PHRASES.tsv")
    source_copies = rows(COPYSHOP / "FOUR_HAND_116_STATEMENT_RENDERINGS.tsv")

    check("173_master_cards", len(master) == len(source_cards) == 173, len(master))
    check("master_ids_unique", len({row["master_card_id"] for row in master}) == 173, "unique")
    check("tuple_ids_exact", {row["joint_tuple_id"] for row in master} == {row["joint_tuple_id"] for row in source_cards}, "same")
    expected_surfaces = {(row["joint_tuple_id"], surface) for row in source_cards for surface in row["surface_family"].split("|")}
    actual_surfaces = {(row["joint_tuple_id"], row["visible_surface"]) for row in surfaces}
    check("230_surface_rows", len(surfaces) == len(expected_surfaces) == 230, len(surfaces))
    check("surface_rows_exact", actual_surfaces == expected_surfaces, "same")
    check("surface_strings_globally_unique", len({row["visible_surface"] for row in surfaces}) == 230, len({row["visible_surface"] for row in surfaces}))
    check("direct_lookup_flags", all(row["direct_lookup_unique"] == "YES" and row["context_needed_for_card_identity"] == "NO" for row in surfaces), "all")
    check("master_heads_registered", all(row["master_head_form"] in row["registered_surface_family"].split("|") for row in master), "all")
    check("master_meanings_nonempty", all(row["short_meaning_de"].strip() for row in master), "all")
    check("master_components_nonempty", all(row["component_reading"].strip() for row in master), "all")

    check("116_statement_rows", len(statements) == len(source_phrases) == 116, len(statements))
    check("381_statement_events", sum(int(row["event_count"]) for row in statements) == len(source_events) == 381, sum(int(row["event_count"]) for row in statements))
    check("statement_ids_exact", {row["statement_id"] for row in statements} == {row["statement_id"] for row in source_phrases}, "same")
    check("statement_reverse_status", all(row["reverse_reading_status"] == "DIRECT_SURFACE_TO_MASTER_CARD_TO_MEANING" for row in statements), "all")
    check("statement_lengths_align", all(len(row["original_surface_sequence"].split()) == len(row["master_head_sequence"].split()) == len(row["master_card_sequence"].split()) == int(row["event_count"]) for row in statements), "all")

    check("464_reverse_rows", len(reverse) == len(source_copies) == 464, len(reverse))
    check("four_per_statement", all(count == 4 for count in Counter(row["statement_id"] for row in reverse).values()), "all")
    check("all_tuple_roundtrips", all(row["tuple_roundtrip"] == "PASS" for row in reverse), "all")
    check("all_meaning_roundtrips", all(row["meaning_roundtrip"] == "PASS" for row in reverse), "all")
    check("roundtrip_context_free", all(row["context_used_for_card_identity"] == "NO" for row in reverse), "all")
    check("64_exercise_tests", len(exercises) == 64, len(exercises))
    check("all_exercise_tuple_roundtrips", all(row["tuple_roundtrip"] == "PASS" for row in exercises), "all")
    check("all_exercise_meaning_roundtrips", all(row["meaning_roundtrip"] == "PASS" for row in exercises), "all")

    roles = Counter(row["surface_role"] for row in surfaces)
    check("q_variants_present", roles["Q_CELL_VARIANT"] > 0, roles)
    check("s_variants_present", roles["S_LINE_VARIANT"] > 0, roles)
    check("other_allographs_present", roles["OTHER_REGISTERED_ALLOGRAPH"] > 0, roles)

    pocket = (OUT / "MASTER_READER_POCKETBOOK.md").read_text(encoding="utf-8")
    check("all_master_heads_in_pocketbook", all(f"`{row['master_head_form']}`" in pocket for row in master), "all")
    edition = (OUT / "ELEVEN_RECORD_MASTER_READING.md").read_text(encoding="utf-8")
    check("all_statements_in_readable_edition", all(f"### {row['statement_id']}" in edition for row in statements), "all")
    report = (OUT / "MASTER_READER_CODEBOOK_REPORT.md").read_text(encoding="utf-8")
    check("creative_caveat", "kreative Arbeitstheorie" in report, "present")

    content_names = [
        "MASTER_173_CARD_DICTIONARY.tsv", "SURFACE_230_READER_KEY.tsv", "MASTER_116_STATEMENT_EDITION.tsv",
        "FOUR_SCRIBE_464_REVERSE_READINGS.tsv", "APPRENTICE_64_READER_TESTS.tsv",
        "MASTER_READER_POCKETBOOK.md", "ELEVEN_RECORD_MASTER_READING.md", "MASTER_READER_CODEBOOK_REPORT.md",
    ]
    content = "\n".join((OUT / name).read_text(encoding="utf-8", errors="replace") for name in content_names)
    sealed = re.compile(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])")
    check("sealed_pages_absent", sealed.search(content) is None, "absent")

    before = {name: digest(OUT / name) for name in content_names}
    subprocess.run([sys.executable, str(OUT / "build_master_reader_codebook.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = {name: digest(OUT / name) for name in content_names}
    check("deterministic_rebuild", before == after, "byte identical")

    passed = all(bool(row["pass"]) for row in checks)
    result = {
        "status": "PASS" if passed else "FAIL",
        "checks_passed": sum(bool(row["pass"]) for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "counts": {
            "master_cards": len(master), "registered_surfaces": len(surfaces), "statements": len(statements),
            "source_events": len(source_events), "four_scribe_roundtrips": len(reverse), "exercise_roundtrips": len(exercises),
            "surface_role_counts": dict(roles),
        },
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        for row in checks:
            if not row["pass"]:
                print(f"FAIL {row['check']}: {row['detail']}")
        raise SystemExit(1)
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
