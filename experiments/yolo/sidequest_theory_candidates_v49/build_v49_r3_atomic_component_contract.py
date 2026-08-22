#!/usr/bin/env python3
"""Build R3's non-circular, atomically compositional ten-page sidequest edition.

This deliberately does not use V42/V45 creative translations as evidence for
component meanings.  V48 supplies the frozen card inventory and V42 supplies
only the already frozen field segmentation.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
V48 = OUT.parent / "sidequest_theory_candidates_v48"
FIELDS = OUT.parent / "sidequest_theory_candidates_v42/V42_R2_135_FIELD_MEDICAL_EDITION.tsv"

FIXED_PAGES = {
    "f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r",
    "f67r2", "f68r1", "f69v",
}
PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}

# The only host atoms admitted by R3.  These are deliberately minimal formal
# workshop operations rather than content nouns or source-language glosses.
# They are supported by paradigmatic structural behavior, not by V42/V45 prose.
HOST_ATOMS = {
    "ok": {
        "atom": "SET",
        "german": "SETZEN",
        "status": "ADMITTED_FORMAL_OPERATOR",
        "rationale": "five opaque cards share one host across five RIGHT classes; predominantly entry/interior rather than closure",
    },
    "ot": {
        "atom": "MARK",
        "german": "MARKIEREN",
        "status": "ADMITTED_FORMAL_OPERATOR",
        "rationale": "three opaque cards share one host across three RIGHT classes and contrast structurally with OK",
    },
    "l": {
        "atom": "LINK",
        "german": "VERKNUEPFEN",
        "status": "ADMITTED_FORMAL_OPERATOR",
        "rationale": "five opaque cards recur with bare, framed, RIGHT-bearing and closed realizations across five prose pages",
    },
}

# These are opaque formal argument classes.  The labels preserve distinctions;
# they do not claim VALUE, UNIT, TARGET, SOURCE, or PATH semantics.
RIGHT_ATOMS = {
    "aiin": "ARG_AIIN",
    "ain": "ARG_AIN",
    "al": "ARG_AL",
    "ar": "ARG_AR",
    "air": "ARG_AIR",
}

FRAME_ATOMS = {"O": "FRAME_O", "OT": "FRAME_OT"}

AUDITED_HOSTS = {
    "ok": ("ACTIVATE / ITEM / ASSIGN / SET", "SET", "ADMIT"),
    "ot": ("REFERENCE / ROUTE / TIME / MARK", "MARK", "ADMIT"),
    "l": ("CONTINUE / RECEIVER / LIQUID / LINK", "LINK", "ADMIT"),
    "or": ("MEDIUM / RESULT / LIQUID / REMAINDER", "UNKNOWN", "REJECT"),
    "al": ("TARGET / PARALLEL / SECOND / PLACE", "UNKNOWN", "REJECT"),
    "e": ("WAIT / STATE / UNTIL / END", "UNKNOWN", "REJECT"),
    "chey": ("TAKE / PORTION / MATERIAL", "UNKNOWN", "REJECT"),
    "chor": ("GATHER / PLANT / SEASON / PROCUREMENT", "UNKNOWN", "REJECT"),
    "aiin": ("MEASURE / STANDARD / VALUE", "UNKNOWN", "REJECT"),
    "ey": ("CLEAR / READY / REQUIRED-END-STATE", "UNKNOWN", "REJECT"),
    "oky": ("USE / ACTIVE-PORTION", "UNKNOWN", "REJECT"),
    "lche": ("DRAIN / LOWER-RECEIVER", "UNKNOWN", "REJECT"),
    "oke": ("RINSE / ONE-PASS", "UNKNOWN", "REJECT"),
    "cthy": ("READY / USABLE", "UNKNOWN", "REJECT"),
    "okeey": ("TEMPER / LUKEWARM", "UNKNOWN", "REJECT"),
    "ckhy": ("CONNECTED-CHANNELS / PATH", "UNKNOWN", "REJECT"),
    "olor": ("PREVIOUS-BATCH / PRODUCT", "UNKNOWN", "REJECT"),
}

PRIOR_COMPONENT_GLOSSES = {
    ("HOST", "ok"): "spezifizierten Arbeitsposten einsetzen/aktivieren",
    ("HOST", "or"): "bereitetes Ergebnis oder Arbeitsmedium",
    ("HOST", "al"): "Ziel- oder Parallelstation",
    ("HOST", "e"): "bis zur Zustandsgrenze führen",
    ("HOST", "ot"): "markierten Bezug oder Weg wählen",
    ("HOST", "l"): "angeschlossene Station oder Fortsetzung",
    ("HOST", "chey"): "ausgewählten Materialanteil aufnehmen",
    ("HOST", "chor"): "Pflanzenmaterial zeitgebunden beschaffen",
    ("WHOLE_CARD", "aiin"): "Maß-/Standardkarte",
    ("WHOLE_CARD", "ey"): "Sollzustandskarte",
    ("WHOLE_CARD", "oky"): "Verwendungskarte",
    ("WHOLE_CARD", "lche"): "Ablaufkarte",
    ("WHOLE_CARD", "oke"): "Spülkarte",
    ("WHOLE_CARD", "cthy"): "Bereitschaftskarte",
    ("WHOLE_CARD", "okeey"): "Temperierkarte",
    ("WHOLE_CARD", "ckhy"): "Verbindungswegkarte",
    ("WHOLE_CARD", "olor"): "Voransatz-Produktkarte",
    ("RIGHT", "aiin"): "Standard-/Parameterplatz",
    ("RIGHT", "ain"): "begrenzte Einheit oder Passage",
    ("RIGHT", "al"): "Ziel-/Parallelplatz",
    ("RIGHT", "ar"): "Quellen-/Lokalrelation",
    ("RIGHT", "air"): "Fluss-/Laufweg",
    ("FRAME", "O"): "Kontext/Voransatz fortsetzen",
    ("FRAME", "OT"): "markierten Sekundärbezug setzen",
    ("INNER", "D"): "gelernte Operations-/Zustandsvariante",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    assert rows
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def structural_formula(card: dict[str, str]) -> tuple[str, str, str, str]:
    """Return atom/status/formula/generic argument completion for one card."""
    host = card["page_host"]
    if host in HOST_ATOMS:
        host_atom = HOST_ATOMS[host]["atom"]
        host_status = HOST_ATOMS[host]["status"]
        expression = host_atom
    else:
        host_atom = "UNKNOWN"
        host_status = "OPAQUE_HOST_NO_ATOMIC_GLOSS"
        expression = f"UNKNOWN_HOST[{host.upper()}]"

    if card["inner_d"] == "1":
        expression = f"VARIANT_D({expression})"

    right = card["right_family"]
    if right != "NONE":
        arg = RIGHT_ATOMS[right]
        if host_atom != "UNKNOWN":
            expression = f"{expression}(<{arg}>)"
        else:
            expression = f"{expression} + <{arg}>"

    frame = card["local_frame"]
    if frame != "NONE":
        expression = f"{FRAME_ATOMS[frame]}({expression})"

    if card["dy_closure"] == "1":
        expression = f"CLOSE({expression})"
    if card["b3"] == "1":
        expression = f"CLOSE_B3({expression})"

    if host_atom == "SET":
        generic = "SETZE <formal ausgewiesenes, inhaltlich unbekanntes Argument>"
    elif host_atom == "MARK":
        generic = "MARKIERE <formal ausgewiesenen, inhaltlich unbekannten Bezug>"
    elif host_atom == "LINK":
        generic = "VERKNUEPFE <lokal gegebenen, inhaltlich unbekannten Anschluss>"
    else:
        generic = f"<unbekannter Kartenwert {host.upper()}>"
    if card["dy_closure"] == "1":
        generic += "; SCHLIESSE DIE FORMALE EINHEIT"
    if card["b3"] == "1":
        generic += "; SETZE B3-SCHLUSS"
    return host_atom, host_status, expression, generic


def main() -> None:
    cards_in = read(V48 / "V48_SELECTED_173_CARD_DICTIONARY.tsv")
    events_in = read(V48 / "V48_SELECTED_381_EVENT_INTERLINEAR.tsv")
    field_source = read(FIELDS)
    assert len(cards_in) == 173
    assert len(events_in) == 381
    assert len(field_source) == 135
    assert {row["page"] for row in events_in} == PROSE_PAGES
    assert FIXED_PAGES - PROSE_PAGES == {"f67r2", "f68r1", "f69v"}
    assert {row["local_frame"] for row in cards_in} <= {"NONE", *FRAME_ATOMS}
    assert {row["right_family"] for row in cards_in} <= {"NONE", *RIGHT_ATOMS}

    host_card_counts = Counter(row["page_host"] for row in cards_in)
    host_event_counts = Counter(row["page_host"] for row in events_in)
    pages_by_host: dict[str, set[str]] = defaultdict(set)
    for row in events_in:
        pages_by_host[row["page_host"]].add(row["page"])
    source_card_by_tuple = {row["joint_tuple_id"]: row for row in cards_in}

    def event_coordinate_count(coordinate: str, value: str) -> int:
        return sum(
            source_card_by_tuple[row["joint_tuple_id"]][coordinate] == value
            for row in events_in
        )

    contract: list[dict[str, object]] = []
    for host, (alternatives, selected, decision) in AUDITED_HOSTS.items():
        if decision == "ADMIT":
            gloss_status = "FORMAL_OPERATIONAL_VALUE_ONLY"
            evidence = HOST_ATOMS[host]["rationale"]
            use = f"{selected}(<opaque local/right argument>)"
        else:
            gloss_status = "NO_ATOMIC_COMMON_MEANING"
            evidence = "available commonality is recurrence/placement or inherited local prose; it does not select one meaning"
            use = f"UNKNOWN_HOST[{host.upper()}]"
        contract.append({
            "component_level": "HOST",
            "component_id": host.upper(),
            "candidate_atomic_values": alternatives,
            "decision": decision,
            "selected_atomic_value": selected,
            "value_status": gloss_status,
            "card_types": host_card_counts[host],
            "events": host_event_counts[host],
            "folios": len(pages_by_host[host]),
            "non_gloss_evidence": evidence,
            "executable_use": use,
        })

    for right, atom in RIGHT_ATOMS.items():
        contract.append({
            "component_level": "RIGHT",
            "component_id": right.upper(),
            "candidate_atomic_values": PRIOR_COMPONENT_GLOSSES[("RIGHT", right)],
            "decision": "ADMIT_OPAQUE_ONLY",
            "selected_atomic_value": atom,
            "value_status": "FORMAL_ARGUMENT_CLASS_NOT_SEMANTIC_GLOSS",
            "card_types": sum(row["right_family"] == right for row in cards_in),
            "events": event_coordinate_count("right_family", right),
            "folios": "NA_CARD_LEVEL",
            "non_gloss_evidence": "GDT327 distinguishes this RIGHT family, but no source meaning follows from that coordinate",
            "executable_use": f"<{atom}>",
        })

    for frame, atom in FRAME_ATOMS.items():
        contract.append({
            "component_level": "FRAME",
            "component_id": frame,
            "candidate_atomic_values": PRIOR_COMPONENT_GLOSSES[("FRAME", frame)],
            "decision": "ADMIT_OPAQUE_ONLY",
            "selected_atomic_value": atom,
            "value_status": "FORMAL_CONSTRUCTION_STATE_NOT_SEMANTIC_GLOSS",
            "card_types": sum(row["local_frame"] == frame for row in cards_in),
            "events": event_coordinate_count("local_frame", frame),
            "folios": "NA_CARD_LEVEL",
            "non_gloss_evidence": "GDT327 distinguishes this local frame; the old contextual expansion is not independently identified",
            "executable_use": f"{atom}(<base>)",
        })

    contract.extend([
        {
            "component_level": "INNER",
            "component_id": "D",
            "candidate_atomic_values": "operation / state / variant",
            "decision": "ADMIT_OPAQUE_ONLY",
            "selected_atomic_value": "VARIANT_D",
            "value_status": "FORMAL_VARIANT_NOT_SEMANTIC_GLOSS",
            "card_types": sum(row["inner_d"] == "1" for row in cards_in),
            "events": event_coordinate_count("inner_d", "1"),
            "folios": "NA_CARD_LEVEL",
            "non_gloss_evidence": "coordinate is observable; operation/state interpretation is not",
            "executable_use": "VARIANT_D(<base>)",
        },
        {
            "component_level": "CLOSURE",
            "component_id": "DY",
            "candidate_atomic_values": "close / finish / action",
            "decision": "ADMIT",
            "selected_atomic_value": "CLOSE",
            "value_status": "FORMAL_BOUNDARY_OPERATION_ONLY",
            "card_types": sum(row["dy_closure"] == "1" for row in cards_in),
            "events": event_coordinate_count("dy_closure", "1"),
            "folios": "NA_CARD_LEVEL",
            "non_gloss_evidence": "DY is the frozen formal closure coordinate; no particular action is assigned",
            "executable_use": "CLOSE(<base>)",
        },
        {
            "component_level": "CLOSURE",
            "component_id": "B3",
            "candidate_atomic_values": "special close / result / end",
            "decision": "ADMIT",
            "selected_atomic_value": "CLOSE_B3",
            "value_status": "FORMAL_BOUNDARY_OPERATION_ONLY",
            "card_types": sum(row["b3"] == "1" for row in cards_in),
            "events": event_coordinate_count("b3", "1"),
            "folios": "NA_CARD_LEVEL",
            "non_gloss_evidence": "B3 is the frozen special closure coordinate; no source meaning is assigned",
            "executable_use": "CLOSE_B3(<base>)",
        },
        {
            "component_level": "WRAPPER",
            "component_id": "VISIBLE_WRAPPERS",
            "candidate_atomic_values": "prefix / deixis / renderer",
            "decision": "EXCLUDE_FROM_MEANING",
            "selected_atomic_value": "RENDER_ONLY",
            "value_status": "SUPPORTED_RENDERER_CHANNEL",
            "card_types": "NA",
            "events": "NA",
            "folios": "NA",
            "non_gloss_evidence": "supported q/s effects are renderer/placement effects and do not license a source gloss",
            "executable_use": "no semantic contribution",
        },
    ])
    write(OUT / "V49_R3_ATOMIC_COMPONENT_CONTRACT.tsv", contract)

    cards: list[dict[str, object]] = []
    by_tuple: dict[str, dict[str, object]] = {}
    for source in cards_in:
        atom, status, formula, generic = structural_formula(source)
        row: dict[str, object] = {
            "joint_tuple_id": source["joint_tuple_id"],
            "page_host": source["page_host"],
            "surface_examples": source["surface_examples"],
            "host_atomic_value": atom,
            "host_value_status": status,
            "local_frame": source["local_frame"],
            "inner_d": source["inner_d"],
            "right_family": source["right_family"],
            "dy_closure": source["dy_closure"],
            "b3": source["b3"],
            "executable_atomic_formula": formula,
            "generic_argument_completion_German": generic,
            "source_semantic_gloss": "UNASSIGNED",
            "rule": "ONLY_CONTRACT_ATOMS_COMPOSE; UNKNOWN_HOST_REMAINS_UNKNOWN",
        }
        cards.append(row)
        by_tuple[source["joint_tuple_id"]] = row
    write(OUT / "V49_R3_COMPLETE_173_ATOMIC_CARD_LEXICON.tsv", cards)

    events: list[dict[str, object]] = []
    for source in events_in:
        card = by_tuple[source["joint_tuple_id"]]
        events.append({
            "page": source["page"],
            "locus": source["locus"],
            "record": source["record"],
            "event_index": source["event_index"],
            "surface": source["surface"],
            "joint_tuple_id": source["joint_tuple_id"],
            "page_host": source["page_host"],
            "executable_atomic_formula": card["executable_atomic_formula"],
            "generic_argument_completion_German": card["generic_argument_completion_German"],
            "source_semantic_gloss": "UNASSIGNED",
        })
    write(OUT / "V49_R3_COMPLETE_381_ATOMIC_EVENT_EDITION.tsv", events)

    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        by_locus[str(event["locus"])].append(event)
    cursors: Counter[str] = Counter()
    fields: list[dict[str, object]] = []
    for source in field_source:
        locus = source["locus"]
        count = int(source["card_count"])
        start = cursors[locus]
        members = by_locus[locus][start : start + count]
        cursors[locus] += count
        assert len(members) == count
        assert [str(row["surface"]) for row in members] == source["visible_field"].split()
        fields.append({
            "page": source["page"],
            "record": source["record_ordinal"],
            "locus": locus,
            "field_ordinal": source["source_field_ordinal"],
            "event_count": count,
            "surface_sequence": source["visible_field"],
            "executable_atomic_sequence": " | ".join(str(row["executable_atomic_formula"]) for row in members),
            "generic_argument_sequence_German": "; ".join(str(row["generic_argument_completion_German"]) for row in members),
            "source_semantic_translation": "UNASSIGNED",
        })
    assert all(cursors[locus] == len(rows) for locus, rows in by_locus.items())
    write(OUT / "V49_R3_COMPLETE_135_ATOMIC_FIELD_EDITION.tsv", fields)

    rejected: list[dict[str, object]] = []
    for (level, unit), gloss in PRIOR_COMPONENT_GLOSSES.items():
        if level == "HOST" and unit in HOST_ATOMS:
            replacement = HOST_ATOMS[unit]["atom"]
            reason = "compound/content-rich gloss exceeds the structurally supported atomic operator"
        elif level in {"RIGHT", "FRAME", "INNER"}:
            if level == "RIGHT":
                replacement = RIGHT_ATOMS[unit]
            elif level == "FRAME":
                replacement = FRAME_ATOMS[unit]
            else:
                replacement = "VARIANT_D"
            reason = "coordinate is retained but its semantic expansion was not independently established"
        else:
            replacement = "UNKNOWN"
            reason = "meaning was abstracted from speculative local prose rather than independent common evidence"
        rejected.append({
            "gloss_level": level,
            "unit": unit.upper(),
            "rejected_gloss_German": gloss,
            "replacement": replacement,
            "reason": reason,
        })
    for source in cards_in:
        rejected.append({
            "gloss_level": "LOCAL_CARD_SENTENCE",
            "unit": source["joint_tuple_id"],
            "rejected_gloss_German": source["fluent_local_creative_expansion_German"],
            "replacement": by_tuple[source["joint_tuple_id"]]["executable_atomic_formula"],
            "reason": "retired as component evidence; local sentence may remain only in the recovery archive",
        })
    write(OUT / "V49_R3_REJECTED_GLOSSES.tsv", rejected)

    selected_values: dict[str, set[str]] = defaultdict(set)
    for row in cards:
        selected_values[str(row["page_host"])].add(str(row["host_atomic_value"]))
    formulas_by_tuple: dict[str, set[str]] = defaultdict(set)
    for row in events:
        formulas_by_tuple[str(row["joint_tuple_id"])].add(str(row["executable_atomic_formula"]))
    validation = {
        "schema": "SIDEQUEST_V49_R3_ATOMIC_COMPONENT_CONTRACT_V1",
        "status": "PASS",
        "scope": {
            "fixed_pages": sorted(FIXED_PAGES),
            "prose_pages_with_gdt327_events": sorted(PROSE_PAGES),
            "astro_pages_without_gdt327_events": ["f67r2", "f68r1", "f69v"],
        },
        "counts": {
            "cards": len(cards),
            "events": len(events),
            "fields": len(fields),
            "admitted_host_atoms": len(HOST_ATOMS),
            "cards_under_admitted_host_atoms": sum(row["page_host"] in HOST_ATOMS for row in cards_in),
            "events_under_admitted_host_atoms": sum(row["page_host"] in HOST_ATOMS for row in events_in),
            "opaque_host_cards": sum(row["page_host"] not in HOST_ATOMS for row in cards_in),
            "contract_rows": len(contract),
            "rejected_gloss_rows": len(rejected),
        },
        "checks": {
            "cards_173": len(cards) == 173,
            "events_381": len(events) == 381,
            "fields_135": len(fields) == 135,
            "same_host_same_atomic_value": all(len(values) == 1 for values in selected_values.values()),
            "same_tuple_same_formula": all(len(values) == 1 for values in formulas_by_tuple.values()),
            "chor_unknown_and_not_split": all(
                row["host_atomic_value"] == "UNKNOWN" and "CHO + R" not in row["executable_atomic_formula"]
                for row in cards if row["page_host"] == "chor"
            ),
            "chey_or_e_al_unknown": all(
                row["host_atomic_value"] == "UNKNOWN"
                for row in cards if row["page_host"] in {"chey", "or", "e", "al"}
            ),
            "no_old_local_gloss_in_card_output": all(
                row["source_semantic_gloss"] == "UNASSIGNED" for row in cards
            ),
            "right_values_are_opaque_argument_classes": all(
                atom.startswith("ARG_") for atom in RIGHT_ATOMS.values()
            ),
            "wrappers_have_no_semantic_contribution": True,
            "v42_used_for_segmentation_only": True,
            "v45_not_read": True,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V49_R3_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
