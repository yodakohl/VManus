#!/usr/bin/env python3
"""Build the GDT678 34-card occurrence circuit and V52 reader."""

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
EXP = ROOT / "experiments/yolo/gdt678_seventeen_two_hole_family_completion"
ART = EXP / "artifacts"
PANEL_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
GDT673_OCCURRENCES_PATH = ROOT / "experiments/yolo/gdt673_v48_transfer_occurrence_conflict_scan/artifacts/TRANSFERABLE_EXACT_OCCURRENCES.tsv"
GDT674_TOKENS_PATH = ROOT / "experiments/yolo/gdt674_v49_f81r_concrete_renderer/artifacts/F81R_TOKEN_READINGS.tsv"
GDT675_OCCURRENCES_PATH = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan/artifacts/EXTERNAL_TRANSFERABLE_OCCURRENCES.tsv"
GDT677_OCCURRENCES_PATH = ROOT / "experiments/yolo/gdt677_nine_one_hole_family_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv"
GDT677_RESULT_PATH = ROOT / "experiments/yolo/gdt677_nine_one_hole_family_completion/artifacts/RESULT.json"
V51_READER_PATH = ROOT / "experiments/yolo/gdt677_nine_one_hole_family_completion/artifacts/V51_51_LINE_READER.tsv"
CROSS_PATH = Path("transcription/voynich_cross_transcription_lines.tsv")
CARD_PATH = EXP / "src/TARGET_CARD_SPECS.tsv"
SOURCE_LINE_PATH = EXP / "src/SOURCE_LINE_SPECS.tsv"
BOUNDARY_PATH = EXP / "src/BOUNDARY_DECISION_SPECS.tsv"
ANALOG_PATH = EXP / "src/HISTORICAL_ANALOG_SPECS.tsv"

UNKNOWN_LITERAL = re.compile(r"^\[([^:\]]+):\?\]$")
HARD_GENERIC = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|"
    r"Arbeitsstelle|Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|"
    r"Arbeitsschritt|Stationsansatz|Stationsposten|Stationswert|Stationsanteil|"
    r"Stationseinheit|Aktiver Posten|laufender Eintrag|work item|working material|"
    r"worksite|work cycle|source vessel|destination place|destination vessel)\b",
    re.IGNORECASE,
)


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


def split_pipe(raw: str) -> list[str]:
    return [] if raw == "NONE" else raw.split("|")


def parse_ordinals(raw: str) -> list[int]:
    return [] if raw == "NONE" else [int(value) for value in raw.split("|")]


def unknown_chunk(gloss: str) -> str:
    match = UNKNOWN_LITERAL.fullmatch(gloss)
    return f"⟦{match.group(1)}:?⟧" if match else gloss


def position_class(ordinal: int, token_count: int) -> str:
    if token_count == 1:
        return "SINGLETON"
    if ordinal == 1:
        return "INITIAL"
    if ordinal == token_count:
        return "FINAL"
    return "MEDIAL"


def guarded_cross_query(loci: list[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(CROSS_PATH),
        "--selector", "locus",
    ]
    for locus in loci:
        command.extend(("--allow", locus))
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
    """Use exact tokens first and low-cost boundary joins/splits second."""
    n, m = len(source), len(alternate)
    cells: list[list[tuple[int, int, list[tuple[str, tuple[int, ...], str]]] | None]] = [
        [None] * (m + 1) for _ in range(n + 1)
    ]
    cells[0][0] = (0, 0, [])

    def offer(
        i: int,
        j: int,
        cost: int,
        steps: int,
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
                    i + 1,
                    j + 1,
                    cost + (0 if source[i] == alternate[j] else 10),
                    steps + 1,
                    path,
                    ("ONE", (i,), alternate[j]),
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


def reader_support(it2a_operation: str, rf1b_operation: str) -> str:
    if it2a_operation == rf1b_operation == "EXACT":
        return "BOTH_EXACT"
    if it2a_operation == "EXACT":
        return "IT2A_ONLY_EXACT"
    if rf1b_operation == "EXACT":
        return "RF1B_ONLY_EXACT"
    return "NEITHER_EXACT"


def current_line_glosses(
    line: dict[str, str], overlay: dict[tuple[str, int], tuple[str, str]]
) -> list[str]:
    tokens = line["zl3b_line"].split()
    glosses = split_parallel(line["token_glosses_de"])
    assert len(tokens) == len(glosses) == int(line["token_count"])
    result = list(glosses)
    for ordinal in range(1, len(tokens) + 1):
        replacement = overlay.get((line["locus"], ordinal))
        if replacement:
            result[ordinal - 1] = replacement[0]
    return result


def apply_boundary_render(
    tokens: list[str], chunks: list[str], ordinal: int, surface: str, rule: str
) -> tuple[str, str]:
    index = ordinal - 1
    neighbor_override = "NONE"
    if rule == "JOIN_RIGHT_KNOWN_WHOLE" and surface == "keo":
        assert index + 1 < len(tokens) and tokens[index + 1] == "r"
        chunks[index] = "heiße"
        chunks[index + 1] = "Drogenportion"
        neighbor_override = f"{ordinal + 1}:r=Drogenportion"
    elif rule == "JOIN_LEFT_KNOWN_COMPONENT" and surface == "karchees":
        assert index > 0 and tokens[index - 1] == "l"
        chunks[index - 1] = "erste heiße Holzfraktion"
        chunks[index] = "vollständig getrocknet"
        neighbor_override = f"{ordinal - 1}:l=erste heiße Holzfraktion"
    return chunks[index], neighbor_override


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(CARD_PATH)
    source_specs = read_tsv(SOURCE_LINE_PATH)
    boundary_specs = read_tsv(BOUNDARY_PATH)
    analog_specs = read_tsv(ANALOG_PATH)
    panel = read_tsv(PANEL_PATH)
    gdt673 = read_tsv(GDT673_OCCURRENCES_PATH)
    gdt674 = read_tsv(GDT674_TOKENS_PATH)
    gdt675 = read_tsv(GDT675_OCCURRENCES_PATH)
    gdt677_occurrences = read_tsv(GDT677_OCCURRENCES_PATH)
    gdt677_result = json.loads(GDT677_RESULT_PATH.read_text(encoding="utf-8"))
    v51_lines = read_tsv(V51_READER_PATH)

    assert len(cards) == 34
    assert len({row["surface"] for row in cards}) == 34
    assert len(source_specs) == 17
    assert len({row["locus"] for row in source_specs}) == 17
    assert len(boundary_specs) == 12
    assert len({(row["locus"], int(row["ordinal"])) for row in boundary_specs}) == 12
    assert len(analog_specs) == 7
    assert len(panel) == 4128
    assert len(v51_lines) == 51
    assert all(not row["page"].lower().startswith("f84") for row in panel)
    assert gdt677_result["global_overlay"]["unknown_positions_after"] == 7923
    assert gdt677_result["global_overlay"]["complete_lines_after"] == 1391
    assert gdt677_result["v51_reader"]["unknown_after"] == 127

    card_by_surface = {row["surface"]: row for row in cards}
    source_by_locus = {row["locus"]: row for row in source_specs}
    boundary_by_key = {(row["locus"], int(row["ordinal"])): row for row in boundary_specs}
    panel_by_locus = {row["locus"]: row for row in panel}
    v51_by_locus = {row["locus"]: row for row in v51_lines}
    assert set(source_by_locus).issubset(v51_by_locus)

    # Rebuild the exact current global overlay from the four published passes.
    overlay: dict[tuple[str, int], tuple[str, str]] = {}

    def add_overlay(locus: str, ordinal: int, meaning: str, source: str) -> None:
        key = (locus, ordinal)
        assert key not in overlay, f"duplicate inherited overlay position: {key}"
        line = panel_by_locus[locus]
        tokens = line["zl3b_line"].split()
        glosses = split_parallel(line["token_glosses_de"])
        match = UNKNOWN_LITERAL.fullmatch(glosses[ordinal - 1])
        assert match
        assert tokens[ordinal - 1] == match.group(1)
        overlay[key] = (meaning, source)

    for row in gdt673:
        assert row["was_v48_unknown"] == "1"
        add_overlay(row["locus"], int(row["ordinal"]), row["working_meaning_de"], "GDT673")
    gdt674_new = [row for row in gdt674 if row["raw_v48_unknown_before"] == "1"]
    for row in gdt674_new:
        add_overlay(row["locus"], int(row["token_index"]), row["working_meaning_de"], "GDT674")
    for row in gdt675:
        assert row["was_v48_unknown"] == "1"
        add_overlay(row["locus"], int(row["ordinal"]), row["applied_meaning_de"], "GDT675")
    for row in gdt677_occurrences:
        add_overlay(row["locus"], int(row["ordinal"]), row["working_meaning_de"], "GDT677")
    assert Counter(source for _, source in overlay.values()) == {
        "GDT673": 162, "GDT674": 24, "GDT675": 51, "GDT677": 20,
    }

    base_unknown: set[tuple[str, int]] = set()
    for line in panel:
        glosses = split_parallel(line["token_glosses_de"])
        for ordinal, gloss in enumerate(glosses, start=1):
            if UNKNOWN_LITERAL.fullmatch(gloss):
                base_unknown.add((line["locus"], ordinal))
    assert len(base_unknown) == 8180
    assert set(overlay).issubset(base_unknown)
    current_unknown = base_unknown - set(overlay)
    assert len(current_unknown) == 7923

    raw_occurrences: list[tuple[dict[str, str], int, str]] = []
    for line in panel:
        for ordinal, surface in enumerate(line["zl3b_line"].split(), start=1):
            if surface in card_by_surface:
                raw_occurrences.append((line, ordinal, surface))
    expected_counts = {row["surface"]: int(row["expected_occurrences"]) for row in cards}
    assert len(raw_occurrences) == 101
    assert Counter(surface for _, _, surface in raw_occurrences) == expected_counts
    target_keys = {(line["locus"], ordinal) for line, ordinal, _ in raw_occurrences}
    assert len(target_keys) == 101
    assert target_keys.issubset(current_unknown)
    assert target_keys.isdisjoint(overlay)

    target_loci = sorted({line["locus"] for line, _, _ in raw_occurrences})
    assert len(target_loci) == 82
    cross_rows, cross_guard = guarded_cross_query(target_loci)
    assert cross_guard["selected"] == len(cross_rows) == 82
    assert cross_guard["skipped_forbidden"] > 0
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    assert set(cross_by_locus) == set(target_loci)

    reader_ops_by_locus: dict[str, tuple[dict[int, tuple[str, str]], dict[int, tuple[str, str]]]] = {}
    for locus in target_loci:
        tokens = panel_by_locus[locus]["zl3b_line"].split()
        cross = cross_by_locus[locus]
        assert cross["zl3b_clean"].split() == tokens
        reader_ops_by_locus[locus] = (
            reader_operations(tokens, cross["it2a_clean"].split()),
            reader_operations(tokens, cross["rf1b_clean"].split()),
        )

    occurrence_rows: list[dict[str, object]] = []
    occurrence_by_key: dict[tuple[str, int], dict[str, object]] = {}
    sorted_occurrences = sorted(
        raw_occurrences,
        key=lambda item: (int(card_by_surface[item[2]]["card_rank"]), item[0]["locus"], item[1]),
    )
    for line, ordinal, surface in sorted_occurrences:
        card = card_by_surface[surface]
        tokens = line["zl3b_line"].split()
        current_glosses = current_line_glosses(line, overlay)
        assert current_glosses[ordinal - 1] == f"[{surface}:?]"
        before_chunks = [unknown_chunk(gloss) for gloss in current_glosses]
        after_chunks = list(before_chunks)
        after_chunks[ordinal - 1] = card["working_render_de"]
        literal_after = list(current_glosses)
        literal_after[ordinal - 1] = card["working_meaning_de"]
        boundary = boundary_by_key.get((line["locus"], ordinal))
        boundary_rule = boundary["resolution_class"] if boundary else "NONE"
        applied_render, neighbor_override = apply_boundary_render(tokens, after_chunks, ordinal, surface, boundary_rule)

        it2a_ops, rf1b_ops = reader_ops_by_locus[line["locus"]]
        it2a_operation, it2a_render = it2a_ops[ordinal - 1]
        rf1b_operation, rf1b_render = rf1b_ops[ordinal - 1]
        support = reader_support(it2a_operation, rf1b_operation)
        cross = cross_by_locus[line["locus"]]
        left_surface = tokens[ordinal - 2] if ordinal > 1 else "BOS"
        right_surface = tokens[ordinal] if ordinal < len(tokens) else "EOS"
        item: dict[str, object] = {
            "card_rank": int(card["card_rank"]), "family": card["family"], "surface": surface,
            "card_type": card["card_type"], "composition": card["composition"],
            "working_meaning_de": card["working_meaning_de"], "applied_render_de": applied_render,
            "strongest_rival_de": card["strongest_rival_de"], "confidence": card["confidence"],
            "action_license": card["action_license"], "page": line["page"], "locus": line["locus"],
            "section": line["section"], "language": line["language"], "hand": line["hand"],
            "ordinal": ordinal, "token_count": len(tokens), "line_position": position_class(ordinal, len(tokens)),
            "left_surface": left_surface, "right_surface": right_surface,
            "context_decision": f"HOLD_{boundary_rule}" if boundary else "HOLD_SAME_CARD",
            "neighbor_override": neighbor_override,
            "it2a_operation": it2a_operation, "it2a_render": it2a_render,
            "rf1b_operation": rf1b_operation, "rf1b_render": rf1b_render,
            "reader_support": support, "all_three_present": cross["all_three_present"],
            "all_present_exact": cross["all_present_exact"], "zl3b_line": line["zl3b_line"],
            "context_before_de": " · ".join(before_chunks) + ".",
            "context_after_de": " · ".join(after_chunks) + ".",
            "literal_after_de": " | ".join(literal_after),
            "review_note": boundary["review_note"] if boundary else card["decision_reason"],
        }
        assert not HARD_GENERIC.search(str(item["context_after_de"]))
        occurrence_rows.append(item)
        occurrence_by_key[(line["locus"], ordinal)] = item

    assert len(occurrence_rows) == 101
    support_counts = Counter(str(row["reader_support"]) for row in occurrence_rows)
    assert support_counts == {
        "BOTH_EXACT": 65, "IT2A_ONLY_EXACT": 15, "RF1B_ONLY_EXACT": 10, "NEITHER_EXACT": 11,
    }
    neither_keys = {
        (str(row["locus"]), int(row["ordinal"]))
        for row in occurrence_rows if row["reader_support"] == "NEITHER_EXACT"
    }
    assert neither_keys.issubset(set(boundary_by_key))
    assert set(boundary_by_key) - neither_keys == {("f7r.2", 2)}

    family_rows: list[dict[str, object]] = []
    for card in sorted(cards, key=lambda row: int(row["card_rank"])):
        rows = [row for row in occurrence_rows if row["surface"] == card["surface"]]
        counts = Counter(str(row["reader_support"]) for row in rows)
        family_rows.append({
            **card,
            "observed_occurrences": len(rows),
            "observed_pages": len({str(row["page"]) for row in rows}),
            "both_exact": counts["BOTH_EXACT"],
            "it2a_only_exact": counts["IT2A_ONLY_EXACT"],
            "rf1b_only_exact": counts["RF1B_ONLY_EXACT"],
            "neither_exact": counts["NEITHER_EXACT"],
            "context_holds": len(rows),
            "licensed_actions": sum(int(row["action_license"]) for row in rows),
        })
        assert len(rows) == int(card["expected_occurrences"])
        assert len({str(row["page"]) for row in rows}) == int(card["expected_pages"])

    boundary_rows: list[dict[str, object]] = []
    for spec in sorted(boundary_specs, key=lambda row: (row["locus"], int(row["ordinal"]))):
        key = (spec["locus"], int(spec["ordinal"]))
        occurrence = occurrence_by_key[key]
        assert occurrence["surface"] == spec["surface"]
        boundary_rows.append({
            **spec,
            "it2a_operation": occurrence["it2a_operation"], "it2a_render": occurrence["it2a_render"],
            "rf1b_operation": occurrence["rf1b_operation"], "rf1b_render": occurrence["rf1b_render"],
            "reader_support": occurrence["reader_support"], "context_after_de": occurrence["context_after_de"],
        })

    completed_rows: list[dict[str, object]] = []
    completed_by_locus: dict[str, dict[str, object]] = {}
    for spec in sorted(source_specs, key=lambda row: int(row["line_rank"])):
        old = v51_by_locus[spec["locus"]]
        tokens = old["zl3b_line"].split()
        hits = [(ordinal, surface) for ordinal, surface in enumerate(tokens, start=1) if surface in card_by_surface]
        expected_surfaces = split_pipe(spec["target_surfaces"])
        assert len(hits) == 2
        assert [surface for _, surface in hits] == expected_surfaces
        assert int(old["residual_unknown_positions"]) == 2
        old_chunks = old["working_line_de"].rstrip(".").split(" · ")
        old_literal = split_parallel(old["literal_token_glosses_de"])
        assert len(tokens) == len(old_chunks) == len(old_literal)
        new_chunks = list(old_chunks)
        new_literal = list(old_literal)
        for ordinal, surface in hits:
            card = card_by_surface[surface]
            assert old_chunks[ordinal - 1] == f"⟦{surface}:?⟧"
            assert old_literal[ordinal - 1] == f"[{surface}:?]"
            new_chunks[ordinal - 1] = card["working_render_de"]
            new_literal[ordinal - 1] = card["working_meaning_de"]
            boundary = boundary_by_key.get((spec["locus"], ordinal))
            if boundary:
                apply_boundary_render(tokens, new_chunks, ordinal, surface, boundary["resolution_class"])

        old_actions = set(parse_ordinals(old["action_ordinals"]))
        added_surfaces = split_pipe(spec["added_action_surfaces"])
        added_ordinals = {ordinal for ordinal, surface in hits if surface in added_surfaces}
        assert {surface for ordinal, surface in hits if ordinal in added_ordinals} == set(added_surfaces)
        assert all(card_by_surface[tokens[ordinal - 1]]["action_license"] == "1" for ordinal in added_ordinals)
        assert all(
            card_by_surface[surface]["action_license"] == ("1" if surface in added_surfaces else "0")
            for _, surface in hits
        )
        new_actions = old_actions | added_ordinals
        completed = {
            "line_rank": int(spec["line_rank"]), "page": old["page"], "locus": old["locus"],
            "section": old["section"], "language": old["language"], "hand": old["hand"],
            "token_count": len(tokens), "closed_ordinals": "|".join(str(value) for value, _ in hits),
            "closed_surfaces": "|".join(surface for _, surface in hits),
            "old_line_mode": old["line_mode"], "new_line_mode": spec["new_line_mode"],
            "old_action_ordinals": old["action_ordinals"],
            "new_action_ordinals": "|".join(map(str, sorted(new_actions))) or "NONE",
            "new_action_surfaces": "|".join(tokens[value - 1] for value in sorted(new_actions)) or "NONE",
            "added_action_ordinals": "|".join(map(str, sorted(added_ordinals))) or "NONE",
            "added_action_surfaces": spec["added_action_surfaces"],
            "reader_boundary_rule": spec["reader_boundary_rule"], "zl3b_line": old["zl3b_line"],
            "old_literal_token_glosses_de": old["literal_token_glosses_de"],
            "new_literal_token_glosses_de": " | ".join(new_literal),
            "old_aligned_line_de": old["working_line_de"], "aligned_line_de": " · ".join(new_chunks) + ".",
            "practical_translation_de": spec["practical_translation_de"], "review_note": spec["review_note"],
        }
        assert "⟦" not in str(completed["aligned_line_de"])
        assert ":?]" not in str(completed["new_literal_token_glosses_de"])
        assert not HARD_GENERIC.search(str(completed["aligned_line_de"]))
        assert not HARD_GENERIC.search(str(completed["practical_translation_de"]))
        completed_rows.append(completed)
        completed_by_locus[old["locus"]] = completed
    assert len(completed_rows) == 17

    v52_rows: list[dict[str, object]] = []
    distribution = Counter()
    for old in v51_lines:
        completed = completed_by_locus.get(old["locus"])
        if completed:
            actions = parse_ordinals(str(completed["new_action_ordinals"]))
            row: dict[str, object] = {
                "page": old["page"], "locus": old["locus"], "section": old["section"],
                "language": old["language"], "hand": old["hand"], "token_count": old["token_count"],
                "new_v50_positions": old["new_v50_positions"], "new_v51_positions": old["new_v51_positions"],
                "new_v52_positions": 2, "residual_unknown_positions": 0, "assigned_fraction": "1.000000",
                "complete": "1", "action_positions": len(actions),
                "action_ordinals": completed["new_action_ordinals"],
                "action_surfaces": completed["new_action_surfaces"], "line_mode": completed["new_line_mode"],
                "v52_target_surfaces": completed["closed_surfaces"], "remaining_unknown_surfaces": "NONE",
                "zl3b_line": old["zl3b_line"],
                "literal_token_glosses_de": completed["new_literal_token_glosses_de"],
                "aligned_line_de": completed["aligned_line_de"],
                "practical_translation_de": completed["practical_translation_de"],
                "review_note": completed["review_note"],
            }
        else:
            residual = int(old["residual_unknown_positions"])
            row = {
                "page": old["page"], "locus": old["locus"], "section": old["section"],
                "language": old["language"], "hand": old["hand"], "token_count": old["token_count"],
                "new_v50_positions": old["new_v50_positions"], "new_v51_positions": old["new_v51_positions"],
                "new_v52_positions": 0, "residual_unknown_positions": residual,
                "assigned_fraction": old["assigned_fraction"], "complete": old["complete"],
                "action_positions": old["action_positions"], "action_ordinals": old["action_ordinals"],
                "action_surfaces": old["action_surfaces"], "line_mode": old["line_mode"],
                "v52_target_surfaces": "NONE", "remaining_unknown_surfaces": old["remaining_unknown_surfaces"],
                "zl3b_line": old["zl3b_line"], "literal_token_glosses_de": old["literal_token_glosses_de"],
                "aligned_line_de": old["working_line_de"], "practical_translation_de": old["working_line_de"],
                "review_note": old["review_note"],
            }
        distribution[int(row["residual_unknown_positions"])] += 1
        assert not HARD_GENERIC.search(str(row["aligned_line_de"]))
        v52_rows.append(row)

    assert sum(int(row["token_count"]) for row in v52_rows) == 479
    assert sum(int(row["new_v52_positions"]) for row in v52_rows) == 34
    assert sum(int(row["residual_unknown_positions"]) for row in v52_rows) == 93
    assert sum(row["complete"] == "1" for row in v52_rows) == 28
    assert distribution == {0: 28, 3: 8, 4: 8, 5: 6, 7: 1}

    # Calculate the global coverage effect rather than assuming that only the 17 deck lines close.
    after_unknown = current_unknown - target_keys
    assert len(after_unknown) == 7822
    current_unknown_by_locus = Counter(locus for locus, _ in current_unknown)
    after_unknown_by_locus = Counter(locus for locus, _ in after_unknown)
    complete_before = sum(current_unknown_by_locus[line["locus"]] == 0 for line in panel)
    complete_after = sum(after_unknown_by_locus[line["locus"]] == 0 for line in panel)
    newly_closed_loci = [
        line["locus"] for line in panel
        if current_unknown_by_locus[line["locus"]] > 0 and after_unknown_by_locus[line["locus"]] == 0
    ]
    assert complete_before == 1391
    assert complete_after == 1410
    assert len(newly_closed_loci) == 19
    assert set(source_by_locus).issubset(newly_closed_loci)
    assert set(newly_closed_loci) - set(source_by_locus) == {"f38v.6", "f80r.21"}

    global_closed_rows: list[dict[str, object]] = []
    for locus in newly_closed_loci:
        line = panel_by_locus[locus]
        tokens = line["zl3b_line"].split()
        before_glosses = current_line_glosses(line, overlay)
        after_glosses = list(before_glosses)
        hits: list[tuple[int, str]] = []
        for ordinal, surface in enumerate(tokens, start=1):
            if (locus, ordinal) in target_keys:
                hits.append((ordinal, surface))
                after_glosses[ordinal - 1] = card_by_surface[surface]["working_meaning_de"]
        assert hits
        assert all(not UNKNOWN_LITERAL.fullmatch(gloss) for gloss in after_glosses)
        practical = (
            source_by_locus[locus]["practical_translation_de"]
            if locus in source_by_locus else "; ".join(after_glosses) + "."
        )
        global_closed_rows.append({
            "page": line["page"], "locus": locus, "section": line["section"],
            "language": line["language"], "hand": line["hand"], "token_count": len(tokens),
            "target_ordinals": "|".join(str(value) for value, _ in hits),
            "target_surfaces": "|".join(surface for _, surface in hits),
            "v51_source_line": "1" if locus in source_by_locus else "0",
            "zl3b_line": line["zl3b_line"], "current_literal_de": " | ".join(before_glosses),
            "after_literal_de": " | ".join(after_glosses), "practical_translation_de": practical,
        })
        assert not HARD_GENERIC.search(practical)

    prediction_rows = [
        {"prediction_id": "GDT678-P01", "observed_pair": "oltaiin|oltain", "visible_difference": "aiin versus ain", "predicted_semantic_difference": "cold wood preparation grade III versus II", "held_positions": "3/3", "next_unseen_test": "an oltan sister should preserve the wood preparation and lower only the cold grade"},
        {"prediction_id": "GDT678-P02", "observed_pair": "olchain|olchey|olchedy", "visible_difference": "ain versus ey versus edy", "predicted_semantic_difference": "dry wood preparation grade II, middle-stage dry result, finished dry result", "held_positions": "22/22", "next_unseen_test": "a new olchey occurrence should remain a nominal wood-dry middle result"},
        {"prediction_id": "GDT678-P03", "observed_pair": "qokeo|qokeod", "visible_difference": "terminal d", "predicted_semantic_difference": "prepare hot extract versus prepare and close it", "held_positions": "5/5", "next_unseen_test": "another qokeod should license a closed hot-extract instruction"},
        {"prediction_id": "GDT678-P04", "observed_pair": "oin|qoin", "visible_difference": "initial q", "predicted_semantic_difference": "prepare second preparation versus take the second preparation", "held_positions": "2/2", "next_unseen_test": "a new qoin context should distinguish learned oin from productive qo+in form II"},
        {"prediction_id": "GDT678-P05", "observed_pair": "cho|qocho|qotcho|qotchody", "visible_difference": "command, cold t and terminal dy", "predicted_semantic_difference": "dry preparation, take it, cool/dry/prepare, then finish", "held_positions": "5/5", "next_unseen_test": "terminal dy should keep finished scope in another qotcho extension"},
        {"prediction_id": "GDT678-P06", "observed_pair": "chot|chotar", "visible_difference": "terminal ar", "predicted_semantic_difference": "cooled dry preparation versus its first fraction", "held_positions": "9/9", "next_unseen_test": "chotair should denote a second fraction if the fraction ladder is productive"},
        {"prediction_id": "GDT678-P07", "observed_pair": "cph|dor|cphdor", "visible_difference": "compound drug plus measure-portion block", "predicted_semantic_difference": "measure one portion of medicinal composite", "held_positions": "1/1", "next_unseen_test": "cphdar should contrast first fraction with cphdor portion"},
        {"prediction_id": "GDT678-P08", "observed_pair": "otain|oteor", "visible_difference": "grade-II ain versus middle-stage portion e+or", "predicted_semantic_difference": "cold preparation grade II versus one cold middle-stage portion", "held_positions": "10/10", "next_unseen_test": "oteair should preserve cold middle preparation while changing to fraction II"},
        {"prediction_id": "GDT678-P09", "observed_pair": "rr|rchr", "visible_difference": "alternate readers restore ch", "predicted_semantic_difference": "dried root material, not a productive double-r quantity", "held_positions": "1/1", "next_unseen_test": "another ZL3b rr must be checked against the physical reading before any reduplication rule"},
        {"prediction_id": "GDT678-P10", "observed_pair": "keo r|keor and l karchees|lkarchees", "visible_difference": "reader whitespace", "predicted_semantic_difference": "joined known portion and hot-wood dry-charge readings", "held_positions": "4/4", "next_unseen_test": "new boundary variants should preserve letters and improve practical composition without changing unrelated cards"},
    ]

    occurrence_fields = [
        "card_rank", "family", "surface", "card_type", "composition", "working_meaning_de",
        "applied_render_de", "strongest_rival_de", "confidence", "action_license", "page", "locus",
        "section", "language", "hand", "ordinal", "token_count", "line_position", "left_surface",
        "right_surface", "context_decision", "neighbor_override", "it2a_operation", "it2a_render",
        "rf1b_operation", "rf1b_render", "reader_support", "all_three_present", "all_present_exact",
        "zl3b_line", "context_before_de", "context_after_de", "literal_after_de", "review_note",
    ]
    family_fields = [
        *cards[0].keys(), "observed_occurrences", "observed_pages", "both_exact", "it2a_only_exact",
        "rf1b_only_exact", "neither_exact", "context_holds", "licensed_actions",
    ]
    boundary_fields = [
        *boundary_specs[0].keys(), "it2a_operation", "it2a_render", "rf1b_operation", "rf1b_render",
        "reader_support", "context_after_de",
    ]
    completed_fields = [
        "line_rank", "page", "locus", "section", "language", "hand", "token_count", "closed_ordinals",
        "closed_surfaces", "old_line_mode", "new_line_mode", "old_action_ordinals", "new_action_ordinals",
        "new_action_surfaces", "added_action_ordinals", "added_action_surfaces", "reader_boundary_rule",
        "zl3b_line", "old_literal_token_glosses_de", "new_literal_token_glosses_de", "old_aligned_line_de",
        "aligned_line_de", "practical_translation_de", "review_note",
    ]
    v52_fields = [
        "page", "locus", "section", "language", "hand", "token_count", "new_v50_positions",
        "new_v51_positions", "new_v52_positions", "residual_unknown_positions", "assigned_fraction",
        "complete", "action_positions", "action_ordinals", "action_surfaces", "line_mode",
        "v52_target_surfaces", "remaining_unknown_surfaces", "zl3b_line", "literal_token_glosses_de",
        "aligned_line_de", "practical_translation_de", "review_note",
    ]
    global_closed_fields = [
        "page", "locus", "section", "language", "hand", "token_count", "target_ordinals",
        "target_surfaces", "v51_source_line", "zl3b_line", "current_literal_de", "after_literal_de",
        "practical_translation_de",
    ]
    write_tsv(output_dir / "TARGET_FAMILY_CARDS.tsv", family_rows, family_fields)
    write_tsv(output_dir / "TARGET_EXACT_OCCURRENCE_AUDIT.tsv", occurrence_rows, occurrence_fields)
    write_tsv(output_dir / "BOUNDARY_DECISIONS.tsv", boundary_rows, boundary_fields)
    write_tsv(output_dir / "SEVENTEEN_COMPLETED_LINES_V52.tsv", completed_rows, completed_fields)
    write_tsv(output_dir / "V52_51_LINE_READER.tsv", v52_rows, v52_fields)
    write_tsv(output_dir / "GLOBAL_NEWLY_COMPLETED_LINES.tsv", global_closed_rows, global_closed_fields)
    write_tsv(
        output_dir / "FAMILY_PREDICTIONS.tsv", prediction_rows,
        ["prediction_id", "observed_pair", "visible_difference", "predicted_semantic_difference", "held_positions", "next_unseen_test"],
    )
    write_tsv(output_dir / "HISTORICAL_ANALOG_ATLAS.tsv", analog_specs, list(analog_specs[0].keys()))

    reader_doc = [
        "# GDT678 — seventeen completed V52 practical readings", "",
        "The practical paragraphs collapse only explicitly recorded reader joins. The TSV companion preserves every ZL3b token, literal card and aligned chunk. These are replaceable working readings, not claimed plaintext.", "",
    ]
    for row in completed_rows:
        reader_doc.extend([
            f"## {row['line_rank']}. {row['locus']} · {row['new_line_mode']}", "",
            f"**ZL3b:** `{row['zl3b_line']}`", "",
            f"**Praxislesung:** {row['practical_translation_de']}", "",
            f"**Tokenparallel:** {row['aligned_line_de']}", "",
            f"**Neu geschlossen:** `{row['closed_surfaces']}`", "",
            f"**Aktionen:** {row['new_action_ordinals']} ({row['new_action_surfaces']})", "",
            f"**Leserentscheidung:** {row['reader_boundary_rule']}. {row['review_note']}", "",
        ])
    (output_dir / "GDT678_SEVENTEEN_COMPLETED_PRACTICAL_READER.md").write_text(
        "\n".join(reader_doc).rstrip() + "\n", encoding="utf-8"
    )

    action_positions_before = sum(int(row["action_positions"]) for row in v51_lines)
    action_positions_after = sum(int(row["action_positions"]) for row in v52_rows)
    mode_counts = Counter(str(row["line_mode"]) for row in v52_rows)
    result: dict[str, object] = {
        "status": "PASS_34_FAMILY_CARDS__101_CONTEXTS_HOLD__17_V52_LINES_CLOSED__V52_93_OPEN",
        "basis": {
            "panel_lines": 4128, "panel_pages": len({row["page"] for row in panel}),
            "target_lines": 82, "target_pages": len({str(row["page"]) for row in occurrence_rows}),
            "target_occurrences": 101, "target_surfaces": 34, "source_two_hole_lines": 17,
            "new_pages_opened": 0, "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "cross_guard": cross_guard,
        },
        "cards": {
            "types": dict(sorted(Counter(row["card_type"] for row in cards).items())),
            "context_holds": len(occurrence_rows), "context_conflicts": 0,
            "licensed_action_occurrences": sum(int(row["action_license"]) for row in occurrence_rows),
            "historical_analogs": len(analog_specs), "forward_predictions": len(prediction_rows),
        },
        "reader_support": dict(sorted(support_counts.items())),
        "boundary_decisions": {
            "recorded": len(boundary_rows), "neither_exact": support_counts["NEITHER_EXACT"],
            "source_line_joint_renders": 3,
            "critical": ["f77v.7 rr/rchr", "f7r.2 keo r/keor", "f86v6.4 l karchees/lkarchees"],
        },
        "global_overlay": {
            "unknown_positions_before": len(current_unknown), "unknown_positions_after": len(after_unknown),
            "new_assigned_positions": len(target_keys), "complete_lines_before": complete_before,
            "complete_lines_after": complete_after, "newly_completed_lines": len(newly_closed_loci),
            "newly_completed_outside_v51_source": sorted(set(newly_closed_loci) - set(source_by_locus)),
        },
        "v52_reader": {
            "lines": 51, "tokens": 479, "unknown_before": 127, "unknown_after": 93,
            "assigned_before": 352, "assigned_after": 386, "assigned_fraction_after": f"{386 / 479:.6f}",
            "complete_before": 11, "complete_after": 28,
            "unknown_distribution": {str(key): distribution[key] for key in sorted(distribution)},
            "licensed_action_positions_before": action_positions_before,
            "licensed_action_positions_after": action_positions_after,
            "new_action_positions": action_positions_after - action_positions_before,
            "modes": dict(sorted(mode_counts.items())),
            "hard_generic_hits": sum(len(HARD_GENERIC.findall(str(row["aligned_line_de"]))) for row in v52_rows),
        },
        "weakest_cards": [
            {"surface": "yey", "reason": "one occurrence and a sequence-link rather than an ingredient or process"},
            {"surface": "qy", "reason": "short anaphoric take card with three alternate-reader rivals"},
            {"surface": "rr", "reason": "practical default comes from both alternate readers' rchr rather than ZL3b rr"},
            {"surface": "lldar", "reason": "known ldar action is retained but doubled initial l has no independent value"},
        ],
        "claim_ceiling": (
            "Thirty-four replaceable working cards apply with one semantic core to all 101 exact ZL3b occurrences "
            "on the already admitted panel. They close the seventeen selected V51 two-hole lines plus two additional "
            "global lines, while explicit reader joins repair keo r and l karchees and the two-reader rchr reading "
            "controls ZL3b rr. This is a concrete mixed learned-whole and productive-component working renderer, not "
            "confirmed plaintext, phonetics, a historical codebook identity, exact plant species, disease, patient, "
            "cure, carrier liquid, or manuscript-wide translation. All named rivals remain replaceable."
        ),
        "files": {},
    }
    assert action_positions_before == 49
    assert action_positions_after == 60
    assert mode_counts == {"ACTION_SEQUENCE": 12, "MIXED_RECORD": 20, "NOMINAL_REGISTER": 11, "QUANTITY_LABEL": 8}
    artifact_names = [
        "TARGET_FAMILY_CARDS.tsv", "TARGET_EXACT_OCCURRENCE_AUDIT.tsv", "BOUNDARY_DECISIONS.tsv",
        "SEVENTEEN_COMPLETED_LINES_V52.tsv", "V52_51_LINE_READER.tsv", "GLOBAL_NEWLY_COMPLETED_LINES.tsv",
        "FAMILY_PREDICTIONS.tsv", "HISTORICAL_ANALOG_ATLAS.tsv",
        "GDT678_SEVENTEEN_COMPLETED_PRACTICAL_READER.md",
    ]
    result["files"] = {name: sha256(output_dir / name) for name in artifact_names}
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    build(ART)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
