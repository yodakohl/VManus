#!/usr/bin/env python3
"""Build V68 clause realization over frozen V67 words and the live V62 action deck."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization"
SRC = BASE / "src"
ART = BASE / "artifacts"
G694 = ROOT / "experiments/yolo/gdt694_residual_fraction_share_migration/artifacts"
G689 = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts"
G688 = ROOT / "experiments/yolo/gdt688_v61_exact_verb_ordinal_provenance_renderer"
G676 = ROOT / "experiments/yolo/gdt676_v50_external_line_renderer/src"

TOKENS = G694 / "V67_479_TOKEN_ZERO_FRACTION_READER.tsv"
LINES = G694 / "V67_51_LINE_ZERO_FRACTION_READER.tsv"
SPANS = G694 / "V67_3_BOUND_SPANS.tsv"
G694_RESULT = G694 / "RESULT.json"
V62_LINES = G689 / "V62_51_LINE_READER.tsv"
V62_VERBS = G689 / "V62_VERB_OCCURRENCE_PROVENANCE.tsv"
G689_RESULT = G689 / "RESULT.json"
VERB_RULES = G688 / "src/V61_VERB_RULES.tsv"
VALUE_BINDINGS = G676 / "VALUE_ATTACHMENT_SPECS.tsv"
POLICY = SRC / "V68_CLAUSE_REALIZATION_POLICY.tsv"
INTRODUCERS = SRC / "V68_RIGHT_BOUND_INTRODUCERS.tsv"

WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")
STATUS = "PASS_V68_83_ACTION_CLAUSES__92_NOMINAL_BLOCKS__175_TOTAL__115_VERBS__ZERO_WORD_DELTA"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Cannot infer fields for empty TSV {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def words(text: str) -> list[str]:
    return [word.casefold() for word in WORD_RE.findall(text)]


def ordinal_list(value: str) -> list[int]:
    return [] if value == "NONE" else [int(item) for item in value.split("|")]


def sentence(text: str) -> str:
    value = text.strip().strip(" ;.")
    if not value:
        return ""
    return value[:1].upper() + value[1:] + "."


def render_v67(glosses: list[str]) -> str:
    """Replay the inherited GDT694 source-order punctuation exactly."""
    text = ""
    for gloss in glosses:
        if gloss in {";", "."}:
            text = text.rstrip(" ,;.") + gloss
            continue
        separator = "" if not text else (" " if text.endswith((";", ".", ":")) else "; ")
        text += separator + gloss
    if text and not text.endswith("."):
        text += "."
    return text[:1].upper() + text[1:] if text else text


def compile_verb_rules(rows: list[dict[str, str]]) -> list[tuple[str, re.Pattern[str]]]:
    compiled = [(row["canonical_lemma"], re.compile(row["regex"], re.IGNORECASE)) for row in rows]
    assert len(compiled) == len({lemma for lemma, _ in compiled}) == 32
    return compiled


def scan_verbs(text: str, rules: list[tuple[str, re.Pattern[str]]]) -> list[dict[str, object]]:
    found = [
        {"start": match.start(), "end": match.end(), "lemma": lemma, "matched_text": match.group(0)}
        for lemma, pattern in rules for match in pattern.finditer(text)
    ]
    found.sort(key=lambda row: (int(row["start"]), int(row["end"]), str(row["lemma"])))
    for left, right in zip(found, found[1:]):
        assert int(left["end"]) <= int(right["start"]), (text, left, right)
    return found


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    token_rows = read_tsv(TOKENS)
    line_rows = read_tsv(LINES)
    span_rows = read_tsv(SPANS)
    v62_line_rows = read_tsv(V62_LINES)
    v62_verb_rows = read_tsv(V62_VERBS)
    verb_rule_rows = read_tsv(VERB_RULES)
    value_rows = read_tsv(VALUE_BINDINGS)
    policy_rows = read_tsv(POLICY)
    intro_rows = read_tsv(INTRODUCERS)
    g694_result = json.loads(G694_RESULT.read_text(encoding="utf-8"))
    g689_result = json.loads(G689_RESULT.read_text(encoding="utf-8"))

    assert g694_result["status"].startswith("PASS_V67_")
    assert g689_result["status"].startswith("PASS_V62_")
    assert g689_result["v62_dispatch"]["action_positions"] == 83
    assert g689_result["v62_dispatch"]["practical_verb_occurrences"] == 115
    assert len(token_rows) == 479 and len(line_rows) == len(v62_line_rows) == 51
    assert len(span_rows) == 3 and len(v62_verb_rows) == 115
    assert len(policy_rows) == 7 and len(intro_rows) == 4
    assert [tuple(row.values()) for row in policy_rows] == [
        ("P001", "BOUND_SPAN", "GDT694 exact span start", "Keep the complete V67 span text as one indivisible nominal unit.", "1"),
        ("P002", "EXPLICIT_PUNCTUATION_TOKEN", "V67 gloss is semicolon or full stop", "Attach the zero-word marker to the preceding semantic unit; never emit an empty clause.", "2"),
        ("P003", "ACTION_CARD", "Ordinal occurs in GDT689 v62_action_ordinals", "Emit the complete written card as one action clause even when it contains several licensed verbs.", "3"),
        ("P004", "RIGHT_BOUND_INTRODUCER", "One of four exact registered connector positions", "Join the connector by colon to its immediately following nominal or action target.", "4"),
        ("P005", "NOMINAL_BINDING", "Adjacent head and value carry GDT676 decision BIND or BIND_NOMINAL", "Keep both inside one nominal block and place a colon between them.", "5"),
        ("P006", "NOMINAL_RUN", "Maximal consecutive non-action units", "Emit one semicolon-delimited nominal block.", "6"),
        ("P007", "LINE_JOIN", "Between action clauses and nominal blocks", "Place a full stop; never add a connective, object, pronoun or verb.", "7"),
    ]
    assert g694_result["basis"]["new_pages"] == 0
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in token_rows)

    def token_key(row: dict[str, str]) -> tuple[str, int]:
        return row["locus"], int(row["token_ordinal"])

    token_by_key = {token_key(row): row for row in token_rows}
    assert len(token_by_key) == 479
    tokens_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        tokens_by_locus[row["locus"]].append(row)
    for locus_tokens in tokens_by_locus.values():
        locus_tokens.sort(key=lambda row: int(row["token_ordinal"]))
        assert [int(row["token_ordinal"]) for row in locus_tokens] == list(range(1, len(locus_tokens) + 1))

    line_by_locus = {row["locus"]: row for row in line_rows}
    v62_line_by_locus = {row["locus"]: row for row in v62_line_rows}
    assert len(line_by_locus) == len(v62_line_by_locus) == 51
    assert list(line_by_locus) == list(v62_line_by_locus)
    for locus in line_by_locus:
        assert line_by_locus[locus]["zl3b_line"] == v62_line_by_locus[locus]["zl3b_line"]

    action_keys: set[tuple[str, int]] = set()
    for line in v62_line_rows:
        ordinals = ordinal_list(line["v62_action_ordinals"])
        surfaces = [] if line["v62_action_surfaces"] == "NONE" else line["v62_action_surfaces"].split("|")
        assert len(ordinals) == len(surfaces) == int(line["v62_action_positions"])
        for ordinal, surface in zip(ordinals, surfaces):
            key = (line["locus"], ordinal)
            assert key not in action_keys and token_by_key[key]["surface"] == surface
            action_keys.add(key)
    assert len(action_keys) == 83

    expected_verbs: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in v62_verb_rows:
        key = (row["locus"], int(row["source_ordinal"]))
        assert key in action_keys
        assert token_by_key[key]["surface"] == row["source_surface"]
        expected_verbs[key].append(row)
    assert set(expected_verbs) == action_keys
    assert sum(len(rows) for rows in expected_verbs.values()) == 115

    compiled_rules = compile_verb_rules(verb_rule_rows)
    scanned_by_key: dict[tuple[str, int], list[dict[str, object]]] = {}
    for row in token_rows:
        key = token_key(row)
        scanned_by_key[key] = scan_verbs(row["v67_token_gloss_de"], compiled_rules)

    assert sum(len(rows) for rows in scanned_by_key.values()) == 115
    assert {key for key, rows in scanned_by_key.items() if rows} == action_keys
    for key in action_keys:
        expected = [row["canonical_lemma"] for row in expected_verbs[key]]
        actual = [str(row["lemma"]) for row in scanned_by_key[key]]
        assert Counter(actual) == Counter(expected)
        assert actual == expected

    action_audit: list[dict[str, object]] = []
    verb_occurrences: list[dict[str, object]] = []
    for key in sorted(action_keys):
        token = token_by_key[key]
        expected_rows = expected_verbs[key]
        actual_rows = scanned_by_key[key]
        expected_lemmas = [row["canonical_lemma"] for row in expected_rows]
        actual_lemmas = [str(row["lemma"]) for row in actual_rows]
        action_audit.append({
            "page": token["page"], "locus": key[0], "token_ordinal": key[1], "surface": token["surface"],
            "v62_source_gloss_de": expected_rows[0]["source_literal_gloss_de"],
            "v67_token_gloss_de": token["v67_token_gloss_de"],
            "expected_verb_occurrences": len(expected_rows),
            "expected_lemma_sequence": "|".join(expected_lemmas),
            "v67_observed_verb_occurrences": len(actual_rows),
            "v67_observed_lemma_sequence": "|".join(actual_lemmas),
            "verb_multiset_exact": 1, "verb_sequence_exact": 1,
            "live_action_source": "GDT689_V62_ACTION_ORDINAL",
        })
        for occurrence_index, (expected, actual) in enumerate(zip(expected_rows, actual_rows), start=1):
            assert expected["canonical_lemma"] == actual["lemma"]
            verb_occurrences.append({
                "page": token["page"], "locus": key[0], "token_ordinal": key[1], "surface": token["surface"],
                "occurrence_within_token": occurrence_index, "canonical_lemma": actual["lemma"],
                "matched_text": actual["matched_text"], "token_char_start": actual["start"], "token_char_end": actual["end"],
                "v62_source_matched_text": expected["matched_text"],
                "v62_source_gloss_de": expected["source_literal_gloss_de"],
                "v67_token_gloss_de": token["v67_token_gloss_de"],
                "action_licensed": 1, "provenance_status": "EXACT_V67_TOKEN_SPAN_TO_GDT689_ACTION_ORDINAL",
            })
    assert len(action_audit) == 83 and len(verb_occurrences) == 115

    span_by_start: dict[tuple[str, int], dict[str, str]] = {}
    span_covered: set[tuple[str, int]] = set()
    for row in span_rows:
        locus = row["locus"]
        start, end = int(row["start_ordinal"]), int(row["end_ordinal"])
        actual = "|".join(token_by_key[(locus, ordinal)]["surface"] for ordinal in range(start, end + 1))
        assert actual == row["surfaces"]
        for ordinal in range(start, end + 1):
            key = (locus, ordinal)
            assert key not in span_covered and key not in action_keys
            span_covered.add(key)
        span_by_start[(locus, start)] = row

    # Replay the complete inherited V67 line channel before changing punctuation.
    for source_line in line_rows:
        locus = source_line["locus"]
        units: list[str] = []
        ordinal = 1
        while ordinal <= len(tokens_by_locus[locus]):
            span = span_by_start.get((locus, ordinal))
            if span:
                units.append(span["v67_selected_gloss_de"])
                ordinal = int(span["end_ordinal"]) + 1
            else:
                units.append(token_by_key[(locus, ordinal)]["v67_token_gloss_de"])
                ordinal += 1
        assert render_v67(units) == source_line["v67_translation_de"], locus

    binding_edges: dict[tuple[str, int, int], dict[str, str]] = {}
    for row in value_rows:
        if row["decision"] not in {"BIND", "BIND_NOMINAL"}:
            continue
        heads, values = ordinal_list(row["head_ordinals"]), ordinal_list(row["value_ordinals"])
        assert len(heads) == len(values) == 1 and values[0] == heads[0] + 1
        key = (row["locus"], heads[0], values[0])
        assert key not in binding_edges
        assert (key[0], key[1]) not in action_keys and (key[0], key[2]) not in action_keys
        binding_edges[key] = row
    assert len(binding_edges) == 10

    intro_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in intro_rows:
        key = (row["locus"], int(row["intro_ordinal"]))
        target = (row["locus"], int(row["target_ordinal"]))
        assert key not in intro_by_key and target[1] == key[1] + 1
        assert token_by_key[key]["surface"] == row["intro_surface"]
        assert token_by_key[key]["v67_token_gloss_de"] == row["expected_v67_gloss_de"]
        assert token_by_key[target]["surface"] == row["target_surface"]
        assert key not in action_keys
        intro_by_key[key] = row

    clauses: list[dict[str, object]] = []
    line_out: list[dict[str, object]] = []
    word_audit: list[dict[str, object]] = []
    position_clause: dict[tuple[str, int], tuple[int, str]] = {}
    mode_map = {
        "ACTION_SEQUENCE": "PROCEDURE_WITH_NOMINAL_CHECKPOINTS",
        "MIXED_RECORD": "HYBRID_LIST_WITH_ACTION_ISLANDS",
        "NOMINAL_REGISTER": "NOMINAL_REGISTER",
        "QUANTITY_LABEL": "QUANTITY_STATE_REGISTER",
    }

    for source_line in line_rows:
        locus = source_line["locus"]
        locus_tokens = tokens_by_locus[locus]
        semantic_units: list[dict[str, object]] = []
        ordinal = 1
        while ordinal <= len(locus_tokens):
            span = span_by_start.get((locus, ordinal))
            if span:
                end = int(span["end_ordinal"])
                semantic_units.append({
                    "kind": "NOMINAL", "start": ordinal, "end": end,
                    "surfaces": span["surfaces"], "text": span["v67_selected_gloss_de"],
                    "unit_origin": span["span_id"], "marker_ordinals": [], "intro_id": "NONE",
                })
                ordinal = end + 1
                continue
            token = token_by_key[(locus, ordinal)]
            gloss = token["v67_token_gloss_de"]
            if gloss in {";", "."}:
                assert semantic_units, (locus, ordinal)
                previous = semantic_units[-1]
                assert int(previous["end"]) == ordinal - 1
                previous["end"] = ordinal
                previous["surfaces"] = str(previous["surfaces"]) + "|" + token["surface"]
                marker_ordinals = list(previous["marker_ordinals"])
                marker_ordinals.append(ordinal)
                previous["marker_ordinals"] = marker_ordinals
                ordinal += 1
                continue
            semantic_units.append({
                "kind": "ACTION" if (locus, ordinal) in action_keys else "NOMINAL",
                "start": ordinal, "end": ordinal, "surfaces": token["surface"], "text": gloss,
                "unit_origin": "TOKEN", "marker_ordinals": [],
                "intro_id": intro_by_key.get((locus, ordinal), {}).get("intro_id", "NONE"),
            })
            ordinal += 1

        groups: list[list[dict[str, object]]] = []
        unit_index = 0
        while unit_index < len(semantic_units):
            unit = semantic_units[unit_index]
            if unit["intro_id"] != "NONE" and semantic_units[unit_index + 1]["kind"] == "ACTION":
                groups.append([unit, semantic_units[unit_index + 1]])
                unit_index += 2
                continue
            if unit["kind"] == "ACTION":
                groups.append([unit])
            elif groups and groups[-1][0]["kind"] == "NOMINAL":
                groups[-1].append(unit)
            else:
                groups.append([unit])
            unit_index += 1

        line_clauses: list[dict[str, object]] = []
        for clause_index, group in enumerate(groups, start=1):
            clause_type = "ACTION_CLAUSE" if any(unit["kind"] == "ACTION" for unit in group) else "NOMINAL_BLOCK"
            start, end = int(group[0]["start"]), int(group[-1]["end"])
            used_bindings: list[str] = [
                f"{locus}#{head}-{value}"
                for (edge_locus, head, value) in binding_edges
                if edge_locus == locus and any(
                    int(unit["start"]) <= head < value <= int(unit["end"]) for unit in group
                )
            ]
            if clause_type == "ACTION_CLAUSE":
                assert sum(unit["kind"] == "ACTION" for unit in group) == 1
                rendered_units = []
                for unit in group:
                    value = str(unit["text"]).strip().strip(" ;.")
                    if unit["intro_id"] != "NONE" and not value.endswith(":"):
                        value += ":"
                    rendered_units.append(value)
                text = sentence(" ".join(rendered_units))
            else:
                assembled = ""
                for unit_index, unit in enumerate(group):
                    if unit_index:
                        previous = group[unit_index - 1]
                        edge = (locus, int(previous["end"]), int(unit["start"]))
                        binding = binding_edges.get(edge)
                        if previous["intro_id"] != "NONE":
                            separator = " "
                        elif binding:
                            separator = ": "
                            used_bindings.append(f"{locus}#{edge[1]}-{edge[2]}")
                        else:
                            separator = "; "
                        assembled += separator
                    value = str(unit["text"]).strip().strip(" ;.")
                    if unit["intro_id"] != "NONE" and not value.endswith(":"):
                        value += ":"
                    if unit_index and value.startswith("Hierzu:"):
                        value = "hierzu:" + value[len("Hierzu:"):]
                    assembled += value
                text = sentence(assembled)
            action_ordinals = [int(unit["start"]) for unit in group if unit["kind"] == "ACTION"]
            marker_ordinals = [marker for unit in group for marker in list(unit["marker_ordinals"])]
            verb_rows_here = expected_verbs[(locus, action_ordinals[0])] if action_ordinals else []
            clause = {
                "page": source_line["page"], "locus": locus, "clause_id": clause_index,
                "line_mode": source_line["v66_line_mode"], "v68_reader_mode": mode_map[source_line["v66_line_mode"]],
                "clause_type": clause_type, "start_ordinal": start, "end_ordinal": end,
                "token_positions": end - start + 1, "semantic_units": len(group),
                "surfaces": "|".join(str(unit["surfaces"]) for unit in group),
                "action_ordinals": "|".join(map(str, action_ordinals)) if action_ordinals else "NONE",
                "verb_lemmas": "|".join(row["canonical_lemma"] for row in verb_rows_here) if verb_rows_here else "NONE",
                "verb_occurrences": len(verb_rows_here),
                "explicit_marker_ordinals": "|".join(map(str, marker_ordinals)) if marker_ordinals else "NONE",
                "right_bound_intro_ids": "|".join(
                    str(unit["intro_id"]) for unit in group if unit["intro_id"] != "NONE"
                ) or "NONE",
                "binding_ids": "|".join(used_bindings) if used_bindings else "NONE",
                "v68_clause_de": text,
                "realization_rule": (
                    "ONE_GDT689_ACTION_CARD_ONE_SENTENCE" if clause_type == "ACTION_CLAUSE"
                    else "MAXIMAL_CONTIGUOUS_NOMINAL_BLOCK"
                ),
                "content_word_delta": 0,
            }
            clauses.append(clause)
            line_clauses.append(clause)
            for consumed in range(start, end + 1):
                assert (locus, consumed) not in position_clause
                position_clause[(locus, consumed)] = (clause_index, clause_type)

        translation = " ".join(str(clause["v68_clause_de"]) for clause in line_clauses)
        old_words, new_words = words(source_line["v67_translation_de"]), words(translation)
        assert old_words == new_words, locus
        action_clause_ids = [int(clause["clause_id"]) for clause in line_clauses if clause["clause_type"] == "ACTION_CLAUSE"]
        nominal_clause_ids = [int(clause["clause_id"]) for clause in line_clauses if clause["clause_type"] == "NOMINAL_BLOCK"]
        binding_ids = [
            binding_id for clause in line_clauses
            for binding_id in str(clause["binding_ids"]).split("|") if binding_id != "NONE"
        ]
        out: dict[str, object] = dict(source_line)
        out.update({
            "v68_reader_mode": mode_map[source_line["v66_line_mode"]],
            "v68_clause_translation_de": translation,
            "v68_clause_count": len(line_clauses),
            "v68_action_clause_count": len(action_clause_ids),
            "v68_nominal_block_count": len(nominal_clause_ids),
            "v68_action_clause_ids": "|".join(map(str, action_clause_ids)) if action_clause_ids else "NONE",
            "v68_nominal_block_ids": "|".join(map(str, nominal_clause_ids)) if nominal_clause_ids else "NONE",
            "v68_binding_ids": "|".join(binding_ids) if binding_ids else "NONE",
            "v68_clause_end_ordinals": "|".join(str(clause["end_ordinal"]) for clause in line_clauses),
            "v68_content_word_sequence_exact": 1,
            "v68_content_word_additions": 0, "v68_content_word_deletions": 0, "v68_content_word_reorders": 0,
            "v68_changed_punctuation": int(translation != source_line["v67_translation_de"]),
            "v68_status": "PUNCTUATION_ONLY_CLAUSE_REALIZATION__V67_WORDS_AND_SPANS_FROZEN",
        })
        line_out.append(out)
        word_audit.append({
            "page": source_line["page"], "locus": locus,
            "v67_word_count": len(old_words), "v68_word_count": len(new_words),
            "word_sequence_exact": 1,
            "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0,
            "v67_translation_de": source_line["v67_translation_de"],
            "v68_clause_translation_de": translation,
        })

    assert len(position_clause) == 479
    assert len(clauses) == 175
    assert Counter(row["clause_type"] for row in clauses) == {"NOMINAL_BLOCK": 92, "ACTION_CLAUSE": 83}
    assert sum(int(row["verb_occurrences"]) for row in clauses) == 115
    assert sum(int(row["v68_action_clause_count"]) for row in line_out) == 83
    assert sum(int(row["v68_nominal_block_count"]) for row in line_out) == 92
    assert sum(
        len(str(row["binding_ids"]).split("|"))
        for row in clauses if row["binding_ids"] != "NONE"
    ) == 10

    token_freeze: list[dict[str, object]] = []
    for source in token_rows:
        key = token_key(source)
        clause_id, clause_type = position_clause[key]
        token_freeze.append({
            "page": source["page"], "locus": source["locus"], "token_ordinal": source["token_ordinal"],
            "surface": source["surface"], "v67_token_gloss_de": source["v67_token_gloss_de"],
            "v68_token_gloss_de": source["v67_token_gloss_de"], "byte_identical": 1,
            "v68_clause_id": clause_id, "v68_clause_type": clause_type,
            "v68_action_license": "GDT689_V62_ACTION_ORDINAL" if key in action_keys else "NOT_ACTION_LICENSED",
            "v68_active_verb_occurrences": len(scanned_by_key[key]),
        })

    span_out = [{
        **row,
        "v68_selected_gloss_de": row["v67_selected_gloss_de"],
        "v68_byte_identical": 1,
        "v68_clause_id": position_clause[(row["locus"], int(row["start_ordinal"]))][0],
        "v68_clause_type": position_clause[(row["locus"], int(row["start_ordinal"]))][1],
    } for row in span_rows]

    mode_census: list[dict[str, object]] = []
    for mode in ("ACTION_SEQUENCE", "MIXED_RECORD", "NOMINAL_REGISTER", "QUANTITY_LABEL"):
        mode_lines = [row for row in line_out if row["v66_line_mode"] == mode]
        mode_clauses = [row for row in clauses if row["line_mode"] == mode]
        mode_census.append({
            "line_mode": mode, "v68_reader_mode": mode_map[mode], "lines": len(mode_lines),
            "action_clauses": sum(row["clause_type"] == "ACTION_CLAUSE" for row in mode_clauses),
            "nominal_blocks": sum(row["clause_type"] == "NOMINAL_BLOCK" for row in mode_clauses),
            "total_clauses": len(mode_clauses),
            "verb_occurrences": sum(int(row["verb_occurrences"]) for row in mode_clauses),
            "punctuation_changed_lines": sum(int(row["v68_changed_punctuation"]) for row in mode_lines),
            "content_word_delta": 0,
        })
    assert [int(row["lines"]) for row in mode_census] == [16, 23, 6, 6]
    assert [(row["line_mode"], int(row["action_clauses"]), int(row["nominal_blocks"])) for row in mode_census] == [
        ("ACTION_SEQUENCE", 49, 38), ("MIXED_RECORD", 34, 42),
        ("NOMINAL_REGISTER", 0, 6), ("QUANTITY_LABEL", 0, 6),
    ]

    baseline_correction = [
        {
            "baseline": "GDT688_V61", "action_positions": 85, "active_verb_occurrences": 113,
            "live_for_v67": 0, "status": "SUPERSEDED_BY_GDT689_DY_SISTER_DISPATCH",
            "note": "Useful historical provenance, but not the live action inventory after V62.",
        },
        {
            "baseline": "GDT689_V62", "action_positions": 83, "active_verb_occurrences": 115,
            "live_for_v67": 1, "status": "AUTHORITATIVE_LIVE_BASELINE",
            "note": "olchdy and dshedy are nominal; ytedy, checthedy and qolsheedy retain sister-derived verbs.",
        },
        {
            "baseline": "GDT694_V67", "action_positions": 83, "active_verb_occurrences": 115,
            "live_for_v67": 1, "status": "EXACT_REPLAY_OF_GDT689_ACTION_MULTISETS",
            "note": "83/83 positional multisets exact; zero active verbs at non-action positions.",
        },
    ]

    write_tsv(output_dir / "V68_479_TOKEN_FREEZE.tsv", token_freeze)
    write_tsv(output_dir / "V68_175_CLAUSE_REALIZATIONS.tsv", clauses)
    write_tsv(output_dir / "V68_51_LINE_CLAUSE_READER.tsv", line_out)
    write_tsv(output_dir / "V68_83_ACTION_VERB_MULTISET_AUDIT.tsv", action_audit)
    write_tsv(output_dir / "V68_115_VERB_OCCURRENCE_PROVENANCE.tsv", verb_occurrences)
    write_tsv(output_dir / "V68_3_BOUND_SPAN_FREEZE.tsv", span_out)
    write_tsv(output_dir / "V68_51_LINE_WORD_SEQUENCE_AUDIT.tsv", word_audit)
    write_tsv(output_dir / "V68_MODE_CENSUS.tsv", mode_census)
    write_tsv(output_dir / "V61_V62_V67_VERB_BASELINE_CORRECTION.tsv", baseline_correction)

    report = [
        "# GDT695 — V68 fixed-word clause reader", "", f"Status: `{STATUS}`", "",
        "## Result", "",
        "V68 changes punctuation and capitalization only. All 479 V67 token glosses,",
        "their word order and all three bound spans remain byte-frozen. The inherited",
        "line stream becomes 175 explicit units: 83 one-written-action-card clauses",
        "and 92 maximal contiguous nominal blocks. Nine already accepted GDT676",
        "head/value adjacencies receive a colon; the tenth remains inside a frozen",
        "GDT694 bound span. Four exact right-bound connectors receive their following",
        "target without adding a word. No other relation is inferred.", "",
        "The live verb baseline is GDT689/V62, not the superseded GDT688/V61 deck.",
        "Against V62, V67 is exact: 83/83 action-position verb sequences, 115/115",
        "active verb occurrences and zero active verbs on non-action positions.",
        "Thus `olchdy` and `dshedy` correctly remain nominal, while the sister-derived",
        "verbs in `ytedy`, `checthedy` and `qolsheedy` correctly remain verbal.", "",
        "The artifact label `NOMINAL_BLOCK` means a maximal non-action register run,",
        "not a part-of-speech assignment for every contained card. Such a block may",
        "contain a registered right-bound connector. A full stop isolates the block",
        "but never promotes a nominal result or state to an action.", "",
        "## Complete 51-line V68 edition", "",
    ]
    for row in line_out:
        report.extend([
            f"### {row['locus']} · {row['v68_reader_mode']}", "",
            f"`{row['zl3b_line']}`", "", str(row["v68_clause_translation_de"]), "",
            f"Clauses: {row['v68_clause_count']} "
            f"({row['v68_action_clause_count']} action / {row['v68_nominal_block_count']} nominal).", "",
        ])
    report.extend([
        "## Limit", "",
        "V68 is a grammatical realization of the current exploratory German working",
        "reader. Clause boundaries come from the existing V62 action ordinals and",
        "accepted local bindings; they do not establish Voynich syntax or plaintext.",
        "No cross-token object, carry, connective, noun or verb is added.", "",
    ])
    (output_dir / "GDT695_V68_FIXED_WORD_CLAUSE_READER.md").write_text("\n".join(report), encoding="utf-8")
    (output_dir / "README.md").write_text(
        "# GDT695 artifacts\n\nThe complete token freeze, 175-clause table, 51-line reader, 83-position/115-verb audits, span freeze, baseline correction, word-sequence audit and mode census reproduce V68. `RESULT.json` binds their hashes; `VALIDATION.json` is written independently.\n",
        encoding="utf-8",
    )

    generated = [
        "GDT695_V68_FIXED_WORD_CLAUSE_READER.md", "README.md",
        "V61_V62_V67_VERB_BASELINE_CORRECTION.tsv",
        "V68_115_VERB_OCCURRENCE_PROVENANCE.tsv", "V68_175_CLAUSE_REALIZATIONS.tsv",
        "V68_3_BOUND_SPAN_FREEZE.tsv", "V68_479_TOKEN_FREEZE.tsv",
        "V68_51_LINE_CLAUSE_READER.tsv", "V68_51_LINE_WORD_SEQUENCE_AUDIT.tsv",
        "V68_83_ACTION_VERB_MULTISET_AUDIT.tsv", "V68_MODE_CENSUS.tsv",
    ]
    input_paths = [
        TOKENS, LINES, SPANS, G694_RESULT,
        V62_LINES, V62_VERBS, G689_RESULT, VERB_RULES,
        VALUE_BINDINGS, POLICY, INTRODUCERS, SRC / "run.py",
    ]
    changed_lines = sum(int(row["v68_changed_punctuation"]) for row in line_out)
    result: dict[str, object] = {
        "status": STATUS,
        "question": "Can the fixed V67 words be divided into executable action clauses and nominal register blocks under the live V62 action inventory without adding, deleting, reordering or reinterpreting any content word?",
        "basis": {
            "token_positions": 479, "lines": 51, "pages": len({row["page"] for row in token_rows}),
            "live_action_positions": 83, "active_verb_occurrences": 115, "bound_spans": 3,
            "accepted_inherited_bindings": 10, "right_bound_introducers": 4,
            "new_colon_edges": 9,
            "binding_inside_frozen_span": 1,
            "new_pages": 0, "f84_access": 0, "f84r_access": 0,
        },
        "clauses": {
            "total": 175, "action": 83, "nominal_blocks": 92,
            "action_bearing_lines": 39, "nominal_only_lines": 12,
            "punctuation_changed_lines": changed_lines,
            "one_written_action_card_per_action_clause": 1,
        },
        "freeze": {
            "token_glosses_byte_identical": 479, "bound_spans_byte_identical": 3,
            "lines_with_exact_content_word_sequence": 51,
            "content_word_additions": 0, "content_word_deletions": 0,
            "content_word_reorders": 0, "new_object_carries": 0,
        },
        "verbs": {
            "authoritative_baseline": "GDT689_V62", "action_position_sequences_exact": 83,
            "expected_occurrences": 115, "observed_occurrences": 115,
            "missing_occurrences": 0, "extra_occurrences": 0,
            "non_action_position_occurrences": 0,
            "superseded_v61_positions": 85, "superseded_v61_occurrences": 113,
        },
        "mode_census": {row["line_mode"]: row for row in mode_census},
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "files": {name: sha256(output_dir / name) for name in sorted(generated)},
        "next_gap": "On V68 only, test a finite exact deck of already licensed local object/carry edges; keep every unresolved deictic unresolved and add no fluent bridge.",
        "claim_ceiling": "V68 is a punctuation-only clause realization of the frozen exploratory V67 German renderer under the live GDT689 action deck. It adds no content meaning and does not establish Voynich syntax, plaintext or historical sentence boundaries.",
    }
    return result


def main() -> int:
    if len(sys.argv) > 2:
        raise SystemExit("usage: run.py [OUTPUT_DIR]")
    output_dir = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else ART
    result = build(output_dir)
    write_json(output_dir / "RESULT.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
