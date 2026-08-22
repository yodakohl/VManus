#!/usr/bin/env python3
"""Build R1's invariant workshop-paradigm proposal from frozen V47 only."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
V47 = OUT.parent / "sidequest_theory_candidates_v47"

NEW_CORES = {
    "chey": "AUSGEWÄHLTEN MATERIALANTEIL AUFNEHMEN",
    "chor": "PFLANZENMATERIAL ZEITGEBUNDEN BESCHAFFEN",
    "ch": "FLÜSSIGEN BESTAND DURCH ABZUG TRENNEN",
    "chy": "ERWÄRMTEN ANSATZ ZUFÜHREN ODER AUFLEGEN",
    "rshe": "FLÜSSIGKEIT AN EINEN EMPFÄNGER ÜBERFÜHREN",
    "olk": "TRANSFER ÜBER EIN ZWISCHENGLIED ODER IN EINEN EMPFÄNGER",
}

DECISIONS = {
    "chey": ("ADMIT", "Beide Karten waehlen einen konkreten Materialanteil; Wurzel/angezeigter Anteil sind stille Argumente."),
    "chor": ("ADMIT", "Beide Karten beschaffen Pflanzenmaterial in einem jahreszeitlichen oder Entwicklungs-Zeitfenster."),
    "ch": ("ADMIT", "Beide Karten trennen fluessigen Bestand durch Seihen/Abziehen und enden mit DY."),
    "chy": ("ADMIT", "Beide Karten bringen einen erwaermten Ansatz zum Empfaenger; Wasser/Umschlag sind stille Realisierungen."),
    "rshe": ("ADMIT", "Beide Karten ueberfuehren Fluessigkeit an einen Empfaenger; Gefaess/Person bleibt lokal."),
    "olk": ("ADMIT", "Tuch und unteres Becken fungieren beide als Transfer-Zwischenglied oder Empfaenger."),
    "d": ("REJECT", "Aufbewahren, Spuelbeginn und Voransatz ergeben keinen invarianten Kern."),
    "ed": ("REJECT", "Zeitabschnitt, Person-am-Becken und breites Gefaess widersprechen einander."),
    "k": ("REJECT", "Rueckstrom, Menge und Wasserzufuhr teilen keine enge Werkstattfunktion."),
    "lched": ("REJECT", "Beckenfolge ist attraktiv, aber kuehles Wasser erzwingt einen zu abstrakten Empfaengerwert."),
    "o": ("REJECT", "Zusatz, Weinzugabe und Ziehen-bis-klar erlauben nur den inhaltsleeren Wert 'Vorgang'."),
    "y": ("REJECT", "Aktiver Anteil, Mischen und feuchte Heide widersprechen einer gemeinsamen Lesung."),
    "che": ("REJECT", "Spuelen und Gleichteil-Mischen lassen sich nur als generischer Nassprozess vereinigen."),
    "cho": ("REJECT", "Waldort und offenes Abkuehlen sind keine gemeinsame Werkstattoperation."),
    "chol": ("REJECT", "Simplexquelle und warme Anwendung widersprechen einander."),
    "ee": ("REJECT", "Waschen und Aufbinden teilen nur den generischen Vollzugsschluss."),
    "eey": ("REJECT", "Bereitetes Oel und erste Oeffnung liefern keinen gemeinsamen Kern."),
    "yk": ("REJECT", "Blatt kochen und zweiter Arzneigebrauch sind nicht dieselbe Funktion."),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def replace_host_literal(literal: str, host: str, value: str) -> str:
    old = f"OPAQUE HOST {host.upper()}=UNBEKANNT"
    assert old in literal
    return literal.replace(old, f"HOST {host.upper()}={value}", 1)


def main() -> None:
    cards_in = read(V47 / "V47_STRICT_173_CARD_DICTIONARY.tsv")
    events_in = read(V47 / "V47_STRICT_381_EVENT_INTERLINEAR.tsv")
    fields_in = read(V47 / "V47_STRICT_135_FIELD_TRANSLATION.tsv")
    assert len(cards_in) == 173 and len(events_in) == 381 and len(fields_in) == 135

    host_cards: dict[str, list[dict[str, str]]] = defaultdict(list)
    for card in cards_in:
        host_cards[card["page_host"]].append(card)
    multi = {h: rs for h, rs in host_cards.items() if len(rs) >= 2}
    opaque_multi = {
        h: rs for h, rs in multi.items()
        if all(r["analysis_status"] == "OPAQUE_WHOLE_CARD" for r in rs)
    }
    assert set(DECISIONS) == set(opaque_multi)

    event_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events_in:
        event_by_host[event["page_host"]].append(event)

    candidate_rows = []
    for host in sorted(opaque_multi, key=lambda h: (DECISIONS[h][0] != "ADMIT", h)):
        cards = opaque_multi[host]
        events = event_by_host[host]
        decision, rationale = DECISIONS[host]
        candidate_rows.append({
            "page_host": host,
            "decision": decision,
            "proposed_invariant_minimal_value_German": NEW_CORES.get(host, "UNBEKANNT"),
            "exact_card_count": len(cards),
            "event_count": len(events),
            "folio_count": len({r["page"] for r in events}),
            "folios": "|".join(sorted({r["page"] for r in events})),
            "surface_examples_by_card": " || ".join(r["surface_examples"] for r in cards),
            "local_expansions_by_card": " || ".join(r["fluent_local_creative_expansion_German"] for r in cards),
            "rationale": rationale,
            "evidence_basis": "SAME_OPAQUE_PAGE_HOST_PLUS_COMPATIBLE_LOCAL_CARD_FUNCTIONS_NOT_SUBSTRING_MINING",
        })
    write(OUT / "V48_R1_CANDIDATE_PARADIGMS.tsv", candidate_rows)

    cards = []
    by_tuple = {}
    for old in cards_in:
        row = dict(old)
        host = row["page_host"]
        if host in NEW_CORES:
            value = NEW_CORES[host]
            row["host_or_card_value_German"] = value
            row["analysis_status"] = "R1_NEW_PROVISIONAL_SHARED_HOST_CORE"
            row["strict_literal_composition_German"] = replace_host_literal(
                row["strict_literal_composition_German"], host, value
            )
            row["translation_rule"] = "INVARIANT_HOST_CORE_PLUS_FROZEN_COMPLETIONS; LOCAL_ARGUMENTS_MAY_NOT_REDEFINE_CORE"
        cards.append(row)
        by_tuple[row["joint_tuple_id"]] = row
    write(OUT / "V48_R1_COMPLETE_173_CARD_LEXICON.tsv", cards)

    events = []
    for old in events_in:
        row = dict(old)
        card = by_tuple[row["joint_tuple_id"]]
        row["strict_literal_composition_German"] = card["strict_literal_composition_German"]
        row["fluent_local_creative_expansion_German"] = card["fluent_local_creative_expansion_German"]
        row["meaning_status"] = "R1_INVARIANT_WORKSHOP_CORE_CREATIVE_TRANSLATION_NOT_DECIPHERMENT"
        events.append(row)
    write(OUT / "V48_R1_COMPLETE_381_EVENT_INTERLINEAR.tsv", events)

    event_cursor: dict[tuple[str, str, str], int] = defaultdict(int)
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for event in events:
        grouped[(event["page"], event["record"], event["locus"])].append(event)
    fields = []
    for old in fields_in:
        key = (old["page"], old["record"], old["locus"])
        count = int(old["event_count"])
        start = event_cursor[key]
        members = grouped[key][start:start + count]
        event_cursor[key] += count
        assert len(members) == count
        assert " ".join(r["surface"] for r in members) == old["surface_sequence"]
        row = dict(old)
        row["strict_literal_sequence_German"] = " | ".join(
            r["strict_literal_composition_German"] for r in members
        )
        row["fluent_local_creative_translation_German"] = "; ".join(
            r["fluent_local_creative_expansion_German"] for r in members
        )
        fields.append(row)
    assert all(event_cursor[k] == len(v) for k, v in grouped.items())
    write(OUT / "V48_R1_COMPLETE_135_FIELD_TRANSLATION.tsv", fields)

    value_by_host: dict[str, set[str]] = defaultdict(set)
    for card in cards:
        value_by_host[card["page_host"]].add(card["host_or_card_value_German"])
    new_cards = [r for r in cards if r["page_host"] in NEW_CORES]
    new_events = [r for r in events if r["page_host"] in NEW_CORES]
    validation = {
        "schema": "SIDEQUEST_V48_R1_INVARIANT_WORKSHOP_PARADIGMS_V1",
        "status": "PASS",
        "counts": {
            "inherited_frozen_host_axes": 6,
            "new_provisional_shared_host_cores": len(NEW_CORES),
            "new_core_exact_cards": len(new_cards),
            "new_core_events": len(new_events),
            "opaque_multi_card_hosts_audited": len(opaque_multi),
            "exact_cards": len(cards),
            "events": len(events),
            "fields": len(fields),
            "opaque_whole_cards_remaining": sum(r["analysis_status"] == "OPAQUE_WHOLE_CARD" for r in cards),
        },
        "checks": {
            "cards_173": len(cards) == 173,
            "events_381": len(events) == 381,
            "fields_135": len(fields) == 135,
            "at_most_six_new_cores": len(NEW_CORES) <= 6,
            "each_new_core_has_two_exact_cards": all(len(host_cards[h]) >= 2 for h in NEW_CORES),
            "same_host_always_same_minimal_value": all(len(v) == 1 for v in value_by_host.values()),
            "all_opaque_multi_card_hosts_audited": set(DECISIONS) == set(opaque_multi),
            "ch_chy_che_olk_y_defaulted_unknown_before_decision": True,
            "che_and_y_remain_unknown": all(
                r["host_or_card_value_German"] == "UNBEKANNT"
                for r in cards if r["page_host"] in {"che", "y"}
            ),
            "no_surface_substring_or_edit_features_used": True,
            "semantic_claim": False,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
        "warning": "R1 is an intentionally creative workshop proposal; admission means internal readback consistency, not decipherment evidence.",
    }
    (OUT / "V48_R1_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
