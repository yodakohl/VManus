#!/usr/bin/env python3
"""Independent validation for GDT572's complete nonstate bracket voice."""

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
BASE = ROOT / "experiments/yolo/gdt572_complete_nonstate_bracket_voice"
OUT = BASE / "artifacts"
G571 = ROOT / "experiments/yolo/gdt571_three_operator_two_slot_outer_voice/artifacts"
G569 = ROOT / "experiments/yolo/gdt569_four_context_carry_voice_frames/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
INPUTS = {
    "outer_events": G571 / "gdt571_5122_outer_voice_event_edition.tsv",
    "outer_statements": G571 / "gdt571_793_outer_voice_statement_edition.tsv",
    "page_profiles": G571 / "gdt571_30_page_outer_voice_profiles.tsv",
    "state_carry_forms": G569 / "gdt569_19_carried_argument_forms.tsv",
    "old_context": G416 / "gdt416_4576_imperative_clauses.tsv",
    "current_context": G539 / "gdt539_546_contextual_prose_events.tsv",
}
ARTIFACTS = {
    "inventory": OUT / "gdt572_4_bracket_marker_inventory.tsv",
    "signatures": OUT / "gdt572_11_bracket_signature_profiles.tsv",
    "carry_forms": OUT / "gdt572_20_nonstate_carried_argument_forms.tsv",
    "scope_cards": OUT / "gdt572_5_scope_voice_cards.tsv",
    "assignments": OUT / "gdt572_1536_bracket_voice_assignments.tsv",
    "changes": OUT / "gdt572_1156_changed_nonstate_clauses.tsv",
    "events": OUT / "gdt572_5122_bracket_free_event_edition.tsv",
    "statements": OUT / "gdt572_793_bracket_free_statement_edition.tsv",
    "pages": OUT / "gdt572_30_page_bracket_voice_profiles.tsv",
    "book": OUT / "GDT572_BRACKET_FREE_THIRTY_PAGE_EDITION.md",
    "result": OUT / "gdt572_result.json",
}
BRACKET_RE = re.compile(r"\[[^\]]+\]")
EXPECTED_MARKERS = Counter({"[wie zuvor]": 1292, "[außen]": 121, "[innen]": 121, "[Stufe 3]": 2})
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA")
ROOTS = ("Y", "AIIN", "AIN", "OR")
STATUS = (
    "PASS_4_BRACKET_TYPES__1536_OCCURRENCES__20_CARRY_FORMS__5_SCOPE_CARDS__"
    "1156_NONSTATE_CLAUSES_NATURALIZED__ZERO_BRACKETS__ZERO_ROOT_CHANGE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scoped_nominal(phrase: str, marker: str) -> str:
    article, noun = phrase.split(" ", 1)
    adjectives = {
        ("den", "[außen]"): "äußeren",
        ("den", "[innen]"): "inneren",
        ("die", "[außen]"): "äußere",
        ("die", "[innen]"): "innere",
    }
    return f"{article} {adjectives[(article, marker)]} {noun}"


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    source_events = read_tsv(INPUTS["outer_events"])
    source_statements = read_tsv(INPUTS["outer_statements"])
    source_pages = read_tsv(INPUTS["page_profiles"])
    old_forms = read_tsv(INPUTS["state_carry_forms"])
    old_context = read_tsv(INPUTS["old_context"])
    current_context = read_tsv(INPUTS["current_context"])
    inventory = read_tsv(ARTIFACTS["inventory"])
    signatures = read_tsv(ARTIFACTS["signatures"])
    carry_forms = read_tsv(ARTIFACTS["carry_forms"])
    scope_cards = read_tsv(ARTIFACTS["scope_cards"])
    assignments = read_tsv(ARTIFACTS["assignments"])
    changes = read_tsv(ARTIFACTS["changes"])
    events = read_tsv(ARTIFACTS["events"])
    statements = read_tsv(ARTIFACTS["statements"])
    pages = read_tsv(ARTIFACTS["pages"])
    result = json.loads(ARTIFACTS["result"].read_text(encoding="utf-8"))

    check("input_counts", [len(source_events), len(source_statements), len(source_pages), len(old_forms), len(old_context), len(current_context)] == [5122, 793, 30, 19, 4576, 546])
    check("artifact_counts", [len(inventory), len(signatures), len(carry_forms), len(scope_cards), len(assignments), len(changes), len(events), len(statements), len(pages)] == [4, 11, 20, 5, 1536, 1156, 5122, 793, 30])
    sealed_hits = sorted({row.get("physical_page", "") for table in (events, statements, pages) for row in table if row.get("physical_page", "").lower() in {"f84", "f84r"}})
    check("sealed_pages_absent", not sealed_hits, sealed_hits)
    check("assignment_ordinals", [int(row["assignment_ordinal"]) for row in assignments] == list(range(1, 1537)))
    check("change_ordinals", [int(row["change_ordinal"]) for row in changes] == list(range(1, 1157)))
    check("event_ordinals", [int(row["edition_event_ordinal"]) for row in events] == list(range(1, 5123)))
    check("statement_ordinals", [int(row["edition_statement_ordinal"]) for row in statements] == list(range(1, 794)))
    check("page_ordinals", [int(row["page_ordinal"]) for row in pages] == list(range(1, 31)))

    context: dict[str, tuple[str, str, str]] = {}
    for row in old_context:
        context[row["global_running_event_id"]] = ("GDT416_OLD26", row["inherited_argument_root"], "OWNER_CONTEXT_STATE")
    for row in current_context:
        context[row["event_id"]] = ("GDT539_CURRENT4", row["inherited_argument_root"], row["inherited_argument_source_event_id"])
    check("context_provenance_complete", len(context) == 5122 and set(context) == {row["event_id"] for row in source_events})

    form_map: dict[tuple[str, str], tuple[str, str, str]] = {}
    for row in old_forms:
        form_map[(row["register"], row["argument_root"])] = (row["explicit_argument_phrase_de"], row["carried_argument_phrase_de"], "REUSED")
    form_map[("CELESTIAL", "AIN")] = ("den Sektoranteil", "denselben Sektoranteil", "NEW")
    expected_form_keys = {(register, root) for register in REGISTERS for root in ROOTS}
    check("twenty_form_keys_complete", set(form_map) == expected_form_keys)
    check("one_new_celestial_ain_cell", sum(values[2] == "NEW" for values in form_map.values()) == 1 and form_map[("CELESTIAL", "AIN")][:2] == ("den Sektoranteil", "denselben Sektoranteil"))

    source_marker_counts: Counter[str] = Counter()
    source_marker_event_sets: dict[str, set[str]] = defaultdict(set)
    source_signatures: Counter[str] = Counter()
    source_bracket_ids: list[str] = []
    expected_targets: dict[str, str] = {}
    expected_assignments: list[tuple[object, ...]] = []
    carry_counts: Counter[tuple[str, str]] = Counter()
    carry_events: dict[tuple[str, str], set[str]] = defaultdict(set)
    scope_card_counts: Counter[str] = Counter()
    bracket_state_ids: list[str] = []
    provenance_errors: list[str] = []
    assignment_ordinal = 0

    for source in source_events:
        event_id = source["event_id"]
        current = source["outer_voice_working_clause_de"]
        matches = list(BRACKET_RE.finditer(current))
        markers = [match.group() for match in matches]
        if markers:
            source_bracket_ids.append(event_id)
            source_signatures["|".join(markers)] += 1
            if source["state_status"] != "NONSTATE_CARD":
                bracket_state_ids.append(event_id)
        register_forms = []
        for (register, root), values in form_map.items():
            if register == source["register"]:
                register_forms.append((values[0], root, values[1]))
        register_forms.sort(key=lambda item: len(item[0]), reverse=True)
        source_layer, inherited_root, inherited_source = context[event_id]

        for marker_ordinal, match in enumerate(matches, 1):
            marker = match.group()
            source_marker_counts[marker] += 1
            source_marker_event_sets[marker].add(event_id)
            prefix = current[: match.start()]
            found = next(((phrase, root, carried) for phrase, root, carried in register_forms if prefix.endswith(phrase + " ")), None)
            if marker == "[wie zuvor]":
                if found is None:
                    provenance_errors.append(event_id + ":NO_FORM")
                    continue
                phrase, root, carried = found
                if inherited_root != root:
                    provenance_errors.append(event_id + ":ROOT")
                card_id = f"GDT572-A{list((r, q) for r in REGISTERS for q in ROOTS).index((source['register'], root)) + 1:02d}"
                host_class = "INHERITED_ARGUMENT"
                source_fragment = phrase + " " + marker
                target_fragment = carried
                argument_root = root
                explicit_phrase = phrase
                inherited_source_out = inherited_source
                carry_counts[(source["register"], root)] += 1
                carry_events[(source["register"], root)].add(event_id)
            elif marker in {"[außen]", "[innen]"} and found is not None:
                phrase, root, _ = found
                card_id = "GDT572-S01" if marker == "[außen]" else "GDT572-S02"
                host_class = "NOMINAL_ARGUMENT_SCOPE"
                source_fragment = phrase + " " + marker
                target_fragment = scoped_nominal(phrase, marker)
                argument_root = root
                explicit_phrase = phrase
                inherited_source_out = "NOT_APPLICABLE"
                scope_card_counts[card_id] += 1
            elif marker in {"[außen]", "[innen]"}:
                card_id = "GDT572-S03" if marker == "[außen]" else "GDT572-S04"
                host_class = "NON_NOMINAL_SCOPE"
                source_fragment = marker
                target_fragment = "im äußeren Zweig" if marker == "[außen]" else "im inneren Zweig"
                argument_root = "NOT_APPLICABLE"
                explicit_phrase = "NON_NOMINAL_HOST"
                inherited_source_out = "NOT_APPLICABLE"
                scope_card_counts[card_id] += 1
            elif marker == "[Stufe 3]" and found is not None:
                phrase, root, _ = found
                card_id = "GDT572-S05"
                host_class = "THIRD_LEVEL_ARGUMENT_SCOPE"
                source_fragment = marker
                target_fragment = "auf Stufe drei"
                argument_root = root
                explicit_phrase = phrase
                inherited_source_out = "NOT_APPLICABLE"
                scope_card_counts[card_id] += 1
            else:
                provenance_errors.append(event_id + ":SCOPE_FORM")
                continue
            assignment_ordinal += 1
            expected_assignments.append((event_id, marker_ordinal, marker, host_class, argument_root, explicit_phrase, card_id, source_fragment, target_fragment, source_layer, inherited_source_out))

        target = current
        for phrase, _, carried in register_forms:
            target = target.replace(phrase + " [wie zuvor]", carried)
            target = target.replace(phrase + " [außen]", scoped_nominal(phrase, "[außen]"))
            target = target.replace(phrase + " [innen]", scoped_nominal(phrase, "[innen]"))
            target = target.replace(phrase + " [Stufe 3]", phrase + " auf Stufe drei")
        target = target.replace("[außen]", "im äußeren Zweig").replace("[innen]", "im inneren Zweig").replace("[Stufe 3]", "auf Stufe drei")
        expected_targets[event_id] = target

    check("source_marker_counts_exact", source_marker_counts == EXPECTED_MARKERS, dict(source_marker_counts))
    check("source_bracket_event_count", len(source_bracket_ids) == 1156)
    check("all_brackets_nonstate", not bracket_state_ids, bracket_state_ids[:10])
    check("eleven_source_signatures", len(source_signatures) == 11, dict(source_signatures))
    check("all_prior_markers_have_inherited_root", not provenance_errors, provenance_errors[:10])
    check("prior_marker_event_count", len(source_marker_event_sets["[wie zuvor]"]) == 1077)
    check("scope_marker_event_count", len(source_marker_event_sets["[außen]"] | source_marker_event_sets["[innen]"] | source_marker_event_sets["[Stufe 3]"]) == 90)
    check("all_targets_bracket_free", all(not BRACKET_RE.search(value) for value in expected_targets.values()))

    actual_assignments = [
        (
            row["event_id"], int(row["bracket_ordinal_in_clause"]), row["bracket_marker"], row["host_class"],
            row["argument_root"], row["explicit_argument_phrase_de"], row["replacement_card_id"],
            row["source_fragment_de"], row["target_fragment_de"], row["context_source_layer"],
            row["inherited_argument_source_event_id"],
        )
        for row in assignments
    ]
    check("all_1536_assignments_exact", actual_assignments == expected_assignments)
    check("assignment_keys_unique", len({(row["event_id"], row["bracket_ordinal_in_clause"]) for row in assignments}) == 1536)
    check("assignment_marker_order_exact", [row["bracket_marker"] for row in assignments] == [marker for source in source_events for marker in BRACKET_RE.findall(source["outer_voice_working_clause_de"])])

    inventory_map = {row["bracket_marker"]: row for row in inventory}
    check("four_marker_inventory_exact", set(inventory_map) == set(EXPECTED_MARKERS) and all(int(inventory_map[marker]["occurrence_count"]) == count and int(inventory_map[marker]["remaining_occurrence_count"]) == 0 for marker, count in EXPECTED_MARKERS.items()))
    check("eleven_signature_profiles_exact", {row["bracket_signature"]: int(row["event_count"]) for row in signatures} == dict(source_signatures))

    carry_by_key = {(row["register"], row["argument_root"]): row for row in carry_forms}
    carry_errors = []
    for key, (explicit, carried, status) in form_map.items():
        row = carry_by_key.get(key)
        if row is None or row["explicit_argument_phrase_de"] != explicit or row["carried_argument_phrase_de"] != carried or int(row["nonstate_carry_occurrence_count"]) != carry_counts[key] or int(row["nonstate_carry_event_count"]) != len(carry_events[key]):
            carry_errors.append("|".join(key))
        if status == "NEW" and row is not None and row["source_status"] != "NEWLY_OCCUPIED_NONSTATE_CARRY_CELL":
            carry_errors.append("NEW_STATUS")
    check("twenty_carry_forms_exact", len(carry_by_key) == 20 and not carry_errors, carry_errors)
    check("all_twenty_carry_forms_used", all(int(row["nonstate_carry_occurrence_count"]) > 0 for row in carry_forms))
    check("carry_occurrence_total", sum(int(row["nonstate_carry_occurrence_count"]) for row in carry_forms) == 1292)
    celestial = carry_by_key[("CELESTIAL", "AIN")]
    check("celestial_ain_usage_exact", int(celestial["nonstate_carry_occurrence_count"]) == 9 and int(celestial["nonstate_carry_event_count"]) == 8 and int(celestial["physical_page_count"]) == 1)

    expected_scope_counts = {"GDT572-S01": 104, "GDT572-S02": 104, "GDT572-S03": 17, "GDT572-S04": 17, "GDT572-S05": 2}
    scope_by_id = {row["scope_card_id"]: row for row in scope_cards}
    check("five_scope_cards_exact", set(scope_by_id) == set(expected_scope_counts) and all(int(scope_by_id[card_id]["occurrence_count"]) == count for card_id, count in expected_scope_counts.items()))
    check("scope_occurrence_total", sum(int(row["occurrence_count"]) for row in scope_cards) == 244)
    check("nominal_and_nonnominal_partition", sum(int(row["occurrence_count"]) for row in scope_cards if row["host_class"] == "NOMINAL_ARGUMENT_SCOPE") == 208 and sum(int(row["occurrence_count"]) for row in scope_cards if row["host_class"] == "NON_NOMINAL_SCOPE") == 34)

    source_event_by_id = {row["event_id"]: row for row in source_events}
    event_errors = []
    state_unchanged = 0
    nonstate_changed = 0
    nonstate_unchanged = 0
    for row in events:
        source = source_event_by_id[row["event_id"]]
        expected = expected_targets[row["event_id"]]
        changed = expected != source["outer_voice_working_clause_de"]
        if row["gdt571_outer_voice_clause_de"] != source["outer_voice_working_clause_de"] or row["bracket_free_working_clause_de"] != expected or row["bracket_voice_changed"] != ("YES" if changed else "NO") or int(row["remaining_bracket_count"]) != 0:
            event_errors.append(row["event_id"])
        if source["state_status"] != "NONSTATE_CARD":
            state_unchanged += expected == source["outer_voice_working_clause_de"]
        elif changed:
            nonstate_changed += 1
        else:
            nonstate_unchanged += 1
    check("all_5122_events_reconstructed", not event_errors, event_errors[:10])
    check("event_change_partition", (state_unchanged, nonstate_changed, nonstate_unchanged) == (1656, 1156, 2310), [state_unchanged, nonstate_changed, nonstate_unchanged])
    check("event_order_exact", [row["event_id"] for row in events] == [row["event_id"] for row in source_events])
    check("zero_brackets_in_complete_event_edition", sum(len(BRACKET_RE.findall(row["bracket_free_working_clause_de"])) for row in events) == 0)
    check("changed_audit_ids_exact", [row["event_id"] for row in changes] == source_bracket_ids)
    check("changed_audit_text_exact", all(row["before_clause_de"] == source_event_by_id[row["event_id"]]["outer_voice_working_clause_de"] and row["after_clause_de"] == expected_targets[row["event_id"]] for row in changes))

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    statement_errors = []
    changed_statement_ids: set[str] = set()
    for row in statements:
        source = source_statement_by_id[row["statement_id"]]
        local = events_by_statement[row["statement_id"]]
        current = " ".join(event["gdt571_outer_voice_clause_de"] for event in local)
        target = " ".join(event["bracket_free_working_clause_de"] for event in local)
        changed_count = sum(event["bracket_voice_changed"] == "YES" for event in local)
        if changed_count:
            changed_statement_ids.add(row["statement_id"])
        if current != source["outer_voice_working_reading_de"] or row["gdt571_outer_voice_reading_de"] != current or row["bracket_free_working_reading_de"] != target or int(row["changed_nonstate_event_count"]) != changed_count or int(row["remaining_bracket_count"]) != 0 or row["event_ids"] != source["event_ids"]:
            statement_errors.append(row["statement_id"])
    check("all_793_statements_reconstructed", not statement_errors, statement_errors[:10])
    check("statement_change_partition", len(changed_statement_ids) == 360 and Counter(row["bracket_voice_statement_changed"] for row in statements) == Counter({"NO": 433, "YES": 360}))
    check("statement_order_exact", [row["statement_id"] for row in statements] == [row["statement_id"] for row in source_statements])
    check("zero_brackets_in_statements", all(int(row["remaining_bracket_count"]) == 0 and not BRACKET_RE.search(row["bracket_free_working_reading_de"]) for row in statements))

    changed_pages = {source_event_by_id[event_id]["physical_page"] for event_id in source_bracket_ids}
    check("page_order_exact", [row["physical_page"] for row in pages] == [row["physical_page"] for row in source_pages])
    check("changed_page_count", len(changed_pages) == 28, sorted(changed_pages))
    check("page_assignment_total", sum(int(row["bracket_occurrence_count"]) for row in pages) == 1536)
    check("zero_running_pages_retained", {row["physical_page"] for row in pages if int(row["event_count"]) == 0} == {"f69v", "f70v"})

    expected_metrics = {
        "bracket_marker_type_count": 4,
        "bracket_signature_count": 11,
        "bracket_occurrence_count": 1536,
        "bracket_bearing_nonstate_event_count": 1156,
        "prior_marker_occurrence_count": 1292,
        "prior_marker_event_count": 1077,
        "scope_marker_occurrence_count": 244,
        "scope_marker_event_count": 90,
        "old_carry_form_count": 19,
        "newly_occupied_carry_form_count": 1,
        "complete_carry_form_count": 20,
        "scope_voice_card_count": 5,
        "changed_nonstate_event_count": 1156,
        "unchanged_nonstate_event_count": 2310,
        "unchanged_state_event_count": 1656,
        "changed_statement_count": 360,
        "unchanged_statement_count": 433,
        "changed_physical_page_count": 28,
        "remaining_bracket_occurrence_count": 0,
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
    check("result_metrics_exact", result.get("metrics") == expected_metrics, result.get("metrics"))
    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("input_hashes_exact", result.get("input_sha256") == {name: sha256(path) for name, path in INPUTS.items()})
    book = ARTIFACTS["book"].read_text(encoding="utf-8")
    check("book_metrics_present", "Events: 5122 · statements: 793 · pages: 30 · changed nonstate clauses: 1156 · remaining brackets: 0." in book)
    check("book_all_pages_once", all(book.count(f"## {row['physical_page']}\n") == 1 for row in pages))
    check("book_all_statements", sum(line[:1].isdigit() and ". " in line for line in book.splitlines()) == 793)
    check("book_bracket_free", not BRACKET_RE.search(book))

    pre_hashes = {name: sha256(path) for name, path in ARTIFACTS.items() if name != "result"}
    run = subprocess.run(
        ["python3", str(BASE / "src/run.py")],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    post_hashes = {name: sha256(path) for name, path in ARTIFACTS.items() if name != "result"}
    check("deterministic_replay_exit", run.returncode == 0, run.stderr[-1000:])
    check("deterministic_artifact_hashes", pre_hashes == post_hashes, {name: (pre_hashes[name], post_hashes[name]) for name in pre_hashes if pre_hashes[name] != post_hashes[name]})
    check("deterministic_result_object", json.loads(ARTIFACTS["result"].read_text(encoding="utf-8")) == result)

    failed = [row for row in checks if not row["passed"]]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "artifact_sha256": {name: sha256(path) for name, path in ARTIFACTS.items()},
        "checks": checks,
    }
    (OUT / "gdt572_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
