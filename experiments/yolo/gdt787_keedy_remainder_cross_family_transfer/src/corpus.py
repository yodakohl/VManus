#!/usr/bin/env python3
"""Guarded corpus and boundary reconstruction for GDT787.

The module is intentionally read-only.  :func:`compute` imports the already
established GDT782 loader, which obtains the admitted current transcription
through ``vmanus-exp query-tsv``.  The legacy Stolfi comparison is likewise
requested through that loader's ``guarded_query`` function.  No source TSV is
opened directly here, no image or new page is accessed, and ``f84``/``f84r``
must be rejected before a row can be materialised.

Returned row collections are composed only of scalar values and are therefore
ready for ``csv.DictWriter``.  The public result contains:

``raw_family_rows``
    One census row for every current complete surface ending in ``keedy``
    (38 rows; 27 have a reader-exact occurrence).
``exact_occurrence_rows``
    All 370 reader-exact complete-word occurrences, including bare ``keedy``.
``paradigm_rows``
    The complete 10-prefix by 5-tail HOT ladder (50 observed exact cells).
``raw_separated_pair_rows`` / ``exact_separated_span_rows``
    All 59 current ``X keedy`` pairs and their 20 all-reader-exact subset.
``fused_split_family_rows``
    The five left wholes attested both as fused ``Xkeedy`` and exact separated
    ``X keedy``.
``stolfi_boundary_rows`` / ``stolfi_nonbare_boundary_rows``
    Per-surface Stolfi summaries for all 27 exact surfaces and the 26 non-bare
    surfaces respectively.  The occurrence audit is also returned.

HOT/END/CLOSE strings in the paradigm are candidate analysis labels, not
translations or component exports.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

G782_REL = Path(
    "experiments/yolo/"
    "gdt782_recurrent_six_target_external_field_adjudication/src/run.py"
)
STOLFI_REL = Path("transcription/voynich_stolfi25e1_lines.tsv")

PARADIGM_PREFIXES = ("", "che", "cho", "l", "o", "ol", "qo", "qol", "sol", "y")
PARADIGM_TAILS = ("ky", "key", "keey", "kedy", "keedy")
TAIL_CANDIDATE_ROLES = {
    "ky": "HOT|BEGIN_STAGE|OPEN",
    "key": "HOT|MIDDLE_STAGE|OPEN",
    "keey": "HOT|END_STAGE|OPEN",
    "kedy": "HOT|MIDDLE_STAGE|CLOSE",
    "keedy": "HOT|END_STAGE|CLOSE",
}
HOT_CONTRAST_PREFIXES = ("qo", "o", "ol", "l", "y", "qol")
FUSED_SPLIT_PREFIXES = ("al", "cheol", "chol", "ol", "sol")

EXPECTED_GUARD = {
    "allowed_pages": 179,
    "tokens": {
        "selected": 32339,
        "skipped_forbidden": 709,
        "skipped_not_allowed": 5940,
    },
    "cross": {
        "selected": 4137,
        "skipped_forbidden": 98,
        "skipped_not_allowed": 1151,
    },
    "lines": {
        "selected": 4137,
        "skipped_forbidden": 98,
        "skipped_not_allowed": 1150,
    },
}
EXPECTED_STOLFI_GUARD = {
    "selected": 610,
    "skipped_forbidden": 33,
    "skipped_not_allowed": 2374,
}

EXPECTED_RAW = {
    "alkeedy": 2,
    "arolkeedy": 1,
    "chalkeedy": 1,
    "chekeedy": 4,
    "cheolkeedy": 2,
    "chkeedy": 1,
    "chokeedy": 2,
    "cholkeedy": 3,
    "dchekeedy": 1,
    "dolkeedy": 1,
    "dykeedy": 1,
    "keedy": 59,
    "lkeedy": 37,
    "lokeedy": 2,
    "oekeedy": 1,
    "okeedy": 94,
    "okokeedy": 1,
    "olkchokeedy": 1,
    "olkeedy": 42,
    "oykeedy": 1,
    "pcholkeedy": 1,
    "polkeedy": 1,
    "qoeekeedy": 1,
    "qokeedy": 292,
    "qolkeedy": 7,
    "qoolkeedy": 1,
    "rokeedy": 1,
    "rolkeedy": 1,
    "salkeedy": 1,
    "sheokeedy": 1,
    "sheolkeedy": 1,
    "shkakeedy": 1,
    "shkeedy": 1,
    "sholkeedy": 2,
    "sokeedy": 2,
    "solkeedy": 3,
    "tsheokeedy": 1,
    "ykeedy": 26,
}
EXPECTED_EXACT = {
    "alkeedy": 2,
    "chalkeedy": 1,
    "chekeedy": 3,
    "cheolkeedy": 1,
    "chkeedy": 1,
    "chokeedy": 2,
    "cholkeedy": 1,
    "dolkeedy": 1,
    "dykeedy": 1,
    "keedy": 22,
    "lkeedy": 23,
    "oekeedy": 1,
    "okeedy": 49,
    "olkchokeedy": 1,
    "olkeedy": 25,
    "qoeekeedy": 1,
    "qokeedy": 201,
    "qolkeedy": 5,
    "qoolkeedy": 1,
    "rolkeedy": 1,
    "salkeedy": 1,
    "sheokeedy": 1,
    "sheolkeedy": 1,
    "sholkeedy": 1,
    "sokeedy": 1,
    "solkeedy": 3,
    "ykeedy": 19,
}

# (raw current count, reader-exact count), in the fixed 10 x 5 grid.
EXPECTED_PARADIGM = {
    "": {
        "ky": (29, 12), "key": (13, 8), "keey": (43, 27),
        "kedy": (42, 16), "keedy": (59, 22),
    },
    "che": {
        "ky": (55, 50), "key": (5, 5), "keey": (3, 3),
        "kedy": (5, 2), "keedy": (4, 3),
    },
    "cho": {
        "ky": (32, 30), "key": (4, 4), "keey": (10, 9),
        "kedy": (4, 2), "keedy": (2, 2),
    },
    "l": {
        "ky": (19, 16), "key": (7, 7), "keey": (38, 34),
        "kedy": (26, 15), "keedy": (37, 23),
    },
    "o": {
        "ky": (89, 80), "key": (40, 36), "keey": (138, 116),
        "kedy": (87, 47), "keedy": (94, 49),
    },
    "ol": {
        "ky": (20, 17), "key": (12, 10), "keey": (35, 32),
        "kedy": (22, 15), "keedy": (42, 25),
    },
    "qo": {
        "ky": (138, 125), "key": (96, 88), "keey": (280, 264),
        "kedy": (249, 164), "keedy": (292, 201),
    },
    "qol": {
        "ky": (4, 4), "key": (1, 1), "keey": (4, 4),
        "kedy": (1, 1), "keedy": (7, 5),
    },
    "sol": {
        "ky": (1, 1), "key": (1, 1), "keey": (3, 3),
        "kedy": (2, 1), "keedy": (3, 3),
    },
    "y": {
        "ky": (12, 10), "key": (5, 5), "keey": (49, 41),
        "kedy": (18, 6), "keedy": (26, 19),
    },
}

EXPECTED_EXACT_SPLITS = {
    ("f34v.9", "qokeey"),
    ("f46r.6", "shee"),
    ("f66v.8", "qokol"),
    ("f75r.13", "pchedy"),
    ("f75r.36", "sol"),
    ("f75r.40", "dal"),
    ("f76r.51", "shey"),
    ("f76v.39", "ol"),
    ("f81v.1", "shey"),
    ("f106v.32", "sheky"),
    ("f108r.21", "shokal"),
    ("f111r.17", "oteed"),
    ("f111v.2", "cheol"),
    ("f111v.37", "chey"),
    ("f112r.40", "qokal"),
    ("f112v.32", "shee"),
    ("f114r.29", "oeedy"),
    ("f115r.10", "qokchey"),
    ("f116r.15", "al"),
    ("f116r.20", "chol"),
}
EXPECTED_FUSED_SPLIT = {
    "al": (2, 1),
    "cheol": (1, 1),
    "chol": (1, 1),
    "ol": (25, 1),
    "sol": (3, 1),
}
EXPECTED_CURRENT_ALT_SPLITS = {
    ("f80v.32", "arolkeedy", "it2a_clean"),
    ("f81v.8", "qolkeedy", "it2a_clean"),
    ("f108v.34", "cholkeedy", "it2a_clean"),
    ("f115r.32", "qokeedy", "rf1b_clean"),
}


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


def _load_g782(repo_root: Path):
    path = repo_root / G782_REL
    spec = importlib.util.spec_from_file_location("gdt782_guarded_for_gdt787", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import guarded GDT782 loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if Path(module.ROOT).resolve() != repo_root:
        raise AssertionError("GDT782 loader resolved a different repository")
    return module


def _physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    return match.group(1) if match else page


def _page_key(page: str) -> tuple[int, str]:
    match = re.match(r"^f(\d+)(.*)$", page)
    return (int(match.group(1)), match.group(2)) if match else (10**9, page)


def _locus_key(locus: str) -> tuple[int, str, int]:
    page, _, line = locus.partition(".")
    pnum, suffix = _page_key(page)
    return pnum, suffix, int(line) if line.isdigit() else 10**9


def _joined(values: Iterable[str], *, page_sort: bool = False) -> str:
    chosen = set(values)
    ordered = sorted(chosen, key=_page_key if page_sort else None)
    return "|".join(ordered) or "NONE"


def _counter_text(counter: Mapping[object, int]) -> str:
    return "|".join(
        f"{key}:{counter[key]}" for key in sorted(counter, key=lambda item: str(item))
    ) or "NONE"


def _line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def _pair_count(tokens: Sequence[str], left: str, right: str) -> int:
    return sum(a == left and b == right for a, b in zip(tokens, tokens[1:]))


def _assert_no_sealed(rows: Iterable[Mapping[str, object]]) -> None:
    forbidden = [str(row.get("page", "")) for row in rows if str(row.get("page", "")).startswith("f84")]
    if forbidden:
        raise AssertionError(f"sealed f84/f84r row materialised: {forbidden[:3]}")


def _raw_and_exact_occurrences(
    by_line: Mapping[str, list[dict[str, str]]],
    exact: Mapping[tuple[str, int], int],
    cross: Mapping[str, Mapping[str, str]],
    line_meta: Mapping[str, Mapping[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    raw_rows: list[dict[str, object]] = []
    exact_rows: list[dict[str, object]] = []
    for locus in sorted(by_line, key=_locus_key):
        line = by_line[locus]
        meta = line_meta[locus]
        surface_rank: Counter[str] = Counter()
        for ordinal, token in enumerate(line, 1):
            surface = token["eva"]
            surface_rank[surface] += 1
            if not surface.endswith("keedy"):
                continue
            is_exact = int(exact[(locus, int(token["token_index"]))])
            row: dict[str, object] = {
                "surface": surface,
                "family_class": "BARE_KEEDY" if surface == "keedy" else "LEFT_WHOLE_PLUS_KEEDY",
                "left_whole": "NONE" if surface == "keedy" else surface[:-5],
                "page": token["page"],
                "physical_folio": _physical_folio(token["page"]),
                "locus": locus,
                "token_ordinal": ordinal,
                "token_index": int(token["token_index"]),
                "surface_rank_in_current_line": surface_rank[surface],
                "line_token_count": len(line),
                "line_position": _line_position(ordinal, len(line)),
                "norm_position": 0.5 if len(line) == 1 else (ordinal - 1) / (len(line) - 1),
                "section": token["section"],
                "language": token["language"],
                "hand": token["hand"],
                "paragraph_start_line": int(meta["paragraph_start"]),
                "paragraph_end_line": int(meta["paragraph_end"]),
                "true_paragraph_start": int(meta["paragraph_start"] == "1" and ordinal == 1),
                "true_paragraph_end": int(meta["paragraph_end"] == "1" and ordinal == len(line)),
                "left_surface": line[ordinal - 2]["eva"] if ordinal > 1 else "EDGE",
                "right_surface": line[ordinal]["eva"] if ordinal < len(line) else "EDGE",
                "left_reader_exact": (
                    int(exact[(locus, int(line[ordinal - 2]["token_index"]))])
                    if ordinal > 1 else 0
                ),
                "right_reader_exact": (
                    int(exact[(locus, int(line[ordinal]["token_index"]))])
                    if ordinal < len(line) else 0
                ),
                "reader_exact": is_exact,
                "zl3b_surface_count": cross[locus]["zl3b_clean"].split().count(surface),
                "it2a_surface_count": cross[locus]["it2a_clean"].split().count(surface),
                "rf1b_surface_count": cross[locus]["rf1b_clean"].split().count(surface),
                "reader_exact_method": "OCCURRENCE_RANK_LE_MIN_THREE_READER_SURFACE_COUNTS",
                "current_line": " ".join(item["eva"] for item in line),
                "component_export_credit": 0,
            }
            raw_rows.append(row)
            if is_exact:
                exact_rows.append(dict(row))

    for number, row in enumerate(exact_rows, 1):
        row["occurrence_id"] = f"G787-O{number:03d}"
    return raw_rows, exact_rows


def _family_rows(
    raw_occurrences: Sequence[Mapping[str, object]],
    exact_occurrences: Sequence[Mapping[str, object]],
    alternate_splits: Mapping[str, Sequence[tuple[str, str]]],
) -> list[dict[str, object]]:
    raw_by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    exact_by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in raw_occurrences:
        raw_by_surface[str(row["surface"])].append(row)
    for row in exact_occurrences:
        exact_by_surface[str(row["surface"])].append(row)

    output: list[dict[str, object]] = []
    for surface in sorted(raw_by_surface):
        raw = raw_by_surface[surface]
        exact = exact_by_surface.get(surface, [])
        position_counts = Counter(str(row["line_position"]) for row in exact)
        register_counts = Counter(
            f"{row['section']}|{row['language']}|{row['hand']}" for row in exact
        )
        split_candidates = alternate_splits.get(surface, [])
        output.append({
            "surface": surface,
            "family_class": "BARE_KEEDY" if surface == "keedy" else "LEFT_WHOLE_PLUS_KEEDY",
            "left_whole": "NONE" if surface == "keedy" else surface[:-5],
            "raw_occurrences": len(raw),
            "raw_page_count": len({str(row["page"]) for row in raw}),
            "raw_pages": _joined((str(row["page"]) for row in raw), page_sort=True),
            "raw_physical_folio_count": len({str(row["physical_folio"]) for row in raw}),
            "raw_physical_folios": _joined((str(row["physical_folio"]) for row in raw), page_sort=True),
            "raw_locus_count": len({str(row["locus"]) for row in raw}),
            "reader_exact_surface": int(bool(exact)),
            "reader_exact_occurrences": len(exact),
            "reader_exact_page_count": len({str(row["page"]) for row in exact}),
            "reader_exact_pages": _joined((str(row["page"]) for row in exact), page_sort=True),
            "reader_exact_physical_folio_count": len({str(row["physical_folio"]) for row in exact}),
            "reader_exact_physical_folios": _joined((str(row["physical_folio"]) for row in exact), page_sort=True),
            "reader_exact_locus_count": len({str(row["locus"]) for row in exact}),
            "exact_first": position_counts["FIRST"],
            "exact_middle": position_counts["MIDDLE"],
            "exact_last": position_counts["LAST"],
            "exact_single": position_counts["SINGLE"],
            "exact_paragraph_start_lines": sum(int(row["paragraph_start_line"]) for row in exact),
            "exact_paragraph_end_lines": sum(int(row["paragraph_end_line"]) for row in exact),
            "exact_true_paragraph_starts": sum(int(row["true_paragraph_start"]) for row in exact),
            "exact_true_paragraph_ends": sum(int(row["true_paragraph_end"]) for row in exact),
            "exact_register_distribution": _counter_text(register_counts),
            "current_alternate_reader_split_candidates": len(split_candidates),
            "current_alternate_reader_split_loci": _joined(item[0] for item in split_candidates),
            "current_alternate_reader_split_sources": _joined(item[1] for item in split_candidates),
            "component_export_credit": 0,
        })
    return output


def _paradigm_rows(
    raw_counts: Mapping[str, int],
    exact_counts: Mapping[str, int],
    exact_by_surface: Mapping[str, Sequence[Mapping[str, object]]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for prefix_index, prefix in enumerate(PARADIGM_PREFIXES, 1):
        for tail_index, tail in enumerate(PARADIGM_TAILS, 1):
            surface = prefix + tail
            rows = exact_by_surface.get(surface, [])
            observed = (raw_counts.get(surface, 0), exact_counts.get(surface, 0))
            if observed != EXPECTED_PARADIGM[prefix][tail]:
                raise AssertionError(
                    f"paradigm cell changed: {prefix!r}+{tail!r}: {observed}"
                )
            positions = Counter(str(row["line_position"]) for row in rows)
            output.append({
                "cell_id": f"G787-P{prefix_index:02d}-{tail_index:02d}",
                "prefix": prefix or "BARE",
                "tail": tail,
                "surface": surface,
                "tail_candidate_role_not_translation": TAIL_CANDIDATE_ROLES[tail],
                "raw_occurrences": observed[0],
                "reader_exact_occurrences": observed[1],
                "reader_exact_page_count": len({str(row["page"]) for row in rows}),
                "reader_exact_pages": _joined((str(row["page"]) for row in rows), page_sort=True),
                "reader_exact_physical_folio_count": len({str(row["physical_folio"]) for row in rows}),
                "reader_exact_physical_folios": _joined((str(row["physical_folio"]) for row in rows), page_sort=True),
                "exact_first": positions["FIRST"],
                "exact_middle": positions["MIDDLE"],
                "exact_last": positions["LAST"],
                "exact_single": positions["SINGLE"],
                "candidate_semantic_credit": 0,
                "component_export_credit": 0,
            })
    return output


def _selected_exact_surface_rows(
    by_line: Mapping[str, list[dict[str, str]]],
    exact: Mapping[tuple[str, int], int],
    surfaces: set[str],
) -> dict[str, list[dict[str, object]]]:
    """Build the small positional index needed by the 50-cell paradigm."""
    output: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for locus in sorted(by_line, key=_locus_key):
        line = by_line[locus]
        for ordinal, token in enumerate(line, 1):
            surface = token["eva"]
            if surface not in surfaces:
                continue
            if not exact[(locus, int(token["token_index"]))]:
                continue
            output[surface].append({
                "surface": surface,
                "page": token["page"],
                "physical_folio": _physical_folio(token["page"]),
                "locus": locus,
                "line_position": _line_position(ordinal, len(line)),
            })
    return dict(output)


def _separated_pairs(
    by_line: Mapping[str, list[dict[str, str]]],
    exact: Mapping[tuple[str, int], int],
    cross: Mapping[str, Mapping[str, str]],
    line_meta: Mapping[str, Mapping[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    raw_rows: list[dict[str, object]] = []
    for locus in sorted(by_line, key=_locus_key):
        line = by_line[locus]
        for index, right in enumerate(line):
            if right["eva"] != "keedy" or index == 0:
                continue
            left = line[index - 1]
            left_exact = int(exact[(locus, int(left["token_index"]))])
            right_exact = int(exact[(locus, int(right["token_index"]))])
            reader_pair_counts = {
                name: _pair_count(cross[locus][name].split(), left["eva"], "keedy")
                for name in ("zl3b_clean", "it2a_clean", "rf1b_clean")
            }
            row: dict[str, object] = {
                "page": right["page"],
                "physical_folio": _physical_folio(right["page"]),
                "locus": locus,
                "left_surface": left["eva"],
                "right_surface": "keedy",
                "separated_pair": f"{left['eva']} keedy",
                "left_token_ordinal": index,
                "right_token_ordinal": index + 1,
                "line_token_count": len(line),
                "line_position_of_keedy": _line_position(index + 1, len(line)),
                "paragraph_start_line": int(line_meta[locus]["paragraph_start"]),
                "paragraph_end_line": int(line_meta[locus]["paragraph_end"]),
                "section": right["section"],
                "language": right["language"],
                "hand": right["hand"],
                "left_reader_exact": left_exact,
                "keedy_reader_exact": right_exact,
                "both_tokens_reader_exact": int(left_exact and right_exact),
                "zl3b_exact_pair_count": reader_pair_counts["zl3b_clean"],
                "it2a_exact_pair_count": reader_pair_counts["it2a_clean"],
                "rf1b_exact_pair_count": reader_pair_counts["rf1b_clean"],
                "all_three_readers_preserve_pair": int(all(reader_pair_counts.values())),
                "current_line": " ".join(item["eva"] for item in line),
                "component_export_credit": 0,
            }
            raw_rows.append(row)

    exact_rows = [dict(row) for row in raw_rows if int(row["both_tokens_reader_exact"])]
    for number, row in enumerate(exact_rows, 1):
        row["span_id"] = f"G787-S{number:02d}"
    return raw_rows, exact_rows


def _current_alternate_splits(
    raw_occurrences: Sequence[Mapping[str, object]],
    cross: Mapping[str, Mapping[str, str]],
) -> tuple[dict[str, list[tuple[str, str]]], set[tuple[str, str, str]]]:
    by_surface: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    observed: set[tuple[str, str, str]] = set()
    for row in raw_occurrences:
        surface = str(row["surface"])
        if surface == "keedy":
            continue
        left = surface[:-5]
        locus = str(row["locus"])
        for reader in ("zl3b_clean", "it2a_clean", "rf1b_clean"):
            if _pair_count(cross[locus][reader].split(), left, "keedy"):
                key = (locus, surface, reader)
                observed.add(key)
                by_surface[surface].append((locus, reader.replace("_clean", "")))
    for surface in by_surface:
        by_surface[surface] = sorted(set(by_surface[surface]))
    return dict(by_surface), observed


def _stolfi_audit(
    base,
    exact_occurrences: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, int]]:
    pages = {str(row["page"]) for row in exact_occurrences}
    if len(pages) != 60 or any(page.startswith("f84") for page in pages):
        raise AssertionError(f"unexpected Stolfi request pages: {sorted(pages)}")
    queried, guard = base.guarded_query(
        STOLFI_REL, pages, "page,locus,raw_text,clean_text",
    )
    if guard != EXPECTED_STOLFI_GUARD:
        raise AssertionError(f"Stolfi guard changed: {guard}")
    _assert_no_sealed(queried)
    by_locus: dict[str, dict[str, str]] = {}
    by_page: Counter[str] = Counter()
    for row in queried:
        if row["locus"] in by_locus:
            raise AssertionError(f"duplicate Stolfi locus: {row['locus']}")
        by_locus[row["locus"]] = row
        by_page[row["page"]] += 1

    occurrence_rows: list[dict[str, object]] = []
    for target in exact_occurrences:
        page = str(target["page"])
        locus = str(target["locus"])
        surface = str(target["surface"])
        left = "" if surface == "keedy" else surface[:-5]
        same = by_locus.get(locus)
        whole_count = 0
        split_count = 0
        separator = "NONE"
        if same is None:
            status = "NO_SAME_LOCUS_ROW" if by_page[page] else "NO_STOLFI_ROWS_FOR_PAGE"
        else:
            tokens = same["clean_text"].split()
            whole_count = tokens.count(surface)
            split_count = _pair_count(tokens, left, "keedy") if left else 0
            rank = int(target["surface_rank_in_current_line"])
            if rank <= whole_count:
                status = (
                    "BARE_KEEDY_AT_SAME_LOCUS" if surface == "keedy"
                    else "FUSED_WHOLE_AT_SAME_LOCUS"
                )
            elif left and rank <= whole_count + split_count:
                status = "SPLIT_LEFT_KEEDY_AT_SAME_LOCUS"
            elif "keedy" in tokens:
                status = "OTHER_KEEDY_BOUNDARY_AT_SAME_LOCUS"
            else:
                status = "ALTERNATE_READING_AT_SAME_LOCUS"
            if left:
                marker = re.search(
                    rf"(?<![A-Za-z]){re.escape(left)}([.,])keedy(?![A-Za-z])",
                    same["raw_text"],
                )
                if marker:
                    separator = marker.group(1)

        occurrence_rows.append({
            "occurrence_id": target["occurrence_id"],
            "surface": surface,
            "left_whole": left or "NONE",
            "page": page,
            "physical_folio": target["physical_folio"],
            "locus": locus,
            "stolfi_page_row_count": by_page[page],
            "stolfi_same_locus_present": int(same is not None),
            "stolfi_whole_count": whole_count,
            "stolfi_split_left_keedy_count": split_count,
            "stolfi_raw_split_separator": separator,
            "boundary_status": status,
            "component_export_credit": 0,
        })
    return occurrence_rows, queried, guard


def _stolfi_summaries(
    exact_occurrences: Sequence[Mapping[str, object]],
    audit_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    target_by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    audit_by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in exact_occurrences:
        target_by_surface[str(row["surface"])].append(row)
    for row in audit_rows:
        audit_by_surface[str(row["surface"])].append(row)

    output: list[dict[str, object]] = []
    for surface in sorted(target_by_surface):
        targets = target_by_surface[surface]
        audits = audit_by_surface[surface]
        statuses = Counter(str(row["boundary_status"]) for row in audits)
        same_loci = [
            str(row["locus"]) for row in audits if int(row["stolfi_same_locus_present"])
        ]
        split_loci = [
            str(row["locus"]) for row in audits
            if row["boundary_status"] == "SPLIT_LEFT_KEEDY_AT_SAME_LOCUS"
        ]
        output.append({
            "surface": surface,
            "family_class": "BARE_KEEDY" if surface == "keedy" else "LEFT_WHOLE_PLUS_KEEDY",
            "left_whole": "NONE" if surface == "keedy" else surface[:-5],
            "current_reader_exact_occurrences": len(targets),
            "current_reader_complete_surface_boundary_occurrences": len(targets),
            "stolfi_page_available_occurrences": len(targets) - statuses["NO_STOLFI_ROWS_FOR_PAGE"],
            "stolfi_same_locus_occurrences": sum(int(row["stolfi_same_locus_present"]) for row in audits),
            "stolfi_fused_whole_occurrences": statuses["FUSED_WHOLE_AT_SAME_LOCUS"],
            "stolfi_bare_keedy_occurrences": statuses["BARE_KEEDY_AT_SAME_LOCUS"],
            "stolfi_split_left_keedy_occurrences": statuses["SPLIT_LEFT_KEEDY_AT_SAME_LOCUS"],
            "stolfi_other_keedy_boundary_occurrences": statuses["OTHER_KEEDY_BOUNDARY_AT_SAME_LOCUS"],
            "stolfi_alternate_reading_occurrences": statuses["ALTERNATE_READING_AT_SAME_LOCUS"],
            "stolfi_no_same_locus_occurrences": statuses["NO_SAME_LOCUS_ROW"],
            "stolfi_no_page_occurrences": statuses["NO_STOLFI_ROWS_FOR_PAGE"],
            "stolfi_same_loci": _joined(same_loci),
            "stolfi_split_loci": _joined(split_loci),
            "boundary_evidence_scope": "LEGACY_TRANSCRIPTION_SENSITIVITY_NOT_INDEPENDENT_SEMANTICS",
            "component_export_credit": 0,
        })
    return output


def _fused_split_summaries(
    exact_by_surface: Mapping[str, Sequence[Mapping[str, object]]],
    exact_splits: Sequence[Mapping[str, object]],
    stolfi_by_surface: Mapping[str, Mapping[str, object]],
) -> list[dict[str, object]]:
    split_by_left: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in exact_splits:
        split_by_left[str(row["left_surface"])].append(row)
    output: list[dict[str, object]] = []
    for left in FUSED_SPLIT_PREFIXES:
        surface = left + "keedy"
        fused = exact_by_surface[surface]
        separated = split_by_left[left]
        observed = (len(fused), len(separated))
        if observed != EXPECTED_FUSED_SPLIT[left]:
            raise AssertionError(f"fused/split family changed for {left}: {observed}")
        stolfi = stolfi_by_surface[surface]
        output.append({
            "left_whole": left,
            "fused_surface": surface,
            "fused_reader_exact_occurrences": len(fused),
            "fused_pages": _joined((str(row["page"]) for row in fused), page_sort=True),
            "fused_physical_folios": _joined((str(row["physical_folio"]) for row in fused), page_sort=True),
            "separated_reader_exact_occurrences": len(separated),
            "separated_pair": f"{left} keedy",
            "separated_loci": _joined(str(row["locus"]) for row in separated),
            "separated_pages": _joined((str(row["page"]) for row in separated), page_sort=True),
            "stolfi_fused_occurrences": stolfi["stolfi_fused_whole_occurrences"],
            "stolfi_split_occurrences": stolfi["stolfi_split_left_keedy_occurrences"],
            "boundary_bridge_only": 1,
            "semantic_credit": 0,
            "component_export_credit": 0,
        })
    return output


def compute(repo_root: Path | str) -> dict[str, object]:
    """Return the complete guarded GDT787 corpus reconstruction.

    The function performs no writes.  Every returned row list is TSV-ready;
    dictionaries under ``diagnostics`` contain only scalar values.
    """
    root = Path(repo_root).resolve()
    if not (root / "AGENTS.md").is_file() or not (root / ".git").exists():
        raise RuntimeError(f"not the VManus repository root: {root}")
    base = _load_g782(root)
    by_line, exact, cross, line_meta, _cells, guard = base.load_context()
    if guard != EXPECTED_GUARD:
        raise AssertionError(f"guarded current source changed: {guard}")
    materialised_tokens = [token for line in by_line.values() for token in line]
    _assert_no_sealed(materialised_tokens)

    raw_occurrences, exact_occurrences = _raw_and_exact_occurrences(
        by_line, exact, cross, line_meta,
    )
    raw_counts = Counter(str(row["surface"]) for row in raw_occurrences)
    exact_counts = Counter(str(row["surface"]) for row in exact_occurrences)
    global_raw_counts = Counter(
        token["eva"] for line in by_line.values() for token in line
    )
    global_exact_counts: Counter[str] = Counter()
    for locus, line in by_line.items():
        for token in line:
            if exact[(locus, int(token["token_index"]))]:
                global_exact_counts[token["eva"]] += 1
    if dict(raw_counts) != EXPECTED_RAW:
        raise AssertionError(f"raw keedy-family census changed: {dict(raw_counts)}")
    if dict(exact_counts) != EXPECTED_EXACT:
        raise AssertionError(f"exact keedy-family census changed: {dict(exact_counts)}")

    if len(raw_occurrences) != 601 or len(exact_occurrences) != 370:
        raise AssertionError("keedy-family occurrence totals changed")
    if (
        sum(surface != "keedy" for surface in raw_counts) != 37
        or sum(surface != "keedy" for surface in exact_counts) != 26
        or sum(count for surface, count in raw_counts.items() if surface != "keedy") != 542
        or sum(count for surface, count in exact_counts.items() if surface != "keedy") != 348
    ):
        raise AssertionError("bare/non-bare keedy partition changed")

    alternate_by_surface, alternate_keys = _current_alternate_splits(
        raw_occurrences, cross,
    )
    if alternate_keys != EXPECTED_CURRENT_ALT_SPLITS:
        raise AssertionError(f"current-reader alternate splits changed: {alternate_keys}")
    if any(
        int(row["reader_exact"])
        for row in raw_occurrences
        if (str(row["locus"]), str(row["surface"]))
        in {(locus, surface) for locus, surface, _reader in alternate_keys}
    ):
        raise AssertionError("an alternate split candidate became reader-exact")

    family_rows = _family_rows(
        raw_occurrences, exact_occurrences, alternate_by_surface,
    )
    if len(family_rows) != 38 or sum(int(row["reader_exact_surface"]) for row in family_rows) != 27:
        raise AssertionError("family row shape changed")

    exact_by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in exact_occurrences:
        exact_by_surface[str(row["surface"])].append(row)
    paradigm_surfaces = {
        prefix + tail for prefix in PARADIGM_PREFIXES for tail in PARADIGM_TAILS
    }
    paradigm_exact_by_surface = _selected_exact_surface_rows(
        by_line, exact, paradigm_surfaces,
    )
    paradigm_rows = _paradigm_rows(
        global_raw_counts, global_exact_counts, paradigm_exact_by_surface,
    )
    if (
        len(paradigm_rows) != 50
        or sum(int(row["raw_occurrences"]) for row in paradigm_rows) != 2208
        or sum(int(row["reader_exact_occurrences"]) for row in paradigm_rows) != 1664
        or any(int(row["reader_exact_occurrences"]) == 0 for row in paradigm_rows)
    ):
        raise AssertionError("50-cell paradigm totals changed")

    raw_split_rows, exact_split_rows = _separated_pairs(
        by_line, exact, cross, line_meta,
    )
    if len(raw_split_rows) != 59 or len({str(row["left_surface"]) for row in raw_split_rows}) != 37:
        raise AssertionError("raw X-keedy pair census changed")
    if (
        len(exact_split_rows) != 20
        or len({str(row["left_surface"]) for row in exact_split_rows}) != 18
        or {(str(row["locus"]), str(row["left_surface"])) for row in exact_split_rows}
        != EXPECTED_EXACT_SPLITS
        or not all(int(row["all_three_readers_preserve_pair"]) for row in exact_split_rows)
    ):
        raise AssertionError("reader-exact separated X-keedy span census changed")

    stolfi_occurrence_rows, _stolfi_source_rows, stolfi_guard = _stolfi_audit(
        base, exact_occurrences,
    )
    status_counts = Counter(str(row["boundary_status"]) for row in stolfi_occurrence_rows)
    expected_status = Counter({
        "NO_STOLFI_ROWS_FOR_PAGE": 184,
        "NO_SAME_LOCUS_ROW": 119,
        "FUSED_WHOLE_AT_SAME_LOCUS": 59,
        "BARE_KEEDY_AT_SAME_LOCUS": 7,
        "SPLIT_LEFT_KEEDY_AT_SAME_LOCUS": 1,
    })
    if status_counts != expected_status:
        raise AssertionError(f"Stolfi occurrence boundary census changed: {status_counts}")
    stolfi_rows = _stolfi_summaries(exact_occurrences, stolfi_occurrence_rows)
    stolfi_nonbare_rows = [row for row in stolfi_rows if row["surface"] != "keedy"]
    if len(stolfi_rows) != 27 or len(stolfi_nonbare_rows) != 26:
        raise AssertionError("Stolfi summary row shape changed")
    nonbare_audit = [row for row in stolfi_occurrence_rows if row["surface"] != "keedy"]
    nonbare_status = Counter(str(row["boundary_status"]) for row in nonbare_audit)
    if nonbare_status != Counter({
        "NO_STOLFI_ROWS_FOR_PAGE": 171,
        "NO_SAME_LOCUS_ROW": 117,
        "FUSED_WHOLE_AT_SAME_LOCUS": 59,
        "SPLIT_LEFT_KEEDY_AT_SAME_LOCUS": 1,
    }):
        raise AssertionError(f"non-bare Stolfi boundary census changed: {nonbare_status}")

    stolfi_by_surface = {str(row["surface"]): row for row in stolfi_rows}
    fused_split_rows = _fused_split_summaries(
        exact_by_surface, exact_split_rows, stolfi_by_surface,
    )
    if len(fused_split_rows) != 5:
        raise AssertionError("fused/split family summary count changed")

    hot_contrast_rows: list[dict[str, object]] = []
    for prefix in HOT_CONTRAST_PREFIXES:
        target, control = prefix + "keedy", prefix + "teedy"
        if not exact_by_surface.get(target):
            raise AssertionError(f"missing HOT target: {target}")
        # teedy is outside the keedy family, so derive its exact occurrences
        # directly from the guarded current token rows.
        control_raw = 0
        control_exact = 0
        for locus, line in by_line.items():
            for token in line:
                if token["eva"] != control:
                    continue
                control_raw += 1
                control_exact += int(exact[(locus, int(token["token_index"]))])
        expected_control = {
            "qo": (74, 51), "o": (88, 66), "ol": (3, 2),
            "l": (6, 3), "y": (27, 19), "qol": (1, 1),
        }[prefix]
        if (control_raw, control_exact) != expected_control:
            raise AssertionError(f"HOT contrast changed for {prefix}: {(control_raw, control_exact)}")
        hot_contrast_rows.append({
            "prefix": prefix,
            "hot_candidate_surface": target,
            "hot_candidate_raw_occurrences": raw_counts[target],
            "hot_candidate_reader_exact_occurrences": exact_counts[target],
            "cold_control_surface": control,
            "cold_control_raw_occurrences": control_raw,
            "cold_control_reader_exact_occurrences": control_exact,
            "contrast_candidate_not_translation": "HOT_VS_COLD_AT_END_CLOSED",
            "semantic_credit": 0,
            "component_export_credit": 0,
        })
    if (
        len(hot_contrast_rows) != 6
        or sum(int(row["hot_candidate_reader_exact_occurrences"]) for row in hot_contrast_rows) != 322
        or sum(int(row["cold_control_reader_exact_occurrences"]) for row in hot_contrast_rows) != 142
    ):
        raise AssertionError("six-prefix HOT contrast deck changed")

    register_counts = Counter(
        f"{row['section']}|{row['language']}|{row['hand']}" for row in exact_occurrences
    )
    position_counts = Counter(str(row["line_position"]) for row in exact_occurrences)
    diagnostics: dict[str, object] = {
        "allowed_pages": guard["allowed_pages"],
        "raw_family_rows": len(family_rows),
        "raw_family_occurrences": len(raw_occurrences),
        "reader_exact_family_surfaces": len(exact_counts),
        "reader_exact_family_occurrences": len(exact_occurrences),
        "reader_exact_family_page_labels": len({str(row["page"]) for row in exact_occurrences}),
        "reader_exact_family_physical_folios": len({str(row["physical_folio"]) for row in exact_occurrences}),
        "reader_exact_family_loci": len({str(row["locus"]) for row in exact_occurrences}),
        "reader_exact_nonbare_surfaces": len(exact_counts) - 1,
        "reader_exact_nonbare_occurrences": len(exact_occurrences) - exact_counts["keedy"],
        "standalone_keedy_raw_occurrences": raw_counts["keedy"],
        "standalone_keedy_reader_exact_occurrences": exact_counts["keedy"],
        "exact_line_position_distribution": _counter_text(position_counts),
        "exact_register_distribution": _counter_text(register_counts),
        "exact_paragraph_start_lines": sum(int(row["paragraph_start_line"]) for row in exact_occurrences),
        "exact_paragraph_end_lines": sum(int(row["paragraph_end_line"]) for row in exact_occurrences),
        "exact_true_paragraph_starts": sum(int(row["true_paragraph_start"]) for row in exact_occurrences),
        "exact_true_paragraph_ends": sum(int(row["true_paragraph_end"]) for row in exact_occurrences),
        "paradigm_cells": len(paradigm_rows),
        "paradigm_observed_exact_cells": sum(int(row["reader_exact_occurrences"]) > 0 for row in paradigm_rows),
        "paradigm_raw_occurrences": sum(int(row["raw_occurrences"]) for row in paradigm_rows),
        "paradigm_reader_exact_occurrences": sum(int(row["reader_exact_occurrences"]) for row in paradigm_rows),
        "raw_separated_x_keedy_spans": len(raw_split_rows),
        "raw_separated_left_types": len({str(row["left_surface"]) for row in raw_split_rows}),
        "reader_exact_separated_x_keedy_spans": len(exact_split_rows),
        "reader_exact_separated_left_types": len({str(row["left_surface"]) for row in exact_split_rows}),
        "fused_and_split_left_types": len(fused_split_rows),
        "current_alternate_reader_split_candidates": len(alternate_keys),
        "current_alternate_split_candidates_reader_exact": 0,
        "stolfi_requested_pages": 60,
        "stolfi_selected_rows": stolfi_guard["selected"],
        "stolfi_same_locus_occurrences": 67,
        "stolfi_fused_nonbare_occurrences": status_counts["FUSED_WHOLE_AT_SAME_LOCUS"],
        "stolfi_split_nonbare_occurrences": status_counts["SPLIT_LEFT_KEEDY_AT_SAME_LOCUS"],
        "stolfi_bare_matches": status_counts["BARE_KEEDY_AT_SAME_LOCUS"],
        "stolfi_no_same_locus_occurrences": status_counts["NO_SAME_LOCUS_ROW"],
        "stolfi_no_page_occurrences": status_counts["NO_STOLFI_ROWS_FOR_PAGE"],
        "sealed_f84_rows_materialised": 0,
        "component_export_credit": 0,
    }
    if (
        diagnostics["reader_exact_family_page_labels"] != 60
        or diagnostics["reader_exact_family_physical_folios"] != 36
        or diagnostics["reader_exact_family_loci"] != 319
        or position_counts != Counter({"MIDDLE": 317, "FIRST": 39, "LAST": 14})
        or diagnostics["exact_paragraph_start_lines"] != 60
        or diagnostics["exact_paragraph_end_lines"] != 36
        or diagnostics["exact_true_paragraph_starts"] != 3
        or diagnostics["exact_true_paragraph_ends"] != 5
    ):
        raise AssertionError(f"family placement diagnostics changed: {diagnostics}")

    guarded_source_stats = []
    for source in ("tokens", "cross", "lines"):
        guarded_source_stats.append({"source": source, **guard[source]})
    guarded_source_stats.append({"source": "stolfi", **stolfi_guard})

    return {
        "raw_family_rows": family_rows,
        "exact_occurrence_rows": exact_occurrences,
        "paradigm_rows": paradigm_rows,
        "hot_contrast_rows": hot_contrast_rows,
        "raw_separated_pair_rows": raw_split_rows,
        "exact_separated_span_rows": exact_split_rows,
        "fused_split_family_rows": fused_split_rows,
        "stolfi_boundary_occurrence_rows": stolfi_occurrence_rows,
        "stolfi_boundary_rows": stolfi_rows,
        "stolfi_nonbare_boundary_rows": stolfi_nonbare_rows,
        "guarded_source_stats": guarded_source_stats,
        "diagnostics": diagnostics,
    }


def main() -> int:
    result = compute(find_repo_root(Path(__file__).resolve()))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
