#!/usr/bin/env python3
"""Validate distinct creative teaching glosses across the 173 master cards."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MASTER = ROOT / "experiments/yolo/sidequest_semantic_master_reader_codebook"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    dictionary = rows(OUT / "UNIQUE_173_MASTER_DICTIONARY.tsv")
    resolutions = rows(OUT / "THIRTY_NINE_GLOSS_DISAMBIGUATIONS.tsv")
    surfaces = rows(OUT / "UNIQUE_230_SURFACE_READER_KEY.tsv")
    events = rows(OUT / "UNIQUE_381_EVENT_INTERLINEAR.tsv")
    statements = rows(OUT / "UNIQUE_116_STATEMENT_EDITION.tsv")
    source_dictionary = rows(MASTER / "MASTER_173_CARD_DICTIONARY.tsv")

    check("173_cards", len(dictionary) == len(source_dictionary) == 173, len(dictionary))
    check("tuple_ids_unchanged", {row["joint_tuple_id"] for row in dictionary} == {row["joint_tuple_id"] for row in source_dictionary}, "same")
    check("173_unique_glosses", len({row["unique_short_meaning_de"] for row in dictionary}) == 173, len({row["unique_short_meaning_de"] for row in dictionary}))
    check("no_empty_gloss", all(row["unique_short_meaning_de"].strip() for row in dictionary), "all")
    check("39_disambiguated_cards", len(resolutions) == 39, len(resolutions))
    check("18_old_duplicate_groups", len({row["previous_duplicate_gloss_de"] for row in resolutions}) == 18, len({row["previous_duplicate_gloss_de"] for row in resolutions}))
    check("resolution_ids_exact", {row["joint_tuple_id"] for row in resolutions} == {row["joint_tuple_id"] for row in dictionary if row["gloss_revision"] == "DISAMBIGUATED_DUPLICATE"}, "same")
    check("all_resolutions_changed", all(row["previous_duplicate_gloss_de"] != row["unique_short_meaning_de"] for row in resolutions), "all")
    check("surface_rows_230", len(surfaces) == 230, len(surfaces))
    check("surfaces_keep_unique_cards", len({row["visible_surface"] for row in surfaces}) == 230 and all(row["direct_lookup_unique"] == "YES" for row in surfaces), "all")
    check("surface_gloss_matches_dictionary", all(row["unique_short_meaning_de"] == {d["joint_tuple_id"]: d["unique_short_meaning_de"] for d in dictionary}[row["joint_tuple_id"]] for row in surfaces), "all")
    check("381_events", len(events) == 381, len(events))
    check("90_affected_events", sum(row["gloss_revision"] == "DISAMBIGUATED_DUPLICATE" for row in events) == 90, sum(row["gloss_revision"] == "DISAMBIGUATED_DUPLICATE" for row in events))
    check("116_statements", len(statements) == 116, len(statements))
    check("statement_event_total", sum(int(row["event_count"]) for row in statements) == 381, sum(int(row["event_count"]) for row in statements))
    check("statement_status", all(row["statement_status"] == "UNIQUE_CARD_DEFAULTS_COMPLETE" for row in statements), "all")
    check("statement_lengths", all(len(row["master_head_sequence"].split()) == len(row["unique_literal_sequence_de"].split(" -> ")) == int(row["event_count"]) for row in statements), "all")
    check("all_affected_cards_have_contrast", all(row["teaching_contrast_de"].strip() for row in resolutions), "all")

    readable = (OUT / "ELEVEN_RECORD_UNIQUE_MASTER_READING.md").read_text(encoding="utf-8")
    check("all_statements_readable", all(f"### {row['statement_id']}" in readable for row in statements), "all")
    report = (OUT / "UNIQUE_MASTER_GLOSS_REPORT.md").read_text(encoding="utf-8")
    check("creative_codebook_caveat", "kreative Arbeitstheorie" in report and "Codebuchentscheidung" in report, "present")

    content_names = [
        "UNIQUE_173_MASTER_DICTIONARY.tsv", "THIRTY_NINE_GLOSS_DISAMBIGUATIONS.tsv",
        "UNIQUE_230_SURFACE_READER_KEY.tsv", "UNIQUE_381_EVENT_INTERLINEAR.tsv",
        "UNIQUE_116_STATEMENT_EDITION.tsv", "ELEVEN_RECORD_UNIQUE_MASTER_READING.md",
        "UNIQUE_MASTER_GLOSS_REPORT.md",
    ]
    content = "\n".join((OUT / name).read_text(encoding="utf-8", errors="replace") for name in content_names)
    sealed = re.compile(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])")
    check("sealed_pages_absent", sealed.search(content) is None, "absent")

    before = {name: digest(OUT / name) for name in content_names}
    subprocess.run([sys.executable, str(OUT / "build_unique_master_glosses.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = {name: digest(OUT / name) for name in content_names}
    check("deterministic_rebuild", before == after, "byte identical")

    passed = all(bool(row["pass"]) for row in checks)
    result = {
        "status": "PASS" if passed else "FAIL",
        "checks_passed": sum(bool(row["pass"]) for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "counts": {
            "cards": len(dictionary), "unique_glosses": len({row["unique_short_meaning_de"] for row in dictionary}),
            "disambiguated_cards": len(resolutions), "old_duplicate_groups": len({row["previous_duplicate_gloss_de"] for row in resolutions}),
            "events": len(events), "affected_events": sum(row["gloss_revision"] == "DISAMBIGUATED_DUPLICATE" for row in events),
            "statements": len(statements), "surface_forms": len(surfaces),
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
