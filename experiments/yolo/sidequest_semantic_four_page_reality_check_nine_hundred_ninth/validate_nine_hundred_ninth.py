#!/usr/bin/env python3
"""Validate the compact four-page creative reality check."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
SOURCE = ROOT / "transcription/voynich_zl3b_lines.tsv"
BUILDER = BASE / "build_nine_hundred_ninth.py"
RESULT = BASE / "NINE_HUNDRED_NINTH_FOUR_PAGE_RESULT.tsv"
SUMMARY = BASE / "NINE_HUNDRED_NINTH_BUILD_SUMMARY.json"
VALIDATION = BASE / "NINE_HUNDRED_NINTH_VALIDATION.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_tokens(page: str) -> list[tuple[str, int, str, str]]:
    if page.lower().startswith("f84"):
        raise ValueError("sealed selector")
    command = [
        str(ROOT / "vmanus-exp"),
        "query-tsv",
        str(SOURCE),
        "--selector",
        "page",
        "--allow",
        page,
        "--columns",
        "page,locus,kind,token_count,eva_clean",
        "--forbid-prefix",
        "f84",
    ]
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    return [
        (row["locus"], index, token, row["kind"])
        for row in rows
        for index, token in enumerate(row["eva_clean"].split(), start=1)
    ]


def record(checks: dict[str, bool], name: str, condition: bool) -> None:
    checks[name] = bool(condition)


def main() -> int:
    checks: dict[str, bool] = {}

    subprocess.run(["python3", str(BUILDER)], cwd=ROOT, check=True, capture_output=True, text=True)
    first = {RESULT.name: sha(RESULT), SUMMARY.name: sha(SUMMARY)}
    subprocess.run(["python3", str(BUILDER)], cwd=ROOT, check=True, capture_output=True, text=True)
    second = {RESULT.name: sha(RESULT), SUMMARY.name: sha(SUMMARY)}
    record(checks, "deterministic_rebuild", first == second)

    result = tsv(RESULT)
    record(checks, "result_rows_5", len(result) == 5)
    expected = {
        "f13r": (10, 77, 61, 77, 0, 25),
        "f75r": (53, 418, 203, 408, 10, 200),
        "f70v": (50, 218, 170, 0, 218, 50),
        "f88r": (31, 150, 110, 134, 16, 50),
        "TOTAL": (144, 863, 472, 619, 244, 325),
    }
    for row in result:
        got = tuple(
            int(row[key])
            for key in (
                "loci",
                "groups",
                "unique_surfaces",
                "prose_groups",
                "label_or_circle_groups",
                "exact_old_surface_groups",
            )
        )
        record(checks, f"counts_{row['unit']}", got == expected[row["unit"]])
    record(
        checks,
        "final_decision",
        result[-1]["working_outcome"] == "MIXED_PRODUCTIVE_GRAMMAR_PLUS_LOCAL_NOMENCLATOR",
    )

    source = {
        "f13r": guarded_tokens("f13r"),
        "f75r": guarded_tokens("f75r"),
        "f70v": guarded_tokens("f70v1") + guarded_tokens("f70v2"),
        "f88r": guarded_tokens("f88r"),
    }

    f13 = tsv(BASE / "F13R_TRANSFER.tsv")
    f13_seq = [(row["locus"], int(row["token_index"]), row["surface"], row["kind"]) for row in f13]
    record(checks, "f13_complete_sequence", f13_seq == source["f13r"])

    f75 = tsv(BASE / "F75R_TRANSFER.tsv")
    f75_seq = [(row["locus"], int(row["token_index"]), row["surface"]) for row in f75]
    record(checks, "f75_complete_sequence", f75_seq == [item[:3] for item in source["f75r"]])

    f70 = tsv(BASE / "F70V_TRANSFER.tsv")
    f70_seq = [(row["locus"], int(row["group_index"]), row["surface"]) for row in f70]
    record(checks, "f70_complete_sequence", f70_seq == [item[:3] for item in source["f70v"]])
    record(checks, "f70_aries_not_capricorn", all("CAPRICORN" not in str(row) for row in f70))

    f88 = tsv(BASE / "F88R_TRANSFER.tsv")
    source_f88_loci = Counter(locus for locus, _, _, _ in source["f88r"])
    f88_loci = {row["locus"]: int(row["tokens"]) for row in f88}
    record(checks, "f88_all_loci", f88_loci == dict(source_f88_loci))
    record(checks, "f88_groups_150", sum(f88_loci.values()) == 150)
    record(checks, "f88_exact_50", sum(int(row["exact_old_surface_tokens"]) for row in f88) == 50)
    record(checks, "f88_labels_16", sum(int(row["tokens"]) for row in f88 if row["kind"] == "LABEL") == 16)
    record(
        checks,
        "f88_labels_zero_exact",
        sum(int(row["exact_old_surface_tokens"]) for row in f88 if row["kind"] == "LABEL") == 0,
    )

    components = tsv(BASE / "NINE_HUNDRED_NINTH_REVISED_COMPONENTS.tsv")
    record(checks, "component_rows_40", len(components) == 40)
    record(checks, "component_unique", len({row["component"] for row in components}) == len(components))
    revised = {row["component"]: row["revised_portable_value_de"] for row in components}
    record(checks, "air_is_not_water", revised.get("AIR") == "LAUF ODER BAHN")
    record(checks, "al_is_connection", revised.get("AL") == "AUFNAHME- ODER ANSCHLUSSSTELLE")
    record(checks, "ar_is_output", revised.get("AR") == "AUSGANGS- ODER ENTNAHMESTELLE")
    record(checks, "cheo_register_bound", revised.get("CHEO") == "REGISTERABHAENGIGER EINTRAG")

    visuals = tsv(BASE / "NINE_HUNDRED_NINTH_VISUAL_INVENTORY.tsv")
    record(checks, "visual_rows_5", len(visuals) == 5)
    record(checks, "physical_pages_4", len({row["physical_page"] for row in visuals}) == 4)
    record(checks, "source_selectors_5", len({row["source_selector"] for row in visuals}) == 5)
    record(checks, "image_hashes_sha256", all(len(row["image_sha256"]) == 64 for row in visuals))

    reports = [
        "F13R_HERBAL_REALITY_CHECK.md",
        "F75R_BIO_REALITY_CHECK.md",
        "F70V_ASTRO_REALITY_CHECK.md",
        "F88R_PHARMA_REALITY_CHECK.md",
        "NINE_HUNDRED_NINTH_REALITY_CHECK_REPORT.md",
    ]
    record(checks, "all_reports_present", all((BASE / name).is_file() for name in reports))
    record(checks, "sealed_selectors_absent", all(not page.lower().startswith("f84") for page in ("f13r", "f75r", "f70v1", "f70v2", "f88r")))

    failures = [name for name, passed in checks.items() if not passed]
    payload = {
        "status": "PASS" if not failures else "FAIL",
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "failures": failures,
        "decision": "MIXED_PRODUCTIVE_GRAMMAR_PLUS_LOCAL_NOMENCLATOR",
        "physical_pages": 4,
        "groups": 863,
        "exact_old_surface_groups": 325,
        "result_sha256": sha(RESULT),
        "report_sha256": sha(BASE / "NINE_HUNDRED_NINTH_REALITY_CHECK_REPORT.md"),
    }
    VALIDATION.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
