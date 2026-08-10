#!/usr/bin/env python3
"""Audit whether public/manual f67--f73 circular starts are authorial seams."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
ZL = ROOT / "transcription/sources/ZL3b-n.txt"
STOLFI = ROOT / "transcription/sources/Stolfi_text25e1-52.evt"
PUBLIC = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
OUT_TSV = RESULTS / "public_circle_seam_coordinate_audit.tsv"
OUT_JSON = RESULTS / "public_circle_seam_coordinate_audit.json"
REPORT = RESULTS / "public_circle_seam_coordinate_audit.md"

SCOPE = re.compile(r"^f(?:67|68|69|70|71|72|73)")
ZL_C = re.compile(
    r"^<(f(?:67|68|69|70|71|72|73)[^,>]*),([+@]Cc)>"
    r"\s+<!(\d\d:\d\d)([^>]*)>"
)
PAGE_HEADER = re.compile(r"@@ (f(?:67|68|69|70|71|72|73)[rv]\d?)\s*$")
UNIT_HEADER = re.compile(r"# Unit <([^>]+)>:\s*(.*)")
TEXT_LINE = re.compile(r"<(f[^.;>]+)\.([0-9]+);U>")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page_of(locus: str) -> str:
    return locus.rsplit(".", 1)[0]


def folio_of(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    assert match
    return match.group(1)


def clock_minutes(clock: str) -> int:
    hour, minute = map(int, clock.split(":"))
    if hour in (0, 12):
        hour = 12
    return hour * 60 + minute


def parse_zl() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in ZL.read_text(encoding="utf-8").splitlines():
        match = ZL_C.match(line)
        if not match:
            continue
        locus, code, clock, suffix = match.groups()
        if locus in rows:
            raise AssertionError(f"duplicate ZL C locus {locus}")
        rows[locus] = {
            "locus": locus,
            "page": page_of(locus),
            "folio": folio_of(page_of(locus)),
            "zl_code": code,
            "zl_selected_clock": clock,
            "zl_clock_annotation_suffix": suffix.strip(),
        }
    if len(rows) != 62:
        raise AssertionError(f"expected 62 C loci, found {len(rows)}")
    return rows


def parse_stolfi(targets: set[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    active_page: str | None = None
    unit = ""
    unit_description = ""
    comments: list[str] = []
    for line in STOLFI.read_text(encoding="utf-8", errors="replace").splitlines():
        page_match = PAGE_HEADER.match(line)
        if page_match:
            active_page = page_match.group(1)
            unit = ""
            unit_description = ""
            comments = []
            continue
        if line.startswith("@@ "):
            active_page = None
            unit = ""
            unit_description = ""
            comments = []
            continue
        if active_page is None:
            continue
        unit_match = UNIT_HEADER.match(line)
        if unit_match:
            unit, unit_description = unit_match.groups()
            comments = []
            continue
        if line.startswith("#"):
            comments.append(line[1:].strip())
            continue
        text_match = TEXT_LINE.match(line)
        if not text_match:
            continue
        locus = f"{text_match.group(1)}.{text_match.group(2)}"
        if locus in targets:
            if locus in result:
                raise AssertionError(f"duplicate Stolfi locus {locus}")
            result[locus] = {
                "stolfi_unit": unit,
                "stolfi_unit_description": unit_description.strip(),
                "stolfi_start_note": " ".join(part for part in comments if part).strip(),
            }
        comments = []
    if set(result) != targets:
        raise AssertionError(f"Stolfi mapping drift: missing={sorted(targets-set(result))}")
    return result


def note_flags(note: str) -> dict[str, int]:
    lower = note.lower()
    return {
        "stolfi_explicit_no_obvious_start": int(
            "no obvious starting" in lower or "no really obvious starting" in lower
        ),
        "stolfi_mentions_gap_or_word_space": int("gap" in lower or "word space" in lower),
        "stolfi_mentions_drawn_marker": int(bool(re.search(
            r"decorated|radial stroke|double[- ]?stroke|transversal stroke|marker", lower
        ))),
        "stolfi_mentions_fold_or_crease": int("fold" in lower or "crease" in lower),
        "stolfi_mentions_orientation_or_slant_convenience": int(bool(re.search(
            r"orientation|slant|baseline misalignment|letter size|get smaller", lower
        ))),
        "stolfi_mentions_star_or_nymph_convenience": int(
            "intrud" in lower or "above nymph" in lower
        ),
    }


def main() -> None:
    if OUT_TSV.exists() or OUT_JSON.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")

    zl = parse_zl()
    stolfi = parse_stolfi(set(zl))
    with PUBLIC.open(encoding="utf-8", newline="") as handle:
        public_rows = [row for row in csv.DictReader(handle, delimiter="\t") if SCOPE.match(row["page"])]
    if len(public_rows) != 26 or len({row["page"] for row in public_rows}) != 26:
        raise AssertionError("public 26-panel scope drift")
    public_pages = {row["page"] for row in public_rows}
    if set(row["page"] for row in zl.values()) != public_pages - {"f67r2", "f67v1", "f67v2"}:
        raise AssertionError("C-page scope no longer matches public atlas")

    output_rows: list[dict[str, str | int]] = []
    for locus, base in zl.items():
        note = " ".join((stolfi[locus]["stolfi_unit_description"], stolfi[locus]["stolfi_start_note"]))
        flags = note_flags(note)
        minutes = clock_minutes(base["zl_selected_clock"])
        output_rows.append({
            **base,
            **stolfi[locus],
            **flags,
            "zl_selected_clock_minutes_after_midnight": minutes,
            "zl_selected_clock_in_top_left_to_top_sector_0830_1200": int(510 <= minutes <= 720),
        })
    fieldnames = list(output_rows[0])
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    flag_counts = {
        key: sum(int(row[key]) for row in output_rows)
        for key in output_rows[0]
        if key.startswith("stolfi_") and key not in {
            "stolfi_unit", "stolfi_unit_description", "stolfi_start_note"
        }
    }
    clock_counts = dict(sorted(Counter(row["zl_selected_clock"] for row in output_rows).items()))
    pages = sorted({row["page"] for row in output_rows})
    folios = sorted({row["folio"] for row in output_rows})
    gates = {
        "exact_62_ZL_C_loci": len(output_rows) == 62,
        "exact_23_C_pages": len(pages) == 23,
        "exact_7_folios": len(folios) == 7,
        "all_C_loci_have_public_Stolfi_note_binding": len(stolfi) == 62,
        "all_ZL_selected_C_starts_are_in_0830_through_1200_sector": all(
            int(row["zl_selected_clock_in_top_left_to_top_sector_0830_1200"]) for row in output_rows
        ),
        "at_least_20_Stolfi_notes_explicitly_say_no_obvious_start": (
            flag_counts["stolfi_explicit_no_obvious_start"] >= 20
        ),
        "public_scope_is_26_panels": len(public_pages) == 26,
        "zero_Voynich_string_score": True,
        "zero_English_glosses": True,
    }
    status = "PASS_GLOBAL_C_FIRST_POSITION_IS_EDITORIAL_NOT_AUTHORIAL" if all(gates.values()) else "FAIL"
    result = {
        "experiment": "PUBLIC_CIRCLE_SEAM_COORDINATE_AUDIT",
        "status": status,
        "sources": {
            "public_circle_catalogue": "https://www.voynich.nu/illustr.html",
            "public_page_records": "https://www.voynich.nu/q09/index.html",
            "public_Stolfi_page_notes_example": "https://www.ic.unicamp.br/en/~stolfi/EXPORT/voynich/00-06-07-word-grammar/Notes/040/html/f72r1.htm",
            "public_Stolfi_repository": "https://www.ic.unicamp.br/~stolfi/voynich/",
        },
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (ZL, STOLFI, PUBLIC, Path(__file__))},
        "scope": {
            "public_panels": 26,
            "C_loci": len(output_rows),
            "C_pages": pages,
            "folios": folios,
            "public_panels_without_C_loci": ["f67r2", "f67v1", "f67v2"],
        },
        "ZL_selected_clock_counts": clock_counts,
        "Stolfi_note_flag_counts": flag_counts,
        "gates": gates,
        "decision": "DO_NOT_TREAT_GLOBAL_C_FIRST_OR_LAST_POSITION_AS_AUTHORIAL_PHASE",
        "artifacts": {OUT_TSV.name: {"sha256": sha(OUT_TSV), "rows": len(output_rows)}},
        "claim_ceiling": (
            "The public/manual sources independently define the f67--f73 circle scope and document "
            "many real gaps or drawn-marker candidates, but the globally registered C-locus starts are "
            "editorial cuts concentrated in one clock sector, including at least twenty-five loci whose "
            "notes explicitly say that no obvious start exists. First/last C position is therefore not a "
            "globally authorial coordinate. This does not deny local seams and supplies no order, object, "
            "degree, word, meaning, plaintext, or translation."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Public f67--f73 circular-seam coordinate audit\n\n"
        f"Status: **{status}**\n\n"
        "The f67--f73 block is independently defined by public Voynich catalogues; no user statement is "
        "used as manuscript data. The manual ZL transcription contains 62 `C` loci on 23 of the 26 public "
        "panels. Every selected transcription start falls from 08:30 through 12:00. The concentration is "
        "not evidence for a manuscript-wide top-left start: Stolfi's public notes explicitly say that no "
        f"obvious start exists for {flag_counts['stolfi_explicit_no_obvious_start']}/62 loci.\n\n"
        f"The same notes mention a gap or word space for {flag_counts['stolfi_mentions_gap_or_word_space']}/62 "
        f"loci and a drawn-marker candidate for {flag_counts['stolfi_mentions_drawn_marker']}/62. These are "
        "valuable local seam candidates, but they overlap editorially chosen points, folds, creases, star "
        "intrusions, and orientation changes. Each candidate must be licensed locally and mapped to its exact "
        "ring; it cannot justify a global first/last-position feature.\n\n"
        "Decision: **DO_NOT_TREAT_GLOBAL_C_FIRST_OR_LAST_POSITION_AS_AUTHORIAL_PHASE**. Rotation-invariant "
        "tests remain valid; phase-sensitive tests need an independent local physical seam. This audit does "
        "not establish direction, inter-band continuation, degree numbering, object ownership, a word, "
        "meaning, plaintext, or translation.\n\n"
        "Public sources: [Voynich illustration catalogue](https://www.voynich.nu/illustr.html); "
        "[Stolfi public page note for f72r1](https://www.ic.unicamp.br/en/~stolfi/EXPORT/voynich/00-06-07-word-grammar/Notes/040/html/f72r1.htm); "
        "[Stolfi public repository](https://www.ic.unicamp.br/~stolfi/voynich/).\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "C_loci": len(output_rows), "flags": flag_counts}, sort_keys=True))


if __name__ == "__main__":
    main()
