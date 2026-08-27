#!/usr/bin/env python3
"""Independent validation for GDT570's modifier voice and join deck."""

from __future__ import annotations

import csv
import hashlib
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
BASE = ROOT / "experiments/yolo/gdt570_five_fragment_four_join_modifier_voice"
OUT = BASE / "artifacts"
G569 = ROOT / "experiments/yolo/gdt569_four_context_carry_voice_frames/artifacts"
G567 = ROOT / "experiments/yolo/gdt567_owner_voice_seam_adapter/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
INPUTS = {
    "context_events": G569 / "gdt569_5122_context_voice_event_edition.tsv",
    "context_statements": G569 / "gdt569_793_context_voice_statement_edition.tsv",
    "context_states": G569 / "gdt569_1656_context_voice_state_clauses.tsv",
    "page_profiles": G569 / "gdt569_30_page_context_voice_profiles.tsv",
    "state_replay": G565 / "gdt565_1656_template_replay.tsv",
    "voice_cards": G567 / "gdt567_39_owner_voice_adapter_cards.tsv",
}
ARTIFACTS = {
    "fragments": OUT / "gdt570_5_modifier_fragment_voice_cards.tsv",
    "joins": OUT / "gdt570_4_modifier_join_cards.tsv",
    "transitions": OUT / "gdt570_16_modifier_type_transition_profiles.tsv",
    "cells": OUT / "gdt570_154_register_modifier_cells.tsv",
    "changes": OUT / "gdt570_164_changed_modifier_clauses.tsv",
    "states": OUT / "gdt570_1656_modifier_voice_state_clauses.tsv",
    "events": OUT / "gdt570_5122_modifier_voice_event_edition.tsv",
    "statements": OUT / "gdt570_793_modifier_voice_statement_edition.tsv",
    "pages": OUT / "gdt570_30_page_modifier_voice_profiles.tsv",
    "book": OUT / "GDT570_MODIFIER_VOICE_THIRTY_PAGE_EDITION.md",
    "result": OUT / "gdt570_result.json",
}
STATUS = (
    "PASS_5_FRAGMENT_CARDS__4_JOIN_RULES__154_MODIFIER_CELLS__224_TRANSITIONS__"
    "103_WITHIN_CLASS_COORDINATED__164_STATE_CLAUSES_REFINED__ZERO_ROOT_CHANGE"
)
CURRENT = {
    "E": "auf Grad I", "EE": "auf Grad II", "EEE": "auf Grad III",
    "IIN": "auf der Stufe", "DA": "auf der zweiten Stufe",
    "O": "zur Ausführung", "CARRIER_Q": "am Beginn",
    "AN": "als Klasse", "LOCAL_CHAR_G": "als Variante",
}
TARGET = {
    **CURRENT,
    "IIN": "auf der bezeichneten Stufe", "O": "als Ausführung",
    "CARRIER_Q": "als neuen Einsatz", "AN": "in der bezeichneten Klasse",
    "LOCAL_CHAR_G": "mit der lokalen Variante",
}
CHANGED_ATOMS = ("O", "IIN", "CARRIER_Q", "AN", "LOCAL_CHAR_G")
HERE = {"AM_ADDR", "A_ADDR", "D_ADDR", "D_LABEL", "LOCAL_CHAR_F", "M_LOCAL", "S_ADDR"}
CLASSES = {
    "GRADE": "OPERATIONAL_MODIFIER",
    "FORMAL_CONTROL": "OPERATIONAL_MODIFIER",
    "RELATION": "RELATION",
    "LOCAL_OR_CLASS_SIGN": "LOCAL_OR_CLASS_SIGN",
}
JOIN_IDS = {
    "OPERATIONAL_MODIFIER": "GDT570-J01",
    "RELATION": "GDT570-J02",
    "LOCAL_OR_CLASS_SIGN": "GDT570-J03",
    "CROSS_CLASS": "GDT570-J04",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("+")


def coordinate(parts: list[str]) -> str:
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " und " + parts[-1]


def target_join(fragments: list[str], types: list[str]) -> tuple[str, list[str], int, int]:
    groups: list[tuple[str, list[str]]] = []
    for phrase, type_name in zip(fragments, types):
        class_name = CLASSES[type_name]
        if groups and groups[-1][0] == class_name:
            groups[-1][1].append(phrase)
        else:
            groups.append((class_name, [phrase]))
    classes = [class_name for class_name, _ in groups]
    transitions = list(zip(types, types[1:]))
    within = sum(CLASSES[left] == CLASSES[right] for left, right in transitions)
    return "; ".join(coordinate(parts) for _, parts in groups), classes, within, len(transitions) - within


def replace_ci(text: str, old: str, new: str) -> str:
    match = re.search(re.escape(old), text, re.IGNORECASE)
    if match is None:
        raise RuntimeError(f"Missing modifier phrase {old!r}")
    replacement = new[0].upper() + new[1:] if match.group()[0].isupper() else new
    return text[:match.start()] + replacement + text[match.end():]


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    source_events = read_tsv(INPUTS["context_events"])
    source_statements = read_tsv(INPUTS["context_statements"])
    source_states = read_tsv(INPUTS["context_states"])
    source_pages = read_tsv(INPUTS["page_profiles"])
    replay = read_tsv(INPUTS["state_replay"])
    voice_cards = read_tsv(INPUTS["voice_cards"])
    fragments = read_tsv(ARTIFACTS["fragments"])
    joins = read_tsv(ARTIFACTS["joins"])
    transitions = read_tsv(ARTIFACTS["transitions"])
    cells = read_tsv(ARTIFACTS["cells"])
    changes = read_tsv(ARTIFACTS["changes"])
    states = read_tsv(ARTIFACTS["states"])
    events = read_tsv(ARTIFACTS["events"])
    statements = read_tsv(ARTIFACTS["statements"])
    pages = read_tsv(ARTIFACTS["pages"])
    result = json.loads(ARTIFACTS["result"].read_text(encoding="utf-8"))

    check("input_counts", [len(source_events), len(source_statements), len(source_states), len(source_pages), len(replay), len(voice_cards)] == [5122, 793, 1656, 30, 1656, 39])
    check("artifact_counts", [len(fragments), len(joins), len(transitions), len(cells), len(changes), len(states), len(events), len(statements), len(pages)] == [5, 4, 16, 154, 164, 1656, 5122, 793, 30])
    observed_pages = {row["physical_page"] for row in events}
    check("sealed_pages_absent", not any(page.startswith("f84") for page in observed_pages), sorted(page for page in observed_pages if page.startswith("f84")))
    check("event_ordinals", [int(row["edition_event_ordinal"]) for row in events] == list(range(1, 5123)))
    check("state_ordinals", [int(row["state_edition_ordinal"]) for row in states] == list(range(1, 1657)))
    check("statement_ordinals", [int(row["edition_statement_ordinal"]) for row in statements] == list(range(1, 794)))
    check("page_ordinals", [int(row["page_ordinal"]) for row in pages] == list(range(1, 31)))

    source_event_by_id = {row["event_id"]: row for row in source_events}
    source_state_by_id = {row["event_id"]: row for row in source_states}
    replay_by_id = {row["event_id"]: row for row in replay}
    state_by_id = {row["event_id"]: row for row in states}
    check("keys_unique", len(source_event_by_id) == 5122 and len(source_state_by_id) == len(replay_by_id) == len(state_by_id) == 1656)
    check("state_partition_exact", set(state_by_id) == set(source_state_by_id) == {row["event_id"] for row in source_events if row["state_status"] == "STATE_CARD"})

    relation_map = {
        (row["register_scope"], row["root_or_trigger"]): row["owner_voice_phrase_de"]
        for row in voice_cards if row["card_class"] == "RELATION_OWNER_VOICE"
    }
    check("relation_voice_cells", len(relation_map) == 18)

    def phrase(atom: str, register: str, target: bool) -> str:
        mapping = TARGET if target else CURRENT
        if atom in mapping:
            return mapping[atom]
        if atom in HERE:
            return "an der bezeichneten Stelle"
        return relation_map[(register, atom)]

    state_errors = []
    modifier_events = multi_events = within_total = cross_total = 0
    term_event_ids = set()
    join_event_ids = set()
    term_occurrences = 0
    current_phrases = set()
    target_phrases = set()
    expected_transition_counts: Counter[tuple[str, str]] = Counter()
    for eid, output in state_by_id.items():
        source = source_state_by_id[eid]
        state = replay_by_id[eid]
        atoms = split(state["modifier_atoms"])
        types = split(state["modifier_type_sequence"])
        current_fragments = [phrase(atom, state["register"], False) for atom in atoms]
        target_fragments = [phrase(atom, state["register"], True) for atom in atoms]
        current_phrase = "; ".join(current_fragments) if atoms else "NONE"
        expected = source["context_voice_working_clause_de"]
        if atoms:
            target_phrase, group_classes, within, cross = target_join(target_fragments, types)
            expected = replace_ci(expected, current_phrase, target_phrase)
            modifier_events += 1
            multi_events += len(atoms) > 1
            current_phrases.add(current_phrase)
            target_phrases.add(target_phrase)
        else:
            target_phrase, group_classes, within, cross = "NONE", [], 0, 0
        changed_atoms = [atom for atom in atoms if atom in CHANGED_ATOMS]
        if changed_atoms:
            term_event_ids.add(eid)
            term_occurrences += sum(atoms.count(atom) for atom in CHANGED_ATOMS)
        if within:
            join_event_ids.add(eid)
        within_total += within
        cross_total += cross
        for pair in zip(types, types[1:]):
            expected_transition_counts[pair] += 1
        conditions = [
            output["modifier_atoms"] == state["modifier_atoms"],
            output["modifier_type_sequence"] == state["modifier_type_sequence"],
            int(output["modifier_count"]) == len(atoms),
            int(output["within_class_transition_count"]) == within,
            int(output["cross_class_transition_count"]) == cross,
            output["modifier_join_group_sequence"] == ("+".join(group_classes) or "NONE"),
            output["changed_fragment_atoms"] == ("|".join(changed_atoms) or "NONE"),
            output["current_modifier_phrase_de"] == current_phrase,
            output["modifier_voice_phrase_de"] == target_phrase,
            output["modifier_voice_working_clause_de"] == expected,
            output["modifier_voice_changed"] == ("YES" if expected != source["context_voice_working_clause_de"] else "NO"),
            output["final_context_recipe"] == source["final_context_recipe"],
            output["state_atom_alignment"] == source["state_atom_alignment"],
        ]
        if not all(conditions):
            state_errors.append(eid)
    check("all_state_transformations_exact", not state_errors, state_errors[:20])
    check("modifier_state_counts", [modifier_events, 1656 - modifier_events, multi_events] == [1042, 614, 172], [modifier_events, 1656 - modifier_events, multi_events])
    check("transition_totals", [within_total + cross_total, within_total, cross_total] == [224, 103, 121], [within_total + cross_total, within_total, cross_total])
    check("term_and_join_event_counts", [len(term_event_ids), term_occurrences, len(join_event_ids), len(term_event_ids | join_event_ids)] == [154, 176, 92, 164])
    check("modifier_phrase_inventory", [len(current_phrases), len(target_phrases)] == [94, 94])

    fragment_by_atom = {row["modifier_atom"]: row for row in fragments}
    check("five_fragment_cards_exact", set(fragment_by_atom) == set(CHANGED_ATOMS) and [row["modifier_voice_card_id"] for row in fragments] == [f"GDT570-F{i:02d}" for i in range(1, 6)])
    fragment_errors = []
    expected_fragment_counts = {"O": (144, 146, 129), "IIN": (8, 8, 8), "CARRIER_Q": (18, 18, 17), "AN": (3, 3, 3), "LOCAL_CHAR_G": (1, 1, 1)}
    for atom, row in fragment_by_atom.items():
        expected_event_count, expected_occurrences, expected_support = expected_fragment_counts[atom]
        if not (
            row["current_fragment_de"] == CURRENT[atom]
            and row["modifier_voice_fragment_de"] == TARGET[atom]
            and int(row["state_event_count"]) == expected_event_count
            and int(row["modifier_occurrence_count"]) == expected_occurrences
            and int(row["owner_control_target_event_support_count"]) == expected_support
        ):
            fragment_errors.append(atom)
    check("fragment_card_counts_and_support", not fragment_errors, fragment_errors)
    check("fragment_guards", all(row["guard"] == "GERMAN_FRAGMENT_VOICE_ONLY__ATOM_VALUE_UNCHANGED" for row in fragments))

    transition_by_pair = {(row["left_modifier_type"], row["right_modifier_type"]): row for row in transitions}
    expected_pairs = {(left, right) for left in CLASSES for right in CLASSES}
    check("sixteen_transition_profiles", set(transition_by_pair) == expected_pairs)
    transition_errors = []
    for pair, row in transition_by_pair.items():
        same = CLASSES[pair[0]] == CLASSES[pair[1]]
        expected_card = JOIN_IDS[CLASSES[pair[0]] if same else "CROSS_CLASS"]
        if int(row["transition_occurrence_count"]) != expected_transition_counts[pair] or row["join_card_id"] != expected_card:
            transition_errors.append("->".join(pair))
    check("transition_profile_counts_exact", not transition_errors, transition_errors)
    check("all_transition_occurrences_accounted", sum(int(row["transition_occurrence_count"]) for row in transitions) == 224)

    join_by_class = {row["join_class"]: row for row in joins}
    expected_join_counts = {
        "OPERATIONAL_MODIFIER": ("GDT570-J01", 4, 96, 86),
        "RELATION": ("GDT570-J02", 1, 2, 2),
        "LOCAL_OR_CLASS_SIGN": ("GDT570-J03", 1, 5, 5),
        "CROSS_CLASS": ("GDT570-J04", 10, 121, 103),
    }
    join_errors = []
    for class_name, expected in expected_join_counts.items():
        row = join_by_class.get(class_name, {})
        observed = (row.get("modifier_join_card_id"), int(row.get("type_pair_count", -1)), int(row.get("transition_occurrence_count", -1)), int(row.get("state_event_count", -1)))
        if observed != expected:
            join_errors.append((class_name, observed, expected))
    check("four_join_cards_exact", not join_errors, join_errors)
    check("join_guards", all(row["guard"] == "CONTIGUOUS_TYPE_RUN_JOIN__WRITTEN_ORDER_UNCHANGED" for row in joins))

    expected_cells = defaultdict(list)
    for row in states:
        if row["modifier_atoms"] != "NONE":
            expected_cells[(row["register"], row["modifier_atoms"])].append(row)
    output_cells = {(row["register"], row["modifier_atoms"]): row for row in cells}
    check("modifier_cell_keys_exact", set(output_cells) == set(expected_cells) and len(output_cells) == 154)
    cell_errors = []
    for key, members in expected_cells.items():
        row = output_cells[key]
        if int(row["state_event_count"]) != len(members) or row["current_modifier_phrase_de"] != members[0]["current_modifier_phrase_de"] or row["modifier_voice_phrase_de"] != members[0]["modifier_voice_phrase_de"]:
            cell_errors.append("|".join(key))
    check("modifier_cell_aggregation_exact", not cell_errors, cell_errors[:20])

    changed_ids = [row["event_id"] for row in states if row["modifier_voice_changed"] == "YES"]
    check("changed_audit_ids_exact", [row["event_id"] for row in changes] == changed_ids and [int(row["changed_modifier_ordinal"]) for row in changes] == list(range(1, 165)))
    check("state_change_partition", Counter(row["modifier_voice_changed"] for row in states) == Counter({"YES": 164, "NO": 1492}))

    event_errors = []
    output_state_by_id = {row["event_id"]: row for row in states}
    for source, output in zip(source_events, events):
        if [source[key] for key in ("event_id", "statement_id", "physical_page", "surface", "final_context_recipe", "state_status")] != [output[key] for key in ("event_id", "statement_id", "physical_page", "surface", "final_context_recipe", "state_status")]:
            event_errors.append(source["event_id"])
            continue
        expected = output_state_by_id[source["event_id"]]["modifier_voice_working_clause_de"] if source["event_id"] in output_state_by_id else source["context_voice_working_clause_de"]
        if output["modifier_voice_working_clause_de"] != expected:
            event_errors.append(source["event_id"])
    check("all_5122_events_reconstructed", not event_errors, event_errors[:20])
    nonstates = [row for row in events if row["state_status"] == "NONSTATE_CARD"]
    check("nonstate_byte_unchanged", len(nonstates) == 3466 and all(row["gdt569_context_voice_clause_de"] == row["modifier_voice_working_clause_de"] for row in nonstates))

    event_by_id = {row["event_id"]: row for row in events}
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    statement_errors = []
    for output in statements:
        source = source_statement_by_id[output["statement_id"]]
        members = [event_by_id[eid] for eid in output["event_ids"].split("|")]
        before = " ".join(row["gdt569_context_voice_clause_de"] for row in members)
        after = " ".join(row["modifier_voice_working_clause_de"] for row in members)
        if before != source["context_voice_working_reading_de"] or after != output["modifier_voice_working_reading_de"]:
            statement_errors.append(output["statement_id"])
    check("all_793_statements_reconstructed", not statement_errors, statement_errors[:20])
    check("statement_change_partition", Counter(row["modifier_voice_statement_changed"] for row in statements) == Counter({"YES": 126, "NO": 667}))
    check("statement_event_order_exact", all(row["event_ids"] == source_statement_by_id[row["statement_id"]]["event_ids"] for row in statements))

    check("page_order_exact", [row["physical_page"] for row in pages] == [row["physical_page"] for row in source_pages])
    check("page_count_parity", all(row["event_count"] == source_pages[index]["event_count"] and row["statement_count"] == source_pages[index]["statement_count"] for index, row in enumerate(pages)))
    check("changed_page_count", sum(int(row["modifier_voice_changed_state_event_count"]) > 0 for row in pages) == 27)
    check("zero_running_pages_retained", [row["physical_page"] for row in pages if int(row["event_count"]) == 0] == ["f69v", "f70v"])

    expected_metrics = {
        "modifier_fragment_voice_card_count": 5,
        "modifier_join_card_count": 4,
        "modifier_transition_type_count": 16,
        "modifier_transition_occurrence_count": 224,
        "within_class_coordinated_transition_count": 103,
        "cross_class_semicolon_transition_count": 121,
        "modifier_bearing_state_event_count": 1042,
        "modifierless_state_event_count": 614,
        "multi_modifier_state_event_count": 172,
        "register_modifier_cell_count": 154,
        "changed_fragment_event_count": 154,
        "changed_fragment_occurrence_count": 176,
        "within_class_join_event_count": 92,
        "changed_state_event_count": 164,
        "unchanged_state_event_count": 1492,
        "changed_statement_count": 126,
        "unchanged_statement_count": 667,
        "changed_physical_page_count": 27,
        "distinct_current_modifier_phrase_count": 94,
        "distinct_modifier_voice_phrase_count": 94,
        "owner_control_target_fragment_event_use_count": 158,
        "owner_control_fragment_event_use_count": 174,
        "dominant_voice_override_event_use_count": 16,
        "state_event_count": 1656,
        "nonstate_event_count": 3466,
        "nonstate_byte_unchanged_count": 3466,
        "complete_event_count": 5122,
        "complete_statement_count": 793,
        "complete_page_count": 30,
        "new_pages": 0,
        "new_events": 0,
        "new_statements": 0,
        "new_surfaces": 0,
        "new_recipes": 0,
        "new_root_values": 0,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_metrics.items()), {key: result.get(key) for key in expected_metrics})
    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    input_hashes = {name: sha256(path) for name, path in INPUTS.items()}
    check("input_hashes_exact", result.get("input_sha256") == input_hashes)
    book_text = ARTIFACTS["book"].read_text(encoding="utf-8")
    check("book_metrics_present", all(text in book_text for text in ("1.042 Modifierkarten", "224 Übergänge", "103 gleichklassig koordiniert", "164 verfeinerte Zustandszeilen")))
    check("book_all_pages_once", all(book_text.count(f"## {row['physical_page']}\n") == 1 for row in pages))
    check("book_all_statements", sum(line.startswith("### G") for line in book_text.splitlines()) == 793)

    before_hashes = {name: sha256(path) for name, path in ARTIFACTS.items()}
    replay_process = subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, capture_output=True, text=True, check=False)
    after_hashes = {name: sha256(path) for name, path in ARTIFACTS.items()}
    check("deterministic_replay_exit", replay_process.returncode == 0, replay_process.stderr[-1000:])
    check("deterministic_artifact_hashes", before_hashes == after_hashes, {name: [before_hashes[name], after_hashes[name]] for name in before_hashes if before_hashes[name] != after_hashes[name]})

    passed = sum(row["passed"] for row in checks)
    validation = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "check_count": len(checks),
        "passed_count": passed,
        "failed_count": len(checks) - passed,
        "input_sha256": input_hashes,
        "artifact_sha256": {name: sha256(path) for name, path in ARTIFACTS.items()},
        "checks": checks,
    }
    (OUT / "gdt570_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
