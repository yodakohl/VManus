#!/usr/bin/env python3
"""Build a scope-safe spoken overlay for V99R4's 175 audible grade frames."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt732_v99r5_grade_frame_spoken_renderer"
SRC, ART = EXP / "src", EXP / "artifacts"
G671 = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts"
G696 = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts"
G727 = ROOT / "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts"
G730 = ROOT / "experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch/artifacts"
G731 = ROOT / "experiments/yolo/gdt731_v99r4_occurrence_passage_impact"

DICTIONARY = G730 / "V99R4_COMPLETE_WORD_CONFIDENCE.tsv"
LINES = G671 / "ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
PAGES = G671 / "PAGE_ALLOWLIST.tsv"
ACTIVE_CONTEXTS = G727 / "V99_479_CONTEXT_REALIZATIONS.tsv"
POLICY = SRC / "GRADE_SPOKEN_RENDER_POLICY.tsv"
BLOCKER_RULES = G731 / "src/PRACTICAL_BLOCKER_RULES.tsv"

G696_PARITY = (
    G696 / "V69_51_LINE_RELATION_OVERLAY.tsv",
    G696 / "V69_479_TOKEN_RELATION_OVERLAY.tsv",
    G696 / "GDT696_V69_LOCAL_OBJECT_CARRY_READER.md",
)
G727_PARITY = tuple(
    G727 / name
    for name in (
        "V99_324_ACTIVE_LEXICAL_READINGS.tsv",
        "V99_479_CONTEXT_REALIZATIONS.tsv",
        "V99_471_PRACTICAL_RENDERED_UNITS.tsv",
        "V99_51_PRACTICAL_LINE_READER.tsv",
        "GDT727_V99_51_LINE_WORKING_READER.md",
    )
)

STATUS = (
    "PASS_175_GRADE_READINGS_2431_LICENSED_POSITIONS__162_GLOBAL_2401_PLUS_13_ACTIVE_30__"
    "1784_TARGET_ACTIVE_SURFACE_LEAK_CONTROLS__75_DIRECT_ROWS_1748_POSITIONS__100_NEUTRAL_"
    "ROWS_683_POSITIONS__ZERO_TARGET_GRADE_FRAMES__4752_V48_BASELINE_RESIDUALS_4692_"
    "ACTIVE_OUTSIDE_EXACT_PLUS_52_SUPERSEDED_EXACT_PLUS_8_ALIAS_MERGE__V99R4_"
    "SEMANTIC_DICTIONARY_BYTE_STABLE__NO_NEW_PAGE"
)

GRADE_RX = re.compile(r"(?:Grades|Gradanfang|Gradmitte|Gradende)", re.IGNORECASE)
UNKNOWN_RX = re.compile(r"\[[^]]+:\?]")
STAGE_RX = re.compile(
    r"am Anfang des Grades|in der Mitte des Grades|am Ende des Grades|"
    r"am Gradanfang|in der Gradmitte|am Gradende|Gradanfang|Gradmitte|Gradende",
    re.IGNORECASE,
)
STAGE_CODES = {
    "am anfang des grades": "BEGIN", "am gradanfang": "BEGIN", "gradanfang": "BEGIN",
    "in der mitte des grades": "MIDDLE", "in der gradmitte": "MIDDLE", "gradmitte": "MIDDLE",
    "am ende des grades": "END", "am gradende": "END", "gradende": "END",
}
STAGE_LABELS = {"BEGIN": "Anfangsstufe", "MIDDLE": "Mittelstufe", "END": "Endstufe"}
MODALITY_SOURCE = {
    "HEISS": re.compile(r"heiß", re.IGNORECASE),
    "KALT": re.compile(r"kalt", re.IGNORECASE),
    "TROCKEN": re.compile(r"trocken", re.IGNORECASE),
    "FEUCHT": re.compile(r"feucht", re.IGNORECASE),
}
MODALITY_OUTPUT = {
    "HEISS": re.compile(r"(?:heiß|erhitz)", re.IGNORECASE),
    "KALT": re.compile(r"(?:kalt|abgekühl)", re.IGNORECASE),
    "TROCKEN": re.compile(r"(?:trocken|getrockn)", re.IGNORECASE),
    "FEUCHT": re.compile(r"(?:feucht|angefeucht)", re.IGNORECASE),
}
OVERLAY_FIELDS = (
    "v99r5_spoken_render_de", "v99r5_formal_stage_sequence", "v99r5_workflow_closure",
    "v99r5_modality_class", "v99r5_renderer_mode", "v99r5_dispatch_scope",
    "v99r5_policy_rule_ids",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None) -> None:
    data = list(rows)
    fields = fields or (list(data[0]) if data else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in data:
            writer.writerow({field: row.get(field, "") for field in fields})


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_sha(row: dict[str, str]) -> str:
    raw = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def ordered_modalities(text: str, patterns: dict[str, re.Pattern[str]]) -> list[str]:
    hits: list[tuple[int, str]] = []
    for code, pattern in patterns.items():
        for match in pattern.finditer(text):
            hits.append((match.start(), code))
    result: list[str] = []
    for _, code in sorted(hits):
        if code not in result:
            result.append(code)
    return result


def stage_sequence(text: str) -> list[str]:
    return [STAGE_CODES[match.group(0).casefold()] for match in STAGE_RX.finditer(text)]


def closure_status(text: str) -> str:
    if re.search(r"(?<!\w)abgeschlossen(?!\w)", text, re.IGNORECASE):
        return "CLOSED"
    if re.search(r"(?<!\w)fertig(?!\w)", text, re.IGNORECASE):
        return "FINISHED"
    return "OPEN"


def load_policy() -> tuple[dict[str, dict[str, str]], dict[str, tuple[str, str]]]:
    rows = read_tsv(POLICY)
    assert [row["rule_id"] for row in rows] == [f"P{i:02d}" for i in range(1, 11)]
    modalities = {row["modality_code"]: row for row in rows if row["rule_kind"] == "MODALITY"}
    exact = {
        row["exact_old_meaning_de"]: (row["exact_new_spoken_de"], row["rule_id"])
        for row in rows if row["rule_kind"] == "EXACT"
    }
    assert set(modalities) == {"HEISS", "KALT", "TROCKEN", "FEUCHT"}
    assert len(exact) == 4
    assert sum(row["rule_kind"] == "NEUTRAL" for row in rows) == 2
    return modalities, exact


def stageize(text: str) -> str:
    replacements = (
        (" am Anfang des Grades", ", Anfangsstufe"),
        (" in der Mitte des Grades", ", Mittelstufe"),
        (" am Ende des Grades", ", Endstufe"),
        (" am Gradanfang", ", Anfangsstufe"),
        (" in der Gradmitte", ", Mittelstufe"),
        (" am Gradende", ", Endstufe"),
        (", Gradanfang", ", Anfangsstufe"),
        (", Gradmitte", ", Mittelstufe"),
        (", Gradende", ", Endstufe"),
        (": Gradanfang", ": Anfangsstufe"),
        (": Gradmitte", ": Mittelstufe"),
        (": Gradende", ": Endstufe"),
    )
    output = text
    for old, new in replacements:
        output = output.replace(old, new)
    return re.sub(r",\s*,", ",", output)


def finish_neutral_closure(text: str) -> str:
    output = text
    for label in STAGE_LABELS.values():
        output = output.replace(
            f", {label}, abgeschlossen", f", {label} erreicht; abgeschlossen"
        )
        output = output.replace(f", {label}, fertig", f", {label} erreicht; fertig")
    return output


def spoken_render(
    old: str, modality_policy: dict[str, dict[str, str]],
    exact_policy: dict[str, tuple[str, str]],
) -> tuple[str, str, str]:
    if old in exact_policy:
        new, rule_id = exact_policy[old]
        return new, "CLAUSE_LOCAL_MULTI_STAGE", rule_id

    modalities = ordered_modalities(old, MODALITY_SOURCE)
    output = stageize(old)
    direct = False
    if len(modalities) == 1:
        code = modalities[0]
        rule = modality_policy[code]
        base, participle = rule["source_form"], rule["participle"]
        for stage_code, label in STAGE_LABELS.items():
            degree = rule[{"BEGIN": "begin_degree", "MIDDLE": "middle_degree", "END": "end_degree"}[stage_code]]
            replaced = re.sub(
                rf"(?<![\w-]){re.escape(base)}, {label}", f"{degree} {participle}", output
            )
            direct |= replaced != output
            output = replaced
            for source_adjective, ending in (
                (base + "er", "er"), (base + "es", "es"),
                (base + "e", "e"), (base + "en", "en"),
            ):
                replaced = re.sub(
                    rf"(?<![\w-]){re.escape(source_adjective)} ([^,;]+), {label}",
                    rf"{degree} {participle}{ending} \1", output,
                )
                direct |= replaced != output
                output = replaced

    output = finish_neutral_closure(output)
    if len(modalities) > 1:
        mode, rules = "MIXED_NEUTRAL_STAGE", "P05"
    elif not modalities:
        mode, rules = "NO_MODALITY_NEUTRAL_STAGE", "P06"
    elif direct:
        mode, rules = "SINGLE_DIRECT", {
            "HEISS": "P01", "KALT": "P02", "TROCKEN": "P03", "FEUCHT": "P04"
        }[modalities[0]]
    else:
        mode = "SINGLE_COMPOSITE_NEUTRAL_STAGE"
        rules = {
            "HEISS": "P01|P05", "KALT": "P02|P05",
            "TROCKEN": "P03|P05", "FEUCHT": "P04|P05",
        }[modalities[0]]
    return output, mode, rules


def build_dictionary_overlay(
    dictionary: list[dict[str, str]], modality_policy: dict[str, dict[str, str]],
    exact_policy: dict[str, tuple[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    target_rows = [row for row in dictionary if GRADE_RX.search(row["working_meaning_de"])]
    assert len(target_rows) == 175
    assert sum(int(row["occurrence_count"]) for row in target_rows) == 2431
    assert Counter(row["current_layer"] for row in target_rows) == {
        "GLOBAL_V48_DEFAULT": 162, "ACTIVE_V99_LEXICAL_CORE": 13
    }
    target_ids = {row["reading_id"] for row in target_rows}
    output: list[dict[str, str]] = []
    audit: list[dict[str, Any]] = []
    for source in dictionary:
        row = dict(source)
        if source["reading_id"] not in target_ids:
            row.update({
                "v99r5_spoken_render_de": source["working_meaning_de"],
                "v99r5_formal_stage_sequence": "NONE",
                "v99r5_workflow_closure": "NONE",
                "v99r5_modality_class": "NONE",
                "v99r5_renderer_mode": "UNCHANGED",
                "v99r5_dispatch_scope": "UNCHANGED",
                "v99r5_policy_rule_ids": "NONE",
            })
            output.append(row)
            continue

        old = source["working_meaning_de"]
        stages = stage_sequence(old)
        modalities = ordered_modalities(old, MODALITY_SOURCE)
        new, mode, policy_ids = spoken_render(old, modality_policy, exact_policy)
        assert stages and len(stages) in {1, 2}
        assert new != old and not GRADE_RX.search(new)
        assert ordered_modalities(new, MODALITY_OUTPUT) == modalities
        assert len(re.findall(r"(?<!\w)abgeschlossen(?!\w)", old, re.I)) == len(
            re.findall(r"(?<!\w)abgeschlossen(?!\w)", new, re.I)
        )
        assert len(re.findall(r"(?<!\w)fertig(?!\w)", old, re.I)) == len(
            re.findall(r"(?<!\w)fertig(?!\w)", new, re.I)
        )
        dispatch = (
            "SURFACE_GLOBAL_2401" if source["current_layer"] == "GLOBAL_V48_DEFAULT"
            else "EXACT_ACTIVE_POSITION_ONLY_30"
        )
        row.update({
            "v99r5_spoken_render_de": new,
            "v99r5_formal_stage_sequence": ">".join(stages),
            "v99r5_workflow_closure": closure_status(old),
            "v99r5_modality_class": ">".join(modalities) if modalities else "NONE",
            "v99r5_renderer_mode": mode,
            "v99r5_dispatch_scope": dispatch,
            "v99r5_policy_rule_ids": policy_ids,
        })
        output.append(row)
        audit.append({
            "audit_id": f"G732-R{len(audit)+1:03d}",
            "surface": source["surface"], "reading_id": source["reading_id"],
            "current_layer": source["current_layer"], "dispatch_scope": dispatch,
            "occurrence_count": source["occurrence_count"],
            "old_working_meaning_de": old, "new_spoken_render_de": new,
            "formal_stage_sequence": ">".join(stages),
            "source_grade_phrases": " | ".join(match.group(0) for match in STAGE_RX.finditer(old)),
            "workflow_closure": closure_status(old),
            "modality_class": ">".join(modalities) if modalities else "NONE",
            "modality_count": len(modalities), "renderer_mode": mode,
            "policy_rule_ids": policy_ids,
            "working_model_score_0_100_not_probability": source["working_model_score_0_100_not_probability"],
            "working_model_level": source["working_model_level"],
            "positive_evidence_de": source["positive_evidence_de"],
            "counterevidence_de": source["counterevidence_de"],
            "semantic_scope": source["semantic_scope"], "global_export_scope": source["global_export_scope"],
            "historical_confirmation": source["historical_confirmation"],
            "component_relation_credit": 0, "source_gdts": source["source_gdts"],
            "source_row_sha256": row_sha(source),
        })

    assert len(output) == len(dictionary) == 1586 and len(audit) == 175
    assert [row["reading_id"] for row in output] == [row["reading_id"] for row in dictionary]
    for before, after in zip(dictionary, output, strict=True):
        assert {field: after[field] for field in before} == before
    mode_rows = Counter(row["renderer_mode"] for row in audit)
    mode_occ = Counter()
    for row in audit:
        mode_occ[row["renderer_mode"]] += int(row["occurrence_count"])
    assert mode_rows == {
        "MIXED_NEUTRAL_STAGE": 82, "SINGLE_DIRECT": 71,
        "SINGLE_COMPOSITE_NEUTRAL_STAGE": 9, "NO_MODALITY_NEUTRAL_STAGE": 9,
        "CLAUSE_LOCAL_MULTI_STAGE": 4,
    }
    assert mode_occ == {
        "MIXED_NEUTRAL_STAGE": 604, "SINGLE_DIRECT": 1710,
        "SINGLE_COMPOSITE_NEUTRAL_STAGE": 21, "NO_MODALITY_NEUTRAL_STAGE": 58,
        "CLAUSE_LOCAL_MULTI_STAGE": 38,
    }
    return output, audit


def practicalize_cells(cells: list[str]) -> str:
    cleaned = [re.sub(r"\s+", " ", cell).strip(" ;") for cell in cells]
    text = "; ".join(cleaned)
    text = re.sub(r"\s+", " ", text).replace(".;", ";").replace(":;", ":")
    return re.sub(r";{2,}", ";", text).strip()


def build_position_overlay(
    lines: list[dict[str, str]], dictionary_audit: list[dict[str, Any]],
    active_contexts: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    by_id = {row["reading_id"]: row for row in dictionary_audit}
    global_by_surface = {
        row["surface"]: row for row in dictionary_audit
        if row["current_layer"] == "GLOBAL_V48_DEFAULT"
    }
    active_by_id = {
        row["reading_id"]: row for row in dictionary_audit
        if row["current_layer"] == "ACTIVE_V99_LEXICAL_CORE"
    }
    assert len(global_by_surface) == 162 and len(active_by_id) == 13
    assert not (set(global_by_surface) & {row["surface"] for row in active_by_id.values()})

    active_positions: dict[tuple[str, str, int, str], tuple[dict[str, str], dict[str, Any]]] = {}
    active_counts = Counter()
    for context in active_contexts:
        target = active_by_id.get(context["v99_reading_id"])
        if target is None:
            continue
        assert context["surface"] == target["surface"]
        assert context["v99_lexical_core_de"] == target["old_working_meaning_de"]
        assert context["v99_context_realization_de"] == target["old_working_meaning_de"]
        key = (context["page"], context["locus"], int(context["token_ordinal"]), context["surface"])
        assert key not in active_positions
        active_positions[key] = (context, target)
        active_counts[target["reading_id"]] += 1
    assert len(active_positions) == 30
    assert all(active_counts[rid] == int(row["occurrence_count"]) for rid, row in active_by_id.items())

    active_surfaces = {row["surface"] for row in active_by_id.values()}
    occurrence_rows: list[dict[str, Any]] = []
    scope_controls: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    global_counts = Counter()
    seen_active_positions: set[tuple[str, str, int, str]] = set()
    total_tokens = 0

    for line in lines:
        tokens = line["zl3b_line"].split()
        inherited = line["token_glosses_de"].split(" | ")
        assert len(tokens) == len(inherited) == int(line["token_count"]), line["locus"]
        total_tokens += len(tokens)
        before, after = list(inherited), list(inherited)
        target_ordinals: list[int] = []
        target_surfaces: list[str] = []
        target_readings: list[str] = []
        formal_tags: list[str] = []
        global_count = active_count = 0

        for ordinal, (surface, inherited_gloss) in enumerate(zip(tokens, inherited, strict=True), 1):
            target = global_by_surface.get(surface)
            context: dict[str, str] | None = None
            dispatch = "GLOBAL_SURFACE"
            active_key = (line["page"], line["locus"], ordinal, surface)
            if target is not None:
                global_counts[target["reading_id"]] += 1
                global_count += 1
            elif active_key in active_positions:
                context, target = active_positions[active_key]
                seen_active_positions.add(active_key)
                active_count += 1
                dispatch = "ACTIVE_EXACT_POSITION"
            elif surface in active_surfaces:
                scope_controls.append({
                    "control_id": f"G732-C{len(scope_controls)+1:04d}",
                    "page": line["page"], "locus": line["locus"], "token_ordinal": ordinal,
                    "surface": surface, "inherited_v48_gloss_de": inherited_gloss,
                    "licensed_target": 0,
                    "control_reason": "ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS",
                    "unchanged_in_overlay": 1,
                })
                continue
            else:
                continue

            assert target is not None
            old = context["v99_context_realization_de"] if context else target["old_working_meaning_de"]
            new = target["new_spoken_render_de"]
            before[ordinal - 1] = old
            after[ordinal - 1] = new
            target_ordinals.append(ordinal)
            target_surfaces.append(surface)
            target_readings.append(target["reading_id"])
            formal_tags.append(f"{target['formal_stage_sequence']}|{target['workflow_closure']}")
            occurrence_rows.append({
                "overlay_id": f"G732-P{len(occurrence_rows)+1:04d}",
                "page": line["page"], "locus": line["locus"], "token_ordinal": ordinal,
                "surface": surface, "reading_id": target["reading_id"],
                "current_layer": target["current_layer"], "dispatch_scope": dispatch,
                "active_position_id": context["position_id"] if context else "NONE",
                "old_v99r4_meaning_de": old, "new_v99r5_spoken_render_de": new,
                "formal_stage_sequence": target["formal_stage_sequence"],
                "workflow_closure": target["workflow_closure"],
                "modality_class": target["modality_class"], "renderer_mode": target["renderer_mode"],
                "inherited_v48_gloss_de": inherited_gloss,
                "working_model_score_0_100_not_probability": target["working_model_score_0_100_not_probability"],
                "working_model_level": target["working_model_level"],
                "positive_evidence_de": target["positive_evidence_de"],
                "counterevidence_de": target["counterevidence_de"],
                "semantic_scope": target["semantic_scope"],
                "historical_confirmation": target["historical_confirmation"],
                "component_relation_credit": 0, "token_retained": 1, "ordinal_retained": 1,
            })

        if not target_ordinals:
            continue
        comparisons.append({
            "page": line["page"], "locus": line["locus"], "section": line["section"],
            "language": line["language"], "hand": line["hand"], "token_count": line["token_count"],
            "unknown_tokens": line["unknown_tokens"], "complete_v48": int(line["unknown_tokens"] == "0"),
            "target_count": len(target_ordinals), "global_target_count": global_count,
            "active_target_count": active_count, "target_ordinals": "|".join(map(str, target_ordinals)),
            "target_surfaces": "|".join(target_surfaces), "target_reading_ids": "|".join(target_readings),
            "formal_grade_tags": " | ".join(formal_tags), "zl3b_line": line["zl3b_line"],
            "v99r4_projected_token_glosses_de": " | ".join(before),
            "v99r5_spoken_token_glosses_de": " | ".join(after),
            "v99r4_target_glosses_de": " | ".join(before[i - 1] for i in target_ordinals),
            "v99r5_spoken_target_glosses_de": " | ".join(after[i - 1] for i in target_ordinals),
            "v99r4_render_de": practicalize_cells(before),
            "v99r5_spoken_render_de": practicalize_cells(after),
            "non_target_cells_unchanged": len(tokens) - len(target_ordinals),
            "exact_tokens_and_ordinals_retained": 1,
        })

    assert total_tokens == 32339
    assert len(occurrence_rows) == 2431
    assert len(seen_active_positions) == len(active_positions) == 30
    assert len(scope_controls) == 1784
    assert sum(row["dispatch_scope"] == "GLOBAL_SURFACE" for row in occurrence_rows) == 2401
    assert sum(row["dispatch_scope"] == "ACTIVE_EXACT_POSITION" for row in occurrence_rows) == 30
    assert all(
        global_counts[rid] == int(row["occurrence_count"])
        for rid, row in by_id.items() if row["current_layer"] == "GLOBAL_V48_DEFAULT"
    )
    assert sum(int(row["non_target_cells_unchanged"]) for row in comparisons) == sum(
        int(row["token_count"]) - int(row["target_count"]) for row in comparisons
    )
    return occurrence_rows, scope_controls, comparisons


def build_class_summary(audit: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for grouping, field in (
        ("RENDERER_MODE", "renderer_mode"), ("CURRENT_LAYER", "current_layer"),
        ("MODALITY_CLASS", "modality_class"), ("STAGE_SEQUENCE", "formal_stage_sequence"),
        ("WORKFLOW_CLOSURE", "workflow_closure"),
    ):
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in audit:
            groups[str(row[field])].append(row)
        for value, rows in sorted(groups.items()):
            output.append({
                "grouping": grouping, "class": value, "reading_rows": len(rows),
                "licensed_positions": sum(int(row["occurrence_count"]) for row in rows),
                "surfaces": "|".join(row["surface"] for row in rows),
            })
    return output


def build_residual_grade_cells(
    lines: list[dict[str, str]], occurrences: list[dict[str, Any]],
    scope_controls: list[dict[str, Any]], comparisons: list[dict[str, Any]],
    dictionary: list[dict[str, str]], active_contexts: list[dict[str, str]],
) -> list[dict[str, Any]]:
    control_keys = {
        (row["page"], row["locus"], int(row["token_ordinal"]), row["surface"])
        for row in scope_controls
    }
    all_active_surfaces = {
        row["surface"] for row in dictionary
        if row["current_layer"] == "ACTIVE_V99_LEXICAL_CORE"
    }
    active_context_by_key = {
        (row["page"], row["locus"], int(row["token_ordinal"]), row["surface"]): row
        for row in active_contexts
    }
    assert len(active_context_by_key) == len(active_contexts) == 479
    target_render = {
        (row["page"], row["locus"], int(row["token_ordinal"]), row["surface"]):
        row["new_v99r5_spoken_render_de"] for row in occurrences
    }
    affected_lines = {(row["page"], row["locus"]) for row in comparisons}
    output: list[dict[str, Any]] = []
    for line in lines:
        tokens = line["zl3b_line"].split()
        inherited = line["token_glosses_de"].split(" | ")
        for ordinal, (surface, inherited_cell) in enumerate(zip(tokens, inherited, strict=True), 1):
            key = (line["page"], line["locus"], ordinal, surface)
            cell = target_render.get(key, inherited_cell)
            if not GRADE_RX.search(cell):
                continue
            if key in control_keys:
                residual_class = "TARGET_ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS"
                reason = "Eine der 13 Zieloberflächen liegt außerhalb ihrer 30 exakten V99-Positionen."
            elif key in active_context_by_key:
                residual_class = "OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL"
                reason = "Die sichtbare V48-Zelle ist an dieser exakten Position bereits durch den aktuellen V99-Kontextwert überholt."
            elif surface in all_active_surfaces:
                residual_class = "OTHER_ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE"
                reason = "Eine andere aktive V99-Oberfläche liegt außerhalb ihrer exakten V99-Positionen."
            else:
                residual_class = "LEGACY_CONTEXTUAL_ALIAS_OR_MERGE"
                reason = "Geerbte V48-Kontextzelle ist kein portabler Oberflächenwert und verlangt Einzelfallprüfung."
            output.append({
                "residual_id": f"G732-X{len(output)+1:04d}",
                "page": line["page"], "locus": line["locus"], "token_ordinal": ordinal,
                "surface": surface, "residual_gloss_de": cell,
                "residual_class": residual_class, "gdt732_rewrite_allowed": 0,
                "line_changed_by_gdt732": int((line["page"], line["locus"]) in affected_lines),
                "current_v99_position_id": active_context_by_key.get(key, {}).get("position_id", "NONE"),
                "current_v99_reading_id": active_context_by_key.get(key, {}).get("v99_reading_id", "NONE"),
                "current_v99_context_realization_de": active_context_by_key.get(key, {}).get(
                    "v99_context_realization_de", "NONE"
                ),
                "next_route_reason_de": reason,
            })
    assert len(output) == 4752
    assert Counter(row["residual_class"] for row in output) == {
        "TARGET_ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS": 1784,
        "OTHER_ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE": 2908,
        "OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL": 52,
        "LEGACY_CONTEXTUAL_ALIAS_OR_MERGE": 8,
    }
    assert sum(int(row["line_changed_by_gdt732"]) for row in output) == 2494
    assert sum(
        int(row["line_changed_by_gdt732"]) for row in output
        if row["residual_class"] == "TARGET_ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS"
    ) == 932
    return output


def build_blocker_delta(
    rules: list[dict[str, str]], dictionary: list[dict[str, str]],
    complete_overlay: list[dict[str, str]], comparisons: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    passage_before: list[tuple[str, str, str]] = []
    passage_after: list[tuple[str, str, str]] = []
    for line in comparisons:
        tokens = line["zl3b_line"].split()
        before = line["v99r4_projected_token_glosses_de"].split(" | ")
        after = line["v99r5_spoken_token_glosses_de"].split(" | ")
        for surface, old, new in zip(tokens, before, after, strict=True):
            passage_before.append((surface, old, "UNKNOWN" if UNKNOWN_RX.fullmatch(old) else "RESOLVED"))
            passage_after.append((surface, new, "UNKNOWN" if UNKNOWN_RX.fullmatch(new) else "RESOLVED"))
    for rule in rules:
        pattern = re.compile(rule["regex"], re.IGNORECASE)
        scope = rule["field_scope"]
        if scope == "working_meaning_de":
            before_rows = [row for row in dictionary if pattern.search(row["working_meaning_de"])]
            after_rows = [row for row in complete_overlay if pattern.search(row["v99r5_spoken_render_de"])]
            before_cells = [row for row in passage_before if pattern.search(row[1])]
            after_cells = [row for row in passage_after if pattern.search(row[1])]
        elif scope == "surface":
            before_rows = [row for row in dictionary if pattern.search(row["surface"])]
            after_rows = [row for row in complete_overlay if pattern.search(row["surface"])]
            before_cells = [row for row in passage_before if pattern.search(row[0])]
            after_cells = [row for row in passage_after if pattern.search(row[0])]
        elif scope == "passage_cell_status":
            before_rows, after_rows = [], []
            before_cells = [row for row in passage_before if pattern.search(row[2])]
            after_cells = [row for row in passage_after if pattern.search(row[2])]
        else:
            raise AssertionError(scope)
        output.append({
            "priority": rule["priority"], "blocker_class": rule["blocker_class"], "field_scope": scope,
            "before_dictionary_rows": len(before_rows), "after_dictionary_rows": len(after_rows),
            "before_dictionary_occurrences": sum(int(row["occurrence_count"]) for row in before_rows),
            "after_dictionary_occurrences": sum(int(row["occurrence_count"]) for row in after_rows),
            "before_affected_passage_cells": len(before_cells),
            "after_affected_passage_cells": len(after_cells),
            "interpretation_de": rule["interpretation_de"],
        })
    grade = next(row for row in output if row["blocker_class"] == "GRADE_FRAME")
    assert (grade["before_dictionary_rows"], grade["before_dictionary_occurrences"]) == (175, 2431)
    assert (grade["after_dictionary_rows"], grade["after_dictionary_occurrences"]) == (0, 0)
    for row in output:
        if row["blocker_class"] != "GRADE_FRAME":
            assert row["before_dictionary_rows"] == row["after_dictionary_rows"]
            assert row["before_dictionary_occurrences"] == row["after_dictionary_occurrences"]
            assert row["before_affected_passage_cells"] == row["after_affected_passage_cells"]
    return output


def build_quality_summary(audit: list[dict[str, Any]], occurrences: list[dict[str, Any]]) -> list[dict[str, Any]]:
    before = [row["old_v99r4_meaning_de"] for row in occurrences]
    after = [row["new_v99r5_spoken_render_de"] for row in occurrences]
    grade_before = sum(len(stage_sequence(text)) for text in before)
    grade_after = sum(len(stage_sequence(text)) for text in after)
    closure_before = sum(len(re.findall(r"(?<!\w)(?:abgeschlossen|fertig)(?!\w)", text, re.I)) for text in before)
    closure_after = sum(len(re.findall(r"(?<!\w)(?:abgeschlossen|fertig)(?!\w)", text, re.I)) for text in after)
    modality_before = sum(len(ordered_modalities(text, MODALITY_SOURCE)) for text in before)
    modality_after = sum(len(ordered_modalities(text, MODALITY_OUTPUT)) for text in after)
    direct_positions = sum(
        int(row["occurrence_count"]) for row in audit
        if row["renderer_mode"] in {"SINGLE_DIRECT", "CLAUSE_LOCAL_MULTI_STAGE"}
    )
    neutral_positions = 2431 - direct_positions
    metrics: list[tuple[str, float | int, float | int, str]] = [
        ("target_reading_rows", 175, 175, "scope census; not plaintext accuracy"),
        ("licensed_target_positions", 2431, 2431, "scope census; not plaintext accuracy"),
        ("target_audible_grade_frame_markers", grade_before, grade_after, "renderer metadata removed from 2,431 licensed target cells only"),
        ("workflow_closure_markers", closure_before, closure_after, "abgeschlossen/fertig preserved exactly"),
        ("explicit_modality_mentions", modality_before, modality_after, "heat/cold/dry/moist polarity preserved"),
        ("mean_target_words", sum(len(x.split()) for x in before) / len(before), sum(len(x.split()) for x in after) / len(after), "concision only; not readability or accuracy"),
        ("direct_participle_positions", 0, direct_positions, "single-axis or clause-local spoken states"),
        ("neutral_stage_positions", 0, neutral_positions, "mixed/composite/unspecified axes retain neutral stages"),
        ("active_surface_scope_leaks", 0, 0, "1,784 outside-scope controls remain unchanged"),
    ]
    return [{
        "metric": name, "v99r4_before": old, "v99r5_after": new,
        "delta_after_minus_before": new - old, "interpretation": interpretation,
    } for name, old, new, interpretation in metrics]


def build_parity() -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for layer, paths in (("GDT696_LOCAL_RELATIONS", G696_PARITY), ("GDT727_ACTIVE_READER", G727_PARITY)):
        for path in paths:
            count = len(read_tsv(path)) if path.suffix == ".tsv" else sum(
                line.startswith("## ") for line in path.read_text(encoding="utf-8").splitlines()
            )
            output.append({
                "source_layer": layer, "source_artifact": str(path.relative_to(ROOT)),
                "row_or_section_count": count, "sha256": file_sha(path),
                "gdt732_rewrite_count": 0, "parity_status": "BYTE_STABLE_INPUT_NOT_REWRITTEN",
            })
    assert len(output) == 8
    return output


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = [row["page"] for row in read_tsv(PAGES)]
    assert len(pages) == len(set(pages)) == 179
    assert not any(re.match(r"^f84(?:r|v|$)", page) for page in pages)
    lines = read_tsv(LINES)
    assert len(lines) == 4128 and {row["page"] for row in lines} <= set(pages)
    assert sum(int(row["token_count"]) for row in lines) == 32339
    dictionary = read_tsv(DICTIONARY)
    assert len(dictionary) == 1586
    modality_policy, exact_policy = load_policy()
    complete_overlay, audit = build_dictionary_overlay(dictionary, modality_policy, exact_policy)
    active_contexts = read_tsv(ACTIVE_CONTEXTS)
    occurrences, scope_controls, comparisons = build_position_overlay(lines, audit, active_contexts)
    dense = sorted(
        comparisons, key=lambda row: (-int(row["target_count"]), -int(row["complete_v48"]), row["locus"])
    )[:50]
    dense = [{"rank": index, **row} for index, row in enumerate(dense, 1)]
    blocker_delta = build_blocker_delta(read_tsv(BLOCKER_RULES), dictionary, complete_overlay, comparisons)
    quality = build_quality_summary(audit, occurrences)
    class_summary = build_class_summary(audit)
    residual_grade_cells = build_residual_grade_cells(
        lines, occurrences, scope_controls, comparisons, dictionary, active_contexts
    )
    residual_counts = Counter(row["residual_class"] for row in residual_grade_cells)
    residual_affected_counts = Counter(
        row["residual_class"] for row in residual_grade_cells
        if int(row["line_changed_by_gdt732"])
    )
    residual_by_locus: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for residual in residual_grade_cells:
        residual_by_locus[residual["locus"]].append(residual)
    for row in dense:
        residuals = residual_by_locus[row["locus"]]
        row["residual_grade_cell_count"] = len(residuals)
        row["residual_grade_cells_de"] = " | ".join(
            (
                f"{item['token_ordinal']}:{item['residual_gloss_de']} [{item['residual_class']}]"
                + (
                    f" => aktuelles V99: {item['current_v99_context_realization_de']}"
                    if item["current_v99_context_realization_de"] != "NONE" else ""
                )
            )
            for item in residuals
        ) or "NONE"
    parity = build_parity()

    dictionary_fields = list(dictionary[0]) + list(OVERLAY_FIELDS)
    write_tsv(ART / "V99R5_COMPLETE_SPOKEN_RENDERER.tsv", complete_overlay, dictionary_fields)
    write_tsv(ART / "V99R5_175_GRADE_FRAME_READING_AUDIT.tsv", audit)
    write_tsv(ART / "V99R5_2431_LICENSED_POSITION_OVERLAY.tsv", occurrences)
    write_tsv(ART / "V99R5_1784_ACTIVE_SURFACE_SCOPE_CONTROLS.tsv", scope_controls)
    write_tsv(ART / "V99R5_4752_RESIDUAL_CACHE_GRADE_FRAME_CELLS.tsv", residual_grade_cells)
    write_tsv(ART / f"V99R5_{len(comparisons)}_AFFECTED_LINE_COMPARISON.tsv", comparisons)
    write_tsv(ART / "V99R5_50_TARGET_DENSE_PASSAGES.tsv", dense)
    write_tsv(ART / "V99R5_RENDERER_CLASS_SUMMARY.tsv", class_summary)
    write_tsv(ART / "V99R5_BLOCKER_DELTA.tsv", blocker_delta)
    write_tsv(ART / "V99R5_RENDER_QUALITY_SUMMARY.tsv", quality)
    write_tsv(ART / "V99R5_INHERITED_ARTIFACT_PARITY.tsv", parity)

    reader = [
        "# GDT732 — 50 gradrahmendichteste Cache-Passagen", "",
        "Diese Rangliste misst nur die Zahl positionsgenau geänderter Gradrahmen. Sie ist keine Rangliste semantischer Wichtigkeit und keine Klartextübersetzung.", "",
        "Nur die 2.431 lizenzierten Zielpositionen werden geändert. Noch hörbare Gradformulierungen in der vollständigen Nachher-Zeile sind bewusst geschützte oder anderweitig geerbte V48-Zellen; GDT732 zählt sie separat.", "",
    ]
    for row in dense:
        reader.extend([
            f"## {row['rank']}. {row['locus']} ({row['target_count']} Gradrahmen)", "",
            f"Voynich: `{row['zl3b_line']}`", "", f"Formal: {row['formal_grade_tags']}", "",
            f"Zielzellen vorher: {row['v99r4_target_glosses_de']}", "",
            f"Zielzellen nachher: {row['v99r5_spoken_target_glosses_de']}", "",
            f"Außerhalb des GDT732-Zielbereichs verbliebene Gradrahmen: {row['residual_grade_cells_de']}", "",
            f"Vorher: {row['v99r4_render_de']}", "", f"Nachher: {row['v99r5_spoken_render_de']}", "",
        ])
    (ART / "GDT732_V99R5_50_TARGET_DENSE_READER.md").write_text(
        "\n".join(reader).rstrip() + "\n", encoding="utf-8"
    )

    result = {
        "experiment_id": "GDT732", "status": STATUS,
        "allowed_pages": 179, "cached_lines": 4128, "aligned_tokens": 32339,
        "complete_dictionary_rows": 1586, "target_reading_rows": 175,
        "global_target_rows": 162, "global_licensed_positions": 2401,
        "active_target_rows": 13, "active_licensed_positions": 30,
        "active_surface_raw_positions": 1814, "active_surface_scope_controls": 1784,
        "licensed_target_positions": 2431, "affected_lines": len(comparisons),
        "affected_complete_v48_lines": sum(int(row["complete_v48"]) for row in comparisons),
        "non_target_positions_unchanged": 32339 - 2431,
        "direct_spoken_rows": 75, "direct_spoken_positions": 1748,
        "neutral_stage_rows": 100, "neutral_stage_positions": 683,
        "target_audible_grade_frame_rows_after": 0,
        "target_audible_grade_frame_occurrences_after": 0,
        "residual_cache_grade_frame_cells_after": 4752,
        "residual_affected_passage_grade_frame_cells_after": 2494,
        "residual_target_active_surface_control_grade_cells": residual_counts[
            "TARGET_ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS"
        ],
        "residual_other_active_surface_grade_cells": residual_counts[
            "OTHER_ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE"
        ],
        "residual_other_active_superseded_exact_v48_grade_cells": residual_counts[
            "OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL"
        ],
        "residual_legacy_alias_merge_grade_cells": residual_counts[
            "LEGACY_CONTEXTUAL_ALIAS_OR_MERGE"
        ],
        "residual_affected_target_active_surface_control_grade_cells": residual_affected_counts[
            "TARGET_ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS"
        ],
        "residual_affected_other_active_surface_grade_cells": residual_affected_counts[
            "OTHER_ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE"
        ],
        "residual_affected_other_active_superseded_exact_v48_grade_cells": residual_affected_counts[
            "OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL"
        ],
        "residual_affected_legacy_alias_merge_grade_cells": residual_affected_counts[
            "LEGACY_CONTEXTUAL_ALIAS_OR_MERGE"
        ],
        "workflow_closure_additions": 0, "modality_additions": 0, "action_default_changes": 0,
        "score_changes": 0, "confidence_changes": 0, "evidence_changes": 0,
        "scope_changes": 0, "export_changes": 0, "component_relation_credit": 0,
        "inherited_artifacts_byte_stable": 8, "new_pages": 0,
        "semantic_dictionary_sha256": file_sha(DICTIONARY),
        "canonical_spoken_renderer": str((ART / "V99R5_COMPLETE_SPOKEN_RENDERER.tsv").relative_to(ROOT)),
        "claim_ceiling": "scope-safe spoken renderer overlay; V99R4 semantics preserved; no plaintext or new meaning",
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
