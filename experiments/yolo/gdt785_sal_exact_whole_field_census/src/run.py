#!/usr/bin/env python3
"""Build GDT785's exhaustive exact-whole `sal` semantic census."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt785_sal_exact_whole_field_census"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
CANDIDATE_SPECS = SRC / "CANDIDATE_ROLE_SPECS.tsv"
FINAL_SPEC = SRC / "FINAL_SELECTION_SPEC.tsv"
PASSAGE_SPECS = SRC / "PASSAGE_RENDER_SPECS.tsv"
HISTORICAL_SPECS = SRC / "HISTORICAL_ROLE_SPECS.tsv"

G782_RUN = ROOT / "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/run.py"
G736_OCC = ROOT / "experiments/yolo/gdt736_opaque_head_record_role_bridge/artifacts/OPAQUE_1166_OCCURRENCE_CONTEXTS.tsv"
G762_NULL = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/DIRECTED_PATTERN_NULL_CENSUS.tsv"
G762_REPAIR = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/SEMANTIC_PRECEDENCE_REPAIR_AUDIT.tsv"
G759_QUANTITY = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/QUANTITY_96_EXACT_PAIR_ATLAS.tsv"
G760_AMOUNT = ROOT / "experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/QUANTITY_281_EXPRESSION_ATLAS.tsv"
G777_SPLIT = ROOT / "experiments/yolo/gdt777_ol_registered_split_fusion_composer/artifacts/SAL_SPLIT_NEGATIVE_CONTROL.tsv"
G784_REVISION = ROOT / "experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/artifacts/GDT784_1_WORKING_REVISION.tsv"
G784_RENDERER = ROOT / "experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/artifacts/GDT784_376_RENDERER.tsv"
G735_HISTORICAL = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_ENTRY_ATLAS.tsv"

TARGET = "sal"
STATUS = (
    "PASS__37_RAW__33_EXACT_SAL__26_PAGES__23_FOLIOS__"
    "7_FIRST_16_MIDDLE_10_LAST__2_1_TRUE_PARAGRAPH_EDGES__"
    "EDGE_RANK_8_OF_68__SAL_SHOL_2__SAL_RAIIN_2__"
    "ZERO_OF_96_QUANTITY_PAIRS__23_SAL_STRING_FORMS__"
    "WORKING_SAL_DROGE__SALT_RETAINED_C0_RIVAL__"
    "CHORCHOLSAL_REINFORCED_NOT_DECOMPOSED__ZERO_LEXEMES"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        raise AssertionError(f"empty output: {path.name}")
    fields = list(rows[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: int(value) if isinstance(value := row.get(field, ""), bool) else value for field in fields})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_locks() -> tuple[int, str]:
    rows = read_tsv(SOURCE_LOCK)
    if len(rows) != 18:
        raise AssertionError(f"expected 18 locks, got {len(rows)}")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise AssertionError(f"unsafe source path: {relative}")
        if sha256(ROOT / relative) != row["expected_sha256"]:
            raise AssertionError(f"source changed: {relative}")
    return len(rows), sha256(SOURCE_LOCK)


def load_base():
    spec = importlib.util.spec_from_file_location("gdt782_locked", G782_RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT782 guarded context helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if match is None:
        raise AssertionError(page)
    return match.group(1)


def position(ordinal: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def broad_axes(base, patterns, cell: Mapping[str, str], repair: Mapping[str, Mapping[str, str]]) -> str:
    surface = cell["surface"]
    if surface == TARGET:
        return "TARGET_MASKED"
    text = repair[surface]["repaired_structural_candidate_de"] if surface in repair else cell["v99r7_semantic_value_de"]
    axes = base.semantic_axes(text, patterns)
    return "|".join(sorted(axes)) if axes else "OPEN"


def build_occurrences(base, by_line, exact, line_meta, cells) -> tuple[list[dict[str, object]], dict[str, object]]:
    repairs = {row["surface"]: row for row in read_tsv(G762_REPAIR)}
    patterns = base.load_axis_patterns()
    raw = [row for rows in by_line.values() for row in rows if row["eva"] == TARGET]
    selected: list[tuple[str, int, dict[str, str], list[dict[str, str]]]] = []
    for locus, rows in by_line.items():
        for index, token in enumerate(rows):
            if token["eva"] == TARGET and exact[locus, int(token["token_index"])]:
                selected.append((locus, index, token, rows))
    selected.sort(key=lambda item: (base.page_sort_key(item[2]["page"]), base.line_number(item[0]), item[1]))
    output: list[dict[str, object]] = []
    for number, (locus, index, token, rows) in enumerate(selected, 1):
        ordinal, length = index + 1, len(rows)
        meta = line_meta[locus]
        neighbor_values: dict[str, object] = {}
        for label, offset in (("l2", -2), ("l1", -1), ("r1", 1), ("r2", 2)):
            j = index + offset
            if j < 0 or j >= length:
                neighbor_values.update({f"{label}_surface": "EDGE", f"{label}_reader_exact": 0, f"{label}_axes": "EDGE"})
                continue
            neighbor = rows[j]
            nordinal = j + 1
            cell = cells[locus, nordinal]
            if cell["surface"] != neighbor["eva"]:
                raise AssertionError(f"cell mismatch: {locus}@{nordinal}")
            neighbor_values.update({
                f"{label}_surface": neighbor["eva"],
                f"{label}_reader_exact": exact[locus, int(neighbor["token_index"])],
                f"{label}_axes": broad_axes(base, patterns, cell, repairs),
            })
        left, right = str(neighbor_values["l1_surface"]), str(neighbor_values["r1_surface"])
        local, dispatch = "Droge", "GLOBAL_NOUN"
        if right == "shol":
            local, dispatch = "feuchte Droge", "RIGHT_MOIST_GERMAN_REORDER"
        elif right == "raiin":
            local, dispatch = "Droge; H3-Stufe III", "RIGHT_VALUE_FIELD"
        elif right == "araiin":
            local, dispatch = "drei Anteile Droge", "RIGHT_AMOUNT_FIELD"
        elif left == "qokeol":
            local, dispatch = "Droge bis zur mittleren Heizstufe erhitzen", "LEFT_HEAT_FIELD"
        elif left == "okey":
            local, dispatch = "bis zur Mittelstufe erhitzte Droge", "LEFT_HEAT_FIELD"
        elif left == "cheol" and right == "dain":
            local, dispatch = "trockene Droge; Wert II", "BILATERAL_DRY_VALUE_FIELD"
        output.append({
            "occurrence_id": f"G785-O{number:03d}", "page": token["page"], "physical_folio": physical_folio(token["page"]),
            "locus": locus, "section": token["section"], "language": token["language"], "hand": token["hand"],
            "sal_ordinal": ordinal, "line_token_count": length, "line_position": position(ordinal, length),
            "normalized_position": f"{(ordinal - 1) / max(length - 1, 1):.6f}",
            "paragraph_start_line": meta["paragraph_start"], "paragraph_end_line": meta["paragraph_end"],
            "sal_at_true_paragraph_start": int(meta["paragraph_start"] == "1" and ordinal == 1),
            "sal_at_true_paragraph_end": int(meta["paragraph_end"] == "1" and ordinal == length),
            "written_line_eva": " ".join(row["eva"] for row in rows), **neighbor_values,
            "fixed_working_default_de": "Droge", "contextual_focus_render_de": local, "syntax_dispatch": dispatch,
            "role_confidence": "C1_WORKING_ROLE", "identity_confidence": "C0_REPLACEABLE_DISPLAY",
            "reader_exact_sal": 1, "default_is_translation": 0, "confirmed_lexeme": 0,
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    summary = {
        "raw_occurrences": len(raw), "raw_page_labels": len({row["page"] for row in raw}),
        "exact_occurrences": len(output), "exact_page_labels": len({row["page"] for row in output}),
        "exact_physical_folios": len({row["physical_folio"] for row in output}), "exact_loci": len({row["locus"] for row in output}),
        "positions": Counter(row["line_position"] for row in output),
        "registers": Counter(f"{row['section']}|{row['language']}|{row['hand']}" for row in output),
        "paragraph_start_lines": sum(int(row["paragraph_start_line"]) for row in output),
        "paragraph_end_lines": sum(int(row["paragraph_end_line"]) for row in output),
        "true_paragraph_starts": sum(int(row["sal_at_true_paragraph_start"]) for row in output),
        "true_paragraph_ends": sum(int(row["sal_at_true_paragraph_end"]) for row in output),
    }
    expected_registers = Counter({"B|B|2": 12, "H|A|1": 7, "S|B|3": 6, "T|B|2": 4, "P|A|1": 3, "H|B|5": 1})
    shape = (summary["raw_occurrences"], summary["raw_page_labels"], summary["exact_occurrences"], summary["exact_page_labels"], summary["exact_physical_folios"], summary["exact_loci"])
    if shape != (37, 28, 33, 26, 23, 33) or summary["positions"] != Counter({"FIRST": 7, "MIDDLE": 16, "LAST": 10}) or summary["registers"] != expected_registers:
        raise AssertionError(f"sal census changed: {summary}")
    paragraph = (summary["paragraph_start_lines"], summary["paragraph_end_lines"], summary["true_paragraph_starts"], summary["true_paragraph_ends"])
    if paragraph != (4, 6, 2, 1):
        raise AssertionError(f"paragraph profile changed: {summary}")
    if any(row["page"].startswith("f84") or row["page"] == "f88r" for row in output):
        raise AssertionError("sealed or downstream target page leaked into standalone sal")
    return output, summary


def position_counts_for_exact(by_line, exact) -> dict[str, Counter[str]]:
    output: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for locus, rows in by_line.items():
        for index, token in enumerate(rows, 1):
            if exact[locus, int(token["token_index"])]:
                output[token["eva"]][position(index, len(rows))] += 1
    return dict(output)


def parse_positions(text: str) -> Counter[str]:
    values: Counter[str] = Counter()
    for field in text.split("|"):
        key, value = field.split(":")
        values[key] = int(value)
    return values


def add_control_row(control_id: str, scope: str, counts: Counter[str], form_count: int, sal_rank: object = "NA") -> dict[str, object]:
    occurrences = sum(counts.values())
    boundary = counts["FIRST"] + counts["LAST"] + counts["SINGLE"]
    return {
        "control_id": control_id, "scope": scope, "form_count": form_count, "exact_occurrences": occurrences,
        "first": counts["FIRST"], "middle": counts["MIDDLE"], "last": counts["LAST"], "single": counts["SINGLE"],
        "line_boundary_occurrences": boundary, "line_boundary_rate": f"{boundary / occurrences:.6f}",
        "sal_boundary_rate_ratio": f"{(17 / 33) / (boundary / occurrences):.6f}",
        "sal_rank_by_boundary_share": sal_rank, "meaning_credit": 0, "component_export_credit": 0,
    }


def build_position_controls(by_line, exact) -> list[dict[str, object]]:
    all_forms = position_counts_for_exact(by_line, exact)
    all_counts = sum(all_forms.values(), Counter())
    sal_counts = all_forms[TARGET]
    full_band = {surface: counts for surface, counts in all_forms.items() if 25 <= sum(counts.values()) <= 45}
    full_order = sorted(full_band, key=lambda surface: (-((full_band[surface]["FIRST"] + full_band[surface]["LAST"] + full_band[surface]["SINGLE"]) / sum(full_band[surface].values())), surface))
    full_counts = sum(full_band.values(), Counter())
    null_rows = [row for row in read_tsv(G762_NULL) if 25 <= int(row["reader_exact_occurrences"]) <= 45]
    clean_counts = sum((parse_positions(row["line_position_counts"]) for row in null_rows), Counter())
    clean_order = sorted(null_rows, key=lambda row: (-((parse_positions(row["line_position_counts"])["FIRST"] + parse_positions(row["line_position_counts"])["LAST"] + parse_positions(row["line_position_counts"])["SINGLE"]) / int(row["reader_exact_occurrences"])), row["surface"]))
    h2_rows = [row for row in read_tsv(G736_OCC) if row["opaque_head_id"] == "H2" and row["all_readers_exact"] == "1"]
    h2_counts = Counter(row["line_position"] for row in h2_rows)
    rows = [
        add_control_row("SAL", "TARGET_COMPLETE_WHOLE", sal_counts, 1, 1),
        add_control_row("ALL_EXACT", "ALL_24090_READER_EXACT_TOKENS", all_counts, len(all_forms)),
        add_control_row("FULL_FREQ_25_45", "ALL_GUARDED_FORMS_WITH_25_TO_45_EXACT", full_counts, len(full_band), full_order.index(TARGET) + 1),
        add_control_row("GDT762_CLEAN_FREQ_25_45", "CLEAN_RECURRENT_COMPLETE_FORMS_WITH_25_TO_45_EXACT", clean_counts, len(null_rows), next(i for i, row in enumerate(clean_order, 1) if row["surface"] == TARGET)),
        add_control_row("H2_EXACT", "ALL_GDT736_H2_READER_EXACT_OCCURRENCES", h2_counts, len({row["form"] for row in h2_rows})),
    ]
    if (sum(all_counts.values()), len(full_band), sum(full_counts.values()), sum(clean_counts.values()), len(null_rows), sum(h2_counts.values())) != (24090, 76, 2576, 2293, 68, 350):
        raise AssertionError("position control populations changed")
    if (rows[2]["line_boundary_occurrences"], rows[2]["sal_rank_by_boundary_share"], rows[3]["line_boundary_occurrences"], rows[3]["sal_rank_by_boundary_share"]) != (479, 8, 457, 8):
        raise AssertionError("matched position controls changed")
    if (h2_counts["FIRST"], h2_counts["MIDDLE"], h2_counts["LAST"]) != (177, 127, 46):
        raise AssertionError("H2 profile changed")
    return rows


def build_frames(occurrences, by_line, exact) -> list[dict[str, object]]:
    groups: defaultdict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for occurrence in occurrences:
        locus = str(occurrence["locus"])
        rows = by_line[locus]
        index = int(occurrence["sal_ordinal"]) - 1
        for side, offset in (("LEFT_TO_SAL", -1), ("SAL_TO_RIGHT", 1)):
            j = index + offset
            if not 0 <= j < len(rows):
                continue
            neighbor = rows[j]
            if not exact[locus, int(neighbor["token_index"])]:
                continue
            pair = f"{neighbor['eva']} sal" if side == "LEFT_TO_SAL" else f"sal {neighbor['eva']}"
            groups[side, pair].append(occurrence)
    output: list[dict[str, object]] = []
    for number, ((side, pair), hits) in enumerate(sorted(groups.items()), 1):
        output.append({
            "frame_id": f"G785-F{number:03d}", "direction": side, "written_pair_eva": pair,
            "reader_exact_pair_occurrences": len(hits), "page_labels": len({hit["page"] for hit in hits}),
            "physical_folios": len({hit["physical_folio"] for hit in hits}), "loci": "|".join(str(hit["locus"]) for hit in hits),
            "repeated_frame": int(len(hits) >= 2),
            "working_relation_de": "Droge mit rechtem Feuchtfeld" if pair == "sal shol" else "Droge mit rechtem H3-Stufe-III-Feld" if pair == "sal raiin" else "einmaliger Direktkontakt",
            "target_default_used_to_select_frame": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    repeats = {(row["written_pair_eva"], int(row["reader_exact_pair_occurrences"])) for row in output if row["repeated_frame"]}
    if repeats != {("sal shol", 2), ("sal raiin", 2)}:
        raise AssertionError(f"repeated direct frames changed: {repeats}")
    return output


def build_state_quantity_diagnostics(by_line, exact) -> list[dict[str, object]]:
    sal_null = next(row for row in read_tsv(G762_NULL) if row["surface"] == TARGET)
    fields = ("left_any_moist_contacts", "right_any_moist_contacts", "left_any_dry_contacts", "right_any_dry_contacts", "occurrences_with_same_line_moist", "occurrences_with_same_line_dry")
    if tuple(sal_null[field] for field in fields) != ("0", "4", "0", "0", "11", "10"):
        raise AssertionError("GDT762 sal polarity changed")
    quantity_rows = read_tsv(G759_QUANTITY)
    if len(quantity_rows) != 96:
        raise AssertionError("quantity pair deck changed")
    quantity_sal = [row for row in quantity_rows if row["left_surface"] == TARGET or row["right_surface"] == TARGET]
    bare_values, sal_raiin = [], []
    for locus, rows in by_line.items():
        for index in range(len(rows) - 1):
            left, right = rows[index], rows[index + 1]
            if left["eva"] != TARGET or not exact[locus, int(left["token_index"])] or not exact[locus, int(right["token_index"])]:
                continue
            if right["eva"] in {"ain", "aiin", "aiiin"}:
                bare_values.append(locus)
            if right["eva"] == "raiin":
                sal_raiin.append(locus)
    amount_contacts = [row for row in read_tsv(G760_AMOUNT) if row["left_surface"] == TARGET or row["right_surface"] == TARGET]
    split = read_tsv(G777_SPLIT)
    if len(split) != 1:
        raise AssertionError("split control changed")
    srow = split[0]
    if (len(quantity_sal), len(bare_values), sorted(sal_raiin), len(amount_contacts), amount_contacts[0]["source_expression_eva"]) != (0, 0, ["f76r.51", "f82r.24"], 1, "araiin"):
        raise AssertionError("sal amount diagnostics changed")
    if (srow["guarded_fused_exact_occurrences"], srow["guarded_raw_split_occurrences"], srow["guarded_reader_exact_split_occurrences"]) != ("33", "5", "0"):
        raise AssertionError("sal split negative control changed")
    values = [
        ("LEFT_DIRECT_MOIST", 0, "no evidence that sal follows a moist-state operator"), ("RIGHT_DIRECT_MOIST", 4, "nominal head before a moist field remains viable"),
        ("LEFT_DIRECT_DRY", 0, "sal is not selected as a dry follower"), ("RIGHT_DIRECT_DRY", 0, "sal itself is not identified as a dry-state word"),
        ("SAME_LINE_MOIST", 11, "moist ecology present"), ("SAME_LINE_DRY", 10, "dry ecology equally present"),
        ("GDT759_QUANTITY_PAIRS_TOTAL", 96, "control capacity"), ("GDT759_QUANTITY_PAIRS_WITH_SAL", 0, "amount/unit role weakened"),
        ("EXACT_SAL_BARE_AIN_FAMILY", 0, "amount/unit role weakened"), ("EXACT_SAL_RAIIN", 2, "nominal item plus H3 value-stage field"),
        ("GDT760_DIRECT_AMOUNT_CONTACTS", 1, "one sal araiin contact supports an item receiving three parts, not a unit"),
        ("RAW_S_AL_SPLIT_CANDIDATES", 5, "boundary dissent retained"), ("EXACT_S_AL_SPLIT_CANDIDATES", 0, "complete sal whole preserved"),
    ]
    return [{"diagnostic_id": f"G785-D{number:02d}", "metric": name, "value": value, "interpretation_de": meaning, "selects_specific_substance": 0, "eva_letter_credit": 0, "component_export_credit": 0} for number, (name, value, meaning) in enumerate(values, 1)]


def build_family(base, by_line, exact) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    form_counts: Counter[str] = Counter()
    pages: defaultdict[str, set[str]] = defaultdict(set)
    loci: defaultdict[str, set[str]] = defaultdict(set)
    all_exact_counts: Counter[str] = Counter()
    for locus, rows in by_line.items():
        for token in rows:
            if not exact[locus, int(token["token_index"])]:
                continue
            surface = token["eva"]
            all_exact_counts[surface] += 1
            if TARGET in surface:
                form_counts[surface] += 1
                pages[surface].add(token["page"])
                loci[surface].add(locus)

    def klass(surface: str) -> str:
        if surface == TARGET:
            return "STANDALONE"
        if surface.startswith(TARGET):
            return "PREFIX_CORE"
        if surface.endswith(TARGET):
            return "SUFFIX_CORE"
        return "INTERNAL_STRING"

    family = []
    for surface in sorted(form_counts):
        remainder = surface[len(TARGET):] if surface.startswith(TARGET) and surface != TARGET else surface[:-len(TARGET)] if surface.endswith(TARGET) and surface != TARGET else "NONE"
        family.append({
            "surface": surface, "sal_string_class": klass(surface), "reader_exact_occurrences": form_counts[surface],
            "page_labels": len(pages[surface]), "loci": len(loci[surface]),
            "sample_loci": "|".join(sorted(loci[surface], key=lambda locus: (base.page_sort_key(locus.split('.')[0]), base.line_number(locus))))[:500],
            "outer_remainder": remainder, "outer_remainder_reader_exact_occurrences": all_exact_counts[remainder] if remainder != "NONE" else 0,
            "clean_outer_remainder_recurrent": int(remainder != "NONE" and all_exact_counts[remainder] >= 2),
            "contains_f88r_target": int(surface == "chorcholsal"), "surface_meaning_assigned_from_sal": 0,
            "sal_core_status": "C1_FORMAL_LEFT_CORE_ONLY" if klass(surface) == "PREFIX_CORE" and remainder != "NONE" and all_exact_counts[remainder] >= 2 else "C0_STRING_ECHO_ONLY",
            "confirmed_component": 0, "component_export_credit": 0,
        })
    roots = [surface for surface, count in all_exact_counts.items() if len(surface) == 3 and 25 <= count <= 45]
    root_stats = []
    for root in roots:
        superforms = [surface for surface in all_exact_counts if surface != root and root in surface]
        prefix = [surface for surface in all_exact_counts if surface != root and surface.startswith(root) and all_exact_counts[surface[len(root):]] >= 2]
        suffix = [surface for surface in all_exact_counts if surface != root and surface.endswith(root) and all_exact_counts[surface[:-len(root)]] >= 2]
        root_stats.append({
            "root": root, "standalone_exact_occurrences": all_exact_counts[root],
            "all_superform_types": len(superforms), "all_superform_occurrences": sum(all_exact_counts[surface] for surface in superforms),
            "clean_prefix_types": len(prefix), "clean_prefix_occurrences": sum(all_exact_counts[surface] for surface in prefix),
            "clean_suffix_types": len(suffix), "clean_suffix_occurrences": sum(all_exact_counts[surface] for surface in suffix),
            "clean_prefix_surfaces": "|".join(sorted(prefix)) or "NONE", "clean_suffix_surfaces": "|".join(sorted(suffix)) or "NONE",
        })
    for field, rank_field in (("all_superform_types", "rank_superform_types"), ("all_superform_occurrences", "rank_superform_occurrences"), ("clean_prefix_types", "rank_clean_prefix_types"), ("clean_prefix_occurrences", "rank_clean_prefix_occurrences"), ("clean_suffix_types", "rank_clean_suffix_types"), ("clean_suffix_occurrences", "rank_clean_suffix_occurrences")):
        ordered = sorted(root_stats, key=lambda row: (-int(row[field]), str(row["root"])))
        ranks = {str(row["root"]): number for number, row in enumerate(ordered, 1)}
        for row in root_stats:
            row[rank_field] = ranks[str(row["root"])]
    root_stats.sort(key=lambda row: str(row["root"]))
    for row in root_stats:
        row.update({"score_is_probability": 0, "semantic_credit": 0, "component_export_credit": 0})
    classes, class_occurrences = Counter(), Counter()
    for row in family:
        classes[str(row["sal_string_class"])] += 1
        class_occurrences[str(row["sal_string_class"])] += int(row["reader_exact_occurrences"])
    summary = {
        "exact_tokens_containing_sal": sum(form_counts.values()), "complete_forms_containing_sal": len(form_counts),
        "standalone_occurrences": form_counts[TARGET], "nonstandalone_occurrences": sum(form_counts.values()) - form_counts[TARGET],
        "nonstandalone_forms": len(form_counts) - 1, "prefix_forms": classes["PREFIX_CORE"], "prefix_occurrences": class_occurrences["PREFIX_CORE"],
        "suffix_forms": classes["SUFFIX_CORE"], "suffix_occurrences": class_occurrences["SUFFIX_CORE"],
        "internal_forms": classes["INTERNAL_STRING"], "internal_occurrences": class_occurrences["INTERNAL_STRING"],
        "after_target_word_removal_occurrences": sum(form_counts.values()) - form_counts["chorcholsal"], "after_target_word_removal_forms": len(form_counts) - 1,
        "after_f88r_removal_occurrences": sum(count for surface, count in form_counts.items() if surface not in {"chorcholsal", "chosals"}), "after_f88r_removal_forms": len(form_counts) - 2,
    }
    sal_root = next(row for row in root_stats if row["root"] == TARGET)
    keys = ("exact_tokens_containing_sal", "complete_forms_containing_sal", "standalone_occurrences", "nonstandalone_occurrences", "nonstandalone_forms", "prefix_forms", "prefix_occurrences", "suffix_forms", "suffix_occurrences", "internal_forms", "internal_occurrences", "after_target_word_removal_occurrences", "after_target_word_removal_forms", "after_f88r_removal_occurrences", "after_f88r_removal_forms")
    if tuple(summary[key] for key in keys) != (58, 23, 33, 25, 22, 12, 14, 6, 7, 4, 4, 57, 22, 56, 21) or len(root_stats) != 12:
        raise AssertionError(f"sal family changed: {summary}")
    root_fields = ("all_superform_occurrences", "all_superform_types", "clean_prefix_occurrences", "clean_prefix_types", "clean_suffix_occurrences", "clean_suffix_types", "rank_superform_occurrences", "rank_superform_types", "rank_clean_prefix_occurrences", "rank_clean_prefix_types", "rank_clean_suffix_occurrences", "rank_clean_suffix_types")
    if tuple(sal_root[field] for field in root_fields) != (25, 22, 13, 11, 2, 1, 11, 10, 5, 3, 11, 12):
        raise AssertionError(f"sal trigram morphology changed: {sal_root}")
    return family, root_stats, summary


def build_candidates(final: Mapping[str, str]) -> list[dict[str, object]]:
    point_fields = ("nominal_content_fit", "right_state_value_fit", "line_field_edge_fit", "paragraph_nonmarker_fit", "h2_distinctiveness_fit", "quantity_null_fit", "long_whole_prediction_fit", "historical_architecture_fit")
    rows = []
    for source in read_tsv(CANDIDATE_SPECS):
        score = sum(int(source[field]) for field in point_fields) - int(source["specificity_penalty"])
        rows.append({**source, "diagnostic_score": score, "score_is_probability": 0, "selected_working_default": int(source["candidate_id"] == final["selected_candidate_id"]), "eva_spelling_credit": 0, "confirmed_lexeme": 0, "specific_substance_confirmed": 0})
    rows.sort(key=lambda row: (-int(row["diagnostic_score"]), str(row["candidate_id"])))
    for rank, row in enumerate(rows, 1):
        row["score_rank"] = rank
    if rows[0]["candidate_id"] != "C01_DRUG_MATERIAL" or int(rows[0]["diagnostic_score"]) != 18 or sum(int(row["selected_working_default"]) for row in rows) != 1:
        raise AssertionError("candidate outcome changed")
    return rows


def build_historical() -> list[dict[str, object]]:
    source_rows = {row["observation_id"]: row for row in read_tsv(G735_HISTORICAL)}
    if not {"HEO005", "HEO006", "HEO007", "HEO008", "HEO009", "HEO013"} <= set(source_rows):
        raise AssertionError("historical provenance changed")
    rows = read_tsv(HISTORICAL_SPECS)
    if len(rows) != 5 or any(row["selects_voynich_identity"] != "0" or row["spelling_credit"] != "0" for row in rows):
        raise AssertionError("historical specs exceed ceiling")
    return [{**row, "allowed_use": "ARCHITECTURE_AND_ROLE_CLASS_ONLY", "voynich_identity_credit": 0, "component_export_credit": 0} for row in rows]


def build_passages(by_line, exact) -> list[dict[str, object]]:
    output = []
    for source in read_tsv(PASSAGE_SPECS):
        locus, ordinal = source["locus"], int(source["sal_ordinal"])
        rows = by_line[locus]
        line = " ".join(row["eva"] for row in rows)
        if rows[ordinal - 1]["eva"] != TARGET or not exact[locus, int(rows[ordinal - 1]["token_index"])] or source["focus_span_eva"] not in line:
            raise AssertionError(f"passage target changed: {source['passage_id']}")
        if "Droge" not in source["focus_render_de"] or "Droge" not in source["full_exploratory_render_de"]:
            raise AssertionError(f"fixed default missing: {source['passage_id']}")
        output.append({**source, "page": rows[0]["page"], "physical_folio": physical_folio(rows[0]["page"]), "written_line_eva": line, "fixed_sal_default_de": "Droge", "render_status": "WORKING_DISPLAY_NOT_PLAINTEXT", "inherited_non_sal_cards_reopened": 0, "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0})
    if len(output) != 12 or len({row["locus"] for row in output}) != 12:
        raise AssertionError("passage deck changed")
    return output


def build_dictionary(final: Mapping[str, str], family_summary: Mapping[str, object]) -> tuple[list[dict[str, object]], dict[str, object]]:
    parent = read_tsv(G784_REVISION)
    if len(parent) != 1 or parent[0]["surface"] != "chorcholsal" or parent[0]["practical_whole_default_de"] != "trockene Blütendroge":
        raise AssertionError("GDT784 target revision changed")
    dictionary = [
        {"entry": TARGET, "preferred_working_default_de": final["practical_default_de"], "alternate_1_de": final["alternate_1_de"], "alternate_2_de": final["alternate_2_de"], "portable_role_de": final["portable_role_de"], "surface_confidence": "C2_COMPLETE_WHOLE", "role_confidence": final["role_confidence"], "identity_confidence": final["identity_confidence"], "exact_occurrences": 33, "exact_pages": 26, "working_evidence": final["positive_evidence_de"], "counterevidence": final["counterevidence_de"], "scope": "ALL_33_READER_EXACT_STANDALONE_SAL_ONLY", "replaceable": 1, "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0},
        {"entry": "chorcholsal", "preferred_working_default_de": "trockene Blütendroge", "alternate_1_de": "getrocknetes Blütenpräparat", "alternate_2_de": "trockenes Blütensalz", "portable_role_de": "lexikalisierte Pflanzendrogenganzform mit PART+DRY und C0 sal-Echo", "surface_confidence": "C2_COMPLETE_WHOLE", "role_confidence": "C1_PART_DRY__C0_SAL_SUFFIX_ECHO", "identity_confidence": "C0_REPLACEABLE_DISPLAY", "exact_occurrences": 1, "exact_pages": 1, "working_evidence": "GDT784 whole boundary and PART+DRY echo; GDT785 makes the drug reading compositionally coherent after target removal.", "counterevidence": "The sal family is morphologically weak in suffix position: only recurrent clean X+sal is o+sal; the target is a singleton and the whole display predates this sal audit.", "scope": "ONE_COMPLETE_WHOLE__NO_SUBSTRING_EXPORT", "replaceable": 1, "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0},
    ]
    bridge = {
        "bridge_id": "G785-B001", "surface": "chorcholsal", "parent_default_de": parent[0]["practical_whole_default_de"],
        "gdt785_default_de": "trockene Blütendroge", "display_changed": 0, "surface_boundary": "C2_COMPLETE_WHOLE",
        "parent_internal_echo": "PART_PLUS_DRY_C1", "new_sal_external_role": "NOMINAL_DRUG_OR_MATERIAL_C1",
        "sal_inside_target_status": "C0_NONEXPORTING_SUFFIX_ECHO", "working_internal_read_de": "Pflanzenteil + trocken + Droge",
        "suffix_direction_morphology": "WEAK__CLEAN_X_PLUS_SAL_ONLY_OSAL_2_OCCURRENCES",
        "target_removed_standalone_sal_occurrences": 33, "target_removed_sal_family_occurrences": family_summary["after_target_word_removal_occurrences"],
        "salt_rival_de": "trockenes Blütensalz", "salt_rival_status": "C0_RETAINED_NO_EXCLUSIVE_PREDICTION_NO_SPELLING_CREDIT",
        "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
    }
    return dictionary, bridge


def build_renderer(parent, bridge) -> tuple[list[dict[str, object]], set[str]]:
    output, owners, targets = [], set(), 0
    for row in parent:
        target = row["locus"] == "f88r.22" and row["right_surface"] == "chorcholsal"
        targets += int(target)
        new = dict(row)
        new.update({
            "gdt785_branch": "SAL_ROLE_REINFORCES_EXISTING_WHOLE" if target else "INHERITED_GDT784",
            "gdt785_default_de": row["gdt784_default_de"],
            "gdt785_sal_external_default_de": "Droge" if target else "NOT_APPLICABLE",
            "gdt785_sal_inside_surface_status": bridge["sal_inside_target_status"] if target else "NOT_APPLICABLE",
            "gdt785_display_changed": 0, "gdt785_renderer_contextual": row["gdt784_renderer_contextual"],
            "gdt785_consumed_token_count": row["gdt784_consumed_token_count"], "gdt785_consumed_token_ids": row["gdt784_consumed_token_ids"],
            "gdt785_default_is_translation": 0, "gdt785_confirmed_lexeme": 0, "gdt785_confirmed_plaintext": 0, "gdt785_component_export_credit": 0,
        })
        output.append(new)
        ids = row["gdt784_consumed_token_ids"]
        if ids not in {"", "NONE"}:
            for token_id in ids.split("|"):
                if token_id in owners:
                    raise AssertionError(f"consumption collision: {token_id}")
                owners.add(token_id)
    shape = (len(output), targets, sum(int(row["gdt785_renderer_contextual"]) for row in output), len(owners), sum(int(row["gdt785_display_changed"]) for row in output))
    if shape != (376, 1, 270, 230, 0):
        raise AssertionError("cumulative renderer totals changed")
    return output, owners


def make_packet(occurrences) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_locus = {row["locus"]: row for row in occurrences}
    packet = []
    for number, (locus, target_surface) in enumerate((("f76r.51", "raiin"), ("f78v.30", "shol"), ("f82r.24", "raiin"), ("f89v1.17", "shol")), 1):
        row = by_locus[locus]
        right_ordinal = int(row["sal_ordinal"]) + 1
        packet.append({
            "edge_id": f"G785-E{number:03d}", "batch_id": "GDT785_REPEATED_SAL_RIGHT_FRAMES", "page": row["page"], "physical_folio": row["physical_folio"],
            "diagram_unit_id": f"LINE:{locus}", "pivot_visual_id": f"TOKEN:{locus}:{row['sal_ordinal']}", "pivot_locus": f"{locus}@{row['sal_ordinal']}",
            "target_visual_id": f"TOKEN:{locus}:{right_ordinal}", "target_locus": f"{locus}@{right_ordinal}", "relation_type": f"SAL_PRECEDES_{target_surface.upper()}",
            "direction_basis": "TRANSCRIPTION_ORDER_ONLY", "ownership_basis": "NONVISUAL_TEXT_FIELD_ADJACENCY", "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT785", "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT785_RUNNER", "relation_reviewer": "GDT785_VALIDATOR", "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "ROLE_C1_IDENTITY_C0", "formal_access_state": "SEALED_NOT_ACCESSED", "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
    crosswalk = [{"edge_id": row["edge_id"], "batch_id": row["batch_id"], "page": row["page"], "physical_folio": row["physical_folio"], "locus": row["diagram_unit_id"].split(":", 1)[1], "relation_type": row["relation_type"], "working_sal_default_de": "Droge", "semantic_score_eligible": 0, "confirmed_plaintext": 0, "component_export_credit": 0} for row in packet]
    return packet, crosswalk


def artifact_readme() -> str:
    return """# GDT785 artifacts

- `GDT785_33_EXACT_CONTEXT_ATLAS.tsv`: every reader-exact standalone `sal` with two neighbours per side and broad target-free axes.
- `GDT785_5_POSITION_CONTROLS.tsv`: target, global, two frequency-matched and H2 position profiles.
- `GDT785_EXACT_DIRECT_FRAME_CENSUS.tsv`: all reader-exact immediate pairs; only `sal shol` and `sal raiin` repeat.
- `GDT785_13_STATE_QUANTITY_DIAGNOSTICS.tsv`: state balance, quantity null and fused/split controls.
- `GDT785_23_SAL_STRING_FAMILY.tsv`: all exact complete surfaces containing the literal string `sal`.
- `GDT785_12_TRIGRAM_ROOT_CONTROLS.tsv`: matched root productivity; `sal` is moderate on the left and weak as a suffix.
- `GDT785_8_CANDIDATE_SCORECARDS.tsv`: concrete role ranking; scores are not probabilities.
- `GDT785_5_HISTORICAL_ROLE_COMPARATORS.tsv`: period architecture only, never a Voynich spelling match.
- `GDT785_12_PRACTICAL_PASSAGES.tsv`: one fixed `sal=Droge` display; only German syntax changes.
- dictionary, `chorcholsal` bridge, cumulative renderer, relation packet/intake and replay metadata.

No artifact confirms a plaintext word, a specific drug, salt, seed, an EVA
letter value or a component usable outside its enumerated whole.
"""


def build_report(result, controls, frames, candidates, passages, family_summary) -> str:
    control_table = "\n".join(f"| {row['control_id']} | {row['exact_occurrences']} | {row['line_boundary_occurrences']} | {row['line_boundary_rate']} | {row['sal_rank_by_boundary_share']} |" for row in controls)
    frame_table = "\n".join(f"| `{row['written_pair_eva']}` | {row['reader_exact_pair_occurrences']} | {row['loci']} | {row['working_relation_de']} |" for row in frames if int(row["repeated_frame"]))
    candidate_table = "\n".join(f"| {row['score_rank']} | {row['one_word_default_de']} | {row['role_id']} | {row['diagnostic_score']} |" for row in candidates)
    passage_table = "\n".join(f"| {row['locus']} | `{row['focus_span_eva']}` | {row['focus_render_de']} |" for row in passages)
    return f"""# GDT785 — `sal`: from open field to **Droge**

Status: `{result['status']}`

## Working result

The single practical card is **`sal = Droge`**, in the historical apothecary
sense of medicinal material or ingredient. It is used unchanged for all 33
reader-exact standalone occurrences. The portable C1 role is a **nominal
drug/material head**; the word identity remains C0 and replaceable. “Arzneizutat”
is the nearest explanatory synonym, “Präparat” the strongest class rival.

This is materially narrower than the inherited “item/subentry” label. It says
what kind of item the field most likely carries. It is still a working renderer,
not a deciphered plaintext lexeme.

## Why a noun rather than a switch

There are 37 raw and 33 reader-exact wholes on 26 page labels and 23 physical
folios: 7 first, 16 medial and 10 last. Although `sal` is strongly line-edge
biased, it itself occupies only **two true paragraph starts and one true
paragraph end**. It therefore cannot globally mean heading, next item or end.
Its H2 parent class is much more initial (177/350) and much less final (46/350)
than `sal`, so the inherited structural head does not by itself explain this
surface.

| control | exact occurrences | line edge | rate | sal rank |
|---|---:|---:|---:|---:|
{control_table}

The clean matched pool contains 68 recurrent whole forms with 25--45 exact
occurrences. Its pooled edge rate is 0.199; `sal` is 17/33 = 0.515, rank 8/68.

## The two repeated constructions

| frame | count | loci | working reading |
|---|---:|---|---|
{frame_table}

`sal shol` naturally yields **feuchte Droge** and `sal raiin` **Droge, H3-Stufe
III**. Four clean moist fields occur immediately right and none left. Yet the
same-line ecology is balanced at 11 moist versus 10 dry contexts, so `sal`
itself is not a moisture or dryness word.

The amount rival fails cleanly: `sal` enters zero of GDT759's 96 quantity pairs,
and there is no reader-exact `sal ain/aiin/aiiin`. The single direct GDT760
contact `sal araiin` reads more naturally as **drei Anteile Droge** than as one
unit followed by another amount.

## Morphology without wishful splitting

There are {family_summary['exact_tokens_containing_sal']} exact tokens in
{family_summary['complete_forms_containing_sal']} complete surfaces containing
the string `sal`: 33 standalone and 25 in 22 longer forms. The longer tail has
12 left-core forms (14 occurrences), six suffix forms (7 occurrences), and four
internal-string forms (4 occurrences). Against twelve equally frequent
three-character wholes, `sal+X` ranks 3/12 by clean recurrent extension types,
but `X+sal` ranks only 12/12. Thus a formal left stem is plausible; a productive
suffix inside `chorcholsal` is specifically weak. Nothing is freely split or
exported.

## Concrete candidate ranking

| rank | display | role | diagnostic score |
|---:|---|---|---:|
{candidate_table}

The scores are throughput weights, not probabilities. **Salz** remains a real
C0 substance rival. It can fit the contexts, but explains none better than an
ordinary drug/ingredient; the resemblance of EVA `sal` to Latin *sal* earns
zero credit. “Saat-Rohstoff” remains retired because it depended on the failed
`s + al` split.

## Twelve practical checks

| locus | focused EVA | fixed-card rendering |
|---|---|---|
{passage_table}

The full exploratory line displays remain in the artifact. Question marks are
preserved instead of being filled with generic prose.

## Consequence for `chorcholsal`

The external 33-case result is independent of f88r: no standalone `sal` occurs
there. Only after selection is the target reopened. The existing whole display
**`chorcholsal = trockene Blütendroge`** now has the coherent internal working
echo `Pflanzenteil + trocken + Droge`, but remains one C2 written whole. Because
the `X+sal` direction is morphologically weak and the target is a singleton,
the new `sal` echo is only C0 and non-exporting. The concrete salt rival would
give “trockenes Blütensalz”; it currently predicts nothing extra.

## Historical fit and ceiling

Wellcome MS.542 supplies the closest period architecture: learned drug/material
and plant-part heads coexist with short quality and degree fields, while recipe
commands and quantities form a separate channel. Pal.lat.1256 likewise combines
drug names, synonyms and substitutes with distinct recipe/dose material. These
comparators support a nominal class, never a Voynich spelling identity.

All 376 cumulative renderer rows remain byte-semantic equivalents: 270
contextual, 106 fallback and 230 consumed token IDs; the existing target display
does not change. Confirmed lexemes, plaintext clauses, specific substances and
component exports remain zero. No new page, image, OCR or transcription was
opened; f84/f84r stayed sealed.

## Reproduction

```bash
python3 -B experiments/yolo/gdt785_sal_exact_whole_field_census/src/run.py
python3 -B experiments/yolo/gdt785_sal_exact_whole_field_census/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt785_sal_exact_whole_field_census/artifacts/GDT785_GDT388_REPEATED_FRAME_PACKET.tsv
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts, report_path = args.artifacts_dir.resolve(), args.report_path.resolve()
    lock_count, lock_hash = verify_locks()
    base = load_base()
    by_line, exact, _, line_meta, cells, guard = base.load_context()
    final_rows = read_tsv(FINAL_SPEC)
    if len(final_rows) != 1 or any(final_rows[0][field] != "0" for field in ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit", "specific_substance_confirmed")):
        raise AssertionError("one ceiling-compliant final selection required")
    final = final_rows[0]
    occurrences, occurrence_summary = build_occurrences(base, by_line, exact, line_meta, cells)
    controls = build_position_controls(by_line, exact)
    frames = build_frames(occurrences, by_line, exact)
    diagnostics = build_state_quantity_diagnostics(by_line, exact)
    family, root_controls, family_summary = build_family(base, by_line, exact)
    candidates = build_candidates(final)
    historical = build_historical()
    passages = build_passages(by_line, exact)
    dictionary, bridge = build_dictionary(final, family_summary)
    renderer, owners = build_renderer(read_tsv(G784_RENDERER), bridge)
    packet, crosswalk = make_packet(occurrences)
    outputs = {
        "GDT785_33_EXACT_CONTEXT_ATLAS.tsv": occurrences, "GDT785_5_POSITION_CONTROLS.tsv": controls,
        "GDT785_EXACT_DIRECT_FRAME_CENSUS.tsv": frames, "GDT785_13_STATE_QUANTITY_DIAGNOSTICS.tsv": diagnostics,
        "GDT785_23_SAL_STRING_FAMILY.tsv": family, "GDT785_12_TRIGRAM_ROOT_CONTROLS.tsv": root_controls,
        "GDT785_8_CANDIDATE_SCORECARDS.tsv": candidates, "GDT785_5_HISTORICAL_ROLE_COMPARATORS.tsv": historical,
        "GDT785_12_PRACTICAL_PASSAGES.tsv": passages, "GDT785_2_WORKING_DICTIONARY.tsv": dictionary,
        "GDT785_1_CHORCHOLSAL_BRIDGE.tsv": [bridge], "GDT785_376_RENDERER.tsv": renderer,
        "GDT785_GDT388_REPEATED_FRAME_PACKET.tsv": packet, "GDT785_RELATION_EDGE_CROSSWALK.tsv": crosswalk,
    }
    for name, rows in outputs.items():
        write_tsv(artifacts / name, rows)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.relation_edge_intake import validate_relation_edge_packet
    intake = validate_relation_edge_packet(artifacts / "GDT785_GDT388_REPEATED_FRAME_PACKET.tsv")
    expected_intake = {"status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 4, "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False, "holdout_gate": False, "mobile_null_gate": False, "score_ready": False, "errors": []}
    if intake != expected_intake:
        raise AssertionError(f"unexpected intake: {intake}")
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)
    result: dict[str, object] = {
        "experiment_id": "GDT785", "status": STATUS, "source_locks": lock_count, "source_lock_sha256": lock_hash,
        "source_spec_sha256": {"candidates": sha256(CANDIDATE_SPECS), "final_selection": sha256(FINAL_SPEC), "passages": sha256(PASSAGE_SPECS), "historical": sha256(HISTORICAL_SPECS)},
        "inherited_guard": guard,
        "sal": {"raw": occurrence_summary["raw_occurrences"], "reader_exact": occurrence_summary["exact_occurrences"], "pages": occurrence_summary["exact_page_labels"], "physical_folios": occurrence_summary["exact_physical_folios"], "positions": dict(occurrence_summary["positions"]), "registers": dict(occurrence_summary["registers"]), "paragraph_start_lines": occurrence_summary["paragraph_start_lines"], "paragraph_end_lines": occurrence_summary["paragraph_end_lines"], "true_paragraph_starts": occurrence_summary["true_paragraph_starts"], "true_paragraph_ends": occurrence_summary["true_paragraph_ends"]},
        "controls": {row["control_id"]: {"occurrences": row["exact_occurrences"], "boundary_rate": row["line_boundary_rate"], "sal_rank": row["sal_rank_by_boundary_share"]} for row in controls},
        "repeated_frames": {row["written_pair_eva"]: row["reader_exact_pair_occurrences"] for row in frames if int(row["repeated_frame"])},
        "state_quantity": {"right_moist": 4, "same_line_moist": 11, "same_line_dry": 10, "gdt759_quantity_pairs_with_sal": 0, "bare_value_pairs": 0, "sal_raiin": 2, "direct_amount_contacts": 1},
        "family": family_summary,
        "adjudication": {"winner": final["selected_candidate_id"], "portable_role_de": final["portable_role_de"], "practical_default_de": final["practical_default_de"], "role_confidence": final["role_confidence"], "identity_confidence": final["identity_confidence"], "salt_retained_rival": True, "salt_spelling_credit": 0},
        "chorcholsal": {"display": bridge["gdt785_default_de"], "display_changed": False, "internal_working_read_de": bridge["working_internal_read_de"], "sal_suffix_status": bridge["sal_inside_target_status"]},
        "renderer": {"rows": len(renderer), "contextual": sum(int(row["gdt785_renderer_contextual"]) for row in renderer), "fallbacks": sum(1 - int(row["gdt785_renderer_contextual"]) for row in renderer), "unique_consumed_tokens": len(owners), "display_changes": 0},
        "relation_packet": intake, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "specific_substances": 0, "component_exports": 0,
        "new_pages": 0, "new_images": 0, "new_ocr": 0, "new_transcriptions": 0, "sealed_pages_accessed": 0,
        "claim_ceiling": "C2 standalone sal whole; C1 nominal drug/material role; C0 replaceable Droge display and nonexporting longer-form echo; no plaintext, specific substance, salt/seed identity, EVA value or component export.",
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.write_text(build_report(result, controls, frames, candidates, passages, family_summary), encoding="utf-8")
    (artifacts / "README.md").write_text(artifact_readme(), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
