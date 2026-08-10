#!/usr/bin/env python3
"""Independent reconstruction of the public f67--f73 seam-coordinate audit."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
R = BASE / "results"
ZL = ROOT / "transcription/sources/ZL3b-n.txt"
EVT = ROOT / "transcription/sources/Stolfi_text25e1-52.evt"
PUB = R / "public_voynich_nu_page_annotations_v2.tsv"
TSV = R / "public_circle_seam_coordinate_audit.tsv"
RESULT = R / "public_circle_seam_coordinate_audit.json"
REPORT = R / "public_circle_seam_coordinate_audit.md"
OUT = R / "public_circle_seam_coordinate_audit_validation.json"
OUT_MD = R / "public_circle_seam_coordinate_audit_validation.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_true(value: bool, label: str, checks: list[str]) -> None:
    if not value:
        raise AssertionError(label)
    checks.append(label)


def independent_flags(text: str) -> dict[str, int]:
    s = text.casefold()
    return {
        "stolfi_explicit_no_obvious_start": int(
            any(p in s for p in ("no obvious starting", "no really obvious starting"))
        ),
        "stolfi_mentions_gap_or_word_space": int(any(p in s for p in ("gap", "word space"))),
        "stolfi_mentions_drawn_marker": int(any(p in s for p in (
            "decorated", "radial stroke", "double stroke", "double-stroke",
            "transversal stroke", "marker",
        ))),
        "stolfi_mentions_fold_or_crease": int(any(p in s for p in ("fold", "crease"))),
        "stolfi_mentions_orientation_or_slant_convenience": int(any(p in s for p in (
            "orientation", "slant", "baseline misalignment", "letter size", "get smaller",
        ))),
        "stolfi_mentions_star_or_nymph_convenience": int(any(p in s for p in ("intrud", "above nymph"))),
    }


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing overwrite")
    checks: list[str] = []
    target: dict[str, tuple[str, str, str]] = {}
    zpat = re.compile(
        r"^<(f(?:67|68|69|70|71|72|73)[^,>]*),([+@]Cc)>\s+"
        r"<!(\d\d:\d\d)([^>]*)>"
    )
    for raw in ZL.read_text(encoding="utf-8").splitlines():
        m = zpat.match(raw)
        if m:
            assert_true(m.group(1) not in target, "unique_ZL_C_locus", checks)
            target[m.group(1)] = (m.group(2), m.group(3), m.group(4).strip())
    assert_true(len(target) == 62, "exact_62_ZL_C_loci", checks)

    mapped: dict[str, tuple[str, str, str]] = {}
    in_scope = False
    unit = ""
    unit_desc = ""
    comments: list[str] = []
    page_re = re.compile(r"@@ (f(?:67|68|69|70|71|72|73)[rv]\d?)$")
    unit_re = re.compile(r"# Unit <([^>]+)>:\s*(.*)")
    locus_re = re.compile(r"<(f[^.;>]+)\.([0-9]+);U>")
    for raw in EVT.read_text(encoding="utf-8", errors="replace").splitlines():
        p = page_re.fullmatch(raw)
        if p:
            in_scope = True
            unit = unit_desc = ""
            comments = []
            continue
        if raw.startswith("@@ "):
            in_scope = False
            comments = []
            continue
        if not in_scope:
            continue
        u = unit_re.match(raw)
        if u:
            unit, unit_desc = u.groups()
            comments = []
            continue
        if raw.startswith("#"):
            comments.append(raw.removeprefix("#").strip())
            continue
        loc = locus_re.match(raw)
        if loc:
            locus = f"{loc.group(1)}.{loc.group(2)}"
            if locus in target:
                assert_true(locus not in mapped, "unique_EVT_target_locus", checks)
                mapped[locus] = (unit, unit_desc.strip(), " ".join(x for x in comments if x).strip())
            comments = []
    assert_true(set(mapped) == set(target), "exact_EVT_binding_set", checks)

    with TSV.open(encoding="utf-8", newline="") as handle:
        stored_rows = list(csv.DictReader(handle, delimiter="\t"))
    assert_true(len(stored_rows) == 62, "exact_62_stored_rows", checks)
    assert_true(len({row["locus"] for row in stored_rows}) == 62, "unique_stored_loci", checks)
    rows = {row["locus"]: row for row in stored_rows}
    assert_true(set(rows) == set(target), "stored_locus_set_exact", checks)

    totals = Counter()
    clocks = Counter()
    pages = set()
    folios = set()
    for locus in sorted(target):
        code, clock, suffix = target[locus]
        u, desc, note = mapped[locus]
        row = rows[locus]
        page = locus.rsplit(".", 1)[0]
        folio = re.match(r"^(f\d+)", page).group(1)
        hour, minute = map(int, clock.split(":"))
        minutes = (12 if hour in (0, 12) else hour) * 60 + minute
        expected = {
            "locus": locus,
            "page": page,
            "folio": folio,
            "zl_code": code,
            "zl_selected_clock": clock,
            "zl_clock_annotation_suffix": suffix,
            "stolfi_unit": u,
            "stolfi_unit_description": desc,
            "stolfi_start_note": note,
            **{key: str(value) for key, value in independent_flags(f"{desc} {note}").items()},
            "zl_selected_clock_minutes_after_midnight": str(minutes),
            "zl_selected_clock_in_top_left_to_top_sector_0830_1200": str(int(510 <= minutes <= 720)),
        }
        assert_true(row == expected, "exact_TSV_row", checks)
        flags = independent_flags(f"{desc} {note}")
        totals.update(flags)
        clocks[clock] += 1
        pages.add(page)
        folios.add(folio)

    with PUB.open(encoding="utf-8", newline="") as handle:
        public_pages = {
            row["page"] for row in csv.DictReader(handle, delimiter="\t")
            if re.match(r"^f(?:67|68|69|70|71|72|73)", row["page"])
        }
    assert_true(len(public_pages) == 26, "exact_26_public_panels", checks)
    assert_true(pages == public_pages - {"f67r2", "f67v1", "f67v2"}, "exact_23_C_page_set", checks)
    assert_true(len(folios) == 7, "exact_7_folios", checks)
    assert_true(sum(clocks.values()) == 62 and all(
        510 <= ((12 if int(c[:2]) in (0, 12) else int(c[:2])) * 60 + int(c[3:])) <= 720
        for c in clocks
    ), "all_selected_starts_in_0830_1200", checks)
    assert_true(totals == Counter({
        "stolfi_mentions_gap_or_word_space": 35,
        "stolfi_explicit_no_obvious_start": 25,
        "stolfi_mentions_drawn_marker": 22,
        "stolfi_mentions_fold_or_crease": 5,
        "stolfi_mentions_star_or_nymph_convenience": 5,
        "stolfi_mentions_orientation_or_slant_convenience": 4,
    }), "exact_note_flag_counts", checks)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert_true(result["status"] == "PASS_GLOBAL_C_FIRST_POSITION_IS_EDITORIAL_NOT_AUTHORIAL", "status_exact", checks)
    assert_true(result["decision"] == "DO_NOT_TREAT_GLOBAL_C_FIRST_OR_LAST_POSITION_AS_AUTHORIAL_PHASE", "decision_exact", checks)
    assert_true(result["ZL_selected_clock_counts"] == dict(sorted(clocks.items())), "clock_counts_exact", checks)
    assert_true(result["Stolfi_note_flag_counts"] == dict(totals), "flag_counts_exact", checks)
    assert_true(result["artifacts"][TSV.name]["sha256"] == digest(TSV), "TSV_hash_bound", checks)
    assert_true(result["inputs"][str(ZL.relative_to(ROOT))] == digest(ZL), "ZL_hash_bound", checks)
    assert_true(result["inputs"][str(EVT.relative_to(ROOT))] == digest(EVT), "EVT_hash_bound", checks)
    assert_true(result["inputs"][str(PUB.relative_to(ROOT))] == digest(PUB), "public_table_hash_bound", checks)
    assert_true(all(result["gates"].values()), "all_result_gates_true", checks)
    report = REPORT.read_text(encoding="utf-8")
    assert_true("25/62 loci" in report, "report_no_obvious_count_bound", checks)
    assert_true(result["decision"] in report, "report_decision_bound", checks)

    validation = {
        "experiment": "PUBLIC_CIRCLE_SEAM_COORDINATE_AUDIT_VALIDATION",
        "status": "PASS_INDEPENDENT_RECONSTRUCTION",
        "checks": len(checks),
        "failures": [],
        "reconstructed": {
            "C_loci": len(target),
            "C_pages": len(pages),
            "folios": len(folios),
            "clock_counts": dict(sorted(clocks.items())),
            "note_flag_counts": dict(totals),
        },
        "bindings": {
            "producer_result_sha256": digest(RESULT),
            "producer_report_sha256": digest(REPORT),
            "producer_TSV_sha256": digest(TSV),
            "validator_sha256": digest(Path(__file__)),
        },
        "decision": "VALIDATED_GLOBAL_FIRST_LAST_C_POSITION_IS_NOT_AUTHORIAL_PHASE",
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Public circle seam-coordinate validation\n\n"
        "Status: **PASS_INDEPENDENT_RECONSTRUCTION**\n\n"
        f"A nonimporting validator passed {len(checks):,} checks and independently reconstructed all "
        "62 ZL circular loci, their exact Stolfi public-note bindings, the 23-page / seven-folio scope, "
        "every selected clock coordinate, all six note-flag totals, the stored TSV, result gates, hashes, "
        "decision, and report claims. It confirms only that global first/last C position is not an "
        "authorial phase; local physical seam candidates remain available for separately licensed tests.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": validation["status"], "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
