#!/usr/bin/env python3
"""Independent validator for GDT674."""
from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt674_v49_f81r_concrete_renderer"
SRC = BASE / "src"
ART = BASE / "artifacts"
V48 = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
EXPECTED_STATUS = "PASS_F81R_210_TOKEN_CONCRETE_READER__27_REVIEW_POSITIONS__24_GAPS_CLOSED"
OUTPUT_NAMES = (
    "F81R_SOURCE_ALIGNMENT.tsv", "F81R_TOKEN_READINGS.tsv", "F81R_COMPONENT_TRACES.tsv",
    "F81R_REVIEW_CARDS.tsv", "F81R_READER_VARIANT_AUDIT.tsv", "F81R_LINE_READER.tsv",
    "F81R_EXPLICIT_ACTION_AUDIT.tsv", "F81R_VALUE_ATTACHMENT_AUDIT.tsv",
    "F81R_COVERAGE_OVERLAY.tsv", "F81R_PAGE_ARCHITECTURE.tsv",
    "LEGACY_TOKEN_RENDERER_AUDIT.tsv", "LEGACY_STATEMENT_BASELINE.tsv",
    "RENDERER_RULE_CARDS.tsv", "GDT674_F81R_CONCRETE_WORKING_READER.md", "RESULT.json",
)

GENERIC_FILLER = re.compile(
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


def guarded_query(rel: Path, columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    completed = subprocess.run(
        [
            str(ROOT / "vmanus-exp"), "query-tsv", str(rel),
            "--selector", "page", "--allow", "f81r", "--columns", columns,
            "--forbid-prefix", "f84",
        ],
        cwd=ROOT, check=True, text=True, capture_output=True,
    )
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("missing GUARD_STATS")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    return rows, {str(key): int(value) for key, value in json.loads(match.group(1)).items()}


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def align_reader_tokens(source: list[str], alternate: list[str]) -> list[tuple[str, tuple[int, ...], str]]:
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
        raise RuntimeError("reader alignment has no path")
    return final[2]


def reader_operations(source: list[str], alternate: list[str]) -> dict[int, tuple[str, str]]:
    result: dict[int, tuple[str, str]] = {}
    for operation, indices, rendered in align_reader_tokens(source, alternate):
        for index in indices:
            result[index] = ("EXACT" if operation == "ONE" and rendered == source[index] else operation, rendered or "EMPTY")
    if set(result) != set(range(len(source))):
        raise RuntimeError("reader alignment failed to cover source")
    return result


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, name: str, condition: bool, detail: str = "") -> None:
        self.rows.append({"name": name, "ok": bool(condition), "detail": detail})


def main() -> int:
    checks = Checks()
    try:
        source, token_guard = guarded_query(
            TOKENS_REL, "page,locus,token_index,eva,kind,section,language,hand",
        )
        cross, cross_guard = guarded_query(
            CROSS_REL, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
        )
        checks.add("guarded token selected", token_guard.get("selected") == 210, str(token_guard))
        checks.add("guarded cross selected", cross_guard.get("selected") == 31, str(cross_guard))
        checks.add("guard rejected token rows", token_guard.get("skipped_forbidden", 0) > 0, str(token_guard))
        checks.add("guard rejected cross rows", cross_guard.get("skipped_forbidden", 0) > 0, str(cross_guard))
        checks.add("source token census", len(source) == 210, str(len(source)))
        checks.add("source key uniqueness", len({(r["locus"], r["token_index"]) for r in source}) == 210)
        checks.add("source f81r only", all(r["page"] == "f81r" and not r["page"].startswith("f84") for r in source))
        checks.add("cross f81r only", all(r["page"] == "f81r" and not r["page"].startswith("f84") for r in cross))
        checks.add("source metadata", {(r["section"], r["language"], r["hand"]) for r in source} == {("B", "B", "2")})
        checks.add("cross line census", len(cross) == 31)
        checks.add("cross all readers", sum(int(r["all_three_present"]) for r in cross) == 31)
        checks.add("cross exact readers", sum(int(r["all_present_exact"]) for r in cross) == 7)

        by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in source:
            by_line[row["locus"]].append(row)
        checks.add("source physical order", list(by_line) == [f"f81r.{i}" for i in range(1, 32)])
        cross_by_locus = {row["locus"]: row for row in cross}
        checks.add("cross physical order", list(cross_by_locus) == [f"f81r.{i}" for i in range(1, 32)])
        for index in range(1, 32):
            locus = f"f81r.{index}"
            rows = by_line[locus]
            checks.add(f"source indices {locus}", [int(r["token_index"]) for r in rows] == list(range(1, len(rows) + 1)))
            checks.add(f"source cross replay {locus}", " ".join(r["eva"] for r in rows) == cross_by_locus[locus]["zl3b_clean"])

        coverage_rows = [
            row for row in read_tsv(V48 / "ALL_LINE_CONCRETE_COVERAGE_V48.tsv")
            if row["page"] == "f81r"
        ]
        coverage_rows.sort(key=lambda row: locus_number(row["locus"]))
        baseline: dict[tuple[str, str], dict[str, str]] = {}
        for row in coverage_rows:
            surfaces = row["zl3b_line"].split()
            glosses = row["token_glosses_de"].split(" | ")
            sources = row["gloss_sources"].split(" | ")
            states = row["scope_states"].split(" | ")
            checks.add(f"coverage vector {row['locus']}", len(surfaces) == len(glosses) == len(sources) == len(states) == int(row["token_count"]))
            for position, values in enumerate(zip(surfaces, glosses, sources, states), 1):
                surface, gloss, meaning_source, state = values
                baseline[(row["locus"], str(position))] = {
                    "surface": surface, "gloss": gloss, "source": meaning_source, "state": state,
                }
        raw_unknown_keys = {key for key, row in baseline.items() if row["state"] == "UNKNOWN_SURFACE"}
        checks.add("raw unknown position count", len(raw_unknown_keys) == 24)
        checks.add("raw unknown surface count", len({baseline[key]["surface"] for key in raw_unknown_keys}) == 23)

        alignment = read_tsv(ART / "F81R_SOURCE_ALIGNMENT.tsv")
        tokens = read_tsv(ART / "F81R_TOKEN_READINGS.tsv")
        components = read_tsv(ART / "F81R_COMPONENT_TRACES.tsv")
        cards = read_tsv(ART / "F81R_REVIEW_CARDS.tsv")
        variants = read_tsv(ART / "F81R_READER_VARIANT_AUDIT.tsv")
        lines = read_tsv(ART / "F81R_LINE_READER.tsv")
        actions = read_tsv(ART / "F81R_EXPLICIT_ACTION_AUDIT.tsv")
        attachments = read_tsv(ART / "F81R_VALUE_ATTACHMENT_AUDIT.tsv")
        overlay = read_tsv(ART / "F81R_COVERAGE_OVERLAY.tsv")
        architecture = read_tsv(ART / "F81R_PAGE_ARCHITECTURE.tsv")
        legacy_tokens = read_tsv(ART / "LEGACY_TOKEN_RENDERER_AUDIT.tsv")
        legacy_statements = read_tsv(ART / "LEGACY_STATEMENT_BASELINE.tsv")
        rules = read_tsv(ART / "RENDERER_RULE_CARDS.tsv")
        result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
        reader = (ART / "GDT674_F81R_CONCRETE_WORKING_READER.md").read_text(encoding="utf-8")

        checks.add("alignment rows", len(alignment) == 210)
        checks.add("token rows", len(tokens) == 210)
        checks.add("component rows nonempty", len(components) == 279, str(len(components)))
        checks.add("review cards", len(cards) == 25 and len({r["surface"] for r in cards}) == 25)
        checks.add("reader variants", len(variants) == 27)
        checks.add("line reader", len(lines) == 31)
        checks.add("action audit", len(actions) == 18)
        checks.add("value attachment audit", len(attachments) == 10)
        checks.add("coverage overlay", len(overlay) == 31)
        checks.add("page architecture", len(architecture) == 2)
        checks.add("legacy token audit", len(legacy_tokens) == 210)
        checks.add("legacy statement audit", len(legacy_statements) == 48)
        checks.add("renderer rules", len(rules) == 13)
        checks.add("result status", result["status"] == EXPECTED_STATUS, result["status"])

        source_keys = [(r["page"], r["locus"], r["token_index"], r["eva"]) for r in source]
        checks.add("alignment exact source replay", [(r["page"], r["locus"], r["token_index"], r["eva"]) for r in alignment] == source_keys)
        checks.add("token exact source replay", [(r["page"], r["locus"], r["token_index"], r["eva"]) for r in tokens] == source_keys)
        checks.add("alignment V48 line match", all(r["v48_line_surface_match"] == "1" for r in alignment))

        token_by_key = {(row["locus"], row["token_index"]): row for row in tokens}
        context_source = read_tsv(SRC / "F81R_CONTEXT_CARDS.tsv")
        context_by_key = {(row["locus"], row["token_index"]): row for row in context_source}
        checks.add("context source rows", len(context_by_key) == 3)
        expected_context_keys = {("f81r.17", "1"), ("f81r.25", "8"), ("f81r.29", "1")}
        checks.add("context source exact keys", set(context_by_key) == expected_context_keys)
        review_keys = raw_unknown_keys | expected_context_keys
        checks.add("review key count", len(review_keys) == 27)
        checks.add("review surface count", len({baseline[key]["surface"] for key in review_keys}) == 25)
        checks.add("token review keys", {(r["locus"], r["token_index"]) for r in tokens if r["review_position"] == "1"} == review_keys)
        checks.add("token raw unknown keys", {(r["locus"], r["token_index"]) for r in tokens if r["raw_v48_unknown_before"] == "1"} == raw_unknown_keys)
        checks.add("route profile", Counter(r["route"] for r in tokens) == {
            "INHERITED_V48": 183, "ROLE_COMPOSED_REVIEW": 21,
            "LOCAL_WHOLE_REVIEW": 3, "OCCURRENCE_CONTEXT_REVIEW": 3,
        })
        checks.add("review class profile", Counter(r["review_class"] for r in tokens) == {"E": 183, "P": 21, "W": 3, "O": 3})

        transfer_source = {row["surface"]: row for row in read_tsv(SRC / "F81R_TRANSFER_CARDS.tsv")}
        checks.add("transfer source cards", len(transfer_source) == 23)
        for key, token in token_by_key.items():
            base = baseline[key]
            if key in raw_unknown_keys:
                card = transfer_source[token["eva"]]
                checks.add(f"transfer meaning {token['global_ordinal']}", token["working_meaning_de"] == card["working_meaning_de"])
                checks.add(f"transfer composition {token['global_ordinal']}", token["composition"] == card["composition"])
                checks.add(f"transfer confidence {token['global_ordinal']}", token["confidence"] == card["confidence"])
            elif key in expected_context_keys:
                card = context_by_key[key]
                checks.add(f"context meaning {token['global_ordinal']}", token["working_meaning_de"] == card["working_meaning_de"] == base["gloss"])
                checks.add(f"context composition {token['global_ordinal']}", token["composition"] == card["composition"])
            else:
                checks.add(f"inherited meaning {token['global_ordinal']}", token["working_meaning_de"] == base["gloss"])
                checks.add(f"inherited source {token['global_ordinal']}", token["meaning_source"] == base["source"])
                checks.add(f"inherited scope {token['global_ordinal']}", token["scope_state"] == base["state"])

        card_by_surface = {row["surface"]: row for row in cards}
        source_counts = Counter(row["eva"] for row in source)
        checks.add("card classes", Counter(row["class"] for row in cards) == {"P": 20, "W": 3, "O": 2})
        checks.add("card position total", sum(int(row["count"]) for row in cards) == 27)
        for surface, card in card_by_surface.items():
            checks.add(f"card source count {surface}", source_counts[surface] == int(card["count"]))
            checks.add(f"card not promoted {surface}", card["promoted_to_v48"] == "0")
            checks.add(f"card meaning nonempty {surface}", bool(card["working_meaning_de"].strip()))
            if card["class"] in {"P", "W"}:
                checks.add(f"card raw unknown {surface}", int(card["raw_unknown_positions"]) == int(card["count"]))
            else:
                checks.add(f"card context only {surface}", int(card["context_recheck_positions"]) == int(card["count"]))

        stem_roles = {row["structural_role"] for row in read_tsv(V48 / "STEM_MODEL_V48.tsv")}
        component_by_global: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in components:
            component_by_global[row["global_ordinal"]].append(row)
        checks.add("component covers all tokens", set(component_by_global) == {str(i) for i in range(1, 211)})
        for token in tokens:
            rows = sorted(component_by_global[token["global_ordinal"]], key=lambda row: int(row["component_ordinal"]))
            checks.add(f"component concatenation {token['global_ordinal']}", "".join(row["surface_segment"] for row in rows) == token["eva"])
            starts = [int(row["char_start"]) for row in rows]
            ends = [int(row["char_end"]) for row in rows]
            checks.add(f"component offsets {token['global_ordinal']}", starts[0] == 0 and ends[-1] == len(token["eva"]) and starts[1:] == ends[:-1])
            if token["route"] == "ROLE_COMPOSED_REVIEW":
                checks.add(f"productive component roles {token['global_ordinal']}", all(row["component_role"] in stem_roles for row in rows))
                checks.add(f"productive component flags {token['global_ordinal']}", all(row["productive"] == "1" for row in rows))
            else:
                checks.add(f"nonproductive component singleton {token['global_ordinal']}", len(rows) == 1 and rows[0]["productive"] == "0")

        variant_keys = {(row["locus"], row["token_index"]): row for row in variants}
        checks.add("variant exact review keys", set(variant_keys) == review_keys)
        recomputed_support = Counter()
        for key, row in variant_keys.items():
            locus, token_index = key
            index = int(token_index) - 1
            zl = cross_by_locus[locus]["zl3b_clean"].split()
            it = reader_operations(zl, cross_by_locus[locus]["it2a_clean"].split())[index]
            rf = reader_operations(zl, cross_by_locus[locus]["rf1b_clean"].split())[index]
            support = "BOTH_EXACT" if it[0] == rf[0] == "EXACT" else "ONE_EXACT" if "EXACT" in {it[0], rf[0]} else "NEITHER_EXACT"
            recomputed_support[support] += 1
            checks.add(f"variant IT2a {locus}:{token_index}", (row["it2a_operation"], row["it2a_form"]) == it)
            checks.add(f"variant RF1b {locus}:{token_index}", (row["rf1b_operation"], row["rf1b_form"]) == rf)
            checks.add(f"variant support {locus}:{token_index}", row["reader_support"] == support)
        checks.add("variant support profile", recomputed_support == {"BOTH_EXACT": 11, "ONE_EXACT": 13, "NEITHER_EXACT": 3}, str(recomputed_support))

        attachment_source = read_tsv(SRC / "F81R_VALUE_ATTACHMENTS.tsv")
        attachment_by_key = {(row["locus"], row["token_index"]): row for row in attachment_source}
        checks.add("attachment source keys", len(attachment_by_key) == 10)
        for token in tokens:
            key = (token["locus"], token["token_index"])
            attachment = attachment_by_key.get(key)
            checks.add(f"attachment flag {token['global_ordinal']}", token["value_attachment"] == ("1" if attachment else "0"))
            checks.add(f"attachment render {token['global_ordinal']}", token["contextual_render_de"] == (attachment["contextual_render_de"] if attachment else token["working_meaning_de"]))
        checks.add("attachment artifact replay", [tuple(row.get(field, "") for field in ("locus", "token_index", "surface", "contextual_render_de", "head_token_index", "relation", "rationale")) for row in attachments] == [tuple(row.get(field, "") for field in ("locus", "token_index", "surface", "contextual_render_de", "head_token_index", "relation", "rationale")) for row in attachment_source])

        action_source = read_tsv(SRC / "F81R_EXPLICIT_ACTIONS.tsv")
        action_keys = {(row["locus"], row["token_index"]) for row in action_source}
        checks.add("action source keys", len(action_keys) == 18 and len({key[0] for key in action_keys}) == 15)
        checks.add("action token flags", {(row["locus"], row["token_index"]) for row in tokens if row["explicit_action"] == "1"} == action_keys)
        checks.add("action artifact source replay", [(row["locus"], row["token_index"], row["surface"], row["action_de"]) for row in actions] == [(row["locus"], row["token_index"], row["surface"], row["action_de"]) for row in action_source])

        tokens_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in tokens:
            tokens_by_locus[row["locus"]].append(row)
        checks.add("line order", [row["locus"] for row in lines] == [f"f81r.{i}" for i in range(1, 32)])
        for row in lines:
            locus_tokens = tokens_by_locus[row["locus"]]
            expected_literal = " | ".join(f"{token['eva']} = {token['working_meaning_de']}" for token in locus_tokens)
            expected_context = " | ".join(f"{token['eva']} = {token['contextual_render_de']}" for token in locus_tokens)
            checks.add(f"line source replay {row['locus']}", row["zl3b_line"] == " ".join(token["eva"] for token in locus_tokens))
            checks.add(f"line literal replay {row['locus']}", row["literal_token_glosses_de"] == expected_literal)
            checks.add(f"line context replay {row['locus']}", row["contextual_token_values_de"] == expected_context)
            checks.add(f"line no generic filler {row['locus']}", GENERIC_FILLER.search(row["working_translation_de"]) is None)
            checks.add(f"line translation nonempty {row['locus']}", bool(row["working_translation_de"].strip()))
            checks.add(f"line reader source visible {row['locus']}", f"`{row['zl3b_line']}`" in reader)
            checks.add(f"line reader literal visible {row['locus']}", expected_literal in reader)
            checks.add(f"line reader context visible {row['locus']}", expected_context in reader)
            checks.add(f"line reader translation visible {row['locus']}", row["working_translation_de"] in reader)
        checks.add("line mode profile", Counter(row["line_mode"] for row in lines) == {"INHERITED_ACTION_ANCHOR": 15, "NO_INHERITED_ACTION_ANCHOR": 16})
        checks.add("line review total", sum(int(row["review_tokens"]) for row in lines) == 27)
        checks.add("line raw unknown total", sum(int(row["raw_unknown_before"]) for row in lines) == 24)
        checks.add("line newly complete", sum(int(row["newly_complete"]) for row in lines) == 12)
        checks.add("line all complete", all(row["unknown_after"] == "0" for row in lines))
        checks.add("reader block count", len(re.findall(r"^## f81r\.\d+ ·", reader, re.M)) == 31)

        checks.add("overlay exact lines", [row["locus"] for row in overlay] == [row["locus"] for row in lines])
        checks.add("overlay unknown before", sum(int(row["unknown_before"]) for row in overlay) == 24)
        checks.add("overlay unknown after", sum(int(row["unknown_after"]) for row in overlay) == 0)
        checks.add("architecture token profile", [int(row["tokens"]) for row in architecture] == [94, 116])
        checks.add("architecture review profile", [int(row["review_positions"]) for row in architecture] == [12, 15])
        checks.add("architecture action lines", sum(int(row["inherited_action_anchor_lines"]) for row in architecture) == 15)
        checks.add("architecture no-action lines", sum(int(row["lines_without_inherited_action_anchor"]) for row in architecture) == 16)

        legacy416 = [row for row in read_tsv(G416 / "gdt416_4576_imperative_clauses.tsv") if row["physical_page"] == "f81r"]
        checks.add("legacy416 source sequence", [row["surface"] for row in legacy416] == [row["eva"] for row in source])
        checks.add("legacy416 audit sequence", [row["surface"] for row in legacy_tokens] == [row["eva"] for row in source])
        checks.add("legacy416 generic rows", sum(int(row["gdt416_generic_station_or_entry"]) for row in legacy_tokens) == 208)
        checks.add("legacy416 inherited action", sum(int(row["gdt416_inherited_action"]) for row in legacy_tokens) == 89)
        checks.add("legacy416 inherited argument", sum(int(row["gdt416_inherited_argument"]) for row in legacy_tokens) == 114)
        checks.add("legacy token comparison only", all(row["comparison_only_not_meaning_input"] == "1" for row in legacy_tokens))
        legacy407 = [row for row in read_tsv(G407 / "gdt407_715_statement_edition.tsv") if row["physical_page"] == "f81r"]
        checks.add("legacy407 surface sequence", [surface for row in legacy407 for surface in row["surface_sequence"].split()] == [row["eva"] for row in source])
        checks.add("legacy407 generic hits", sum(int(row["generic_filler_hits"]) for row in legacy_statements) == 71)
        checks.add("legacy statement comparison only", all(row["comparison_only_not_meaning_input"] == "1" for row in legacy_statements))

        checks.add("result source", result["source"]["tokens"] == 210 and result["source"]["physical_lines"] == 31)
        checks.add("result inherited", result["coverage"]["inherited_v48_positions"] == 183 and result["coverage"]["inherited_v48_surface_types"] == 103)
        checks.add("result review", result["coverage"]["review_positions"] == 27 and result["coverage"]["review_surface_types"] == 25)
        checks.add("result raw unknown", result["coverage"]["raw_v48_unknown_positions_before"] == 24 and result["coverage"]["unassigned_positions"] == 0)
        checks.add("result reader", result["reader"] == {"review_both_exact": 11, "review_neither_exact": 3, "review_one_exact": 13})
        checks.add("result architecture", result["architecture"]["inherited_action_positions"] == 18 and result["architecture"]["inherited_action_anchor_lines"] == 15)
        checks.add("result legacy", result["renderer_comparison"]["gdt416_rows_with_generic_station_or_entry"] == 208 and result["renderer_comparison"]["gdt674_generic_filler_hits"] == 0)
        checks.add("result global unknown", result["global_overlay"]["unknown_positions_before"] == 8018 and result["global_overlay"]["unknown_positions_after"] == 7994)
        checks.add("result global complete", result["global_overlay"]["complete_lines_before"] == 1368 and result["global_overlay"]["complete_lines_after"] == 1380)
        checks.add("manifest sealed pages", json.loads((BASE / "experiment.json").read_text(encoding="utf-8"))["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"})

        with tempfile.TemporaryDirectory(prefix="gdt674_validate_") as temp:
            temp_path = Path(temp)
            completed = subprocess.run(
                [sys.executable, str(SRC / "run.py"), "--output-dir", str(temp_path), "--no-docs"],
                cwd=ROOT, text=True, capture_output=True,
            )
            checks.add("fresh builder exits zero", completed.returncode == 0, completed.stderr[-1000:])
            if completed.returncode == 0:
                for name in OUTPUT_NAMES:
                    checks.add(f"byte replay {name}", (temp_path / name).read_bytes() == (ART / name).read_bytes())
    except Exception as exc:
        checks.add("validator exception", False, repr(exc))

    failed = [row for row in checks.rows if not row["ok"]]
    validation = {
        "experiment_id": "GDT674",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks.rows) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": failed,
        "checks": checks.rows,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: validation[key] for key in ("status", "checks_passed", "checks_failed")}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
