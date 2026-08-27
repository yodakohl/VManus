#!/usr/bin/env python3
"""Independent validation for GDT574's adjacent-action count voice."""

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
BASE = ROOT / "experiments/yolo/gdt574_adjacent_action_count_voice"
OUT = BASE / "artifacts"
G573 = ROOT / "experiments/yolo/gdt573_intra_clause_argument_pronoun_voice/artifacts"
G568 = ROOT / "experiments/yolo/gdt568_twenty_owner_action_voice_frames/artifacts"
G500 = ROOT / "experiments/yolo/gdt500_repeated_action_fluency_matrix/artifacts"
INPUTS = {
    "events": G573 / "gdt573_5122_pronoun_voice_event_edition.tsv",
    "statements": G573 / "gdt573_793_pronoun_voice_statement_edition.tsv",
    "pages": G573 / "gdt573_30_page_pronoun_voice_profiles.tsv",
    "owner_action_cards": G568 / "gdt568_20_owner_action_voice_cards.tsv",
    "prior_twice_cards": G500 / "gdt500_15_repeated_action_fluency_cards.tsv",
}
ARTIFACTS = {
    "topology_events": OUT / "gdt574_105_repeated_action_events.tsv",
    "profiles": OUT / "gdt574_28_repeated_action_sequence_profiles.tsv",
    "cards": OUT / "gdt574_5_action_count_cards.tsv",
    "assignments": OUT / "gdt574_43_adjacent_action_pair_assignments.tsv",
    "changes": OUT / "gdt574_36_changed_action_clauses.tsv",
    "events": OUT / "gdt574_5122_action_count_event_edition.tsv",
    "statements": OUT / "gdt574_793_action_count_statement_edition.tsv",
    "pages": OUT / "gdt574_30_page_action_count_profiles.tsv",
    "book": OUT / "GDT574_ACTION_COUNT_VOICE_THIRTY_PAGE_EDITION.md",
    "result": OUT / "gdt574_result.json",
}
ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
STATUS = (
    "PASS_105_REPEAT_ACTION_EVENTS__43_RAW_ADJACENT_PAIRS__5_COUNT_CARDS__"
    "36_NEW_PLUS_7_RETAINED_TWICE__62_INTERRUPTED_ORDER_EXPLICIT__"
    "5122_EXACT_ROUNDTRIPS__ZERO_ROOT_CHANGE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pronoun(argument: str) -> str:
    return "sie" if argument.lower().startswith(("die ", "dieselbe ")) else "ihn"


def expected_card(row: dict[str, str], root: str, clause: str) -> str:
    if root == "OK":
        return "GDT574-C05"
    if re.match(r"^(?:Weiter: |Danach: )?(?:Nimm|nimm|Entnimm|entnimm)(?:,| und) (?:nimm|entnimm)", clause):
        return "GDT574-C04"
    if row["register"] == "CELESTIAL":
        return "GDT574-C03"
    if row["register"] in {"SOURCE_SECTION_T", "BIOLOGICAL"}:
        return "GDT574-C01"
    return "GDT574-C02"


def independent_transform(clause: str, card_id: str) -> dict[str, object]:
    prefix_pattern = r"(?P<prefix>(?:Weiter|Danach): )?"
    old = "zweimal" in clause
    if card_id in {"GDT574-C01", "GDT574-C02"}:
        first = r"(?P<verb>Entnimm|entnimm)" if card_id.endswith("01") else r"(?P<verb>Nimm|nimm)"
        second = "entnimm" if card_id.endswith("01") else "nimm"
        pattern = (
            re.compile(r"^" + prefix_pattern + r"(?P<pair>" + first + r" (?P<arg>.+?) zweimal)(?P<tail>.*)$")
            if old
            else re.compile(r"^" + prefix_pattern + r"(?P<pair>" + first + r" (?P<arg>.+?)(?P<join>,| und) " + second + r" (?P<pro>ihn|sie))(?P<tail>.*)$")
        )
    elif card_id == "GDT574-C03":
        pattern = (
            re.compile(r"^" + prefix_pattern + r"(?P<pair>(?P<verb>Nimm|nimm) (?P<arg>.+?) zweimal auf)(?P<tail>.*)$")
            if old
            else re.compile(r"^" + prefix_pattern + r"(?P<pair>(?P<verb>Nimm|nimm) (?P<arg>.+?) auf(?P<join>,| und) nimm (?P<pro>ihn|sie) auf)(?P<tail>.*)$")
        )
    elif card_id == "GDT574-C04":
        pattern = (
            re.compile(r"^" + prefix_pattern + r"(?P<pair>(?P<verb>Nimm|nimm|Entnimm|entnimm) zweimal)(?P<tail>.*)$")
            if old
            else re.compile(r"^" + prefix_pattern + r"(?P<pair>(?P<verb>Nimm|nimm|Entnimm|entnimm)(?P<join>,| und) (?P<second>nimm|entnimm))(?P<tail>.*)$")
        )
    else:
        pattern = (
            re.compile(r"^" + prefix_pattern + r"(?P<pair>(?P<verb>Setze|setze) (?P<arg>.+?) im Arbeitsgang zweimal an)(?P<tail>.*)$")
            if old
            else re.compile(r"^" + prefix_pattern + r"(?P<pair>(?P<verb>Setze|setze) (?P<arg>.+?) im Arbeitsgang an(?P<join>,| und) setze (?P<pro>ihn|sie) im Arbeitsgang an)(?P<tail>.*)$")
        )
    match = pattern.match(clause)
    if match is None:
        raise RuntimeError(f"Independent frame mismatch {card_id}: {clause}")
    data = match.groupdict()
    prefix = data.get("prefix") or ""
    verb = data["verb"]
    argument = data.get("arg")
    if card_id in {"GDT574-C01", "GDT574-C02"}:
        second = "entnimm" if card_id.endswith("01") else "nimm"
        target_pair = f"{verb} {argument} zweimal"
        expanded_pair = data["pair"] if not old else f"{verb} {argument}, {second} {pronoun(str(argument))}"
    elif card_id == "GDT574-C03":
        target_pair = f"{verb} {argument} zweimal auf"
        expanded_pair = data["pair"] if not old else f"{verb} {argument} auf, nimm {pronoun(str(argument))} auf"
    elif card_id == "GDT574-C04":
        target_pair = f"{verb} zweimal"
        second = "entnimm" if verb.lower() == "entnimm" else "nimm"
        expanded_pair = data["pair"] if not old else f"{verb}, {second}"
    else:
        target_pair = f"{verb} {argument} im Arbeitsgang zweimal an"
        expanded_pair = data["pair"] if not old else f"{verb} {argument} im Arbeitsgang an, setze {pronoun(str(argument))} im Arbeitsgang an"
    target = prefix + target_pair + data["tail"]
    start = len(prefix)
    return {
        "target": target, "source_pair": data["pair"], "target_pair": target_pair,
        "expanded_pair": expanded_pair, "source_start": start, "source_end": start + len(data["pair"]),
        "target_start": start, "target_end": start + len(target_pair), "old": old,
    }


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    source_events = read_tsv(INPUTS["events"])
    source_statements = read_tsv(INPUTS["statements"])
    source_pages = read_tsv(INPUTS["pages"])
    owner_cards = read_tsv(INPUTS["owner_action_cards"])
    prior_cards = read_tsv(INPUTS["prior_twice_cards"])
    topology_events = read_tsv(ARTIFACTS["topology_events"])
    profiles = read_tsv(ARTIFACTS["profiles"])
    cards = read_tsv(ARTIFACTS["cards"])
    assignments = read_tsv(ARTIFACTS["assignments"])
    changes = read_tsv(ARTIFACTS["changes"])
    events = read_tsv(ARTIFACTS["events"])
    statements = read_tsv(ARTIFACTS["statements"])
    pages = read_tsv(ARTIFACTS["pages"])
    result = json.loads(ARTIFACTS["result"].read_text(encoding="utf-8"))

    check("input_counts", [len(source_events), len(source_statements), len(source_pages), len(owner_cards), len(prior_cards)] == [5122, 793, 30, 20, 15])
    check("artifact_counts", [len(topology_events), len(profiles), len(cards), len(assignments), len(changes), len(events), len(statements), len(pages)] == [105, 28, 5, 43, 36, 5122, 793, 30])
    sealed_hits = sorted({row.get("physical_page", "").lower() for table in (events, statements, pages) for row in table if row.get("physical_page", "").lower() in {"f84", "f84r"}})
    check("sealed_pages_absent", not sealed_hits, sealed_hits)
    check("topology_ordinals", [int(row["repeated_event_ordinal"]) for row in topology_events] == list(range(1, 106)))
    check("profile_ordinals", [int(row["profile_ordinal"]) for row in profiles] == list(range(1, 29)))
    check("card_ordinals", [int(row["count_card_ordinal"]) for row in cards] == list(range(1, 6)))
    check("assignment_ordinals", [int(row["assignment_ordinal"]) for row in assignments] == list(range(1, 44)))
    check("change_ordinals", [int(row["change_ordinal"]) for row in changes] == list(range(1, 37)))
    check("event_ordinals", [int(row["edition_event_ordinal"]) for row in events] == list(range(1, 5123)))
    check("statement_ordinals", [int(row["edition_statement_ordinal"]) for row in statements] == list(range(1, 794)))
    check("page_ordinals", [int(row["page_ordinal"]) for row in pages] == list(range(1, 31)))

    owner_by_id = {row["action_voice_card_id"]: row for row in owner_cards}
    check("owner_frame_source", owner_by_id["GDT568-A02"]["owner_with_argument_de"] == "setze {argument} im Arbeitsgang an" and owner_by_id["GDT568-A06"]["owner_with_argument_de"] == "entnimm {argument}" and owner_by_id["GDT568-A07"]["owner_with_argument_de"] == "nimm {argument}" and owner_by_id["GDT568-A08"]["owner_with_argument_de"] == "nimm {argument} auf")
    check("prior_twice_precedent", Counter(row["compressed_count_marker_de"] for row in prior_cards) == Counter({"zweimal": 15}) and all(row["action_slot_count_retained"] == "2" and row["exact_source_phrase_roundtrip"] == "YES" for row in prior_cards))
    expected_card_ids = [f"GDT574-C{n:02d}" for n in range(1, 6)]
    check("five_card_ids", [row["count_card_id"] for row in cards] == expected_card_ids)
    check("card_root_partition", Counter(row["action_root"] for row in cards) == Counter({"CH": 4, "OK": 1}))

    expected_targets: dict[str, str] = {}
    expected_roundtrips: dict[str, str] = {}
    expected_slots: dict[str, str] = {}
    expected_class: dict[str, str] = {}
    expected_card_by_event: dict[str, str] = {}
    expected_topology_core: list[tuple[object, ...]] = []
    expected_assignment_core: list[tuple[object, ...]] = []
    expected_changed_ids: list[str] = []
    profile_counts: Counter[tuple[str, str]] = Counter()
    repeated_count = adjacent_count = interrupted_count = 0
    root_counts: Counter[str] = Counter()
    card_counts: Counter[str] = Counter()
    card_new: Counter[str] = Counter()
    card_old: Counter[str] = Counter()

    for source in source_events:
        event_id = source["event_id"]
        clause = source["pronoun_voice_working_clause_de"]
        tokens = source["final_context_recipe"].split("+")
        action_sequence = [token for token in tokens if token in ACTIONS]
        counts = Counter(action_sequence)
        repeated_roots = list(dict.fromkeys(root for root in action_sequence if counts[root] > 1))
        adjacent = [(index, tokens[index]) for index in range(len(tokens) - 1) if tokens[index] in ACTIONS and tokens[index + 1] == tokens[index]]
        if not repeated_roots:
            expected_targets[event_id] = clause
            expected_roundtrips[event_id] = clause
            expected_slots[event_id] = clause
            expected_class[event_id] = "NO_REPEATED_ACTION_ROOT"
            expected_card_by_event[event_id] = "NOT_APPLICABLE"
            continue
        repeated_count += 1
        classification = "ADJACENT_IDENTICAL_PAIR_COUNTABLE" if adjacent else "INTERRUPTED_OR_NONADJACENT_REPEAT_ORDER_EXPLICIT"
        profile_counts[("+".join(action_sequence), classification)] += 1
        if not adjacent:
            interrupted_count += 1
            target = roundtrip = slot_expansion = clause
            card_id = "NOT_APPLICABLE"
            positions = "NONE"
            changed = False
        else:
            if len(adjacent) != 1:
                raise RuntimeError(f"Independent multiple adjacency at {event_id}")
            adjacent_count += 1
            raw_index, root = adjacent[0]
            root_counts[root] += 1
            card_id = expected_card(source, root, clause)
            parsed = independent_transform(clause, card_id)
            target = str(parsed["target"])
            roundtrip = target[: int(parsed["target_start"])] + str(parsed["source_pair"]) + target[int(parsed["target_end"]) :]
            slot_expansion = target[: int(parsed["target_start"])] + str(parsed["expanded_pair"]) + target[int(parsed["target_end"]) :]
            changed = target != clause
            positions = f"{raw_index + 1}|{raw_index + 2}"
            card_counts[card_id] += 1
            (card_new if changed else card_old)[card_id] += 1
            expected_assignment_core.append((
                event_id, "+".join(action_sequence), root, positions, card_id,
                "NEWLY_COMPRESSED" if changed else "RETAINED_EXISTING_ZWEIMAL",
                int(parsed["source_start"]), int(parsed["source_end"]), int(parsed["target_start"]), int(parsed["target_end"]),
                str(parsed["source_pair"]), str(parsed["target_pair"]), str(parsed["expanded_pair"]), 2,
            ))
            if changed:
                expected_changed_ids.append(event_id)
        expected_targets[event_id] = target
        expected_roundtrips[event_id] = roundtrip
        expected_slots[event_id] = slot_expansion
        expected_class[event_id] = classification
        expected_card_by_event[event_id] = card_id
        expected_topology_core.append((
            event_id, "+".join(action_sequence), "|".join(repeated_roots),
            "|".join(f"{root}:{counts[root]}" for root in repeated_roots), len(adjacent), positions,
            classification, card_id, "YES" if changed else "NO", clause, target,
        ))

    check("repeated_event_total", repeated_count == 105, repeated_count)
    check("adjacent_event_total", adjacent_count == 43, adjacent_count)
    check("interrupted_event_total", interrupted_count == 62, interrupted_count)
    check("profile_total", len(profile_counts) == 28, len(profile_counts))
    check("adjacent_root_partition", root_counts == Counter({"CH": 42, "OK": 1}), dict(root_counts))
    check("change_partition", len(expected_changed_ids) == 36 and sum(card_old.values()) == 7, [len(expected_changed_ids), sum(card_old.values())])
    check("five_cards_used", set(card_counts) == set(expected_card_ids), dict(card_counts))

    actual_topology_core = [(
        row["event_id"], row["action_sequence"], row["repeated_action_roots"], row["repeated_action_root_counts"],
        int(row["raw_adjacent_pair_count"]), row["raw_action_atom_positions"], row["classification"], row["count_card_id"],
        row["count_voice_changed"], row["before_clause_de"], row["after_clause_de"],
    ) for row in topology_events]
    check("all_105_topology_events_exact", actual_topology_core == expected_topology_core)
    actual_assignment_core = [(
        row["event_id"], row["action_sequence"], row["repeated_action_root"], row["raw_action_atom_positions"], row["count_card_id"], row["source_status"],
        int(row["source_start_char"]), int(row["source_end_char"]), int(row["target_start_char"]), int(row["target_end_char"]),
        row["source_action_pair_fragment_de"], row["count_fragment_de"], row["full_two_slot_expansion_fragment_de"], int(row["action_slot_count_retained"]),
    ) for row in assignments]
    check("all_43_assignments_exact", actual_assignment_core == expected_assignment_core)
    check("all_assignment_slots_two", all(row["action_slot_count_retained"] == "2" for row in assignments))
    check("all_count_fragments_once", all(row["count_fragment_de"].count("zweimal") == 1 for row in assignments))

    source_by_id = {row["event_id"]: row for row in source_events}
    event_errors: list[str] = []
    for row in events:
        source = source_by_id[row["event_id"]]
        if (
            row["gdt573_pronoun_voice_clause_de"] != source["pronoun_voice_working_clause_de"]
            or row["action_count_working_clause_de"] != expected_targets[row["event_id"]]
            or row["gdt573_source_roundtrip_de"] != expected_roundtrips[row["event_id"]]
            or row["full_two_action_slot_expansion_de"] != expected_slots[row["event_id"]]
            or row["repeated_action_classification"] != expected_class[row["event_id"]]
            or row["count_card_id"] != expected_card_by_event[row["event_id"]]
        ):
            event_errors.append(row["event_id"])
    check("all_5122_events_exact", not event_errors, event_errors[:10])
    check("event_order_exact", [row["event_id"] for row in events] == [row["event_id"] for row in source_events])
    check("all_5122_source_roundtrips", all(row["gdt573_source_roundtrip_de"] == row["gdt573_pronoun_voice_clause_de"] for row in events))
    check("changed_ids_exact", [row["event_id"] for row in changes] == expected_changed_ids)
    check("changed_text_exact", all(row["before_clause_de"] == source_by_id[row["event_id"]]["pronoun_voice_working_clause_de"] and row["after_clause_de"] == expected_targets[row["event_id"]] and row["gdt573_source_roundtrip_de"] == row["before_clause_de"] for row in changes))
    check("only_nonstate_changed", Counter(source_by_id[event_id]["state_status"] for event_id in expected_changed_ids) == Counter({"NONSTATE_CARD": 36}))
    check("twice_total_43", sum(int(row["zweimal_occurrence_count"]) for row in events) == 43)
    check("interrupted_62_byte_exact", sum(row["repeated_action_classification"] == "INTERRUPTED_OR_NONADJACENT_REPEAT_ORDER_EXPLICIT" and row["gdt573_pronoun_voice_clause_de"] == row["action_count_working_clause_de"] for row in events) == 62)
    head_by_card = {"GDT574-C01": "entnimm", "GDT574-C02": "nimm", "GDT574-C03": "nimm", "GDT574-C04": "nimm", "GDT574-C05": "setze"}
    check("all_43_slot_expansions_have_two_heads", all(row["full_two_slot_expansion_fragment_de"].lower().count(head_by_card[row["count_card_id"]]) == 2 for row in assignments))

    profile_actual = {(row["action_sequence"], row["classification"]): int(row["event_count"]) for row in profiles}
    check("all_28_profiles_exact", profile_actual == dict(profile_counts))
    card_by_id = {row["count_card_id"]: row for row in cards}
    check("card_event_counts_exact", all(int(card_by_id[card_id]["eligible_event_count"]) == count for card_id, count in card_counts.items()))
    check("card_new_counts_exact", all(int(card_by_id[card_id]["newly_compressed_event_count"]) == card_new[card_id] for card_id in expected_card_ids))
    check("card_old_counts_exact", all(int(card_by_id[card_id]["retained_existing_twice_event_count"]) == card_old[card_id] for card_id in expected_card_ids))

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    statement_errors: list[str] = []
    changed_statement_ids: set[str] = set()
    eligible_statement_ids: set[str] = set()
    for row in statements:
        source = source_statement_by_id[row["statement_id"]]
        local = events_by_statement[row["statement_id"]]
        before = " ".join(item["gdt573_pronoun_voice_clause_de"] for item in local)
        after = " ".join(item["action_count_working_clause_de"] for item in local)
        roundtrip = " ".join(item["gdt573_source_roundtrip_de"] for item in local)
        changed_count = sum(item["action_count_changed"] == "YES" for item in local)
        eligible_count = sum(item["repeated_action_classification"] == "ADJACENT_IDENTICAL_PAIR_COUNTABLE" for item in local)
        if changed_count:
            changed_statement_ids.add(row["statement_id"])
        if eligible_count:
            eligible_statement_ids.add(row["statement_id"])
        if before != source["pronoun_voice_working_reading_de"] or row["gdt573_pronoun_voice_reading_de"] != before or row["action_count_working_reading_de"] != after or row["gdt573_source_roundtrip_de"] != roundtrip or roundtrip != before or int(row["changed_event_count"]) != changed_count or int(row["eligible_adjacent_pair_event_count"]) != eligible_count:
            statement_errors.append(row["statement_id"])
    check("all_793_statements_exact", not statement_errors, statement_errors[:10])
    check("statement_order_exact", [row["statement_id"] for row in statements] == [row["statement_id"] for row in source_statements])
    check("statement_partition", (len(changed_statement_ids), len(eligible_statement_ids)) == (33, 40), [len(changed_statement_ids), len(eligible_statement_ids)])

    changed_pages = {source_by_id[event_id]["physical_page"] for event_id in expected_changed_ids}
    eligible_pages = {source_by_id[row["event_id"]]["physical_page"] for row in assignments}
    check("page_order_exact", [row["physical_page"] for row in pages] == [row["physical_page"] for row in source_pages])
    check("page_partition", (len(changed_pages), len(eligible_pages)) == (17, 18), [len(changed_pages), len(eligible_pages)])
    check("page_twice_total", sum(int(row["zweimal_occurrence_count"]) for row in pages) == 43)
    check("zero_running_pages_retained", {row["physical_page"] for row in pages if int(row["event_count"]) == 0} == {"f69v", "f70v"})

    expected_metrics = {
        "repeated_action_event_count": 105,
        "repeated_action_sequence_profile_count": 28,
        "raw_adjacent_identical_pair_event_count": 43,
        "interrupted_or_nonadjacent_repeat_event_count": 62,
        "action_count_card_count": 5,
        "adjacent_ch_pair_count": 42,
        "adjacent_ok_pair_count": 1,
        "newly_compressed_event_count": 36,
        "retained_existing_twice_event_count": 7,
        "complete_twice_occurrence_count": 43,
        "unchanged_event_count": 5086,
        "changed_state_event_count": 0,
        "changed_nonstate_event_count": 36,
        "changed_statement_count": 33,
        "eligible_statement_count": 40,
        "changed_physical_page_count": 17,
        "eligible_physical_page_count": 18,
        "exact_gdt573_event_roundtrip_count": 5122,
        "two_action_slot_expansion_count": 43,
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
    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_metrics_exact", result.get("metrics") == expected_metrics, result.get("metrics"))
    check("input_hashes_exact", result.get("input_sha256") == {name: sha256(path) for name, path in INPUTS.items()})
    book = ARTIFACTS["book"].read_text(encoding="utf-8")
    check("book_metrics_present", "repeated-action events: 105 · adjacent counted pairs: 43 · newly changed clauses: 36 · interrupted repeats retained: 62" in book)
    check("book_all_pages_once", all(book.count(f"## {row['physical_page']}\n") == 1 for row in pages))
    check("book_all_statements", sum(line[:1].isdigit() and ". " in line for line in book.splitlines()) == 793)

    pre_hashes = {name: sha256(path) for name, path in ARTIFACTS.items() if name != "result"}
    run = subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
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
    (OUT / "gdt574_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
