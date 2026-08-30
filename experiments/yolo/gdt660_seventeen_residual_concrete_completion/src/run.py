#!/usr/bin/env python3
"""Build GDT660: concrete completion of the seventeen V36 residual surfaces."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
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
BASE_REL = Path("experiments/yolo/gdt660_seventeen_residual_concrete_completion")
ART = ROOT / BASE_REL / "artifacts"
G659 = Path("experiments/yolo/gdt659_naked_y_local_reference")
_spec = importlib.util.spec_from_file_location("gdt659_builder_for_gdt660", ROOT / G659 / "src/run.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load GDT659 builder")
g659 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g659)

TOKENS_REL = g659.TOKENS_REL
CROSS_REL = g659.CROSS_REL
STATUS = "PASS_566_TARGET_POSITIONS__V37"


def whole(surface: str, meaning: str, composition: str, rival: str) -> dict[str, str]:
    return {"surface": surface, "working_meaning_de": meaning, "composition": composition, "strongest_rival_de": rival}


# Central semantic edit point. These cards dispatch exact whitespace-delimited wholes only.
EXACT_WHOLE_SPECS = (
    whole("cholkar", "Trockengut: heiße Fraktion I", "CHOL_DRY_MATERIAL+KAR_HOT_FRACTION_I", "heiße Drogenfraktion I oder gelernte CHOLKAR-Ganzform"),
    whole("qodain", "Qualitätsgrad II", "QODA_QUALITY+MINIM_II", "Ansatzdosis II"),
    whole("lcho", "Trockenansatz aus Drogenholz", "L_WOOD+CHO_DRY_PREPARATION", "Drogenholzauszug oder gelernte LCHO-Ganzform"),
    whole("kchor", "Drogenportion, heiß-trocken", "K_HOT+CH_DRY+OR_PORTION", "heiß-trockener Drogenteil"),
    whole("okchan", "heiß-trockener Ansatz, Grad I", "O_PREP+K_HOT+CH_DRY+A_MINIM_I", "heiß-trockene Ansatzcharge I"),
    whole("opchar", "trockene Pulverfraktion I im Ansatz", "O_PREP+P_POWDER+CH_DRY+AR_FRACTION_I", "Ansatz aus trockenem Drogenteil I"),
    whole("ydy", "Wertfeldwechsel/-schluss", "Y_PLACEMENT+DY_VALUE_FIELD_BOUNDARY", "bloßer Trenner ohne Wertfeldfunktion"),
    whole("schokey", "heiß-trockener Samenansatz in der Gradmitte", "S_SEED+CHOKEY_HOT_DRY_PREP_MIDDLE", "Salzansatz oder gelernte SCHOKEY-Ganzform"),
    whole("solkchy", "Saatgut, heiß-trocken am Gradanfang", "SOL_SEED_MATERIAL+KCHY_HOT_DRY_START", "Salzmaterial, heiß-trocken am Gradanfang"),
    whole("yckhey", "Eintrags-/Bezugsform: Arzneikompositum in der Gradmitte", "Y_PLACEMENT+CKHEY_MEDIAL_COMPOSITE", "lokaler Verweis auf ein Arzneikompositum"),
    whole("lshcthy", "feuchtes CTH-Drogenholz", "L_WOOD+SHCTHY_MOIST_CTH_FORM", "feuchte Holzcharge oder gelernte LSHCTHY-Ganzform"),
    whole("ysheey", "Eintrags-/Bezugsform: feucht am Gradende", "Y_PLACEMENT+SHEEY_MOIST_GRADE_END", "lokaler Verweis auf feuchtes Material"),
    whole("cheeytal", "Rohstoffklasse I: trocken am Gradende, kalt am Gradanfang", "CHEEY_DRY_END+TAL_COLD_RAW_I_START", "zweigliedrige Qualitätsfolge ohne Rohstoffklasse"),
    whole("ochedar", "trockener Ansatz in der Gradmitte, abgemessene Fraktion I", "O_PREP+CHE_DRY_MIDDLE+DAR_MEASURED_FRACTION_I", "Ansatz aus abgemessener Trockenfraktion I"),
    whole("cheoty", "trocken angesetzte kalte Zubereitung am Gradanfang", "CHEO_DRY_PREP+T_COLD+Y_START", "kalter Trockenstoff am Gradanfang"),
)
EXACT_BY_SURFACE = {row["surface"]: row for row in EXACT_WHOLE_SPECS}
TARGET_SURFACES = frozenset((*EXACT_BY_SURFACE, "s", "dy"))

# Exactly seven S/DY position cards. S attachment remains an audit dimension.
S_DY_CONTEXT_SPECS = {
    "S_LABEL_SIGLUM": ("s", "token kind L; all observed cases are one-token labels", "NAKED_S|TOKEN_KIND=L|POSITION=ONLY|ROLE=LABEL_SIGLUM", "[Beschriftungszeichen]", "[Beschriftungszeichen]", "Sorten- oder Formzeichen ohne Stoffbezug"),
    "S_BOS": ("s", "P token at physical-line beginning", "NAKED_S|TOKEN_KIND=P|POSITION=BOS|ROLE=SEED_HEAD", "Samen-/Saatgutposten", "Samen-/Saatgutposten:", "Salzposten oder bloßer Rubrikkopf"),
    "S_MEDIAL": ("s", "P token inside a physical line; attachment audited separately", "NAKED_S|TOKEN_KIND=P|POSITION=MEDIAL|ROLE=SEED_POST", "Samen-/Saatgutposten", "Samen-/Saatgutposten", "links gebundene Species-/Drogenart"),
    "S_EOS": ("s", "P token at physical-line end", "NAKED_S|TOKEN_KIND=P|POSITION=EOS|ROLE=SEED_POST", "Samen-/Saatgutposten", "Samen-/Saatgutposten.", "links gebundene Species-/Drogenart"),
    "DY_BOS_CLOSE": ("dy", "token at physical-line beginning", "NAKED_DY|POSITION=BOS|ROLE=CLOSURE_NOTE", "voriges Qualitäts-/Wertfeld geschlossen", "voriges Qualitäts-/Wertfeld geschlossen:", "neuer Unterposten statt Rückschluss"),
    "DY_MEDIAL": ("dy", "token inside a physical line; left-bound status audited separately", "NAKED_DY|POSITION=MEDIAL|ROLE=LEFT_VALUE_FIELD_CLOSE", "Qualitäts-/Wertfeld geschlossen", ";", "eigenständige Arzneiform statt Feldschluss"),
    "DY_EOS": ("dy", "token at physical-line end", "NAKED_DY|POSITION=EOS|ROLE=VALUE_FIELD_CLOSE", "Qualitäts-/Wertfeld geschlossen", ".", "eigenständige Arzneiform statt Schlusszeichen"),
}
S_DY_CONTEXT_ORDER = tuple(S_DY_CONTEXT_SPECS)

EXPECTED_SURFACE_COUNTS = {
    "cholkar": 3, "qodain": 10, "lcho": 6, "kchor": 19, "okchan": 1, "opchar": 2,
    "ydy": 5, "schokey": 1, "s": 272, "dy": 229, "solkchy": 1, "yckhey": 2,
    "lshcthy": 1, "ysheey": 8, "cheeytal": 1, "ochedar": 1, "cheoty": 4,
}
EXPECTED_CONTEXT_COUNTS = {"S_LABEL_SIGLUM": 8, "S_BOS": 17, "S_MEDIAL": 214, "S_EOS": 33, "DY_BOS_CLOSE": 2, "DY_MEDIAL": 150, "DY_EOS": 77}

MATERIA_AMOUNT_FAMILIES = {
    "CHOLKAR_DRY_HOT_FRACTION": ("cholkar", "chol", "kar", "cholkaiin"),
    "QODAIN_QUALITY_II": ("qodain", "dain", "qodal", "qodaiin"),
    "LCHO_WOOD_DRY_PREP": ("lcho", "cho", "lcheo", "lchol"),
    "KCHOR_HOT_DRY_PORTION": ("kchor", "kor", "qotchor", "qokchor"),
    "OPCHAR_POWDER_FRACTION": ("opchar", "par", "opal", "pchar", "qopchar"),
    "SOLKCHY_SEED_MATERIAL": ("solkchy", "sol", "kchy"),
    "LSHCTHY_WOOD_MOIST_FORM": ("lshcthy", "shcthy", "lsheey"),
    "OCHEDAR_MEASURED_DRY_FRACTION": ("ochedar", "dar", "chedar", "odal"),
}
QUALITY_PREPARATION_FAMILIES = {
    "OKCHAN_HOT_DRY_GRADE_I": ("okchan", "chan", "okchy", "okchey"),
    "SCHOKEY_SEED_DRY_PREP": ("schokey", "chokey", "schos"),
    "CHEEYTAL_DUAL_QUALITY": ("cheeytal", "cheey", "tal", "chekal"),
    "CHEOTY_COLD_DRY_START": ("cheoty", "cheoky", "otcho"),
}
Y_PREFIX_FAMILIES = {"YDY_VALUE_BOUNDARY": ("ydy", "dy"), "YSHEEY_MOIST_END": ("ysheey", "sheey"), "YCKHEY_COMPOSITE": ("yckhey", "ckhey")}

GENERIC_FILLER = re.compile(r"arbeitsgut|arbeitsvorgang|arbeitschritt|arbeitsschritt", re.IGNORECASE)
OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv", "S_DY_CONTEXT_CENSUS.tsv",
    "S_DY_CONTEXT_CARDS.tsv", "S_DY_CONTEXT_SUMMARY.tsv", "MATERIA_AMOUNT_FAMILY_ATLAS.tsv",
    "QUALITY_PREPARATION_FAMILY_ATLAS.tsv", "Y_PREFIX_PLACEMENT_ATLAS.tsv", "TARGET_LINE_TRANSLATIONS.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V37_WORKING_TOKEN_GLOSSARY.tsv", "WORKING_DICTIONARY_V37.tsv", "ALL_LINE_CONCRETE_COVERAGE_V37.tsv",
    "COMPLETE_PASSAGES_V37.tsv", "ONE_UNKNOWN_PASSAGES_V37.tsv",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    return g659.read_tsv(path)


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    g659.write_tsv(path, rows, fields)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def split_pipe(value: object) -> list[str]:
    return str(value).split(" | ") if str(value) else []


def parse_compact_pipe(value: object) -> list[str]:
    return [] if str(value) in {"", "NONE"} else str(value).split("|")


def position_label(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "BOS"
    if ordinal == length:
        return "EOS"
    return "MEDIAL"


def concatenated_span_count(words: list[str], target: str) -> int:
    count = 0
    for start in range(len(words)):
        joined = ""
        for end in range(start, len(words)):
            joined += words[end]
            if joined == target:
                count += 1
                break
            if len(joined) >= len(target) or not target.startswith(joined):
                break
    return count


def stable_maps(token_rows: list[dict[str, str]], cross_by_locus: dict[str, dict[str, str]]) -> tuple[dict[tuple[str, int], int], dict[tuple[str, int], int]]:
    ordinals: Counter[tuple[str, str]] = Counter()
    exact: dict[tuple[str, int], int] = {}
    normalized: dict[tuple[str, int], int] = {}
    for row in sorted(token_rows, key=lambda item: (item["page"], item["locus"], int(item["token_index"]))):
        locus, surface = row["locus"], row["eva"]
        ordinals[locus, surface] += 1
        cross = cross_by_locus[locus]
        exact_caps = [cross[field].split().count(surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        norm_caps = [concatenated_span_count(cross[field].split(), surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        key = (locus, int(row["token_index"]))
        exact[key] = int(ordinals[locus, surface] <= min(exact_caps))
        normalized[key] = int(ordinals[locus, surface] <= min(norm_caps))
    return exact, normalized


def context_class(surface: str, position: str, kind: str) -> str:
    if surface == "s":
        if kind == "L":
            return "S_LABEL_SIGLUM"
        return {"BOS": "S_BOS", "MEDIAL": "S_MEDIAL", "EOS": "S_EOS"}[position]
    if surface == "dy":
        return {"BOS": "DY_BOS_CLOSE", "MEDIAL": "DY_MEDIAL", "EOS": "DY_EOS"}[position]
    return "EXACT_WHOLE"


def card_value(klass: str, index: int) -> str:
    return S_DY_CONTEXT_SPECS[klass][index]


def s_attachment_class(position: str, left_count: int, right_count: int, kind: str) -> str:
    if kind == "L":
        return "LABEL_SIGLUM"
    if position == "BOS":
        return "RIGHT_SEED_HEAD"
    if position == "EOS":
        return "LEFT_OR_SPECIES_RIVAL"
    if left_count and right_count:
        return "BIDIRECTIONAL"
    if left_count:
        return "LEFT_ATTACHED"
    if right_count:
        return "RIGHT_HEAD"
    return "UNRESOLVED_EXPLICIT_SEED_DEFAULT"


def occurrence_gloss(surface: str, position: str, kind: str) -> str:
    if surface in {"s", "dy"}:
        return card_value(context_class(surface, position, kind), 3)
    if surface == "ydy":
        return "nächstes Wertfeld:" if position == "MEDIAL" else "Wertfeld abgeschlossen"
    if surface == "ysheey":
        return "Eintrag: feucht am Gradende" if position == "BOS" else "hierzu: feucht am Gradende"
    if surface == "yckhey":
        return "Eintrag: Arzneikompositum in der Gradmitte" if position == "BOS" else "Arzneikompositum in der Gradmitte"
    return EXACT_BY_SURFACE[surface]["working_meaning_de"]


def occurrence_render(surface: str, position: str, kind: str) -> str:
    if surface in {"s", "dy"}:
        return card_value(context_class(surface, position, kind), 4)
    if surface == "ydy":
        return "nächstes Wertfeld:" if position == "MEDIAL" else "."
    return occurrence_gloss(surface, position, kind)


def occurrence_rival(surface: str, position: str, kind: str) -> str:
    if surface in {"s", "dy"}:
        return card_value(context_class(surface, position, kind), 5)
    return EXACT_BY_SURFACE[surface]["strongest_rival_de"]


def practical_line_translation(
    locus: str,
    line: list[dict[str, str]],
    glosses: list[str],
    y_occurrence_by_token: dict[tuple[str, int], dict[str, object]],
    target_occurrence_by_token: dict[tuple[str, int], dict[str, object]],
) -> str:
    if locus == "f80v.21":
        return g659.F80V21_TRANSLATION_DE
    rendered: list[str] = []
    terminal_close = False
    index = 0
    while index < len(line):
        token = line[index]
        surface = token["eva"]
        key = (locus, int(token["token_index"]))
        if surface == "y":
            occurrence = y_occurrence_by_token[key]
            klass = str(occurrence["context_class"])
            if klass == "Y_LABEL_SIGLUM":
                if occurrence["label_subrole"] == "LABEL_ONLY":
                    rendered.append("[Beschriftungszeichen]")
                terminal_close = terminal_close or occurrence["label_subrole"] == "LABEL_CLOSE"
                index += 1
                continue
            if klass == "Y_BOS_ENTRY" and index + 1 < len(line):
                rendered.append(f"Eintrag: {glosses[index + 1]}")
                index += 2
                continue
            if klass == "Y_EOS_CLOSE":
                terminal_close = True
                index += 1
                continue
            if klass == "Y_MEDIAL_LEFT_CLOSE":
                index += 1
                continue
            if index + 1 < len(line):
                right_token = line[index + 1]
                right_surface = right_token["eva"]
                right_meaning = g659.natural_right_meaning(locus, right_surface, glosses[index + 1])
                rendered.append(f"hierzu: {right_meaning}")
                right_target = target_occurrence_by_token.get((locus, int(right_token["token_index"])))
                if right_target is not None and right_surface == "dy" and right_target["position"] == "EOS":
                    terminal_close = True
                index += 2
                continue
            rendered.append(glosses[index])
            index += 1
            continue
        if key not in target_occurrence_by_token:
            rendered.append(glosses[index])
            index += 1
            continue
        occurrence = target_occurrence_by_token[key]
        position = str(occurrence["position"])
        if surface == "s":
            if token["kind"] == "L":
                rendered.append("[Beschriftungszeichen]")
            elif position == "BOS":
                rendered.append("Samen-/Saatgutposten:")
            else:
                rendered.append("Samen-/Saatgutposten")
                terminal_close = terminal_close or position == "EOS"
            index += 1
            continue
        if surface == "dy":
            if position == "BOS":
                rendered.append("voriges Qualitäts-/Wertfeld geschlossen:")
            elif position == "EOS":
                terminal_close = True
            index += 1
            continue
        if surface == "ydy":
            if position == "EOS":
                terminal_close = True
                index += 1
                continue
            if index + 1 < len(line):
                rendered.append(f"nächstes Wertfeld: {glosses[index + 1]}")
                index += 2
                continue
        rendered.append(glosses[index])
        index += 1
    practical = "; ".join(item for item in rendered if item)
    if terminal_close and practical:
        practical = practical.rstrip("; .") + "."
    return practical


def metrics(coverage, one_unknown, complete, glossary) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "working_glossary_surfaces": len(glossary),
    }


def family_atlas(families, surface_counts, surface_pages, exact, normalized, tokens_by_surface, base_glossary) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for family, surfaces in families.items():
        for role_index, surface in enumerate(surfaces):
            members = tokens_by_surface.get(surface, [])
            rows.append({
                "family": family, "role": "TARGET" if role_index == 0 else "VISIBLE_ANCHOR",
                "surface": surface, "occurrences": surface_counts[surface],
                "lines": len({row["locus"] for row in members}), "pages": len(surface_pages.get(surface, set())),
                "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
                "split_normalized_occurrences": sum(normalized[row["locus"], int(row["token_index"])] for row in members),
                "v36_meaning_de": base_glossary.get(surface, {}).get("working_meaning_de", "OPEN"),
                "v36_source": base_glossary.get(surface, {}).get("source", "OPEN"),
                "gdt660_default_de": EXACT_BY_SURFACE.get(surface, {}).get("working_meaning_de", "ANCHOR_ONLY"),
                "claim_scope": "exact observed surface; structural comparison only; no glyph identity or substring export",
            })
    return rows


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G659 / "artifacts/PAGE_ALLOWLIST.tsv")}
    if len(pages) != 179 or "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("inherited page allow-list is not the exact safe 179-page panel")
    tokens, token_stats = g659.guarded_query(TOKENS_REL, pages, "page,locus,token_index,eva,kind,section,language,hand")
    cross, cross_stats = g659.guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean"
    )
    if (len(tokens), len(cross)) != (32339, 4137):
        raise RuntimeError("guarded source census drift")
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    tokens_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
        tokens_by_surface[row["eva"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda row: int(row["token_index"]))
    cross_by_locus = {row["locus"]: row for row in cross}
    if len(by_line) != 4128:
        raise RuntimeError("ZL physical-line count drift")
    for locus, line in by_line.items():
        if locus not in cross_by_locus or " ".join(row["eva"] for row in line) != cross_by_locus[locus]["zl3b_clean"]:
            raise RuntimeError(f"guarded token/cross line mismatch: {locus}")

    base_dictionary = read_tsv(ROOT / G659 / "artifacts/WORKING_DICTIONARY_V36.tsv")
    base_glossary_rows = read_tsv(ROOT / G659 / "artifacts/V36_WORKING_TOKEN_GLOSSARY.tsv")
    base_coverage = read_tsv(ROOT / G659 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V36.tsv")
    base_complete = read_tsv(ROOT / G659 / "artifacts/COMPLETE_PASSAGES_V36.tsv")
    base_one = read_tsv(ROOT / G659 / "artifacts/ONE_UNKNOWN_PASSAGES_V36.tsv")
    y_occurrences = read_tsv(ROOT / G659 / "artifacts/Y_OCCURRENCE_CENSUS.tsv")
    if (len(base_dictionary), len(base_glossary_rows), len(base_coverage), len(base_complete), len(base_one), len(y_occurrences)) != (582, 495, 4128, 146, 249, 270):
        raise RuntimeError("V36 base dimensions drift")
    base_glossary = {row["surface"]: row for row in base_glossary_rows}
    if any(surface in base_glossary for surface in TARGET_SURFACES):
        raise RuntimeError("a GDT660 residual unexpectedly already has a V36 glossary row")
    y_occurrence_by_token = {(row["locus"], int(row["token_index"])): row for row in y_occurrences}
    surface_counts = Counter(row["eva"] for row in tokens)
    observed_counts = {surface: surface_counts[surface] for surface in EXPECTED_SURFACE_COUNTS}
    if observed_counts != EXPECTED_SURFACE_COUNTS:
        raise RuntimeError(f"target surface count drift: {observed_counts!r}")
    surface_pages: dict[str, set[str]] = defaultdict(set)
    for row in tokens:
        surface_pages[row["eva"]].add(row["page"])
    exact, normalized = stable_maps(tokens, cross_by_locus)

    occurrence_rows: list[dict[str, object]] = []
    target_occurrence_by_token: dict[tuple[str, int], dict[str, object]] = {}
    context_counts: Counter[str] = Counter()
    placement_counts: Counter[str] = Counter()
    for locus in sorted(by_line):
        line = by_line[locus]
        words = [row["eva"] for row in line]
        for index, token in enumerate(line):
            surface = token["eva"]
            if surface not in TARGET_SURFACES:
                continue
            ordinal = index + 1
            position = position_label(ordinal, len(line))
            left = words[index - 1] if index else "<BOS>"
            right = words[index + 1] if index + 1 < len(line) else "<EOS>"
            left_fused = left + surface if index else ""
            right_fused = surface + right if index + 1 < len(line) else ""
            klass = context_class(surface, position, token["kind"])
            attachment = (
                s_attachment_class(position, surface_counts[left_fused], surface_counts[right_fused], token["kind"])
                if surface == "s" else
                ("LEFT_BOUND" if position == "MEDIAL" and surface_counts[left_fused] else position)
            )
            placement = (
                "YDY_MEDIAL_NEXT_VALUE" if surface == "ydy" and position == "MEDIAL" else
                "YDY_EOS_CLOSE" if surface == "ydy" else
                "YSHEEY_BOS_ENTRY" if surface == "ysheey" and position == "BOS" else
                "YSHEEY_MEDIAL_REFERENCE" if surface == "ysheey" else
                "YCKHEY_BOS_ENTRY" if surface == "yckhey" and position == "BOS" else
                "YCKHEY_EOS_FORM" if surface == "yckhey" else "NONE"
            )
            key = (locus, int(token["token_index"]))
            row: dict[str, object] = {
                "occurrence_id": f"G660-T{len(occurrence_rows) + 1:03d}",
                "page": token["page"], "locus": locus, "token_index": token["token_index"],
                "ordinal": ordinal, "line_length": len(line), "surface": surface,
                "token_kind": token["kind"], "position": position,
                "section": token["section"], "language": token["language"], "hand": token["hand"],
                "scope_mode": "CONTEXT_SCOPED" if surface in {"s", "dy"} else "EXACT_WHOLE",
                "context_class": klass, "placement_class": placement, "attachment_class": attachment,
                "left_surface": left, "right_surface": right,
                "left_fused_surface": left_fused or "NONE", "left_fused_occurrences": surface_counts[left_fused],
                "right_fused_surface": right_fused or "NONE", "right_fused_occurrences": surface_counts[right_fused],
                "working_gloss_de": occurrence_gloss(surface, position, token["kind"]),
                "working_render_de": occurrence_render(surface, position, token["kind"]),
                "strongest_rival_de": occurrence_rival(surface, position, token["kind"]),
                "reader_exact": exact[key], "split_normalized": normalized[key],
                "all_three_present": cross_by_locus[locus]["all_three_present"],
                "all_present_exact": cross_by_locus[locus]["all_present_exact"],
                "zl3b_line": cross_by_locus[locus]["zl3b_clean"],
                "it2a_line": cross_by_locus[locus]["it2a_clean"],
                "rf1b_line": cross_by_locus[locus]["rf1b_clean"],
            }
            occurrence_rows.append(row)
            target_occurrence_by_token[key] = row
            if klass != "EXACT_WHOLE":
                context_counts[klass] += 1
            if placement != "NONE":
                placement_counts[placement] += 1
    if len(occurrence_rows) != 566 or len(target_occurrence_by_token) != 566:
        raise RuntimeError("target occurrence census drift")
    if len({row["locus"] for row in occurrence_rows}) != 510 or len({row["page"] for row in occurrence_rows}) != 169:
        raise RuntimeError("target line/page census drift")
    if dict(context_counts) != EXPECTED_CONTEXT_COUNTS:
        raise RuntimeError(f"S/DY context count drift: {dict(context_counts)!r}")
    if sum(int(row["reader_exact"]) for row in occurrence_rows) != 357 or sum(int(row["split_normalized"]) for row in occurrence_rows) != 360:
        raise RuntimeError("target reader capacity drift")
    if Counter(row["token_kind"] for row in occurrence_rows if row["surface"] == "s") != {"P": 264, "L": 8}:
        raise RuntimeError("naked-s token-kind drift")
    if any(row["position"] != "ONLY" for row in occurrence_rows if row["context_class"] == "S_LABEL_SIGLUM"):
        raise RuntimeError("S label-siglum scope drift")
    expected_placements = {"YSHEEY_BOS_ENTRY": 7, "YSHEEY_MEDIAL_REFERENCE": 1, "YDY_MEDIAL_NEXT_VALUE": 3, "YDY_EOS_CLOSE": 2, "YCKHEY_BOS_ENTRY": 1, "YCKHEY_EOS_FORM": 1}
    if dict(placement_counts) != expected_placements:
        raise RuntimeError(f"Y-prefix placement drift: {dict(placement_counts)!r}")

    base_coverage_by_locus = {row["locus"]: row for row in base_coverage}
    coverage_rows: list[dict[str, object]] = []
    non_target_before: list[tuple[object, ...]] = []
    non_target_after: list[tuple[object, ...]] = []
    affected_loci: set[str] = set()
    for base_row in base_coverage:
        locus = base_row["locus"]
        line = by_line[locus]
        glosses = split_pipe(base_row["token_glosses_de"])
        sources = split_pipe(base_row["gloss_sources"])
        states = split_pipe(base_row["scope_states"])
        if not (len(line) == len(glosses) == len(sources) == len(states)):
            raise RuntimeError(f"V36 coverage token columns misalign: {locus}")
        unknown_pairs = list(zip(parse_compact_pipe(base_row["unknown_ordinals"]), parse_compact_pipe(base_row["unknown_surfaces"])))
        target_ordinals: set[str] = set()
        for index, token in enumerate(line):
            key = (locus, int(token["token_index"]))
            if key not in target_occurrence_by_token:
                non_target_before.append((locus, index + 1, token["eva"], glosses[index], sources[index], states[index]))
                continue
            occurrence = target_occurrence_by_token[key]
            surface = token["eva"]
            if glosses[index] != f"[{surface}:?]" or sources[index] != "OPEN" or states[index] != "UNKNOWN_SURFACE":
                raise RuntimeError(f"V36 target is not an exact open surface at {locus}.{index + 1}: {surface}")
            glosses[index] = str(occurrence["working_gloss_de"])
            if surface in {"s", "dy"}:
                sources[index] = "GDT660:" + str(occurrence["context_class"])
                states[index] = "KNOWN_CONTEXT_LICENSED" if int(occurrence["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
            else:
                sources[index] = f"GDT660:EXACT_WHOLE:{surface}"
                states[index] = "KNOWN_EXACT_WHOLE" if int(occurrence["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
            target_ordinals.add(str(index + 1))
            affected_loci.add(locus)
        for index, token in enumerate(line):
            key = (locus, int(token["token_index"]))
            if key not in target_occurrence_by_token:
                non_target_after.append((locus, index + 1, token["eva"], glosses[index], sources[index], states[index]))
        unknown_pairs = [pair for pair in unknown_pairs if pair[0] not in target_ordinals]
        row: dict[str, object] = dict(base_row)
        row["known_tokens"] = int(base_row["known_tokens"]) + len(target_ordinals)
        row["context_licensed_tokens"] = states.count("KNOWN_CONTEXT_LICENSED")
        row["ambiguous_tokens"] = states.count("AMBIGUOUS_ACTIVE_RIVAL")
        row["reader_unstable_tokens"] = states.count("READER_BOUNDARY_UNSTABLE")
        row["unknown_tokens"] = len(unknown_pairs)
        row["coverage_fraction"] = f"{int(row['known_tokens']) / int(row['token_count']):.6f}"
        row["token_glosses_de"] = " | ".join(glosses)
        row["gloss_sources"] = " | ".join(sources)
        row["scope_states"] = " | ".join(states)
        row["unknown_ordinals"] = "|".join(pair[0] for pair in unknown_pairs) or "NONE"
        row["unknown_surfaces"] = "|".join(pair[1] for pair in unknown_pairs) or "NONE"
        if int(base_row["unknown_tokens"]) - len(target_ordinals) != len(unknown_pairs):
            raise RuntimeError(f"V36→V37 unknown-token arithmetic drift: {locus}")
        coverage_rows.append(row)
    if len(affected_loci) != 510 or len(non_target_before) != 31773 or non_target_before != non_target_after:
        raise RuntimeError("non-target preservation or affected-line count drift")
    non_target_before_sha = canonical_hash(non_target_before)
    non_target_after_sha = canonical_hash(non_target_after)
    coverage_by_locus = {str(row["locus"]): row for row in coverage_rows}

    complete_rows: list[dict[str, object]] = []
    for row in coverage_rows:
        if int(row["unknown_tokens"]) or int(row["token_count"]) < 2:
            continue
        complete = dict(row)
        complete["strict_complete"] = int(int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0 and int(row["all_present_exact"]) == 1)
        complete["working_translation_de"] = practical_line_translation(
            str(row["locus"]), by_line[str(row["locus"])], split_pipe(row["token_glosses_de"]),
            y_occurrence_by_token, target_occurrence_by_token,
        )
        complete_rows.append(complete)
    complete_rows.sort(key=lambda row: (-int(row["strict_complete"]), -int(row["token_count"]), str(row["locus"])))
    for rank, row in enumerate(complete_rows, 1):
        row["rank"] = rank

    base_one_by_locus = {row["locus"]: row for row in base_one}
    one_rows: list[dict[str, object]] = []
    for row in coverage_rows:
        if int(row["unknown_tokens"]) != 1 or int(row["known_tokens"]) < 1:
            continue
        ordinal = int(str(row["unknown_ordinals"]))
        surface = str(row["unknown_surfaces"])
        previous_card = base_one_by_locus.get(str(row["locus"]))
        if previous_card and previous_card["unknown_surface"] == surface and int(previous_card["unknown_ordinal"]) == ordinal:
            proposal = previous_card["proposed_default_de"]
            basis = previous_card["proposal_basis"]
            strength = previous_card["proposal_strength"]
        else:
            proposal = f"[{surface}:?]"
            basis = "NEWLY_EXPOSED_BY_GDT660_NO_NEW_CARD"
            strength = "OPEN"
        strict = int(int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0 and int(row["all_present_exact"]) == 1)
        strength_rank = {"HIGH": 4, "MEDIUM": 3, "LOW": 2, "OPEN": 1}[strength]
        score = int(row["known_tokens"]) * 1_000_000 + strength_rank * 100_000 + strict * 10_000 - int(row["token_count"]) * 100
        line = by_line[str(row["locus"])]
        proposed_glosses = split_pipe(row["token_glosses_de"])
        proposed_glosses[ordinal - 1] = proposal
        one_rows.append({
            "rank": 0, "score": score, "strict_eligible": strict, **row,
            "unknown_ordinal": ordinal, "unknown_surface": surface,
            "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
            "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
            "proposed_default_de": proposal, "proposal_basis": basis, "proposal_strength": strength,
            "proposed_complete_translation_de": practical_line_translation(
                str(row["locus"]), line, proposed_glosses, y_occurrence_by_token, target_occurrence_by_token
            ),
        })
    one_rows.sort(key=lambda row: (-int(row["score"]), str(row["locus"])))
    for rank, row in enumerate(one_rows, 1):
        row["rank"] = rank

    glossary_rows: list[dict[str, object]] = [dict(row) for row in base_glossary_rows]
    for spec_row in EXACT_WHOLE_SPECS:
        glossary_rows.append({
            "surface": spec_row["surface"], "working_meaning_de": spec_row["working_meaning_de"],
            "source": "GDT660:EXACT_WHOLE", "strength": "PROVISIONAL_CONCRETE_EXACT_WHOLE",
            "scope_state": "KNOWN_EXACT_WHOLE", "priority": 210,
        })
    glossary_rows.sort(key=lambda row: str(row["surface"]))
    if len(glossary_rows) != 510 or any(row["surface"] in {"s", "dy"} for row in glossary_rows):
        raise RuntimeError("V37 glossary count or naked s/dy exclusion drift")

    dictionary_rows: list[dict[str, object]] = [dict(row) for row in base_dictionary]
    for spec_row in EXACT_WHOLE_SPECS:
        dictionary_rows.append({
            "entry": f"{spec_row['surface']}@GDT660_EXACT_WHOLE", "kind": "EXACT_WHOLE_SURFACE_CARD",
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "context_rule": "only the exact whitespace-delimited surface; no substring inheritance",
            "status": "NEW_V37_PROVISIONAL_CONCRETE_EXACT_WHOLE",
        })
    for klass in S_DY_CONTEXT_ORDER:
        dictionary_rows.append({
            "entry": f"{card_value(klass, 0)}@{klass}", "kind": "OCCURRENCE_SCOPED_CONTEXT_CARD",
            "working_meaning_de": card_value(klass, 4), "composition": card_value(klass, 2),
            "context_rule": card_value(klass, 1), "status": "NEW_V37_CONTEXT_CARD_NOT_GLOBAL_LEXEME",
        })
    for klass, render, rule in (
        ("YDY_MEDIAL_NEXT_VALUE", "nächstes Wertfeld:", "ydy at a medial physical-line position"),
        ("YDY_EOS_CLOSE", ".", "ydy at physical-line end"),
    ):
        dictionary_rows.append({
            "entry": f"ydy@{klass}", "kind": "EXACT_WHOLE_PLACEMENT_CARD",
            "working_meaning_de": render, "composition": "YDY_VALUE_FIELD_BOUNDARY",
            "context_rule": rule, "status": "NEW_V37_POSITIONAL_RENDER_OF_EXACT_WHOLE",
        })
    if len(dictionary_rows) != 606 or any(row["entry"] in {"s", "dy"} for row in dictionary_rows):
        raise RuntimeError("V37 dictionary count or global naked-s/dy entry drift")

    base_complete_loci = {row["locus"] for row in base_complete}
    newly_completed = [dict(row) for row in complete_rows if row["locus"] not in base_complete_loci]
    newly_completed.sort(key=lambda row: str(row["locus"]))
    for rank, row in enumerate(newly_completed, 1):
        row["rank"] = rank
    base_one_loci = {row["locus"] for row in base_one}
    newly_one = [dict(row) for row in one_rows if row["locus"] not in base_one_loci]
    newly_one.sort(key=lambda row: str(row["locus"]))
    for rank, row in enumerate(newly_one, 1):
        row["rank"] = rank
        row["base_unknown_tokens"] = base_coverage_by_locus[str(row["locus"])]["unknown_tokens"]

    audit_rows: list[dict[str, object]] = []
    reader_rows: list[dict[str, object]] = []
    for occurrence in occurrence_rows:
        locus = str(occurrence["locus"])
        ordinal = int(occurrence["ordinal"])
        base_row = base_coverage_by_locus[locus]
        final_row = coverage_by_locus[locus]
        final_translation = practical_line_translation(
            locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
            y_occurrence_by_token, target_occurrence_by_token,
        )
        audit_rows.append({
            **occurrence,
            "v36_gloss_de": split_pipe(base_row["token_glosses_de"])[ordinal - 1],
            "v37_gloss_de": split_pipe(final_row["token_glosses_de"])[ordinal - 1],
            "v36_scope_state": split_pipe(base_row["scope_states"])[ordinal - 1],
            "v37_scope_state": split_pipe(final_row["scope_states"])[ordinal - 1],
            "v36_token_glosses_de": base_row["token_glosses_de"],
            "v37_token_glosses_de": final_row["token_glosses_de"],
            "v37_working_translation_de": final_translation,
            "exact_surface_dispatch": int(str(occurrence["surface"]) in EXACT_BY_SURFACE),
            "substring_dispatch": 0,
        })
        reader_rows.append({
            "occurrence_id": occurrence["occurrence_id"], "page": occurrence["page"], "locus": locus,
            "ordinal": ordinal, "surface": occurrence["surface"], "position": occurrence["position"],
            "reader_exact": occurrence["reader_exact"], "split_normalized": occurrence["split_normalized"],
            "all_present_exact": occurrence["all_present_exact"], "zl3b_line": occurrence["zl3b_line"],
            "it2a_line": occurrence["it2a_line"], "rf1b_line": occurrence["rf1b_line"],
            "semantic_scope": occurrence["scope_mode"],
            "claim_boundary": "reader agreement conditions confidence only; it does not identify glyphs or plaintext",
        })
    if any(
        str(row["v36_gloss_de"]) != f"[{row['surface']}:?]"
        or str(row["v37_gloss_de"]).endswith(":?]")
        for row in audit_rows
    ):
        raise RuntimeError("not every target position changed from open to concrete")
    if any(GENERIC_FILLER.search(str(row["v37_gloss_de"])) for row in audit_rows):
        raise RuntimeError("generic work filler leaked into a concrete target default")

    decision_rows: list[dict[str, object]] = []
    for surface in EXPECTED_SURFACE_COUNTS:
        members = [row for row in occurrence_rows if row["surface"] == surface]
        if surface in EXACT_BY_SURFACE:
            spec_row = EXACT_BY_SURFACE[surface]
            mode = "EXACT_WHOLE_WITH_PLACEMENT_RENDER" if surface in {"ydy", "ysheey", "yckhey"} else "EXACT_WHOLE"
            default = spec_row["working_meaning_de"]
            composition = spec_row["composition"]
            rival = spec_row["strongest_rival_de"]
            rule = "exact whitespace-delimited whole only; placement may change practical punctuation"
            status = "ACCEPT_V37_EXACT_WHOLE_NO_SUBSTRING_EXPORT"
        else:
            mode = "OCCURRENCE_SCOPED_CONTEXT_CARDS"
            default = "Samen-/Saatgutposten; L-only Siglum" if surface == "s" else "Qualitäts-/Wertfeldschluss"
            composition = "NAKED_S_POSITION_DISPATCH" if surface == "s" else "NAKED_DY_POSITION_DISPATCH"
            rival = "Species-/Drogenart oder Salz" if surface == "s" else "eigenständige Arzneiform"
            rule = "dispatch by exact token equality, kind and physical-line position; never by substring"
            status = "ACCEPT_V37_CONTEXT_SCOPED_NOT_GLOBAL_LEXEME"
        decision_rows.append({
            "decision_id": f"G660-D{len(decision_rows) + 1:02d}", "surface": surface,
            "mode": mode, "working_default_de": default, "composition": composition,
            "selection_rule": rule, "strongest_rival_de": rival,
            "occurrences": len(members), "lines": len({row["locus"] for row in members}),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in members),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in members),
            "status": status,
        })
    accepted_rows = [{
        "surface": row["surface"], "working_meaning_de": row["working_meaning_de"],
        "composition": row["composition"], "strongest_rival_de": row["strongest_rival_de"],
        "occurrences": EXPECTED_SURFACE_COUNTS[row["surface"]], "scope": "EXACT_WHITESPACE_DELIMITED_WHOLE",
        "status": "ACCEPT_V37_PROVISIONAL_REPLACEABLE_NO_SUBSTRING_EXPORT",
    } for row in EXACT_WHOLE_SPECS]

    sd_rows = [dict(row) for row in occurrence_rows if row["surface"] in {"s", "dy"}]
    cards: list[dict[str, object]] = []
    for index, klass in enumerate(S_DY_CONTEXT_ORDER, 1):
        members = [row for row in sd_rows if row["context_class"] == klass]
        cards.append({
            "card_id": f"G660-C{index:02d}", "surface": card_value(klass, 0), "context_class": klass,
            "structural_tag": card_value(klass, 2), "selection_rule": card_value(klass, 1),
            "working_meaning_de": card_value(klass, 3), "practical_render_de": card_value(klass, 4),
            "token_gloss_de": card_value(klass, 3), "working_render_de": card_value(klass, 4),
            "strongest_rival_de": card_value(klass, 5), "occurrences": len(members),
            "lines": len({row["locus"] for row in members}), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in members),
            "status": "ACCEPT_V37_CONTEXT_CARD_NOT_GLOBAL_LEXEME",
        })
    if len(cards) != 7 or {row["context_class"]: row["occurrences"] for row in cards} != EXPECTED_CONTEXT_COUNTS:
        raise RuntimeError("seven-card S/DY deck drift")
    sd_summary = [{
        "surface": surface, "context_class": klass,
        "occurrences": sum(row["surface"] == surface and row["context_class"] == klass for row in sd_rows),
        "attachment_profile": "|".join(f"{key}:{value}" for key, value in sorted(Counter(
            str(row["attachment_class"]) for row in sd_rows if row["surface"] == surface and row["context_class"] == klass
        ).items())) or "NONE",
        "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in sd_rows if row["surface"] == surface and row["context_class"] == klass),
        "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in sd_rows if row["surface"] == surface and row["context_class"] == klass),
    } for surface in ("s", "dy") for klass in S_DY_CONTEXT_ORDER if card_value(klass, 0) == surface]

    target_line_rows: list[dict[str, object]] = []
    for locus in sorted(affected_loci):
        members = [row for row in occurrence_rows if row["locus"] == locus]
        base_row = base_coverage_by_locus[locus]
        final_row = coverage_by_locus[locus]
        target_line_rows.append({
            "page": final_row["page"], "locus": locus, "section": final_row["section"],
            "language": final_row["language"], "hand": final_row["hand"],
            "target_occurrences": len(members), "target_ordinals": "|".join(str(row["ordinal"]) for row in members),
            "target_surfaces": "|".join(str(row["surface"]) for row in members),
            "context_or_placement_classes": "|".join(str(row["context_class"] if row["context_class"] != "EXACT_WHOLE" else row["placement_class"]) for row in members),
            "zl3b_line": final_row["zl3b_line"], "v36_token_glosses_de": base_row["token_glosses_de"],
            "v37_token_glosses_de": final_row["token_glosses_de"],
            "v36_working_translation_de": g659.render_line(locus, by_line[locus], split_pipe(base_row["token_glosses_de"]), y_occurrence_by_token),
            "v37_working_translation_de": practical_line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]), y_occurrence_by_token, target_occurrence_by_token
            ),
            "v36_unknown_tokens": base_row["unknown_tokens"], "v37_unknown_tokens": final_row["unknown_tokens"],
            "v37_complete": int(int(final_row["unknown_tokens"]) == 0),
        })
    if len(target_line_rows) != 510 or sum(int(row["target_occurrences"]) for row in target_line_rows) != 566:
        raise RuntimeError("target-line translation census drift")

    materia_atlas = family_atlas(MATERIA_AMOUNT_FAMILIES, surface_counts, surface_pages, exact, normalized, tokens_by_surface, base_glossary)
    quality_atlas = family_atlas(QUALITY_PREPARATION_FAMILIES, surface_counts, surface_pages, exact, normalized, tokens_by_surface, base_glossary)
    y_prefix_atlas = family_atlas(Y_PREFIX_FAMILIES, surface_counts, surface_pages, exact, normalized, tokens_by_surface, base_glossary)
    for row in y_prefix_atlas:
        surface = str(row["surface"])
        row["placement_profile"] = "|".join(f"{key}:{value}" for key, value in sorted(Counter(
            str(member["placement_class"]) for member in occurrence_rows if member["surface"] == surface
        ).items())) or "ANCHOR_ONLY"

    base_metrics = metrics(base_coverage, base_one, base_complete, base_glossary_rows)
    final_metrics = metrics(coverage_rows, one_rows, complete_rows, glossary_rows)
    expected_base_metrics = {
        "physical_lines": 4128, "known_token_positions": 17013, "unknown_token_positions": 15326,
        "complete_multi_token_lines": 146, "strict_complete_lines": 80,
        "one_unknown_lines": 249, "strict_one_unknown_lines": 58, "working_glossary_surfaces": 495,
    }
    if base_metrics != expected_base_metrics:
        raise RuntimeError(f"V36 base coverage metrics drift: {base_metrics!r}")
    if final_metrics["known_token_positions"] != 17579 or final_metrics["unknown_token_positions"] != 14760 or final_metrics["working_glossary_surfaces"] != 510:
        raise RuntimeError(f"V37 target arithmetic drift: {final_metrics!r}")
    round_rows = [
        {"version": "V36", "added_cards": "BASE", "dictionary_entries": len(base_dictionary), **base_metrics},
        {"version": "V37", "added_cards": "15_EXACT_WHOLES+7_S_DY_CONTEXT+2_YDY_PLACEMENT", "dictionary_entries": len(dictionary_rows), **final_metrics},
    ]

    coverage_fields = list(base_coverage[0])
    complete_fields = list(base_complete[0])
    one_fields = list(base_one[0])
    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", decision_rows, list(decision_rows[0]))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_rows, list(accepted_rows[0]))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, list(audit_rows[0]))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", reader_rows, list(reader_rows[0]))
    write_tsv(output_dir / "S_DY_CONTEXT_CENSUS.tsv", sd_rows, list(sd_rows[0]))
    write_tsv(output_dir / "S_DY_CONTEXT_CARDS.tsv", cards, list(cards[0]))
    write_tsv(output_dir / "S_DY_CONTEXT_SUMMARY.tsv", sd_summary, list(sd_summary[0]))
    write_tsv(output_dir / "MATERIA_AMOUNT_FAMILY_ATLAS.tsv", materia_atlas, list(materia_atlas[0]))
    write_tsv(output_dir / "QUALITY_PREPARATION_FAMILY_ATLAS.tsv", quality_atlas, list(quality_atlas[0]))
    write_tsv(output_dir / "Y_PREFIX_PLACEMENT_ATLAS.tsv", y_prefix_atlas, list(y_prefix_atlas[0]))
    write_tsv(output_dir / "TARGET_LINE_TRANSLATIONS.tsv", target_line_rows, list(target_line_rows[0]))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, list(round_rows[0]))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", newly_completed, complete_fields)
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_one, ["base_unknown_tokens", *one_fields])
    write_tsv(output_dir / "V37_WORKING_TOKEN_GLOSSARY.tsv", glossary_rows, list(base_glossary_rows[0]))
    write_tsv(output_dir / "WORKING_DICTIONARY_V37.tsv", dictionary_rows, list(base_dictionary[0]))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V37.tsv", coverage_rows, coverage_fields)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V37.tsv", complete_rows, complete_fields)
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V37.tsv", one_rows, one_fields)

    input_paths = (
        G659 / "REPORT.md", G659 / "artifacts/RESULT.json", G659 / "artifacts/PAGE_ALLOWLIST.tsv",
        G659 / "artifacts/V36_WORKING_TOKEN_GLOSSARY.tsv", G659 / "artifacts/WORKING_DICTIONARY_V36.tsv",
        G659 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V36.tsv", G659 / "artifacts/COMPLETE_PASSAGES_V36.tsv",
        G659 / "artifacts/ONE_UNKNOWN_PASSAGES_V36.tsv", G659 / "artifacts/Y_OCCURRENCE_CENSUS.tsv",
        TOKENS_REL, CROSS_REL,
    )
    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    result_core: dict[str, object] = {
        "schema": "GDT660_SEVENTEEN_RESIDUAL_CONCRETE_COMPLETION_RESULT_V1",
        "experiment_id": "GDT660", "status": STATUS,
        "guard": {
            "allowed_pages": len(pages), "f1r": "EXCLUDED_BY_EXACT_ALLOWLIST",
            "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0, "new_images": 0,
            "token_query": token_stats, "cross_query": cross_stats,
        },
        "targets": {
            "surface_types": len(TARGET_SURFACES), "exact_whole_surfaces": len(EXACT_WHOLE_SPECS),
            "context_scoped_surfaces": 2, "positions": len(occurrence_rows),
            "lines": len(affected_loci), "pages": len({row["page"] for row in occurrence_rows}),
            "surface_counts": observed_counts,
            "reader_exact_positions": sum(int(row["reader_exact"]) for row in occurrence_rows),
            "split_normalized_positions": sum(int(row["split_normalized"]) for row in occurrence_rows),
            "all_positions_concrete": True, "substring_dispatch_positions": 0,
        },
        "context_cards": {
            "s_dy_cards": len(cards), "counts": dict(context_counts),
            "s_attachment_audit": dict(sorted(Counter(str(row["attachment_class"]) for row in sd_rows if row["surface"] == "s").items())),
            "dy_attachment_audit": dict(sorted(Counter(str(row["attachment_class"]) for row in sd_rows if row["surface"] == "dy").items())),
            "global_s_lexeme_added": False, "global_dy_lexeme_added": False,
        },
        "coverage": {
            "base": base_metrics, "final": final_metrics, "affected_lines": len(affected_loci),
            "newly_completed_lines": len(newly_completed),
            "newly_completed_loci": sorted(row["locus"] for row in newly_completed),
            "newly_exposed_one_hole_lines": len(newly_one),
            "newly_exposed_one_hole_loci": sorted(row["locus"] for row in newly_one),
            "non_target_token_positions_unchanged": len(non_target_before),
            "non_target_before_sha256": non_target_before_sha, "non_target_after_sha256": non_target_after_sha,
            "non_target_exactly_unchanged": non_target_before == non_target_after,
        },
        "working_dictionary": {
            "v36_entries": len(base_dictionary), "v37_entries": len(dictionary_rows),
            "added_exact_whole_entries": len(EXACT_WHOLE_SPECS), "added_s_dy_context_entries": len(cards),
            "added_ydy_placement_entries": 2, "v36_glossary_surfaces": len(base_glossary_rows),
            "v37_glossary_surfaces": len(glossary_rows), "global_s_dy_glossary_rows": 0,
        },
        "determinism_contract": {
            "builder_supports_artifact_dir_cli": True, "exact_whole_dispatch_requires_token_equality": True,
            "s_dy_occurrence_dispatcher_required": True,
            "replay_files": [str(BASE_REL / "artifacts" / name) for name in (*OUTPUT_NAMES, "RESULT.json")],
        },
        "claim_boundary": (
            "Exploratory replaceable concrete defaults for exactly seventeen residual whitespace-delimited surfaces. "
            "Fifteen are exact whole cards; naked s and dy remain position-scoped. No substring inheritance, glyph identity, "
            "phonetics, language, plaintext, exact ingredient identity, new page, image, f1r, f84 or f84r is asserted."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=ART)
    args = parser.parse_args(argv)
    result = build(args.artifact_dir)
    if args.artifact_dir.resolve() == ART.resolve():
        with tempfile.TemporaryDirectory(prefix="gdt660_replay_") as directory:
            replay_dir = Path(directory)
            replay_result = build(replay_dir)
            if replay_result != result:
                raise RuntimeError("tempdir RESULT replay differs")
            for name in (*OUTPUT_NAMES, "RESULT.json"):
                if (ART / name).read_bytes() != (replay_dir / name).read_bytes():
                    raise RuntimeError(f"tempdir replay differs: {name}")
    print(
        f"GDT660 built: targets={result['targets']['positions']} exact_wholes=15 cards=7 "
        f"known={result['coverage']['final']['known_token_positions']} "
        f"complete={result['coverage']['final']['complete_multi_token_lines']} "
        f"one_hole={result['coverage']['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
