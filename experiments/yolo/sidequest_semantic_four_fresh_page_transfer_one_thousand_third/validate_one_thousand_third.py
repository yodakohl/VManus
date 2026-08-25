#!/usr/bin/env python3
"""Validate the counts, guarded source binding, and complete meanings of Pass 1003."""

from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "transcription/voynich_zl3b_lines.tsv"
ROOTS = (
    ROOT
    / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"
    / "PASS996_53_PORTABLE_ROOTS.tsv"
)
PAGES = {"f17r": 80, "f77r": 332, "f88v": 145, "f71v": 100}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded(page: str) -> list[tuple[str, str, int, str]]:
    result = subprocess.run(
        [
            str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE),
            "--selector", "page", "--allow", page,
            "--columns", "page,locus,kind,token_count,eva_clean",
            "--forbid-prefix", "f84",
        ],
        cwd=ROOT, check=True, text=True, capture_output=True,
    )
    rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    return [
        (row["locus"], row["kind"], index, token)
        for row in rows
        for index, token in enumerate(row["eva_clean"].split(), 1)
    ]


def main() -> int:
    events = read(HERE / "PASS1003_657_FRESH_EVENT_INTERLINEAR.tsv")
    loci = read(HERE / "PASS1003_111_LOCUS_READINGS.tsv")
    surfaces = read(HERE / "PASS1003_393_FRESH_SURFACE_DICTIONARY.tsv")
    owners = read(HERE / "PASS1003_VISUAL_OWNER_MAP.tsv")
    pressure = read(HERE / "PASS1003_ROOT_TRANSFER_PRESSURE.tsv")
    combined = read(HERE / "PASS1003_3168_COMBINED_EVENT_INTERLINEAR.tsv")
    summary = json.loads((HERE / "PASS1003_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    roots = {row["recognition_form"] for row in read(ROOTS)}

    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    check("events_657", len(events) == 657)
    check("loci_111", len(loci) == 111)
    check("surfaces_393", len(surfaces) == 393 and len({row["surface"] for row in surfaces}) == 393)
    check("owners_11", len(owners) == 11 and len({row["owner_id"] for row in owners}) == 11)
    check("combined_3168", len(combined) == 3168)
    check("fresh_ids_contiguous", [row["fresh_event_id"] for row in events] == [f"P1003-E{i:04d}" for i in range(1, 658)])
    check("page_counts", Counter(row["physical_page"] for row in events) == Counter(PAGES))
    check("label_groups_49", sum(row["kind"] == "L" for row in events) == 49)
    check("running_groups_608", sum(row["kind"] != "L" for row in events) == 608)
    check("labels_are_addresses", all(row["component_recipe"] == "LOCAL_ADDRESS" for row in events if row["kind"] == "L"))
    check("running_not_addresses", all(row["component_recipe"] != "LOCAL_ADDRESS" for row in events if row["kind"] != "L"))
    check("no_empty_readings", all(row["portable_default_de"].strip() and row["local_contextual_expansion_de"].strip() for row in events))
    check("no_empty_recipes", all(row["component_recipe"].strip() for row in events))
    check("known_components_only", all(
        component in roots
        for row in events if row["component_recipe"] != "LOCAL_ADDRESS"
        for component in row["component_recipe"].split("+")
    ))
    check("no_new_portable_root", summary["new_portable_roots"] == 0 and all(row["new_portable_root"] == "NO" for row in pressure))
    check("exact_count_411", sum(row["transfer_class"] == "EXACT_REGISTERED_SURFACE" for row in events) == 411)
    check("visible_count_150", sum(row["transfer_class"] == "VISIBLE_NEW_COMPOSITION" for row in events) == 150)
    check("one_edit_count_34", sum(row["transfer_class"] == "NEAR_REGISTERED_ALLOGRAPH" for row in events) == 34)
    check("tentative_count_13", sum(row["transfer_class"] == "TENTATIVE_ROOTED_VARIANT" for row in events) == 13)
    check("owner_addresses_49", sum(row["transfer_class"] == "LOCAL_OWNER_ADDRESS" for row in events) == 49)
    check("no_low_confidence", all(row["confidence"] != "LOW" for row in events))
    check("combined_old_2511", sum(row["edition_source"] == "PASS1002" for row in combined) == 2511)
    check("combined_new_657", sum(row["edition_source"] == "PASS1003_FRESH_TRANSFER" for row in combined) == 657)
    check("combined_pages_18", len({row["physical_page"] for row in combined}) == 18)
    check("combined_running_2618", summary["combined_running_groups"] == 2618)
    check("combined_addresses_550", summary["combined_local_addresses"] == 550)
    check("sealed_absent_events", not any(row["physical_page"].lower().startswith("f84") for row in events))
    check("sealed_absent_combined", not any(row["physical_page"].lower().startswith("f84") for row in combined))
    check("all_owner_ids_declared", {row["owner_id"] for row in events} <= {row["owner_id"] for row in owners})
    check("all_image_sources_official", all(row["image_source"].startswith("https://collections.library.yale.edu/iiif/2/") for row in owners))

    for page, expected in PAGES.items():
        source = guarded(page)
        produced = [
            (row["locus"], row["kind"], int(row["group_index"]), row["surface"])
            for row in events if row["physical_page"] == page
        ]
        check(f"guarded_sequence_{page}", source == produced and len(produced) == expected)

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": len(checks),
        "passed": sum(checks.values()),
        "failed": [name for name, value in checks.items() if not value],
        "details": checks,
    }
    (HERE / "PASS1003_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
