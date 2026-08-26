#!/usr/bin/env python3
"""Resolve the four GDT400 amber attachments as three visible card transitions."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "artifacts"
G399 = ROOT / "experiments/yolo/gdt399_creative_scope_rebuild_after_visible_resegmentation/artifacts"
G400 = ROOT / "experiments/yolo/gdt400_future_page_scope_error_deck/artifacts"
ATTACHMENTS = G399 / "gdt399_4374_scope_attachments.tsv"
EVENTS = G399 / "gdt399_3888_event_replay.tsv"
STATEMENTS = G399 / "gdt399_627_statement_scope_edition.tsv"
REPLAY400 = G400 / "gdt400_4374_hierarchical_replay.tsv"
DECK400 = G400 / "gdt400_error_deck.tsv"

AMBER_IDS = ["G399-A01468", "G399-A02820", "G399-A03234", "G399-A03235"]

# Manual grouping after reading each complete statement. The two f82r rows are
# two focus atoms of one OT+EE+Y card and therefore one visible transition.
TRANSITIONS = [
    {
        "transition_id": "G401-T01",
        "attachment_ids": ["G399-A01468"],
        "scope_parent": "ONE_CARD_FORWARD",
        "structural_reading": "Y | R+OL  =>  R[Y]; OL",
        "plain_reading_de": "Den bereits geöffneten Posten am ersten Kopf der nächsten Karte markieren; danach fortsetzen.",
        "semantic_caution": "NONE",
    },
    {
        "transition_id": "G401-T02",
        "attachment_ids": ["G399-A02820"],
        "scope_parent": "ONE_CARD_FORWARD",
        "structural_reading": "Y | R+SH+D_ADDR+Y  =>  R[Y_previous]; SH[D_ADDR,Y_internal]",
        "plain_reading_de": "Den vorangestellten Posten markieren; den in der Zielkarte stehenden Teilposten getrennt halten.",
        "semantic_caution": "NONE",
    },
    {
        "transition_id": "G401-T03",
        "attachment_ids": ["G399-A03234", "G399-A03235"],
        "scope_parent": "Q_OT_PACKAGE_FORWARD",
        "structural_reading": "OT+EE+Y | R+AIIN  =>  R[OT_PACKET(EE,Y),AIIN]",
        "plain_reading_de": "Den nächsten Posten der zweiten Stufe mit dem angegebenen Wert markieren.",
        "semantic_caution": "EE bleibt im OT-Paket; nicht als Dauer oder Intensität des Markierens ausgeben.",
    },
]

# Selected nearest parents. Every OUTSIDE_REGISTER_PARENT row is non-Biological;
# the f77r row is a same-register packet control: OT+AL | R | AIN.
PARENTS = [
    ("P01", "FORWARD_Y", "G399-A00269", "OUTSIDE_REGISTER_PARENT", "Y springt genau eine Karte zu K."),
    ("P02", "FORWARD_Y", "G399-A00649", "OUTSIDE_REGISTER_PARENT", "Y springt genau eine Karte zu K im Himmelsregister."),
    ("P03", "FORWARD_Y", "G399-A04253", "OUTSIDE_REGISTER_PARENT", "Y springt genau eine Karte zu SH im Gefäßregister."),
    ("P04", "OT_EE_Y_FORWARD", "G399-A00858", "OUTSIDE_REGISTER_PARENT", "EE aus OT+EE+Y springt zu CHD."),
    ("P05", "OT_EE_Y_FORWARD", "G399-A00859", "OUTSIDE_REGISTER_PARENT", "Y aus derselben OT+EE+Y-Karte springt zu CHD."),
    ("P06", "OT_EE_Y_FORWARD", "G399-A00992", "OUTSIDE_REGISTER_PARENT", "EE aus OT+EE+Y springt zu T."),
    ("P07", "OT_EE_Y_FORWARD", "G399-A00993", "OUTSIDE_REGISTER_PARENT", "Y aus derselben OT+EE+Y-Karte springt zu T."),
    ("P08", "R_HEAD_Y", "G399-A00317", "OUTSIDE_REGISTER_PARENT", "R nimmt Y sichtbar in derselben Karte."),
    ("P09", "R_HEAD_Y", "G399-A00742", "OUTSIDE_REGISTER_PARENT", "R nimmt Y sichtbar in einer Himmelskarte."),
    ("P10", "R_HEAD_ARGUMENT", "G399-A00735", "OUTSIDE_REGISTER_PARENT", "R nimmt OR sichtbar in derselben Karte."),
    ("P11", "R_HEAD_ARGUMENT", "G399-A03682", "OUTSIDE_REGISTER_PARENT", "R nimmt AL sichtbar in derselben Gefäßkarte."),
    ("P12", "R_HEAD_ARGUMENT", "G399-A03962", "OUTSIDE_REGISTER_PARENT", "AIN bindet an den unmittelbar vorigen R-Kopf."),
    ("P13", "FORWARD_TO_R_PACKET", "G399-A02584", "SAME_REGISTER_PACKET_CONTROL", "OT+AL springt zu R; das folgende AIN bindet an denselben R-Kopf zurück."),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise AssertionError(f"empty output {path.name}")
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def pipe(values: set[str] | list[str]) -> str:
    selected = sorted({value for value in values if value and value != "NONE"})
    return "|".join(selected) if selected else "NONE"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    attachments = read_tsv(ATTACHMENTS)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    replay400 = read_tsv(REPLAY400)
    deck400 = read_tsv(DECK400)
    if [len(attachments), len(events), len(statements), len(replay400), len(deck400)] != [4374, 3888, 627, 4374, 14]:
        raise AssertionError("upstream inventory mismatch")

    attachment_by_id = {row["attachment_id"]: row for row in attachments}
    event_by_id = {row["event_id"]: row for row in events}
    statement_by_id = {row["statement_id"]: row for row in statements}
    amber400 = [row for row in replay400 if row["outside_register_support_level"] == "COMPOSED_RULE_COMPONENTS"]
    if [row["attachment_id"] for row in amber400] != AMBER_IDS:
        raise AssertionError("GDT400 amber identity drift")

    attachments_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in attachments:
        attachments_by_event[row["event_id"]].append(row)

    transition_rows: list[dict[str, object]] = []
    attachment_rows: list[dict[str, object]] = []
    for transition in TRANSITIONS:
        selected = [attachment_by_id[item] for item in transition["attachment_ids"]]
        source_events = {row["event_id"] for row in selected}
        target_events = {row["chosen_action_event_id"] for row in selected}
        statements_here = {row["statement_id"] for row in selected}
        if len(source_events) != 1 or len(target_events) != 1 or len(statements_here) != 1:
            raise AssertionError(f"transition grouping failed: {transition['transition_id']}")
        source_id = next(iter(source_events))
        target_id = next(iter(target_events))
        statement_id = next(iter(statements_here))
        source = event_by_id[source_id]
        target = event_by_id[target_id]
        statement = statement_by_id[statement_id]
        source_card = int(selected[0]["card_ordinal_in_statement"])
        target_card = int(selected[0]["chosen_action_card_ordinal"])
        target_atoms = target["component_recipe"].split("+")
        internal = [f"{row['focus_core']}->{row['chosen_action']}" for row in attachments_by_event[target_id]]
        transition_rows.append({
            "transition_id": transition["transition_id"],
            "attachment_ids": "|".join(transition["attachment_ids"]),
            "attachment_count": len(selected),
            "physical_page": selected[0]["physical_page"],
            "register": selected[0]["register"],
            "statement_id": statement_id,
            "owner_de": selected[0]["owner_de"],
            "complete_surface_sequence": statement["surface_sequence"],
            "complete_recipe_sequence": statement["corrected_recipe_sequence"],
            "source_event_id": source_id,
            "source_card_ordinal": source_card,
            "source_locus": source["locus"],
            "source_surface": source["surface"],
            "source_recipe": source["component_recipe"],
            "focus_packet": "+".join(row["focus_core"] for row in selected),
            "target_event_id": target_id,
            "target_card_ordinal": target_card,
            "target_locus": target["locus"],
            "target_surface": target["surface"],
            "target_recipe": target["component_recipe"],
            "target_first_atom": target_atoms[0],
            "card_distance": target_card - source_card,
            "same_statement": "YES",
            "same_owner": "YES",
            "physical_locus_crossing": "YES" if source["locus"] != target["locus"] else "NO",
            "target_internal_bindings": pipe(internal),
            "scope_parent": transition["scope_parent"],
            "structural_reading": transition["structural_reading"],
            "plain_reading_de": transition["plain_reading_de"],
            "scope_decision": "GREEN_EXISTING_FORWARD_TO_VISIBLE_R_HEAD",
            "semantic_caution": transition["semantic_caution"],
        })
        for row in selected:
            attachment_rows.append({
                "attachment_id": row["attachment_id"],
                "transition_id": transition["transition_id"],
                "physical_page": row["physical_page"],
                "statement_id": row["statement_id"],
                "source_surface": row["surface"],
                "source_recipe": row["component_recipe"],
                "focus_core": row["focus_core"],
                "focus_value_de": row["focus_value_de"],
                "target_surface": target["surface"],
                "target_recipe": target["component_recipe"],
                "target_action": row["chosen_action"],
                "target_action_atom_ordinal": row["chosen_action_atom_ordinal"],
                "card_distance": row["bounded_lookahead_cards"],
                "owner_boundary_crossed": row["owner_boundary_crossed"],
                "old_support_level": "COMPOSED_RULE_COMPONENTS",
                "factorized_scope_rule": transition["scope_parent"],
                "factorized_head_license": "R_POSITIONAL_HEAD",
                "scope_result": "GREEN_EXISTING_TWO_STAGE_PARSE",
                "semantic_result": "AMBER_KEEP_EE_INSIDE_OT_PACKET" if row["focus_core"] == "EE" else "UNCHANGED_CORE_VALUE",
            })

    parent_rows: list[dict[str, object]] = []
    for parent_id, factor, attachment_id, role, note in PARENTS:
        row = attachment_by_id[attachment_id]
        statement = statement_by_id[row["statement_id"]]
        parent_rows.append({
            "parent_id": parent_id,
            "factor": factor,
            "evidence_role": role,
            "attachment_id": attachment_id,
            "physical_page": row["physical_page"],
            "register": row["register"],
            "statement_id": row["statement_id"],
            "complete_surface_sequence": statement["surface_sequence"],
            "source_surface": row["surface"],
            "source_recipe": row["component_recipe"],
            "focus_core": row["focus_core"],
            "attachment_class": row["chosen_attachment_class"],
            "chosen_action": row["chosen_action"],
            "chosen_action_card_ordinal": row["chosen_action_card_ordinal"],
            "rule_families": row["teaching_rule_families"],
            "r_position_mode": row["r_position_mode"],
            "note_de": note,
        })

    r_heads = [row for row in attachments if row["r_position_mode"] == "R_POSITIONAL_HEAD"]
    forward = [row for row in attachments if row["chosen_attachment_class"] == "BOUNDED_NEXT_CARD_ACTION"]
    outside_r_heads = [row for row in r_heads if row["register"] != "BIOLOGICAL"]
    outside_forward = [row for row in forward if row["register"] != "BIOLOGICAL"]
    forward_to_r = [row for row in forward if row["chosen_action"] == "R"]

    def factor_row(name: str, selected: list[dict[str, str]], interpretation: str) -> dict[str, object]:
        outside = [row for row in selected if row["register"] != "BIOLOGICAL"]
        return {
            "factor": name,
            "occurrences": len(selected),
            "pages": pipe({row["physical_page"] for row in selected}),
            "registers": pipe({row["register"] for row in selected}),
            "attachment_classes": pipe({row["chosen_attachment_class"] for row in selected}),
            "focus_cores": pipe({row["focus_core"] for row in selected}),
            "chosen_actions": pipe({row["chosen_action"] for row in selected}),
            "outside_biological_occurrences": len(outside),
            "outside_biological_registers": pipe({row["register"] for row in outside}),
            "interpretation": interpretation,
        }

    one_card = [row for row in attachments if "ONE_CARD_FORWARD" in row["teaching_rule_families"].split("|")]
    q_ot = [row for row in attachments if "Q_OT_PACKAGE_FORWARD" in row["teaching_rule_families"].split("|")]
    factor_rows = [
        factor_row("BOUNDED_NEXT_CARD_ACTION", forward, "Scope-Operation; genau eine sichtbare Zielkarte."),
        factor_row("ONE_CARD_FORWARD", one_card, "Kopfloses Paket bindet an den ersten sichtbaren Kopf der nächsten Karte."),
        factor_row("Q_OT_PACKAGE_FORWARD", q_ot, "OT/Q öffnet ein Paket für den ersten sichtbaren Kopf der nächsten Karte."),
        factor_row("R_POSITIONAL_HEAD", r_heads, "Kopf-Lizenz; R ist an dieser Position ein sichtbarer Handlungskopf, keine Distanzregel."),
        factor_row("FORWARD_THEN_R_HEAD", forward_to_r, "Abgeleitet: zuerst Vorgriff, dann R als ersten sichtbaren Kopf wählen; keine zehnte Familie."),
    ]

    revised_deck: list[dict[str, object]] = []
    for row in deck400:
        revised_deck.append({
            **row,
            "gdt401_addition": (
                "KNOWN_FORWARD_TO_R_IS_GREEN_WHEN_R_IS_FIRST_VISIBLE_HEAD"
                if row["trigger"] == "HEADLESS_PACKAGE_NEXT_CARD" else
                "IF_OT_EE_Y_PRECEDES_R_KEEP_EE_INSIDE_PACKET"
                if row["trigger"] == "PAGE_PRIVATE_MICRO" else
                "UNCHANGED"
            ),
        })

    transition_path = OUT / "gdt401_three_transition_adjudication.tsv"
    attachment_path = OUT / "gdt401_four_attachment_resolution.tsv"
    parent_path = OUT / "gdt401_parent_examples.tsv"
    factor_path = OUT / "gdt401_factor_support.tsv"
    deck_path = OUT / "gdt401_error_deck_v2.tsv"
    write_tsv(transition_path, transition_rows)
    write_tsv(attachment_path, attachment_rows)
    write_tsv(parent_path, parent_rows)
    write_tsv(factor_path, factor_rows)
    write_tsv(deck_path, revised_deck)

    result = {
        "experiment_id": "GDT401",
        "status": "AMBER_SCOPE_CLOSED__ONE_SEMANTIC_CAUTION_RETAINED",
        "gdt400_amber_attachment_count": 4,
        "visible_transition_count": 3,
        "scope_green_attachment_count": 4,
        "semantic_amber_attachment_count": 1,
        "new_coarse_scope_family_count": 0,
        "forward_attachment_count": len(forward),
        "r_positional_head_attachment_count": len(r_heads),
        "forward_to_r_attachment_count": len(forward_to_r),
        "outside_biological_forward_count": len(outside_forward),
        "outside_biological_r_head_count": len(outside_r_heads),
        "forward_action_distribution": dict(sorted(Counter(row["chosen_action"] for row in forward).items())),
        "r_head_scope_distribution": dict(sorted(Counter(row["chosen_attachment_class"] for row in r_heads).items())),
        "selected_rule": "APPLY_FORWARD_SCOPE_THEN_LICENSE_FIRST_VISIBLE_R_HEAD",
        "semantic_caution": "OT+EE+Y stays one packet; do not gloss EE as duration/intensity of R.",
        "output_hashes": {},
    }
    result_path = OUT / "gdt401_result.json"
    output_paths = [transition_path, attachment_path, parent_path, factor_path, deck_path]
    result["output_hashes"] = {path.name: sha256(path) for path in output_paths}
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
