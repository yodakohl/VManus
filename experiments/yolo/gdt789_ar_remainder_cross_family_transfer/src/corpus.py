#!/usr/bin/env python3
"""Guarded corpus, boundary, and construction census for GDT789.

The target is the complete written ``*ar`` family.  EVA strings remain opaque
surface labels: suffix membership and boundary alternation do not assign a
sound, Latin letter, or plaintext meaning to ``a`` or ``r``.
"""

from __future__ import annotations

import importlib.util
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

SQUARE_PREFIXES = ("ch", "che", "o", "oke", "ol", "ote", "qo", "qoke", "sh", "she")
SQUARE_SENSITIVITY_PREFIXES = SQUARE_PREFIXES + ("cheo", "dch", "lche", "opch", "p", "qokee")
SQUARE_TAILS = ("al", "dal", "ar", "dar")
SUPPORT_PRIMARY_PREFIXES = (
    "ch", "che", "chok", "chot", "cph", "cth", "k", "l", "lk", "ok",
    "okch", "oke", "ol", "op", "ot", "otch", "ote", "p", "qo", "qok",
    "qoke", "qop", "qot", "r", "s", "sh", "she", "t", "tch", "yk", "yt",
)
ROBUST_AR_OR_PREFIXES = (
    "al", "ch", "che", "cho", "chok", "chot", "ckh", "cph", "cth", "dar",
    "k", "kee", "l", "lch", "lk", "o", "ok", "okch", "oke", "okee", "ol",
    "op", "opch", "or", "ot", "otal", "otch", "ote", "p", "pch", "pche",
    "qo", "qok", "qoke", "qop", "qot", "qotch", "r", "s", "sh", "she",
    "shee", "t", "tch", "yche", "yk", "yt",
)
HISTORICAL_EXCLUSION_PREFIXES = (
    "al", "cho", "chok", "chot", "ckh", "cph", "cth", "dar", "kee", "l",
    "lch", "lk", "okch", "okee", "op", "opch", "or", "otal", "otch", "p",
    "pch", "pche", "qop", "qotch", "r", "s", "shee", "tch", "yche", "yk", "yt",
)
RN12_PREFIXES = ("d", "k", "ok", "ot", "qok", "qot", "s")
RN23_PREFIXES = ("d", "lk", "o", "ok", "ot", "qok")

EXPECTED_GUARD = {
    "allowed_pages": 179,
    "tokens": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940},
    "cross": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151},
    "lines": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150},
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    return match.group(1) if match else page


def _page_key(page: str) -> tuple[int, str]:
    match = re.match(r"^f(\d+)(.*)$", page)
    return (int(match.group(1)), match.group(2)) if match else (10**9, page)


def _locus_key(locus: str) -> tuple[int, str, int]:
    page, _, line = locus.partition(".")
    number, suffix = _page_key(page)
    return number, suffix, int(line) if line.isdigit() else 10**9


def _joined(values: Iterable[str], *, pages: bool = False) -> str:
    ordered = sorted(set(values), key=_page_key if pages else None)
    return "|".join(ordered) or "NONE"


def _counter_text(values: Mapping[object, int]) -> str:
    return "|".join(f"{key}:{values[key]}" for key in sorted(values, key=str)) or "NONE"


def _position(ordinal: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def _pair_count(tokens: Sequence[str], left: str, right: str) -> int:
    return sum(a == left and b == right for a, b in zip(tokens, tokens[1:]))


def _assert_safe(rows: Iterable[Mapping[str, object]]) -> None:
    bad = [str(row.get("page", "")) for row in rows if str(row.get("page", "")).startswith("f84")]
    if bad:
        raise AssertionError(f"sealed row materialised: {bad[:3]}")


def _target_occurrences(by_line, exact, cross, line_meta):
    raw: list[dict[str, object]] = []
    selected: list[dict[str, object]] = []
    for locus in sorted(by_line, key=_locus_key):
        line = by_line[locus]
        ranks: Counter[str] = Counter()
        for ordinal, token in enumerate(line, 1):
            surface = str(token["eva"])
            ranks[surface] += 1
            if not surface.endswith("ar") or surface.endswith("dar"):
                continue
            is_exact = int(exact[(locus, int(token["token_index"]))])
            row = {
                "surface": surface,
                "family_class": "BARE_AR" if surface == "ar" else "LEFT_STRING_PLUS_AR",
                "left_string": "NONE" if surface == "ar" else surface[:-2],
                "page": token["page"],
                "physical_folio": _physical_folio(str(token["page"])),
                "locus": locus,
                "token_ordinal": ordinal,
                "token_index": int(token["token_index"]),
                "surface_rank_in_current_line": ranks[surface],
                "line_token_count": len(line),
                "line_position": _position(ordinal, len(line)),
                "norm_position": 0.5 if len(line) == 1 else (ordinal - 1) / (len(line) - 1),
                "section": token["section"],
                "language": token["language"],
                "hand": token["hand"],
                "paragraph_start_line": int(line_meta[locus]["paragraph_start"]),
                "paragraph_end_line": int(line_meta[locus]["paragraph_end"]),
                "true_paragraph_start": int(line_meta[locus]["paragraph_start"] == "1" and ordinal == 1),
                "true_paragraph_end": int(line_meta[locus]["paragraph_end"] == "1" and ordinal == len(line)),
                "left_surface": line[ordinal - 2]["eva"] if ordinal > 1 else "EDGE",
                "right_surface": line[ordinal]["eva"] if ordinal < len(line) else "EDGE",
                "reader_exact": is_exact,
                "zl3b_surface_count": cross[locus]["zl3b_clean"].split().count(surface),
                "it2a_surface_count": cross[locus]["it2a_clean"].split().count(surface),
                "rf1b_surface_count": cross[locus]["rf1b_clean"].split().count(surface),
                "reader_exact_method": "OCCURRENCE_RANK_LE_MIN_THREE_READER_SURFACE_COUNTS",
                "current_line": " ".join(str(item["eva"]) for item in line),
                "component_export_credit": 0,
            }
            raw.append(row)
            if is_exact:
                selected.append(dict(row))
    for number, row in enumerate(selected, 1):
        row["occurrence_id"] = f"G789-O{number:04d}"
    return raw, selected


def _alternate_splits(raw_rows, cross):
    by_surface: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in raw_rows:
        surface = str(row["surface"])
        if surface == "ar":
            continue
        left, locus = surface[:-2], str(row["locus"])
        for field in ("zl3b_clean", "it2a_clean", "rf1b_clean"):
            if _pair_count(cross[locus][field].split(), left, "ar"):
                by_surface[surface].append((locus, field.replace("_clean", "")))
    return {surface: sorted(set(values)) for surface, values in by_surface.items()}


def _family_census(raw_rows, exact_rows, alternate_splits):
    raw_by: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    exact_by: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in raw_rows:
        raw_by[str(row["surface"])].append(row)
    for row in exact_rows:
        exact_by[str(row["surface"])].append(row)
    output = []
    for surface in sorted(raw_by):
        raw, selected = raw_by[surface], exact_by.get(surface, [])
        positions = Counter(str(row["line_position"]) for row in selected)
        registers = Counter(f"{row['section']}|{row['language']}|{row['hand']}" for row in selected)
        splits = alternate_splits.get(surface, [])
        output.append({
            "surface": surface,
            "family_class": "BARE_AR" if surface == "ar" else "LEFT_STRING_PLUS_AR",
            "left_string": "NONE" if surface == "ar" else surface[:-2],
            "raw_occurrences": len(raw),
            "raw_page_count": len({str(row["page"]) for row in raw}),
            "raw_pages": _joined((str(row["page"]) for row in raw), pages=True),
            "raw_physical_folio_count": len({str(row["physical_folio"]) for row in raw}),
            "raw_locus_count": len({str(row["locus"]) for row in raw}),
            "reader_exact_surface": int(bool(selected)),
            "reader_exact_occurrences": len(selected),
            "reader_exact_page_count": len({str(row["page"]) for row in selected}),
            "reader_exact_pages": _joined((str(row["page"]) for row in selected), pages=True),
            "reader_exact_physical_folio_count": len({str(row["physical_folio"]) for row in selected}),
            "reader_exact_locus_count": len({str(row["locus"]) for row in selected}),
            "exact_first": positions["FIRST"],
            "exact_middle": positions["MIDDLE"],
            "exact_last": positions["LAST"],
            "exact_single": positions["SINGLE"],
            "exact_true_paragraph_starts": sum(int(row["true_paragraph_start"]) for row in selected),
            "exact_true_paragraph_ends": sum(int(row["true_paragraph_end"]) for row in selected),
            "exact_register_distribution": _counter_text(registers),
            "current_alternate_reader_split_candidates": len(splits),
            "current_alternate_reader_split_loci": _joined(item[0] for item in splits),
            "current_alternate_reader_split_sources": _joined(item[1] for item in splits),
            "component_export_credit": 0,
        })
    return output


def _all_exact_rows(by_line, exact):
    output = []
    for locus, line in by_line.items():
        for token in line:
            if exact[(locus, int(token["token_index"]))]:
                output.append({
                    "surface": token["eva"], "page": token["page"],
                    "physical_folio": _physical_folio(str(token["page"])), "locus": locus,
                })
    return output


def _lattice(exact_rows, prefixes, tails, prefix_code, cohort):
    by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in exact_rows:
        by_surface[str(row["surface"])].append(row)
    output = []
    for pi, prefix in enumerate(prefixes, 1):
        for ti, tail in enumerate(tails, 1):
            surface, rows = prefix + tail, by_surface[prefix + tail]
            if not rows:
                raise AssertionError(f"empty lattice cell: {surface}")
            folios = {str(row["physical_folio"]) for row in rows}
            output.append({
                "cell_id": f"G789-{prefix_code}{pi:02d}-{ti:02d}",
                "cohort": cohort,
                "prefix_complete_surface_required": 0,
                "prefix": prefix,
                "tail": tail,
                "surface": surface,
                "reader_exact_occurrences": len(rows),
                "reader_exact_page_count": len({str(row["page"]) for row in rows}),
                "reader_exact_physical_folio_count": len(folios),
                "reader_exact_physical_folios": _joined(folios, pages=True),
                "candidate_semantic_credit": 0,
                "component_export_credit": 0,
            })
    return output


def _ar_or_lattice(exact_rows):
    by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in exact_rows:
        by_surface[str(row["surface"])].append(row)
    output = []
    for pi, prefix in enumerate(ROBUST_AR_OR_PREFIXES, 1):
        for ti, tail in enumerate(("ar", "or"), 1):
            surface, rows = prefix + tail, by_surface[prefix + tail]
            folios = {str(row["physical_folio"]) for row in rows}
            if len(rows) < 2 or len(folios) < 2:
                raise AssertionError(f"AR/OR target gate changed: {surface}")
            output.append({
                "cell_id": f"G789-P{pi:02d}-{ti:02d}",
                "cohort": "ROBUST_AR_OR_47",
                "support_primary_31": int(prefix in SUPPORT_PRIMARY_PREFIXES),
                "historical_exclusion_31": int(prefix in HISTORICAL_EXCLUSION_PREFIXES),
                "prefix": prefix,
                "tail": tail,
                "surface": surface,
                "reader_exact_occurrences": len(rows),
                "reader_exact_page_count": len({str(row["page"]) for row in rows}),
                "reader_exact_physical_folio_count": len(folios),
                "reader_exact_physical_folios": _joined(folios, pages=True),
                "candidate_semantic_credit": 0,
                "component_export_credit": 0,
            })
    return output


def _rn_lattice(exact_rows, prefixes, tails, code, cohort):
    by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in exact_rows:
        by_surface[str(row["surface"])].append(row)
    output = []
    for pi, prefix in enumerate(prefixes, 1):
        for ti, tail in enumerate(tails, 1):
            rows = by_surface[prefix + tail]
            folios = {str(row["physical_folio"]) for row in rows}
            if len(rows) < 2 or len(folios) < 2:
                raise AssertionError(f"R/N lattice gate changed: {prefix + tail}")
            output.append({
                "cell_id": f"G789-{code}{pi:02d}-{ti:02d}",
                "cohort": cohort,
                "prefix": prefix,
                "tail": tail,
                "surface": prefix + tail,
                "reader_exact_occurrences": len(rows),
                "reader_exact_page_count": len({str(row["page"]) for row in rows}),
                "reader_exact_physical_folio_count": len(folios),
                "reader_exact_physical_folios": _joined(folios, pages=True),
                "candidate_semantic_credit": 0,
                "component_export_credit": 0,
            })
    return output


def _separated_pairs(by_line, exact, cross, line_meta):
    raw = []
    for locus in sorted(by_line, key=_locus_key):
        line = by_line[locus]
        for index, right in enumerate(line):
            if right["eva"] != "ar" or index == 0:
                continue
            left = line[index - 1]
            pair_counts = {
                field: _pair_count(cross[locus][field].split(), str(left["eva"]), "ar")
                for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")
            }
            both_exact = int(
                exact[(locus, int(left["token_index"]))]
                and exact[(locus, int(right["token_index"]))]
            )
            preserved = int(all(pair_counts.values()))
            raw.append({
                "page": right["page"],
                "physical_folio": _physical_folio(str(right["page"])),
                "locus": locus,
                "left_surface": left["eva"],
                "right_surface": "ar",
                "separated_pair": f"{left['eva']} ar",
                "left_token_ordinal": index,
                "right_token_ordinal": index + 1,
                "line_token_count": len(line),
                "line_position_of_ar": _position(index + 1, len(line)),
                "paragraph_start_line": int(line_meta[locus]["paragraph_start"]),
                "paragraph_end_line": int(line_meta[locus]["paragraph_end"]),
                "section": right["section"],
                "language": right["language"],
                "hand": right["hand"],
                "both_tokens_reader_exact": both_exact,
                "zl3b_pair_count": pair_counts["zl3b_clean"],
                "it2a_pair_count": pair_counts["it2a_clean"],
                "rf1b_pair_count": pair_counts["rf1b_clean"],
                "all_three_readers_preserve_pair": preserved,
                "clean_exact_span": int(both_exact and preserved),
                "current_line": " ".join(str(item["eva"]) for item in line),
                "component_export_credit": 0,
            })
    clean = [dict(row) for row in raw if int(row["clean_exact_span"])]
    for number, row in enumerate(clean, 1):
        row["span_id"] = f"G789-S{number:03d}"
    return raw, clean


def _stolfi(base, exact_rows):
    pages = {str(row["page"]) for row in exact_rows}
    if any(page.startswith("f84") for page in pages):
        raise AssertionError("sealed Stolfi request")
    queried, guard = base.guarded_query(STOLFI_REL, pages, "page,locus,raw_text,clean_text")
    _assert_safe(queried)
    by_locus = {row["locus"]: row for row in queried}
    if len(by_locus) != len(queried):
        raise AssertionError("duplicate Stolfi locus")
    by_page = Counter(row["page"] for row in queried)
    output = []
    for target in exact_rows:
        surface, locus, page = str(target["surface"]), str(target["locus"]), str(target["page"])
        left = "" if surface == "ar" else surface[:-2]
        same = by_locus.get(locus)
        whole_count = split_count = 0
        separator = "NONE"
        if same is None:
            status = "NO_SAME_LOCUS_ROW" if by_page[page] else "NO_STOLFI_ROWS_FOR_PAGE"
        else:
            tokens = same["clean_text"].split()
            whole_count = tokens.count(surface)
            split_count = _pair_count(tokens, left, "ar") if left else 0
            rank = int(target["surface_rank_in_current_line"])
            if rank <= whole_count:
                status = "BARE_AR_AT_SAME_LOCUS" if surface == "ar" else "FUSED_WHOLE_AT_SAME_LOCUS"
            elif left and rank <= whole_count + split_count:
                status = "SPLIT_LEFT_AR_AT_SAME_LOCUS"
            elif "ar" in tokens:
                status = "OTHER_AR_BOUNDARY_AT_SAME_LOCUS"
            else:
                status = "ALTERNATE_READING_AT_SAME_LOCUS"
            if left:
                marker = re.search(rf"(?<![A-Za-z]){re.escape(left)}([.,])ar(?![A-Za-z])", same["raw_text"])
                if marker:
                    separator = marker.group(1)
        output.append({
            "occurrence_id": target["occurrence_id"],
            "surface": surface,
            "left_string": left or "NONE",
            "page": page,
            "physical_folio": target["physical_folio"],
            "locus": locus,
            "stolfi_page_row_count": by_page[page],
            "stolfi_same_locus_present": int(same is not None),
            "stolfi_whole_count": whole_count,
            "stolfi_split_left_ar_count": split_count,
            "stolfi_raw_split_separator": separator,
            "boundary_status": status,
            "component_export_credit": 0,
        })
    return output, queried, guard, len(pages)


def _stolfi_summary(exact_rows, audit_rows):
    targets: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    audits: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in exact_rows:
        targets[str(row["surface"])].append(row)
    for row in audit_rows:
        audits[str(row["surface"])].append(row)
    output = []
    for surface in sorted(targets):
        rows, checks = targets[surface], audits[surface]
        statuses = Counter(str(row["boundary_status"]) for row in checks)
        output.append({
            "surface": surface,
            "left_string": "NONE" if surface == "ar" else surface[:-2],
            "current_reader_exact_occurrences": len(rows),
            "stolfi_same_locus_occurrences": sum(int(row["stolfi_same_locus_present"]) for row in checks),
            "stolfi_fused_whole_occurrences": statuses["FUSED_WHOLE_AT_SAME_LOCUS"],
            "stolfi_bare_ar_occurrences": statuses["BARE_AR_AT_SAME_LOCUS"],
            "stolfi_split_left_ar_occurrences": statuses["SPLIT_LEFT_AR_AT_SAME_LOCUS"],
            "stolfi_other_ar_boundary_occurrences": statuses["OTHER_AR_BOUNDARY_AT_SAME_LOCUS"],
            "stolfi_alternate_reading_occurrences": statuses["ALTERNATE_READING_AT_SAME_LOCUS"],
            "stolfi_no_same_locus_occurrences": statuses["NO_SAME_LOCUS_ROW"],
            "stolfi_no_page_occurrences": statuses["NO_STOLFI_ROWS_FOR_PAGE"],
            "boundary_evidence_scope": "LEGACY_TRANSCRIPTION_SENSITIVITY_NOT_INDEPENDENT_SEMANTICS",
            "component_export_credit": 0,
        })
    return output


def _fused_split(exact_rows, clean_splits, stolfi_summary):
    fused: Counter[str] = Counter(str(row["surface"]) for row in exact_rows)
    separated: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in clean_splits:
        separated[str(row["left_surface"])].append(row)
    stolfi = {str(row["surface"]): row for row in stolfi_summary}
    lefts = sorted(left for left in separated if fused[left + "ar"])
    return [{
        "left_surface": left,
        "fused_surface": left + "ar",
        "fused_reader_exact_occurrences": fused[left + "ar"],
        "separated_pair": f"{left} ar",
        "separated_reader_exact_occurrences": len(separated[left]),
        "separated_loci": _joined(str(row["locus"]) for row in separated[left]),
        "stolfi_fused_occurrences": stolfi[left + "ar"]["stolfi_fused_whole_occurrences"],
        "stolfi_split_occurrences": stolfi[left + "ar"]["stolfi_split_left_ar_occurrences"],
        "boundary_bridge_only": 1,
        "semantic_credit": 0,
        "component_export_credit": 0,
    } for left in lefts]


def _construction_deck(by_line, exact, cross, exact_counts):
    specs = [
        *( (head, value, "VALUE") for head in ("ar", "or", "s") for value in ("ain", "aiin", "aiiin") ),
        *( (left, right, "HEAD_NESTING") for left in ("ar", "or") for right in ("ar", "or") ),
    ]
    raw_counts: Counter[tuple[str, str]] = Counter()
    clean_counts: Counter[tuple[str, str]] = Counter()
    loci: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    for locus, line in by_line.items():
        for index, (left, right) in enumerate(zip(line, line[1:])):
            pair = str(left["eva"]), str(right["eva"])
            if pair not in {(a, b) for a, b, _ in specs}:
                continue
            raw_counts[pair] += 1
            if not (
                exact[(locus, int(left["token_index"]))]
                and exact[(locus, int(right["token_index"]))]
            ):
                continue
            reader_counts = [
                _pair_count(cross[locus][field].split(), pair[0], pair[1])
                for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")
            ]
            if all(reader_counts):
                clean_counts[pair] += 1
                loci[pair].add(locus)
    output = []
    for number, (left, right, family) in enumerate(specs, 1):
        fused = left + right
        output.append({
            "construction_id": f"G789-C{number:02d}",
            "construction_family": family,
            "left_complete_surface": left,
            "right_complete_surface": right,
            "separated_expression": f"{left} {right}",
            "raw_separated_occurrences": raw_counts[(left, right)],
            "reader_exact_separated_occurrences": clean_counts[(left, right)],
            "reader_exact_separated_loci": _joined(loci[(left, right)]),
            "fused_surface": fused,
            "fused_reader_exact_occurrences": exact_counts[fused],
            "working_construction_de": (
                "Anteile/Portionen/Maße mit Wert II/III/IV"
                if family == "VALUE" else "verschachteltes Anteil-/Portionsfeld"
            ),
            "supports_specific_unit_identity": 0,
            "supports_distinct_or_nested_heads": int(family == "HEAD_NESTING" and left != right),
            "component_export_credit": 0,
        })
    return output


def compute(repo_root: Path | str) -> dict[str, object]:
    root = Path(repo_root).resolve()
    if not (root / "AGENTS.md").is_file() or not (root / ".git").exists():
        raise RuntimeError(f"not repository root: {root}")
    base = _load_module("gdt782_guarded_for_gdt789", root / G782_REL)
    by_line, exact, cross, line_meta, _cells, guard = base.load_context()
    if guard != EXPECTED_GUARD:
        raise AssertionError(f"guard changed: {guard}")
    all_tokens = [token for line in by_line.values() for token in line]
    _assert_safe(all_tokens)

    raw_rows, exact_rows = _target_occurrences(by_line, exact, cross, line_meta)
    alternate = _alternate_splits(raw_rows, cross)
    census = _family_census(raw_rows, exact_rows, alternate)
    all_exact = _all_exact_rows(by_line, exact)
    square = _lattice(all_exact, SQUARE_PREFIXES, SQUARE_TAILS, "Q", "PRIMARY_SQUARE")
    square_sensitivity = _lattice(
        all_exact, SQUARE_SENSITIVITY_PREFIXES, SQUARE_TAILS, "X", "SQUARE_SENSITIVITY"
    )
    ar_or = _ar_or_lattice(all_exact)
    rn12 = _rn_lattice(all_exact, RN12_PREFIXES, ("ar", "an", "air", "ain"), "R12-", "R_N_LEVEL_I_TO_II")
    rn23 = _rn_lattice(all_exact, RN23_PREFIXES, ("air", "ain", "aiir", "aiin"), "R23-", "R_N_LEVEL_II_TO_III")
    raw_splits, clean_splits = _separated_pairs(by_line, exact, cross, line_meta)
    stolfi_occ, stolfi_source, stolfi_guard, stolfi_pages = _stolfi(base, exact_rows)
    stolfi_summary = _stolfi_summary(exact_rows, stolfi_occ)
    fused_split = _fused_split(exact_rows, clean_splits, stolfi_summary)

    raw_counts = Counter(str(row["surface"]) for row in raw_rows)
    exact_counts = Counter(str(row["surface"]) for row in exact_rows)
    all_exact_counts = Counter(str(row["surface"]) for row in all_exact)
    construction = _construction_deck(by_line, exact, cross, all_exact_counts)
    if (len(raw_counts), sum(raw_counts.values()), len(exact_counts), sum(exact_counts.values())) != (285, 1698, 225, 1348):
        raise AssertionError("AR family census changed")
    if (raw_counts["ar"], exact_counts["ar"]) != (321, 242):
        raise AssertionError("bare ar census changed")
    if (len(raw_splits), len(clean_splits)) != (318, 192):
        raise AssertionError("X ar span census changed")
    if len(square) != 40 or len(square_sensitivity) != 64:
        raise AssertionError("square lattice size changed")
    if len(ar_or) != 94 or len(rn12) != 28 or len(rn23) != 24:
        raise AssertionError("AR/OR lattice size changed")

    nonbare_stolfi = Counter(
        str(row["boundary_status"]) for row in stolfi_occ if row["surface"] != "ar"
    )
    diagnostics = {
        "allowed_pages": int(guard["allowed_pages"]),
        "raw_family_surfaces": len(raw_counts),
        "raw_family_occurrences": sum(raw_counts.values()),
        "raw_family_page_labels": len({str(row["page"]) for row in raw_rows}),
        "raw_family_physical_folios": len({str(row["physical_folio"]) for row in raw_rows}),
        "reader_exact_family_surfaces": len(exact_counts),
        "reader_exact_family_occurrences": sum(exact_counts.values()),
        "reader_exact_family_page_labels": len({str(row["page"]) for row in exact_rows}),
        "reader_exact_family_physical_folios": len({str(row["physical_folio"]) for row in exact_rows}),
        "reader_exact_family_loci": len({str(row["locus"]) for row in exact_rows}),
        "bare_ar_raw_occurrences": raw_counts["ar"],
        "bare_ar_reader_exact_occurrences": exact_counts["ar"],
        "reader_exact_nonbare_surfaces": len(exact_counts) - 1,
        "reader_exact_nonbare_occurrences": sum(exact_counts.values()) - exact_counts["ar"],
        "reader_exact_nonbare_recurrent_surfaces": sum(surface != "ar" and count >= 2 for surface, count in exact_counts.items()),
        "reader_exact_nonbare_singleton_surfaces": sum(surface != "ar" and count == 1 for surface, count in exact_counts.items()),
        "square_primary_cells": len(square),
        "square_primary_exact_occurrences": sum(int(row["reader_exact_occurrences"]) for row in square),
        "square_sensitivity_cells": len(square_sensitivity),
        "square_sensitivity_exact_occurrences": sum(int(row["reader_exact_occurrences"]) for row in square_sensitivity),
        "ar_or_robust_cells": len(ar_or),
        "ar_or_robust_prefixes": len(ROBUST_AR_OR_PREFIXES),
        "ar_or_robust_exact_occurrences": sum(int(row["reader_exact_occurrences"]) for row in ar_or),
        "ar_or_support_primary_prefixes": len(SUPPORT_PRIMARY_PREFIXES),
        "ar_or_historical_exclusion_prefixes": len(HISTORICAL_EXCLUSION_PREFIXES),
        "rn12_cells": len(rn12),
        "rn23_cells": len(rn23),
        "raw_separated_spans": len(raw_splits),
        "clean_exact_separated_spans": len(clean_splits),
        "clean_exact_separated_left_types": len({str(row["left_surface"]) for row in clean_splits}),
        "fused_and_separated_left_types": len(fused_split),
        "current_alternate_reader_split_candidates": sum(len(values) for values in alternate.values()),
        "current_alternate_reader_split_surfaces": len(alternate),
        "stolfi_requested_pages": stolfi_pages,
        "stolfi_selected_rows": len(stolfi_source),
        "stolfi_nonbare_fused_occurrences": nonbare_stolfi["FUSED_WHOLE_AT_SAME_LOCUS"],
        "stolfi_nonbare_split_occurrences": nonbare_stolfi["SPLIT_LEFT_AR_AT_SAME_LOCUS"],
        "construction_rows": len(construction),
        "sealed_f84_rows_materialised": 0,
    }
    return {
        "raw_occurrence_rows": raw_rows,
        "exact_occurrence_rows": exact_rows,
        "family_rows": census,
        "square_lattice_rows": square,
        "square_sensitivity_rows": square_sensitivity,
        "ar_or_lattice_rows": ar_or,
        "rn12_lattice_rows": rn12,
        "rn23_lattice_rows": rn23,
        "raw_separated_rows": raw_splits,
        "clean_exact_separated_rows": clean_splits,
        "fused_split_rows": fused_split,
        "stolfi_occurrence_rows": stolfi_occ,
        "stolfi_summary_rows": stolfi_summary,
        "construction_rows": construction,
        "diagnostics": diagnostics,
        "guard": guard,
        "stolfi_guard": stolfi_guard,
    }


if __name__ == "__main__":
    raise SystemExit("import and call compute(repo_root)")
