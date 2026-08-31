#!/usr/bin/env python3
"""Build the GDT682 seven-card occurrence circuit and complete V56 reader."""

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
EXP = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion"
ART = EXP / "artifacts"
PANEL_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
GDT673_PATH = ROOT / "experiments/yolo/gdt673_v48_transfer_occurrence_conflict_scan/artifacts/TRANSFERABLE_EXACT_OCCURRENCES.tsv"
GDT674_PATH = ROOT / "experiments/yolo/gdt674_v49_f81r_concrete_renderer/artifacts/F81R_TOKEN_READINGS.tsv"
GDT675_PATH = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan/artifacts/EXTERNAL_TRANSFERABLE_OCCURRENCES.tsv"
GDT677_PATH = ROOT / "experiments/yolo/gdt677_nine_one_hole_family_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv"
GDT678_PATH = ROOT / "experiments/yolo/gdt678_seventeen_two_hole_family_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv"
GDT679_PATH = ROOT / "experiments/yolo/gdt679_eight_three_hole_family_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv"
GDT680_PATH = ROOT / "experiments/yolo/gdt680_eight_four_hole_family_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv"
GDT681_PATH = ROOT / "experiments/yolo/gdt681_six_five_hole_family_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv"
GDT681_RESULT_PATH = ROOT / "experiments/yolo/gdt681_six_five_hole_family_completion/artifacts/RESULT.json"
V55_PATH = ROOT / "experiments/yolo/gdt681_six_five_hole_family_completion/artifacts/V55_51_LINE_READER.tsv"
CROSS_PATH = Path("transcription/voynich_cross_transcription_lines.tsv")
CARD_PATH = EXP / "src/TARGET_CARD_SPECS.tsv"
SOURCE_PATH = EXP / "src/SOURCE_LINE_SPECS.tsv"
BOUNDARY_PATH = EXP / "src/BOUNDARY_DECISION_SPECS.tsv"
CONTEXT_PATH = EXP / "src/CONTEXT_ROLE_SPECS.tsv"
ANALOG_PATH = EXP / "src/HISTORICAL_ANALOG_SPECS.tsv"

UNKNOWN_LITERAL = re.compile(r"^\[([^:\]]+):\?\]$")
HARD_GENERIC = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|"
    r"Arbeitsstelle|Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|"
    r"Arbeitsschritt|Stationsansatz|Stationsposten|Stationswert|Stationsanteil|"
    r"Stationseinheit|Aktiver Posten|laufender Eintrag|weiterführen|work item|"
    r"working material|worksite|work cycle|source vessel|destination place|"
    r"destination vessel)\b",
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


def align_reader_tokens(source: list[str], alternate: list[str]) -> list[tuple[str, tuple[int, ...], str]]:
    """Prefer exact tokens, then low-cost boundary joins or splits."""
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
                offer(i + 1, j + 1, cost + (0 if source[i] == alternate[j] else 10), steps + 1, path, ("ONE", (i,), alternate[j]))
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


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(CARD_PATH)
    source_specs = read_tsv(SOURCE_PATH)
    boundary_specs = read_tsv(BOUNDARY_PATH)
    context_specs = read_tsv(CONTEXT_PATH)
    analog_specs = read_tsv(ANALOG_PATH)
    panel = read_tsv(PANEL_PATH)
    gdt673 = read_tsv(GDT673_PATH)
    gdt674 = read_tsv(GDT674_PATH)
    gdt675 = read_tsv(GDT675_PATH)
    gdt677 = read_tsv(GDT677_PATH)
    gdt678 = read_tsv(GDT678_PATH)
    gdt679 = read_tsv(GDT679_PATH)
    gdt680 = read_tsv(GDT680_PATH)
    gdt681 = read_tsv(GDT681_PATH)
    gdt681_result = json.loads(GDT681_RESULT_PATH.read_text(encoding="utf-8"))
    v55_lines = read_tsv(V55_PATH)

    assert len(cards) == len({row["surface"] for row in cards}) == 7
    assert {int(row["card_rank"]) for row in cards} == set(range(1, 8))
    assert len(source_specs) == len({row["locus"] for row in source_specs}) == 1
    assert len(boundary_specs) == 1
    assert len({(row["locus"], int(row["ordinal"])) for row in boundary_specs}) == 1
    assert len(context_specs) == 17
    assert len({(row["locus"], int(row["ordinal"])) for row in context_specs}) == 17
    assert all(row["context_verdict"].startswith("HOLD") for row in context_specs)
    assert len(analog_specs) == len({row["analog_id"] for row in analog_specs}) == 7
    assert len(panel) == 4128
    assert len(v55_lines) == 51
    assert all(not row["page"].lower().startswith("f84") for row in panel)
    assert gdt681_result["global_overlay"]["unknown_positions_after"] == 7573
    assert gdt681_result["global_overlay"]["complete_lines_after"] == 1439
    assert gdt681_result["v55_reader"]["unknown_after"] == 7

    card_by_surface = {row["surface"]: row for row in cards}
    source_by_locus = {row["locus"]: row for row in source_specs}
    boundary_by_key = {(row["locus"], int(row["ordinal"])): row for row in boundary_specs}
    context_by_key = {(row["locus"], int(row["ordinal"])): row for row in context_specs}
    panel_by_locus = {row["locus"]: row for row in panel}
    v55_by_locus = {row["locus"]: row for row in v55_lines}
    assert set(source_by_locus).issubset(v55_by_locus)

    overlay: dict[tuple[str, int], tuple[str, str]] = {}

    def add_overlay(locus: str, ordinal: int, meaning: str, source: str) -> None:
        key = (locus, ordinal)
        assert key not in overlay, f"duplicate inherited overlay position: {key}"
        line = panel_by_locus[locus]
        tokens = line["zl3b_line"].split()
        glosses = split_parallel(line["token_glosses_de"])
        match = UNKNOWN_LITERAL.fullmatch(glosses[ordinal - 1])
        assert match and tokens[ordinal - 1] == match.group(1)
        overlay[key] = (meaning, source)

    for row in gdt673:
        assert row["was_v48_unknown"] == "1"
        add_overlay(row["locus"], int(row["ordinal"]), row["working_meaning_de"], "GDT673")
    for row in gdt674:
        if row["raw_v48_unknown_before"] == "1":
            add_overlay(row["locus"], int(row["token_index"]), row["working_meaning_de"], "GDT674")
    for row in gdt675:
        assert row["was_v48_unknown"] == "1"
        add_overlay(row["locus"], int(row["ordinal"]), row["applied_meaning_de"], "GDT675")
    for row in gdt677:
        add_overlay(row["locus"], int(row["ordinal"]), row["working_meaning_de"], "GDT677")
    for row in gdt678:
        add_overlay(row["locus"], int(row["ordinal"]), row["working_meaning_de"], "GDT678")
    for row in gdt679:
        add_overlay(row["locus"], int(row["ordinal"]), row["working_meaning_de"], "GDT679")
    for row in gdt680:
        add_overlay(row["locus"], int(row["ordinal"]), row["working_meaning_de"], "GDT680")
    for row in gdt681:
        add_overlay(row["locus"], int(row["ordinal"]), row["working_meaning_de"], "GDT681")
    assert Counter(source for _, source in overlay.values()) == {
        "GDT673": 162,
        "GDT674": 24,
        "GDT675": 51,
        "GDT677": 20,
        "GDT678": 101,
        "GDT679": 57,
        "GDT680": 88,
        "GDT681": 104,
    }

    base_unknown: set[tuple[str, int]] = set()
    for line in panel:
        for ordinal, gloss in enumerate(split_parallel(line["token_glosses_de"]), start=1):
            if UNKNOWN_LITERAL.fullmatch(gloss):
                base_unknown.add((line["locus"], ordinal))
    assert len(base_unknown) == 8180
    assert set(overlay).issubset(base_unknown)
    current_unknown = base_unknown - set(overlay)
    assert len(current_unknown) == 7573

    raw_occurrences: list[tuple[dict[str, str], int, str]] = []
    for line in panel:
        for ordinal, surface in enumerate(line["zl3b_line"].split(), start=1):
            if surface in card_by_surface:
                raw_occurrences.append((line, ordinal, surface))
    expected_counts = {row["surface"]: int(row["expected_occurrences"]) for row in cards}
    assert len(raw_occurrences) == 17
    assert Counter(surface for _, _, surface in raw_occurrences) == expected_counts
    target_keys = {(line["locus"], ordinal) for line, ordinal, _ in raw_occurrences}
    assert len(target_keys) == 17
    assert target_keys == set(context_by_key)
    assert target_keys.issubset(current_unknown)
    target_loci = sorted({line["locus"] for line, _, _ in raw_occurrences})
    assert len(target_loci) == 11

    cross_rows, cross_guard = guarded_cross_query(target_loci)
    assert cross_guard == {"selected": 11, "skipped_forbidden": 98, "skipped_not_allowed": 5277}
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
        boundary = boundary_by_key.get((line["locus"], ordinal))
        context_spec = context_by_key[(line["locus"], ordinal)]
        assert context_spec["surface"] == surface
        applied_render = boundary["applied_render_de"] if boundary else card["working_render_de"]
        after_chunks[ordinal - 1] = applied_render
        literal_after = list(current_glosses)
        literal_after[ordinal - 1] = card["working_meaning_de"]
        it2a_ops, rf1b_ops = reader_ops_by_locus[line["locus"]]
        it2a_operation, it2a_render = it2a_ops[ordinal - 1]
        rf1b_operation, rf1b_render = rf1b_ops[ordinal - 1]
        support = reader_support(it2a_operation, rf1b_operation)
        cross = cross_by_locus[line["locus"]]
        item: dict[str, object] = {
            "card_rank": int(card["card_rank"]),
            "family": card["family"],
            "surface": surface,
            "card_type": card["card_type"],
            "composition": card["composition"],
            "working_meaning_de": card["working_meaning_de"],
            "applied_render_de": applied_render,
            "strongest_rival_de": card["strongest_rival_de"],
            "confidence": card["confidence"],
            "action_license": card["action_license"],
            "page": line["page"],
            "locus": line["locus"],
            "section": line["section"],
            "language": line["language"],
            "hand": line["hand"],
            "ordinal": ordinal,
            "token_count": len(tokens),
            "line_position": position_class(ordinal, len(tokens)),
            "left_surface": tokens[ordinal - 2] if ordinal > 1 else "BOS",
            "right_surface": tokens[ordinal] if ordinal < len(tokens) else "EOS",
            "context_role": context_spec["context_role"],
            "context_verdict": context_spec["context_verdict"],
            "context_decision": boundary["resolution_class"] if boundary else context_spec["context_verdict"],
            "it2a_operation": it2a_operation,
            "it2a_render": it2a_render,
            "rf1b_operation": rf1b_operation,
            "rf1b_render": rf1b_render,
            "reader_support": support,
            "all_three_present": cross["all_three_present"],
            "all_present_exact": cross["all_present_exact"],
            "zl3b_line": line["zl3b_line"],
            "context_before_de": " · ".join(before_chunks) + ".",
            "context_after_de": " · ".join(after_chunks) + ".",
            "literal_after_de": " | ".join(literal_after),
            "review_note": context_spec["context_reason"] + " " + (
                boundary["review_note"] if boundary else card["decision_reason"]
            ),
        }
        assert not HARD_GENERIC.search(str(item["context_after_de"]))
        occurrence_rows.append(item)
        occurrence_by_key[(line["locus"], ordinal)] = item

    support_counts = Counter(str(row["reader_support"]) for row in occurrence_rows)
    assert support_counts == {
        "BOTH_EXACT": 16,
        "RF1B_ONLY_EXACT": 1,
    }
    non_both_keys = {
        (str(row["locus"]), int(row["ordinal"]))
        for row in occurrence_rows
        if row["reader_support"] != "BOTH_EXACT"
    }
    assert non_both_keys == set(boundary_by_key)

    family_rows: list[dict[str, object]] = []
    for card in sorted(cards, key=lambda row: int(row["card_rank"])):
        rows = [row for row in occurrence_rows if row["surface"] == card["surface"]]
        counts = Counter(str(row["reader_support"]) for row in rows)
        family_rows.append(
            {
                **card,
                "observed_occurrences": len(rows),
                "observed_pages": len({str(row["page"]) for row in rows}),
                "both_exact": counts["BOTH_EXACT"],
                "it2a_only_exact": counts["IT2A_ONLY_EXACT"],
                "rf1b_only_exact": counts["RF1B_ONLY_EXACT"],
                "neither_exact": counts["NEITHER_EXACT"],
                "context_holds": sum(str(row["context_verdict"]).startswith("HOLD") for row in rows),
            }
        )
        assert len(rows) == int(card["expected_occurrences"])
        assert len({str(row["page"]) for row in rows}) == int(card["expected_pages"])

    boundary_rows: list[dict[str, object]] = []
    for spec in sorted(boundary_specs, key=lambda row: (row["locus"], int(row["ordinal"]))):
        occurrence = occurrence_by_key[(spec["locus"], int(spec["ordinal"]))]
        assert occurrence["surface"] == spec["surface"]
        boundary_rows.append(
            {
                **spec,
                "it2a_operation": occurrence["it2a_operation"],
                "it2a_render": occurrence["it2a_render"],
                "rf1b_operation": occurrence["rf1b_operation"],
                "rf1b_render": occurrence["rf1b_render"],
                "reader_support": occurrence["reader_support"],
                "context_after_de": occurrence["context_after_de"],
            }
        )

    completed_rows: list[dict[str, object]] = []
    completed_by_locus: dict[str, dict[str, object]] = {}
    for spec in sorted(source_specs, key=lambda row: int(row["line_rank"])):
        old = v55_by_locus[spec["locus"]]
        tokens = old["zl3b_line"].split()
        hits = [(ordinal, surface) for ordinal, surface in enumerate(tokens, start=1) if surface in card_by_surface]
        assert len(hits) == 7
        assert [surface for _, surface in hits] == split_pipe(spec["target_surfaces"])
        old_literal = split_parallel(old["literal_token_glosses_de"])
        old_chunks = old["aligned_line_de"].removesuffix(".").split(" · ")
        assert len(old_literal) == len(old_chunks) == len(tokens)
        new_literal = list(old_literal)
        new_chunks = list(old_chunks)
        for ordinal, surface in hits:
            assert old_literal[ordinal - 1] == f"[{surface}:?]"
            occurrence = occurrence_by_key[(spec["locus"], ordinal)]
            new_literal[ordinal - 1] = card_by_surface[surface]["working_meaning_de"]
            new_chunks[ordinal - 1] = str(occurrence["applied_render_de"])
        old_actions = set(parse_ordinals(old["action_ordinals"]))
        added_surfaces = split_pipe(spec["added_action_surfaces"])
        licensed_source_surfaces = [surface for _, surface in hits if card_by_surface[surface]["action_license"] == "1"]
        assert added_surfaces == licensed_source_surfaces
        added_ordinals = {ordinal for ordinal, surface in hits if surface in added_surfaces}
        assert len(added_ordinals) == len(added_surfaces)
        assert all(card_by_surface[surface]["action_license"] == "1" for surface in added_surfaces)
        new_actions = old_actions | added_ordinals
        completed: dict[str, object] = {
            "line_rank": int(spec["line_rank"]),
            "page": old["page"],
            "locus": old["locus"],
            "section": old["section"],
            "language": old["language"],
            "hand": old["hand"],
            "token_count": len(tokens),
            "closed_ordinals": "|".join(str(value) for value, _ in hits),
            "closed_surfaces": "|".join(surface for _, surface in hits),
            "old_line_mode": old["line_mode"],
            "new_line_mode": spec["new_line_mode"],
            "old_action_ordinals": old["action_ordinals"],
            "new_action_ordinals": "|".join(map(str, sorted(new_actions))) or "NONE",
            "new_action_surfaces": "|".join(tokens[value - 1] for value in sorted(new_actions)) or "NONE",
            "added_action_ordinals": "|".join(map(str, sorted(added_ordinals))) or "NONE",
            "added_action_surfaces": spec["added_action_surfaces"],
            "zl3b_line": old["zl3b_line"],
            "old_literal_token_glosses_de": old["literal_token_glosses_de"],
            "new_literal_token_glosses_de": " | ".join(new_literal),
            "old_aligned_line_de": old["aligned_line_de"],
            "aligned_line_de": " · ".join(new_chunks) + ".",
            "practical_translation_de": spec["practical_translation_de"],
            "review_note": spec["review_note"],
        }
        assert "⟦" not in str(completed["aligned_line_de"])
        assert ":?]" not in str(completed["new_literal_token_glosses_de"])
        assert not HARD_GENERIC.search(str(completed["aligned_line_de"]))
        assert not HARD_GENERIC.search(str(completed["practical_translation_de"]))
        completed_rows.append(completed)
        completed_by_locus[old["locus"]] = completed

    v56_rows: list[dict[str, object]] = []
    distribution: Counter[int] = Counter()
    for old in v55_lines:
        completed = completed_by_locus.get(old["locus"])
        if completed:
            actions = parse_ordinals(str(completed["new_action_ordinals"]))
            row: dict[str, object] = {
                "page": old["page"], "locus": old["locus"], "section": old["section"],
                "language": old["language"], "hand": old["hand"], "token_count": old["token_count"],
                "new_v50_positions": old["new_v50_positions"], "new_v51_positions": old["new_v51_positions"],
                "new_v52_positions": old["new_v52_positions"], "new_v53_positions": old["new_v53_positions"],
                "new_v54_positions": old["new_v54_positions"], "new_v55_positions": old["new_v55_positions"],
                "new_v56_positions": 7, "residual_unknown_positions": 0, "assigned_fraction": "1.000000",
                "complete": "1", "action_positions": len(actions),
                "action_ordinals": completed["new_action_ordinals"], "action_surfaces": completed["new_action_surfaces"],
                "line_mode": completed["new_line_mode"], "v54_target_surfaces": old["v54_target_surfaces"],
                "v55_target_surfaces": old["v55_target_surfaces"], "v56_target_surfaces": completed["closed_surfaces"],
                "remaining_unknown_surfaces": "NONE", "zl3b_line": old["zl3b_line"],
                "literal_token_glosses_de": completed["new_literal_token_glosses_de"],
                "aligned_line_de": completed["aligned_line_de"],
                "practical_translation_de": completed["practical_translation_de"], "review_note": completed["review_note"],
            }
        else:
            row = {
                "page": old["page"], "locus": old["locus"], "section": old["section"],
                "language": old["language"], "hand": old["hand"], "token_count": old["token_count"],
                "new_v50_positions": old["new_v50_positions"], "new_v51_positions": old["new_v51_positions"],
                "new_v52_positions": old["new_v52_positions"], "new_v53_positions": old["new_v53_positions"],
                "new_v54_positions": old["new_v54_positions"], "new_v55_positions": old["new_v55_positions"],
                "new_v56_positions": 0, "residual_unknown_positions": old["residual_unknown_positions"],
                "assigned_fraction": old["assigned_fraction"], "complete": old["complete"],
                "action_positions": old["action_positions"], "action_ordinals": old["action_ordinals"],
                "action_surfaces": old["action_surfaces"], "line_mode": old["line_mode"],
                "v54_target_surfaces": old["v54_target_surfaces"], "v55_target_surfaces": old["v55_target_surfaces"],
                "v56_target_surfaces": "NONE", "remaining_unknown_surfaces": old["remaining_unknown_surfaces"],
                "zl3b_line": old["zl3b_line"], "literal_token_glosses_de": old["literal_token_glosses_de"],
                "aligned_line_de": old["aligned_line_de"], "practical_translation_de": old["practical_translation_de"],
                "review_note": old["review_note"],
            }
        distribution[int(row["residual_unknown_positions"])] += 1
        assert not HARD_GENERIC.search(str(row["aligned_line_de"]))
        assert not HARD_GENERIC.search(str(row["practical_translation_de"]))
        v56_rows.append(row)

    assert sum(int(row["token_count"]) for row in v56_rows) == 479
    assert sum(int(row["new_v56_positions"]) for row in v56_rows) == 7
    assert sum(int(row["residual_unknown_positions"]) for row in v56_rows) == 0
    assert sum(row["complete"] == "1" for row in v56_rows) == 51
    assert distribution == {0: 51}

    after_unknown = current_unknown - target_keys
    assert len(after_unknown) == 7556
    current_by_locus = Counter(locus for locus, _ in current_unknown)
    after_by_locus = Counter(locus for locus, _ in after_unknown)
    complete_before = sum(current_by_locus[line["locus"]] == 0 for line in panel)
    complete_after = sum(after_by_locus[line["locus"]] == 0 for line in panel)
    newly_closed_loci = [
        line["locus"] for line in panel
        if current_by_locus[line["locus"]] > 0 and after_by_locus[line["locus"]] == 0
    ]
    assert complete_before == 1439
    assert complete_after == 1440
    assert newly_closed_loci == ["f105v.1"]

    global_closed_rows: list[dict[str, object]] = []
    for locus in sorted(newly_closed_loci):
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
        global_closed_rows.append(
            {
                "page": line["page"],
                "locus": locus,
                "section": line["section"],
                "language": line["language"],
                "hand": line["hand"],
                "token_count": len(tokens),
                "target_ordinals": "|".join(str(value) for value, _ in hits),
                "target_surfaces": "|".join(surface for _, surface in hits),
                "zl3b_line": line["zl3b_line"],
                "current_literal_de": " | ".join(before_glosses),
                "after_literal_de": " | ".join(after_glosses),
                "practical_translation_de": (
                    source_by_locus[locus]["practical_translation_de"]
                    if locus in source_by_locus
                    else " · ".join(after_glosses) + "."
                ),
            }
        )

    prediction_rows = [
        {"prediction_id": "GDT682-P01", "observed_family": "oar|oair|oaiir", "visible_difference": "zero, one and two internal i strokes inside the same O preparation frame", "predicted_semantic_difference": "first, second and third preparation fraction", "held_positions": "4/4 OAIR positions", "next_unseen_test": "another O plus fraction form should change only the fraction index and retain preparation scope"},
        {"prediction_id": "GDT682-P02", "observed_family": "pol|air|polairy", "visible_difference": "powder-material head followed by second-fraction and closed-state fields", "predicted_semantic_difference": "powder material becomes a closed second powder fraction", "held_positions": "1/1 POLAIRY position", "next_unseen_test": "another POL plus fraction tail should retain powder material while the tail controls index or state"},
        {"prediction_id": "GDT682-P03", "observed_family": "pcheey|olpcheey", "visible_difference": "published dry powder form II receives O preparation and L wood-drug wrappers", "predicted_semantic_difference": "dry powder form II becomes fully dried powder from wood-drug preparation", "held_positions": "1/1 OLPCHEEY position", "next_unseen_test": "another material wrapper around PCHEEY should replace only the drug material and retain dry powder form II"},
        {"prediction_id": "GDT682-P04", "observed_family": "pchedaiin|opchedaiin", "visible_difference": "published three-dose middle-dry powder card receives O preparation frame", "predicted_semantic_difference": "three dry powder doses become three doses of a dried powder preparation", "held_positions": "4/4 OPCHEDAIIN positions", "next_unseen_test": "another wrapper around PCHEDAIIN should retain powder, middle drying and three-dose quantity"},
        {"prediction_id": "GDT682-P05", "observed_family": "dair|dairodg|dairody", "visible_difference": "second measured fraction receives O preparation and a terminal completion form", "predicted_semantic_difference": "measure the second fraction and finish it as a preparation", "held_positions": "3/3 DAIRODY positions", "next_unseen_test": "another DAIR-O completion should retain the measured second-fraction operation"},
        {"prediction_id": "GDT682-P06", "observed_family": "ypchedy|ypcheddy", "visible_difference": "one additional D inside the published anaphoric powder-drying command", "predicted_semantic_difference": "the longer form adds a terminal close step before final completion", "held_positions": "1/1 YPCHEDDY position", "next_unseen_test": "another PCHEDDY form should add closure without losing powder and middle-stage drying; drawing off remains the rival"},
        {"prediction_id": "GDT682-P07", "observed_family": "sary|sairy", "visible_difference": "one internal i stroke in an otherwise stable seed-fraction closed form", "predicted_semantic_difference": "closed first seed fraction becomes closed second seed fraction", "held_positions": "3/3 SAIRY positions", "next_unseen_test": "an SAIIRY form, if encountered, should denote the corresponding third closed seed fraction"},
    ]

    occurrence_fields = [
        "card_rank", "family", "surface", "card_type", "composition", "working_meaning_de",
        "applied_render_de", "strongest_rival_de", "confidence", "action_license", "page", "locus",
        "section", "language", "hand", "ordinal", "token_count", "line_position", "left_surface",
        "right_surface", "context_role", "context_verdict", "context_decision", "it2a_operation", "it2a_render", "rf1b_operation",
        "rf1b_render", "reader_support", "all_three_present", "all_present_exact", "zl3b_line",
        "context_before_de", "context_after_de", "literal_after_de", "review_note",
    ]
    family_fields = [
        *cards[0].keys(), "observed_occurrences", "observed_pages", "both_exact", "it2a_only_exact",
        "rf1b_only_exact", "neither_exact", "context_holds",
    ]
    boundary_fields = [
        *boundary_specs[0].keys(), "it2a_operation", "it2a_render", "rf1b_operation", "rf1b_render",
        "reader_support", "context_after_de",
    ]
    completed_fields = [
        "line_rank", "page", "locus", "section", "language", "hand", "token_count", "closed_ordinals",
        "closed_surfaces", "old_line_mode", "new_line_mode", "old_action_ordinals", "new_action_ordinals",
        "new_action_surfaces", "added_action_ordinals", "added_action_surfaces", "zl3b_line",
        "old_literal_token_glosses_de", "new_literal_token_glosses_de", "old_aligned_line_de",
        "aligned_line_de", "practical_translation_de", "review_note",
    ]
    v56_fields = [
        "page", "locus", "section", "language", "hand", "token_count", "new_v50_positions",
        "new_v51_positions", "new_v52_positions", "new_v53_positions", "new_v54_positions",
        "new_v55_positions", "new_v56_positions", "residual_unknown_positions",
        "assigned_fraction", "complete", "action_positions", "action_ordinals", "action_surfaces",
        "line_mode", "v54_target_surfaces", "v55_target_surfaces", "v56_target_surfaces",
        "remaining_unknown_surfaces", "zl3b_line",
        "literal_token_glosses_de", "aligned_line_de", "practical_translation_de", "review_note",
    ]
    global_fields = [
        "page", "locus", "section", "language", "hand", "token_count", "target_ordinals",
        "target_surfaces", "zl3b_line", "current_literal_de", "after_literal_de", "practical_translation_de",
    ]
    write_tsv(output_dir / "TARGET_FAMILY_CARDS.tsv", family_rows, family_fields)
    write_tsv(output_dir / "CONTEXT_ROLE_VERDICTS.tsv", context_specs, list(context_specs[0].keys()))
    write_tsv(output_dir / "TARGET_EXACT_OCCURRENCE_AUDIT.tsv", occurrence_rows, occurrence_fields)
    write_tsv(output_dir / "BOUNDARY_DECISIONS.tsv", boundary_rows, boundary_fields)
    write_tsv(output_dir / "FINAL_COMPLETED_LINE_V56.tsv", completed_rows, completed_fields)
    write_tsv(output_dir / "V56_51_LINE_READER.tsv", v56_rows, v56_fields)
    write_tsv(output_dir / "GLOBAL_NEWLY_COMPLETED_LINES.tsv", global_closed_rows, global_fields)
    write_tsv(
        output_dir / "FAMILY_PREDICTIONS.tsv",
        prediction_rows,
        ["prediction_id", "observed_family", "visible_difference", "predicted_semantic_difference", "held_positions", "next_unseen_test"],
    )
    write_tsv(output_dir / "HISTORICAL_ANALOG_ATLAS.tsv", analog_specs, list(analog_specs[0].keys()))

    reader_doc = [
        "# GDT682 — completed V56 practical reading",
        "",
        "The TSV companion preserves every ZL3b token and every reader decision. This is a concrete replaceable working reading, not claimed plaintext.",
        "",
    ]
    for row in completed_rows:
        reader_doc.extend(
            [
                f"## {row['line_rank']}. {row['locus']} · {row['new_line_mode']}",
                "",
                f"**ZL3b:** `{row['zl3b_line']}`",
                "",
                f"**Praxislesung:** {row['practical_translation_de']}",
                "",
                f"**Tokenparallel:** {row['aligned_line_de']}",
                "",
                f"**Neu geschlossen:** `{row['closed_surfaces']}`",
                "",
                f"**Aktionen:** {row['new_action_ordinals']} ({row['new_action_surfaces']})",
                "",
                f"**Leserentscheidung:** {row['review_note']}",
                "",
            ]
        )
    (output_dir / "GDT682_FINAL_COMPLETED_PRACTICAL_READER.md").write_text(
        "\n".join(reader_doc).rstrip() + "\n", encoding="utf-8"
    )

    action_before = sum(int(row["action_positions"]) for row in v55_lines)
    action_after = sum(int(row["action_positions"]) for row in v56_rows)
    mode_counts = Counter(str(row["line_mode"]) for row in v56_rows)
    assert action_before == 85
    assert action_after == 86
    assert mode_counts == {"ACTION_SEQUENCE": 16, "MIXED_RECORD": 23, "NOMINAL_REGISTER": 6, "QUANTITY_LABEL": 6}
    legacy_marker = "Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz"
    legacy_generic_token_positions = sum(
        gloss == legacy_marker
        for row in v56_rows
        for gloss in split_parallel(str(row["literal_token_glosses_de"]))
    )
    legacy_generic_loci = sorted({
        str(row["locus"]) for row in v56_rows if legacy_marker in str(row["literal_token_glosses_de"])
    })
    legacy_generic_practical_loci = sorted(
        str(row["locus"]) for row in v56_rows if "Ansatz/Gut" in str(row["practical_translation_de"])
    )
    assert legacy_generic_loci == ["f112r.36", "f115r.1", "f80r.17", "f80v.35", "f86v5.2", "f86v6.4"]
    assert legacy_generic_token_positions == 6
    assert legacy_generic_practical_loci == ["f112r.36", "f86v5.2"]

    result: dict[str, object] = {
        "status": "PASS_7_NEW_CARDS__17_CONTEXTS_HOLD__FINAL_V56_LINE_CLOSED__V56_COMPLETE",
        "basis": {
            "panel_lines": 4128,
            "panel_pages": len({row["page"] for row in panel}),
            "target_lines": 11,
            "target_pages": len({str(row["page"]) for row in occurrence_rows}),
            "target_occurrences": 17,
            "target_surfaces": 7,
            "source_seven_hole_lines": 1,
            "source_open_positions": 7,
            "source_distinct_surfaces": 7,
            "inherited_cards_reused": 0,
            "new_pages_opened": 0,
            "f84": "FORBIDDEN",
            "f84r": "FORBIDDEN",
            "cross_guard": cross_guard,
        },
        "cards": {
            "types": dict(sorted(Counter(row["card_type"] for row in cards).items())),
            "context_holds": sum(row["context_verdict"].startswith("HOLD") for row in context_specs),
            "context_conflicts": sum(row["context_verdict"].startswith("CONFLICT") for row in context_specs),
            "licensed_action_cards": sum(int(row["action_license"]) for row in cards),
            "historical_analogs": len(analog_specs),
            "forward_predictions": len(prediction_rows),
        },
        "reader_support": dict(sorted(support_counts.items())),
        "boundary_decisions": {
            "recorded": len(boundary_rows),
            "non_both_exact": len(non_both_keys),
            "neither_exact": support_counts["NEITHER_EXACT"],
            "bilateral_reader_repairs": [],
            "local_reader_rival": "f111v.33 ZL3b/RF1b oair versus IT2a qoair",
        },
        "global_overlay": {
            "unknown_positions_before": len(current_unknown),
            "unknown_positions_after": len(after_unknown),
            "new_assigned_positions": len(target_keys),
            "complete_lines_before": complete_before,
            "complete_lines_after": complete_after,
            "newly_completed_lines": len(newly_closed_loci),
            "newly_completed_outside_source": [],
        },
        "v56_reader": {
            "lines": 51,
            "tokens": 479,
            "unknown_before": 7,
            "unknown_after": 0,
            "assigned_before": 472,
            "assigned_after": 479,
            "assigned_fraction_after": "1.000000",
            "complete_before": 50,
            "complete_after": 51,
            "unknown_distribution": {str(key): distribution[key] for key in sorted(distribution)},
            "licensed_action_positions_before": action_before,
            "licensed_action_positions_after": action_after,
            "new_action_positions": action_after - action_before,
            "modes": dict(sorted(mode_counts.items())),
            "hard_generic_hits": sum(
                len(HARD_GENERIC.findall(str(row["aligned_line_de"])))
                + len(HARD_GENERIC.findall(str(row["practical_translation_de"])))
                for row in v56_rows
            ),
            "legacy_generic_token_positions": legacy_generic_token_positions,
            "legacy_generic_loci": legacy_generic_loci,
            "legacy_generic_practical_lines": legacy_generic_practical_loci,
        },
        "weakest_cards": [
            {"surface": "ypcheddy", "reason": "the visible extra D is rendered as closure before final completion, but drawing off or scribal expansion remains a live rival"},
            {"surface": "polairy", "reason": "the singleton is compositionally strong but lacks an independent whole-form context"},
            {"surface": "olpcheey", "reason": "the singleton securely preserves wood-drug powder, while full drying versus dry binding remains replaceable"},
            {"surface": "dairody", "reason": "two external registers select a finished measured fraction, while the source admits an imperative measure-and-finish parse"},
            {"surface": "oair", "reason": "one of four occurrences has an IT2a Q-command join, quarantined locally against three triply exact nominal contexts"},
        ],
        "claim_ceiling": (
            "Seven new replaceable working cards apply with one practical core to all 17 exact ZL3b occurrences "
            "on the already admitted panel. They close the final seven positions of the 51-line reader, whose 479 "
            "positions now all have assigned defaults. Six inherited OL positions remain explicit semantic debt rather "
            "than being mislabeled as concrete. The resulting source reading is a powder recipe with a second "
            "preparation fraction, wood-drug powder, heat grade III, three doses, a finished measured fraction and a "
            "provisionally, powder of a closed second seed fraction dried to the middle stage and finished. This is a concrete mixed "
            "learned-whole and productive-component working renderer, not confirmed plaintext, phonetics, historical "
            "codebook identity, exact plant species, disease, patient, cure, carrier liquid or manuscript-wide "
            "translation. Every named rival remains replaceable."
        ),
        "files": {},
    }
    artifact_names = [
        "TARGET_FAMILY_CARDS.tsv",
        "CONTEXT_ROLE_VERDICTS.tsv",
        "TARGET_EXACT_OCCURRENCE_AUDIT.tsv",
        "BOUNDARY_DECISIONS.tsv",
        "FINAL_COMPLETED_LINE_V56.tsv",
        "V56_51_LINE_READER.tsv",
        "GLOBAL_NEWLY_COMPLETED_LINES.tsv",
        "FAMILY_PREDICTIONS.tsv",
        "HISTORICAL_ANALOG_ATLAS.tsv",
        "GDT682_FINAL_COMPLETED_PRACTICAL_READER.md",
    ]
    result["files"] = {name: sha256(output_dir / name) for name in artifact_names}
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    build(ART)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
