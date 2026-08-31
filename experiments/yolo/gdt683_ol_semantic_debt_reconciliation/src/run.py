#!/usr/bin/env python3
"""Build the GDT683 OL-card reconciliation and V57 reader."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation"
ART = EXP / "artifacts"
PANEL_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
GLOSSARY_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/V48_WORKING_TOKEN_GLOSSARY.tsv"
STEM_PATH = ROOT / "experiments/yolo/gdt664_one_hundred_forty_residual_family_completion/artifacts/STEM_MODEL_V41.tsv"
V56_PATH = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/V56_51_LINE_READER.tsv"
V56_RESULT_PATH = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/RESULT.json"
CROSS_PATH = Path("transcription/voynich_cross_transcription_lines.tsv")
V56_SPEC_PATH = EXP / "src/V56_OL_DEBT_SPECS.tsv"
N_SPEC_PATH = EXP / "src/N_BOUNDARY_OVERRIDE_SPECS.tsv"

LEGACY_GLOSS = "Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz"
GENERIC = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|"
    r"Arbeitsstelle|Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|"
    r"Arbeitsschritt|Stationsansatz|Stationsposten|Stationswert|Stationsanteil|"
    r"Stationseinheit|work item|working material|worksite|work cycle|source vessel|"
    r"destination place|destination vessel)\b",
    re.IGNORECASE,
)

# Narrow reader corrections discovered while auditing the six V57 lines.  They
# are deliberately keyed by locus and token ordinal so no prose repair can
# drift onto another line.
V57_ALIGNED_CORRECTIONS = {
    ("f80r.17", 13): "eine Teilmenge abmessen",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_glosses(raw: str) -> list[str]:
    return raw.split(" | ") if raw else []


def position_class(ordinal: int, token_count: int) -> str:
    if token_count == 1:
        return "SINGLETON"
    if ordinal == 1:
        return "BOS"
    if ordinal == token_count:
        return "EOS"
    return "MEDIAL"


def guarded_cross_query(loci: list[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(CROSS_PATH), "--selector", "locus"]
    for locus in loci:
        command.extend(("--allow", locus))
    command.extend(
        (
            "--columns",
            "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
            "--forbid-prefix",
            "f84",
        )
    )
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("guarded cross-transcription query emitted no GUARD_STATS")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    return rows, {str(key): int(value) for key, value in json.loads(match.group(1)).items()}


def edit_distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, 1):
        current = [left_index]
        for right_index, right_char in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[right_index] + 1,
                previous[right_index - 1] + (left_char != right_char),
            ))
        previous = current
    return previous[-1]


def align_reader_tokens(source: list[str], alternate: list[str]) -> list[tuple[str, tuple[int, ...], str]]:
    """Character-cost alignment with exact-OL tie-breaking and fuzzy joins."""
    n, m = len(source), len(alternate)
    cells: list[list[tuple[tuple[int, int, int, int, int, int, int], list[tuple[str, tuple[int, ...], str]]] | None]] = [
        [None] * (m + 1) for _ in range(n + 1)
    ]
    cells[0][0] = ((0, 0, 0, 0, 0, 0, 0), [])

    def offer(
        i: int,
        j: int,
        score: tuple[int, int, int, int, int, int, int],
        path: list[tuple[str, tuple[int, ...], str]],
        operation: tuple[str, tuple[int, ...], str],
        delta: tuple[int, int, int, int, int, int, int],
    ) -> None:
        candidate_score = tuple(left + right for left, right in zip(score, delta))
        candidate = (candidate_score, [*path, operation])
        previous = cells[i][j]
        if previous is None or candidate_score < previous[0]:
            cells[i][j] = candidate

    def fuzzy_join_allowed(left: str, right: str, distance: int) -> bool:
        longest = max(len(left), len(right))
        return distance <= max(1, longest // 3) and abs(len(left) - len(right)) <= 2

    for i in range(n + 1):
        for j in range(m + 1):
            cell = cells[i][j]
            if cell is None:
                continue
            score, path = cell
            if i < n and j < m:
                left, right = source[i], alternate[j]
                distance = edit_distance(left, right)
                exact = left == right
                offer(
                    i + 1, j + 1, score, path, ("ONE", (i,), right),
                    (distance, -int(exact and left == "ol"), -int(exact), 0, 0, 0 if exact else 3, 1),
                )
            for width in (2, 3):
                if i + width <= n and j < m:
                    indices = tuple(range(i, i + width))
                    left, right = "".join(source[index] for index in indices), alternate[j]
                    distance = edit_distance(left, right)
                    if fuzzy_join_allowed(left, right, distance):
                        label = f"MERGE_{width}" if distance == 0 else f"FUZZY_MERGE_{width}"
                        offer(
                            i + width, j + 1, score, path, (label, indices, right),
                            (distance, 0, 0, 0, int(distance > 0), 1 if distance == 0 else 2, 1),
                        )
                if i < n and j + width <= m:
                    left, right = source[i], "".join(alternate[j:j + width])
                    distance = edit_distance(left, right)
                    if fuzzy_join_allowed(left, right, distance):
                        label = f"SPLIT_{width}" if distance == 0 else f"FUZZY_SPLIT_{width}"
                        offer(
                            i + 1, j + width, score, path, (label, (i,), "|".join(alternate[j:j + width])),
                            (distance, 0, 0, 0, int(distance > 0), 1 if distance == 0 else 2, 1),
                        )
            if i + 2 <= n and j + 2 <= m:
                left_block = "".join(source[i:i + 2])
                right_block = "".join(alternate[j:j + 2])
                block_distance = edit_distance(left_block, right_block)
                paired_distance = edit_distance(source[i], alternate[j]) + edit_distance(source[i + 1], alternate[j + 1])
                if block_distance < paired_distance and fuzzy_join_allowed(left_block, right_block, block_distance):
                    offer(
                        i + 2, j + 2, score, path,
                        ("RESEG_2_2", (i, i + 1), "|".join(alternate[j:j + 2])),
                        (block_distance, 0, 0, 0, 1, 2, 1),
                    )
            if i < n:
                offer(i + 1, j, score, path, ("DELETE", (i,), ""), (len(source[i]), 0, 0, len(source[i]), 0, 4, 1))
            if j < m:
                offer(i, j + 1, score, path, ("INSERT", (), alternate[j]), (len(alternate[j]), 0, 0, len(alternate[j]), 0, 4, 1))
    final = cells[n][m]
    if final is None:
        raise RuntimeError("reader token alignment unexpectedly has no path")
    return final[1]


def reader_operations(source: list[str], alternate: list[str]) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    for operation, indices, rendered in align_reader_tokens(source, alternate):
        source_span = "|".join(source[index] for index in indices)
        for index in indices:
            label = "EXACT" if operation == "ONE" and rendered == source[index] else operation
            result[index] = {
                "operation": label,
                "render": rendered or "EMPTY",
                "source_span": source_span,
                "span_ordinals": "|".join(str(value + 1) for value in indices),
            }
    if set(result) != set(range(len(source))):
        raise RuntimeError("reader alignment did not cover every ZL3b source position")
    return result


def reader_support(it_op: str, rf_op: str) -> str:
    if it_op == rf_op == "EXACT":
        return "BOTH_EXACT"
    if it_op == "EXACT":
        return "IT2A_ONLY_EXACT"
    if rf_op == "EXACT":
        return "RF1B_ONLY_EXACT"
    return "NEITHER_EXACT"


def is_boundary(operation: str) -> bool:
    return "MERGE_" in operation or "SPLIT_" in operation or operation == "RESEG_2_2"


def locate_target_span(tokens: list[str], pattern_raw: str, target_index: int) -> tuple[int, int]:
    pattern = pattern_raw.split("|")
    matches = [
        (start, start + len(pattern) - 1)
        for start in range(len(tokens) - len(pattern) + 1)
        if tokens[start:start + len(pattern)] == pattern and start <= target_index < start + len(pattern)
    ]
    if len(matches) != 1:
        raise RuntimeError(f"target span {pattern_raw} is not unique around ordinal {target_index + 1}")
    return matches[0]


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    panel = read_tsv(PANEL_PATH)
    v56 = read_tsv(V56_PATH)
    v56_result = json.loads(V56_RESULT_PATH.read_text(encoding="utf-8"))
    v56_specs = read_tsv(V56_SPEC_PATH)
    n_specs = read_tsv(N_SPEC_PATH)
    stem_rows = read_tsv(STEM_PATH)
    glossary = read_tsv(GLOSSARY_PATH)
    glossary_by_surface = {row["surface"]: row for row in glossary}

    stem = next(row for row in stem_rows if row["stem"] == "ol" and row["structural_role"] == "LEARNED_OL_BASE")
    glossary_ol = next(row for row in glossary if row["surface"] == "ol")
    assert stem["practical_default_de"] == "Grundansatz"
    assert stem["scope"] == "exaktes nacktes Ganzwort"
    assert glossary_ol["working_meaning_de"] == LEGACY_GLOSS

    source_rows: list[dict[str, str]] = []
    occurrence_count = 0
    for row in panel:
        tokens = row["zl3b_line"].split()
        glosses = split_glosses(row["token_glosses_de"])
        if len(tokens) != len(glosses):
            raise RuntimeError(f"panel token/gloss mismatch at {row['locus']}")
        count = tokens.count("ol")
        if count:
            source_rows.append(row)
            occurrence_count += count
    loci = sorted(row["locus"] for row in source_rows)
    assert len(panel) == 4128
    assert occurrence_count == 463
    assert len(source_rows) == len(loci) == 417
    assert len({row["page"] for row in source_rows}) == 108
    assert all(not row["page"].lower().startswith("f84") for row in source_rows)

    cross_rows, cross_guard = guarded_cross_query(loci)
    assert len(cross_rows) == 417
    assert cross_guard["selected"] == 417
    assert cross_guard["skipped_forbidden"] == 98
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    assert set(cross_by_locus) == set(loci)

    n_spec_by_locus = {row["locus"]: row for row in n_specs}
    assert len(n_spec_by_locus) == len(n_specs) == 25
    occurrence_rows: list[dict[str, object]] = []
    line_rows: list[dict[str, object]] = []
    adjacent_rows: list[dict[str, object]] = []
    support_counts: Counter[str] = Counter()
    operation_counts: dict[str, Counter[str]] = {"IT2A": Counter(), "RF1B": Counter()}
    n_loci: set[str] = set()
    occurrence_id = 0

    for panel_row in source_rows:
        locus = panel_row["locus"]
        cross = cross_by_locus[locus]
        tokens = panel_row["zl3b_line"].split()
        if cross["zl3b_clean"].split() != tokens:
            raise RuntimeError(f"guarded ZL3b line drift at {locus}")
        old_glosses = split_glosses(panel_row["token_glosses_de"])
        token_dispatch_glosses = old_glosses.copy()
        it_ops = reader_operations(tokens, cross["it2a_clean"].split())
        rf_ops = reader_operations(tokens, cross["rf1b_clean"].split())
        line_occurrences: list[dict[str, object]] = []
        for index, token in enumerate(tokens):
            if token != "ol":
                continue
            occurrence_id += 1
            ordinal = index + 1
            old_gloss = old_glosses[index]
            if old_gloss != LEGACY_GLOSS:
                raise RuntimeError(f"unexpected inherited OL gloss at {locus}#{ordinal}: {old_gloss}")
            it, rf = it_ops[index], rf_ops[index]
            support = reader_support(it["operation"], rf["operation"])
            support_counts[support] += 1
            operation_counts["IT2A"][it["operation"]] += 1
            operation_counts["RF1B"][rf["operation"]] += 1
            if support == "NEITHER_EXACT":
                n_loci.add(locus)
                spec = n_spec_by_locus.get(locus)
                if spec is None:
                    raise RuntimeError(f"missing N-boundary specification for {locus}")
                working = spec["working_render_de"]
                decision = spec["boundary_class"]
                export_policy = spec["export_policy"]
                rationale = spec["rationale"]
                evidence_type = spec["evidence_type"]
                composition = spec["composition"]
                unresolved_component = spec["unresolved_component"]
                reader_scope = spec["reader_scope"]
                render_span_tokens = spec["render_span_tokens"]
                reader_rival_surface = f"IT2A:{it['render']}|RF1B:{rf['render']}"
                reader_rival_de = working
                reader_rival_source = evidence_type
            else:
                working = "Grundansatz"
                decision = "BILATERAL_PORTABLE_OL_BASE" if support == "BOTH_EXACT" else "MAJORITY_OL_BASE_WITH_READER_RIVAL"
                export_policy = "BILATERAL_EXACT_WHOLE" if support == "BOTH_EXACT" else "MAJORITY_DEFAULT__NOT_ALL_READERS"
                rationale = "GDT664s publizierte LEARNED_OL_BASE-Karte wird aus dem Praxis-/Stammkanal in den Tokenrenderer übernommen."
                evidence_type = "GDT664_PUBLISHED_LEARNED_WHOLE"
                composition = "OL_BASE"
                unresolved_component = "NONE"
                render_span_tokens = "ol"
                if support == "BOTH_EXACT":
                    reader_scope = "BILATERAL_EXACT"
                    reader_rival_surface = "NONE"
                    reader_rival_de = "NONE"
                    reader_rival_source = "NONE"
                else:
                    rival_reader, rival = ("RF1B", rf) if support == "IT2A_ONLY_EXACT" else ("IT2A", it)
                    reader_scope = f"ZL3B_PLUS_ONE_EXACT__{rival_reader}_RIVAL"
                    reader_rival_surface = f"{rival_reader}:{rival['render']}"
                    known_rival = glossary_by_surface.get(rival["render"])
                    if known_rival is not None:
                        if known_rival["working_meaning_de"] == LEGACY_GLOSS:
                            reader_rival_de = f"Leserform {rival['render']}; lokale Bedeutung offen"
                            reader_rival_source = "UNRESOLVED_READER_FORM__STALE_META_CARD_EXCLUDED"
                        else:
                            reader_rival_de = known_rival["working_meaning_de"]
                            reader_rival_source = known_rival["source"]
                    elif "|" in rival["render"]:
                        rival_parts = rival["render"].split("|")
                        part_cards = [glossary_by_surface.get(part) for part in rival_parts]
                        rendered_parts = [
                            card["working_meaning_de"]
                            if card is not None and card["working_meaning_de"] != LEGACY_GLOSS
                            else f"Leserform {part}; Bedeutung offen"
                            for part, card in zip(rival_parts, part_cards)
                        ]
                        reader_rival_de = " | ".join(rendered_parts)
                        reader_rival_source = "READER_SPLIT_COMPONENT_CARDS"
                    elif rival["operation"] == "DELETE":
                        reader_rival_de = "Auslassung im Alternativleser"
                        reader_rival_source = "READER_DELETION"
                    else:
                        reader_rival_de = f"Leserform {rival['render']}; lokale Bedeutung offen"
                        reader_rival_source = "UNRESOLVED_READER_FORM"
            token_dispatch_glosses[index] = working
            occurrence = {
                "occurrence_id": f"G683-OL-{occurrence_id:04d}",
                "page": panel_row["page"],
                "locus": locus,
                "section": panel_row["section"],
                "language": panel_row["language"],
                "hand": panel_row["hand"],
                "ordinal": ordinal,
                "token_count": len(tokens),
                "position": position_class(ordinal, len(tokens)),
                "previous_token": tokens[index - 1] if index else "BOS",
                "next_token": tokens[index + 1] if index + 1 < len(tokens) else "EOS",
                "old_structural_meta_gloss": old_gloss,
                "working_translation_de": working,
                "semantic_decision": decision,
                "export_policy": export_policy,
                "evidence_type": evidence_type,
                "composition": composition,
                "unresolved_component": unresolved_component,
                "reader_scope": reader_scope,
                "render_span_tokens": render_span_tokens,
                "reader_rival_surface": reader_rival_surface,
                "reader_rival_de": reader_rival_de,
                "reader_rival_source": reader_rival_source,
                "it2a_operation": it["operation"],
                "it2a_render": it["render"],
                "it2a_source_span": it["source_span"],
                "it2a_span_ordinals": it["span_ordinals"],
                "rf1b_operation": rf["operation"],
                "rf1b_render": rf["render"],
                "rf1b_source_span": rf["source_span"],
                "rf1b_span_ordinals": rf["span_ordinals"],
                "reader_support": support,
                "boundary_active": int(is_boundary(it["operation"]) or is_boundary(rf["operation"])),
                "render_once": int(support == "NEITHER_EXACT"),
                "rationale": rationale,
                "zl3b_line": cross["zl3b_clean"],
                "it2a_line": cross["it2a_clean"],
                "rf1b_line": cross["rf1b_clean"],
            }
            occurrence_rows.append(occurrence)
            line_occurrences.append(occurrence)
        span_by_start: dict[int, tuple[int, str]] = {}
        claimed_span_positions: set[int] = set()
        for occurrence in line_occurrences:
            target_index = int(occurrence["ordinal"]) - 1
            start, end = locate_target_span(tokens, str(occurrence["render_span_tokens"]), target_index)
            if any(index in claimed_span_positions for index in range(start, end + 1)):
                raise RuntimeError(f"overlapping OL render spans at {locus}")
            claimed_span_positions.update(range(start, end + 1))
            span_by_start[start] = (end, str(occurrence["working_translation_de"]))
        span_source_groups: list[str] = []
        span_renderings: list[str] = []
        index = 0
        while index < len(tokens):
            if index in span_by_start:
                end, rendering = span_by_start[index]
                span_source_groups.append("+".join(tokens[index:end + 1]))
                span_renderings.append(rendering)
                index = end + 1
            else:
                span_source_groups.append(tokens[index])
                span_renderings.append(old_glosses[index])
                index += 1
        ol_indices = [index for index, token in enumerate(tokens) if token == "ol"]
        for left, right in zip(ol_indices, ol_indices[1:]):
            if right == left + 1:
                adjacent_rows.append({
                    "page": panel_row["page"], "locus": locus,
                    "left_ordinal": left + 1, "right_ordinal": right + 1,
                    "working_render_de": "zwei getrennte Grundansatz-Einträge",
                    "nominal_scope_render_de": "zwei getrennte Grundansatz-Einträge",
                    "action_scope_render_de": "Grundansatz in zwei Zugaben" if locus == "f81r.5" else "NONE",
                    "selected_scope": "ACTION_ADDITION" if locus == "f81r.5" else "NOMINAL_REGISTER",
                    "rule": "REPEAT_SAME_PORTABLE_CARD__CONTEXT_SELECTS_ENTRY_OR_ADDITION__DO_NOT_INVENT_SECOND_LEXEME_OR_MEASURE",
                    "zl3b_line": panel_row["zl3b_line"],
                })
        line_rows.append({
            "page": panel_row["page"], "locus": locus, "section": panel_row["section"],
            "language": panel_row["language"], "hand": panel_row["hand"],
            "token_count": len(tokens), "ol_count": len(line_occurrences),
            "ol_ordinals": "|".join(str(row["ordinal"]) for row in line_occurrences),
            "semantic_decisions": "|".join(str(row["semantic_decision"]) for row in line_occurrences),
            "reader_support": "|".join(str(row["reader_support"]) for row in line_occurrences),
            "all_three_present": cross["all_three_present"],
            "all_present_exact": cross["all_present_exact"],
            "zl3b_line": cross["zl3b_clean"], "it2a_line": cross["it2a_clean"], "rf1b_line": cross["rf1b_clean"],
            "original_token_glosses_de": panel_row["token_glosses_de"],
            "token_debt_dispatch_de": " | ".join(token_dispatch_glosses),
            "span_aware_source_groups": " | ".join(span_source_groups),
            "span_aware_render_de": " · ".join(span_renderings),
            "span_aware_segment_count": len(span_source_groups),
            "collapsed_source_positions": len(tokens) - len(span_source_groups),
            "old_target_legacy_positions": sum(old_glosses[index] == LEGACY_GLOSS for index in ol_indices),
            "new_target_legacy_positions": sum(token_dispatch_glosses[index] == LEGACY_GLOSS for index in ol_indices),
            "unrelated_legacy_positions": sum(
                gloss == LEGACY_GLOSS and tokens[index] != "ol"
                for index, gloss in enumerate(token_dispatch_glosses)
            ),
        })

    assert occurrence_id == 463
    assert support_counts == {"BOTH_EXACT": 374, "IT2A_ONLY_EXACT": 35, "RF1B_ONLY_EXACT": 29, "NEITHER_EXACT": 25}
    assert n_loci == set(n_spec_by_locus)
    boundary_active_count = sum(int(row["boundary_active"]) for row in occurrence_rows)
    n_boundary_count = sum(row["reader_support"] == "NEITHER_EXACT" and int(row["boundary_active"]) for row in occurrence_rows)
    n_glyph_count = sum(row["reader_support"] == "NEITHER_EXACT" and not int(row["boundary_active"]) for row in occurrence_rows)
    assert boundary_active_count == 63
    assert n_boundary_count == 23
    assert n_glyph_count == 2
    assert Counter(row["semantic_decision"] for row in occurrence_rows) == {
        "BILATERAL_PORTABLE_OL_BASE": 374,
        "MAJORITY_OL_BASE_WITH_READER_RIVAL": 64,
        "BOUND_OL_MATERIAL_COMPONENT": 19,
        "LOCAL_MATERIAL_READER_CONFLICT": 5,
        "LOCAL_OLY_ACTION_CONFLICT": 1,
    }
    assert Counter(row["section"] for row in occurrence_rows) == {"B": 193, "S": 117, "H": 85, "T": 42, "P": 22, "C": 4}
    assert Counter(row["position"] for row in occurrence_rows) == {"MEDIAL": 390, "EOS": 42, "BOS": 31}
    assert len(adjacent_rows) == 7
    assert sum(int(row["old_target_legacy_positions"]) for row in line_rows) == 463
    assert sum(int(row["new_target_legacy_positions"]) for row in line_rows) == 0
    assert sum(int(row["unrelated_legacy_positions"]) for row in line_rows) == 1
    assert all(row["reader_rival_surface"] != "NONE" for row in occurrence_rows if row["semantic_decision"] == "MAJORITY_OL_BASE_WITH_READER_RIVAL")
    assert all(row["reader_rival_de"] != "NONE" for row in occurrence_rows if row["semantic_decision"] == "MAJORITY_OL_BASE_WITH_READER_RIVAL")
    assert all(row["evidence_type"] and row["composition"] and row["reader_scope"] for row in occurrence_rows)
    line_by_locus = {row["locus"]: row for row in line_rows}
    for occurrence in occurrence_rows:
        if occurrence["reader_support"] != "NEITHER_EXACT":
            continue
        line = line_by_locus[str(occurrence["locus"])]
        groups = str(line["span_aware_source_groups"]).split(" | ")
        renderings = str(line["span_aware_render_de"]).split(" · ")
        expected_group = str(occurrence["render_span_tokens"]).replace("|", "+")
        assert groups.count(expected_group) == 1
        assert renderings[groups.index(expected_group)] == occurrence["working_translation_de"]

    v56_spec_by_locus = {row["locus"]: row for row in v56_specs}
    assert len(v56_spec_by_locus) == len(v56_specs) == 6
    occurrence_by_key = {(str(row["locus"]), int(row["ordinal"])): row for row in occurrence_rows}
    v57_rows: list[dict[str, object]] = []
    debt_rows: list[dict[str, object]] = []
    for old_row in v56:
        row: dict[str, object] = dict(old_row)
        spec = v56_spec_by_locus.get(old_row["locus"])
        row["v57_semantic_revisions"] = 0
        row["v57_bound_compounds"] = 0
        row["v57_ol_decision"] = "NONE"
        row["v57_reader_support"] = "NONE"
        if spec is not None:
            tokens = old_row["zl3b_line"].split()
            literals = split_glosses(old_row["literal_token_glosses_de"])
            aligned = old_row["aligned_line_de"].split(" · ")
            ordinal = int(spec["ordinal"])
            index = ordinal - 1
            assert tokens[index] == "ol"
            assert literals[index] == LEGACY_GLOSS
            if len(aligned) != len(tokens):
                raise RuntimeError(f"V56 aligned token drift at {old_row['locus']}")
            literals[index] = spec["ol_gloss_de"]
            aligned[index] = spec["aligned_ol_chunk_de"]
            if spec["previous_token_override_de"] != "NONE":
                literals[index - 1] = spec["previous_token_override_de"]
                aligned[index - 1] = spec["aligned_previous_chunk_override_de"]
            for (correction_locus, correction_ordinal), corrected_gloss in V57_ALIGNED_CORRECTIONS.items():
                if old_row["locus"] == correction_locus:
                    aligned[correction_ordinal - 1] = corrected_gloss
            occurrence = occurrence_by_key[(old_row["locus"], ordinal)]
            row["literal_token_glosses_de"] = " | ".join(literals)
            row["aligned_line_de"] = " · ".join(aligned)
            row["practical_translation_de"] = spec["practical_translation_de"]
            row["review_note"] = f"{old_row['review_note']} GDT683: {spec['rationale']} Rival: {spec['strongest_rival_de']}."
            row["v57_semantic_revisions"] = 1
            row["v57_bound_compounds"] = int(spec["render_mode"] == "MERGE_WITH_PREVIOUS")
            row["v57_ol_decision"] = spec["decision"]
            row["v57_reader_support"] = occurrence["reader_support"]
            debt_rows.append({
                "page": old_row["page"], "locus": old_row["locus"], "ordinal": ordinal,
                "decision": spec["decision"], "render_mode": spec["render_mode"],
                "reader_support": occurrence["reader_support"],
                "before_literal_token_glosses_de": old_row["literal_token_glosses_de"],
                "after_literal_token_glosses_de": row["literal_token_glosses_de"],
                "before_aligned_line_de": old_row["aligned_line_de"],
                "after_aligned_line_de": row["aligned_line_de"],
                "before_practical_translation_de": old_row["practical_translation_de"],
                "after_practical_translation_de": row["practical_translation_de"],
                "rationale": spec["rationale"], "strongest_rival_de": spec["strongest_rival_de"],
            })
        v57_rows.append(row)

    assert len(v57_rows) == 51
    assert sum(int(row["v57_semantic_revisions"]) for row in v57_rows) == 6
    assert sum(int(row["v57_bound_compounds"]) for row in v57_rows) == 1
    assert all(LEGACY_GLOSS not in str(row["literal_token_glosses_de"]) for row in v57_rows)
    assert all("Ansatz/Gut" not in str(row["aligned_line_de"]) for row in v57_rows)
    assert all("Ansatz/Gut" not in str(row["practical_translation_de"]) for row in v57_rows)
    assert all(not GENERIC.search(str(row["practical_translation_de"])) for row in v57_rows)
    assert sum(int(row["residual_unknown_positions"]) for row in v57_rows) == 0
    assert sum(int(row["action_positions"]) for row in v57_rows) == 86
    f115 = next(row for row in v57_rows if row["locus"] == "f115r.1")
    f115_literals = split_glosses(str(f115["literal_token_glosses_de"]))
    f115_aligned = str(f115["aligned_line_de"]).split(" · ")
    assert f115_literals[4:6] == ["bis zur Mittelstufe getrocknet", "Pulverstoff"]
    assert f115_aligned[4:6] == ["bis zur Mittelstufe getrocknet", "Pulverstoff"]

    card_rows = [
        {
            "layer": "STRUCTURAL_META_GLOSS", "surface_or_class": "ol",
            "value_de": LEGACY_GLOSS, "scope": "inherited V13 structural label",
            "status": "RETAIN_AS_STRUCTURAL_HISTORY__DO_NOT_RENDER_AS_PLAINTEXT",
            "provenance": glossary_ol["source"],
        },
        {
            "layer": "BILATERAL_WORKING_TRANSLATION", "surface_or_class": "ol",
            "value_de": "Grundansatz", "scope": "374 positions with exact ol in both alternate readers",
            "status": "BILATERAL_PORTABLE_REPLACEABLE_DEFAULT",
            "provenance": "GDT664:STEM_MODEL_V41:LEARNED_OL_BASE",
        },
        {
            "layer": "MAJORITY_WORKING_TRANSLATION", "surface_or_class": "ol",
            "value_de": "Grundansatz", "scope": "64 positions with exact ol in exactly one alternate reader",
            "status": "MAJORITY_DEFAULT_WITH_EXPLICIT_READER_RIVAL__NOT_ALL_READERS",
            "provenance": "GDT664 card plus GDT683 reader-rival audit",
        },
        {
            "layer": "BOUNDARY_RENDERER", "surface_or_class": "19 N-bound material positions",
            "value_de": "explicit local compound meaning", "scope": "reader-joined local surface only",
            "status": "LOCAL_COMPOUND_ONLY",
            "provenance": "GDT683:N_BOUNDARY_OVERRIDE_SPECS",
        },
        {
            "layer": "LOCAL_RIVAL_RENDERER", "surface_or_class": "5 material conflicts + 1 oly action",
            "value_de": "explicit reader-specific rival", "scope": "local locus only",
            "status": "NO_OL_EXPORT",
            "provenance": "GDT683:N_BOUNDARY_OVERRIDE_SPECS",
        },
    ]

    occurrence_fields = list(occurrence_rows[0].keys())
    line_fields = list(line_rows[0].keys())
    v57_fields = [*v56[0].keys(), "v57_semantic_revisions", "v57_bound_compounds", "v57_ol_decision", "v57_reader_support"]
    debt_fields = list(debt_rows[0].keys())
    write_tsv(output_dir / "OL_CARD_RECONCILIATION.tsv", card_rows, list(card_rows[0].keys()))
    write_tsv(output_dir / "OL_463_OCCURRENCE_AUDIT.tsv", occurrence_rows, occurrence_fields)
    write_tsv(output_dir / "OL_417_LINE_RERENDER.tsv", line_rows, line_fields)
    write_tsv(output_dir / "N25_BOUNDARY_DECISIONS.tsv", [row for row in occurrence_rows if row["reader_support"] == "NEITHER_EXACT"], occurrence_fields)
    write_tsv(output_dir / "ADJACENT_OL_PAIRS.tsv", adjacent_rows, list(adjacent_rows[0].keys()))
    write_tsv(output_dir / "V57_SIX_OL_DEBT_REVISIONS.tsv", debt_rows, debt_fields)
    write_tsv(output_dir / "V57_51_LINE_READER.tsv", v57_rows, v57_fields)

    reader_doc = [
        "# GDT683 — six OL debt revisions in V57",
        "",
        "Four positions inherit the bilateral free whole-word card `ol = Grundansatz`; f80r.17 retains the same card only as a one-reader majority default with an explicit RF1b rival. At f115r.1 both alternate readers bind the source boundary into `cheopol...`, so the local powder compound is rendered once.",
        "",
    ]
    for row in debt_rows:
        reader_doc.extend(
            [
                f"## {row['locus']}#{row['ordinal']} · {row['decision']}",
                "",
                f"**Praxislesung:** {row['after_practical_translation_de']}",
                "",
                f"**Tokenparallel:** {row['after_aligned_line_de']}",
                "",
                f"**Grenze:** {row['reader_support']} · {row['render_mode']}",
                "",
                f"**Rivale:** {row['strongest_rival_de']}",
                "",
            ]
        )
    (output_dir / "GDT683_V57_PRACTICAL_READER.md").write_text("\n".join(reader_doc).rstrip() + "\n", encoding="utf-8")

    result: dict[str, object] = {
        "status": "PASS_374_BILATERAL_OL_BASE__64_MAJORITY_WITH_RIVAL__25_OVERRIDES__V57_ZERO_OL_DEBT",
        "basis": {
            "panel_lines": len(panel), "ol_positions": 463, "ol_loci": 417,
            "ol_pages": 108, "new_pages_opened": 0, "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "cross_guard": cross_guard,
        },
        "provenance_reconciliation": {
            "published_practical_card": "GDT664 LEARNED_OL_BASE = Grundansatz",
            "stale_renderer_row": f"GDT664/V48 glossary retained: {LEGACY_GLOSS}",
            "diagnosis": "integration omission between practical stem model and inherited token glossary",
        },
        "reader_support": dict(sorted(support_counts.items())),
        "reader_operations": {reader: dict(sorted(counts.items())) for reader, counts in operation_counts.items()},
        "semantic_dispatch": dict(sorted(Counter(str(row["semantic_decision"]) for row in occurrence_rows).items())),
        "boundary": {
            "active_positions": sum(int(row["boundary_active"]) for row in occurrence_rows),
            "neither_exact_positions": len(n_loci),
            "neither_exact_boundary_positions": n_boundary_count,
            "neither_exact_form_conflicts": n_glyph_count,
            "adjacent_ol_pairs": len(adjacent_rows),
        },
        "distribution": {
            "section": dict(sorted(Counter(str(row["section"]) for row in occurrence_rows).items())),
            "position": dict(sorted(Counter(str(row["position"]) for row in occurrence_rows).items())),
        },
        "v57_reader": {
            "lines": len(v57_rows), "tokens": sum(int(row["token_count"]) for row in v57_rows),
            "semantic_revisions": 6, "free_ol_base_revisions": 5,
            "bilateral_free_ol_base_revisions": 4, "majority_free_ol_base_revisions": 1,
            "bound_compound_revisions": 1,
            "legacy_generic_positions_before": v56_result["v56_reader"]["legacy_generic_token_positions"],
            "legacy_generic_positions_after": 0,
            "legacy_generic_practical_lines_before": len(v56_result["v56_reader"]["legacy_generic_practical_lines"]),
            "legacy_generic_practical_lines_after": 0,
            "unknown_positions_before": 0, "unknown_positions_after": 0,
            "action_positions_before": 86, "action_positions_after": 86,
        },
        "claim_ceiling": (
            "All 463 admitted exact whitespace-delimited ZL3b ol positions now have an explicit concrete working dispatch: "
            "374 use GDT664's published replaceable Grundansatz card with bilateral exact reader support; another 64 use it only as a majority default with an explicit reader rival; "
            "19 use a local bound-material renderer, five preserve concrete reader-specific material rivals, and one uses the local oly=abseihen action rival. "
            "Grundansatz is not exported into the 25 neither-exact cases, whose source spans are rendered once. "
            "V57 removes the six inherited generic OL renderer debts, with four bilateral free Grundansatz readings, one majority Grundansatz default with an explicit RF1b rival, and one cheopol powder compound. "
            "No unknown count, action count, page scope, confirmed plaintext, phonetic value, plant, disease, carrier liquid or historical codebook identity is added."
        ),
        "files": {},
    }
    artifact_names = [
        "OL_CARD_RECONCILIATION.tsv", "OL_463_OCCURRENCE_AUDIT.tsv", "OL_417_LINE_RERENDER.tsv",
        "N25_BOUNDARY_DECISIONS.tsv", "ADJACENT_OL_PAIRS.tsv", "V57_SIX_OL_DEBT_REVISIONS.tsv",
        "V57_51_LINE_READER.tsv", "GDT683_V57_PRACTICAL_READER.md",
    ]
    result["files"] = {name: sha256(output_dir / name) for name in artifact_names}
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    build(ART)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
