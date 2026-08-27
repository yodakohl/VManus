#!/usr/bin/env python3
"""Naturalize every bracketed audit marker in the complete nonstate edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
BRACKET_RE = re.compile(r"\[[^\]]+\]")
BRACKET_ORDER = ("[wie zuvor]", "[außen]", "[innen]", "[Stufe 3]")
REGISTER_ORDER = ("SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA")
ROOT_ORDER = ("Y", "AIIN", "AIN", "OR")
STATUS = (
    "PASS_4_BRACKET_TYPES__1536_OCCURRENCES__20_CARRY_FORMS__5_SCOPE_CARDS__"
    "1156_NONSTATE_CLAUSES_NATURALIZED__ZERO_BRACKETS__ZERO_ROOT_CHANGE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nominal_scope(phrase: str, outer: bool) -> str:
    article, noun = phrase.split(" ", 1)
    forms = {
        ("den", True): "äußeren",
        ("den", False): "inneren",
        ("die", True): "äußere",
        ("die", False): "innere",
    }
    if (article, outer) not in forms:
        raise RuntimeError(f"Unsupported argument article in {phrase}")
    return f"{article} {forms[(article, outer)]} {noun}"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["outer_events"])
    source_statements = read_tsv(INPUTS["outer_statements"])
    source_pages = read_tsv(INPUTS["page_profiles"])
    old_forms = read_tsv(INPUTS["state_carry_forms"])
    old_context = read_tsv(INPUTS["old_context"])
    current_context = read_tsv(INPUTS["current_context"])
    counts = [len(source_events), len(source_statements), len(source_pages), len(old_forms), len(old_context), len(current_context)]
    if counts != [5122, 793, 30, 19, 4576, 546]:
        raise RuntimeError(f"Input count drift: {counts}")

    context_by_id: dict[str, dict[str, str]] = {}
    for row in old_context:
        event_id = row["global_running_event_id"]
        context_by_id[event_id] = {
            "source_layer": "GDT416_OLD26",
            "inherited_argument_root": row["inherited_argument_root"],
            "inherited_argument_source_event_id": "OWNER_CONTEXT_STATE",
        }
    for row in current_context:
        event_id = row["event_id"]
        if event_id in context_by_id:
            raise RuntimeError(f"Context overlap at {event_id}")
        context_by_id[event_id] = {
            "source_layer": "GDT539_CURRENT4",
            "inherited_argument_root": row["inherited_argument_root"],
            "inherited_argument_source_event_id": row["inherited_argument_source_event_id"],
        }
    if len(context_by_id) != 5122 or set(context_by_id) != {row["event_id"] for row in source_events}:
        raise RuntimeError("Complete context provenance drift")

    form_seed: dict[tuple[str, str], dict[str, str]] = {}
    for row in old_forms:
        key = (row["register"], row["argument_root"])
        form_seed[key] = {
            "explicit": row["explicit_argument_phrase_de"],
            "carried": row["carried_argument_phrase_de"],
            "source_status": "REUSED_GDT569_STATE_CARRY_FORM",
            "source_card_id": row["carried_argument_card_id"],
        }
    new_key = ("CELESTIAL", "AIN")
    if new_key in form_seed:
        raise RuntimeError("Celestial AIN cell unexpectedly already present")
    form_seed[new_key] = {
        "explicit": "den Sektoranteil",
        "carried": "denselben Sektoranteil",
        "source_status": "NEWLY_OCCUPIED_NONSTATE_CARRY_CELL",
        "source_card_id": "NONE",
    }
    expected_keys = {(register, root) for register in REGISTER_ORDER for root in ROOT_ORDER}
    if set(form_seed) != expected_keys:
        raise RuntimeError(f"Twenty-cell inventory drift: {set(form_seed) ^ expected_keys}")

    ordered_keys = [(register, root) for register in REGISTER_ORDER for root in ROOT_ORDER]
    card_id_by_key = {key: f"GDT572-A{ordinal:02d}" for ordinal, key in enumerate(ordered_keys, 1)}
    form_by_register_phrase = {(register, values["explicit"]): (root, values) for (register, root), values in form_seed.items()}

    marker_counter: Counter[str] = Counter()
    marker_event_sets: dict[str, set[str]] = defaultdict(set)
    marker_page_sets: dict[str, set[str]] = defaultdict(set)
    marker_register_sets: dict[str, set[str]] = defaultdict(set)
    carry_occurrence_counts: Counter[tuple[str, str]] = Counter()
    carry_event_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    carry_page_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    scope_occurrence_counts: Counter[str] = Counter()
    scope_event_sets: dict[str, set[str]] = defaultdict(set)
    scope_page_sets: dict[str, set[str]] = defaultdict(set)
    scope_register_sets: dict[str, set[str]] = defaultdict(set)
    assignments: list[dict[str, object]] = []
    signature_counter: Counter[str] = Counter()
    signature_event_sets: dict[str, set[str]] = defaultdict(set)
    signature_page_sets: dict[str, set[str]] = defaultdict(set)
    signature_register_sets: dict[str, set[str]] = defaultdict(set)
    target_by_event: dict[str, str] = {}
    changed_rows: list[dict[str, object]] = []

    assignment_ordinal = 0
    for source in source_events:
        event_id = source["event_id"]
        current = source["outer_voice_working_clause_de"]
        markers = BRACKET_RE.findall(current)
        if markers:
            if source["state_status"] != "NONSTATE_CARD":
                raise RuntimeError(f"Bracket marker reached state card {event_id}")
            signature = "|".join(markers)
            signature_counter[signature] += 1
            signature_event_sets[signature].add(event_id)
            signature_page_sets[signature].add(source["physical_page"])
            signature_register_sets[signature].add(source["register"])
        context = context_by_id[event_id]
        register_forms = [(phrase, root, values) for (register, phrase), (root, values) in form_by_register_phrase.items() if register == source["register"]]
        register_forms.sort(key=lambda item: len(item[0]), reverse=True)

        for marker_ordinal, match in enumerate(BRACKET_RE.finditer(current), 1):
            marker = match.group()
            if marker not in BRACKET_ORDER:
                raise RuntimeError(f"Unknown bracket marker {marker} at {event_id}")
            prefix = current[: match.start()]
            matched_form: tuple[str, str, dict[str, str]] | None = None
            for phrase, root, values in register_forms:
                if prefix.endswith(phrase + " "):
                    matched_form = (phrase, root, values)
                    break

            if marker == "[wie zuvor]":
                if matched_form is None:
                    raise RuntimeError(f"Prior marker without owner argument form at {event_id}")
                phrase, root, values = matched_form
                if context["inherited_argument_root"] != root:
                    raise RuntimeError(f"Inherited-root mismatch at {event_id}: {context['inherited_argument_root']} vs {root}")
                card_id = card_id_by_key[(source["register"], root)]
                host_class = "INHERITED_ARGUMENT"
                source_fragment = phrase + " " + marker
                target_fragment = values["carried"]
                carry_occurrence_counts[(source["register"], root)] += 1
                carry_event_sets[(source["register"], root)].add(event_id)
                carry_page_sets[(source["register"], root)].add(source["physical_page"])
            elif marker in {"[außen]", "[innen]"} and matched_form is not None:
                phrase, root, _ = matched_form
                outer = marker == "[außen]"
                card_id = "GDT572-S01" if outer else "GDT572-S02"
                host_class = "NOMINAL_ARGUMENT_SCOPE"
                source_fragment = phrase + " " + marker
                target_fragment = nominal_scope(phrase, outer)
            elif marker in {"[außen]", "[innen]"}:
                outer = marker == "[außen]"
                card_id = "GDT572-S03" if outer else "GDT572-S04"
                host_class = "NON_NOMINAL_SCOPE"
                source_fragment = marker
                target_fragment = "im äußeren Zweig" if outer else "im inneren Zweig"
                root = "NOT_APPLICABLE"
                phrase = "NON_NOMINAL_HOST"
            elif marker == "[Stufe 3]" and matched_form is not None:
                phrase, root, _ = matched_form
                card_id = "GDT572-S05"
                host_class = "THIRD_LEVEL_ARGUMENT_SCOPE"
                source_fragment = marker
                target_fragment = "auf Stufe drei"
            else:
                raise RuntimeError(f"Third-level marker without argument form at {event_id}")

            assignment_ordinal += 1
            assignments.append({
                "assignment_ordinal": assignment_ordinal,
                "event_id": event_id,
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "surface": source["surface"],
                "final_context_recipe": source["final_context_recipe"],
                "bracket_ordinal_in_clause": marker_ordinal,
                "bracket_marker": marker,
                "host_class": host_class,
                "argument_root": root,
                "explicit_argument_phrase_de": phrase,
                "replacement_card_id": card_id,
                "source_fragment_de": source_fragment,
                "target_fragment_de": target_fragment,
                "context_source_layer": context["source_layer"],
                "inherited_argument_source_event_id": context["inherited_argument_source_event_id"] if marker == "[wie zuvor]" else "NOT_APPLICABLE",
                "guard": "BRACKET_VOICE_ONLY__ROOTS_RECIPE_AND_BOUNDARY_UNCHANGED",
            })
            marker_counter[marker] += 1
            marker_event_sets[marker].add(event_id)
            marker_page_sets[marker].add(source["physical_page"])
            marker_register_sets[marker].add(source["register"])
            if marker != "[wie zuvor]":
                scope_occurrence_counts[card_id] += 1
                scope_event_sets[card_id].add(event_id)
                scope_page_sets[card_id].add(source["physical_page"])
                scope_register_sets[card_id].add(source["register"])

        target = current
        for phrase, root, values in register_forms:
            target = target.replace(phrase + " [wie zuvor]", values["carried"])
            target = target.replace(phrase + " [außen]", nominal_scope(phrase, True))
            target = target.replace(phrase + " [innen]", nominal_scope(phrase, False))
            target = target.replace(phrase + " [Stufe 3]", phrase + " auf Stufe drei")
        target = target.replace("[außen]", "im äußeren Zweig")
        target = target.replace("[innen]", "im inneren Zweig")
        target = target.replace("[Stufe 3]", "auf Stufe drei")
        if BRACKET_RE.search(target):
            raise RuntimeError(f"Unresolved bracket marker at {event_id}: {target}")
        target_by_event[event_id] = target
        if target != current:
            changed_rows.append({
                "change_ordinal": len(changed_rows) + 1,
                "event_id": event_id,
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "surface": source["surface"],
                "final_context_recipe": source["final_context_recipe"],
                "bracket_signature": "|".join(markers),
                "bracket_occurrence_count": len(markers),
                "before_clause_de": current,
                "after_clause_de": target,
                "guard": "ALL_BRACKETS_NATURALIZED__SEMANTIC_ROOTS_UNCHANGED",
            })

    if marker_counter != Counter({"[wie zuvor]": 1292, "[außen]": 121, "[innen]": 121, "[Stufe 3]": 2}):
        raise RuntimeError(f"Bracket inventory drift: {marker_counter}")
    if len(assignments) != 1536 or len(changed_rows) != 1156 or len(signature_counter) != 11:
        raise RuntimeError("Bracket assignment/change/signature count drift")
    if sum(carry_occurrence_counts.values()) != 1292:
        raise RuntimeError("Carry occurrence drift")
    if scope_occurrence_counts != Counter({"GDT572-S01": 104, "GDT572-S02": 104, "GDT572-S03": 17, "GDT572-S04": 17, "GDT572-S05": 2}):
        raise RuntimeError(f"Scope card drift: {scope_occurrence_counts}")

    carry_rows: list[dict[str, object]] = []
    for ordinal, key in enumerate(ordered_keys, 1):
        register, root = key
        values = form_seed[key]
        carry_rows.append({
            "carry_card_ordinal": ordinal,
            "carry_card_id": card_id_by_key[key],
            "register": register,
            "argument_root": root,
            "explicit_argument_phrase_de": values["explicit"],
            "carried_argument_phrase_de": values["carried"],
            "nonstate_carry_event_count": len(carry_event_sets[key]),
            "nonstate_carry_occurrence_count": carry_occurrence_counts[key],
            "physical_page_count": len(carry_page_sets[key]),
            "source_status": values["source_status"],
            "source_card_id": values["source_card_id"],
            "guard": "ARTICLE_REALIZATION_OF_INHERITED_ARGUMENT__ROOT_UNCHANGED",
        })
    if any(int(row["nonstate_carry_occurrence_count"]) == 0 for row in carry_rows):
        raise RuntimeError("A carry card is unused")

    scope_specs = [
        ("GDT572-S01", "[außen]", "NOMINAL_ARGUMENT_SCOPE", "INFLECT_EXPLICIT_ARGUMENT_WITH_OUTER_ADJECTIVE", "äußere/äußerer Argumentform"),
        ("GDT572-S02", "[innen]", "NOMINAL_ARGUMENT_SCOPE", "INFLECT_EXPLICIT_ARGUMENT_WITH_INNER_ADJECTIVE", "innere/innerer Argumentform"),
        ("GDT572-S03", "[außen]", "NON_NOMINAL_SCOPE", "REPLACE_MARKER_AFTER_RELATION_OR_CONTROL_HOST", "im äußeren Zweig"),
        ("GDT572-S04", "[innen]", "NON_NOMINAL_SCOPE", "REPLACE_MARKER_AFTER_RELATION_OR_CONTROL_HOST", "im inneren Zweig"),
        ("GDT572-S05", "[Stufe 3]", "THIRD_LEVEL_ARGUMENT_SCOPE", "REPLACE_MARKER_AFTER_NOMINAL_HOST", "auf Stufe drei"),
    ]
    scope_rows = []
    for ordinal, (card_id, marker, host_class, rule, realization) in enumerate(scope_specs, 1):
        scope_rows.append({
            "scope_card_ordinal": ordinal,
            "scope_card_id": card_id,
            "bracket_marker": marker,
            "host_class": host_class,
            "render_rule": rule,
            "working_realization_de": realization,
            "occurrence_count": scope_occurrence_counts[card_id],
            "event_count": len(scope_event_sets[card_id]),
            "physical_page_count": len(scope_page_sets[card_id]),
            "register_count": len(scope_register_sets[card_id]),
            "guard": "SCOPE_VOICE_ONLY__NO_PORTABLE_ROOT_VALUE",
        })

    inventory_rows = []
    for ordinal, marker in enumerate(BRACKET_ORDER, 1):
        inventory_rows.append({
            "marker_ordinal": ordinal,
            "bracket_marker": marker,
            "occurrence_count": marker_counter[marker],
            "event_count": len(marker_event_sets[marker]),
            "physical_page_count": len(marker_page_sets[marker]),
            "register_count": len(marker_register_sets[marker]),
            "replacement_layer": "20_OWNER_ARGUMENT_CELLS" if marker == "[wie zuvor]" else "5_SCOPE_VOICE_CARDS",
            "remaining_occurrence_count": 0,
            "guard": "EXHAUSTIVE_CURRENT_NONSTATE_BRACKET_INVENTORY",
        })

    signature_rows = []
    signature_order = sorted(signature_counter, key=lambda key: (-signature_counter[key], key))
    for ordinal, signature in enumerate(signature_order, 1):
        signature_rows.append({
            "signature_ordinal": ordinal,
            "bracket_signature": signature,
            "marker_occurrence_count_per_event": len(signature.split("|")),
            "event_count": signature_counter[signature],
            "physical_page_count": len(signature_page_sets[signature]),
            "register_count": len(signature_register_sets[signature]),
            "example_event_ids": "|".join(sorted(signature_event_sets[signature])[:8]),
            "guard": "SIGNATURE_IS_EDITORIAL_PATTERN_NOT_WHOLE_CARD_MEANING",
        })

    changed_ids = {row["event_id"] for row in changed_rows}
    event_rows: list[dict[str, object]] = []
    unchanged_state_count = 0
    unchanged_nonstate_count = 0
    for ordinal, source in enumerate(source_events, 1):
        event_id = source["event_id"]
        target = target_by_event[event_id]
        changed = event_id in changed_ids
        if source["state_status"] != "NONSTATE_CARD":
            if changed or target != source["outer_voice_working_clause_de"]:
                raise RuntimeError(f"State clause changed at {event_id}")
            unchanged_state_count += 1
        elif not changed:
            unchanged_nonstate_count += 1
        event_rows.append({
            "edition_event_ordinal": ordinal,
            "event_id": event_id,
            "statement_id": source["statement_id"],
            "card_ordinal_in_statement": source["card_ordinal_in_statement"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "state_status": source["state_status"],
            "state_marker_sequence": source["state_marker_sequence"],
            "gdt571_outer_voice_clause_de": source["outer_voice_working_clause_de"],
            "bracket_free_working_clause_de": target,
            "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "bracket_voice_changed": "YES" if changed else "NO",
            "remaining_bracket_count": len(BRACKET_RE.findall(target)),
            "state_atom_alignment": source["state_atom_alignment"],
            "guard": "COMPLETE_EVENT_ORDER__STATE_TEXT_BYTE_UNCHANGED",
        })
    if unchanged_state_count != 1656 or unchanged_nonstate_count != 2310:
        raise RuntimeError("State/nonstate change partition drift")

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    changed_statement_ids: set[str] = set()
    for ordinal, source in enumerate(source_statements, 1):
        statement_id = source["statement_id"]
        local = events_by_statement[statement_id]
        current = " ".join(str(row["gdt571_outer_voice_clause_de"]) for row in local)
        target = " ".join(str(row["bracket_free_working_clause_de"]) for row in local)
        if current != source["outer_voice_working_reading_de"]:
            raise RuntimeError(f"Source statement reconstruction drift at {statement_id}")
        changed_count = sum(row["bracket_voice_changed"] == "YES" for row in local)
        if changed_count:
            changed_statement_ids.add(statement_id)
        statement_rows.append({
            "edition_statement_ordinal": ordinal,
            "statement_id": statement_id,
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "event_count": source["event_count"],
            "state_card_count": source["state_card_count"],
            "nonstate_card_count": source["nonstate_card_count"],
            "statement_mode": source["statement_mode"],
            "changed_nonstate_event_count": changed_count,
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "gdt571_outer_voice_reading_de": current,
            "bracket_free_working_reading_de": target,
            "owner_bound_control_reading_de": source["owner_bound_control_reading_de"],
            "bracket_voice_statement_changed": "YES" if changed_count else "NO",
            "end_mode": source["end_mode"],
            "remaining_bracket_count": len(BRACKET_RE.findall(target)),
            "guard": "STATEMENT_EVENT_ORDER_AND_BOUNDARIES_UNCHANGED",
        })

    page_events: dict[str, list[dict[str, object]]] = defaultdict(list)
    page_changed_statements: dict[str, set[str]] = defaultdict(set)
    for row in event_rows:
        page_events[str(row["physical_page"])].append(row)
        if row["bracket_voice_changed"] == "YES":
            page_changed_statements[str(row["physical_page"])].add(str(row["statement_id"]))
    page_rows: list[dict[str, object]] = []
    changed_pages: set[str] = set()
    for ordinal, source in enumerate(source_pages, 1):
        page = source["physical_page"]
        local = page_events.get(page, [])
        local_assignments = [row for row in assignments if row["physical_page"] == page]
        changed_count = sum(row["bracket_voice_changed"] == "YES" for row in local)
        if changed_count:
            changed_pages.add(page)
        page_rows.append({
            "page_ordinal": ordinal,
            "physical_page": page,
            "registers": source["registers"],
            "event_count": source["event_count"],
            "statement_count": source["statement_count"],
            "state_event_count": source["state_event_count"],
            "nonstate_event_count": int(source["event_count"]) - int(source["state_event_count"]),
            "bracket_occurrence_count": len(local_assignments),
            "changed_nonstate_event_count": changed_count,
            "changed_statement_count": len(page_changed_statements[page]),
            "remaining_bracket_count": 0,
            "page_status": source["page_status"],
            "guard": "ADMITTED_PAGE_ORDER_UNCHANGED",
        })

    book_lines = [
        "# GDT572 bracket-free thirty-page working edition",
        "",
        "Twenty owner-argument carry forms and five scope cards naturalize every current bracketed audit marker.",
        "All written recipes, roots, event order and statement boundaries are unchanged.",
        "",
        f"Events: {len(event_rows)} · statements: {len(statement_rows)} · pages: {len(page_rows)} · changed nonstate clauses: {len(changed_rows)} · remaining brackets: 0.",
        "",
    ]
    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    for page in page_rows:
        page_id = str(page["physical_page"])
        book_lines.extend([f"## {page_id}", ""])
        local = statements_by_page.get(page_id, [])
        if not local:
            book_lines.extend(["_No admitted running statements._", ""])
            continue
        for row in local:
            book_lines.extend([f"{row['edition_statement_ordinal']}. {row['bracket_free_working_reading_de']}", ""])
    (OUT / "GDT572_BRACKET_FREE_THIRTY_PAGE_EDITION.md").write_text("\n".join(book_lines), encoding="utf-8")

    artifacts = {
        "inventory": OUT / "gdt572_4_bracket_marker_inventory.tsv",
        "signatures": OUT / "gdt572_11_bracket_signature_profiles.tsv",
        "carry_forms": OUT / "gdt572_20_nonstate_carried_argument_forms.tsv",
        "scope_cards": OUT / "gdt572_5_scope_voice_cards.tsv",
        "assignments": OUT / "gdt572_1536_bracket_voice_assignments.tsv",
        "changes": OUT / "gdt572_1156_changed_nonstate_clauses.tsv",
        "events": OUT / "gdt572_5122_bracket_free_event_edition.tsv",
        "statements": OUT / "gdt572_793_bracket_free_statement_edition.tsv",
        "pages": OUT / "gdt572_30_page_bracket_voice_profiles.tsv",
    }
    write_tsv(artifacts["inventory"], inventory_rows)
    write_tsv(artifacts["signatures"], signature_rows)
    write_tsv(artifacts["carry_forms"], carry_rows)
    write_tsv(artifacts["scope_cards"], scope_rows)
    write_tsv(artifacts["assignments"], assignments)
    write_tsv(artifacts["changes"], changed_rows)
    write_tsv(artifacts["events"], event_rows)
    write_tsv(artifacts["statements"], statement_rows)
    write_tsv(artifacts["pages"], page_rows)

    result = {
        "experiment_id": "GDT572",
        "status": STATUS,
        "metrics": {
            "bracket_marker_type_count": len(marker_counter),
            "bracket_signature_count": len(signature_counter),
            "bracket_occurrence_count": len(assignments),
            "bracket_bearing_nonstate_event_count": len(changed_rows),
            "prior_marker_occurrence_count": marker_counter["[wie zuvor]"],
            "prior_marker_event_count": len(marker_event_sets["[wie zuvor]"]),
            "scope_marker_occurrence_count": len(assignments) - marker_counter["[wie zuvor]"],
            "scope_marker_event_count": len(marker_event_sets["[außen]"] | marker_event_sets["[innen]"] | marker_event_sets["[Stufe 3]"]),
            "old_carry_form_count": 19,
            "newly_occupied_carry_form_count": 1,
            "complete_carry_form_count": len(carry_rows),
            "scope_voice_card_count": len(scope_rows),
            "changed_nonstate_event_count": len(changed_rows),
            "unchanged_nonstate_event_count": unchanged_nonstate_count,
            "unchanged_state_event_count": unchanged_state_count,
            "changed_statement_count": len(changed_statement_ids),
            "unchanged_statement_count": len(statement_rows) - len(changed_statement_ids),
            "changed_physical_page_count": len(changed_pages),
            "remaining_bracket_occurrence_count": 0,
            "complete_event_count": len(event_rows),
            "complete_statement_count": len(statement_rows),
            "complete_page_count": len(page_rows),
            "new_pages": 0,
            "new_events": 0,
            "new_statements": 0,
            "new_surfaces": 0,
            "new_recipes": 0,
            "new_root_values": 0,
        },
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "artifact_sha256": {
            **{name: sha256(path) for name, path in artifacts.items()},
            "book": sha256(OUT / "GDT572_BRACKET_FREE_THIRTY_PAGE_EDITION.md"),
        },
        "notes": [
            "All 1,292 prior markers have an inherited argument root in the original context record.",
            "Nineteen carry forms reuse GDT569; nine Celestial AIN occurrences occupy the previously absent Sektoranteil cell.",
            "Outer, inner and third-level wording is an editorial scope voice and adds no portable root value.",
        ],
    }
    result_path = OUT / "gdt572_result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
