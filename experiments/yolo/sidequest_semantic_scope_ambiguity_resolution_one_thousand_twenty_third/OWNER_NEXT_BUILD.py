#!/usr/bin/env python3
"""Resolve the 146 Pass1022 OWNER_OR_NEXT_CARD_ACTION cases."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_argument_scope_stack_one_thousand_twenty_second"
OUTDIR = Path(__file__).resolve().parent

AMBIGUITIES = SOURCE / "SCOPE_STACK_AMBIGUITIES.tsv"
ATTACHMENTS = SOURCE / "SCOPE_STACK_ATTACHMENTS.tsv"
EVENTS = SOURCE / "PASS1022_3888_EVENT_SCOPE_BINDINGS.tsv"
OUTPUT = OUTDIR / "OWNER_NEXT_146_RESOLUTIONS.tsv"
VALIDATION = OUTDIR / "OWNER_NEXT_VALIDATION.json"

ALLOWED_PAGES = {
    "f10r", "f11r", "f13r", "f17r", "f18r", "f55v", "f56r", "f67r2",
    "f68r1", "f71v", "f72r", "f75r", "f76r", "f77r", "f81v", "f82r",
    "f83r", "f88r", "f88v", "f89r",
}

FIELDS = [
    "resolution_id", "ambiguity_id", "attachment_id", "physical_page", "register",
    "statement_id", "current_event_id", "current_card_ordinal", "statement_card_count",
    "current_locus", "owner_de", "surface_card", "component_recipe", "focus_core",
    "focus_value_de", "previous_card_recipe", "inherited_action_before_card",
    "current_scope_cues", "next_event_id", "next_card_ordinal", "next_locus",
    "next_surface_card", "next_component_recipe", "next_scope_cues", "next_action",
    "next_action_value_de", "next_action_atom_ordinal", "head_distance_cards",
    "owner_boundary", "proseblock_boundary", "locus_relation", "next_closes_dy",
    "decision", "attachment_target", "decision_rule", "rationale_de",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def cues(recipe: str) -> str:
    tokens = set(recipe.split("+"))
    found = [token for token in ("CARRIER_Q", "OT", "OS", "DY", "OL", "L", "AIR") if token in tokens]
    return "|".join(found) if found else "NONE"


def resolve(row: dict[str, str], att: dict[str, str], current: dict[str, str], nxt: dict[str, str]) -> tuple[str, str, str]:
    tokens = set(row["component_recipe"].split("+"))
    owner_boundary = current["owner_de"] != nxt["owner_de"]
    proseblock_boundary = current["statement_id"] != nxt["statement_id"]

    if owner_boundary or proseblock_boundary:
        return (
            "OWNER_ONLY",
            "REAL_OWNER_OR_PROSEBLOCK_BOUNDARY",
            "Eine dokumentierte Besitzer-/Proseblockgrenze sperrt jede Vorwaertsbindung.",
        )
    if "DY" in tokens:
        return (
            "OWNER_ONLY",
            "CURRENT_DY_CLOSE",
            "DY schliesst das aktuelle Paket vor dem naechsten Kartenkopf.",
        )
    if "OS" in tokens:
        return (
            "OWNER_ONLY",
            "CURRENT_OS_RESTORE",
            "OS stellt den Besitzerrahmen wieder her; kein neuer rechter Kopf wird geerbt.",
        )
    if "OT" in tokens:
        return (
            "BOUNDED_FORWARD",
            "OT_SIBLING_FORWARD",
            "OT schaltet auf den unmittelbar folgenden Geschwisterkopf; Besitzer und Proseblock bleiben gleich.",
        )
    if "CARRIER_Q" in tokens:
        return (
            "BOUNDED_FORWARD",
            "Q_PACKET_FORWARD",
            "Q oeffnet das lokale Paket, dessen erster Kopf auf der unmittelbar folgenden Karte steht.",
        )
    if tokens & {"L", "AIR"}:
        return (
            "BOUNDED_FORWARD",
            "L_OR_AIR_RIGHT_FRAME",
            "L/AIR bildet hier einen rechten Rahmen bis zum ersten Kopf der unmittelbar folgenden Karte.",
        )
    if row["focus_core"] in {"AR", "AL"}:
        return (
            "OWNER_ONLY",
            "AR_AL_DEFAULT_OWNER",
            "AR/AL bevorzugt links; ohne lokalen oder geerbten Kopf und ohne Q/OT/L/AIR-Lizenz bleibt der Wert beim Besitzer.",
        )
    if row["focus_core"] in {"E", "EE"}:
        return (
            "BOUNDED_FORWARD",
            "GRADE_TO_NEXT_COMPATIBLE_HEAD",
            "Der Grad erreicht den ersten kompatiblen Kopf der naechsten Karte; keine Grenze liegt dazwischen.",
        )
    if "CARRIER_Q" in set(nxt["component_recipe"].split("+")):
        return (
            "BOUNDED_FORWARD",
            "OPENING_ARGUMENT_TO_NEXT_Q_PACKET",
            "Die kopflose Anfangsfolge bindet an den ersten Kopf des unmittelbar folgenden Q-Pakets.",
        )
    return (
        "BOUNDED_FORWARD",
        "OPENING_ARGUMENT_FORWARD",
        "Die kopflose Anfangsfolge erreicht den ersten Kopf der unmittelbar folgenden Karte im selben Besitzer-/Proseblock.",
    )


def main() -> None:
    ambiguities = [
        row for row in read_tsv(AMBIGUITIES)
        if row["ambiguity_class"] == "OWNER_OR_NEXT_CARD_ACTION"
    ]
    attachments = {row["attachment_id"]: row for row in read_tsv(ATTACHMENTS)}
    events = read_tsv(EVENTS)
    event_by_id = {row["event_id"]: row for row in events}
    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        statement_events[event["statement_id"]].append(event)
    for event_rows in statement_events.values():
        event_rows.sort(key=lambda row: int(row["running_event_ordinal"]))
    card_ordinal = {
        event["event_id"]: index
        for event_rows in statement_events.values()
        for index, event in enumerate(event_rows, start=1)
    }

    assert len(ambiguities) == 146
    assert len({row["ambiguity_id"] for row in ambiguities}) == 146
    assert {row["physical_page"] for row in ambiguities} <= ALLOWED_PAGES

    out_rows: list[dict[str, str]] = []
    for number, row in enumerate(ambiguities, start=1):
        att = attachments[row["attachment_id"]]
        current = event_by_id[row["event_id"]]
        nxt = event_by_id[att["next_card_event_id"]]
        match = re.fullmatch(r"([^=]+)=([^@]+)@NÄCHSTE_KARTE_ATOM([1-9][0-9]*)", row["alternative_attachment"])
        assert match, row["alternative_attachment"]
        next_action, next_action_value, next_atom = match.groups()
        decision, rule, rationale = resolve(row, att, current, nxt)
        owner_boundary = current["owner_de"] != nxt["owner_de"]
        proseblock_boundary = current["statement_id"] != nxt["statement_id"]
        assert card_ordinal[nxt["event_id"]] - card_ordinal[current["event_id"]] == 1
        assert att["same_card_left_actions"] == "NONE"
        assert att["inherited_action_before_card"] == "NONE"

        out_rows.append({
            "resolution_id": f"OWNERNEXT-{number:03d}",
            "ambiguity_id": row["ambiguity_id"],
            "attachment_id": row["attachment_id"],
            "physical_page": row["physical_page"],
            "register": current["register"],
            "statement_id": row["statement_id"],
            "current_event_id": row["event_id"],
            "current_card_ordinal": str(card_ordinal[current["event_id"]]),
            "statement_card_count": str(len(statement_events[row["statement_id"]])),
            "current_locus": row["locus"],
            "owner_de": current["owner_de"],
            "surface_card": row["surface_card"],
            "component_recipe": row["component_recipe"],
            "focus_core": row["focus_core"],
            "focus_value_de": row["focus_value_de"],
            "previous_card_recipe": att["previous_card_recipe"],
            "inherited_action_before_card": att["inherited_action_before_card"],
            "current_scope_cues": cues(row["component_recipe"]),
            "next_event_id": nxt["event_id"],
            "next_card_ordinal": str(card_ordinal[nxt["event_id"]]),
            "next_locus": nxt["locus"],
            "next_surface_card": nxt["surface"],
            "next_component_recipe": nxt["component_recipe"],
            "next_scope_cues": cues(nxt["component_recipe"]),
            "next_action": next_action,
            "next_action_value_de": next_action_value,
            "next_action_atom_ordinal": next_atom,
            "head_distance_cards": "1",
            "owner_boundary": "YES" if owner_boundary else "NO",
            "proseblock_boundary": "YES" if proseblock_boundary else "NO",
            "locus_relation": "SAME_LOCUS" if current["locus"] == nxt["locus"] else "WRAP_WITHIN_SAME_OWNER",
            "next_closes_dy": nxt["closes_gang"],
            "decision": decision,
            "attachment_target": row["alternative_attachment"] if decision == "BOUNDED_FORWARD" else row["chosen_attachment"],
            "decision_rule": rule,
            "rationale_de": rationale,
        })

    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    validation = {
        "result": "PASS",
        "source_scope": "Pass1022 primary artifacts only",
        "input_hashes": {path.name: sha256(path) for path in (AMBIGUITIES, ATTACHMENTS, EVENTS)},
        "checks": {
            "owner_or_next_rows": len(out_rows),
            "unique_ambiguity_ids": len({row["ambiguity_id"] for row in out_rows}),
            "pages_used": sorted({row["physical_page"] for row in out_rows}),
            "page_count": len({row["physical_page"] for row in out_rows}),
            "outside_allowed_pages": sorted({row["physical_page"] for row in out_rows} - ALLOWED_PAGES),
            "decisions": dict(sorted(Counter(row["decision"] for row in out_rows).items())),
            "decision_rules": dict(sorted(Counter(row["decision_rule"] for row in out_rows).items())),
            "focus_by_decision": {
                focus: dict(sorted(Counter(row["decision"] for row in out_rows if row["focus_core"] == focus).items()))
                for focus in sorted({row["focus_core"] for row in out_rows})
            },
            "head_distance_cards": dict(sorted(Counter(row["head_distance_cards"] for row in out_rows).items())),
            "next_action_atom_ordinal": dict(sorted(Counter(row["next_action_atom_ordinal"] for row in out_rows).items())),
            "owner_boundary_yes": sum(row["owner_boundary"] == "YES" for row in out_rows),
            "proseblock_boundary_yes": sum(row["proseblock_boundary"] == "YES" for row in out_rows),
            "locus_wraps_within_same_owner": sum(row["locus_relation"] == "WRAP_WITHIN_SAME_OWNER" for row in out_rows),
            "current_q": sum("CARRIER_Q" in row["current_scope_cues"].split("|") for row in out_rows),
            "current_ot": sum("OT" in row["current_scope_cues"].split("|") for row in out_rows),
            "current_os": sum("OS" in row["current_scope_cues"].split("|") for row in out_rows),
            "current_dy": sum("DY" in row["current_scope_cues"].split("|") for row in out_rows),
            "next_q": sum("CARRIER_Q" in row["next_scope_cues"].split("|") for row in out_rows),
            "next_ot": sum("OT" in row["next_scope_cues"].split("|") for row in out_rows),
            "next_os": sum("OS" in row["next_scope_cues"].split("|") for row in out_rows),
            "next_dy": sum("DY" in row["next_scope_cues"].split("|") for row in out_rows),
            "next_dy_closures": sum(row["next_closes_dy"] == "YES" for row in out_rows),
            "unresolved": sum(row["decision"] == "UNRESOLVED" for row in out_rows),
        },
        "output_hash": sha256(OUTPUT),
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
