#!/usr/bin/env python3
"""Build the compact Pass-1011 manual optical repair edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1010 = (
    ROOT
    / "experiments/yolo/sidequest_semantic_ot_grade_and_concept_review_one_thousand_tenth"
    / "PASS1010_627_GRADE_AWARE_STATEMENTS.tsv"
)
HERBAL = HERE / "HERBAL_APOTHECARY_OPTICAL_AUDIT.tsv"
BATH = HERE / "BATHHOUSE_DRAUGHTSMAN_OPTICAL_AUDIT.tsv"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_herbal(row: dict[str, str]) -> dict[str, str]:
    return {
        "reviewer": "HERBAL_APOTHECARY_SCRIBE_CA1420",
        "domain": "HERBAL",
        "audit_id": row["audit_id"],
        "page": row["page"],
        "image_source": f"YALE_CANVAS_{row['image_object_id']}",
        "statement_id": row["statement_id"],
        "locus_span": row["locus_span"],
        "visible_zone": "WHOLE_PLANT_AND_VISIBLE_PARTS",
        "owner_binding": "WHOLE_PLANT_OWNER",
        "image_observation": row["image_observation"],
        "current_translation": row["current_translation"],
        "optical_fit": row["optical_fit"],
        "supported_elements": row["supported_elements"],
        "unsupported_or_invisible_elements": row[
            "unsupported_or_invisible_elements"
        ],
        "repair": row["repair"],
        "revised_translation": row["revised_translation"],
    }


def normalize_bath(row: dict[str, str]) -> dict[str, str]:
    return {
        "reviewer": "BATHHOUSE_MASTER_TECHNICAL_DRAUGHTSMAN_CA1420",
        "domain": "BIOLOGICAL",
        "audit_id": row["audit_id"],
        "page": row["page"],
        "image_source": row["image_source"],
        "statement_id": row["statement_id"],
        "locus_span": row["locus_span"],
        "visible_zone": row["visible_station"],
        "owner_binding": row["owner_binding"],
        "image_observation": row["image_observation"],
        "current_translation": row["current_translation"],
        "optical_fit": row["optical_fit"],
        "supported_elements": row["supported_elements"],
        "unsupported_or_invisible_elements": row[
            "unsupported_or_invisible_elements"
        ],
        "repair": row["repair"],
        "revised_translation": row["revised_translation"],
    }


def main() -> None:
    source_fields, source_rows = read_tsv(PASS1010)
    _, herbal_rows = read_tsv(HERBAL)
    _, bath_rows = read_tsv(BATH)
    source_by_id = {row["statement_id"]: row for row in source_rows}

    combined = [normalize_herbal(row) for row in herbal_rows]
    combined.extend(normalize_bath(row) for row in bath_rows)
    combined.sort(key=lambda row: int(source_by_id[row["statement_id"]]["book_statement_ordinal"]))

    combined_fields = [
        "reviewer",
        "domain",
        "audit_id",
        "page",
        "image_source",
        "statement_id",
        "locus_span",
        "visible_zone",
        "owner_binding",
        "image_observation",
        "current_translation",
        "optical_fit",
        "supported_elements",
        "unsupported_or_invisible_elements",
        "repair",
        "revised_translation",
    ]
    combined_path = HERE / "PASS1011_COMBINED_OPTICAL_AUDIT.tsv"
    write_tsv(combined_path, combined_fields, combined)

    audit_by_id = {row["statement_id"]: row for row in combined}
    revised_rows: list[dict[str, str]] = []
    extra_fields = [
        "optical_review_status",
        "optical_reviewer",
        "optical_fit",
        "optical_image_source",
        "optical_visible_zone",
        "optical_repair",
        "optically_revised_translation",
    ]
    for source in source_rows:
        row = dict(source)
        audit = audit_by_id.get(source["statement_id"])
        if audit:
            row.update(
                {
                    "optical_review_status": "MANUALLY_REVIEWED_ORIGINAL_IMAGE",
                    "optical_reviewer": audit["reviewer"],
                    "optical_fit": audit["optical_fit"],
                    "optical_image_source": audit["image_source"],
                    "optical_visible_zone": audit["visible_zone"],
                    "optical_repair": audit["repair"],
                    "optically_revised_translation": audit["revised_translation"],
                }
            )
        else:
            row.update(
                {
                    "optical_review_status": "NOT_MANUALLY_REVIEWED_IN_PASS1011",
                    "optical_reviewer": "",
                    "optical_fit": "NOT_REVIEWED",
                    "optical_image_source": "",
                    "optical_visible_zone": "",
                    "optical_repair": "",
                    "optically_revised_translation": source[
                        "grade_neutral_workshop_de"
                    ],
                }
            )
        revised_rows.append(row)

    revised_path = HERE / "PASS1011_627_OPTICALLY_REPAIRED_STATEMENTS.tsv"
    write_tsv(revised_path, source_fields + extra_fields, revised_rows)

    per_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in combined:
        per_page[row["page"]].append(row)
    summary_rows: list[dict[str, str]] = []
    for page, rows in sorted(
        per_page.items(),
        key=lambda item: int(source_by_id[item[1][0]["statement_id"]]["book_statement_ordinal"]),
    ):
        counts = Counter(row["optical_fit"] for row in rows)
        summary_rows.append(
            {
                "page": page,
                "domain": rows[0]["domain"],
                "reviewed_statements": str(len(rows)),
                "strong_fit": str(counts["STRONG_FIT"]),
                "plausible": str(counts["PLAUSIBLE"]),
                "strained": str(counts["STRAINED"]),
                "image_contradiction": str(counts["IMAGE_CONTRADICTION"]),
                "translation_repairs": str(
                    sum(
                        row["current_translation"] != row["revised_translation"]
                        for row in rows
                    )
                ),
            }
        )
    summary_path = HERE / "PASS1011_PAGE_SUMMARY.tsv"
    summary_fields = [
        "page",
        "domain",
        "reviewed_statements",
        "strong_fit",
        "plausible",
        "strained",
        "image_contradiction",
        "translation_repairs",
    ]
    write_tsv(summary_path, summary_fields, summary_rows)

    fit_counts = Counter(row["optical_fit"] for row in combined)
    domain_counts = {
        domain: Counter(row["optical_fit"] for row in combined if row["domain"] == domain)
        for domain in ("HERBAL", "BIOLOGICAL")
    }
    output_paths = [combined_path, revised_path, summary_path, HERBAL, BATH]
    summary = {
        "pass": 1011,
        "source_statements": len(source_rows),
        "manual_reviews": len(combined),
        "unreviewed_statements_carried_forward": len(source_rows) - len(combined),
        "reviewers": 2,
        "reviewed_pages": len(per_page),
        "domains": {domain: sum(domain_counts[domain].values()) for domain in domain_counts},
        "fit_counts": dict(sorted(fit_counts.items())),
        "domain_fit_counts": {
            domain: dict(sorted(counts.items())) for domain, counts in domain_counts.items()
        },
        "translation_repairs": sum(
            row["current_translation"] != row["revised_translation"] for row in combined
        ),
        "image_contradictions_repaired": fit_counts["IMAGE_CONTRADICTION"],
        "outputs_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in output_paths},
    }
    (HERE / "PASS1011_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
