#!/usr/bin/env python3
"""Build an exact-whole atlas of likely line-opening formula roles."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
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
BASE_REL = Path("experiments/yolo/gdt757_initial_formula_role_atlas")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G756_RUN_REL = Path(
    "experiments/yolo/gdt756_ychor_line_frame_content_slots/src/run.py"
)
G756_INITIAL_REL = Path(
    "experiments/yolo/gdt756_ychor_line_frame_content_slots/"
    "artifacts/LINE_INITIAL_RECIPE_TRIAD_RANKING.tsv"
)
G754_INVENTORY_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/ACTIVE_172_PRODUCTIVE_COMPOUND_INVENTORY.tsv"
)
OUTPUT_NAMES = (
    "INITIAL_FORMULA_79_OCCURRENCE_ATLAS.tsv",
    "INITIAL_FORMULA_11_WHOLE_ROLE_ATLAS.tsv",
    "FORMULA_ROLE_CANDIDATE_RANKING.tsv",
    "LOW_PURITY_HIGH_TRIAD_COMPARATORS.tsv",
    "EDIT1_FORMULA_NEIGHBOR_ATLAS.tsv",
    "GDT757_FORMULA_ROLE_READER.md",
    "RESULT.json",
)
TARGET_FORMS = (
    "pchor", "ychor", "polaiin", "pol", "ycheol", "ychol",
    "dcheol", "paiin", "qokchor", "tshol", "ycheor",
)
COMPARATOR_FORMS = ("ykar", "yteedy", "qotor", "dchey")
CONTINUATION_ROLES = {
    "ITEM_CONTINUATION", "ITEM_PLUS_COMMAND", "PROCESS_CONTINUATION",
    "CLOSURE_FORMULA", "ADDITION_COMMAND",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g756 = load_module("gdt756_builder_for_gdt757", ROOT / G756_RUN_REL)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]
) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def fixed(value: float) -> str:
    return f"{value:.6f}"


def count_text(items: Iterable[str]) -> str:
    counts = Counter(items)
    return "|".join(f"{item}:{counts[item]}" for item in sorted(counts)) or "NONE"


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, char_left in enumerate(left, start=1):
        current = [i]
        for j, char_right in enumerate(right, start=1):
            current.append(min(
                current[-1] + 1,
                previous[j] + 1,
                previous[j - 1] + int(char_left != char_right),
            ))
        previous = current
    return previous[-1]


def profile_for_surface(
    surface: str,
    context: object,
    line_meta: dict[str, dict[str, str]],
    paragraph_indices: dict[str, int],
    suspect_surfaces: set[str],
    initial_rank: dict[str, dict[str, str]],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    global_occurrences: list[tuple[str, int]] = []
    initial_rows: list[dict[str, object]] = []
    for locus, line in context.by_line.items():
        for ordinal, token in enumerate(line, start=1):
            if (
                str(token["eva"]) == surface
                and context.exact[(locus, int(token["token_index"]))]
            ):
                global_occurrences.append((locus, ordinal))
        if not line or str(line[0]["eva"]) != surface:
            continue
        if not context.exact[(locus, int(line[0]["token_index"]))]:
            continue
        features = g756.body_features(context, locus, suspect_surfaces)
        initial_rows.append({
            "surface": surface,
            "page": line[0]["page"],
            "locus": locus,
            "section": line[0]["section"],
            "language": line[0]["language"],
            "hand": line[0]["hand"],
            "paragraph_line_index": paragraph_indices[locus],
            "paragraph_start": line_meta[locus]["paragraph_start"],
            "paragraph_end": line_meta[locus]["paragraph_end"],
            "line_token_count": len(line),
            "written_line_eva": " ".join(str(token["eva"]) for token in line),
            "written_body_eva": " ".join(str(token["eva"]) for token in line[1:]),
            "independent_body_axes": g756.joined(features["independent_body_axes"]),
            "content_present": features["content_present"],
            "amount_or_level_present": features["amount_or_level_present"],
            "process_present": features["process_present"],
            "quality_or_stage_present": features["quality_or_stage_present"],
            "recipe_content_amount_process_triad": features["recipe_content_amount_process_triad"],
            "reader_exact_body_tokens": features["reader_exact_body_tokens"],
            "independent_axis_body_tokens": features["independent_axis_body_tokens"],
            "suspect_axis_tokens_excluded": features["suspect_axis_tokens_excluded"],
        })
    total_initial = len(initial_rows)
    total_global = len(global_occurrences)
    section_counts = Counter(str(row["section"]) for row in initial_rows)
    profile = {
        "surface": surface,
        "global_reader_exact_occurrences": total_global,
        "reader_exact_line_initial_occurrences": total_initial,
        "global_line_initial_purity": rate(total_initial, total_global),
        "paragraph_initial_occurrences": sum(int(row["paragraph_start"]) for row in initial_rows),
        "paragraph_initial_rate": rate(sum(int(row["paragraph_start"]) for row in initial_rows), total_initial),
        "paragraph_final_occurrences": sum(int(row["paragraph_end"]) for row in initial_rows),
        "paragraph_final_rate": rate(sum(int(row["paragraph_end"]) for row in initial_rows), total_initial),
        "mean_paragraph_line_index": rate(sum(int(row["paragraph_line_index"]) for row in initial_rows), total_initial),
        "section_counts": count_text(str(row["section"]) for row in initial_rows),
        "section_count": len(section_counts),
        "dominant_section_share": rate(max(section_counts.values(), default=0), total_initial),
        "herbal_share": rate(section_counts.get("H", 0), total_initial),
        "content_lines": sum(int(row["content_present"]) for row in initial_rows),
        "content_rate": rate(sum(int(row["content_present"]) for row in initial_rows), total_initial),
        "amount_or_level_lines": sum(int(row["amount_or_level_present"]) for row in initial_rows),
        "amount_or_level_rate": rate(sum(int(row["amount_or_level_present"]) for row in initial_rows), total_initial),
        "process_lines": sum(int(row["process_present"]) for row in initial_rows),
        "process_rate": rate(sum(int(row["process_present"]) for row in initial_rows), total_initial),
        "quality_or_stage_lines": sum(int(row["quality_or_stage_present"]) for row in initial_rows),
        "quality_or_stage_rate": rate(sum(int(row["quality_or_stage_present"]) for row in initial_rows), total_initial),
        "recipe_triad_lines": sum(int(row["recipe_content_amount_process_triad"]) for row in initial_rows),
        "recipe_triad_rate": rate(sum(int(row["recipe_content_amount_process_triad"]) for row in initial_rows), total_initial),
        "recipe_triad_rate_rank": int(initial_rank[surface]["recipe_triad_rate_rank"]),
    }
    return profile, initial_rows


def role_fit(role: str, profile: dict[str, object]) -> tuple[float, str]:
    ps = float(profile["paragraph_initial_rate"])
    pe = float(profile["paragraph_final_rate"])
    cont = 1.0 - ps
    triad = float(profile["recipe_triad_rate"])
    content = float(profile["content_rate"])
    amount = float(profile["amount_or_level_rate"])
    process = float(profile["process_rate"])
    quality = float(profile["quality_or_stage_rate"])
    purity = float(profile["global_line_initial_purity"])
    herbal = float(profile["herbal_share"])
    dominant = float(profile["dominant_section_share"])
    triad_rank = int(profile["recipe_triad_rate_rank"])
    if role == "RECIPE_OPENING":
        score = 35*ps + 25*triad + 15*process + 10*content + 5*amount + 10*purity
        if triad_rank == 1:
            score += 10
        basis = "Absatzanfang + vollständiger Inhalts/Mengen/Vorgangs-Körper"
    elif role == "INDICATION_OPENING":
        score = 40*ps + 20*herbal + 10*content + 10*amount + 10*purity + 10*(1-triad)
        basis = "Absatzanfang, herbaler Schwerpunkt und kein Zwang zu vollständigem Rezeptkörper"
    elif role == "ENTRY_HEADING":
        score = 45*ps + 15*content + 10*quality + 15*purity + 15*dominant
        basis = "Absatzanfang + sektional konzentrierter Inhalts/Qualitäts-Körper"
    elif role == "ITEM_CONTINUATION":
        score = 40*cont + 20*triad + 10*content + 10*process + 15*purity + 5*pe
        basis = "interne Zeile + Rezeptkörper + hohe Anfangsreinheit"
    elif role == "ITEM_PLUS_COMMAND":
        score = 40*cont + 20*triad + 10*content + 10*process + 15*purity + 5*pe - 3
        basis = "wie Item-Fortsetzung, mit Spezifitätsabzug für zwei Bedeutungen in einer Form"
    elif role == "PROCESS_CONTINUATION":
        score = 35*cont + 20*process + 10*quality + 10*content + 15*purity + 10*(1-pe)
        basis = "interne, nicht überwiegend finale Zeile mit Vorgangs-/Qualitätskörper"
    elif role == "CLOSURE_FORMULA":
        score = 30*cont + 40*pe + 10*process + 5*content + 15*purity
        basis = "interne Zeile mit starkem Absatzendgewicht"
    elif role == "QUANTITY_HEADING":
        score = 30*amount + 20*quality + 15*purity + 15*cont + 10*pe + 15*triad
        basis = "Mengen-/Gradkörper + lineares Kopfgewicht; Ganzwortlesung ohne aiin-Export"
    elif role == "ADDITION_COMMAND":
        score = 35*cont + 25*content + 15*quality + 10*process + 15*purity
        basis = "interne Zeile, danach besonders oft Inhalt und Qualität"
    else:
        raise ValueError(f"unknown role {role}")
    return min(100.0, score), basis


def candidate_rankings(
    profiles: dict[str, dict[str, object]],
    priors_by_surface: dict[str, list[dict[str, str]]],
    historical: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for surface in TARGET_FORMS:
        rows: list[dict[str, object]] = []
        for prior in priors_by_surface[surface]:
            source_ids = prior["source_ids"].split("|")
            if not source_ids or any(source_id not in historical for source_id in source_ids):
                raise AssertionError(f"unknown historical source for {surface}")
            score, score_basis = role_fit(prior["role_id"], profiles[surface])
            rows.append({
                "surface": surface,
                "source_prior_order": prior["prior_order"],
                "role_id": prior["role_id"],
                "historical_expression": prior["historical_expression"],
                "working_candidate_de": prior["working_candidate_de"],
                "placement_fit_score_0_100": fixed(score),
                "placement_fit_basis": score_basis,
                "source_ids": prior["source_ids"],
                "historical_source_count": len(source_ids),
                "candidate_evidence": prior["candidate_evidence"],
                "counterevidence": prior["counterevidence"],
                "exact_whole_only": 1,
                "eva_spelling_used": 0,
                "component_export_credit": 0,
                "confirmed_lexeme": 0,
            })
        rows.sort(key=lambda row: (-float(row["placement_fit_score_0_100"]), int(row["source_prior_order"])))
        for rank, row in enumerate(rows, start=1):
            row["candidate_rank"] = rank
            row["selected_primary"] = int(rank == 1)
        fields = ["surface", "candidate_rank", "selected_primary", *[
            key for key in rows[0] if key not in {"surface", "candidate_rank", "selected_primary"}
        ]]
        output.extend({field: row[field] for field in fields} for row in rows)
    return output


def whole_atlas(
    profiles: dict[str, dict[str, object]],
    rankings: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rankings:
        by_surface[str(row["surface"])].append(row)
    output: list[dict[str, object]] = []
    for surface in TARGET_FORMS:
        candidates = sorted(by_surface[surface], key=lambda row: int(row["candidate_rank"]))
        primary, second, third = candidates
        profile = profiles[surface]
        primary_score = float(primary["placement_fit_score_0_100"])
        confidence = (
            "C2_GEOMETRY_STRONG_EXPLORATORY"
            if (
                float(profile["global_line_initial_purity"]) >= 0.8
                and (
                    float(profile["paragraph_initial_rate"]) >= 0.8
                    or float(profile["paragraph_final_rate"]) >= 0.5
                    or int(profile["paragraph_initial_occurrences"]) == 0
                )
                and primary_score >= 65
            ) else "C1_PLACEMENT_CONSTRAINED"
            if primary_score >= 60
            else "C0_FORCED_EXPLORATORY"
        )
        output.append({
            "surface": surface,
            "selection_gate": "TRIAD_RATE_GE_0.20__INITIAL_PURITY_GE_0.70__MIN5_INITIAL",
            "global_reader_exact_occurrences": profile["global_reader_exact_occurrences"],
            "reader_exact_line_initial_occurrences": profile["reader_exact_line_initial_occurrences"],
            "global_line_initial_purity": fixed(float(profile["global_line_initial_purity"])),
            "paragraph_initial_occurrences": profile["paragraph_initial_occurrences"],
            "paragraph_initial_rate": fixed(float(profile["paragraph_initial_rate"])),
            "paragraph_final_occurrences": profile["paragraph_final_occurrences"],
            "paragraph_final_rate": fixed(float(profile["paragraph_final_rate"])),
            "mean_paragraph_line_index": fixed(float(profile["mean_paragraph_line_index"])),
            "section_counts": profile["section_counts"],
            "section_count": profile["section_count"],
            "dominant_section_share": fixed(float(profile["dominant_section_share"])),
            "herbal_share": fixed(float(profile["herbal_share"])),
            "content_lines": profile["content_lines"],
            "amount_or_level_lines": profile["amount_or_level_lines"],
            "process_lines": profile["process_lines"],
            "quality_or_stage_lines": profile["quality_or_stage_lines"],
            "recipe_triad_lines": profile["recipe_triad_lines"],
            "recipe_triad_rate": fixed(float(profile["recipe_triad_rate"])),
            "recipe_triad_rate_rank": profile["recipe_triad_rate_rank"],
            "primary_role_id": primary["role_id"],
            "primary_historical_expression": primary["historical_expression"],
            "working_candidate_de": primary["working_candidate_de"],
            "primary_fit_score_0_100": primary["placement_fit_score_0_100"],
            "alternate_1_de": second["working_candidate_de"],
            "alternate_1_role_id": second["role_id"],
            "alternate_2_de": third["working_candidate_de"],
            "alternate_2_role_id": third["role_id"],
            "fit_gap_to_second": fixed(float(primary["placement_fit_score_0_100"]) - float(second["placement_fit_score_0_100"])),
            "working_confidence": confidence,
            "evidence": primary["candidate_evidence"],
            "counterevidence": primary["counterevidence"],
            "exact_whole_only": 1,
            "eva_spelling_used": 0,
            "component_export_credit": 0,
            "confirmed_lexeme": 0,
        })
    return output


def comparator_atlas(
    profiles: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for surface in COMPARATOR_FORMS:
        profile = profiles[surface]
        output.append({
            "surface": surface,
            "global_reader_exact_occurrences": profile["global_reader_exact_occurrences"],
            "reader_exact_line_initial_occurrences": profile["reader_exact_line_initial_occurrences"],
            "global_line_initial_purity": fixed(float(profile["global_line_initial_purity"])),
            "paragraph_initial_occurrences": profile["paragraph_initial_occurrences"],
            "paragraph_final_occurrences": profile["paragraph_final_occurrences"],
            "recipe_triad_lines": profile["recipe_triad_lines"],
            "recipe_triad_rate": fixed(float(profile["recipe_triad_rate"])),
            "recipe_triad_rate_rank": profile["recipe_triad_rate_rank"],
            "disposition": "LEFT_EDGE_CONTENT_OR_CONTEXTUAL_FORM__NOT_GLOBAL_FORMULA",
            "reason": "good initial body score but the complete form usually occurs away from line start",
            "working_translation_assigned": 0,
            "confirmed_lexeme": 0,
        })
    return output


def edit_neighbor_atlas(whole_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_surface = {str(row["surface"]): row for row in whole_rows}
    output: list[dict[str, object]] = []
    number = 0
    for left_index, left in enumerate(TARGET_FORMS):
        for right in TARGET_FORMS[left_index + 1:]:
            distance = levenshtein(left, right)
            if distance != 1:
                continue
            number += 1
            a, b = by_surface[left], by_surface[right]
            roles = {str(a["primary_role_id"]), str(b["primary_role_id"])}
            if {left, right} == {"pchor", "ychor"}:
                relation = "OPENER_VS_CONTINUATION_CONTRAST"
            elif roles <= CONTINUATION_ROLES:
                relation = "INTERNAL_CONTINUATION_OR_CLOSURE_FAMILY"
            else:
                relation = "NEAR_FORM_ROLE_RELATION_OPEN"
            output.append({
                "pair_id": f"G757-N{number:02d}",
                "left_surface": left,
                "right_surface": right,
                "levenshtein_distance": distance,
                "left_initial_occurrences": a["reader_exact_line_initial_occurrences"],
                "right_initial_occurrences": b["reader_exact_line_initial_occurrences"],
                "left_paragraph_initial_rate": a["paragraph_initial_rate"],
                "right_paragraph_initial_rate": b["paragraph_initial_rate"],
                "paragraph_initial_rate_delta_left_minus_right": fixed(float(a["paragraph_initial_rate"]) - float(b["paragraph_initial_rate"])),
                "left_paragraph_final_rate": a["paragraph_final_rate"],
                "right_paragraph_final_rate": b["paragraph_final_rate"],
                "left_primary_role": a["primary_role_id"],
                "right_primary_role": b["primary_role_id"],
                "relation": relation,
                "component_meaning_inferred": 0,
                "whole_form_prediction_only": 1,
            })
    return output


def write_reader(
    path: Path,
    whole_rows: list[dict[str, object]],
    occurrence_rows: list[dict[str, object]],
    comparator_rows: list[dict[str, object]],
    neighbors: list[dict[str, object]],
) -> None:
    text = [
        "# GDT757 formula-role reader", "",
        "## Current compact dictionary", "",
        "These are complete-form working readings. They do not decompose EVA spelling.", "",
        "| whole | primary candidate | role | placement | rivals | confidence |",
        "|---|---|---|---|---|---|",
    ]
    for row in whole_rows:
        text.append(
            f"| `{row['surface']}` | **{row['working_candidate_de']}** | `{row['primary_role_id']}` | "
            f"P-start {row['paragraph_initial_occurrences']}/{row['reader_exact_line_initial_occurrences']}; "
            f"P-end {row['paragraph_final_occurrences']}/{row['reader_exact_line_initial_occurrences']} | "
            f"{row['alternate_1_de']} / {row['alternate_2_de']} | `{row['working_confidence']}` |"
        )
    text.extend([
        "", "## The decisive split", "",
        "`pchor` and `ychor` are edit-distance-one complete forms but occupy opposite paragraph frames. `pchor` opens 6/7 of its initial paragraphs; `ychor` opens 0/13. This supports two learned formula wholes—recipe/entry opening versus Item-like continuation—without assigning a meaning to `p` or `y`.", "",
        "The neighboring `ycheol`, `ychol`, `dcheol`, and `ycheor` wholes jointly contribute 26 initial lines, only one paragraph start, and nine paragraph ends. Their current readings therefore stay in an internal continuation/closure family.", "",
        "## Complete formula-only line reader", "",
        "The marker is translated; the untouched body remains EVA in brackets so this artifact does not smuggle generic filler into the line.", "",
    ])
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    whole_by_surface = {str(row["surface"]): row for row in whole_rows}
    for row in occurrence_rows:
        by_surface[str(row["surface"])].append(row)
    for surface in TARGET_FORMS:
        whole = whole_by_surface[surface]
        text.extend([f"### `{surface}` → {whole['working_candidate_de']}", ""])
        for row in by_surface[surface]:
            punctuation = ":" if str(whole["primary_role_id"]) not in {"PROCESS_CONTINUATION", "CLOSURE_FORMULA", "ADDITION_COMMAND"} else ","
            text.append(
                f"- {row['locus']} (P{row['paragraph_line_index']}; start={row['paragraph_start']}; end={row['paragraph_end']}): "
                f"**{whole['working_candidate_de']}**{punctuation} [{row['written_body_eva']}]"
            )
        text.append("")
    text.extend([
        "## Rejected shortcut", "",
        "The high-triad initials `ykar`, `yteedy`, `qotor`, and `dchey` are not promoted to global formula words because their line-initial purity is below 0.70. They remain possible contextual left-edge content or local formula uses.", "",
        "## Neighbor inventory", "",
        "| left | right | relation | paragraph-start rates |",
        "|---|---|---|---|",
    ])
    for row in neighbors:
        text.append(
            f"| `{row['left_surface']}` | `{row['right_surface']}` | `{row['relation']}` | "
            f"{row['left_paragraph_initial_rate']} / {row['right_paragraph_initial_rate']} |"
        )
    text.extend([
        "", "No candidate is a confirmed lexeme. The practical result is an eleven-whole formula inventory with explicit rivals and a predictive distinction between opening, continuation, addition and closure positions.",
    ])
    path.write_text("\n".join(text).rstrip() + "\n", encoding="utf-8")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    context, line_meta, guard = g756.g755.g753.g752.g751.load_context()
    initial_rows = read_tsv(ROOT / G756_INITIAL_REL)
    inventory = read_tsv(ROOT / G754_INVENTORY_REL)
    prior_rows = read_tsv(SRC / "FORMULA_ROLE_PRIORS.tsv")
    historical_rows = read_tsv(SRC / "HISTORICAL_FORMULA_REGISTER.tsv")
    initial_rank = {row["initial_surface"]: row for row in initial_rows}
    suspect_surfaces = {row["surface"] for row in inventory}
    historical = {row["source_id"]: row for row in historical_rows}
    priors_by_surface: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in prior_rows:
        priors_by_surface[row["surface"]].append(row)

    selected_from_gate = tuple(
        row["initial_surface"] for row in initial_rows
        if float(row["recipe_triad_rate"]) >= 0.2
        and float(row["global_line_initial_purity"]) >= 0.7
    )
    if set(selected_from_gate) != set(TARGET_FORMS) or len(selected_from_gate) != 11:
        raise AssertionError(f"target gate changed: {selected_from_gate}")
    if set(priors_by_surface) != set(TARGET_FORMS):
        raise AssertionError("formula prior surface universe mismatch")
    if any(len(priors_by_surface[surface]) != 3 for surface in TARGET_FORMS):
        raise AssertionError("each target needs exactly three candidates")
    if len(historical) != 8 or len(historical_rows) != 8:
        raise AssertionError("historical formula register changed")

    paragraph_indices = g756.paragraph_line_indices(context, line_meta)
    profiles: dict[str, dict[str, object]] = {}
    occurrence_by_surface: dict[str, list[dict[str, object]]] = {}
    for surface in (*TARGET_FORMS, *COMPARATOR_FORMS):
        profile, occurrences = profile_for_surface(
            surface, context, line_meta, paragraph_indices, suspect_surfaces,
            initial_rank,
        )
        profiles[surface] = profile
        occurrence_by_surface[surface] = occurrences

    rankings = candidate_rankings(profiles, priors_by_surface, historical)
    wholes = whole_atlas(profiles, rankings)
    whole_by_surface = {str(row["surface"]): row for row in wholes}
    occurrences: list[dict[str, object]] = []
    number = 0
    for surface in TARGET_FORMS:
        whole = whole_by_surface[surface]
        for row in occurrence_by_surface[surface]:
            number += 1
            occurrences.append({
                "occurrence_id": f"G757-O{number:03d}",
                **row,
                "primary_role_id": whole["primary_role_id"],
                "working_candidate_de": whole["working_candidate_de"],
                "alternate_1_de": whole["alternate_1_de"],
                "alternate_2_de": whole["alternate_2_de"],
                "formula_only_render_de": f"{whole['working_candidate_de']}: [{row['written_body_eva']}]",
                "exact_whole_only": 1,
                "body_translation_claimed": 0,
                "confirmed_lexeme": 0,
            })
    comparators = comparator_atlas(profiles)
    neighbors = edit_neighbor_atlas(wholes)

    if len(occurrences) != 79 or len(wholes) != 11 or len(rankings) != 33:
        raise AssertionError("fixed target artifact size changed")
    if sum(int(row["paragraph_start"]) for row in occurrences) != 27:
        raise AssertionError("target paragraph-start total changed")
    if sum(int(row["paragraph_end"]) for row in occurrences) != 15:
        raise AssertionError("target paragraph-end total changed")
    primary = {row["surface"]: row["working_candidate_de"] for row in wholes}
    expected_primary = {
        "pchor": "nimm", "ychor": "ferner / ebenso",
        "polaiin": "Zubereitung / Rezept", "pol": "Zubereitung / Eintrag",
        "ycheol": "danach", "ychol": "danach / als Nächstes",
        "dcheol": "danach / darauf", "paiin": "drei Teile / dritte Menge",
        "qokchor": "mische hinein", "tshol": "für / gegen",
        "ycheor": "zum Schluss",
    }
    if primary != expected_primary:
        raise AssertionError(f"candidate ranking changed: {primary}")
    family = [whole_by_surface[s] for s in ("ycheol", "ychol", "dcheol", "ycheor")]
    family_initial = sum(int(row["reader_exact_line_initial_occurrences"]) for row in family)
    family_start = sum(int(row["paragraph_initial_occurrences"]) for row in family)
    family_end = sum(int(row["paragraph_final_occurrences"]) for row in family)
    if (family_initial, family_start, family_end) != (26, 1, 9):
        raise AssertionError("internal formula family geometry changed")

    write_tsv(output_dir / OUTPUT_NAMES[0], occurrences, list(occurrences[0]))
    write_tsv(output_dir / OUTPUT_NAMES[1], wholes, list(wholes[0]))
    write_tsv(output_dir / OUTPUT_NAMES[2], rankings, list(rankings[0]))
    write_tsv(output_dir / OUTPUT_NAMES[3], comparators, list(comparators[0]))
    write_tsv(output_dir / OUTPUT_NAMES[4], neighbors, list(neighbors[0]))
    write_reader(output_dir / OUTPUT_NAMES[5], wholes, occurrences, comparators, neighbors)

    status = (
        "PARTIAL__11_COMPLETE_FORMULA_WHOLES__79_INITIAL_LINES__"
        "PCHOR_RECIPE_OPEN_6_OF7_PARAGRAPH_START__YCHOR_ITEM_0_OF13_START__"
        "YCHEOL_YCHOL_DCHEOL_YCHEOR_FAMILY_1_OF26_START_9_OF26_END__"
        "4_LOW_PURITY_CONTROLS_NOT_PROMOTED__ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
    )
    result = {
        "schema": "GDT757_RESULT_V1",
        "status": status,
        "scope": {
            "target_complete_forms": len(wholes),
            "target_initial_occurrences": len(occurrences),
            "target_pages": len({str(row["page"]) for row in occurrences}),
            "target_sections": len({str(row["section"]) for row in occurrences}),
            "candidate_rows": len(rankings),
            "historical_formula_sources": len(historical),
            "low_purity_comparator_forms": len(comparators),
            "edit_distance_one_pairs": len(neighbors),
        },
        "primary_working_dictionary": primary,
        "decisive_geometry": {
            "pchor": {
                "initial_occurrences": 7,
                "paragraph_starts": 6,
                "recipe_triads": 3,
                "working_candidate_de": "nimm",
            },
            "ychor": {
                "initial_occurrences": 13,
                "paragraph_starts": 0,
                "recipe_triads": 4,
                "working_candidate_de": "ferner / ebenso",
            },
            "edit_distance_one_pchor_ychor": 1,
            "internal_near_form_family": {
                "surfaces": ["ycheol", "ychol", "dcheol", "ycheor"],
                "initial_occurrences": family_initial,
                "paragraph_starts": family_start,
                "paragraph_ends": family_end,
            },
        },
        "independence_controls": {
            "target_gate_uses_complete_form_geometry_only": True,
            "gdt754_suspect_surfaces_excluded_from_body_axes": len(suspect_surfaces),
            "eva_spelling_used_to_select_historical_expression": 0,
            "substring_meanings_assigned": 0,
            "all_targets_have_two_live_rivals": True,
            "low_initial_purity_forms_promoted": 0,
        },
        "guard": guard,
        "claim_boundary": {
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "component_values": 0,
            "body_translations_claimed": 0,
            "new_pages_opened": 0,
            "new_images_opened": 0,
            "f84_accessed": 0,
            "f84r_accessed": 0,
        },
    }
    (output_dir / OUTPUT_NAMES[6]).write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir.resolve())
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
