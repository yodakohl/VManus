#!/usr/bin/env python3
"""Validate Pass 1011 and its complete repaired statement binding."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = (
    ROOT
    / "experiments/yolo/sidequest_semantic_ot_grade_and_concept_review_one_thousand_tenth"
    / "PASS1010_627_GRADE_AWARE_STATEMENTS.tsv"
)
COMBINED = HERE / "PASS1011_COMBINED_OPTICAL_AUDIT.tsv"
REVISED = HERE / "PASS1011_627_OPTICALLY_REPAIRED_STATEMENTS.tsv"
PAGE_SUMMARY = HERE / "PASS1011_PAGE_SUMMARY.tsv"
BUILD_SUMMARY = HERE / "PASS1011_BUILD_SUMMARY.json"
OUTPUT = HERE / "PASS1011_VALIDATION.json"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = rows(SOURCE)
    combined = rows(COMBINED)
    revised = rows(REVISED)
    page_summary = rows(PAGE_SUMMARY)
    source_by_id = {row["statement_id"]: row for row in source}
    audit_by_id = {row["statement_id"]: row for row in combined}
    revised_by_id = {row["statement_id"]: row for row in revised}
    checks: dict[str, bool] = {}

    checks["source_627"] = len(source) == 627
    checks["combined_35"] = len(combined) == 35
    checks["two_reviewers"] = len({row["reviewer"] for row in combined}) == 2
    checks["two_domains"] = {row["domain"] for row in combined} == {
        "HERBAL",
        "BIOLOGICAL",
    }
    checks["unique_audit_ids"] = len({row["audit_id"] for row in combined}) == 35
    checks["unique_statement_ids"] = len(audit_by_id) == 35
    checks["all_audits_in_source"] = set(audit_by_id) <= set(source_by_id)
    checks["page_bindings"] = all(
        row["page"] == source_by_id[row["statement_id"]]["physical_page"]
        for row in combined
    )
    checks["locus_bindings"] = all(
        row["locus_span"] == source_by_id[row["statement_id"]]["locus_span"]
        for row in combined
    )
    checks["translation_bindings"] = all(
        row["current_translation"]
        == source_by_id[row["statement_id"]]["grade_neutral_workshop_de"]
        for row in combined
    )
    allowed_fit = {
        "STRONG_FIT",
        "PLAUSIBLE",
        "STRAINED",
        "IMAGE_CONTRADICTION",
    }
    checks["fit_vocabulary"] = all(row["optical_fit"] in allowed_fit for row in combined)
    fit = Counter(row["optical_fit"] for row in combined)
    checks["fit_counts"] = fit == Counter(
        {"STRONG_FIT": 4, "PLAUSIBLE": 15, "STRAINED": 14, "IMAGE_CONTRADICTION": 2}
    )
    herbal = [row for row in combined if row["domain"] == "HERBAL"]
    biological = [row for row in combined if row["domain"] == "BIOLOGICAL"]
    checks["herbal_14"] = len(herbal) == 14
    checks["biological_21"] = len(biological) == 21
    checks["herbal_pages"] = {row["page"] for row in herbal} == {
        "f10r",
        "f11r",
        "f13r",
        "f17r",
        "f18r",
        "f55v",
        "f56r",
    }
    checks["biological_pages"] = {row["page"] for row in biological} == {
        "f75r",
        "f77r",
        "f81v",
        "f82r",
        "f83r",
    }
    checks["herbal_two_per_page"] = all(
        sum(row["page"] == page for row in herbal) == 2
        for page in {row["page"] for row in herbal}
    )
    checks["biological_distribution"] = Counter(row["page"] for row in biological) == Counter(
        {"f75r": 4, "f77r": 4, "f81v": 4, "f82r": 4, "f83r": 5}
    )
    checks["all_revised_nonempty"] = all(row["revised_translation"].strip() for row in combined)
    checks["all_repairs_nonempty"] = all(row["repair"].strip() for row in combined)
    checks["all_image_observations_nonempty"] = all(
        row["image_observation"].strip() for row in combined
    )
    checks["all_image_sources_nonempty"] = all(row["image_source"].strip() for row in combined)

    checks["revised_627"] = len(revised) == 627
    checks["revised_same_ids"] = set(revised_by_id) == set(source_by_id)
    checks["revised_order_preserved"] = [row["statement_id"] for row in revised] == [
        row["statement_id"] for row in source
    ]
    source_fields_to_preserve = [
        "book_statement_ordinal",
        "statement_id",
        "physical_page",
        "locus_span",
        "surface_sequence",
        "component_sequence",
        "event_ids",
        "grade_neutral_workshop_de",
    ]
    checks["source_fields_preserved"] = all(
        all(revised_by_id[sid][field] == source_by_id[sid][field] for field in source_fields_to_preserve)
        for sid in source_by_id
    )
    checks["review_status_counts"] = Counter(
        row["optical_review_status"] for row in revised
    ) == Counter(
        {
            "MANUALLY_REVIEWED_ORIGINAL_IMAGE": 35,
            "NOT_MANUALLY_REVIEWED_IN_PASS1011": 592,
        }
    )
    checks["reviewed_translation_matches_audit"] = all(
        revised_by_id[sid]["optically_revised_translation"]
        == audit_by_id[sid]["revised_translation"]
        for sid in audit_by_id
    )
    checks["unreviewed_translation_carried"] = all(
        row["optically_revised_translation"] == row["grade_neutral_workshop_de"]
        for row in revised
        if row["statement_id"] not in audit_by_id
    )
    checks["page_summary_12"] = len(page_summary) == 12
    checks["page_summary_total_35"] = sum(
        int(row["reviewed_statements"]) for row in page_summary
    ) == 35
    checks["two_direct_contradictions_named"] = {
        row["statement_id"] for row in combined if row["optical_fit"] == "IMAGE_CONTRADICTION"
    } == {"P1009-S400", "P1009-S498"}
    checks["reports_exist"] = all(
        (HERE / name).is_file()
        for name in (
            "HERBAL_APOTHECARY_OPTICAL_REPORT.md",
            "BATHHOUSE_DRAUGHTSMAN_OPTICAL_REPORT.md",
            "PASS1011_REPORT.md",
        )
    )

    sealed_tokens = ("f84", "f84r")
    audited_text = "\n".join(
        "\t".join(row.values()) for row in combined
    ).lower()
    checks["sealed_pages_absent"] = not any(token in audited_text for token in sealed_tokens)
    checks["no_absolute_local_paths_in_outputs"] = all(
        str(ROOT) not in path.read_text(encoding="utf-8")
        for path in (COMBINED, REVISED, PAGE_SUMMARY, HERE / "PASS1011_REPORT.md")
    )

    before = {path.name: sha256(path) for path in (COMBINED, REVISED, PAGE_SUMMARY, BUILD_SUMMARY)}
    subprocess.run(["python3", str(HERE / "build_pass1011.py")], cwd=ROOT, check=True)
    after = {path.name: sha256(path) for path in (COMBINED, REVISED, PAGE_SUMMARY, BUILD_SUMMARY)}
    checks["deterministic_rebuild"] = before == after

    result = {
        "pass": 1011,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
        "counts": {
            "source_statements": len(source),
            "manual_reviews": len(combined),
            "reviewed_pages": len(page_summary),
            "fit_counts": dict(sorted(fit.items())),
            "carried_unreviewed": len(source) - len(combined),
        },
    }
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise SystemExit("validation failed: " + ", ".join(failed))
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
