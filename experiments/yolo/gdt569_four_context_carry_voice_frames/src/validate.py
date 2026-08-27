#!/usr/bin/env python3
"""Independent validation for GDT569's four context-carry frames."""

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
BASE = ROOT / "experiments/yolo/gdt569_four_context_carry_voice_frames"
OUT = BASE / "artifacts"
G568 = ROOT / "experiments/yolo/gdt568_twenty_owner_action_voice_frames/artifacts"
G567 = ROOT / "experiments/yolo/gdt567_owner_voice_seam_adapter/artifacts"
G566 = ROOT / "experiments/yolo/gdt566_complete_thirty_page_prose_working_edition/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
G562 = ROOT / "experiments/yolo/gdt562_thirty_page_actionless_state_role_reader/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
INPUTS = {
    "action_events": G568 / "gdt568_5122_action_voice_event_edition.tsv",
    "action_statements": G568 / "gdt568_793_action_voice_statement_edition.tsv",
    "page_profiles": G566 / "gdt566_30_page_edition_profiles.tsv",
    "state_replay": G565 / "gdt565_1656_template_replay.tsv",
    "argument_cards": G567 / "gdt567_39_owner_voice_adapter_cards.tsv",
    "action_provenance": G562 / "gdt562_693_action_provenance.tsv",
    "old_context": G416 / "gdt416_4576_imperative_clauses.tsv",
    "current_context": G539 / "gdt539_546_contextual_prose_events.tsv",
}
ARTIFACTS = {
    "modes": OUT / "gdt569_4_context_carry_cards.tsv",
    "scopes": OUT / "gdt569_3_action_scope_frames.tsv",
    "argument_forms": OUT / "gdt569_19_carried_argument_forms.tsv",
    "action_carries": OUT / "gdt569_693_action_carry_provenance.tsv",
    "argument_carries": OUT / "gdt569_1208_argument_carry_provenance.tsv",
    "states": OUT / "gdt569_1656_context_voice_state_clauses.tsv",
    "events": OUT / "gdt569_5122_context_voice_event_edition.tsv",
    "statements": OUT / "gdt569_793_context_voice_statement_edition.tsv",
    "pages": OUT / "gdt569_30_page_context_voice_profiles.tsv",
    "book": OUT / "GDT569_CONTEXT_VOICE_THIRTY_PAGE_EDITION.md",
    "result": OUT / "gdt569_result.json",
}
EXPECTED_STATUS = (
    "PASS_4_CONTEXT_MODES__693_ACTION_CARRIES__1208_ARGUMENT_CARRIES__"
    "1348_PRIOR_ARGUMENT_REALIZATIONS__1442_STATE_CLAUSES_CONTEXT_EXPLICIT__"
    "19_CARRIED_ARGUMENT_CELLS__ZERO_ROOT_CHANGE"
)
EXPECTED_MODES = {
    (False, False): ("GDT569-C01", "LOCAL_EXPLICIT", 214),
    (False, True): ("GDT569-C02", "ARGUMENT_CARRY", 749),
    (True, False): ("GDT569-C03", "ACTION_CARRY", 234),
    (True, True): ("GDT569-C04", "ACTION_AND_ARGUMENT_CARRY", 459),
}
EXPECTED_SCOPES = {
    "WEITER": ("GDT569-S01", 339),
    "DANACH": ("GDT569-S02", 316),
    "BARE": ("GDT569-S03", 38),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def roots(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("|")


def prior_form(phrase: str) -> str:
    if phrase.startswith("die beiden "):
        return "dieselben beiden " + phrase[len("die beiden "):]
    if phrase.startswith("den "):
        return "denselben " + phrase[len("den "):]
    if phrase.startswith("die "):
        return "dieselbe " + phrase[len("die "):]
    raise RuntimeError(f"Unexpected argument phrase {phrase!r}")


def join_arguments(parts: list[str]) -> str:
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " und " + parts[-1]


def replace_case_insensitive(text: str, old: str, new: str) -> str:
    match = re.search(re.escape(old), text, re.IGNORECASE)
    if match is None:
        raise RuntimeError(f"Missing chain {old!r}")
    replacement = new[0].upper() + new[1:] if match.group()[0].isupper() else new
    return text[:match.start()] + replacement + text[match.end():]


def scope_transform(text: str) -> tuple[str, str, str]:
    if text.startswith("Weiter: "):
        return "WEITER", "GDT569-S01", "Weiter im laufenden Gang: " + text[len("Weiter: "):]
    if text.startswith("Danach: "):
        return "DANACH", "GDT569-S02", "Danach im laufenden Gang: " + text[len("Danach: "):]
    return "BARE", "GDT569-S03", "Im laufenden Gang: " + text


def context_witness(text: str) -> bool:
    lower = text.lower()
    return any(
        phrase in lower
        for phrase in (
            "im laufenden gang", "im laufenden satz", "führe fort",
            "führe 2-mal fort", "schließe den schritt",
        )
    )


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    source_events = read_tsv(INPUTS["action_events"])
    source_statements = read_tsv(INPUTS["action_statements"])
    source_pages = read_tsv(INPUTS["page_profiles"])
    state_source = read_tsv(INPUTS["state_replay"])
    adapter_cards = read_tsv(INPUTS["argument_cards"])
    source_action_prov = read_tsv(INPUTS["action_provenance"])
    old_context = read_tsv(INPUTS["old_context"])
    current_context = read_tsv(INPUTS["current_context"])
    modes = read_tsv(ARTIFACTS["modes"])
    scopes = read_tsv(ARTIFACTS["scopes"])
    argument_forms = read_tsv(ARTIFACTS["argument_forms"])
    action_carries = read_tsv(ARTIFACTS["action_carries"])
    argument_carries = read_tsv(ARTIFACTS["argument_carries"])
    states = read_tsv(ARTIFACTS["states"])
    events = read_tsv(ARTIFACTS["events"])
    statements = read_tsv(ARTIFACTS["statements"])
    pages = read_tsv(ARTIFACTS["pages"])
    result = json.loads(ARTIFACTS["result"].read_text(encoding="utf-8"))

    check("input_counts", [len(source_events), len(source_statements), len(source_pages), len(state_source), len(adapter_cards), len(source_action_prov), len(old_context), len(current_context)] == [5122, 793, 30, 1656, 39, 693, 4576, 546])
    check("artifact_counts", [len(modes), len(scopes), len(argument_forms), len(action_carries), len(argument_carries), len(states), len(events), len(statements), len(pages)] == [4, 3, 19, 693, 1208, 1656, 5122, 793, 30])
    all_pages = {row["physical_page"] for row in events} | {row["physical_page"] for row in states}
    check("sealed_pages_absent", not any(page.startswith("f84") for page in all_pages), sorted(page for page in all_pages if page.startswith("f84")))
    check("event_ordinals", [int(row["edition_event_ordinal"]) for row in events] == list(range(1, 5123)))
    check("state_ordinals", [int(row["state_edition_ordinal"]) for row in states] == list(range(1, 1657)))
    check("statement_ordinals", [int(row["edition_statement_ordinal"]) for row in statements] == list(range(1, 794)))
    check("page_ordinals", [int(row["page_ordinal"]) for row in pages] == list(range(1, 31)))

    source_event_by_id = {row["event_id"]: row for row in source_events}
    source_state_by_id = {row["event_id"]: row for row in state_source}
    state_by_id = {row["event_id"]: row for row in states}
    check("event_keys_unique", len(source_event_by_id) == len(source_events) == len({row["event_id"] for row in events}))
    check("state_keys_unique", len(state_by_id) == len(states) == len(source_state_by_id))
    check("state_partition_exact", set(state_by_id) == {row["event_id"] for row in source_events if row["state_status"] == "STATE_CARD"})

    metadata = {row["global_running_event_id"]: row for row in old_context}
    metadata.update({row["event_id"]: row for row in current_context})
    action_prov_by_id = {row["event_id"]: row for row in source_action_prov}
    expected_action_ids = {eid for eid in source_state_by_id if metadata[eid]["inherited_action_root"] not in ("", "NONE")}
    expected_argument_ids = {eid for eid in source_state_by_id if metadata[eid]["inherited_argument_root"] not in ("", "NONE")}
    check("action_carry_ids_exact", set(action_prov_by_id) == expected_action_ids == {row["event_id"] for row in action_carries})
    check("argument_carry_ids_exact", expected_argument_ids == {row["event_id"] for row in argument_carries})
    check("carry_id_counts", [len(expected_action_ids), len(expected_argument_ids)] == [693, 1208])

    arg_cards = [row for row in adapter_cards if row["card_class"] == "ARGUMENT_OWNER_VOICE"]
    arg_by_cell = {(row["register_scope"], row["root_or_trigger"]): row for row in arg_cards}
    check("nineteen_argument_source_cards", len(arg_cards) == len(arg_by_cell) == 19)

    def argument_phrase(state: dict[str, str], carry: bool) -> str:
        values = roots(state["effective_argument_roots"])
        if not values:
            return ""
        register = state["register"]
        if values == ["Y", "Y"]:
            base = arg_by_cell[(register, "Y")]["double_y_phrase_de"]
            return prior_form(base) if carry else base
        pieces = [arg_by_cell[(register, root)]["owner_voice_phrase_de"] for root in values]
        if carry:
            pieces = [prior_form(piece) for piece in pieces]
        return join_arguments(pieces)

    mode_counter = Counter()
    state_errors = []
    carry_realization_total = 0
    marker_event_total = 0
    marker_occurrence_total = 0
    action_witness_total = 0
    for eid, output in state_by_id.items():
        source = source_event_by_id[eid]
        state = source_state_by_id[eid]
        meta = metadata[eid]
        action_carry = meta["inherited_action_root"] not in ("", "NONE")
        argument_carry = meta["inherited_argument_root"] not in ("", "NONE")
        card_id, mode, _ = EXPECTED_MODES[(action_carry, argument_carry)]
        mode_counter[mode] += 1
        before = source["action_voice_working_clause_de"]
        expected = before
        explicit_argument = argument_phrase(state, False)
        expected_prior = argument_phrase(state, True) if argument_carry else "NOT_APPLICABLE"
        expected_chain = source["owner_action_chain_de"]
        expected_realizations = 0
        if argument_carry:
            expected_realizations = expected_chain.count(explicit_argument)
            expected_chain = expected_chain.replace(explicit_argument, expected_prior)
            expected = replace_case_insensitive(expected, source["owner_action_chain_de"], expected_chain)
        expected_scope_kind = expected_scope_id = "NOT_APPLICABLE"
        if action_carry:
            expected_scope_kind, expected_scope_id, expected = scope_transform(expected)
        marker_count = source["owner_bound_control_clause_de"].count("[wie zuvor]")
        witness = context_witness(source["owner_bound_control_clause_de"])
        carry_realization_total += expected_realizations
        marker_event_total += marker_count > 0
        marker_occurrence_total += marker_count
        action_witness_total += action_carry and witness
        conditions = [
            output["context_mode_card_id"] == card_id,
            output["context_mode"] == mode,
            output["action_carry"] == ("YES" if action_carry else "NO"),
            output["argument_carry"] == ("YES" if argument_carry else "NO"),
            output["explicit_argument_phrase_de"] == (explicit_argument or "NONE"),
            output["carried_argument_phrase_de"] == expected_prior,
            int(output["carried_argument_realization_count"]) == expected_realizations,
            output["control_prior_marker_count"] == str(marker_count),
            output["context_voice_action_chain_de"] == expected_chain,
            output["action_scope_kind"] == expected_scope_kind,
            output["action_scope_frame_id"] == expected_scope_id,
            output["context_voice_working_clause_de"] == expected,
            output["context_voice_changed"] == ("YES" if mode != "LOCAL_EXPLICIT" else "NO"),
            output["final_context_recipe"] == source["final_context_recipe"],
            output["state_atom_alignment"] == source["state_atom_alignment"],
        ]
        if not all(conditions):
            state_errors.append(eid)
    check("all_state_transformations_exact", not state_errors, state_errors[:20])
    check("four_mode_counts_exact", mode_counter == Counter({"LOCAL_EXPLICIT": 214, "ARGUMENT_CARRY": 749, "ACTION_CARRY": 234, "ACTION_AND_ARGUMENT_CARRY": 459}), dict(mode_counter))
    check("argument_realization_total", carry_realization_total == 1348, carry_realization_total)
    check("control_marker_totals", [marker_event_total, marker_occurrence_total] == [1208, 1354], [marker_event_total, marker_occurrence_total])
    check("control_action_witness_total", action_witness_total == 693, action_witness_total)

    expected_mode_rows = {(row["context_mode_card_id"], row["context_mode"]): int(row["state_event_count"]) for row in modes}
    check(
        "mode_cards_exact",
        expected_mode_rows == {(v[0], v[1]): v[2] for v in EXPECTED_MODES.values()},
        {"|".join(key): value for key, value in expected_mode_rows.items()},
    )
    check("mode_card_guards", all(row["guard"] == "FOUR_WAY_CONTEXT_MODE__NO_NEW_WRITTEN_ATOM" for row in modes))
    scope_counts = {row["action_scope_kind"]: (row["action_scope_frame_id"], int(row["action_carry_event_count"])) for row in scopes}
    check("scope_frames_exact", scope_counts == {key: value for key, value in EXPECTED_SCOPES.items()}, scope_counts)
    check("scope_source_partition", sum(int(row["same_statement_visible_action_count"]) for row in scopes) == 544 and sum(int(row["owner_context_default_action_count"]) for row in scopes) == 149)
    check("scope_control_witnesses", all(row["action_carry_event_count"] == row["control_context_witness_count"] for row in scopes))

    expected_cells = {(row["register_scope"], row["root_or_trigger"]) for row in arg_cards}
    output_cells = {(row["register"], row["argument_root"]) for row in argument_forms}
    check("carried_argument_cells_exact", output_cells == expected_cells and len(output_cells) == 19)
    form_errors = []
    for row in argument_forms:
        card = arg_by_cell[(row["register"], row["argument_root"])]
        if row["explicit_argument_phrase_de"] != card["owner_voice_phrase_de"] or row["carried_argument_phrase_de"] != prior_form(card["owner_voice_phrase_de"]):
            form_errors.append(row["carried_argument_card_id"])
    check("carried_argument_forms_exact", not form_errors, form_errors)
    check("all_argument_cells_used", all(int(row["argument_carry_event_count"]) > 0 for row in argument_forms))
    check("argument_form_totals", sum(int(row["argument_carry_event_count"]) for row in argument_forms) == 1208 and sum(int(row["carried_argument_realization_count"]) for row in argument_forms) == 1348)
    check("argument_control_support", all(row["argument_carry_event_count"] == row["control_prior_marker_event_count"] for row in argument_forms))

    source_action_by_id = {row["event_id"]: row for row in source_action_prov}
    action_errors = []
    for row in action_carries:
        src = source_action_by_id[row["event_id"]]
        for key in ("inherited_action_root", "inherited_action_value_de", "action_source_type", "action_source_event_id", "source_card_distance"):
            if row[key] != src[key]:
                action_errors.append((row["event_id"], key))
    check("action_provenance_byte_exact", not action_errors, action_errors[:20])
    check("action_source_counts", Counter(row["action_source_type"] for row in action_carries) == Counter({"SAME_STATEMENT_VISIBLE_ACTION": 544, "OWNER_CONTEXT_DEFAULT_ACTION": 149}))
    check("all_action_controls_witnessed", all(row["control_action_context_witness"] == "YES" for row in action_carries))
    check("all_argument_controls_witnessed", all(int(row["control_prior_marker_count"]) > 0 for row in argument_carries))

    event_errors = []
    for source, output in zip(source_events, events):
        if [source[key] for key in ("event_id", "statement_id", "physical_page", "surface", "final_context_recipe", "state_status")] != [output[key] for key in ("event_id", "statement_id", "physical_page", "surface", "final_context_recipe", "state_status")]:
            event_errors.append(source["event_id"])
            continue
        state = state_by_id.get(source["event_id"])
        expected = state["context_voice_working_clause_de"] if state else source["action_voice_working_clause_de"]
        if output["context_voice_working_clause_de"] != expected:
            event_errors.append(source["event_id"])
    check("all_5122_events_reconstructed", not event_errors, event_errors[:20])
    nonstates = [row for row in events if row["state_status"] == "NONSTATE_CARD"]
    check("nonstate_byte_unchanged", len(nonstates) == 3466 and all(row["gdt568_action_voice_clause_de"] == row["context_voice_working_clause_de"] for row in nonstates))
    check("state_change_partition", Counter(row["context_voice_changed"] for row in states) == Counter({"YES": 1442, "NO": 214}))

    event_by_id = {row["event_id"]: row for row in events}
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    statement_errors = []
    for output in statements:
        source = source_statement_by_id[output["statement_id"]]
        members = [event_by_id[eid] for eid in output["event_ids"].split("|")]
        before = " ".join(row["gdt568_action_voice_clause_de"] for row in members)
        after = " ".join(row["context_voice_working_clause_de"] for row in members)
        control = " ".join(row["owner_bound_control_clause_de"] for row in members)
        if before != source["action_voice_working_reading_de"] or after != output["context_voice_working_reading_de"] or control != source["owner_bound_control_reading_de"]:
            statement_errors.append(output["statement_id"])
    check("all_793_statements_reconstructed", not statement_errors, statement_errors[:20])
    check("statement_change_partition", Counter(row["context_voice_statement_changed"] for row in statements) == Counter({"YES": 711, "NO": 82}))
    check("statement_event_order_exact", all(row["event_ids"] == source_statement_by_id[row["statement_id"]]["event_ids"] for row in statements))

    check("page_order_exact", [row["physical_page"] for row in pages] == [row["physical_page"] for row in source_pages])
    check("page_count_parity", all(int(row["event_count"]) == int(source_pages[i]["edition_event_count"]) and int(row["statement_count"]) == int(source_pages[i]["edition_statement_count"]) for i, row in enumerate(pages)))
    check("changed_page_count", sum(int(row["context_changed_state_event_count"]) > 0 for row in pages) == 28)
    check("zero_running_pages_retained", [row["physical_page"] for row in pages if int(row["event_count"]) == 0] == ["f69v", "f70v"])

    expected_metrics = {
        "context_mode_card_count": 4,
        "local_explicit_state_event_count": 214,
        "argument_only_carry_event_count": 749,
        "action_only_carry_event_count": 234,
        "action_and_argument_carry_event_count": 459,
        "action_carry_event_count": 693,
        "same_statement_visible_action_carry_count": 544,
        "owner_context_default_action_carry_count": 149,
        "action_scope_frame_count": 3,
        "argument_carry_event_count": 1208,
        "carried_argument_cell_count": 19,
        "carried_argument_realization_count": 1348,
        "control_prior_marker_event_count": 1208,
        "control_prior_marker_occurrence_count": 1354,
        "control_action_context_witness_count": 693,
        "changed_state_event_count": 1442,
        "unchanged_state_event_count": 214,
        "changed_statement_count": 711,
        "unchanged_statement_count": 82,
        "changed_physical_page_count": 28,
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
    check("result_status_exact", result.get("status") == EXPECTED_STATUS, result.get("status"))
    input_hashes = {name: sha256(path) for name, path in INPUTS.items()}
    check("input_hashes_exact", result.get("input_sha256") == input_hashes)
    check("book_metrics_present", all(text in ARTIFACTS["book"].read_text(encoding="utf-8") for text in ("214 lokal explizit", "693 Handlungsträger", "1.208 Argumentträger", "1.442 angepasste Zustandszeilen")))
    check("book_all_pages_once", all(ARTIFACTS["book"].read_text(encoding="utf-8").count(f"## {row['physical_page']}\n") == 1 for row in pages))
    check("book_all_statements", sum(1 for line in ARTIFACTS["book"].read_text(encoding="utf-8").splitlines() if line.startswith("### G")) == 793)

    before_hashes = {name: sha256(path) for name, path in ARTIFACTS.items()}
    replay = subprocess.run(
        ["python3", str(BASE / "src/run.py")], cwd=ROOT, capture_output=True, text=True, check=False
    )
    after_hashes = {name: sha256(path) for name, path in ARTIFACTS.items()}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr[-1000:])
    check("deterministic_artifact_hashes", before_hashes == after_hashes, {key: (before_hashes[key], after_hashes[key]) for key in before_hashes if before_hashes[key] != after_hashes[key]})

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
    (OUT / "gdt569_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
