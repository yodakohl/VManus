#!/usr/bin/env python3
"""Build the GDT677 nine-family completion and V51 reader."""

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
EXP = ROOT / "experiments/yolo/gdt677_nine_one_hole_family_completion"
ART = EXP / "artifacts"
PANEL_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
GDT673_OCCURRENCES_PATH = ROOT / "experiments/yolo/gdt673_v48_transfer_occurrence_conflict_scan/artifacts/TRANSFERABLE_EXACT_OCCURRENCES.tsv"
GDT674_RESULT_PATH = ROOT / "experiments/yolo/gdt674_v49_f81r_concrete_renderer/artifacts/RESULT.json"
GDT675_OCCURRENCES_PATH = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan/artifacts/EXTERNAL_TRANSFERABLE_OCCURRENCES.tsv"
GDT675_RESULT_PATH = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan/artifacts/RESULT.json"
V50_READER_PATH = ROOT / "experiments/yolo/gdt676_v50_external_line_renderer/artifacts/V50_EXTERNAL_LINE_READER.tsv"
GDT676_RESULT_PATH = ROOT / "experiments/yolo/gdt676_v50_external_line_renderer/artifacts/RESULT.json"
CROSS_PATH = Path("transcription/voynich_cross_transcription_lines.tsv")
CARD_PATH = EXP / "src/TARGET_CARD_SPECS.tsv"
CONTEXT_PATH = EXP / "src/OCCURRENCE_CONTEXT_SPECS.tsv"
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
    """Use the inherited exact-token / low-cost-boundary alignment."""
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


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(CARD_PATH)
    context_specs = read_tsv(CONTEXT_PATH)
    analog_specs = read_tsv(ANALOG_PATH)
    panel = read_tsv(PANEL_PATH)
    gdt673_occurrences = read_tsv(GDT673_OCCURRENCES_PATH)
    gdt675_occurrences = read_tsv(GDT675_OCCURRENCES_PATH)
    v50_lines = read_tsv(V50_READER_PATH)
    gdt674_result = json.loads(GDT674_RESULT_PATH.read_text(encoding="utf-8"))
    gdt675_result = json.loads(GDT675_RESULT_PATH.read_text(encoding="utf-8"))
    gdt676_result = json.loads(GDT676_RESULT_PATH.read_text(encoding="utf-8"))

    assert len(cards) == 9
    assert len({row["surface"] for row in cards}) == 9
    assert len(context_specs) == 20
    assert len({(row["locus"], int(row["ordinal"])) for row in context_specs}) == 20
    assert len(v50_lines) == 51
    assert len(panel) == 4128
    assert all(not row["page"].lower().startswith("f84") for row in panel)
    assert gdt675_result["coverage_overlay"]["unknown_positions_after"] == 7943
    assert gdt676_result["information"]["unknown_after_v50"] == 136
    assert gdt674_result["status"].startswith("PASS_")

    card_by_surface = {row["surface"]: row for row in cards}
    v50_by_locus = {row["locus"]: row for row in v50_lines}
    context_by_key = {(row["locus"], int(row["ordinal"])): row for row in context_specs}
    inherited_overlay_keys = {
        (row["locus"], int(row["ordinal"])) for row in [*gdt673_occurrences, *gdt675_occurrences]
    }

    raw_occurrences: list[tuple[dict[str, str], int, str]] = []
    for line in panel:
        for ordinal, surface in enumerate(line["zl3b_line"].split(), start=1):
            if surface in card_by_surface:
                raw_occurrences.append((line, ordinal, surface))
    assert len(raw_occurrences) == 20
    assert Counter(surface for _, _, surface in raw_occurrences) == {
        row["surface"]: int(row["expected_occurrences"]) for row in cards
    }
    assert {(line["locus"], ordinal) for line, ordinal, _ in raw_occurrences} == set(context_by_key)
    assert all((line["locus"], ordinal) not in inherited_overlay_keys for line, ordinal, _ in raw_occurrences)

    target_loci = sorted({line["locus"] for line, _, _ in raw_occurrences})
    assert len(target_loci) == 20
    cross_rows, cross_guard = guarded_cross_query(target_loci)
    assert cross_guard["selected"] == len(cross_rows) == 20
    assert cross_guard["skipped_forbidden"] > 0
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    assert set(cross_by_locus) == set(target_loci)

    occurrence_rows: list[dict[str, object]] = []
    occurrence_by_key: dict[tuple[str, int], dict[str, object]] = {}
    sorted_occurrences = sorted(
        raw_occurrences,
        key=lambda item: (
            int(card_by_surface[item[2]]["family_rank"]), item[2], item[0]["locus"], item[1]
        ),
    )

    for line, ordinal, surface in sorted_occurrences:
        card = card_by_surface[surface]
        context = context_by_key[(line["locus"], ordinal)]
        tokens = line["zl3b_line"].split()
        glosses = split_parallel(line["token_glosses_de"])
        sources = split_parallel(line["gloss_sources"])
        states = split_parallel(line["scope_states"])
        assert len(tokens) == len(glosses) == len(sources) == len(states) == int(line["token_count"])
        assert tokens[ordinal - 1] == surface
        assert glosses[ordinal - 1] == f"[{surface}:?]"
        assert states[ordinal - 1] == "UNKNOWN_SURFACE"
        after_glosses = list(glosses)
        after_glosses[ordinal - 1] = card["working_meaning_de"]
        cross = cross_by_locus[line["locus"]]
        assert cross["zl3b_clean"].split() == tokens
        it2a_ops = reader_operations(tokens, cross["it2a_clean"].split())
        rf1b_ops = reader_operations(tokens, cross["rf1b_clean"].split())
        it2a_operation, it2a_render = it2a_ops[ordinal - 1]
        rf1b_operation, rf1b_render = rf1b_ops[ordinal - 1]
        reader_support = (
            "BOTH_EXACT" if it2a_operation == rf1b_operation == "EXACT"
            else "ONE_EXACT" if "EXACT" in {it2a_operation, rf1b_operation}
            else "NEITHER_EXACT"
        )

        if line["locus"] in v50_by_locus:
            v50 = v50_by_locus[line["locus"]]
            before_chunks = v50["working_line_de"].rstrip(".").split(" · ")
            literal_before = split_parallel(v50["literal_token_glosses_de"])
            assert len(before_chunks) == len(literal_before) == len(tokens)
            assert before_chunks[ordinal - 1] == f"⟦{surface}:?⟧"
            assert literal_before[ordinal - 1] == f"[{surface}:?]"
            context_basis = "GDT676_V50_LINE_READER"
        else:
            before_chunks = [unknown_chunk(gloss) for gloss in glosses]
            literal_before = glosses
            context_basis = "GDT671_V48_PANEL"
        after_chunks = list(before_chunks)
        after_chunks[ordinal - 1] = context["working_render_de"]
        literal_after = list(literal_before)
        literal_after[ordinal - 1] = card["working_meaning_de"]

        item: dict[str, object] = {
            "family_rank": int(card["family_rank"]), "family": card["family"],
            "surface": surface, "card_type": card["card_type"], "composition": card["composition"],
            "working_meaning_de": card["working_meaning_de"], "strongest_rival_de": card["strongest_rival_de"],
            "confidence": card["confidence"], "page": line["page"], "locus": line["locus"],
            "section": line["section"], "language": line["language"], "hand": line["hand"],
            "ordinal": ordinal, "token_count": len(tokens), "line_position": position_class(ordinal, len(tokens)),
            "context_basis": context_basis, "context_decision": context["context_decision"],
            "action_license": context["action_license"], "it2a_operation": it2a_operation,
            "it2a_render": it2a_render, "rf1b_operation": rf1b_operation, "rf1b_render": rf1b_render,
            "reader_support": reader_support, "all_three_present": cross["all_three_present"],
            "all_present_exact": cross["all_present_exact"], "zl3b_line": line["zl3b_line"],
            "context_before_de": " · ".join(before_chunks) + ".",
            "context_after_de": " · ".join(after_chunks) + ".",
            "literal_after_de": " | ".join(literal_after), "review_note": context["review_note"],
        }
        occurrence_rows.append(item)
        occurrence_by_key[(line["locus"], ordinal)] = item

    assert len(occurrence_rows) == 20
    assert all(not HARD_GENERIC.search(str(row["context_after_de"])) for row in occurrence_rows)
    assert all(str(row["context_decision"]).startswith("HOLD_") for row in occurrence_rows)

    family_rows: list[dict[str, object]] = []
    for card in sorted(cards, key=lambda row: (int(row["family_rank"]), row["surface"])):
        rows = [row for row in occurrence_rows if row["surface"] == card["surface"]]
        support = Counter(str(row["reader_support"]) for row in rows)
        decisions = Counter(str(row["context_decision"]) for row in rows)
        family_rows.append({
            **card, "observed_occurrences": len(rows), "observed_pages": len({str(row["page"]) for row in rows}),
            "both_exact": support["BOTH_EXACT"], "one_exact": support["ONE_EXACT"],
            "neither_exact": support["NEITHER_EXACT"],
            "context_holds": sum(value for key, value in decisions.items() if key.startswith("HOLD_")),
            "licensed_actions": sum(int(row["action_license"]) for row in rows),
        })
        assert len(rows) == int(card["expected_occurrences"])
        assert len({str(row["page"]) for row in rows}) == int(card["expected_pages"])

    completed_rows: list[dict[str, object]] = []
    completed_by_locus: dict[str, dict[str, object]] = {}
    for v50 in v50_lines:
        tokens = v50["zl3b_line"].split()
        hits = [(ordinal, surface) for ordinal, surface in enumerate(tokens, start=1) if surface in card_by_surface]
        if not hits:
            continue
        assert len(hits) == 1
        ordinal, surface = hits[0]
        assert int(v50["residual_unknown_positions"]) == 1
        occurrence = occurrence_by_key[(v50["locus"], ordinal)]
        old_chunks = v50["working_line_de"].rstrip(".").split(" · ")
        old_literal = split_parallel(v50["literal_token_glosses_de"])
        assert len(old_chunks) == len(old_literal) == len(tokens)
        assert old_chunks[ordinal - 1] == f"⟦{surface}:?⟧"
        assert old_literal[ordinal - 1] == f"[{surface}:?]"
        new_chunks = list(old_chunks)
        new_chunks[ordinal - 1] = str(occurrence["context_after_de"]).rstrip(".").split(" · ")[ordinal - 1]
        new_literal = list(old_literal)
        new_literal[ordinal - 1] = card_by_surface[surface]["working_meaning_de"]
        old_actions = set(parse_ordinals(v50["action_ordinals"]))
        new_actions = set(old_actions)
        if occurrence["action_license"] == "1":
            new_actions.add(ordinal)
        new_mode = v50["line_mode"]
        if new_actions != old_actions and new_mode in {"NOMINAL_REGISTER", "QUANTITY_LABEL"}:
            new_mode = "MIXED_RECORD"
        completed = {
            "page": v50["page"], "locus": v50["locus"], "section": v50["section"],
            "language": v50["language"], "hand": v50["hand"], "token_count": len(tokens),
            "closed_ordinal": ordinal, "closed_surface": surface,
            "composition": card_by_surface[surface]["composition"],
            "working_meaning_de": card_by_surface[surface]["working_meaning_de"],
            "confidence": card_by_surface[surface]["confidence"], "old_line_mode": v50["line_mode"],
            "new_line_mode": new_mode, "old_action_ordinals": v50["action_ordinals"],
            "new_action_ordinals": "|".join(map(str, sorted(new_actions))) or "NONE",
            "new_action_surfaces": "|".join(tokens[value - 1] for value in sorted(new_actions)) or "NONE",
            "zl3b_line": v50["zl3b_line"], "old_literal_token_glosses_de": v50["literal_token_glosses_de"],
            "new_literal_token_glosses_de": " | ".join(new_literal),
            "old_working_line_de": v50["working_line_de"], "working_line_de": " · ".join(new_chunks) + ".",
            "review_note": f"GDT677 closes {surface}; {occurrence['review_note']}",
        }
        assert not HARD_GENERIC.search(str(completed["working_line_de"]))
        completed_rows.append(completed)
        completed_by_locus[v50["locus"]] = completed

    assert len(completed_rows) == 9
    assert len(completed_by_locus) == 9

    v51_rows: list[dict[str, object]] = []
    distribution = Counter()
    for v50 in v50_lines:
        completed = completed_by_locus.get(v50["locus"])
        if completed:
            residual = 0
            actions = parse_ordinals(str(completed["new_action_ordinals"]))
            row = {
                "page": v50["page"], "locus": v50["locus"], "section": v50["section"],
                "language": v50["language"], "hand": v50["hand"], "token_count": v50["token_count"],
                "new_v50_positions": v50["new_v50_positions"], "new_v51_positions": 1,
                "residual_unknown_positions": residual, "assigned_fraction": "1.000000", "complete": "1",
                "action_positions": len(actions), "action_ordinals": completed["new_action_ordinals"],
                "action_surfaces": completed["new_action_surfaces"], "line_mode": completed["new_line_mode"],
                "v51_target_surface": completed["closed_surface"], "remaining_unknown_surfaces": "NONE",
                "zl3b_line": v50["zl3b_line"], "literal_token_glosses_de": completed["new_literal_token_glosses_de"],
                "working_line_de": completed["working_line_de"], "review_note": completed["review_note"],
            }
        else:
            residual = int(v50["residual_unknown_positions"])
            row = {
                "page": v50["page"], "locus": v50["locus"], "section": v50["section"],
                "language": v50["language"], "hand": v50["hand"], "token_count": v50["token_count"],
                "new_v50_positions": v50["new_v50_positions"], "new_v51_positions": 0,
                "residual_unknown_positions": residual,
                "assigned_fraction": f"{(int(v50['token_count']) - residual) / int(v50['token_count']):.6f}",
                "complete": v50["complete"], "action_positions": v50["action_positions"],
                "action_ordinals": v50["action_ordinals"], "action_surfaces": v50["action_surfaces"],
                "line_mode": v50["line_mode"], "v51_target_surface": "NONE",
                "remaining_unknown_surfaces": v50["remaining_unknown_surfaces"], "zl3b_line": v50["zl3b_line"],
                "literal_token_glosses_de": v50["literal_token_glosses_de"],
                "working_line_de": v50["working_line_de"], "review_note": v50["review_note"],
            }
        distribution[residual] += 1
        v51_rows.append(row)

    assert sum(int(row["token_count"]) for row in v51_rows) == 479
    assert sum(int(row["residual_unknown_positions"]) for row in v51_rows) == 127
    assert sum(row["complete"] == "1" for row in v51_rows) == 11
    assert distribution == {0: 11, 2: 17, 3: 8, 4: 8, 5: 6, 7: 1}
    assert all(not HARD_GENERIC.search(str(row["working_line_de"])) for row in v51_rows)

    prediction_rows = [
        {"prediction_id": "GDT677-P01", "observed_pair": "ltaiin|oltaiin", "visible_difference": "initial o",
         "predicted_semantic_difference": "Holzdroge -> Holzdrogenansatz", "held_positions": "2/2",
         "next_unseen_test": "an exact l/ol cold-grade sister pair should preserve grade and change only preparation status"},
        {"prediction_id": "GDT677-P02", "observed_pair": "ykcho|kchody", "visible_difference": "initial y versus terminal dy",
         "predicted_semantic_difference": "anaphoric preparation versus completed hot-dry result", "held_positions": "8/8",
         "next_unseen_test": "a new y+kcho context should permit backward reference; a kcho+dy context should be result-like"},
        {"prediction_id": "GDT677-P03", "observed_pair": "olchain|lolkaiin", "visible_difference": "ol+ch+ain versus lol+k+aiin",
         "predicted_semantic_difference": "wood preparation dry-II versus wood material hot-III", "held_positions": "2/2",
         "next_unseen_test": "chain and kaiin sisters should preserve dry-II and hot-III under additional material heads"},
        {"prediction_id": "GDT677-P04", "observed_pair": "ar|or|aror", "visible_difference": "fraction-I plus portion",
         "predicted_semantic_difference": "one portion nested inside the first drug fraction", "held_positions": "6/6",
         "next_unseen_test": "another exact aror occurrence should remain a quantity rather than a plant or action"},
        {"prediction_id": "GDT677-P05", "observed_pair": "taiky", "visible_difference": "t ... ky with opaque local middle",
         "predicted_semantic_difference": "cold-set batch lightly warmed", "held_positions": "1/1",
         "next_unseen_test": "aiky may test the learned inner block, but no productive ai rule is asserted"},
        {"prediction_id": "GDT677-P06", "observed_pair": "losair", "visible_difference": "RF1b los+air versus unsplit lo+sair",
         "predicted_semantic_difference": "second fraction of a drugwood batch versus wood decoction with seed fraction II", "held_positions": "1/1",
         "next_unseen_test": "a new occurrence or reader boundary must distinguish the two fully visible parses"},
    ]

    occurrence_fields = [
        "family_rank", "family", "surface", "card_type", "composition", "working_meaning_de",
        "strongest_rival_de", "confidence", "page", "locus", "section", "language", "hand", "ordinal",
        "token_count", "line_position", "context_basis", "context_decision", "action_license", "it2a_operation",
        "it2a_render", "rf1b_operation", "rf1b_render", "reader_support", "all_three_present", "all_present_exact",
        "zl3b_line", "context_before_de", "context_after_de", "literal_after_de", "review_note",
    ]
    family_fields = [
        *cards[0].keys(), "observed_occurrences", "observed_pages", "both_exact", "one_exact",
        "neither_exact", "context_holds", "licensed_actions",
    ]
    completed_fields = [
        "page", "locus", "section", "language", "hand", "token_count", "closed_ordinal", "closed_surface",
        "composition", "working_meaning_de", "confidence", "old_line_mode", "new_line_mode",
        "old_action_ordinals", "new_action_ordinals", "new_action_surfaces", "zl3b_line",
        "old_literal_token_glosses_de", "new_literal_token_glosses_de", "old_working_line_de",
        "working_line_de", "review_note",
    ]
    v51_fields = [
        "page", "locus", "section", "language", "hand", "token_count", "new_v50_positions",
        "new_v51_positions", "residual_unknown_positions", "assigned_fraction", "complete", "action_positions",
        "action_ordinals", "action_surfaces", "line_mode", "v51_target_surface", "remaining_unknown_surfaces",
        "zl3b_line", "literal_token_glosses_de", "working_line_de", "review_note",
    ]
    write_tsv(output_dir / "TARGET_FAMILY_CARDS.tsv", family_rows, family_fields)
    write_tsv(output_dir / "TARGET_EXACT_OCCURRENCE_AUDIT.tsv", occurrence_rows, occurrence_fields)
    write_tsv(output_dir / "NINE_COMPLETED_LINES_V51.tsv", completed_rows, completed_fields)
    write_tsv(output_dir / "V51_51_LINE_READER.tsv", v51_rows, v51_fields)
    write_tsv(output_dir / "FAMILY_PREDICTIONS.tsv", prediction_rows,
              ["prediction_id", "observed_pair", "visible_difference", "predicted_semantic_difference", "held_positions", "next_unseen_test"])
    write_tsv(output_dir / "HISTORICAL_ANALOG_ATLAS.tsv", analog_specs, list(analog_specs[0].keys()))

    reader_doc = [
        "# GDT677 — nine newly completed V51 lines", "",
        "Each Voynich token remains visible in the TSV companion. These are concrete replaceable working readings, not claimed plaintext.", "",
    ]
    for row in completed_rows:
        reader_doc.extend([
            f"## {row['locus']} · {row['new_line_mode']}", "", f"**ZL3b:** `{row['zl3b_line']}`", "",
            f"**Arbeitslesung:** {row['working_line_de']}", "",
            f"**Geschlossen:** `{row['closed_surface']}` = {row['working_meaning_de']} (`{row['composition']}`)", "",
            f"**Aktionen:** {row['new_action_ordinals']} ({row['new_action_surfaces']})", "",
            f"**Audit:** {row['review_note']}", "",
        ])
    (output_dir / "GDT677_NINE_COMPLETED_WORKING_READER.md").write_text(
        "\n".join(reader_doc).rstrip() + "\n", encoding="utf-8"
    )

    action_positions_before = gdt676_result["lines"]["licensed_action_positions"]
    action_positions_after = sum(int(row["action_positions"]) for row in v51_rows)
    mode_counts = Counter(str(row["line_mode"]) for row in v51_rows)
    reader_counts = Counter(str(row["reader_support"]) for row in occurrence_rows)
    result: dict[str, object] = {
        "status": "PASS_9_FAMILY_CARDS__20_CONTEXTS_HOLD__9_LINES_CLOSED__V51_127_OPEN",
        "basis": {
            "panel_lines": 4128, "panel_pages": len({row["page"] for row in panel}), "target_lines": 20,
            "target_pages": len({str(row["page"]) for row in occurrence_rows}), "target_occurrences": 20,
            "target_surfaces": 9, "new_pages_opened": 0, "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "cross_guard": cross_guard,
        },
        "cards": {
            "productive_compounds": sum(row["card_type"] == "PRODUCTIVE_COMPOUND" for row in cards),
            "reader_conditioned_compounds": sum(row["card_type"] == "READER_CONDITIONED_COMPOUND" for row in cards),
            "learned_exact_wholes": sum(row["card_type"] == "LEARNED_EXACT_WHOLE" for row in cards),
            "context_holds": sum(int(row["context_holds"]) for row in family_rows),
            "context_conflicts": 20 - sum(int(row["context_holds"]) for row in family_rows),
            "historical_analogs": len(analog_specs), "forward_predictions": len(prediction_rows),
        },
        "reader_support": dict(sorted(reader_counts.items())),
        "global_overlay": {
            "unknown_positions_before": 7943, "unknown_positions_after": 7923, "new_assigned_positions": 20,
            "complete_lines_before": gdt675_result["coverage_overlay"]["complete_lines_after"],
            "complete_lines_after": gdt675_result["coverage_overlay"]["complete_lines_after"] + 9,
            "newly_completed_lines": 9,
        },
        "v51_reader": {
            "lines": 51, "tokens": 479, "unknown_before": 136, "unknown_after": 127,
            "assigned_before": 343, "assigned_after": 352, "assigned_fraction_after": f"{352 / 479:.6f}",
            "complete_before": 2, "complete_after": 11,
            "unknown_distribution": {str(key): distribution[key] for key in sorted(distribution)},
            "licensed_action_positions_before": action_positions_before,
            "licensed_action_positions_after": action_positions_after, "modes": dict(sorted(mode_counts.items())),
            "hard_generic_hits": sum(len(HARD_GENERIC.findall(str(row["working_line_de"]))) for row in v51_rows),
        },
        "weakest_card": {"surface": "taiky", "reason": "the inner ai sequence stays opaque inside this exact whole and is not promoted as a productive stem"},
        "open_reader_rival": {
            "surface": "losair", "default": "RF1b los+air: zweite Fraktion des Drogenholzpostens",
            "rival": "lo+sair: Holzabsud mit Samenfraktion II",
        },
        "files": {},
        "claim_ceiling": (
            "Nine replaceable exact-surface working cards applied without meaning change to all twenty exact occurrences "
            "on the already admitted panel. They close nine previously one-hole V50 lines and reduce the 51-line deck "
            "from 136 to 127 explicit gaps. The cards are a concrete compositional working theory, not confirmed plaintext, "
            "phonetics, historical codebook identity, exact substances, plant species, disease, patient, cure, carrier liquid, "
            "or manuscript-wide translation. taiky remains a learned low-confidence whole and the losair reader split remains open."
        ),
    }
    artifact_names = [
        "TARGET_FAMILY_CARDS.tsv", "TARGET_EXACT_OCCURRENCE_AUDIT.tsv", "NINE_COMPLETED_LINES_V51.tsv",
        "V51_51_LINE_READER.tsv", "FAMILY_PREDICTIONS.tsv", "HISTORICAL_ANALOG_ATLAS.tsv",
        "GDT677_NINE_COMPLETED_WORKING_READER.md",
    ]
    result["files"] = {name: sha256(output_dir / name) for name in artifact_names}
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    build(ART)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
