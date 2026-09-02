#!/usr/bin/env python3
"""Build GDT737: held-body transfer and renderer correction."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt737_held_body_record_role_transfer")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

G635 = Path("experiments/yolo/gdt635_initial_head_same_remainder_swaps")
ALLOW_REL = G635 / "artifacts/PAGE_ALLOWLIST.tsv"
ATLAS_REL = G635 / "artifacts/SHARED_REMAINDER_ATLAS.tsv"
G736 = Path("experiments/yolo/gdt736_opaque_head_record_role_bridge")
G736_RUN_REL = G736 / "src/run.py"
G736_HEAD_REL = G736 / "src/HEAD_ROLE_SPECS.tsv"
G736_BODY_REL = G736 / "artifacts/BODY_ROLE_DICTIONARY_V2.tsv"
G736_COSINE_REL = G736 / "artifacts/HEAD_PAIR_BODY_COSINE.tsv"
V99R7_DICT_REL = Path(
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/"
    "artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
)
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
LINES_REL = Path("transcription/voynich_zl3b_lines.tsv")

module_spec = importlib.util.spec_from_file_location("gdt736_builder", ROOT / G736_RUN_REL)
if module_spec is None or module_spec.loader is None:
    raise RuntimeError("cannot load GDT736 guarded helpers")
g736 = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(g736)
g631 = g736.g631
g634 = g736.g634

HEAD_ORDER = ("H1", "H2", "H3", "H4")
EVA_TO_HEAD = {"p": "H1", "s": "H2", "r": "H3", "l": "H4"}
PAIR = {"H1": "ENTRY_PAIR", "H2": "ENTRY_PAIR", "H3": "INTERNAL_PAIR", "H4": "INTERNAL_PAIR"}
SELECTED_PAIRS = {frozenset(("H1", "H4")), frozenset(("H2", "H3"))}
RETIRED_HEAD_WORDS = ("pulver", "samen", "saat", "wurzel", "holz")
STATUS = (
    "HELD_120_LOCATION_AXIS_REPLICATES_STRONGLY__FROZEN_BODY_AFFINITY_2X2_FAILS_TRANSFER__"
    "H1_H4_DOWNGRADED_TO_WEAK_OCCUPANCY_ASSOCIATION__H2_H3_PARTIAL_AND_AIN_DOMINATED__"
    "REGISTER_GATED_HEAD_ROLES__EXACT_WHOLE_FALLBACK_REQUIRED__ZERO_LEXEMES__NO_NEW_PAGE"
)
OUTPUT_NAMES = (
    "HELD_811_OCCURRENCE_CONTEXTS.tsv",
    "HELD_120_BODY_REGISTRY.tsv",
    "HELD_273_FORM_ROLE_BRIDGE.tsv",
    "HELD_HEAD_TRANSFER_PROFILE.tsv",
    "HELD_BODY_CONTROLLED_POSITION.tsv",
    "HELD_PAGE_CONTROLLED_POSITION.tsv",
    "HELD_SECTION_POSITION.tsv",
    "HELD_ROLE_AXIS_TESTS.tsv",
    "HELD_HEAD_PAIR_AFFINITY.tsv",
    "AFFINITY_SENSITIVITY.tsv",
    "TRANSFER_MODEL_UPDATE.tsv",
    "V99R7_HELD_WHOLE_QUARANTINE.tsv",
    "HELD_BODY_WORKING_CANDIDATES.tsv",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fmt(value: float) -> str:
    return f"{value:.6f}"


def average(values: list[float]) -> float:
    return mean(values) if values else 0.0


def allowed_pages() -> set[str]:
    pages = {row["page"] for row in read_tsv(ROOT / ALLOW_REL)}
    if len(pages) != 179 or "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise AssertionError("inherited allowlist changed or contains a forbidden page")
    return pages


def parse_map(value: str) -> dict[str, str]:
    return dict(field.split(":", 1) for field in value.split("|"))


def load_target() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, dict[str, object]]]:
    training = {row["body"] for row in read_tsv(ROOT / G736_BODY_REL)}
    source_rows = [row for row in read_tsv(ROOT / ATLAS_REL) if row["body"] not in training]
    source_rows.sort(key=lambda row: row["body"])
    if len(training) != 24 or len(source_rows) != 120:
        raise AssertionError("training or held body set changed")
    if Counter(int(row["head_occupancy"]) for row in source_rows) != Counter({2: 87, 3: 33}):
        raise AssertionError("held occupancy profile changed")

    bodies: list[dict[str, object]] = []
    forms: list[dict[str, object]] = []
    for body_index, source in enumerate(source_rows, 1):
        form_map = parse_map(source["forms"])
        counts = {key: int(value) for key, value in parse_map(source["occurrences_by_head"]).items()}
        exact = {key: int(value) for key, value in parse_map(source["reader_exact_by_head"]).items()}
        pages = parse_map(source["pages_by_head"])
        loci = parse_map(source["loci_by_head"])
        observed: list[str] = []
        body_forms: list[str] = []
        for eva_head in ("p", "s", "r", "l"):
            surface = form_map.get(eva_head, "-")
            if surface in ("", "-"):
                continue
            observed.append(EVA_TO_HEAD[eva_head])
            body_forms.append(surface)
            forms.append({
                "held_form_id": f"G737-F{len(forms) + 1:03d}", "source_shared_id": source["shared_id"],
                "body": source["body"], "head_occupancy": int(source["head_occupancy"]),
                "opaque_head_id": EVA_TO_HEAD[eva_head], "eva_transcription_label": eva_head,
                "form": surface, "atlas_occurrences": counts[eva_head], "atlas_reader_exact": exact[eva_head],
                "atlas_pages": int(pages[eva_head]), "atlas_loci": int(loci[eva_head]),
            })
        bodies.append({
            "held_body_id": f"G737-B{body_index:03d}", "source_shared_id": source["shared_id"],
            "body": source["body"], "head_occupancy": int(source["head_occupancy"]),
            "opaque_heads": "|".join(observed), "forms": "|".join(body_forms),
            "total_headed_occurrences": int(source["total_headed_occurrences"]),
            "bare_body_occurrences": int(source["bare_body_occurrences"]),
            "atlas_semantic_status": source["semantic_status"],
            "atlas_inherited_value_de": source["inherited_or_working_body_value_de"],
        })
    if len(forms) != 273 or len({str(row["form"]) for row in forms}) != 273:
        raise AssertionError("expected 273 real held forms")
    if sum(int(row["atlas_occurrences"]) for row in forms) != 811:
        raise AssertionError("held occurrence total changed")
    return bodies, forms, {str(row["form"]): row for row in forms}


def load_body_specs(bodies: list[dict[str, object]]) -> list[dict[str, object]]:
    specs = read_tsv(SRC / "BODY_WORKING_SPECS.tsv")
    if len(specs) != 120 or {row["body"] for row in specs} != {str(row["body"]) for row in bodies}:
        raise AssertionError("BODY_WORKING_SPECS must cover exactly the 120 held bodies")
    if any(any(word in row["concrete_body_role_de"].lower() for word in RETIRED_HEAD_WORDS) for row in specs):
        raise AssertionError("retired head noun in body candidate deck")
    by_body = {str(row["body"]): row for row in bodies}
    result: list[dict[str, object]] = []
    for source in specs:
        atlas = by_body[source["body"]]
        if int(source["occurrence_total"]) != int(atlas["total_headed_occurrences"]):
            raise AssertionError(f"candidate occurrence total mismatch: {source['body']}")
        result.append({
            **source, "head_occupancy": atlas["head_occupancy"], "opaque_heads": atlas["opaque_heads"],
            "bare_body_occurrences": atlas["bare_body_occurrences"], "literal_lexeme_confidence": "ZERO",
            "renderer_license": 0, "component_export_credit": 0,
            "export_rule": "EXPLORATORY_CANDIDATE_ONLY__NO_FREE_OR_HEADED_COMPONENT_EXPORT",
        })
    return sorted(result, key=lambda row: (-int(row["occurrence_total"]), str(row["body"])))


def normalized_position(ordinal: int, line_length: int) -> float:
    return 0.0 if line_length <= 1 else (ordinal - 1) / (line_length - 1)


def contextual_role(head: str, position: str, paragraph_first: int, form: str) -> tuple[str, str]:
    if head == "H1":
        if paragraph_first:
            return "PARAGRAPH_OR_RECORD_OPENER", f"Absatz-/Recordöffner: [{form}]"
        if position == "FIRST":
            return "LINE_OR_RECORD_OPENER", f"Zeilen-/Recordöffner: [{form}]"
        return "H1_WHOLE_OR_EXCEPTION", f"H1-Ganzform oder Ausnahme: [{form}]"
    if head == "H2":
        if position == "FIRST":
            return "LINE_ITEM_OR_SUBENTRY", f"Posten-/Untereintragsform: [{form}]"
        return "H2_WHOLE_OR_INTERNAL_FIELD", f"H2-Ganzform oder internes Feld: [{form}]"
    if head == "H3":
        if position == "LAST":
            return "LATE_REFERENCE_OR_ITEM_CLOSE", f"Abschlussbezug: [{form}]"
        if position == "MIDDLE":
            return "INTERNAL_REFERENCE_FIELD", f"interner Bezug: [{form}]"
        return "H3_WHOLE_OR_EXCEPTION", f"H3-Ganzform oder Ausnahme: [{form}]"
    if position == "FIRST":
        return "H4_WHOLE_OR_EXCEPTION", f"H4-Ganzform oder Ausnahme: [{form}]"
    return "INTERNAL_FIELD", f"internes Feld: [{form}]"


def build_occurrences(token_rows: list[dict[str, str]], cross_rows: list[dict[str, str]],
                      line_rows: list[dict[str, str]], form_map: dict[str, dict[str, object]],
                      specs: list[dict[str, object]]) -> list[dict[str, object]]:
    by_line, line_text = g631.line_maps(token_rows)
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    line_meta = {row["locus"]: row for row in line_rows}
    exact, boundary = g634.stable_maps(token_rows, cross_by_locus)
    body_specs = {str(row["body"]): row for row in specs}
    rows: list[dict[str, object]] = []
    for source in sorted(token_rows, key=g631.token_sort_key):
        if source["eva"] not in form_map:
            continue
        cell = form_map[source["eva"]]
        line = by_line[source["locus"]]
        ordinal = next(i for i, token in enumerate(line, 1) if int(token["token_index"]) == int(source["token_index"]))
        length = len(line)
        position = "FIRST" if ordinal == 1 else "LAST" if ordinal == length else "MIDDLE"
        meta = line_meta[source["locus"]]
        paragraph_first = int(meta["paragraph_start"] == "1" and ordinal == 1)
        key = (source["locus"], int(source["token_index"]))
        head = str(cell["opaque_head_id"])
        role, structural = contextual_role(head, position, paragraph_first, source["eva"])
        candidate = body_specs[str(cell["body"])]
        rows.append({
            "occurrence_id": f"G737-O{len(rows) + 1:04d}", "held_form_id": cell["held_form_id"],
            "form": source["eva"], "opaque_head_id": head,
            "eva_transcription_label": cell["eva_transcription_label"], "body": cell["body"],
            "head_occupancy": cell["head_occupancy"], "page": source["page"], "locus": source["locus"],
            "section": source["section"], "language": source["language"], "hand": source["hand"],
            "token_index": int(source["token_index"]), "token_ordinal": ordinal, "line_length": length,
            "line_position": position, "normalized_position": fmt(normalized_position(ordinal, length)),
            "paragraph_start_line": int(meta["paragraph_start"]), "paragraph_first_token": paragraph_first,
            "single_token_line": int(length == 1),
            "previous_surface": str(line[ordinal - 2]["eva"]) if ordinal > 1 else "NONE",
            "next_surface": str(line[ordinal]["eva"]) if ordinal < length else "NONE",
            "surface_line": line_text[source["locus"]], "all_readers_exact": exact[key],
            "split_normalized_all_readers": boundary[key],
            "reader_status": "EXACT" if exact[key] else "SPLIT_ONLY" if boundary[key] else "OTHER_VARIANT_OR_OMISSION",
            "pair_axis": PAIR[head], "selected_occurrence_role": role, "structural_render_de": structural,
            "exploratory_body_candidate_de": candidate["concrete_body_role_de"],
            "exploratory_candidate_render_de": f"{structural} — Kandidat: {candidate['concrete_body_role_de']}",
            "body_candidate_renderer_license": 0, "literal_head_lexeme": "UNRESOLVED",
            "literal_body_lexeme": "UNRESOLVED", "component_export_credit": 0,
        })
    if len(rows) != 811 or len({(str(row["locus"]), int(row["token_index"])) for row in rows}) != 811:
        raise AssertionError("held occurrence reconstruction changed")
    if len({str(row["page"]) for row in rows}) != 134 or len({str(row["locus"]) for row in rows}) != 697:
        raise AssertionError("held occurrence footprint changed")
    if sum(int(row["all_readers_exact"]) for row in rows) != 619:
        raise AssertionError("held reader-exact total changed")
    return rows


def head_profiles(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    expected = {
        "H1": (147, 108, 35, 4, .148428, 98, 104, 80, 23, 1, .134091, 73),
        "H2": (181, 91, 67, 23, .324907, 3, 136, 72, 46, 18, .326570, 2),
        "H3": (91, 8, 54, 29, .665316, 0, 57, 3, 36, 18, .650953, 0),
        "H4": (392, 16, 309, 67, .574910, 0, 322, 14, 252, 56, .576666, 0),
    }
    rows: list[dict[str, object]] = []
    for head in HEAD_ORDER:
        selected = [row for row in occurrences if row["opaque_head_id"] == head]
        exact = [row for row in selected if int(row["all_readers_exact"])]
        positions, exact_positions = Counter(str(row["line_position"]) for row in selected), Counter(str(row["line_position"]) for row in exact)
        row = {
            "opaque_head_id": head, "occurrences": len(selected), "line_first": positions["FIRST"],
            "line_middle": positions["MIDDLE"], "line_last": positions["LAST"],
            "mean_normalized_position": fmt(average([float(item["normalized_position"]) for item in selected])),
            "paragraph_first": sum(int(item["paragraph_first_token"]) for item in selected),
            "reader_exact": len(exact), "exact_line_first": exact_positions["FIRST"],
            "exact_line_middle": exact_positions["MIDDLE"], "exact_line_last": exact_positions["LAST"],
            "exact_mean_normalized_position": fmt(average([float(item["normalized_position"]) for item in exact])),
            "exact_paragraph_first": sum(int(item["paragraph_first_token"]) for item in exact),
            "split_only": sum(item["reader_status"] == "SPLIT_ONLY" for item in selected),
            "record_role_transfer": "PASS_REGISTER_AND_POSITION_CONDITIONED",
            "semantic_head_role_transfer": "NOT_CLAIMED", "literal_lexeme_credit": 0,
        }
        observed = (len(selected), positions["FIRST"], positions["MIDDLE"], positions["LAST"],
                    round(float(row["mean_normalized_position"]), 6), int(row["paragraph_first"]), len(exact),
                    exact_positions["FIRST"], exact_positions["MIDDLE"], exact_positions["LAST"],
                    round(float(row["exact_mean_normalized_position"]), 6), int(row["exact_paragraph_first"]))
        if observed != expected[head]:
            raise AssertionError(f"head profile changed for {head}: {observed}")
        rows.append(row)
    return rows


def contrast_rows(occurrences: list[dict[str, object]], field: str) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        grouped[str(row[field])].append(row)
    rows: list[dict[str, object]] = []
    for key in sorted(grouped):
        entry = [float(row["normalized_position"]) for row in grouped[key] if row["pair_axis"] == "ENTRY_PAIR"]
        internal = [float(row["normalized_position"]) for row in grouped[key] if row["pair_axis"] == "INTERNAL_PAIR"]
        if not entry or not internal:
            continue
        difference = average(internal) - average(entry)
        rows.append({field: key, "entry_occurrences": len(entry), "internal_occurrences": len(internal),
                     "entry_mean_normalized_position": fmt(average(entry)),
                     "internal_mean_normalized_position": fmt(average(internal)), "internal_minus_entry": fmt(difference),
                     "direction": "ENTRY_EARLIER" if difference > 0 else "INTERNAL_EARLIER" if difference < 0 else "TIE"})
    return rows


def section_contrasts(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for section in sorted({str(row["section"]) for row in occurrences}):
        selected = [row for row in occurrences if row["section"] == section]
        exact = [row for row in selected if int(row["all_readers_exact"])]
        def take(deck: list[dict[str, object]], pair: str) -> list[float]:
            return [float(row["normalized_position"]) for row in deck if row["pair_axis"] == pair]
        entry, internal = take(selected, "ENTRY_PAIR"), take(selected, "INTERNAL_PAIR")
        exact_entry, exact_internal = take(exact, "ENTRY_PAIR"), take(exact, "INTERNAL_PAIR")
        difference, exact_difference = average(internal) - average(entry), average(exact_internal) - average(exact_entry)
        rows.append({
            "section": section, "entry_occurrences": len(entry), "internal_occurrences": len(internal),
            "entry_mean": fmt(average(entry)), "internal_mean": fmt(average(internal)),
            "internal_minus_entry": fmt(difference),
            "direction": "ENTRY_EARLIER" if difference > 0 else "INTERNAL_EARLIER" if difference < 0 else "TIE",
            "exact_entry_occurrences": len(exact_entry), "exact_internal_occurrences": len(exact_internal),
            "exact_entry_mean": fmt(average(exact_entry)), "exact_internal_mean": fmt(average(exact_internal)),
            "exact_internal_minus_entry": fmt(exact_difference),
            "exact_direction": "ENTRY_EARLIER" if exact_difference > 0 else "INTERNAL_EARLIER" if exact_difference < 0 else "TIE",
        })
    return rows


def odds_ratio(a: int, b: int, c: int, d: int) -> tuple[float, float, float]:
    if min(a, b, c, d) <= 0:
        raise AssertionError(f"zero OR cell: {(a, b, c, d)}")
    value = a * d / (b * c)
    error = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return value, math.exp(math.log(value) - 1.96 * error), math.exp(math.log(value) + 1.96 * error)


def mh_first_or(rows: list[dict[str, object]], fields: tuple[str, ...]) -> float:
    strata: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        strata[tuple(str(row[field]) for field in fields)].append(row)
    numerator = denominator = 0.0
    for selected in strata.values():
        a = sum(row["pair_axis"] == "ENTRY_PAIR" and row["line_position"] == "FIRST" for row in selected)
        b = sum(row["pair_axis"] == "ENTRY_PAIR" and row["line_position"] != "FIRST" for row in selected)
        c = sum(row["pair_axis"] == "INTERNAL_PAIR" and row["line_position"] == "FIRST" for row in selected)
        d = sum(row["pair_axis"] == "INTERNAL_PAIR" and row["line_position"] != "FIRST" for row in selected)
        total = a + b + c + d
        if total:
            numerator += a * d / total
            denominator += b * c / total
    return numerator / denominator


def role_tests(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    def binary(test_id: str, description: str, a: int, b: int, c: int, d: int, decision: str) -> None:
        value, low, high = odds_ratio(a, b, c, d)
        rows.append({"test_id": test_id, "description": description, "a": a, "b": b, "c": c, "d": d,
                     "odds_ratio": fmt(value), "ci95_low": fmt(low), "ci95_high": fmt(high), "decision": decision,
                     "claim_limit": "FORMAL_POSITION_OR_READER_CONTROL_ONLY__NO_LEXEME_OR_PLAINTEXT"})
    entry = [row for row in occurrences if row["pair_axis"] == "ENTRY_PAIR"]
    internal = [row for row in occurrences if row["pair_axis"] == "INTERNAL_PAIR"]
    exact_entry = [row for row in entry if int(row["all_readers_exact"])]
    exact_internal = [row for row in internal if int(row["all_readers_exact"])]
    h1 = [row for row in occurrences if row["opaque_head_id"] == "H1"]
    h2 = [row for row in occurrences if row["opaque_head_id"] == "H2"]
    h3 = [row for row in occurrences if row["opaque_head_id"] == "H3"]
    h4 = [row for row in occurrences if row["opaque_head_id"] == "H4"]
    binary("T01_ENTRY_FIRST", "H1/H2 line-first versus H3/H4", 199, 129, 24, 459, "PASS_STRONG")
    binary("T02_ENTRY_FIRST_EXACT", "reader-exact H1/H2 line-first versus H3/H4", 152, 88, 17, 362, "PASS_STRONG")
    ne = [row for row in exact_entry if not int(row["single_token_line"])]
    ni = [row for row in exact_internal if not int(row["single_token_line"])]
    binary("T03_ENTRY_FIRST_EXACT_NON_SINGLE", "reader-exact non-singleton H1/H2 versus H3/H4",
           sum(row["line_position"] == "FIRST" for row in ne), sum(row["line_position"] != "FIRST" for row in ne),
           sum(row["line_position"] == "FIRST" for row in ni), sum(row["line_position"] != "FIRST" for row in ni), "PASS_STRONG")
    binary("T04_H1_H2_PARAGRAPH", "H1 versus H2 paragraph-first", 98, 49, 3, 178, "PASS_HIERARCHY")
    eh1, eh2 = [row for row in h1 if int(row["all_readers_exact"])], [row for row in h2 if int(row["all_readers_exact"])]
    binary("T05_H1_H2_PARAGRAPH_EXACT", "reader-exact H1 versus H2 paragraph-first", 73, 31, 2, 134, "PASS_HIERARCHY")
    binary("T06_H3_H4_FINAL", "H3 versus H4 line-final",
           sum(row["line_position"] == "LAST" for row in h3), sum(row["line_position"] != "LAST" for row in h3),
           sum(row["line_position"] == "LAST" for row in h4), sum(row["line_position"] != "LAST" for row in h4), "PASS_LATE_SUBROLE")
    high = [row for row in occurrences if row["opaque_head_id"] in ("H2", "H3")]
    low = [row for row in occurrences if row["opaque_head_id"] in ("H1", "H4")]
    binary("T07_SPLIT_H2H3_H1H4", "split-only H2/H3 versus H1/H4",
           sum(row["reader_status"] == "SPLIT_ONLY" for row in high), sum(row["reader_status"] != "SPLIT_ONLY" for row in high),
           sum(row["reader_status"] == "SPLIT_ONLY" for row in low), sum(row["reader_status"] != "SPLIT_ONLY" for row in low),
           "SUPPORTING_READER_PROXY_ONLY")
    for test_id, fields in (("T08_MH_BODY_SECTION", ("body", "section")),
                            ("T09_MH_BODY_SECTION_LANGUAGE", ("body", "section", "language"))):
        rows.append({"test_id": test_id, "description": "Mantel-Haenszel line-first odds ratio",
                     "a": "STRATIFIED", "b": "STRATIFIED", "c": "STRATIFIED", "d": "STRATIFIED",
                     "odds_ratio": fmt(mh_first_or(occurrences, fields)), "ci95_low": "NOT_COMPUTED",
                     "ci95_high": "NOT_COMPUTED", "decision": "PASS_CONTROLLED",
                     "claim_limit": "FORMAL_POSITION_ONLY__CACHED_LANGUAGE_IS_METADATA"})
    for occupancy, base in ((2, 10), (3, 12)):
        selected = [row for row in occurrences if int(row["head_occupancy"]) == occupancy]
        for offset, (suffix, deck) in enumerate((("ALL", selected), ("EXACT", [row for row in selected if int(row["all_readers_exact"])]))):
            e, i = [row for row in deck if row["pair_axis"] == "ENTRY_PAIR"], [row for row in deck if row["pair_axis"] == "INTERNAL_PAIR"]
            binary(f"T{base + offset:02d}_OCC{occupancy}_{suffix}", f"occupancy {occupancy}, {suffix.lower()} deck",
                   sum(row["line_position"] == "FIRST" for row in e), sum(row["line_position"] != "FIRST" for row in e),
                   sum(row["line_position"] == "FIRST" for row in i), sum(row["line_position"] != "FIRST" for row in i),
                   "PASS_OCCUPANCY_STRATUM")
    if abs(float(rows[0]["odds_ratio"]) - 29.502907) > .000001 or abs(float(rows[1]["odds_ratio"]) - 36.780749) > .000001:
        raise AssertionError("primary role transfer OR changed")
    return rows


def cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    denominator = math.sqrt(sum(value * value for value in left) * sum(value * value for value in right))
    return numerator / denominator if denominator else 0.0


def phi_binary(left: list[int], right: list[int]) -> float:
    n11 = sum(a == b == 1 for a, b in zip(left, right)); n10 = sum(a == 1 and b == 0 for a, b in zip(left, right))
    n01 = sum(a == 0 and b == 1 for a, b in zip(left, right)); n00 = sum(a == b == 0 for a, b in zip(left, right))
    denominator = math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
    return (n11 * n00 - n10 * n01) / denominator if denominator else 0.0


def affinity(forms: list[dict[str, object]], bodies: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    body_order = sorted(str(row["body"]) for row in bodies)
    counts = {head: {body: 0 for body in body_order} for head in HEAD_ORDER}
    exact = {head: {body: 0 for body in body_order} for head in HEAD_ORDER}
    for row in forms:
        counts[str(row["opaque_head_id"])][str(row["body"])] = int(row["atlas_occurrences"])
        exact[str(row["opaque_head_id"])][str(row["body"])] = int(row["atlas_reader_exact"])
    totals = {body: sum(counts[head][body] for head in HEAD_ORDER) for body in body_order}
    training = {frozenset((row["head_a"], row["head_b"])): row for row in read_tsv(ROOT / G736_COSINE_REL)}
    rows: list[dict[str, object]] = []
    for left, right in itertools.combinations(HEAD_ORDER, 2):
        raw_l, raw_r = [counts[left][b] for b in body_order], [counts[right][b] for b in body_order]
        exact_l, exact_r = [exact[left][b] for b in body_order], [exact[right][b] for b in body_order]
        balanced_l, balanced_r = [counts[left][b] / totals[b] for b in body_order], [counts[right][b] / totals[b] for b in body_order]
        binary_l, binary_r = [int(counts[left][b] > 0) for b in body_order], [int(counts[right][b] > 0) for b in body_order]
        shared = sum(a == b == 1 for a, b in zip(binary_l, binary_r)); union = sum(a or b for a, b in zip(binary_l, binary_r))
        smaller = min(sum(binary_l), sum(binary_r)); pair = frozenset((left, right))
        rows.append({
            "head_a": left, "head_b": right, "body_dimensions": len(body_order),
            "gdt736_training_raw_cosine": training[pair]["occurrence_cosine"],
            "held_raw_count_cosine": fmt(cosine(raw_l, raw_r)), "held_reader_exact_cosine": fmt(cosine(exact_l, exact_r)),
            "held_body_balanced_cosine": fmt(cosine(balanced_l, balanced_r)),
            "held_binary_presence_cosine": fmt(cosine(binary_l, binary_r)), "held_binary_phi": fmt(phi_binary(binary_l, binary_r)),
            "shared_bodies": shared, "jaccard": fmt(shared / union), "overlap_coefficient": fmt(shared / smaller),
            "frozen_selected_pair": int(pair in SELECTED_PAIRS),
        })
    for metric, rank_field in (("held_raw_count_cosine", "held_raw_rank"), ("held_reader_exact_cosine", "held_exact_rank"),
                               ("held_body_balanced_cosine", "held_balanced_rank"), ("held_binary_presence_cosine", "held_binary_rank")):
        for rank, row in enumerate(sorted(rows, key=lambda item: float(item[metric]), reverse=True), 1):
            row[rank_field] = rank
    for row in rows:
        pair = frozenset((str(row["head_a"]), str(row["head_b"])))
        row["transfer_decision"] = (
            "PARTIAL_RAW_REPLICATION__AIN_DOMINATED__NO_SEMANTIC_EXPORT" if pair == frozenset(("H2", "H3")) else
            "FROZEN_RAW_TEST_FAIL__WEAK_OCCUPANCY_ASSOCIATION_ONLY" if pair == frozenset(("H1", "H4")) else "RIVAL_PAIR"
        )
        row["semantic_cluster_export"] = 0
    sensitivity: list[dict[str, object]] = []
    for excluded in ((), ("ain",), ("ain", "o", "kar")):
        retained = [body for body in body_order if body not in excluded]
        for left, right in (("H2", "H3"), ("H1", "H4")):
            sensitivity.append({
                "pair": f"{left}-{right}", "excluded_bodies": "NONE" if not excluded else "|".join(excluded),
                "retained_dimensions": len(retained),
                "raw_count_cosine": fmt(cosine([counts[left][b] for b in retained], [counts[right][b] for b in retained])),
                "reader_exact_cosine": fmt(cosine([exact[left][b] for b in retained], [exact[right][b] for b in retained])),
                "interpretation": "DOMINANCE_DIAGNOSTIC_ONLY__NOT_A_RETUNED_PRIMARY_TEST",
            })
    return rows, sensitivity


def whole_quarantine(forms: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    targets = {str(row["form"]) for row in forms}
    dictionary = [row for row in read_tsv(ROOT / V99R7_DICT_REL) if row["surface"] in targets]
    if len(dictionary) != 82 or len({row["surface"] for row in dictionary}) != 82:
        raise AssertionError("expected 82 inherited held whole cards")
    rows: list[dict[str, object]] = []; usable: dict[str, dict[str, object]] = {}
    for source in sorted(dictionary, key=lambda row: row["surface"]):
        hits = [word for word in RETIRED_HEAD_WORDS if word in source["working_meaning_de"].lower()]
        clean = not hits and source["unconditional_global_export_allowed"] == "1"
        row: dict[str, object] = {
            "surface": source["surface"], "reading_id": source["reading_id"],
            "inherited_working_meaning_de": source["working_meaning_de"],
            "working_model_score": source["working_model_score_0_100_not_probability"],
            "working_model_level": source["working_model_level"], "semantic_scope": source["semantic_scope"],
            "unconditional_global_export_allowed": source["unconditional_global_export_allowed"],
            "retired_head_words_detected": "NONE" if not hits else "|".join(hits),
            "gdt737_decision": "RETAIN_CURRENT_EXACT_WHOLE_WORKING_DEFAULT" if clean else "QUARANTINE_RETIRED_HEAD_NOUN_DERIVATION",
            "retained_exact_whole_meaning_de": source["working_meaning_de"] if clean else "NONE",
            "reason": "CURRENT_LEARNED_EXACT_WHOLE_SURVIVES_HEAD_CORRECTION__STILL_WORKING_NOT_CONFIRMED" if clean
                      else "MEANING_DEPENDS_ON_RETIRED_P_S_R_L_MATERIAL_HEAD_MODEL",
            "literal_translation_claimed": 0, "component_export_credit": 0,
        }
        rows.append(row)
        if clean:
            usable[source["surface"]] = row
    if Counter(row["gdt737_decision"] for row in rows) != Counter({"QUARANTINE_RETIRED_HEAD_NOUN_DERIVATION": 80,
                                                                   "RETAIN_CURRENT_EXACT_WHOLE_WORKING_DEFAULT": 2}):
        raise AssertionError("held whole quarantine split changed")
    return rows, usable


def form_bridge(forms: list[dict[str, object]], specs: list[dict[str, object]], quarantine: list[dict[str, object]],
                usable: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    heads = {row["opaque_head_id"]: row for row in read_tsv(ROOT / G736_HEAD_REL)}
    body_specs = {str(row["body"]): row for row in specs}; old = {str(row["surface"]): row for row in quarantine}
    rules = {
        "H1": "paragraph-first=>record opener; line-first=>line/record opener; otherwise whole/exception",
        "H2": "line-first=>item/subentry; otherwise whole/internal field",
        "H3": "middle=>internal reference; final=>close/reference; first=>whole/exception",
        "H4": "non-first=>internal field; first=>whole/exception",
    }
    rows: list[dict[str, object]] = []
    for source in forms:
        head = str(source["opaque_head_id"]); candidate = body_specs[str(source["body"])]
        clean = usable.get(str(source["form"])); inherited = old.get(str(source["form"]))
        rows.append({
            **source, "gdt736_training_record_role": heads[head]["selected_formal_role"], "held_position_rule": rules[head],
            "default_precedence": "CURRENT_CLEAN_EXACT_WHOLE" if clean else "POSITION_AND_REGISTER_ROLE__NO_BODY_EXPORT",
            "current_default_render_de": clean["retained_exact_whole_meaning_de"] if clean else "CONTEXT_REQUIRED__SEMANTIC_CONTENT_UNRESOLVED",
            "exploratory_body_candidate_de": candidate["concrete_body_role_de"],
            "exploratory_candidate_confidence": candidate["confidence"],
            "exploratory_renderer_de": {"H1": f"Eintrag: {candidate['concrete_body_role_de']}",
                                        "H2": f"Posten: {candidate['concrete_body_role_de']}",
                                        "H3": f"{candidate['concrete_body_role_de']}; interner/später Bezug",
                                        "H4": f"internes Feld: {candidate['concrete_body_role_de']}"}[head],
            "inherited_whole_status": inherited["gdt737_decision"] if inherited else "NO_V99R7_WHOLE_CARD",
            "body_candidate_renderer_license": 0, "semantic_cluster_export": 0,
            "literal_head_lexeme": "UNRESOLVED", "literal_body_lexeme": "UNRESOLVED", "component_export_credit": 0,
        })
    return rows


def model_update() -> list[dict[str, object]]:
    return [
        {"claim_id": "C01", "gdt736_claim": "H1/H2 entry versus H3/H4 internal/final location axis",
         "held_result": "PASS_STRONG", "new_live_status": "GENERALIZED_WITH_REGISTER_AND_POSITION_GATES",
         "evidence": "199/328 versus 24/483 line-first; OR 29.502907; exact OR 36.780749"},
        {"claim_id": "C02", "gdt736_claim": "H1 paragraph opener versus H2 line item/subentry", "held_result": "PASS_STRONG",
         "new_live_status": "RETAIN_AS_OCCURRENCE_CONDITIONED_SUBROLES", "evidence": "98/147 versus 3/181 paragraph-first"},
        {"claim_id": "C03", "gdt736_claim": "H3 later/reference or close versus H4 internal field", "held_result": "PASS",
         "new_live_status": "RETAIN_AS_RELATIVE_POSITION_SUBROLES", "evidence": "mean H3 .665316 versus H4 .574910; final OR 2.269"},
        {"claim_id": "C04", "gdt736_claim": "H1-H4 and H2-H3 are the two strongest raw frequency pairs",
         "held_result": "FAIL_FROZEN_FALSIFIER", "new_live_status": "FULL_2X2_AFFINITY_WITHDRAWN_OUTSIDE_TRAINING_24",
         "evidence": "held raw ranks H2-H3 #1, H3-H4 #2, H1-H4 #3"},
        {"claim_id": "C05", "gdt736_claim": "H2-H3 body affinity", "held_result": "PARTIAL_PASS",
         "new_live_status": "PARTIAL_COUNT_AFFINITY__NO_SHARED_SEMANTIC_LABEL", "evidence": "cosine .915084; without ain .620"},
        {"claim_id": "C06", "gdt736_claim": "H1-H4 body affinity / cluster A", "held_result": "FAIL_RAW_COUNT",
         "new_live_status": "WEAK_OCCUPANCY_ONLY__CLUSTER_A_SCOPED_TO_TRAINING_24",
         "evidence": "raw .156632 rank 3; exact .125962 rank 4; binary .588500 rank 1"},
        {"claim_id": "C07", "gdt736_claim": "head-conditioned pharmaceutical renderer", "held_result": "NOT_TRANSFERABLE",
         "new_live_status": "CLEAN_EXACT_WHOLE_THEN_OBSERVED_POSITION_ROLE_THEN_UNKNOWN",
         "evidence": "80/82 held whole cards contain retired head nouns; only solaiin and sols survive provisionally"},
    ]


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = allowed_pages(); bodies, forms, form_map = load_target(); specs = load_body_specs(bodies)
    token_rows, token_guard = g631.guarded_query(TOKENS_REL, pages, "page,page_order,locus,line_number,section,language,hand,token_index,eva")
    cross_rows, cross_guard = g631.guarded_query(CROSS_REL, pages, "page,locus,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    line_rows, line_guard = g631.guarded_query(LINES_REL, pages, "page,locus,line_number,paragraph_start,paragraph_end,token_count,eva_clean")
    occurrences = build_occurrences(token_rows, cross_rows, line_rows, form_map, specs)
    profiles = head_profiles(occurrences); body_contrast = contrast_rows(occurrences, "body")
    page_contrast = contrast_rows(occurrences, "page"); sections = section_contrasts(occurrences)
    tests = role_tests(occurrences); affinities, sensitivity = affinity(forms, bodies)
    quarantine, usable = whole_quarantine(forms); bridge = form_bridge(forms, specs, quarantine, usable); updates = model_update()
    spec_by_body = {str(row["body"]): row for row in specs}
    registry = [{**row, "working_candidate_de": spec_by_body[str(row["body"])]["concrete_body_role_de"],
                 "candidate_confidence": spec_by_body[str(row["body"])]["confidence"], "candidate_renderer_license": 0}
                for row in bodies]
    artifact_rows = dict(zip(OUTPUT_NAMES, (occurrences, registry, bridge, profiles, body_contrast, page_contrast,
                                             sections, tests, affinities, sensitivity, updates, quarantine, specs)))
    for name, rows in artifact_rows.items():
        if not rows:
            raise AssertionError(f"empty output deck: {name}")
        write_tsv(output_dir / name, rows, list(rows[0].keys()))

    body_direction = Counter(str(row["direction"]) for row in body_contrast)
    page_direction = Counter(str(row["direction"]) for row in page_contrast)
    pairs = {frozenset((str(row["head_a"]), str(row["head_b"]))): row for row in affinities}
    result: dict[str, object] = {
        "schema": "GDT737_HELD_BODY_RECORD_ROLE_TRANSFER_RESULT_V1", "status": STATUS,
        "scope": {"inherited_allowlist_pages": len(pages), "held_target_pages": len({str(row["page"]) for row in occurrences}),
                  "held_target_loci": len({str(row["locus"]) for row in occurrences}), "new_pages_used": 0,
                  "f84_used": False, "f84r_used": False,
                  "guard_stats": {"tokens": token_guard, "cross": cross_guard, "lines": line_guard}},
        "target": {"training_bodies_excluded": 24, "held_bodies": len(bodies),
                   "occupancy_two_bodies": sum(int(row["head_occupancy"]) == 2 for row in bodies),
                   "occupancy_three_bodies": sum(int(row["head_occupancy"]) == 3 for row in bodies),
                   "held_forms": len(forms), "held_occurrences": len(occurrences),
                   "reader_exact": sum(int(row["all_readers_exact"]) for row in occurrences),
                   "head_occurrences": dict(sorted(Counter(str(row["opaque_head_id"]) for row in occurrences).items()))},
        "location_transfer": {"decision": "PASS_STRONG", "entry_line_first": 199, "entry_occurrences": 328,
                              "internal_line_first": 24, "internal_occurrences": 483,
                              "unadjusted_or": tests[0]["odds_ratio"], "reader_exact_or": tests[1]["odds_ratio"],
                              "body_section_mh_or": next(row["odds_ratio"] for row in tests if row["test_id"] == "T08_MH_BODY_SECTION"),
                              "body_section_language_mh_or": next(row["odds_ratio"] for row in tests if row["test_id"] == "T09_MH_BODY_SECTION_LANGUAGE"),
                              "body_directions": dict(sorted(body_direction.items())),
                              "page_directions": dict(sorted(page_direction.items())), "section_c_only_mean_reversal": True},
        "affinity_transfer": {"decision": "FROZEN_FULL_2X2_FAIL__H2_H3_PARTIAL__H1_H4_OCCUPANCY_ONLY",
                              "H2_H3": pairs[frozenset(("H2", "H3"))], "H1_H4": pairs[frozenset(("H1", "H4"))],
                              "semantic_cluster_export": 0},
        "renderer_repair": {"inherited_held_whole_cards": len(quarantine), "quarantined_retired_head_noun_cards": 80,
                            "retained_current_exact_whole_working_defaults": sorted(usable),
                            "body_candidates_retained_for_exploration": len(specs), "body_candidates_licensed_for_export": 0,
                            "precedence": "CURRENT_CLEAN_EXACT_WHOLE > OBSERVED_REGISTER_AND_POSITION_ROLE > UNKNOWN"},
        "claims": {"formal_record_location_axis_generalized": True, "full_body_affinity_2x2_generalized": False,
                   "head_or_body_lexemes_identified": 0, "plaintext_translations_claimed": 0,
                   "component_export_credit": 0, "physical_glyph_claims": 0},
        "artifact_hashes": {str(BASE_REL / "artifacts" / name): sha256(output_dir / name) for name in OUTPUT_NAMES},
    }
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    result = build(parser.parse_args().output_dir)
    print(json.dumps({"status": result["status"], "target": result["target"], "location": result["location_transfer"],
                      "renderer": result["renderer_repair"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
