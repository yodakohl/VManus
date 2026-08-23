#!/usr/bin/env python3
"""Reanalyse the final nineteen whole cards and rebuild the prose edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_reduced_complete_edition"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


BRIDGES = [
    {"bridge_id": "BR01", "visible_core": "DCH", "meaning_de": "voriger Posten", "role_de": "Rückbezug", "master_card_ids": "MC142", "combination": "DCH+OL = vorigen Posten fortsetzen", "teaching_note_de": "dchol und schol sind zwei sichtbare Fassungen derselben Rückbezugskarte"},
    {"bridge_id": "BR02", "visible_core": "CFH", "meaning_de": "auswringen", "role_de": "Druckoperation", "master_card_ids": "MC129", "combination": "CFH+Y = aktuellen Posten auswringen", "teaching_note_de": "F steht in diesem Paar für den Druckgang"},
    {"bridge_id": "BR03", "visible_core": "CPH", "meaning_de": "nachseihen", "role_de": "zweiter Durchgang", "master_card_ids": "MC156", "combination": "CPH+Y = aktuellen Posten nachseihen", "teaching_note_de": "P kontrastiert im lokalen Paar mit CFH"},
    {"bridge_id": "BR04", "visible_core": "DCHE", "meaning_de": "Wurzel", "role_de": "bildgebundener Stoffkern", "master_card_ids": "MC071", "combination": "DCHE+Y = Wurzel als aktuellen Posten nehmen", "teaching_note_de": "der Bildbesitzer konkretisiert den Stoffkern"},
    {"bridge_id": "BR05", "visible_core": "LDDY", "meaning_de": "befestigen und schließen", "role_de": "lokaler Endgang", "master_card_ids": "MC164", "combination": "OK+Y+LDDY = aktuellen Posten ansetzen und befestigen", "teaching_note_de": "LDDY wird als ein gelernter Endgang behandelt"},
    {"bridge_id": "BR06", "visible_core": "SK", "meaning_de": "ausgießen", "role_de": "Flüssigkeitsbewegung", "master_card_ids": "MC089", "combination": "SK+AR = vom Ausgang ausgießen", "teaching_note_de": "AR liefert die Quelle; SK nur die Bewegung"},
    {"bridge_id": "BR07", "visible_core": "DAN", "meaning_de": "anwenden", "role_de": "Anwendungsoperation", "master_card_ids": "MC068", "combination": "OT+DAN = danach anwenden", "teaching_note_de": "OT liefert allein die Folgereihenfolge"},
    {"bridge_id": "BR08", "visible_core": "AM", "meaning_de": "verwahren", "role_de": "Speicheroperation", "master_card_ids": "MC160", "combination": "AL+AM = am Ziel verwahren", "teaching_note_de": "AL liefert die Zieladresse"},
]


REANALYSIS = {
    "MC142": ("COMPOSED_WITH_BRIDGE_STEM", "DCH+OL", "VORIGEN POSTEN FORTSETZEN", "vorigen Posten fortsetzen", "Nimm den vorigen Posten wieder auf", "DCH Rückbezug plus bekanntes OL Fortsetzung"),
    "MC012": ("LEARNED_WHOLE_CARD", "LOCAL_WHOLE", "ZUSATZ", "Zusatz", "Gib den Zusatz zu", "einzige weiterhin ungeteilte Sachkarte"),
    "MC129": ("COMPOSED_WITH_BRIDGE_STEM", "CFH+Y", "AKTUELLEN POSTEN AUSWRINGEN", "aktuellen Posten auswringen", "Wringe den aktuellen Posten aus", "CFH Druckkern plus Y aktueller Posten"),
    "MC099": ("COMPOSED_EXISTING_ATOMS", "EE+CKH+HO+CLOSE", "EINGANGSPOSTEN LÄNGER FÜHREN; SCHLUSS", "länger auftragen; Schluss", "Führe den Eingangsposten länger und schließe", "EE Grad plus CKH Weg plus HO Eingangsposten plus Schluss"),
    "MC156": ("COMPOSED_WITH_BRIDGE_STEM", "CPH+Y", "AKTUELLEN POSTEN NACHSEIHEN", "aktuellen Posten nachseihen", "Seihe den aktuellen Posten nach", "CPH zweiter Seihgang plus Y aktueller Posten"),
    "MC071": ("COMPOSED_WITH_BRIDGE_STEM", "DCHE+Y", "WURZEL ALS AKTUELLEN POSTEN", "Wurzel als aktueller Posten", "Nimm die Wurzel als aktuellen Posten", "DCHE bildgebundener Stoffkern plus Y"),
    "MC138": ("COMPOSED_EXISTING_ATOMS", "SHED+E+CLOSE", "KURZ ABSETZEN; SCHLUSS", "kurz absetzen; Schluss", "Lass kurz absetzen und schließe", "dieselbe Absetzreihe wie shedy; führendes d bleibt Rahmen"),
    "MC124": ("COMPOSED_EXISTING_ATOMS", "L+E+CLOSE", "KURZ ABFÜHREN; SCHLUSS", "kurz abführen; Schluss", "Führe kurz ab und schließe", "L Ausweg plus E Kurzgrad plus Schluss"),
    "MC118": ("COMPOSED_EXISTING_ATOMS", "L+Y", "AKTUELLEN POSTEN ABFÜHREN", "aktuellen Posten abführen", "Führe den aktuellen Posten ab", "direkte Verbindung der bekannten L- und Y-Karten"),
    "MC027": ("COMPOSED_EXISTING_ATOMS", "Y+KCH+OR", "AKTUELLEN ANSATZ BEARBEITEN", "aktuellen Ansatz bearbeiten", "Bearbeite den aktuellen Ansatz", "Y Posten plus KCH Arbeitsgang plus OR Ansatz"),
    "MC052": ("COMPOSED_EXISTING_ATOMS", "KCH+E+Y", "AKTUELLEN POSTEN KURZ BEARBEITEN", "aktuellen Posten kurz bearbeiten", "Bearbeite den aktuellen Posten kurz", "dieselbe Komponentenfolge wie die kurze KCH-Karte"),
    "MC164": ("COMPOSED_WITH_BRIDGE_STEM", "OK+Y+LDDY", "AKTUELLEN POSTEN BEFESTIGEN; SCHLUSS", "aktuellen Posten befestigen; Schluss", "Befestige den aktuellen Posten und schließe", "OK und Y bleiben produktiv; nur LDDY ist gelernter Endgang"),
    "MC114": ("COMPOSED_EXISTING_ATOMS", "SH", "HALTEN", "halten", "Halte den aktuellen Posten", "die sichtbare Einzelkarte erhält denselben Wert wie das bekannte SH-Atom"),
    "MC089": ("COMPOSED_WITH_BRIDGE_STEM", "SK+AR", "VOM AUSGANG AUSGIESSEN", "vom Ausgang ausgießen", "Gieße vom Ausgang aus", "SK Bewegung plus AR Quelle"),
    "MC068": ("COMPOSED_WITH_BRIDGE_STEM", "OT+DAN", "DANACH ANWENDEN", "danach anwenden", "Wende danach an", "OT Folge plus DAN Anwendung"),
    "MC061": ("COMPOSED_EXISTING_ATOMS", "SH+KCH+CHD+CLOSE", "HALTEN, BEARBEITEN UND ÜBERTRAGEN; SCHLUSS", "im Arbeitsgang schwenken; Schluss", "Halte, bearbeite, übertrage und schließe", "bekannte Halte-, Arbeits- und Übertragungskerne erklären den Schwenkgang"),
    "MC160": ("COMPOSED_WITH_BRIDGE_STEM", "AL+AM", "AM ZIEL VERWAHREN", "am Ziel verwahren", "Verwahre am Ziel", "AL Ziel plus AM Speicheroperation"),
    "MC037": ("COMPOSED_EXISTING_ATOMS", "HO+CLOSE", "EINGANGSPOSTEN BEISEITESTELLEN; SCHLUSS", "Eingangsposten beiseitestellen; Schluss", "Stelle den Eingangsposten beiseite und schließe", "HO Eingangsposten plus Schluss; die alte Kaltlesung war zu eng"),
    "MC109": ("COMPOSED_EXISTING_ATOMS", "Y+E+TY", "KURZEN TEIL DES AKTUELLEN POSTENS NEHMEN", "kurzen Teil des aktuellen Postens nehmen", "Nimm einen kurzen Teil des aktuellen Postens", "Y aktueller Posten plus E Kurzgrad plus TY Teil"),
}


FLUENT_OVERRIDES = {
    "H1-S001": "Nimm die Wurzel als aktuellen Posten, halte den Ansatz bereit, nimm vom Ausgang, trenne einen Teil, gib ihn in den Träger, öffne den Wasserlauf, führe den nächsten Teil weiter und stelle auf den Vorgabewert ein.",
    "H2-S003": "Bearbeite den aktuellen Ansatz, führe den Ansatz weiter, halte den laufenden Posten auf der gewählten Stufe und stelle den Eingangswert ein.",
    "H3-S001": "Entnimm den Eingangsposten, führe ihn zum Ziel, wringe ihn aus, halte bis zum Vorgabewert, seihe den aktuellen Posten nach, lies den freigegebenen Wert, stelle ihn beiseite und schließe.",
    "H3-S003": "Nimm den vorigen Posten wieder auf, bearbeite den aktuellen Posten und stelle den Vorgabewert ein.",
    "H4-S002": "Stelle den Vorgabewert ein, übertrage den Posten und verwahre ihn am Ziel.",
    "H5-S002": "Nimm den vorigen Posten wieder auf, setze den aktuellen Eingangsposten an, führe ihn länger über die Zielstelle und schließe.",
    "H5-S003": "Halte den Eingangsposten, bearbeite ihn kurz und setze ihn erneut an.",
    "H5-S005": "Setze den Ansatz als Eingangsposten an, nimm den Auszug daraus und wende ihn danach an.",
    "B1-S002": "Stelle den Vorgabewert ein, öffne den Wasserlauf am Ziel, nimm vom Ausgang, führe weiter, gib einen Anteil, einen weiteren Anteil und den Zusatz zum Ziel, halte dort länger, übertrage und schließe.",
    "B1-S003": "Führe weiter, halte den Posten im Arbeitsgang, übertrage und schließe.",
    "B1-S006": "Gib einen gezählten Anteil und den Zusatz zu, leite den Posten durch und führe ihn zum Ziel.",
    "B1-S015": "Nimm einen kurzen Teil des aktuellen Postens, setze ihn an, übertrage und schließe.",
    "B1-S018": "Führe den aktuellen Posten ab, halte kurz, führe fort, stelle die Stufe ein, sammle länger und schließe.",
    "B2-S007": "Lass kurz absetzen und schließe.",
    "B4-S004": "Befestige den aktuellen Posten und schließe.",
    "B4-S011": "Stelle den Vorgabewert ein, wärme kurz, führe länger fort, gib einen Anteil zu, übertrage, führe weiter, führe kurz ab und schließe.",
    "B4-S016": "Gib einen weiteren Anteil zum Ziel, gieße ihn vom Ausgang aus, lass absetzen und schließe.",
    "B6-S001": "Sammle den aktuellen Posten länger, bearbeite ihn kurz, führe ihn zum Ziel, stelle den Vorgabewert ein, führe weiter, lege den Abdeckträger ein und führe den Posten zum Endziel.",
}


def main() -> None:
    source_cards = read_tsv(BASE / "IMPERATIVE_173_CARD_DICTIONARY.tsv")
    source_events = read_tsv(BASE / "IMPERATIVE_381_EVENT_TRACE.tsv")
    source_statements = read_tsv(BASE / "COMPLETE_116_RETRANSLATED_STATEMENTS.tsv")
    source_records = read_tsv(BASE / "ELEVEN_RECORD_REDUCED_SUMMARY.tsv")

    write_tsv(OUT / "EIGHT_LEARNED_BRIDGE_STEMS.tsv", BRIDGES, list(BRIDGES[0]))

    card_rows = []
    exception_rows = []
    for card in source_cards:
        mc = card["master_card_id"]
        if mc in REANALYSIS:
            new_class, atoms, nucleus, concrete, imperative, reason = REANALYSIS[mc]
            exception_rows.append({
                "master_card_id": mc,
                "master_head_form": card["master_head_form"],
                "registered_surface_family": card["registered_surface_family"],
                "prose_event_count": card["prose_event_count"],
                "old_class": card["composition_layer"],
                "old_atom_sequence": card["atom_sequence"],
                "old_nucleus_de": card["portable_nucleus_de"],
                "new_class": new_class,
                "new_atom_sequence": atoms,
                "new_nucleus_de": nucleus,
                "new_concrete_default_de": concrete,
                "new_imperative_de": imperative,
                "composition_reason_de": reason,
            })
        else:
            new_class = "PREVIOUSLY_COMPOSED"
            atoms = card["atom_sequence"]
            nucleus = card["portable_nucleus_de"]
            concrete = card["concrete_default_de"]
            imperative = card["imperative_phrase_de"]
            reason = "aus der ersten oder zweiten Ringsprache übernommen"
        card_rows.append({
            **card,
            "third_ring_class": new_class,
            "third_ring_atom_sequence": atoms,
            "third_ring_nucleus_de": nucleus,
            "third_ring_concrete_default_de": concrete,
            "third_ring_imperative_de": imperative,
            "third_ring_reason_de": reason,
        })
    write_tsv(OUT / "NINETEEN_EXCEPTION_REANALYSIS.tsv", exception_rows, list(exception_rows[0]))
    write_tsv(OUT / "COMPLETE_173_THIRD_RING_DICTIONARY.tsv", card_rows, list(card_rows[0]))

    card_by_id = {row["master_card_id"]: row for row in card_rows}
    event_rows = []
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in source_events:
        card = card_by_id[event["master_card_id"]]
        row = {
            **event,
            "third_ring_class": card["third_ring_class"],
            "third_ring_atom_sequence": card["third_ring_atom_sequence"],
            "third_ring_nucleus_de": card["third_ring_nucleus_de"],
            "third_ring_concrete_default_de": card["third_ring_concrete_default_de"],
            "third_ring_imperative_de": card["third_ring_imperative_de"],
        }
        event_rows.append(row)
        events_by_statement[event["statement_id"]].append(row)
    write_tsv(OUT / "COMPLETE_381_THIRD_RING_EVENT_TRACE.tsv", event_rows, list(event_rows[0]))

    statement_rows = []
    for statement in source_statements:
        sid = statement["statement_id"]
        statement_events = events_by_statement[sid]
        classes = {str(event["third_ring_class"]) for event in statement_events}
        if "LEARNED_WHOLE_CARD" in classes:
            status = "CONTAINS_ONE_LEARNED_WHOLE_CARD"
        elif "COMPOSED_WITH_BRIDGE_STEM" in classes:
            status = "COMPOSED_WITH_BRIDGE_STEM"
        else:
            status = "FULLY_COMPOSED_EXISTING_ATOMS"
        new_fluent = FLUENT_OVERRIDES.get(sid, statement["reduced_fluent_reading_de"])
        statement_rows.append({
            **statement,
            "third_ring_atom_chain": " | ".join(str(event["third_ring_atom_sequence"]) for event in statement_events),
            "third_ring_nucleus_chain_de": " → ".join(str(event["third_ring_nucleus_de"]) for event in statement_events),
            "third_ring_imperative_chain_de": "; ".join(str(event["third_ring_imperative_de"]) for event in statement_events),
            "third_ring_fluent_reading_de": new_fluent,
            "third_ring_statement_status": status,
            "bridge_stem_event_count": sum(event["third_ring_class"] == "COMPOSED_WITH_BRIDGE_STEM" for event in statement_events),
            "whole_card_event_count": sum(event["third_ring_class"] == "LEARNED_WHOLE_CARD" for event in statement_events),
            "third_ring_revision": "REVISED" if new_fluent != statement["reduced_fluent_reading_de"] else "UNCHANGED",
        })
    write_tsv(OUT / "COMPLETE_116_THIRD_RING_STATEMENTS.tsv", statement_rows, list(statement_rows[0]))

    statements_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for statement in statement_rows:
        statements_by_record[str(statement["record_unit_id"])].append(statement)
    source_record_by_id = {row["record_unit_id"]: row for row in source_records}
    record_lines = [
        "# Elf Records nach Zerlegung der letzten Ganzkarten",
        "",
        "Die Aussagen folgen dem aktuellen Karten- und Komponentenstand; Zeilenwechsel bleiben reine Schreibraumgrenzen.",
        "",
    ]
    record_rows = []
    for record_id in source_record_by_id:
        source_record = source_record_by_id[record_id]
        rows = statements_by_record[record_id]
        continuous = " ".join(str(row["third_ring_fluent_reading_de"]) for row in rows)
        status_counts = Counter(str(row["third_ring_statement_status"]) for row in rows)
        record_rows.append({
            "record_unit_id": record_id,
            "title_de": source_record["title_de"],
            "pages": source_record["pages"],
            "statement_count": len(rows),
            "event_count": sum(int(row["event_count"]) for row in rows),
            "fully_existing_atom_statements": status_counts["FULLY_COMPOSED_EXISTING_ATOMS"],
            "bridge_stem_statements": status_counts["COMPOSED_WITH_BRIDGE_STEM"],
            "whole_card_statements": status_counts["CONTAINS_ONE_LEARNED_WHOLE_CARD"],
            "continuous_third_ring_reading_de": continuous,
        })
        record_lines += [f"## {record_id} — {source_record['title_de']} · {source_record['pages']}", "", continuous, ""]
        for row in rows:
            record_lines.append(f"- **{row['statement_id']} · {row['loci']}** — `{row['surface_sequence']}`")
            record_lines.append(f"  {row['third_ring_fluent_reading_de']}")
        record_lines.append("")
    write_tsv(OUT / "ELEVEN_RECORD_THIRD_RING_SUMMARY.tsv", record_rows, list(record_rows[0]))
    (OUT / "ELEVEN_RECORD_THIRD_RING_READING.md").write_text("\n".join(record_lines).rstrip() + "\n", encoding="utf-8")

    card_class_counts = Counter(row["third_ring_class"] for row in card_rows)
    event_class_counts = Counter(row["third_ring_class"] for row in event_rows)
    statement_status_counts = Counter(row["third_ring_statement_status"] for row in statement_rows)
    report = f"""# Anatomie der letzten neunzehn Ganzkarten

## Ergebnis

Die vermeintlichen neunzehn Ausnahmen zerfallen in drei Schichten. Zehn Karten lassen sich vollständig aus den bereits bekannten Atomen lesen. Acht Karten brauchen genau einen kurzen gelernten Fachkern, verbinden ihn aber regelhaft mit `Y`, `OL`, `AR`, `AL`, `OT`, `OK` oder einem Schluss. Nur **`dl = Zusatz`** bleibt als ungeteilte Sachkarte übrig.

Damit sind jetzt {card_class_counts['PREVIOUSLY_COMPOSED'] + card_class_counts['COMPOSED_EXISTING_ATOMS']} von 173 Kartentypen vollständig mit den bestehenden Atomen lesbar, weitere {card_class_counts['COMPOSED_WITH_BRIDGE_STEM']} als Mischkomposition und genau {card_class_counts['LEARNED_WHOLE_CARD']} als Ganzkarte. Auf Ereignisebene sind {event_class_counts['PREVIOUSLY_COMPOSED'] + event_class_counts['COMPOSED_EXISTING_ATOMS']} von 381 vollständig atomar, {event_class_counts['COMPOSED_WITH_BRIDGE_STEM']} benutzen einen Fachkern und {event_class_counts['LEARNED_WHOLE_CARD']} bleiben Ganzkarten.

## Die stärksten Reparaturen

- `ly = L+Y`: nicht mehr ein frei erfundenes Sammelgefäß, sondern den aktuellen Posten abführen.
- `dshedy = SHED+E+CLOSE`: nicht mehr Frischwasser, sondern kurz absetzen und schließen.
- `lkedy = L+E+CLOSE`: nicht mehr Nachwaschen, sondern kurz abführen und schließen.
- `qekey = KCH+E+Y`: nicht mehr das isolierte Adjektiv roh, sondern den aktuellen Posten kurz bearbeiten.
- `ytey = Y+E+TY`: nicht mehr das unanalysierte Füllen, sondern einen kurzen Teil des aktuellen Postens nehmen.
- `oykchor = Y+KCH+OR`: nicht mehr ein erfundenes Gefäß, sondern den aktuellen Ansatz bearbeiten.
- `cheeckhody = EE+CKH+HO+CLOSE`: den Eingangsposten länger führen und den Schritt schließen.
- `sh = SH`: der sichtbare Einzelträger erhält denselben Haltewert wie der bekannte Kern; der Pflanzenbesitzer kann lokal weiterhin den Stängel liefern.

## Gelernte Fachkerne

Die acht Brücken sind klein genug für ein Werkstattcodebuch: `DCH` voriger Posten, `CFH` auswringen, `CPH` nachseihen, `DCHE` Wurzel, `LDDY` befestigen und schließen, `SK` ausgießen, `DAN` anwenden und `AM` verwahren. Sie sind keine neue universelle Sprachmorphologie. Sie sind die kurze Nomenklatorschicht, die neben der produktiven Kürzungsgrammatik gelernt wird.

## Neue Gesamtbilanz

Von den 116 Aussagen bestehen {statement_status_counts['FULLY_COMPOSED_EXISTING_ATOMS']} vollständig aus den bestehenden Atomen, {statement_status_counts['COMPOSED_WITH_BRIDGE_STEM']} enthalten einen der acht Fachkerne und nur {statement_status_counts['CONTAINS_ONE_LEARNED_WHOLE_CARD']} enthalten die letzte Ganzkarte `dl`. Die elf Records sind mit dieser strengeren Stammlesung vollständig neu gesetzt.
"""
    (OUT / "EXCEPTION_ANATOMY_REPORT.md").write_text(report, encoding="utf-8")

    content_names = [
        "EIGHT_LEARNED_BRIDGE_STEMS.tsv", "NINETEEN_EXCEPTION_REANALYSIS.tsv",
        "COMPLETE_173_THIRD_RING_DICTIONARY.tsv", "COMPLETE_381_THIRD_RING_EVENT_TRACE.tsv",
        "COMPLETE_116_THIRD_RING_STATEMENTS.tsv", "ELEVEN_RECORD_THIRD_RING_SUMMARY.tsv",
        "ELEVEN_RECORD_THIRD_RING_READING.md", "EXCEPTION_ANATOMY_REPORT.md",
    ]
    summary = {
        "status": "BUILT",
        "bridge_stems": len(BRIDGES),
        "reanalyzed_cards": len(exception_rows),
        "master_cards": len(card_rows),
        "prose_events": len(event_rows),
        "statements": len(statement_rows),
        "records": len(record_rows),
        "card_class_counts": dict(card_class_counts),
        "event_class_counts": dict(event_class_counts),
        "statement_status_counts": dict(statement_status_counts),
        "source_sha256": {
            "base_cards": sha256(BASE / "IMPERATIVE_173_CARD_DICTIONARY.tsv"),
            "base_events": sha256(BASE / "IMPERATIVE_381_EVENT_TRACE.tsv"),
            "base_statements": sha256(BASE / "COMPLETE_116_RETRANSLATED_STATEMENTS.tsv"),
            "base_records": sha256(BASE / "ELEVEN_RECORD_REDUCED_SUMMARY.tsv"),
        },
        "output_sha256": {name: sha256(OUT / name) for name in content_names},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
