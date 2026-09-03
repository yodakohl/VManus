#!/usr/bin/env python3
"""Guarded qualitative source reconstruction for GDT786.

The public entry point is :func:`compute`.  It writes nothing.  All current
transcription rows are obtained through GDT782's guarded loader and inherited
179-page allow-list.  The legacy Stolfi source is queried with that loader's
guard for the thirteen target pages only.

The module deliberately keeps three different objects separate:

* the fourteen reader-exact, fused ``salX`` occurrences;
* raw versus reader-exact *separated* ``sal X`` pairs;
* Stolfi's legacy boundary at the same physical locus, when that locus exists
  in the cached Stolfi transcription.

No EVA character, prefix, suffix, or spelling is assigned a meaning here.
The qualitative German candidates are copied from the experiment's fixed
whole-form specs and are returned only as replaceable displays.
"""

from __future__ import annotations

import csv
import importlib.util
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


EXPERIMENT_REL = Path("experiments/yolo/gdt786_sal_left_root_transfer_tournament")
G782_RUN_REL = Path(
    "experiments/yolo/"
    "gdt782_recurrent_six_target_external_field_adjudication/src/run.py"
)
STOLFI_REL = Path("transcription/voynich_stolfi25e1_lines.tsv")

EXPECTED_REMAINDERS = (
    "al", "ar", "dal", "dam", "dy", "f", "keedy", "o", "ol",
    "shcthdy", "tar", "y",
)
EXPECTED_SURFACES = {
    "salal": "al",
    "salar": "ar",
    "saldal": "dal",
    "saldam": "dam",
    "saldy": "dy",
    "salf": "f",
    "salkeedy": "keedy",
    "salo": "o",
    "salol": "ol",
    "salshcthdy": "shcthdy",
    "saltar": "tar",
    "saly": "y",
}
EXPECTED_EXACT_COUNTS = Counter({
    "salo": 2,
    "saly": 2,
    "salal": 1,
    "salar": 1,
    "saldal": 1,
    "saldam": 1,
    "saldy": 1,
    "salf": 1,
    "salkeedy": 1,
    "salol": 1,
    "salshcthdy": 1,
    "saltar": 1,
})
EXPECTED_RAW_SPLIT_COUNTS = Counter({"ol": 1})
EXPECTED_TARGET_PAGES = frozenset({
    "f58r", "f58v", "f66r", "f75r", "f80r", "f80v", "f81v",
    "f87r", "f89r1", "f99r", "f106v", "f111r", "f116r",
})


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _one_by(
    rows: Sequence[Mapping[str, str]], key: str
) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row[key]
        if value in result:
            raise AssertionError(f"duplicate {key}: {value}")
        result[value] = dict(row)
    return result


def _load_g782(repo_root: Path):
    path = repo_root / G782_RUN_REL
    spec = importlib.util.spec_from_file_location(
        "gdt782_guarded_for_gdt786_qualitative", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import guarded GDT782 loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if Path(module.ROOT).resolve() != repo_root:
        raise AssertionError("GDT782 loader resolved a different repository")
    return module


def _line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def _physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if match is None:
        raise AssertionError(f"invalid page label: {page}")
    return match.group(1)


def _joined(values: Sequence[str]) -> str:
    return "|".join(values) if values else "NONE"


def _consecutive_count(tokens: Sequence[str], left: str, right: str) -> int:
    return sum(
        tokens[index] == left and tokens[index + 1] == right
        for index in range(len(tokens) - 1)
    )


def _target_specs(repo_root: Path) -> tuple[
    dict[str, dict[str, str]],
    list[dict[str, str]],
]:
    source = repo_root / EXPERIMENT_REL / "src"
    target_rows = _read_tsv(source / "TARGET_12_SPECS.tsv")
    target_by_surface = _one_by(target_rows, "surface")
    observed = {
        surface: row["remainder"] for surface, row in target_by_surface.items()
    }
    if observed != EXPECTED_SURFACES:
        raise AssertionError(f"twelve target specs changed: {observed}")

    passage_rows = _read_tsv(source / "PASSAGE_14_SPECS.tsv")
    if len(passage_rows) != 14:
        raise AssertionError("expected fourteen passage specs")
    passage_ids = [row["passage_id"] for row in passage_rows]
    if passage_ids != [f"G786-P{number:02d}" for number in range(1, 15)]:
        raise AssertionError(f"passage order changed: {passage_ids}")
    if Counter(row["surface"] for row in passage_rows) != EXPECTED_EXACT_COUNTS:
        raise AssertionError("passage surface census changed")
    if any(
        row["surface"] not in target_by_surface for row in passage_rows
    ):
        raise AssertionError("passage spec names an unknown target surface")
    return target_by_surface, passage_rows


def _occurrence_rows(
    by_line: Mapping[str, list[dict[str, str]]],
    exact: Mapping[tuple[str, int], int],
    cross_by_locus: Mapping[str, Mapping[str, str]],
    line_by_locus: Mapping[str, Mapping[str, str]],
    target_by_surface: Mapping[str, Mapping[str, str]],
    passage_rows: Sequence[Mapping[str, str]],
) -> list[dict[str, object]]:
    discovered: dict[tuple[str, int, str], dict[str, object]] = {}
    raw_target_counts: Counter[str] = Counter()

    for locus, line in by_line.items():
        surface_rank: Counter[str] = Counter()
        for ordinal, token in enumerate(line, 1):
            surface = token["eva"]
            if surface not in target_by_surface:
                continue
            raw_target_counts[surface] += 1
            surface_rank[surface] += 1
            token_index = int(token["token_index"])
            if not exact[locus, token_index]:
                continue
            cross = cross_by_locus[locus]
            counts = {
                name: cross[name].split().count(surface)
                for name in ("zl3b_clean", "it2a_clean", "rf1b_clean")
            }
            if surface_rank[surface] > min(counts.values()):
                raise AssertionError("GDT782 exact map and reader capacities disagree")
            meta = line_by_locus[locus]
            key = (locus, ordinal, surface)
            if key in discovered:
                raise AssertionError(f"duplicate exact target coordinate: {key}")
            discovered[key] = {
                "surface": surface,
                "remainder": target_by_surface[surface]["remainder"],
                "page": token["page"],
                "physical_folio": _physical_folio(token["page"]),
                "locus": locus,
                "target_ordinal": ordinal,
                "token_index": token_index,
                "line_token_count": len(line),
                "line_position": _line_position(ordinal, len(line)),
                "section": token["section"],
                "language": token["language"],
                "hand": token["hand"],
                "paragraph_start": int(meta["paragraph_start"]),
                "paragraph_end": int(meta["paragraph_end"]),
                "true_paragraph_start": int(
                    meta["paragraph_start"] == "1" and ordinal == 1
                ),
                "true_paragraph_end": int(
                    meta["paragraph_end"] == "1" and ordinal == len(line)
                ),
                "reader_exact": 1,
                "reader_exact_method": (
                    "GDT782_OCCURRENCE_RANK_LE_MIN_"
                    "ZL3B_IT2A_RF1B_SURFACE_COUNTS"
                ),
                "zl3b_surface_count": counts["zl3b_clean"],
                "it2a_surface_count": counts["it2a_clean"],
                "rf1b_surface_count": counts["rf1b_clean"],
                "all_three_current_readers_fused": 1,
                "all_present_exact_line": int(cross["all_present_exact"]),
                "written_line_eva": " ".join(item["eva"] for item in line),
                "zl3b_line": cross["zl3b_clean"],
                "it2a_line": cross["it2a_clean"],
                "rf1b_line": cross["rf1b_clean"],
            }

    if Counter(row["surface"] for row in discovered.values()) != EXPECTED_EXACT_COUNTS:
        raise AssertionError("guarded exact salX occurrence census changed")

    passage_keys = [
        (row["locus"], int(row["target_ordinal"]), row["surface"])
        for row in passage_rows
    ]
    if len(set(passage_keys)) != 14 or set(passage_keys) != set(discovered):
        missing = sorted(set(passage_keys) - set(discovered))
        extra = sorted(set(discovered) - set(passage_keys))
        raise AssertionError(
            f"passage coordinates disagree with guard: missing={missing}, extra={extra}"
        )

    output: list[dict[str, object]] = []
    for passage, key in zip(passage_rows, passage_keys, strict=True):
        row = dict(discovered[key])
        target = target_by_surface[str(row["surface"])]
        row.update({
            "passage_id": passage["passage_id"],
            "historical_preference": passage["historical_preference"],
            "focus_display_de": passage["focus_display_de"],
            "interpretive_note_de": passage["interpretive_note_de"],
            "preferred_mechanism": target["preferred_mechanism"],
            "practical_default_de": target["practical_default_de"],
            "drug_composite_de": target["drug_composite_de"],
            "learned_whole_rival_de": target["learned_whole_rival_de"],
            "salt_rival_de": target["salt_rival_de"],
            "working_confidence": target["working_confidence"],
            "raw_complete_surface_occurrences": raw_target_counts[
                str(row["surface"])
            ],
        })
        output.append(row)
    return output


def _split_rows(
    by_line: Mapping[str, list[dict[str, str]]],
    exact: Mapping[tuple[str, int], int],
    target_by_surface: Mapping[str, Mapping[str, str]],
) -> list[dict[str, object]]:
    raw: defaultdict[str, list[str]] = defaultdict(list)
    reader_exact: defaultdict[str, list[str]] = defaultdict(list)
    left_exact: Counter[str] = Counter()
    right_exact: Counter[str] = Counter()

    for locus, line in by_line.items():
        for index in range(len(line) - 1):
            left, right = line[index], line[index + 1]
            if left["eva"] != "sal" or right["eva"] not in EXPECTED_REMAINDERS:
                continue
            remainder = right["eva"]
            coordinate = f"{locus}:{index + 1}-{index + 2}"
            raw[remainder].append(coordinate)
            is_left_exact = int(exact[locus, int(left["token_index"])])
            is_right_exact = int(exact[locus, int(right["token_index"])])
            left_exact[remainder] += is_left_exact
            right_exact[remainder] += is_right_exact
            if is_left_exact and is_right_exact:
                reader_exact[remainder].append(coordinate)

    observed_raw = Counter({key: len(value) for key, value in raw.items()})
    if observed_raw != EXPECTED_RAW_SPLIT_COUNTS:
        raise AssertionError(f"raw sal-X pair census changed: {observed_raw}")
    if any(reader_exact.values()):
        raise AssertionError(f"reader-exact sal-X pair appeared: {reader_exact}")

    surface_for_remainder = {
        row["remainder"]: surface for surface, row in target_by_surface.items()
    }
    output: list[dict[str, object]] = []
    for remainder in EXPECTED_REMAINDERS:
        raw_coordinates = raw.get(remainder, [])
        exact_coordinates = reader_exact.get(remainder, [])
        output.append({
            "surface": surface_for_remainder[remainder],
            "remainder": remainder,
            "separated_pair": f"sal {remainder}",
            "raw_pair_occurrences": len(raw_coordinates),
            "raw_pair_coordinates": _joined(raw_coordinates),
            "raw_pairs_with_exact_sal": left_exact[remainder],
            "raw_pairs_with_exact_remainder": right_exact[remainder],
            "reader_exact_pair_occurrences": len(exact_coordinates),
            "reader_exact_pair_coordinates": _joined(exact_coordinates),
            "reader_exact_boundary_bridge": int(bool(exact_coordinates)),
        })
    return output


def _stolfi_rows(
    base,
    occurrence_rows: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], dict[str, int]]:
    target_pages = {str(row["page"]) for row in occurrence_rows}
    if target_pages != EXPECTED_TARGET_PAGES:
        raise AssertionError(f"target page set changed: {sorted(target_pages)}")
    if any(page.startswith("f84") for page in target_pages):
        raise AssertionError("sealed page requested for Stolfi")

    queried, guard = base.guarded_query(
        STOLFI_REL,
        target_pages,
        "page,locus,raw_text,clean_text",
    )
    if any(row["page"].startswith("f84") for row in queried):
        raise AssertionError("sealed Stolfi row materialized")
    by_locus = _one_by(queried, "locus")
    by_page: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in queried:
        by_page[row["page"]].append(row)

    output: list[dict[str, object]] = []
    for occurrence in occurrence_rows:
        page = str(occurrence["page"])
        locus = str(occurrence["locus"])
        surface = str(occurrence["surface"])
        remainder = str(occurrence["remainder"])
        same = by_locus.get(locus)
        page_rows = by_page.get(page, [])

        page_whole_count = sum(
            row["clean_text"].split().count(surface) for row in page_rows
        )
        page_split_count = sum(
            _consecutive_count(row["clean_text"].split(), "sal", remainder)
            for row in page_rows
        )
        if same is None:
            status = (
                "NO_SAME_LOCUS_ROW"
                if page_rows else "NO_STOLFI_ROWS_FOR_PAGE"
            )
            same_tokens: list[str] = []
            same_whole_count = 0
            same_split_count = 0
            raw_boundary = "NONE"
        else:
            same_tokens = same["clean_text"].split()
            same_whole_count = same_tokens.count(surface)
            same_split_count = _consecutive_count(
                same_tokens, "sal", remainder
            )
            marker = re.search(
                rf"(?<![A-Za-z])sal([.,]){re.escape(remainder)}(?![A-Za-z])",
                same["raw_text"],
            )
            raw_boundary = marker.group(1) if marker else "NONE"
            if same_whole_count:
                status = "FUSED_WHOLE_AT_SAME_LOCUS"
            elif same_split_count:
                status = "SAL_X_SPLIT_AT_SAME_LOCUS"
            else:
                status = "ALTERNATE_READING_OR_OTHER_BOUNDARY"

        output.append({
            "passage_id": occurrence["passage_id"],
            "page": page,
            "target_locus": locus,
            "surface": surface,
            "remainder": remainder,
            "stolfi_page_row_count": len(page_rows),
            "stolfi_same_locus_present": int(same is not None),
            "stolfi_raw_text": same["raw_text"] if same else "NONE",
            "stolfi_clean_text": same["clean_text"] if same else "NONE",
            "same_locus_whole_count": same_whole_count,
            "same_locus_sal_x_count": same_split_count,
            "same_locus_raw_sal_x_separator": raw_boundary,
            "page_whole_count": page_whole_count,
            "page_sal_x_count": page_split_count,
            "boundary_status": status,
        })
    return output, guard


def compute(repo_root: Path) -> dict[str, object]:
    """Return the guarded qualitative GDT786 reconstruction.

    The result contains TSV-friendly row dictionaries under
    ``occurrence_rows``, ``split_rows`` and ``stolfi_rows`` plus compact audit
    counts under ``summary``.  No file is created or modified.
    """
    root = Path(repo_root).resolve()
    if not (root / "AGENTS.md").is_file() or not (root / ".git").exists():
        raise RuntimeError(f"not the VManus repository root: {root}")

    target_by_surface, passage_rows = _target_specs(root)
    base = _load_g782(root)
    by_line, exact, cross, line_meta, _cells, guard = base.load_context()
    if int(guard["allowed_pages"]) != 179:
        raise AssertionError(f"GDT782 allow-list changed: {guard}")
    if any(
        token["page"].startswith("f84")
        for line in by_line.values()
        for token in line
    ):
        raise AssertionError("sealed f84/f84r token materialized")

    occurrence_rows = _occurrence_rows(
        by_line,
        exact,
        cross,
        line_meta,
        target_by_surface,
        passage_rows,
    )
    split_rows = _split_rows(by_line, exact, target_by_surface)
    stolfi_rows, stolfi_guard = _stolfi_rows(base, occurrence_rows)

    split_raw_total = sum(int(row["raw_pair_occurrences"]) for row in split_rows)
    split_exact_total = sum(
        int(row["reader_exact_pair_occurrences"]) for row in split_rows
    )
    boundary_counts = Counter(str(row["boundary_status"]) for row in stolfi_rows)
    preference_counts = Counter(
        str(row["historical_preference"]) for row in occurrence_rows
    )
    mechanism_counts = Counter(
        str(target_by_surface[surface]["preferred_mechanism"])
        for surface in EXPECTED_SURFACES
    )
    summary: dict[str, object] = {
        "allowed_pages": int(guard["allowed_pages"]),
        "target_types": len(EXPECTED_SURFACES),
        "target_occurrences": len(occurrence_rows),
        "target_pages": len({str(row["page"]) for row in occurrence_rows}),
        "current_reader_fused_occurrences": sum(
            int(row["all_three_current_readers_fused"])
            for row in occurrence_rows
        ),
        "raw_separated_sal_x_pairs": split_raw_total,
        "reader_exact_separated_sal_x_pairs": split_exact_total,
        "raw_split_remainders": sum(
            int(row["raw_pair_occurrences"]) > 0 for row in split_rows
        ),
        "reader_exact_split_remainders": sum(
            int(row["reader_exact_pair_occurrences"]) > 0
            for row in split_rows
        ),
        "stolfi_requested_pages": len(EXPECTED_TARGET_PAGES),
        "stolfi_selected_rows": stolfi_guard["selected"],
        "stolfi_same_locus_rows": sum(
            int(row["stolfi_same_locus_present"]) for row in stolfi_rows
        ),
        "stolfi_fused_same_locus": boundary_counts[
            "FUSED_WHOLE_AT_SAME_LOCUS"
        ],
        "stolfi_sal_x_split_same_locus": boundary_counts[
            "SAL_X_SPLIT_AT_SAME_LOCUS"
        ],
        "stolfi_alternate_same_locus": boundary_counts[
            "ALTERNATE_READING_OR_OTHER_BOUNDARY"
        ],
        "stolfi_missing_same_locus": (
            boundary_counts["NO_SAME_LOCUS_ROW"]
            + boundary_counts["NO_STOLFI_ROWS_FOR_PAGE"]
        ),
        "historical_preference_counts": dict(sorted(preference_counts.items())),
        "preferred_mechanism_type_counts": dict(sorted(mechanism_counts.items())),
        "guard": guard,
        "stolfi_guard": stolfi_guard,
        "forbidden_page_rows_materialized": 0,
        "component_export_credit": 0,
        "confirmed_lexemes": 0,
    }
    expected_summary = {
        "target_types": 12,
        "target_occurrences": 14,
        "target_pages": 13,
        "current_reader_fused_occurrences": 14,
        "raw_separated_sal_x_pairs": 1,
        "reader_exact_separated_sal_x_pairs": 0,
        "stolfi_same_locus_rows": 7,
        "stolfi_fused_same_locus": 6,
        "stolfi_sal_x_split_same_locus": 0,
        "stolfi_alternate_same_locus": 1,
        "stolfi_missing_same_locus": 7,
    }
    changed = {
        key: (summary[key], expected)
        for key, expected in expected_summary.items()
        if summary[key] != expected
    }
    if changed:
        raise AssertionError(f"qualitative audit invariants changed: {changed}")

    return {
        "occurrence_rows": occurrence_rows,
        "split_rows": split_rows,
        "stolfi_rows": stolfi_rows,
        "summary": summary,
    }
