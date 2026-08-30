#!/usr/bin/env python3
"""Build the GDT673 exact-occurrence conflict scan."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt673_v48_transfer_occurrence_conflict_scan"
ART = EXP / "artifacts"
CARDS_PATH = ROOT / "experiments/yolo/gdt672_v48_concrete_page_renderer/src/F1R_TRANSFER_CARDS.tsv"
F1R_READINGS_PATH = ROOT / "experiments/yolo/gdt672_v48_concrete_page_renderer/artifacts/F1R_TOKEN_READINGS.tsv"
PANEL_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
ALLOWLIST_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/PAGE_ALLOWLIST.tsv"
DECISIONS_PATH = EXP / "src/CARD_CONTEXT_DECISIONS.tsv"
RIVALS_PATH = EXP / "src/SEMANTIC_RIVAL_DECISIONS.tsv"
READER_RIVALS_PATH = EXP / "src/READER_CONDITIONED_RIVALS.tsv"
VALUE_ATTACHMENTS_PATH = EXP / "src/PANEL_VALUE_ATTACHMENT_DECISIONS.tsv"
CROSS_PATH = Path("transcription/voynich_cross_transcription_lines.tsv")


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


def split_parallel(raw: str) -> list[str]:
    return raw.split(" | ") if raw else []


def unknown_ordinals(row: dict[str, str]) -> set[int]:
    return {int(value) for value in row["unknown_ordinals"].split("|") if value and value != "NONE"}


def joined_counter(values: list[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def position_class(ordinal: int, total: int) -> str:
    if total == 1:
        return "SINGLETON"
    if ordinal == 1:
        return "INITIAL"
    if ordinal == total:
        return "FINAL"
    return "MEDIAL"


def guarded_cross_query(allowlist: list[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(CROSS_PATH),
        "--selector", "page",
    ]
    for page in allowlist:
        command.extend(("--allow", page))
    command.extend(
        (
            "--columns", "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
            "--forbid-prefix", "f84",
        )
    )
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("guarded cross-transcription query emitted no GUARD_STATS")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    return rows, {str(key): int(value) for key, value in json.loads(match.group(1)).items()}


def align_reader_tokens(source: list[str], alternate: list[str]) -> list[tuple[str, tuple[int, ...], str]]:
    """Copy GDT671's exact-token/low-cost-boundary alignment."""
    n, m = len(source), len(alternate)
    cells: list[list[tuple[int, int, list[tuple[str, tuple[int, ...], str]]] | None]] = [
        [None] * (m + 1) for _ in range(n + 1)
    ]
    cells[0][0] = (0, 0, [])

    def offer(
        i: int, j: int, cost: int, steps: int,
        path: list[tuple[str, tuple[int, ...], str]],
        operation: tuple[str, tuple[int, ...], str],
    ) -> None:
        candidate = (cost, steps, [*path, operation])
        previous = cells[i][j]
        if previous is None or candidate[:2] < previous[:2]:
            cells[i][j] = candidate

    for i in range(n + 1):
        for j in range(m + 1):
            cell = cells[i][j]
            if cell is None:
                continue
            cost, steps, path = cell
            if i < n and j < m:
                offer(
                    i + 1, j + 1, cost + (0 if source[i] == alternate[j] else 10), steps + 1,
                    path, ("ONE", (i,), alternate[j]),
                )
            if i + 1 < n and j < m and source[i] + source[i + 1] == alternate[j]:
                offer(i + 2, j + 1, cost + 1, steps + 1, path, ("MERGE_2", (i, i + 1), alternate[j]))
            if i + 2 < n and j < m and source[i] + source[i + 1] + source[i + 2] == alternate[j]:
                offer(i + 3, j + 1, cost + 1, steps + 1, path, ("MERGE_3", (i, i + 1, i + 2), alternate[j]))
            if i < n and j + 1 < m and source[i] == alternate[j] + alternate[j + 1]:
                offer(i + 1, j + 2, cost + 1, steps + 1, path, ("SPLIT_2", (i,), source[i]))
            if i < n:
                offer(i + 1, j, cost + 10, steps + 1, path, ("DELETE", (i,), ""))
            if j < m:
                offer(i, j + 1, cost + 10, steps + 1, path, ("INSERT", (), alternate[j]))
    final = cells[n][m]
    if final is None:
        raise RuntimeError("reader token alignment unexpectedly has no path")
    return final[2]


def reader_operations(source: list[str], alternate: list[str]) -> dict[int, tuple[str, str]]:
    result: dict[int, tuple[str, str]] = {}
    for operation, indices, rendered in align_reader_tokens(source, alternate):
        for index in indices:
            label = "EXACT" if operation == "ONE" and rendered == source[index] else operation
            result[index] = (label, rendered or "EMPTY")
    if set(result) != set(range(len(source))):
        raise RuntimeError("reader alignment did not cover every ZL3b source position")
    return result


def occurrence_scope_decision(
    surface: str, target_gloss: str, line_position: str,
    right_surface: str, right_gloss: str,
) -> tuple[str, str]:
    if surface == "y":
        allowed = {"hierzu:", "; hierzu:", "Eintrag abgeschlossen", "Eintragsteil abgeschlossen", "Labelschluss"}
        if target_gloss in allowed:
            return "O_HOLD_COMPATIBLE", "Y_ALLOWED_REFERENCE_OR_LEFT_CLOSE"
        return "O_NAMED_CONTEXT_CONFLICT", "Y_ENTRY_OR_LABEL_OUTSIDE_CARD"
    if surface == "s":
        if target_gloss == "[Beschriftungszeichen]":
            return "O_HOLD_COMPATIBLE", "S_SIGLUM_COMPATIBLE"
        return "O_NAMED_CONTEXT_CONFLICT", "S_SEED_MATERIAL_NOT_SIGLUM"
    if surface == "d":
        if right_surface == "or":
            return "O_HOLD_COMPATIBLE", "D_RIGHT_OR_READER_BINDING_VISIBLE"
        if target_gloss == "Dosis":
            return "O_NAMED_CONTEXT_CONFLICT", "D_FREE_DOSE_NOT_SUFFIX_CLOSE"
        return "O_UNTESTABLE_LOCAL_BINDING", "D_FREE_QUANTITY_SIGN_NOT_ACTION"
    if surface == "r":
        if right_gloss in {"Trockenfraktion I", "trockene Fraktion I"}:
            return "O_HOLD_COMPATIBLE", "R_FOLLOWING_DRY_FRACTION_VISIBLE"
        return "O_UNTESTABLE_LOCAL_BINDING", "R_LOCAL_BINDING_CONDITION_ABSENT"
    if surface == "ok":
        if right_surface == "chey":
            return "O_HOLD_COMPATIBLE", "OK_CHEY_CONDITION_VISIBLE"
        return "O_UNTESTABLE_LOCAL_BINDING", "OK_LOCAL_LEFT_OF_CHEY_CONDITION_ABSENT"
    raise RuntimeError(f"unexpected occurrence-scoped surface: {surface}")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(CARDS_PATH)
    f1r_readings = read_tsv(F1R_READINGS_PATH)
    panel = read_tsv(PANEL_PATH)
    allow_rows = read_tsv(ALLOWLIST_PATH)
    decision_rows = read_tsv(DECISIONS_PATH)
    rival_rows = read_tsv(RIVALS_PATH)
    reader_rival_rows = read_tsv(READER_RIVALS_PATH)
    value_attachment_rows = read_tsv(VALUE_ATTACHMENTS_PATH)

    assert len(cards) == 80
    assert len({row["surface"] for row in cards}) == 80
    assert Counter(row["class"] for row in cards) == {"P": 53, "W": 22, "O": 5}
    assert len(f1r_readings) == 214
    assert len(panel) == 4128
    allowlist = [row["page"] for row in allow_rows]
    assert len(allowlist) == len(set(allowlist)) == 179
    assert set(row["page"] for row in panel) == set(allowlist)
    assert "f1r" not in allowlist
    assert all(not page.lower().startswith("f84") for page in allowlist)
    cross_rows, cross_guard = guarded_cross_query(allowlist)
    assert cross_guard["selected"] == len(cross_rows)
    assert cross_guard["skipped_forbidden"] > 0
    assert all(row["page"] in allowlist and not row["page"].lower().startswith("f84") for row in cross_rows)
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    assert len(cross_by_locus) == len(cross_rows)
    assert all(row["locus"] in cross_by_locus for row in panel)

    card_by_surface = {row["surface"]: row for row in cards}
    decisions = {row["surface"]: row for row in decision_rows}
    assert len(decisions) == len(decision_rows)
    allowed_decisions = {"HOLD_SAME_CARD", "NAMED_CONTEXT_CONFLICT"}
    assert all(row["decision"] in allowed_decisions for row in decision_rows)
    assert len(rival_rows) == 3 and {row["surface"] for row in rival_rows} == {"shoaiin", "ytain", "yto"}
    assert len(reader_rival_rows) == 3 and {row["surface"] for row in reader_rival_rows} == {"sory", "kod", "daraiin"}
    assert len(value_attachment_rows) == 20 and len({(row["locus"], row["head_ordinal"], row["value_ordinal"]) for row in value_attachment_rows}) == 20

    f1r_counts = Counter(row["eva"] for row in f1r_readings if row["eva"] in card_by_surface)
    occurrence_rows: list[dict[str, object]] = []
    occurrences_by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)

    for line in panel:
        tokens = line["zl3b_line"].split()
        glosses = split_parallel(line["token_glosses_de"])
        sources = split_parallel(line["gloss_sources"])
        states = split_parallel(line["scope_states"])
        assert len(tokens) == int(line["token_count"])
        assert len(tokens) == len(glosses) == len(sources) == len(states)
        cross = cross_by_locus[line["locus"]]
        assert cross["zl3b_clean"].split() == tokens
        if any(surface in card_by_surface for surface in tokens):
            assert cross["it2a_clean"] and cross["rf1b_clean"]
            it2a_ops = reader_operations(tokens, cross["it2a_clean"].split())
            rf1b_ops = reader_operations(tokens, cross["rf1b_clean"].split())
        else:
            it2a_ops = rf1b_ops = {}
        unknown = unknown_ordinals(line)
        for index, surface in enumerate(tokens, start=1):
            card = card_by_surface.get(surface)
            if card is None:
                continue
            card_class = card["class"]
            pos_class = position_class(index, len(tokens))
            right_surface = tokens[index] if index < len(tokens) else "BOUNDARY"
            right_gloss = glosses[index] if index < len(tokens) else "BOUNDARY"
            if card_class == "O":
                decision, reason_code = occurrence_scope_decision(
                    surface, glosses[index - 1], pos_class, right_surface, right_gloss,
                )
                note = reason_code
                promotable = "0"
            else:
                audited = decisions.get(surface)
                if audited is None:
                    decision = "MISSING_MANUAL_AUDIT"
                    note = "No manual panel-context decision supplied."
                    promotable = "0"
                else:
                    decision = audited["decision"]
                    note = audited["review_note"]
                    promotable = "1" if decision == "HOLD_SAME_CARD" else "0"
                reason_code = "P_OR_W_MANUAL_CONTEXT_AUDIT"
            it2a_operation, it2a_render = it2a_ops[index - 1]
            rf1b_operation, rf1b_render = rf1b_ops[index - 1]
            reader_support = (
                "BOTH_EXACT" if it2a_operation == rf1b_operation == "EXACT"
                else "ONE_EXACT" if "EXACT" in {it2a_operation, rf1b_operation}
                else "NEITHER_EXACT"
            )
            item = {
                "surface": surface,
                "card_class": card_class,
                "composition": card["composition"],
                "working_meaning_de": card["working_meaning_de"],
                "confidence": card["confidence"],
                "page": line["page"],
                "locus": line["locus"],
                "section": line["section"],
                "language": line["language"],
                "hand": line["hand"],
                "ordinal": index,
                "line_token_count": len(tokens),
                "line_position": pos_class,
                "was_v48_unknown": "1" if index in unknown else "0",
                "target_v48_gloss_de": glosses[index - 1],
                "target_v48_source": sources[index - 1],
                "target_v48_scope_state": states[index - 1],
                "left_surface": tokens[index - 2] if index > 1 else "BOUNDARY",
                "left_gloss_de": glosses[index - 2] if index > 1 else "BOUNDARY",
                "right_surface": right_surface,
                "right_gloss_de": right_gloss,
                "it2a_operation": it2a_operation,
                "it2a_render": it2a_render,
                "rf1b_operation": rf1b_operation,
                "rf1b_render": rf1b_render,
                "reader_support": reader_support,
                "zl3b_line": line["zl3b_line"],
                "decision": decision,
                "reason_code": reason_code,
                "promotable": promotable,
                "review_note": note,
            }
            occurrence_rows.append(item)
            occurrences_by_surface[surface].append(item)

    present_transferable = {
        surface
        for surface, rows in occurrences_by_surface.items()
        if card_by_surface[surface]["class"] in {"P", "W"} and rows
    }
    assert set(decisions) == present_transferable
    assert all(
        row["was_v48_unknown"] == "1"
        for row in occurrence_rows if row["card_class"] in {"P", "W"}
    )

    profile_rows: list[dict[str, object]] = []
    promoted_surfaces: set[str] = set()
    for card in cards:
        surface = card["surface"]
        hits = occurrences_by_surface.get(surface, [])
        if card["class"] == "O":
            hit_decisions = Counter(str(row["decision"]) for row in hits)
            if not hits:
                decision = "UNTESTABLE"
            elif hit_decisions["O_NAMED_CONTEXT_CONFLICT"]:
                decision = "NAMED_CONTEXT_CONFLICT"
            elif hit_decisions["O_HOLD_COMPATIBLE"]:
                decision = "HOLD_OCCURRENCE_SCOPED"
            else:
                decision = "UNTESTABLE"
            review_note = "Free occurrence-scoped surface; classify each occurrence and never export by spelling alone."
        elif not hits:
            decision = "UNTESTABLE"
            review_note = "No exact occurrence in the admitted 179-side panel."
        else:
            decision = decisions[surface]["decision"]
            review_note = decisions[surface]["review_note"]
            if decision == "HOLD_SAME_CARD":
                promoted_surfaces.add(surface)
        profile_rows.append(
            {
                "surface": surface,
                "f1r_card_class": card["class"],
                "composition": card["composition"],
                "working_meaning_de": card["working_meaning_de"],
                "confidence": card["confidence"],
                "f1r_positions": f1r_counts[surface],
                "panel_positions": len(hits),
                "panel_lines": len({str(row["locus"]) for row in hits}),
                "panel_pages": len({str(row["page"]) for row in hits}),
                "sections": joined_counter([str(row["section"]) for row in hits]),
                "languages": joined_counter([str(row["language"]) for row in hits]),
                "hands": joined_counter([str(row["hand"]) for row in hits]),
                "position_profile": joined_counter([str(row["line_position"]) for row in hits]),
                "first_loci": "|".join(str(row["locus"]) for row in hits[:8]) or "NONE",
                "decision": decision,
                "promote_to_v49_overlay": "1" if surface in promoted_surfaces else "0",
                "hold_occurrences": sum(str(row["decision"]) in {"HOLD_SAME_CARD", "O_HOLD_COMPATIBLE"} for row in hits),
                "conflict_occurrences": sum(row["decision"] == "O_NAMED_CONTEXT_CONFLICT" for row in hits),
                "untestable_occurrences": sum(row["decision"] == "O_UNTESTABLE_LOCAL_BINDING" for row in hits),
                "reader_exact_both": sum(row["reader_support"] == "BOTH_EXACT" for row in hits),
                "reader_exact_one": sum(row["reader_support"] == "ONE_EXACT" for row in hits),
                "reader_exact_neither": sum(row["reader_support"] == "NEITHER_EXACT" for row in hits),
                "review_note": review_note,
            }
        )

    touched_rows: list[dict[str, object]] = []
    newly_closed_rows: list[dict[str, object]] = []
    overlay_positions = 0
    line_metrics = Counter()
    for line in panel:
        tokens = line["zl3b_line"].split()
        glosses = split_parallel(line["token_glosses_de"])
        unknown = unknown_ordinals(line)
        applied = [index for index in sorted(unknown) if tokens[index - 1] in promoted_surfaces]
        remaining = [index for index in sorted(unknown) if index not in applied]
        before = len(unknown)
        after = len(remaining)
        line_metrics["all_lines"] += 1
        line_metrics["complete_before"] += before == 0
        line_metrics["complete_after"] += after == 0
        line_metrics["one_unknown_before"] += before == 1
        line_metrics["one_unknown_after"] += after == 1
        if len(tokens) > 1:
            line_metrics["multi_lines"] += 1
            line_metrics["multi_complete_before"] += before == 0
            line_metrics["multi_complete_after"] += after == 0
            line_metrics["multi_one_unknown_before"] += before == 1
            line_metrics["multi_one_unknown_after"] += after == 1
        if not applied:
            continue
        overlay_positions += len(applied)
        rendered = list(glosses)
        for index in applied:
            rendered[index - 1] = card_by_surface[tokens[index - 1]]["working_meaning_de"]
        touched = {
            "page": line["page"],
            "locus": line["locus"],
            "section": line["section"],
            "language": line["language"],
            "hand": line["hand"],
            "zl3b_line": line["zl3b_line"],
            "unknown_before": before,
            "applied_ordinals": "|".join(map(str, applied)),
            "applied_surfaces": "|".join(tokens[index - 1] for index in applied),
            "unknown_after": after,
            "remaining_unknown_ordinals": "|".join(map(str, remaining)) or "NONE",
            "remaining_unknown_surfaces": "|".join(tokens[index - 1] for index in remaining) or "NONE",
            "overlay_glosses_de": " | ".join(rendered),
        }
        touched_rows.append(touched)
        if before > 0 and after == 0:
            newly_closed_rows.append(touched)

    promoted_rows = [
        {
            "surface": row["surface"],
            "working_meaning_de": row["working_meaning_de"],
            "composition": row["composition"],
            "source": "GDT673:GDT672_EXACT_PANEL_TRANSFER" if row["class"] == "P" else "GDT673:GDT672_LEARNED_WHOLE_TRANSFER",
            "strength": row["confidence"],
            "scope_state": "ROLE_COMPOSED_EXACT_TRANSFER" if row["class"] == "P" else "LEARNED_EXACT_WHOLE_TRANSFER",
            "panel_positions": len(occurrences_by_surface[row["surface"]]),
            "panel_pages": len({str(hit["page"]) for hit in occurrences_by_surface[row["surface"]]}),
        }
        for row in cards
        if row["surface"] in promoted_surfaces
    ]

    o_reasons = Counter(
        (str(row["surface"]), str(row["reason_code"]))
        for row in occurrence_rows if row["card_class"] == "O"
    )
    o_rule_specs = [
        ("y", "target_v48_gloss in allowed reference/left-close set", "O_HOLD_COMPATIBLE", "Y_ALLOWED_REFERENCE_OR_LEFT_CLOSE"),
        ("y", "target_v48_gloss is entry or label function", "O_NAMED_CONTEXT_CONFLICT", "Y_ENTRY_OR_LABEL_OUTSIDE_CARD"),
        ("s", "target_v48_gloss=[Beschriftungszeichen]", "O_HOLD_COMPATIBLE", "S_SIGLUM_COMPATIBLE"),
        ("s", "target_v48_gloss=Samen-/Saatgutposten", "O_NAMED_CONTEXT_CONFLICT", "S_SEED_MATERIAL_NOT_SIGLUM"),
        ("d", "right1_surface=or", "O_HOLD_COMPATIBLE", "D_RIGHT_OR_READER_BINDING_VISIBLE"),
        ("d", "target_v48_gloss=Dosis and right1_surface!=or", "O_NAMED_CONTEXT_CONFLICT", "D_FREE_DOSE_NOT_SUFFIX_CLOSE"),
        ("d", "target_v48_gloss=[Dosis-/Maßzeichen] and right1_surface!=or", "O_UNTESTABLE_LOCAL_BINDING", "D_FREE_QUANTITY_SIGN_NOT_ACTION"),
        ("r", "right1_v48_gloss is a dry fraction", "O_HOLD_COMPATIBLE", "R_FOLLOWING_DRY_FRACTION_VISIBLE"),
        ("r", "otherwise", "O_UNTESTABLE_LOCAL_BINDING", "R_LOCAL_BINDING_CONDITION_ABSENT"),
        ("ok", "right1_surface=chey", "O_HOLD_COMPATIBLE", "OK_CHEY_CONDITION_VISIBLE"),
        ("ok", "right1_surface!=chey", "O_UNTESTABLE_LOCAL_BINDING", "OK_LOCAL_LEFT_OF_CHEY_CONDITION_ABSENT"),
    ]
    o_rule_rows = [
        {
            "surface": surface,
            "occurrence_predicate": predicate,
            "occurrences": o_reasons[(surface, reason)],
            "decision": decision,
            "reason_code": reason,
        }
        for surface, predicate, decision, reason in o_rule_specs
    ]
    correction_rows = [
        {
            "locus": "f1r.7", "ordinal": 6, "surface": "s",
            "old_gdt672_meaning_de": "Species- oder Chargensiglum",
            "v49_contextual_meaning_de": "Samen-/Saatgutposten",
            "decision": "REVISE_F1R_OCCURRENCE",
            "evidence": "264/272 panel s positions are seed/material; the eight sigla are singleton label tokens, unlike f1r.7.",
        },
        {
            "locus": "f1r.13", "ordinal": 9, "surface": "d",
            "old_gdt672_meaning_de": "abschließen?",
            "v49_contextual_meaning_de": "Dosis-/Maßzeichen?",
            "decision": "REVISE_F1R_OCCURRENCE",
            "evidence": "47/53 panel d positions read Dosis and six read a quantity sign; naked d is never a suffix-close card.",
        },
        {
            "locus": "f1r.16", "ordinal": 6, "surface": "d",
            "old_gdt672_meaning_de": "eine Portion abmessen",
            "v49_contextual_meaning_de": "eine Portion abmessen",
            "decision": "RETAIN_LOCAL_READER_JOIN",
            "evidence": "The bilateral d+or→dor join is visible at f1r.16; no separated d+or occurs in the panel.",
        },
    ]
    panel_by_locus = {row["locus"]: row for row in panel}
    for attachment in value_attachment_rows:
        tokens = panel_by_locus[attachment["locus"]]["zl3b_line"].split()
        head = int(attachment["head_ordinal"])
        value = int(attachment["value_ordinal"])
        assert abs(head - value) == 1
        assert tokens[head - 1] == attachment["head_surface"]
        assert tokens[value - 1] == attachment["value_surface"]
    previous_reference_locus = {"f114r.34": "f114r.33", "f37v.23": "f37v.22"}
    reference_warning_rows = [
        {
            "surface": row["surface"], "locus": row["locus"], "ordinal": row["ordinal"],
            "zl3b_line": row["zl3b_line"], "working_meaning_de": row["working_meaning_de"],
            "previous_locus": previous_reference_locus[str(row["locus"])],
            "previous_zl3b_line": panel_by_locus[previous_reference_locus[str(row["locus"])]] ["zl3b_line"],
            "contextual_requirement": "CROSS_LINE_ANTECEDENT_VISIBLE",
        }
        for row in occurrence_rows
        if row["surface"] in {"ytain", "yto"} and row["line_position"] == "INITIAL"
    ]

    occurrence_fields = [
        "surface", "card_class", "composition", "working_meaning_de", "confidence", "page", "locus",
        "section", "language", "hand", "ordinal", "line_token_count", "line_position", "was_v48_unknown",
        "target_v48_gloss_de", "target_v48_source", "target_v48_scope_state", "left_surface", "left_gloss_de",
        "right_surface", "right_gloss_de", "it2a_operation", "it2a_render", "rf1b_operation", "rf1b_render",
        "reader_support", "zl3b_line", "decision", "reason_code", "promotable", "review_note",
    ]
    profile_fields = [
        "surface", "f1r_card_class", "composition", "working_meaning_de", "confidence", "f1r_positions",
        "panel_positions", "panel_lines", "panel_pages", "sections", "languages", "hands", "position_profile",
        "first_loci", "decision", "promote_to_v49_overlay", "hold_occurrences", "conflict_occurrences",
        "untestable_occurrences", "reader_exact_both", "reader_exact_one", "reader_exact_neither", "review_note",
    ]
    touched_fields = [
        "page", "locus", "section", "language", "hand", "zl3b_line", "unknown_before", "applied_ordinals",
        "applied_surfaces", "unknown_after", "remaining_unknown_ordinals", "remaining_unknown_surfaces",
        "overlay_glosses_de",
    ]
    write_tsv(ART / "CARD_PANEL_TRANSFER_PROFILE.tsv", profile_rows, profile_fields)
    write_tsv(ART / "EXACT_OCCURRENCE_CONTEXTS.tsv", occurrence_rows, occurrence_fields)
    write_tsv(
        ART / "TRANSFERABLE_EXACT_OCCURRENCES.tsv",
        [row for row in occurrence_rows if row["promotable"] == "1"],
        occurrence_fields,
    )
    write_tsv(
        ART / "OCCURRENCE_SCOPED_BLOCKS.tsv",
        [row for row in occurrence_rows if row["card_class"] == "O"],
        occurrence_fields,
    )
    write_tsv(ART / "TOUCHED_LINE_OVERLAY.tsv", touched_rows, touched_fields)
    write_tsv(ART / "NEWLY_CLOSED_LINES.tsv", newly_closed_rows, touched_fields)
    write_tsv(
        ART / "V49_PANEL_TRANSFER_OVERLAY.tsv",
        promoted_rows,
        ["surface", "working_meaning_de", "composition", "source", "strength", "scope_state", "panel_positions", "panel_pages"],
    )
    write_tsv(
        ART / "O_CONTEXT_RULES.tsv", o_rule_rows,
        ["surface", "occurrence_predicate", "occurrences", "decision", "reason_code"],
    )
    write_tsv(
        ART / "CONTEXT_CONFLICTS.tsv",
        [row for row in occurrence_rows if row["decision"] == "O_NAMED_CONTEXT_CONFLICT"],
        occurrence_fields,
    )
    write_tsv(
        ART / "F1R_OCCURRENCE_CARD_CORRECTIONS.tsv", correction_rows,
        ["locus", "ordinal", "surface", "old_gdt672_meaning_de", "v49_contextual_meaning_de", "decision", "evidence"],
    )
    write_tsv(
        ART / "REFERENCE_SCOPE_WARNINGS.tsv", reference_warning_rows,
        ["surface", "locus", "ordinal", "zl3b_line", "working_meaning_de", "previous_locus", "previous_zl3b_line", "contextual_requirement"],
    )
    write_tsv(
        ART / "SEMANTIC_RIVAL_AUDIT.tsv", rival_rows,
        ["surface", "loci", "current_meaning_de", "rival_or_warning_de", "decision", "evidence"],
    )
    write_tsv(
        ART / "READER_CONDITIONED_RIVALS.tsv", reader_rival_rows,
        ["surface", "locus", "zl3b_form", "it2a_form", "rf1b_form", "zl3b_working_meaning_de", "reader_conditioned_rival_de", "decision", "note"],
    )
    write_tsv(
        ART / "PANEL_VALUE_ATTACHMENT_AUDIT.tsv", value_attachment_rows,
        ["locus", "head_ordinal", "value_ordinal", "head_surface", "value_surface", "direction", "binding_kind", "contextual_render_de", "decision", "note"],
    )

    class_positions = Counter(str(row["card_class"]) for row in occurrence_rows)
    decisions_count = Counter(row["decision"] for row in profile_rows)
    named_conflicts = decisions_count["NAMED_CONTEXT_CONFLICT"]
    occurrence_decisions = Counter(str(row["decision"]) for row in occurrence_rows)
    reader_support = Counter(str(row["reader_support"]) for row in occurrence_rows)
    hold_positions = occurrence_decisions["HOLD_SAME_CARD"] + occurrence_decisions["O_HOLD_COMPATIBLE"]
    conflict_positions = occurrence_decisions["O_NAMED_CONTEXT_CONFLICT"]
    untestable_positions = occurrence_decisions["O_UNTESTABLE_LOCAL_BINDING"]
    assert class_positions == {"P": 155, "W": 7, "O": 732}
    assert decisions_count == {"HOLD_SAME_CARD": 39, "NAMED_CONTEXT_CONFLICT": 3, "HOLD_OCCURRENCE_SCOPED": 1, "UNTESTABLE": 37}
    assert (hold_positions, conflict_positions, untestable_positions) == (373, 381, 140)
    assert reader_support == {"BOTH_EXACT": 432, "ONE_EXACT": 261, "NEITHER_EXACT": 201}
    assert len(reference_warning_rows) == 2 and len(newly_closed_rows) == 6
    assert len(cross_rows) == 4137 and sum(int(row["token_count"]) for row in panel) == 32339
    status = f"PASS_{overlay_positions}_PW_TRANSFER_POSITIONS__{len(promoted_surfaces)}_CARDS_HOLD__3_O_CARDS_SPLIT__2_F1R_CORRECTIONS"
    result = {
        "status": status,
        "basis": {
            "panel_pages": len(allowlist),
            "panel_lines": len(panel),
            "panel_tokens": sum(int(row["token_count"]) for row in panel),
            "cross_transcription_lines_selected": len(cross_rows),
            "cross_guard": cross_guard,
            "f1r_outside_panel": True,
            "f84": "FORBIDDEN",
            "f84r": "FORBIDDEN",
        },
        "cards": {
            "gdt672_transfer_cards": len(cards),
            "panel_present_surfaces": sum(bool(occurrences_by_surface.get(row["surface"])) for row in cards),
            "panel_absent_surfaces": sum(not occurrences_by_surface.get(row["surface"]) for row in cards),
            "applied_exact_transfer_surfaces": len(promoted_surfaces),
            "applied_role_composed_surfaces": sum(row["class"] == "P" and row["surface"] in promoted_surfaces for row in cards),
            "retained_learned_whole_surfaces": sum(row["class"] == "W" and row["surface"] in promoted_surfaces for row in cards),
            "card_status_hold": decisions_count["HOLD_SAME_CARD"] + decisions_count["HOLD_OCCURRENCE_SCOPED"],
            "named_context_conflict_surfaces": named_conflicts,
            "card_status_untestable": decisions_count["UNTESTABLE"],
            "occurrence_scoped_surfaces": sum(row["class"] == "O" for row in cards),
        },
        "occurrences": {
            "all_exact_card_positions": len(occurrence_rows),
            "applied_exact_transfer_positions": overlay_positions,
            "occurrence_scoped_blocked_positions": class_positions["O"],
            "decision_hold_positions": hold_positions,
            "decision_conflict_positions": conflict_positions,
            "decision_untestable_positions": untestable_positions,
            "reader_exact_both": reader_support["BOTH_EXACT"],
            "reader_exact_one": reader_support["ONE_EXACT"],
            "reader_exact_neither": reader_support["NEITHER_EXACT"],
            "applied_touched_lines": len(touched_rows),
            "applied_touched_pages": len({row["page"] for row in touched_rows}),
            "sections": dict(sorted(Counter(str(row["section"]) for row in occurrence_rows if row["promotable"] == "1").items())),
            "languages": dict(sorted(Counter(str(row["language"]) for row in occurrence_rows if row["promotable"] == "1").items())),
            "hands": dict(sorted(Counter(str(row["hand"]) for row in occurrence_rows if row["promotable"] == "1").items())),
        },
        "coverage_overlay": {
            "unknown_positions_before": sum(int(row["unknown_tokens"]) for row in panel),
            "unknown_positions_after": sum(int(row["unknown_tokens"]) for row in panel) - overlay_positions,
            "complete_lines_before": line_metrics["complete_before"],
            "complete_lines_after": line_metrics["complete_after"],
            "multi_token_complete_before": line_metrics["multi_complete_before"],
            "multi_token_complete_after": line_metrics["multi_complete_after"],
            "multi_token_one_unknown_before": line_metrics["multi_one_unknown_before"],
            "multi_token_one_unknown_after": line_metrics["multi_one_unknown_after"],
            "newly_closed_lines": len(newly_closed_rows),
        },
        "corrections": {
            "f1r_occurrence_revisions": 2,
            "f1r_local_reader_joins_retained": 1,
            "cross_line_reference_bindings": len(reference_warning_rows),
            "semantic_rivals_retained_visible": 1,
            "reader_conditioned_rivals": len(reader_rival_rows),
            "material_value_bindings": sum(row["decision"] == "BIND" for row in value_attachment_rows),
            "open_process_value_candidates": sum(row["decision"] == "DIRECTION_OPEN" for row in value_attachment_rows),
        },
        "files": {},
        "claim_ceiling": (
            "An exact-spelling exploratory transfer overlay on the already admitted V48 panel. "
            "It preserves GDT672 card meanings where no named contextual contradiction was found; "
            "it does not confirm plaintext, language, lexemes, substances, procedures, or manuscript-wide semantics."
        ),
    }
    for path in sorted(ART.glob("*.tsv")):
        result["files"][path.name] = sha256(path)
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "cards": result["cards"], "occurrences": result["occurrences"], "coverage_overlay": result["coverage_overlay"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
