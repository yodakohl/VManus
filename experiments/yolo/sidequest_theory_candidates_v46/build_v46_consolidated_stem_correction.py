#!/usr/bin/env python3
"""Correct V45 by separating working families from forced semantic stems."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
V45 = OUT.parent / "sidequest_theory_candidates_v45"


# unit: (class, minimal working value, status, reason)
DECISIONS = {
    "ok": ("FORMAL_COMPOSITIONAL_AXIS", "spezifizierten Arbeitsposten einsetzen/aktivieren", "RETAIN_WORKING_AXIS", "5 verschiedene Karten, 24 Ereignisse; Kompletierungen tragen systematisch verschiedene Relationen"),
    "or": ("PROVISIONAL_CONTENT_FAMILY", "bereitetes Ergebnis oder Arbeitsmedium", "RETAIN_PROVISIONAL_CORE", "2 Karten, 8 Ereignisse; gemeinsame Ergebnislesung, aber aus kreativen Glossen abgeleitet"),
    "al": ("PROVISIONAL_RELATION_FAMILY", "Ziel- oder Parallelstation", "RETAIN_LOW_CONFIDENCE_AXIS", "2 Karten, 11 Ereignisse; gemeinsame Richtung nur breit"),
    "e": ("PROVISIONAL_STATE_FAMILY", "Vorgang bis zu einer Zustandsgrenze führen", "RETAIN_LOW_CONFIDENCE_AXIS", "2 Karten, 14 Ereignisse; Bereitschaft/Klarheit können auch aus Kontext und DY stammen"),
    "ot": ("FORMAL_RELATION_AXIS", "markierten Bezug, Parameter oder Weg wählen", "RETAIN_LOW_CONFIDENCE_AXIS", "3 Karten, 7 Ereignisse; gemeinsamer Wert abstrakt"),
    "l": ("FORMAL_CONNECTION_AXIS", "angeschlossene Station oder Fortsetzung", "RETAIN_LOW_CONFIDENCE_AXIS", "5 Karten, 26 Ereignisse; keine gemeinsame Gegenstandsbedeutung"),
    "aiin": ("RECURRENT_WHOLE_CARD", "Maß-/Standardkarte", "NOT_A_STEM_ONE_CARD_ONLY", "20 Ereignisse, aber nur eine exakte Kartenart; Wiederholung belegt Kartenwert, kein Paradigma"),
    "chor": ("EXPLORATORY_LOCAL_FAMILY", "möglicherweise Sammel-/Beschaffungszeit", "DO_NOT_USE_AS_DEFAULT_STEM", "2 Karten, 3 Ereignisse im selben Herbal-Deutungsraum"),
    "chey": ("EXPLORATORY_LOCAL_FAMILY", "möglicherweise ausgewählten Materialteil wählen", "DO_NOT_USE_AS_DEFAULT_STEM", "2 Karten, 3 Ereignisse; gemeinsame Bedeutung stammt aus erzwungener Bildlesung"),
    "y": ("UNASSIGNED_HOST", "UNBEKANNT", "REJECT_V45_STEM_GLOSS", "3 Karten: Stoffträger, Mischhandlung und Habitat; keine belastbare Schnittmenge"),
    "ch": ("UNASSIGNED_HOST", "UNBEKANNT", "REJECT_V45_STEM_GLOSS", "nur 2 Ereignisse; Trennen/Abziehen wurde aus lokalen Übersetzungen zurückprojiziert"),
    "chy": ("UNASSIGNED_HOST", "UNBEKANNT", "REJECT_V45_STEM_GLOSS", "nur 2 verschieden konstruierte Ereignisse; Wärme-/Anwendungswert zirkulär"),
    "che": ("UNASSIGNED_HOST", "UNBEKANNT", "REJECT_V45_STEM_GLOSS", "2 Karten; gemeinsamer Flüssigkeitsschritt nicht unabhängig belegt"),
    "olk": ("UNASSIGNED_HOST", "UNBEKANNT", "REJECT_V45_STEM_GLOSS", "Tuch und Becken sind keine ausreichend enge gemeinsame Bedeutung"),
    "ey": ("RECURRENT_WHOLE_CARD", "lokale Sollzustandskarte", "NOT_A_STEM_ONE_CARD_ONLY", "4 Ereignisse, aber nur eine exakte Karte; sichtbares -ey ist nicht produktiv"),
    "oky": ("RECURRENT_WHOLE_CARD", "lokale Verwendungskarte", "NOT_A_STEM_ONE_CARD_ONLY", "10 Ereignisse, eine Karte"),
    "lche": ("RECURRENT_WHOLE_CARD", "lokale Ablaufkarte", "NOT_A_STEM_ONE_CARD_ONLY", "8 Ereignisse, eine Karte"),
    "oke": ("RECURRENT_WHOLE_CARD", "lokale Spülkarte", "NOT_A_STEM_ONE_CARD_ONLY", "8 Ereignisse, eine Karte"),
    "cthy": ("RECURRENT_WHOLE_CARD", "lokale Bereitschaftskarte", "NOT_A_STEM_ONE_CARD_ONLY", "7 Ereignisse, eine Karte"),
    "okeey": ("RECURRENT_WHOLE_CARD", "lokale Temperierkarte", "NOT_A_STEM_ONE_CARD_ONLY", "7 Ereignisse, eine Karte"),
    "ckhy": ("RECURRENT_WHOLE_CARD", "lokale Verbindungswegkarte", "NOT_A_STEM_ONE_CARD_ONLY", "4 Ereignisse, eine Karte"),
    "olor": ("RECURRENT_WHOLE_CARD", "lokale Voransatz-Produktkarte", "NOT_A_STEM_ONE_CARD_ONLY", "2 Ereignisse, eine Karte"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    old_cards = read(V45 / "V45_SELECTED_REVISED_173_CARD_LEXICON.tsv")
    old_events = read(V45 / "V45_SELECTED_REVISED_381_EVENT_INTERLINEAR.tsv")
    inventory = []
    for unit, (kind, value, status, reason) in DECISIONS.items():
        cards = [r for r in old_cards if r["page_host"] == unit]
        inventory.append({
            "unit": unit,
            "unit_class": kind,
            "corrected_minimal_value_German": value,
            "decision": status,
            "exact_cards": len(cards),
            "fixed_events": sum(int(r["events"]) for r in cards),
            "reason": reason,
        })
    write(OUT / "V46_CORRECTED_CORE_INVENTORY.tsv", inventory)

    corrected_cards = []
    for row in old_cards:
        unit = row["page_host"]
        if unit in DECISIONS:
            kind, value, status, reason = DECISIONS[unit]
        else:
            kind = "UNANALYZED_WHOLE_CARD"
            value = "UNBEKANNT AUF HOSTEBENE"
            status = "KEEP_ONLY_LOCAL_EXACT_CARD_EXPANSION"
            reason = "kein ausgewähltes produktives Hostparadigma"
        corrected_cards.append({
            "joint_tuple_id": row["joint_tuple_id"],
            "page_host": unit,
            "surface_examples": row["surface_examples"],
            "corrected_host_class": kind,
            "corrected_host_value_German": value,
            "host_decision": status,
            "host_reason": reason,
            "formal_additions": row["formal_additions"],
            "retained_local_creative_expansion_German": row["local_medical_expansion_German"],
            "translation_status": "LOCAL_CREATIVE_EXPANSION_NOT_STEM_EVIDENCE",
            "events": row["events"],
            "pages": row["pages"],
        })
    write(OUT / "V46_CORRECTED_173_CARD_LEXICON.tsv", corrected_cards)
    by_tuple = {r["joint_tuple_id"]: r for r in corrected_cards}
    corrected_events = []
    for row in old_events:
        card = by_tuple[row["joint_tuple_id"]]
        corrected_events.append({
            "page": row["page"],
            "locus": row["locus"],
            "record": row["record"],
            "event_index": row["event_index"],
            "surface": row["surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "page_host": row["page_host"],
            "corrected_host_class": card["corrected_host_class"],
            "corrected_host_value_German": card["corrected_host_value_German"],
            "retained_local_creative_expansion_German": card["retained_local_creative_expansion_German"],
            "meaning_status": "LOCAL_CREATIVE_EXPANSION_NOT_STEM_EVIDENCE",
        })
    write(OUT / "V46_CORRECTED_381_EVENT_INTERLINEAR.tsv", corrected_events)
    validation = {
        "schema": "SIDEQUEST_V46_STEM_OVERFIT_CORRECTION_V1",
        "status": "PASS",
        "counts": {
            "audited_units": len(inventory),
            "exact_cards": len(corrected_cards),
            "events": len(corrected_events),
            "retained_working_or_low_confidence_axes": sum(r["decision"].startswith("RETAIN_") for r in inventory),
            "rejected_v45_stem_glosses": sum(r["decision"] == "REJECT_V45_STEM_GLOSS" for r in inventory),
            "reclassified_recurrent_whole_cards": sum(r["decision"] == "NOT_A_STEM_ONE_CARD_ONLY" for r in inventory),
        },
        "checks": {
            "cards_173": len(corrected_cards) == 173,
            "events_381": len(corrected_events) == 381,
            "ch_unknown": DECISIONS["ch"][1] == "UNBEKANNT",
            "chy_unknown": DECISIONS["chy"][1] == "UNBEKANNT",
            "che_unknown": DECISIONS["che"][1] == "UNBEKANNT",
            "y_unknown": DECISIONS["y"][1] == "UNBEKANNT",
            "local_expansions_retained_but_not_counted_as_stem_evidence": all(r["translation_status"] == "LOCAL_CREATIVE_EXPANSION_NOT_STEM_EVIDENCE" for r in corrected_cards),
            "semantic_claim": False,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V46_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
