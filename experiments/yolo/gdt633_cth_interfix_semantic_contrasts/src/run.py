#!/usr/bin/env python3
"""Build GDT633: concrete semantic defaults for the GDT632 CTH lattice."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts")
ART = ROOT / BASE_REL / "artifacts"
G632_BASE = Path("experiments/yolo/gdt632_cth_interfix_lattice")
G632_RUN_REL = G632_BASE / "src/run.py"
G632_RESULT_REL = G632_BASE / "artifacts/RESULT.json"
G632_ALLOW_REL = G632_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G632_OCC_REL = G632_BASE / "artifacts/INTERFIX_FAMILY_OCCURRENCES.tsv"
G632_QUALITY_REL = G632_BASE / "artifacts/INTERFIX_QUALITY_DEGREE_CONTACTS.tsv"
G632_SEPARATED_REL = G632_BASE / "artifacts/ALL_READER_SEPARATED_SHELL_CTH_SPANS.tsv"
G632_BRIDGES_REL = G632_BASE / "artifacts/CROSS_READER_INTERFIX_BOUNDARY_BRIDGES.tsv"
G632_DICT_REL = G632_BASE / "artifacts/WORKING_DICTIONARY_V9.tsv"
G624_BASE = Path("experiments/yolo/gdt624_productive_quality_shell_grid")
G624_RESULT_REL = G624_BASE / "artifacts/RESULT.json"
G624_E_SERIES_REL = G624_BASE / "artifacts/E_LENGTH_SERIES.tsv"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")

spec = importlib.util.spec_from_file_location("gdt632_builder", ROOT / G632_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT632 builder helpers")
g632 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g632)

OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "outer_occurrences": BASE_REL / "artifacts/OUTER_LITERAL_E_RUN_OCCURRENCES.tsv",
    "outer_lattice": BASE_REL / "artifacts/OUTER_LITERAL_E_RUN_LATTICE.tsv",
    "outer_ladders": BASE_REL / "artifacts/OUTER_E_FIXED_BODY_LADDERS.tsv",
    "ee_contexts": BASE_REL / "artifacts/EE_RIVAL_CONTEXTS.tsv",
    "e_background": BASE_REL / "artifacts/LITERAL_E_RUN_BACKGROUND.tsv",
    "inner_ladders": BASE_REL / "artifacts/INNER_CTH_E_RUN_LADDERS.tsv",
    "inner_pages": BASE_REL / "artifacts/INNER_E_PAGE_COEXISTENCE.tsv",
    "inner_contexts": BASE_REL / "artifacts/INNER_E_SHARED_CONTEXTS.tsv",
    "o_distribution": BASE_REL / "artifacts/O_HEAD_DISTRIBUTION.tsv",
    "o_same_remainder": BASE_REL / "artifacts/O_CTH_SAME_REMAINDER_CONTEXTS.tsv",
    "o_shared_contexts": BASE_REL / "artifacts/O_CTH_SHARED_CONTEXTS.tsv",
    "e_heating": BASE_REL / "artifacts/E_BINDING_VS_HEATING.tsv",
    "controlled_pairs": BASE_REL / "artifacts/CONTROLLED_INTERFIX_TYPE_PAIRS.tsv",
    "microeditions": BASE_REL / "artifacts/SAME_PAGE_MICROEDITIONS.tsv",
    "translations": BASE_REL / "artifacts/CONCRETE_TRANSLATIONS_V5.tsv",
    "atoms": BASE_REL / "artifacts/ATOMIC_MEANING_CANDIDATES.tsv",
    "scoreboard": BASE_REL / "artifacts/CANDIDATE_SCOREBOARD.tsv",
    "predictions": BASE_REL / "artifacts/PREDICTION_DECK.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V10.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

OUTER_RE = re.compile(r"^(ch|sh)(e*)(o?)cth(.*)$")
HEAD_RE = re.compile(r"^(o?)cth(.*)$")
INNER_Y_RE = re.compile(r"^(o?)cth(e*)y$")
Q_LABEL = {"ch": "CH", "sh": "SH"}
Q_SURFACE = {"CH": "ch", "SH": "sh"}
INTERFIX_FOR = {(0, 0): "NONE", (1, 0): "E", (0, 1): "O", (1, 1): "EO"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    g632.write_tsv(path, rows, fields)


def pos_label(index: int, length: int) -> str:
    if index == 0:
        return "FIRST"
    if index + 1 == length:
        return "LAST"
    return "MIDDLE"


def counter_text(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def form_label(remainder: str) -> str:
    if remainder == "y":
        return "GRUNDFORM"
    if remainder == "ey":
        return "FORM_I"
    if remainder == "eey":
        return "FORM_II"
    if remainder == "BARE":
        return "KOPF_OHNE_REST"
    return f"RESTFORM_{remainder}"


def concrete_gloss(q: str, e_level: int, o_slot: int, remainder: str, section: str) -> tuple[str, str, str, str]:
    dry = q == "CH"
    quality_pred = "trocken" if dry else "feucht"
    if o_slot:
        noun = "Blatt-/Krautzubereitung" if section == "H" else "CTH-Drogenzubereitung"
        adjective = "trockene" if dry else "feuchte"
    else:
        noun = "Blatt-/Krautgut" if section == "H" else "CTH-Drogenmaterial"
        adjective = "trockenes" if dry else "feuchtes"
    if e_level == 0:
        reading = f"{noun}: {quality_pred}"
        binding = "UNgebunden_prädikativ"
    elif e_level == 1:
        reading = f"{adjective} {noun}"
        binding = "attributiv_gebunden"
    else:
        reading = f"{adjective} {noun}; erweiterte Bindungsstufe {e_level}"
        binding = f"erweiterte_Bindungsstufe_{e_level}"
    label = form_label(remainder)
    if label == "FORM_I":
        reading += ", Form I"
    elif label == "FORM_II":
        reading += ", Form II"
    elif label.startswith("RESTFORM_"):
        reading += f"; Rest {remainder} offen"
    return reading, noun, binding, label


def make_outer_occurrences(
    token_rows: list[dict[str, str]], cross_by_locus: dict[str, dict[str, str]],
    by_line: dict[str, list[dict[str, object]]], line_text: dict[str, str],
) -> list[dict[str, object]]:
    ordinal: Counter[tuple[str, str]] = Counter()
    positions = {
        (locus, int(token["token_index"])): (index, len(line))
        for locus, line in by_line.items() for index, token in enumerate(line)
    }
    rows: list[dict[str, object]] = []
    for source in sorted(token_rows, key=g632.g631.token_sort_key):
        match = OUTER_RE.fullmatch(source["eva"])
        if match is None:
            continue
        q = Q_LABEL[match.group(1)]
        e_level = len(match.group(2))
        o_slot = int(bool(match.group(3)))
        remainder = match.group(4) or "BARE"
        if e_level > 2:
            continue
        ordinal[source["locus"], source["eva"]] += 1
        cross = cross_by_locus[source["locus"]]
        exact_caps = [cross[field].split().count(source["eva"]) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        norm_caps = [g632.g631.concatenated_span_count(cross[field].split(), source["eva"]) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        index, length = positions[source["locus"], int(source["token_index"])]
        line = by_line[source["locus"]]
        reading, noun, binding, inner_form = concrete_gloss(q, e_level, o_slot, remainder, source["section"])
        rows.append({
            "occurrence_id": "", "page": source["page"], "locus": source["locus"],
            "token_index": int(source["token_index"]), "surface": source["eva"], "quality_prefix": q,
            "outer_e_level": e_level, "o_slot": o_slot, "remainder": remainder,
            "structural_parse": f"{match.group(1)}+{'e' * e_level or '∅'}+{match.group(3) or '∅'}+cth+{remainder}",
            "triple_exact_token_stable": int(ordinal[source["locus"], source["eva"]] <= min(exact_caps)),
            "triple_boundary_normalized": int(ordinal[source["locus"], source["eva"]] <= min(norm_caps)),
            "left_surface": str(line[index - 1]["eva"]) if index else "<START>",
            "right_surface": str(line[index + 1]["eva"]) if index + 1 < length else "<END>",
            "position": pos_label(index, length), "section": source["section"], "language": source["language"], "hand": source["hand"],
            "material_default_de": noun, "outer_e_default_de": binding, "inner_form_default_de": inner_form,
            "working_translation_de": reading, "surface_line": line_text[source["locus"]],
        })
    for index, row in enumerate(rows, 1):
        row["occurrence_id"] = f"G633-O{index:04d}"
    return rows


def make_outer_lattice(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for e_level in range(3):
        for o_slot in range(2):
            cell = [row for row in rows if int(row["outer_e_level"]) == e_level and int(row["o_slot"]) == o_slot]
            result.append({
                "outer_e_level": e_level, "o_slot": o_slot, "occurrences": len(cell),
                "types": len({str(row["surface"]) for row in cell}), "pages": len({str(row["page"]) for row in cell}),
                "ch_occurrences": sum(row["quality_prefix"] == "CH" for row in cell),
                "sh_occurrences": sum(row["quality_prefix"] == "SH" for row in cell),
                "section_counts": counter_text(str(row["section"]) for row in cell),
                "language_counts": counter_text(str(row["language"]) for row in cell),
                "position_counts": counter_text(str(row["position"]) for row in cell),
                "working_slot_de": "attributive Bindung" if e_level == 1 else "erweiterte Bindungsstufe II" if e_level == 2 else "ungebundene/prädikative Form",
                "working_head_de": "Zubereitung/Ansatz aus CTH-Material" if o_slot else "CTH-Material",
            })
    return result


def make_outer_ladders(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    surface_counts = Counter(str(row["surface"]) for row in rows)
    groups: dict[tuple[str, int, str], dict[int, str]] = defaultdict(dict)
    for surface in sorted(surface_counts):
        match = OUTER_RE.fullmatch(surface)
        assert match is not None
        groups[(Q_LABEL[match.group(1)], int(bool(match.group(3))), match.group(4) or "BARE")][len(match.group(2))] = surface
    result: list[dict[str, object]] = []
    for key, levels in sorted(groups.items()):
        if len(levels) < 2:
            continue
        q, o_slot, remainder = key
        result.append({
            "ladder_id": "", "quality_prefix": q, "o_slot": o_slot, "remainder": remainder,
            "observed_e_levels": "|".join(map(str, sorted(levels))), "distinct_levels": len(levels),
            "e0_surface": levels.get(0, "NONE"), "e0_occurrences": surface_counts[levels[0]] if 0 in levels else 0,
            "e1_surface": levels.get(1, "NONE"), "e1_occurrences": surface_counts[levels[1]] if 1 in levels else 0,
            "e2_surface": levels.get(2, "NONE"), "e2_occurrences": surface_counts[levels[2]] if 2 in levels else 0,
            "working_contrast_de": "prädikativ/ungebunden ↔ attributiv gebunden ↔ erweiterte Bindungsstufe",
        })
    for index, row in enumerate(result, 1):
        row["ladder_id"] = f"G633-L{index:03d}"
    return result


def make_ee_contexts(rows: list[dict[str, object]], cross_by_locus: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    counts = Counter(str(row["surface"]) for row in rows)
    result: list[dict[str, object]] = []
    for source in rows:
        if int(source["outer_e_level"]) != 2:
            continue
        q = str(source["quality_prefix"])
        o_slot = int(source["o_slot"])
        remainder = str(source["remainder"])
        prefix = Q_SURFACE[q]
        e0 = prefix + ("o" if o_slot else "") + "cth" + ("" if remainder == "BARE" else remainder)
        e1 = prefix + "e" + ("o" if o_slot else "") + "cth" + ("" if remainder == "BARE" else remainder)
        cross = cross_by_locus[str(source["locus"])]
        result.append({
            "ee_id": "", "page": source["page"], "locus": source["locus"], "surface": source["surface"],
            "quality_prefix": q, "o_slot": o_slot, "remainder": remainder,
            "e0_counterpart": e0, "e0_occurrences": counts[e0], "e1_counterpart": e1, "e1_occurrences": counts[e1],
            "triple_exact_token_stable": source["triple_exact_token_stable"], "position": source["position"],
            "section": source["section"], "language": source["language"], "hand": source["hand"],
            "left_surface": source["left_surface"], "right_surface": source["right_surface"],
            "working_translation_de": source["working_translation_de"],
            "zl3b_line": cross["zl3b_clean"], "it2a_line": cross["it2a_clean"], "rf1b_line": cross["rf1b_clean"],
        })
    for index, row in enumerate(result, 1):
        row["ee_id"] = f"G633-EE{index:02d}"
    return result


def make_e_background(token_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    token_counts = Counter(row["eva"] for row in token_rows)
    families: dict[str, dict[int, str]] = defaultdict(dict)
    for surface in sorted(token_counts):
        runs = list(re.finditer(r"e+", surface))
        if len(runs) != 1:
            continue
        run = runs[0]
        skeleton = surface[:run.start()] + "<E>" + surface[run.end():]
        families[skeleton][len(run.group())] = surface
    result: list[dict[str, object]] = []
    for skeleton, levels in sorted(families.items()):
        if len(levels) < 2:
            continue
        result.append({
            "family_id": "", "skeleton": skeleton, "e_lengths": "|".join(map(str, sorted(levels))),
            "distinct_lengths": len(levels), "surfaces_by_length": "|".join(f"{level}:{levels[level]}" for level in sorted(levels)),
            "occurrences_by_length": "|".join(f"{level}:{token_counts[levels[level]]}" for level in sorted(levels)),
            "types": len(levels), "occurrences": sum(token_counts[surface] for surface in levels.values()),
            "has_e_ee": int({1, 2} <= set(levels)), "has_e_ee_eee": int({1, 2, 3} <= set(levels)),
            "has_e_through_eeee": int({1, 2, 3, 4} <= set(levels)),
        })
    for index, row in enumerate(result, 1):
        row["family_id"] = f"G633-EB{index:04d}"
    return result


def make_inner_occurrences(
    token_rows: list[dict[str, str]], cross_by_locus: dict[str, dict[str, str]],
    by_line: dict[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    positions = {
        (locus, int(token["token_index"])): (index, len(line))
        for locus, line in by_line.items() for index, token in enumerate(line)
    }
    ordinal: Counter[tuple[str, str]] = Counter()
    rows: list[dict[str, object]] = []
    for source in sorted(token_rows, key=g632.g631.token_sort_key):
        match = INNER_Y_RE.fullmatch(source["eva"])
        if match is None:
            continue
        level = len(match.group(2))
        if level > 3:
            continue
        ordinal[source["locus"], source["eva"]] += 1
        exact_caps = [cross_by_locus[source["locus"]][field].split().count(source["eva"]) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        index, length = positions[source["locus"], int(source["token_index"])]
        line = by_line[source["locus"]]
        rows.append({
            "page": source["page"], "locus": source["locus"], "surface": source["eva"],
            "head_prefix": "O_CTH" if match.group(1) else "CTH", "inner_e_level": level,
            "left_surface": str(line[index - 1]["eva"]) if index else "<START>",
            "right_surface": str(line[index + 1]["eva"]) if index + 1 < length else "<END>",
            "position": pos_label(index, length), "section": source["section"], "language": source["language"], "hand": source["hand"],
            "triple_exact_token_stable": int(ordinal[source["locus"], source["eva"]] <= min(exact_caps)),
        })
    return rows


def make_inner_tables(inner: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    ladders: list[dict[str, object]] = []
    for head in ("CTH", "O_CTH"):
        for level in range(4):
            cell = [row for row in inner if row["head_prefix"] == head and int(row["inner_e_level"]) == level]
            surface = ("o" if head == "O_CTH" else "") + "cth" + "e" * level + "y"
            ladders.append({
                "head_prefix": head, "inner_e_level": level, "surface": surface, "occurrences": len(cell),
                "pages": len({str(row["page"]) for row in cell}), "herbal_occurrences": sum(row["section"] == "H" for row in cell),
                "section_counts": counter_text(str(row["section"]) for row in cell),
                "language_counts": counter_text(str(row["language"]) for row in cell),
                "position_counts": counter_text(str(row["position"]) for row in cell),
                "triple_exact_occurrences": sum(int(row["triple_exact_token_stable"]) for row in cell),
                "working_form_de": "Grundform" if level == 0 else f"Formstufe {level}",
                "observation_status": "ATTESTED" if cell else "PREDICTED_GAP" if (head, level) in (("CTH", 3), ("O_CTH", 2)) else "UNOBSERVED_CONTROL",
            })
    page_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in inner:
        page_groups[str(row["head_prefix"]), str(row["page"])].append(row)
    pages: list[dict[str, object]] = []
    for (head, page), rows in sorted(page_groups.items()):
        levels = sorted({int(row["inner_e_level"]) for row in rows if int(row["inner_e_level"]) <= 2})
        if len(levels) < 2:
            continue
        pages.append({
            "head_prefix": head, "page": page, "inner_e_levels": "|".join(map(str, levels)),
            "distinct_levels": len(levels), "occurrences": len(rows), "surfaces": "|".join(sorted({str(row["surface"]) for row in rows})),
            "loci": "|".join(sorted({str(row["locus"]) for row in rows})),
        })
    contexts_by: dict[tuple[str, str], dict[int, list[dict[str, object]]]] = defaultdict(lambda: defaultdict(list))
    for row in inner:
        if row["head_prefix"] != "CTH" or int(row["inner_e_level"]) > 2:
            continue
        for side, neighbor in (("LEFT", str(row["left_surface"])), ("RIGHT", str(row["right_surface"]))):
            contexts_by[side, neighbor][int(row["inner_e_level"])].append(row)
    contexts: list[dict[str, object]] = []
    for (side, neighbor), levels in sorted(contexts_by.items()):
        if len(levels) < 2:
            continue
        contexts.append({
            "context_id": "", "fixed_side": side, "fixed_neighbor": neighbor,
            "inner_e_levels": "|".join(map(str, sorted(levels))), "distinct_levels": len(levels),
            "occurrences_by_level": "|".join(f"{level}:{len(levels[level])}" for level in sorted(levels)),
            "surfaces": "|".join(sorted({str(row["surface"]) for rows in levels.values() for row in rows})),
            "pages": len({str(row["page"]) for rows in levels.values() for row in rows}),
            "loci": "|".join(sorted({str(row["locus"]) for rows in levels.values() for row in rows})),
        })
    for index, row in enumerate(contexts, 1):
        row["context_id"] = f"G633-IC{index:03d}"
    return ladders, pages, contexts


def make_head_rows(token_rows: list[dict[str, str]], by_line: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    positions = {
        (locus, int(token["token_index"])): (index, len(line))
        for locus, line in by_line.items() for index, token in enumerate(line)
    }
    rows: list[dict[str, object]] = []
    for source in sorted(token_rows, key=g632.g631.token_sort_key):
        match = HEAD_RE.fullmatch(source["eva"])
        if match is None:
            continue
        index, length = positions[source["locus"], int(source["token_index"])]
        line = by_line[source["locus"]]
        rows.append({
            "page": source["page"], "locus": source["locus"], "surface": source["eva"],
            "head_prefix": "O_CTH" if match.group(1) else "CTH", "remainder": match.group(2) or "BARE",
            "left_surface": str(line[index - 1]["eva"]) if index else "<START>",
            "right_surface": str(line[index + 1]["eva"]) if index + 1 < length else "<END>",
            "position": pos_label(index, length), "section": source["section"], "language": source["language"], "hand": source["hand"],
        })
    return rows


def make_o_tables(heads: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    distribution: list[dict[str, object]] = []
    for head in ("CTH", "O_CTH"):
        cell = [row for row in heads if row["head_prefix"] == head]
        distribution.append({
            "head_prefix": head, "occurrences": len(cell), "types": len({str(row["surface"]) for row in cell}),
            "remainders": len({str(row["remainder"]) for row in cell}), "pages": len({str(row["page"]) for row in cell}),
            "herbal_occurrences": sum(row["section"] == "H" for row in cell),
            "section_counts": counter_text(str(row["section"]) for row in cell),
            "language_counts": counter_text(str(row["language"]) for row in cell),
            "position_counts": counter_text(str(row["position"]) for row in cell),
            "working_head_de": "Zubereitung/Ansatz aus CTH-Material" if head == "O_CTH" else "CTH-Drogenmaterial; im Herbal Blatt-/Krautgut",
        })
    cth_counts = Counter(str(row["surface"]) for row in heads if row["head_prefix"] == "CTH")
    cth_pages: dict[str, set[str]] = defaultdict(set)
    for row in heads:
        if row["head_prefix"] == "CTH":
            cth_pages[str(row["surface"])].add(str(row["page"]))
    same: list[dict[str, object]] = []
    for source in [row for row in heads if row["head_prefix"] == "O_CTH"]:
        counterpart = "cth" + ("" if source["remainder"] == "BARE" else str(source["remainder"]))
        same.append({
            "context_id": "", "page": source["page"], "locus": source["locus"], "o_surface": source["surface"],
            "remainder": source["remainder"], "cth_counterpart": counterpart,
            "cth_counterpart_occurrences": cth_counts[counterpart], "cth_counterpart_pages": len(cth_pages[counterpart]),
            "same_page_counterpart": int(str(source["page"]) in cth_pages[counterpart]),
            "left_surface": source["left_surface"], "right_surface": source["right_surface"],
            "position": source["position"], "section": source["section"], "language": source["language"], "hand": source["hand"],
            "working_contrast_de": "CTH-Material ↔ Zubereitung/Ansatz aus demselben CTH-Material",
        })
    for index, row in enumerate(same, 1):
        row["context_id"] = f"G633-OR{index:03d}"
    contexts_by: dict[tuple[str, str, str], dict[str, list[dict[str, object]]]] = defaultdict(lambda: defaultdict(list))
    for row in heads:
        for side, neighbor in (("LEFT", str(row["left_surface"])), ("RIGHT", str(row["right_surface"]))):
            contexts_by[str(row["remainder"]), side, neighbor][str(row["head_prefix"])].append(row)
    shared: list[dict[str, object]] = []
    for (remainder, side, neighbor), values in sorted(contexts_by.items()):
        if not {"CTH", "O_CTH"} <= set(values):
            continue
        shared.append({
            "context_id": "", "remainder": remainder, "fixed_side": side, "fixed_neighbor": neighbor,
            "cth_occurrences": len(values["CTH"]), "octh_occurrences": len(values["O_CTH"]),
            "cth_surfaces": "|".join(sorted({str(row["surface"]) for row in values["CTH"]})),
            "octh_surfaces": "|".join(sorted({str(row["surface"]) for row in values["O_CTH"]})),
            "pages": len({str(row["page"]) for rows in values.values() for row in rows}),
            "loci": "|".join(sorted({str(row["locus"]) for rows in values.values() for row in rows})),
        })
    for index, row in enumerate(shared, 1):
        row["context_id"] = f"G633-OC{index:03d}"
    return distribution, same, shared


def make_heating_rows(g632_occ: list[dict[str, str]], quality: list[dict[str, str]]) -> list[dict[str, object]]:
    contacts: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in quality:
        contacts[row["occurrence_id"]].append(row)
    rows: list[dict[str, object]] = []
    for scope, section in (("GLOBAL", None), ("SECTION_B", "B"), ("SECTION_S", "S")):
        for o_slot in range(2):
            for e_slot in range(2):
                target_interfix = INTERFIX_FOR[e_slot, o_slot]
                cell = [row for row in g632_occ if row["interfix"] == target_interfix and (section is None or row["section"] == section)]
                def has(row: dict[str, str], axis: str, immediate: bool = False) -> bool:
                    return any(axis in item["quality_axes"].split("|") and (not immediate or int(item["distance"]) == 1) for item in contacts[row["occurrence_id"]])
                rows.append({
                    "scope": scope, "outer_e_slot": e_slot, "o_slot": o_slot, "interfix": target_interfix,
                    "occurrences": len(cell), "hot_occurrences": sum(has(row, "HOT") for row in cell),
                    "cold_occurrences": sum(has(row, "COLD") for row in cell),
                    "immediate_hot_occurrences": sum(has(row, "HOT", True) for row in cell),
                    "immediate_cold_occurrences": sum(has(row, "COLD", True) for row in cell),
                    "hot_share": f"{sum(has(row, 'HOT') for row in cell) / len(cell):.6f}" if cell else "0.000000",
                    "cold_share": f"{sum(has(row, 'COLD') for row in cell) / len(cell):.6f}" if cell else "0.000000",
                    "diagnosis_de": "E ist vorkommensnormalisiert nicht heiß-angereichert; Kältemangel hält Erhitzen nur als schwachen Rivalen offen",
                })
    return rows


def make_controlled_pairs(outer: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter(str(row["surface"]) for row in outer)
    groups: dict[tuple[str, int, int, str], str] = {}
    for surface in counts:
        match = OUTER_RE.fullmatch(surface)
        assert match is not None
        groups[Q_LABEL[match.group(1)], len(match.group(2)), int(bool(match.group(3))), match.group(4) or "BARE"] = surface
    result: list[dict[str, object]] = []
    def add(axis: str, fixed: str, left_key: tuple[str, int, int, str], right_key: tuple[str, int, int, str], meaning: str) -> None:
        left, right = groups[left_key], groups[right_key]
        result.append({
            "pair_id": "", "axis": axis, "fixed_body": fixed, "left_surface": left, "right_surface": right,
            "left_occurrences": counts[left], "right_occurrences": counts[right], "working_contrast_de": meaning,
        })
    for q, e_level, o_slot, remainder in sorted(groups):
        if e_level == 0 and (q, 1, o_slot, remainder) in groups:
            add("OUTER_E_INSERTION", f"{q}|O{o_slot}|{remainder}", (q, 0, o_slot, remainder), (q, 1, o_slot, remainder), "prädikativ/ungebunden ↔ attributiv gebunden")
        if o_slot == 0 and (q, e_level, 1, remainder) in groups and e_level <= 1:
            add("O_INSERTION", f"{q}|E{e_level}|{remainder}", (q, e_level, 0, remainder), (q, e_level, 1, remainder), "CTH-Material ↔ Zubereitung/Ansatz aus CTH-Material")
        if e_level == 1 and o_slot == 0 and (q, 0, 1, remainder) in groups:
            add("E_VS_O", f"{q}|{remainder}", (q, 1, 0, remainder), (q, 0, 1, remainder), "attributive Materialform ↔ prädikative Zubereitungsform")
    for index, row in enumerate(result, 1):
        row["pair_id"] = f"G633-P{index:03d}"
    return result


def make_microeditions(line_text: dict[str, str]) -> list[dict[str, object]]:
    cases = (
        ("f29r.1", "cheecthy", "ch+ee+cth+y", "trockenes Blatt-/Krautgut; erweiterte Bindungsstufe II", "qotchy und qoty bleiben außerhalb dieser CTH-Lesung"),
        ("f82v.36", "sheecthey qokaiin", "sh+ee+cth+ey | qok+a+III", "feuchtes CTH-Drogenmaterial, Form I, erweiterte Bindungsstufe II; heiß, Grad III", "übrige Nachbarn bleiben unverändert"),
        ("f80r.18", "shcthy qotol shecthy qokain", "sh+cth+y | qot+ol | sh+e+cth+y | qok+a+II", "CTH-Drogenmaterial: feucht; kalt; feuchtes CTH-Drogenmaterial; heiß, Grad II", "keine Prozesswörter ergänzt"),
        ("f80v.10", "qokaiin shcthy ... qokal shecthy", "qok+a+III | sh+cth+y | ... | qok+al | sh+e+cth+y", "heiß, Grad III: CTH-Drogenmaterial, feucht; …; feuchtes CTH-Drogenmaterial", "qokal bleibt als sichtbarer Qualitätsnachbar erhalten"),
        ("f20v.10", "chocthy chol daiin", "ch+o+cth+y | ch+ol | d+a+III", "trockene Blatt-/Krautzubereitung: trocken, Grad III", "nur die unmittelbar sichtbare Materialphrase gelesen"),
        ("f22v.15", "sho | cthy chocthy qokchy", "sh+o | cth+y | ch+o+cth+y | qok+ch+y", "feuchte Blatt-/Krautzubereitung; trockene Blatt-/Krautzubereitung; heiß-trockene Qualitätsangabe", "dory bleibt für die nächste Nachbarwort-Runde"),
        ("f114v.33", "cheo | ctheey ↔ cheoctheey", "ch+e+o | cth+eey", "attributiv trockene CTH-Drogenzubereitung, Form II", "octheey ist daraus vorhergesagt, nicht beobachtet"),
        ("f85r1.21", "okaiin cheocthey", "ok+a+III | ch+e+o+cth+ey", "heiß, Grad III: attributiv trockene CTH-Drogenzubereitung, Form I", "keine Bedeutung für die entfernten Nachbarn ergänzt"),
    )
    rows: list[dict[str, object]] = []
    for index, (locus, target, parse, reading, residual) in enumerate(cases, 1):
        rows.append({
            "case_id": f"G633-M{index:02d}", "page": locus.split(".")[0], "locus": locus,
            "surface_line": line_text[locus], "target_span": target, "structural_parse": parse,
            "working_translation_de": reading, "residual_policy_de": residual,
        })
    return rows


def make_translations(
    outer: list[dict[str, object]], separated: list[dict[str, str]], bridges: list[dict[str, str]],
    meta_by_locus: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in outer:
        rows.append({
            "translation_id": "", "source_kind": "FUSED", "source_id": source["occurrence_id"],
            "page": source["page"], "locus": source["locus"], "surface_display": source["surface"],
            "normalized_surface": source["surface"], "quality_prefix": source["quality_prefix"],
            "outer_e_level": source["outer_e_level"], "o_slot": source["o_slot"], "remainder": source["remainder"],
            "working_translation_de": source["working_translation_de"], "observation_status": "OBSERVED_FUSED",
            "residual_policy_de": "Nur der sichtbare CTH-Ausdruck wird gelesen; Nachbarn werden nicht mit Füllprosa ergänzt",
        })
    boundary_rows: list[dict[str, str]] = list(separated)
    selected_loci = {"f114v.33", "f21r.9", "f21v.5", "f21r.7"}
    for row in bridges:
        if row["locus"] in selected_loci:
            boundary_rows.append(row)
    for source in boundary_rows:
        q = source["quality_prefix"]
        interfix = source["interfix"]
        e_level = int(interfix in ("E", "EO"))
        o_slot = int(interfix in ("O", "EO"))
        remainder = source["remainder"]
        meta = meta_by_locus[source["locus"]]
        reading, _, _, _ = concrete_gloss(q, e_level, o_slot, remainder, meta["section"])
        display = source["separated_surface"] if "separated_surface" in source else source.get("observed_realizations", source.get("surface", "NONE"))
        normalized = source["fused_counterpart"] if "fused_counterpart" in source else source["surface"]
        rows.append({
            "translation_id": "", "source_kind": "ALL_READER_SEPARATED" if "span_id" in source else "READER_BOUNDARY_BRIDGE",
            "source_id": source.get("span_id", source.get("bridge_id", "NONE")), "page": source["page"], "locus": source["locus"],
            "surface_display": display, "normalized_surface": normalized, "quality_prefix": q,
            "outer_e_level": e_level, "o_slot": o_slot, "remainder": remainder,
            "working_translation_de": reading, "observation_status": "OBSERVED_BOUNDARY_REALIZATION",
            "residual_policy_de": "Wortgrenze ändert die Arbeitsbedeutung nicht",
        })
    for index, row in enumerate(rows, 1):
        row["translation_id"] = f"G633-T{index:04d}"
    return rows


def make_atoms() -> list[dict[str, object]]:
    values = (
        ("ch", "QUALITÄTSKERN", "trocken", "technische Klasse A", "PROVISIONAL_PRIMARY"),
        ("sh", "QUALITÄTSKERN", "feucht", "technische Klasse B", "PROVISIONAL_PRIMARY"),
        ("äußeres e", "BINDUNG", "attributive Bindung; im deutschen Fließtext meist null", "erhitzt/gekocht; Grad I", "NEW_PRIMARY_DEFAULT"),
        ("äußeres ee", "BINDUNGSSTUFE", "erweiterte/zweite Bindungsstufe", "Intensität; Grad II", "NEW_PRIMARY_DEFAULT"),
        ("cth", "MATERIALKOPF", "Drogenmaterial; im Herbal Blatt-/Krautgut", "oberirdischer Pflanzenteil", "INHERITED_PRIMARY"),
        ("o+cth", "ABGELEITETER_MATERIALKOPF", "Zubereitung/Ansatz aus CTH-Material", "Auszug/Mazerat; Nominalmarker", "NEW_PRIMARY_DEFAULT"),
        ("inneres y", "FORM", "Grundform", "Flexionsschluss", "NEW_FORM_DEFAULT"),
        ("inneres ey", "FORM", "Material-/Zubereitungsform I", "Flexionsform", "NEW_FORM_DEFAULT"),
        ("inneres eey", "FORM", "Material-/Zubereitungsform II", "Flexionsform", "NEW_FORM_DEFAULT"),
    )
    return [
        {"candidate_id": f"G633-A{index:02d}", "visible_unit": unit, "slot": slot, "primary_default_de": primary,
         "live_rival_de": rival, "status": status}
        for index, (unit, slot, primary, rival, status) in enumerate(values, 1)
    ]


def make_scoreboard() -> list[dict[str, object]]:
    values = (
        (1, "E_ATTRIBUTIVE__O_PREPARATION", "e bindet ch/sh attributiv; o bildet eine Zubereitung aus CTH-Material", "13 E- und 10 O-Kanten; nackte octh-Reihe; same-line E-Wechsel; praktische Materialkomposition", "o kann noch Nominal-/Registermarker sein", "PRIMARY_WORKING_TRANSLATION"),
        (2, "E_GRADE_OR_COLD_EXCLUSION__O_PREPARATION", "e/ee markieren Qualitätsstufen oder vermeiden kalte Kontexte; o bleibt Zubereitung", "produktive e-Längen; kalte E-Kontakte selten", "E ist vorkommensnormalisiert nicht heiß-angereichert", "LIVE_CONCRETE_RIVAL"),
        (3, "REGISTER_INFLECTION__O_NOMINAL", "e und o sind Flexions-/Registerformen desselben CTH-Kopfs", "starke Registerprofile und geteilte Reste", "same-page Koexistenz und konkrete Kopfportabilität bleiben unerklärt", "LIVE_FORMAL_RIVAL"),
        (4, "O_SPECIFIC_MEDIUM", "o bedeutet Wasser, Wein, Öl, Saft oder einen bestimmten Auszug", "eine Zubereitungslesung könnte später enger werden", "kein unabhängiger Mediumanker und keine ch/sh-Präferenz", "TOO_NARROW_NOW"),
        (5, "INDEPENDENT_WHOLE_WORDS", "jede Oberfläche ist ein separat gelerntes Wort", "orthographische Fusion ist häufig", "Raster, nackte Köpfe, Lesergrenzen und vorhergesagte Komposition werden unnötig teuer", "REJECTED_AS_PRIMARY"),
    )
    return [
        {"rank": rank, "model": model, "working_model_de": reading, "support": support, "counterevidence": counter, "disposition": disposition}
        for rank, model, reading, support, counter, disposition in values
    ]


def make_predictions(token_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    counts = Counter(row["eva"] for row in token_rows)
    values = (
        ("octheey", "o+cth+eey", "CTH-Zubereitung, Form II", "fehlende dritte O-Kopfstufe"),
        ("cheeecthy", "ch+eee+cth+y", "trockenes CTH-Material, erweiterte Bindungsstufe III", "Fortsetzung der äußeren E-Leiter"),
        ("sheeecthey", "sh+eee+cth+ey", "feuchtes CTH-Material, Form I, Bindungsstufe III", "Fortsetzung der äußeren E-Leiter"),
        ("cheeocthy", "ch+ee+o+cth+y", "trockene CTH-Zubereitung, Bindungsstufe II", "leere EE+O-Zelle"),
        ("sheeocthy", "sh+ee+o+cth+y", "feuchte CTH-Zubereitung, Bindungsstufe II", "leere EE+O-Zelle"),
        ("ctheeey", "cth+eeey", "CTH-Material, Form III", "Fortsetzung der inneren E-Leiter"),
    )
    return [
        {"prediction_id": f"G633-X{index:02d}", "surface": surface, "structural_parse": parse,
         "working_translation_de": reading, "prediction_basis_de": basis, "observed_allowed_tokens": counts[surface],
         "status": "PREDICTED_NOT_OBSERVED" if counts[surface] == 0 else "OBSERVED_UNEXPECTEDLY"}
        for index, (surface, parse, reading, basis) in enumerate(values, 1)
    ]


def make_dictionary(old: list[dict[str, str]]) -> tuple[list[dict[str, object]], int, int]:
    revisions = {
        "e nach ch/sh": ("ATTRIBUTIVE_E_BINDING", "bindet trocken/feucht attributiv an den folgenden Kopf; im deutschen Fließtext meist null", "ch|sh+e+KOPF"),
        "o+cth+R": ("PREPARED_CTH_HEAD", "Zubereitung/Ansatz aus CTH-Drogenmaterial; im Herbal Blatt-/Krautansatz", "o+[cth+Rest]"),
        "ch/sh+e?+[o?+cth+R]": ("CONCRETE_E_O_CTH_HIERARCHY", "trocken/feucht + attributive Bindung? + Zubereitung? + CTH-Material + Restform", "Qualitätskern+e?+[o?+cth+Rest]"),
        "che-": ("DRY_ATTRIBUTIVE_SHELL", "attributiv trocken", "ch+e"),
        "she-": ("MOIST_ATTRIBUTIVE_SHELL", "attributiv feucht", "sh+e"),
        "cho-": ("DRY_PREPARATION_SHELL", "trocken markierte Zubereitung", "ch+o"),
        "sho-": ("MOIST_PREPARATION_SHELL", "feucht markierte Zubereitung", "sh+o"),
        "cheo-": ("DRY_BOUND_PREPARATION_SHELL", "attributiv trocken markierte Zubereitung", "ch+e+o"),
        "sheo-": ("MOIST_BOUND_PREPARATION_SHELL", "attributiv feucht markierte Zubereitung", "sh+e+o"),
        "checthy": ("DRY_BOUND_CTH_MATERIAL", "trockenes CTH-Drogenmaterial; im Herbal trockenes Blatt-/Krautgut", "ch+e+cth+y"),
        "shecthy": ("MOIST_BOUND_CTH_MATERIAL", "feuchtes CTH-Drogenmaterial; im Herbal feuchtes Blatt-/Krautgut", "sh+e+cth+y"),
        "chocthy": ("DRY_CTH_PREPARATION", "trockene CTH-Drogenzubereitung; im Herbal trockene Blatt-/Krautzubereitung", "ch+o+cth+y"),
        "shocthy": ("MOIST_CTH_PREPARATION", "feuchte CTH-Drogenzubereitung; im Herbal feuchte Blatt-/Krautzubereitung", "sh+o+cth+y"),
        "cheocthy": ("DRY_BOUND_CTH_PREPARATION", "attributiv trockene CTH-Drogenzubereitung", "ch+e+o+cth+y"),
        "sheocthy": ("MOIST_BOUND_CTH_PREPARATION", "attributiv feuchte CTH-Drogenzubereitung", "sh+e+o+cth+y"),
    }
    rows: list[dict[str, object]] = []
    revised = 0
    for source in old:
        row: dict[str, object] = dict(source)
        if source["entry"] in revisions:
            kind, meaning, composition = revisions[source["entry"]]
            row.update({
                "kind": kind, "working_meaning_de": meaning, "composition": composition,
                "context_rule": "konkreter GDT633-Default; e=Bindung und o=Zubereitung bleiben ersetzbar, falls ein besserer Sachkontrast erscheint",
                "status": "REVISED_V10_CONCRETE_DEFAULT",
            })
            revised += 1
        rows.append(row)
    additions = (
        ("ee nach ch/sh", "EXTENDED_ATTRIBUTIVE_E_BINDING", "erweiterte/zweite attributive Bindungsstufe", "ch|sh+ee+KOPF", "nur zwei CTH-Belege; Grad-/Intensitätsrival sichtbar"),
        ("cth+y", "CTH_BASE_FORM", "CTH-Drogenmaterial, Grundform", "cth+y", "Herbal konkretisiert zu Blatt-/Krautgut"),
        ("cth+ey", "CTH_FORM_I", "CTH-Drogenmaterial, Form I", "cth+ey", "Flexionsrival sichtbar"),
        ("cth+eey", "CTH_FORM_II", "CTH-Drogenmaterial, Form II", "cth+eey", "Flexionsrival sichtbar"),
        ("octhy", "CTH_PREPARATION_BASE", "CTH-Zubereitung/Ansatz, Grundform", "o+cth+y", "im Herbal Blatt-/Krautansatz"),
        ("octhey", "CTH_PREPARATION_FORM_I", "CTH-Zubereitung/Ansatz, Form I", "o+cth+ey", "Flexionsrival sichtbar"),
        ("octheey", "CTH_PREPARATION_FORM_II", "CTH-Zubereitung/Ansatz, Form II", "o+cth+eey", "VORHERSAGE, nicht beobachtet"),
        ("cheecthy", "DRY_EXTENDED_BOUND_CTH", "trockenes Blatt-/Krautgut mit erweiterter Bindungsstufe II", "ch+ee+cth+y", "f29r.1 dreifach stabil"),
        ("sheecthey", "MOIST_EXTENDED_BOUND_CTH_FORM_I", "feuchtes CTH-Drogenmaterial, Form I, mit erweiterter Bindungsstufe II", "sh+ee+cth+ey", "f82v.36 dreifach stabil"),
    )
    for entry, kind, meaning, composition, rule in additions:
        rows.append({
            "entry": entry, "kind": kind, "working_meaning_de": meaning, "composition": composition,
            "context_rule": rule, "status": "NEW_V10_CONCRETE_DEFAULT" if entry != "octheey" else "NEW_V10_PREDICTED_ENTRY",
        })
    return rows, revised, len(additions)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G632_ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    token_rows, token_stats = g632.g631.guarded_query(TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand")
    cross_rows, cross_stats = g632.g631.guarded_query(CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, line_text = g632.g631.line_maps([dict(row) for row in token_rows])
    meta_by_locus = {row["locus"]: row for row in token_rows}

    outer = make_outer_occurrences(token_rows, cross_by_locus, by_line, line_text)
    outer_lattice = make_outer_lattice(outer)
    outer_ladders = make_outer_ladders(outer)
    ee_contexts = make_ee_contexts(outer, cross_by_locus)
    e_background = make_e_background(token_rows)
    inner = make_inner_occurrences(token_rows, cross_by_locus, by_line)
    inner_ladders, inner_pages, inner_contexts = make_inner_tables(inner)
    heads = make_head_rows(token_rows, by_line)
    o_distribution, o_same_remainder, o_shared = make_o_tables(heads)
    g632_occ = read_tsv(ROOT / G632_OCC_REL)
    g632_quality = read_tsv(ROOT / G632_QUALITY_REL)
    e_heating = make_heating_rows(g632_occ, g632_quality)
    controlled_pairs = make_controlled_pairs(outer)
    microeditions = make_microeditions(line_text)
    translations = make_translations(outer, read_tsv(ROOT / G632_SEPARATED_REL), read_tsv(ROOT / G632_BRIDGES_REL), meta_by_locus)
    atoms = make_atoms()
    scoreboard = make_scoreboard()
    predictions = make_predictions(token_rows)
    dictionary, revised_dictionary, added_dictionary = make_dictionary(read_tsv(ROOT / G632_DICT_REL))

    write_tsv(ROOT / OUTPUTS["allowlist"], [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(ROOT / OUTPUTS["outer_occurrences"], outer, (
        "occurrence_id", "page", "locus", "token_index", "surface", "quality_prefix", "outer_e_level", "o_slot", "remainder", "structural_parse",
        "triple_exact_token_stable", "triple_boundary_normalized", "left_surface", "right_surface", "position", "section", "language", "hand",
        "material_default_de", "outer_e_default_de", "inner_form_default_de", "working_translation_de", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["outer_lattice"], outer_lattice, (
        "outer_e_level", "o_slot", "occurrences", "types", "pages", "ch_occurrences", "sh_occurrences", "section_counts", "language_counts", "position_counts", "working_slot_de", "working_head_de",
    ))
    write_tsv(ROOT / OUTPUTS["outer_ladders"], outer_ladders, (
        "ladder_id", "quality_prefix", "o_slot", "remainder", "observed_e_levels", "distinct_levels", "e0_surface", "e0_occurrences", "e1_surface", "e1_occurrences", "e2_surface", "e2_occurrences", "working_contrast_de",
    ))
    write_tsv(ROOT / OUTPUTS["ee_contexts"], ee_contexts, (
        "ee_id", "page", "locus", "surface", "quality_prefix", "o_slot", "remainder", "e0_counterpart", "e0_occurrences", "e1_counterpart", "e1_occurrences",
        "triple_exact_token_stable", "position", "section", "language", "hand", "left_surface", "right_surface", "working_translation_de", "zl3b_line", "it2a_line", "rf1b_line",
    ))
    write_tsv(ROOT / OUTPUTS["e_background"], e_background, (
        "family_id", "skeleton", "e_lengths", "distinct_lengths", "surfaces_by_length", "occurrences_by_length", "types", "occurrences", "has_e_ee", "has_e_ee_eee", "has_e_through_eeee",
    ))
    write_tsv(ROOT / OUTPUTS["inner_ladders"], inner_ladders, (
        "head_prefix", "inner_e_level", "surface", "occurrences", "pages", "herbal_occurrences", "section_counts", "language_counts", "position_counts", "triple_exact_occurrences", "working_form_de", "observation_status",
    ))
    write_tsv(ROOT / OUTPUTS["inner_pages"], inner_pages, ("head_prefix", "page", "inner_e_levels", "distinct_levels", "occurrences", "surfaces", "loci"))
    write_tsv(ROOT / OUTPUTS["inner_contexts"], inner_contexts, ("context_id", "fixed_side", "fixed_neighbor", "inner_e_levels", "distinct_levels", "occurrences_by_level", "surfaces", "pages", "loci"))
    write_tsv(ROOT / OUTPUTS["o_distribution"], o_distribution, (
        "head_prefix", "occurrences", "types", "remainders", "pages", "herbal_occurrences", "section_counts", "language_counts", "position_counts", "working_head_de",
    ))
    write_tsv(ROOT / OUTPUTS["o_same_remainder"], o_same_remainder, (
        "context_id", "page", "locus", "o_surface", "remainder", "cth_counterpart", "cth_counterpart_occurrences", "cth_counterpart_pages", "same_page_counterpart", "left_surface", "right_surface", "position", "section", "language", "hand", "working_contrast_de",
    ))
    write_tsv(ROOT / OUTPUTS["o_shared_contexts"], o_shared, (
        "context_id", "remainder", "fixed_side", "fixed_neighbor", "cth_occurrences", "octh_occurrences", "cth_surfaces", "octh_surfaces", "pages", "loci",
    ))
    write_tsv(ROOT / OUTPUTS["e_heating"], e_heating, (
        "scope", "outer_e_slot", "o_slot", "interfix", "occurrences", "hot_occurrences", "cold_occurrences", "immediate_hot_occurrences", "immediate_cold_occurrences", "hot_share", "cold_share", "diagnosis_de",
    ))
    write_tsv(ROOT / OUTPUTS["controlled_pairs"], controlled_pairs, (
        "pair_id", "axis", "fixed_body", "left_surface", "right_surface", "left_occurrences", "right_occurrences", "working_contrast_de",
    ))
    write_tsv(ROOT / OUTPUTS["microeditions"], microeditions, (
        "case_id", "page", "locus", "surface_line", "target_span", "structural_parse", "working_translation_de", "residual_policy_de",
    ))
    write_tsv(ROOT / OUTPUTS["translations"], translations, (
        "translation_id", "source_kind", "source_id", "page", "locus", "surface_display", "normalized_surface", "quality_prefix", "outer_e_level", "o_slot", "remainder", "working_translation_de", "observation_status", "residual_policy_de",
    ))
    write_tsv(ROOT / OUTPUTS["atoms"], atoms, ("candidate_id", "visible_unit", "slot", "primary_default_de", "live_rival_de", "status"))
    write_tsv(ROOT / OUTPUTS["scoreboard"], scoreboard, ("rank", "model", "working_model_de", "support", "counterevidence", "disposition"))
    write_tsv(ROOT / OUTPUTS["predictions"], predictions, ("prediction_id", "surface", "structural_parse", "working_translation_de", "prediction_basis_de", "observed_allowed_tokens", "status"))
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status"))

    outer_counts = {(int(row["outer_e_level"]), int(row["o_slot"])): row for row in outer_lattice}
    head_counts = {str(row["head_prefix"]): row for row in o_distribution}
    heating_global = {(int(row["outer_e_slot"]), int(row["o_slot"])): row for row in e_heating if row["scope"] == "GLOBAL"}
    output_hashes = {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"}
    input_paths = (
        TOKENS_REL, CROSS_REL, G632_ALLOW_REL, G632_OCC_REL, G632_QUALITY_REL, G632_SEPARATED_REL,
        G632_BRIDGES_REL, G632_DICT_REL, G632_RUN_REL, G632_RESULT_REL, G624_RESULT_REL, G624_E_SERIES_REL,
    )
    result_core = {
        "schema": "GDT633_CTH_INTERFIX_SEMANTIC_CONTRASTS_RESULT_V1", "experiment_id": "GDT633",
        "status": "WORKING_E_ATTRIBUTIVE_O_PREPARATION_DEFAULTS__INNER_E_FORM_STAGES",
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "outer_e_o": {
            "occurrences": len(outer), "types": len({str(row["surface"]) for row in outer}), "pages": len({str(row["page"]) for row in outer}),
            "lattice": {f"E{e}_O{o}": {"occurrences": int(outer_counts[e, o]["occurrences"]), "types": int(outer_counts[e, o]["types"]), "pages": int(outer_counts[e, o]["pages"])} for e in range(3) for o in range(2)},
            "fixed_body_e_ladders": len(outer_ladders), "complete_e0_e1_e2_ladders": sum(row["observed_e_levels"] == "0|1|2" for row in outer_ladders),
            "ee_occurrences": len(ee_contexts), "ee_types": len({str(row["surface"]) for row in ee_contexts}),
            "controlled_pair_counts": dict(sorted(Counter(str(row["axis"]) for row in controlled_pairs).items())),
        },
        "literal_e_background": {
            "multi_length_families": len(e_background), "types": sum(int(row["types"]) for row in e_background), "occurrences": sum(int(row["occurrences"]) for row in e_background),
            "families_with_e_ee": sum(int(row["has_e_ee"]) for row in e_background), "families_with_e_ee_eee": sum(int(row["has_e_ee_eee"]) for row in e_background),
            "families_with_e_through_eeee": sum(int(row["has_e_through_eeee"]) for row in e_background),
        },
        "inner_e": {
            "counts": {str(row["surface"]): int(row["occurrences"]) for row in inner_ladders},
            "cth_pages_with_multiple_levels": sum(row["head_prefix"] == "CTH" for row in inner_pages),
            "cth_pages_with_all_three_levels": sum(row["head_prefix"] == "CTH" and row["inner_e_levels"] == "0|1|2" for row in inner_pages),
            "shared_one_sided_contexts": len(inner_contexts), "shared_contexts_all_three_levels": sum(row["inner_e_levels"] == "0|1|2" for row in inner_contexts),
            "octheey": "PREDICTED_NOT_OBSERVED",
        },
        "o_head": {
            "cth": {key: int(head_counts["CTH"][key]) for key in ("occurrences", "types", "pages", "herbal_occurrences")},
            "octh": {key: int(head_counts["O_CTH"][key]) for key in ("occurrences", "types", "pages", "herbal_occurrences")},
            "o_occurrences_with_cth_counterpart": sum(int(row["cth_counterpart_occurrences"]) > 0 for row in o_same_remainder),
            "o_types_with_cth_counterpart": len({str(row["o_surface"]) for row in o_same_remainder if int(row["cth_counterpart_occurrences"]) > 0}),
            "pages_with_same_remainder_both_heads": len({str(row["page"]) for row in o_same_remainder if int(row["same_page_counterpart"])}),
            "shared_one_sided_contexts": len(o_shared),
        },
        "e_heating_occurrence_normalized": {
            f"E{e}_O{o}": {key: int(heating_global[e, o][key]) for key in ("occurrences", "hot_occurrences", "cold_occurrences", "immediate_hot_occurrences", "immediate_cold_occurrences")}
            for e in range(2) for o in range(2)
        },
        "translations": {"expressions": len(translations), "normalized_types": len({str(row["normalized_surface"]) for row in translations}), "microeditions": len(microeditions), "unknown_neighbor_filler_added": 0},
        "working_semantics": {
            "ch": "dry/provisionally trocken", "sh": "moist/provisionally feucht",
            "outer_e": "attributive binding; silent in fluent German", "outer_ee": "extended/second binding stage",
            "o_cth": "preparation or batch made from CTH material", "cth": "drug material; Herbal leaf/herb material",
            "inner_y_ey_eey": "base form / form I / form II",
            "heating_rival": "WEAK_COLD_EXCLUSION_RIVAL__NOT_HOT_ENRICHED_AFTER_OCCURRENCE_NORMALIZATION",
            "specific_medium": "NOT_LICENSED",
        },
        "working_dictionary": {"entries": len(dictionary), "inherited_v9_entries": len(dictionary) - added_dictionary, "revised_v9_entries": revised_dictionary, "new_v10_entries": added_dictionary},
        "predictions": {"rows": len(predictions), "observed_allowed": sum(int(row["observed_allowed_tokens"]) for row in predictions), "primary": "octheey"},
        "claim_boundary": "GDT633 gives every observed expression in the extended ch/sh plus outer e/ee plus optional o plus CTH panel a concrete working reading: ch/sh remain dry/moist, outer e is primarily attributive binding, outer ee an extended binding stage, o+CTH a preparation or batch derived from CTH drug material, and inner y/ey/eey base/form I/form II. The reading covers 257 fused occurrences and, with eleven boundary realizations, 268 expressions in 55 normalized types. Occurrence-normalized contacts do not show E as hotter than NONE; heating survives only as a weak cold-exclusion rival. CTH is narrowed to leaf/herb material only in Herbal, and no specific water, wine, oil, species, language, phonetics, operation or full plaintext is claimed. octheey is predicted and unobserved.",
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths}, "outputs": output_hashes,
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"GDT633 built: outer={len(outer)}/{len({str(row['surface']) for row in outer})} "
        f"ladders={len(outer_ladders)} ee={len(ee_contexts)} e_background={len(e_background)} "
        f"inner_contexts={len(inner_contexts)} o_shared={len(o_shared)} pairs={len(controlled_pairs)} "
        f"translations={len(translations)}/{len({str(row['normalized_surface']) for row in translations})} dictionary={len(dictionary)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
