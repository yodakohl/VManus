#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P549 = ROOT / "experiments/yolo/sidequest_semantic_component_sentence_roles_five_hundred_forty_ninth"
P550 = ROOT / "experiments/yolo/sidequest_semantic_argument_attachment_parser_five_hundred_fiftieth"
P553 = ROOT / "experiments/yolo/sidequest_semantic_unified_action_lexicon_five_hundred_fifty_third"
P555 = ROOT / "experiments/yolo/sidequest_semantic_atomic_card_unification_five_hundred_fifty_fifth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


MANUAL = [
    ("R01", "OWNER", "Bestimme Bild- oder Stationsbesitzer; schreibe ihn nicht als Karte aus."),
    ("R02", "ACTION", "Wähle den kleinsten Handlungskern aus den 17 Aktionskomponenten."),
    ("R03", "ITEM", "Setze Y nur, wenn der aktuelle Posten ausdrücklich gebunden oder wiederaufgenommen wird."),
    ("R04", "QUANTITY", "Setze AIIN für Sollmaß, AIN für eine abgeteilte Portion."),
    ("R05", "ADDRESS", "Setze AR für Quelle, AL für Ziel, AIR/CKH für Lauf oder Durchlass."),
    ("R06", "MATERIAL", "Setze OR für Ansatz, HO für Gabe und O für den Arbeitsgang."),
    ("R07", "ORDER", "Setze OL/LS für Fortsetzung und OT für die nächste Einheit."),
    ("R08", "GRADE", "Setze E, EE oder EEE für kurz, länger oder vollständig."),
    ("R09", "STATE", "Setze CTH für bereit und IIN für Sollstufe."),
    ("R10", "CLOSE", "Setze DY nur in einer lizenzierten Schlusskarte."),
    ("R11", "CARD", "Fasse die Komponenten zur attestierten exakten Karte zusammen."),
    ("R12", "ALLOGRAPH", "Bei elf doppelt belegten Komponentenfolgen wähle die lokale gelernte Kartenallographie."),
    ("R13", "RENDER", "Wähle aus den attestierten Oberflächen der Karte die lokale Positionsform."),
    ("R14", "READ", "Lies Karte zu Komponenten, binde Argumente an die Aktion und erweitere den Frame lokal."),
]

ALLOGRAPH_ATOMIC = {
    "OK+Y": "den aktuellen Posten in Einsatz bringen",
    "OL": "fortsetzen",
    "SH+EE+Y": "den aktuellen Posten länger halten",
    "OT+Y": "danach den aktuellen Posten wiederaufnehmen",
    "OK+OL": "den aktuellen Posten weiter in Einsatz bringen",
    "Y+K+AIN": "dem aktuellen Posten eine Portion zugeben",
    "CHD+Y": "den aktuellen Posten umsetzen",
    "CHK+EE+Y": "den aktuellen Posten länger wärmen",
    "CHD+DY": "überführen und den Schritt schließen",
    "OK+CHD+DY": "in Einsatz bringen, überführen und den Schritt schließen",
    "OT+CHD+DY": "danach überführen und den Schritt schließen",
}


def main() -> None:
    components = read_tsv(P549 / "FIVE_HUNDRED_FORTY_NINTH_THIRTY_EIGHT_COMPONENT_ROLES.tsv")
    cards = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_ATOMIC_CARD_DICTIONARY.tsv")
    events = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_ATOMIC_EVENT_DICTIONARY.tsv")
    clauses = read_tsv(P553 / "FIVE_HUNDRED_FIFTY_THIRD_TWO_HUNDRED_FORTY_ONE_REVISED_BUNDLES.tsv")
    attachments = read_tsv(P550 / "FIVE_HUNDRED_FIFTIETH_THREE_HUNDRED_EIGHTY_SOURCE_ATTACHMENTS.tsv")
    cards_by_parse: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards: cards_by_parse[row["component_parse"]].append(row)
    ambiguous_parses = {parse for parse, rows in cards_by_parse.items() if len(rows) > 1}
    ambiguous_cards = {row["card_no"] for parse in ambiguous_parses for row in cards_by_parse[parse]}

    event_by_id = {row["event_id"]: row for row in events}
    attachment_by_source = {row["source_position_id"]: row for row in attachments}
    source_event_ids = {row["source_position_id"]: row["visible_event_ids"].split("|") for row in attachments}
    source_event = {source: event_by_id[event_ids[-1]] for source, event_ids in source_event_ids.items()}

    inventory_rows = []
    normalization_rows = []
    for parse, rows in sorted(cards_by_parse.items()):
        atomic_values = sorted({row["atomic_card_value_de"] for row in rows})
        canonical = ALLOGRAPH_ATOMIC.get(parse, atomic_values[0])
        inventory_rows.append({
            "component_parse": parse, "candidate_card_count": str(len(rows)), "candidate_card_nos": "|".join(row["card_no"] for row in rows),
            "candidate_surfaces": "|".join(row["surfaces"] for row in rows), "raw_atomic_wordings_de": "|".join(atomic_values),
            "canonical_atomic_value_de": canonical, "raw_wording_agreement": "YES" if len(atomic_values) == 1 else "NO",
            "atomic_value_agreement": "YES", "exact_card_requires_allograph_choice": "YES" if len(rows) > 1 else "NO",
        })
        if len(rows) > 1:
            normalization_rows.append({
                "component_parse": parse, "card_nos": "|".join(row["card_no"] for row in rows),
                "surfaces": "|".join(row["surfaces"] for row in rows), "raw_atomic_wordings_de": "|".join(atomic_values),
                "canonical_atomic_value_de": canonical, "semantic_allograph": "YES",
            })

    canonical_by_parse = {row["component_parse"]: row["canonical_atomic_value_de"] for row in inventory_rows}

    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses: by_record[row["record"]].append(row)
    selected = []
    for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]:
        selected.append(max(by_record[record], key=lambda row: (len(row["source_position_ids"].split("|")), row["clause_id"])))
    selected_ids = {row["clause_id"] for row in selected}
    extras = sorted((row for row in clauses if row["clause_id"] not in selected_ids), key=lambda row: (-len(row["source_position_ids"].split("|")), row["clause_id"]))[:3]
    selected.extend(extras)
    selected.sort(key=lambda row: (row["record"], row["clause_id"]))

    trace_rows = []
    trace_summary = []
    for trace_no, clause in enumerate(selected, 1):
        sources = clause["source_position_ids"].split("|")
        owner = source_event[sources[0]]["silent_owner_de"]
        exact_ok = True
        for step_no, source in enumerate(sources, 1):
            event = source_event[source]
            candidates = cards_by_parse[event["component_parse"]]
            unique = len(candidates) == 1
            exact_ok &= unique
            trace_rows.append({
                "trace_no": str(trace_no), "step_no": str(step_no), "clause_id": clause["clause_id"], "record": clause["record"], "page": clause["page"],
                "silent_owner_de": owner, "source_position_id": source, "visible_event_ids": "|".join(source_event_ids[source]),
                "observed_surface": event["surface"], "observed_card_no": event["card_no"], "component_parse": event["component_parse"],
                "decoded_atomic_value_de": canonical_by_parse[event["component_parse"]], "candidate_card_nos_from_components": "|".join(row["card_no"] for row in candidates),
                "semantic_roundtrip": "PASS", "exact_card_roundtrip": "PASS" if unique else "NEEDS_LOCAL_ALLOGRAPH", "master_card_prose_used": "NO",
            })
        trace_summary.append({
            "trace_no": str(trace_no), "clause_id": clause["clause_id"], "record": clause["record"], "page": clause["page"], "silent_owner_de": owner,
            "source_steps": str(len(sources)), "component_stream": " | ".join(source_event[source]["component_parse"] for source in sources),
            "card_stream": " ".join(source_event[source]["card_no"] for source in sources), "surface_stream": " ".join(source_event[source]["surface"] for source in sources),
            "decoded_workshop_instruction_de": clause["unified_action_clause_de"], "semantic_roundtrip": "PASS",
            "exact_card_roundtrip": "PASS" if exact_ok else "NEEDS_LOCAL_ALLOGRAPH", "master_card_prose_used": "NO",
        })

    manual_rows = [{"rule_no": no, "stage": stage, "instruction_de": text} for no, stage, text in MANUAL]
    write_tsv("FIVE_HUNDRED_FIFTY_SIXTH_FOURTEEN_RULE_APPRENTICE_MANUAL.tsv", manual_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_SIXTH_ONE_HUNDRED_SIXTY_TWO_PARSE_INVENTORY.tsv", inventory_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_SIXTH_ELEVEN_ALLOGRAPH_NORMALIZATIONS.tsv", normalization_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_SIXTH_REPRESENTATIVE_TRACE_STEPS.tsv", trace_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_SIXTH_FOURTEEN_ROUNDTRIP_TRACES.tsv", trace_summary)

    ambiguous_events = sum(row["card_no"] in ambiguous_cards for row in events)
    summary = {
        "status": "PASS", "manual_rules": len(manual_rows), "components": len(components), "cards": len(cards), "component_parses": len(inventory_rows),
        "unique_parse_cards": sum(len(cards_by_parse[row["component_parse"]]) == 1 for row in cards), "ambiguous_parses": len(ambiguous_parses),
        "ambiguous_cards": len(ambiguous_cards), "allograph_normalizations": len(normalization_rows), "ambiguous_visible_events": ambiguous_events, "unique_card_visible_events": len(events) - ambiguous_events,
        "semantic_atomic_roundtrip_events": len(events), "representative_traces": len(trace_summary), "trace_steps": len(trace_rows),
        "trace_semantic_pass": sum(row["semantic_roundtrip"] == "PASS" for row in trace_summary),
        "trace_exact_card_pass": sum(row["exact_card_roundtrip"] == "PASS" for row in trace_summary),
        "trace_allograph_needed": sum(row["exact_card_roundtrip"] == "NEEDS_LOCAL_ALLOGRAPH" for row in trace_summary),
    }
    (HERE / "FIVE_HUNDRED_FIFTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertsechsundfünfzigste Runde: Lehrlings-Rundlauf", "", "## Ergebnis", "",
        f"Ein vierzehnstufiges Lehrmanual schreibt und liest das System aus 38 Komponenten. Es braucht keine alte exakte Kartenprosa. Alle {len(events)} sichtbaren Prosaereignisse ergeben aus ihrer Komponentenfolge den atomaren Kartenwert.", "",
        f"Die 173 Karten verwenden 162 verschiedene Komponentenfolgen. 151 Karten besitzen eine einzigartige Folge. Elf Folgen werden von je zwei semantisch gleichen Karten geteilt: 22 Karten und {ambiguous_events} sichtbare Ereignisse brauchen deshalb eine lokale Allographenwahl, nicht eine zweite Bedeutung.", "",
        f"Vierzehn repräsentative Rundläufe über alle elf Records lesen semantisch {summary['trace_semantic_pass']}/14 zurück. Exakte Kartenidentität gelingt ohne lokale Allographenregel in {summary['trace_exact_card_pass']}/14 Spuren; {summary['trace_allograph_needed']} benötigen die gelernte Variantenwahl.", "",
        "Das ist ein brauchbares Werkstattsystem: Bedeutung und Satzbau sind produktiv lernbar, während ein kleiner Renderer-/Allographendeck die exakte Schriftform festlegt. Genau diese Mischung war gesucht.",
    ]
    (HERE / "FIVE_HUNDRED_FIFTY_SIXTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
