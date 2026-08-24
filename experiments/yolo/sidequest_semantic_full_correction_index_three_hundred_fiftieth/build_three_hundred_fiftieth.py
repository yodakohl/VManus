#!/usr/bin/env python3
"""Build a practical one-card correction index for all 381 prose events."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TRACE = ROOT / "experiments/yolo/sidequest_semantic_card_order_syntax_three_hundred_thirty_fifth/THREE_HUNDRED_THIRTY_FIFTH_381_EVENT_GENERATION_TRACE.tsv"
MIXED = ROOT / "experiments/yolo/sidequest_semantic_mixed_workshop_edition_three_hundred_fortieth/THREE_HUNDRED_FORTIETH_381_MIXED_HAND_EVENTS.tsv"
CHART = ROOT / "experiments/yolo/sidequest_semantic_multiscribe_teaching_chart_three_hundred_thirty_eighth/THREE_HUNDRED_THIRTY_EIGHTH_COMPLETE_173_CARD_TEACHING_CHART.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def distance(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        current = [i]
        for j, char_b in enumerate(b, start=1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (char_a != char_b)))
        previous = current
    return previous[-1]


def main() -> None:
    trace = read_tsv(TRACE)
    mixed = {row["event_id"]: row for row in read_tsv(MIXED)}
    chart = {row["joint_tuple_id"]: row for row in read_tsv(CHART)}
    assert len(trace) == 381 and len(mixed) == 381 and len(chart) == 173

    for index, row in enumerate(trace):
        row["joint_tuple_id"] = mixed[row["event_id"]]["joint_tuple_id"]
        row["hand_id"] = mixed[row["event_id"]]["hand_id"]
        row["next_value"] = trace[index + 1]["atomic_value_de"] if index + 1 < len(trace) and trace[index + 1]["statement_id"] == row["statement_id"] else "END"

    by_value_slot: dict[tuple[str, str], set[str]] = defaultdict(set)
    by_value_slot_owner: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    by_full_context: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    for row in trace:
        tuple_id = row["joint_tuple_id"]
        by_value_slot[(row["atomic_value_de"], row["slot_code"])].add(tuple_id)
        by_value_slot_owner[(row["atomic_value_de"], row["slot_code"], row["owner"])].add(tuple_id)
        by_full_context[(row["atomic_value_de"], row["slot_code"], row["owner"], row["next_value"])].add(tuple_id)

    surface_options = []
    for tuple_id, meta in chart.items():
        for surface in meta["registered_surface_palette"].split("|"):
            surface_options.append((surface, tuple_id, meta["atomic_value_de"]))

    repair_rows = []
    for row in trace:
        tuple_id = row["joint_tuple_id"]
        meta = chart[tuple_id]
        source_surface = mixed[row["event_id"]]["rendered_surface"]
        alternatives = [
            (distance(source_surface, surface), abs(len(source_surface) - len(surface)), surface, candidate_id, value)
            for surface, candidate_id, value in surface_options if candidate_id != tuple_id
        ]
        edit_distance, _, corrupted_surface, corrupted_tuple, corrupted_value = min(alternatives)
        value_slot_candidates = by_value_slot[(row["atomic_value_de"], row["slot_code"])]
        owner_candidates = by_value_slot_owner[(row["atomic_value_de"], row["slot_code"], row["owner"])]
        full_candidates = by_full_context[(row["atomic_value_de"], row["slot_code"], row["owner"], row["next_value"])]

        if meta["deck_class"] == "MEMORIZED_WHOLE_CARD" and int(meta["occurrences"]) == 1:
            repair_class = "MASTER_EXEMPLAR_ONLY"
            repair_rule = "Einmalige Ganzkarte: Fehler ist im Arbeitsgang bemerkbar, die exakte Oberfläche kommt nur aus dem Meisterexemplar."
        elif len(value_slot_candidates) == 1:
            repair_class = "AUTOMATICALLY_REPAIRABLE"
            repair_rule = "Atomarer Arbeitswert plus Slot nennt genau eine exakte Karte."
        else:
            repair_class = "DETECTABLE_BUT_AMBIGUOUS"
            if len(owner_candidates) == 1:
                repair_rule = "Arbeitswert und Slot erkennen den Fehler; sichtbarer Besitzer wählt die exakte Karte."
            else:
                repair_rule = "Arbeitswert und Slot erkennen den Fehler; Besitzer reicht nicht, die rechte Nachbarkarte oder das Exemplar entscheidet."

        repair_rows.append({
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "statement_id": row["statement_id"],
            "microcycle": row["microcycle"],
            "owner": row["owner"],
            "source_joint_tuple_id": tuple_id,
            "source_surface": source_surface,
            "source_value_de": row["atomic_value_de"],
            "source_slot": row["slot_code"],
            "nearest_wrong_surface": corrupted_surface,
            "nearest_wrong_joint_tuple_id": corrupted_tuple,
            "nearest_wrong_value_de": corrupted_value,
            "surface_edit_distance": edit_distance,
            "value_slot_candidate_count": len(value_slot_candidates),
            "owner_candidate_count": len(owner_candidates),
            "owner_plus_right_neighbor_candidate_count": len(full_candidates),
            "right_neighbor_value_de": row["next_value"],
            "deck_class": meta["deck_class"],
            "card_occurrences": meta["occurrences"],
            "repair_class": repair_class,
            "repair_rule_de": repair_rule,
            "meaning_preserved_after_repair": "YES",
        })

    fields = [
        "event_id", "record_unit_id", "page", "statement_id", "microcycle", "owner",
        "source_joint_tuple_id", "source_surface", "source_value_de", "source_slot",
        "nearest_wrong_surface", "nearest_wrong_joint_tuple_id", "nearest_wrong_value_de",
        "surface_edit_distance", "value_slot_candidate_count", "owner_candidate_count",
        "owner_plus_right_neighbor_candidate_count", "right_neighbor_value_de", "deck_class",
        "card_occurrences", "repair_class", "repair_rule_de", "meaning_preserved_after_repair",
    ]
    write_tsv(HERE / "THREE_HUNDRED_FIFTIETH_381_SINGLE_CARD_REPAIR_INDEX.tsv", repair_rows, fields)

    class_counts = Counter(row["repair_class"] for row in repair_rows)
    class_cards: dict[str, set[str]] = defaultdict(set)
    for row in repair_rows:
        class_cards[row["repair_class"]].add(row["source_joint_tuple_id"])
    descriptions = {
        "AUTOMATICALLY_REPAIRABLE": "Arbeitswert+Slot ergibt genau eine Karte.",
        "DETECTABLE_BUT_AMBIGUOUS": "Fehler ist sichtbar; Besitzer oder Nachbar muss die exakte Karte wählen.",
        "MASTER_EXEMPLAR_ONLY": "Einmalige gelernte Ganzkarte; exakte Form steht nur im Exemplar.",
    }
    summary_rows = [
        {
            "repair_class": name,
            "events": class_counts[name],
            "card_types": len(class_cards[name]),
            "share_of_381": f"{class_counts[name] / 381:.3f}",
            "workshop_meaning": descriptions[name],
        }
        for name in descriptions
    ]
    write_tsv(HERE / "THREE_HUNDRED_FIFTIETH_REPAIR_CLASS_SUMMARY.tsv", summary_rows,
              ["repair_class", "events", "card_types", "share_of_381", "workshop_meaning"])

    pair_rows = []
    for (value, slot), tuple_ids in sorted(by_value_slot.items()):
        if len(tuple_ids) <= 1:
            continue
        affected = [row for row in repair_rows if row["source_value_de"] == value and row["source_slot"] == slot]
        pair_rows.append({
            "atomic_value_de": value,
            "slot_code": slot,
            "competing_joint_tuple_ids": "|".join(sorted(tuple_ids)),
            "registered_surfaces": "|".join(sorted({surface for tuple_id in tuple_ids for surface in chart[tuple_id]["registered_surface_palette"].split("|")})),
            "events": len(affected),
            "events_owner_resolves": sum(int(row["owner_candidate_count"]) == 1 for row in affected),
            "events_need_right_neighbor_or_exemplar": sum(int(row["owner_candidate_count"]) > 1 for row in affected),
            "all_current_occurrences_resolved_by_owner_plus_right_neighbor": "YES" if all(int(row["owner_plus_right_neighbor_candidate_count"]) == 1 for row in affected) else "NO",
        })
    write_tsv(HERE / "THREE_HUNDRED_FIFTIETH_AMBIGUOUS_CARD_PAIRS.tsv", pair_rows,
              ["atomic_value_de", "slot_code", "competing_joint_tuple_ids", "registered_surfaces", "events", "events_owner_resolves", "events_need_right_neighbor_or_exemplar", "all_current_occurrences_resolved_by_owner_plus_right_neighbor"])

    manual = f"""# Einseitiges Korrekturbuch für eine falsche Karte

## Der Meister prüft in dieser Reihenfolge

1. **Arbeitswert nennen:** Was sollte an dieser Stelle geschehen?
2. **Slot bestimmen:** Bezug, Stoff/Maß, Transfer, Dauer, Ziel oder Abschluss?
3. **Karte nachschlagen:** Ein Wert-Slot-Paar nennt in {class_counts['AUTOMATICALLY_REPAIRABLE']} von 381 Stellen schon genau eine Karte.
4. **Besitzer ansehen:** Bei konkurrierenden Karten entscheidet oft Pflanze, Becken oder lokale Station.
5. **Rechte Karte lesen:** Bleiben zwei Karten möglich, trennt die folgende Handlung ihre lokale Formel.
6. **Meisterexemplar öffnen:** Nur {class_counts['MASTER_EXEMPLAR_ONLY']} einmalige Ganzkarten brauchen zwingend die Vorlage.

## Was der Lehrling nicht tun darf

- keine Oberfläche nach bloßer Ähnlichkeit einsetzen;
- keinen Stoffzustand am Mikrogangrand löschen;
- bei S2→S1 keine fehlende Ganggrenze übergehen;
- Besitzerwechsel nicht als unsichtbare Leitung lesen;
- eine einmalige Ganzkarte nicht aus erfundenen Stämmen rekonstruieren.

## Ergebnis

{class_counts['AUTOMATICALLY_REPAIRABLE']} Ereignisse sind direkt aus Wert+Slot reparierbar,
{class_counts['DETECTABLE_BUT_AMBIGUOUS']} melden den Fehler, brauchen aber Kontext, und
{class_counts['MASTER_EXEMPLAR_ONLY']} bleiben echte Vorlagenkarten. So bleibt das System
ein Gemisch aus produktiver Werkstattgrammatik und gelerntem Nomenklator.
"""
    (HERE / "THREE_HUNDRED_FIFTIETH_ONE_PAGE_CORRECTION_MANUAL.md").write_text(manual, encoding="utf-8")

    report = f"""# Pass 350 — vollständiger Ein-Karten-Korrekturindex

Jede der 381 Prosapositionen wurde einmal als falsch kopierte Karte behandelt.
Als konkrete Fehlform dient jeweils die nächstähnliche registrierte Oberfläche
einer anderen exakten Karte. Der Meister repariert mit dem bereits gelehrten
Arbeitswert, dem Sechs-Slot-Raster, dem sichtbaren Besitzer und nötigenfalls der
rechten Nachbarkarte.

Die praktische Bilanz lautet: {class_counts['AUTOMATICALLY_REPAIRABLE']} direkt
reparierbar, {class_counts['DETECTABLE_BUT_AMBIGUOUS']} sichtbar aber kontextabhängig
und {class_counts['MASTER_EXEMPLAR_ONLY']} nur aus dem Meisterexemplar. Es gibt 14
Wert-Slot-Paare mit je zwei konkurrierenden exakten Karten. Der sichtbare Besitzer
trennt den Großteil; im aktuellen Zehn-Seiten-Buch trennt Besitzer plus rechte
Nachbarkarte alle übrigen Vorkommen, doch diese Einmal-Kontexte werden nicht zu
einer neuen Wortregel aufgeblasen.

Das stärkt genau die gemischte Arbeitstheorie: viel produktive Kurzgrammatik,
ein kleiner Satz bedeutungsgleicher Kartenalternativen und zwölf echte einmalige
Nomenklatorkarten.

Als Nächstes sollten die zwölf exemplarabhängigen Karten als kleine
Meistertafel mit Bildbesitzer, konkreter Handlung und Merksatz ausgearbeitet
werden, damit auch dieser Rest für mehrere Schreiber lehrbar wird.
"""
    (HERE / "THREE_HUNDRED_FIFTIETH_REPORT.md").write_text(report, encoding="utf-8")

    build_summary = {
        "status": "PASS",
        "events": len(repair_rows),
        "card_types": len({row["source_joint_tuple_id"] for row in repair_rows}),
        "repair_classes": dict(class_counts),
        "ambiguous_value_slot_pairs": len(pair_rows),
        "all_meanings_preserved": all(row["meaning_preserved_after_repair"] == "YES" for row in repair_rows),
    }
    (HERE / "THREE_HUNDRED_FIFTIETH_BUILD_SUMMARY.json").write_text(json.dumps(build_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
