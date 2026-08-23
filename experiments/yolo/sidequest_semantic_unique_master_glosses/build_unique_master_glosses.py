#!/usr/bin/env python3
"""Give every creative master card a distinct, short workshop teaching gloss."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MASTER = ROOT / "experiments/yolo/sidequest_semantic_master_reader_codebook"
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# tuple id -> (unique teaching gloss, concrete contrast)
REFINEMENTS: dict[str, tuple[str, str]] = {
    "07913ef9b1fb773cd325": ("angesetzten Inhalt überführen; Schluss", "OK+CHED: erst ansetzen, dann den Inhalt überführen"),
    "259b2b3b0bf859882e2c": ("Posten überführen; Schluss", "unmarkierte geschlossene CHED-Überführung"),
    "87411f84689b4f93a303": ("Umsetzung ansetzen; Schluss", "OK+CHD: einen eigenen Umsetzgang ansetzen"),
    "d225b7a7b95da7aee437": ("weitergeführten Posten überführen; Schluss", "D+CHD nach bereits laufender Weiterführung"),
    "27d97af8c96eb056c2e6": ("Ansatzgefäß", "Gefäß für den weitergeführten Pflanzenansatz"),
    "b38d70daefd663d74625": ("Sammelgefäß", "Gefäß vor dem längeren Sammelschritt"),
    "df1098831679a8ad1b39": ("Mischgefäß", "Gefäß für Wurzelteil und Wasserzulauf"),
    "433713294b25b0a12f66": ("zur Ablaufstelle führen", "L+CHED+AL bezeichnet den Weg zum Ablaufziel"),
    "5eff216ba51fbfb21f22": ("Durchlassöffnung", "kurze L+S-Portkarte zwischen Ansatz und Klarlauf"),
    "a48efd6c4491a046ba78": ("anschließender Arbeitsposten", "OT+CHY nimmt den anschließenden bearbeiteten Posten"),
    "faf321940aed922846a9": ("nächster Teilposten", "OT+Y wählt den nächsten allgemeinen Teilposten"),
    "4de12cf322dfb76ded1e": ("nächsten Posten überführen; Schluss", "OT+CHED schließt die folgende Überführung"),
    "601b77449028deed39de": ("Folgegang vollziehen; Schluss", "OT+CHD schließt den nächsten ganzen Arbeitsgang"),
    "232195d6ff2f326322f7": ("Fortsetzung ansetzen", "OK+OL setzt die Fortsetzung als neuen Gang an"),
    "322281bd391aa621f568": ("weiterlaufenden Posten aufnehmen", "OK+CH+OL nimmt einen bereits laufenden Posten auf"),
    "b5df9126607030b95175": ("klarer Auszug", "Stoffkarte des gewonnenen Klarlaufs"),
    "d4a31dbcf1ed6d9e5aa9": ("Klarlauf zugeben", "T+SHEY bringt Klarlauf in den nächsten Gang"),
    "276a7c2d74d1143446f4": ("aktuellen Posten ansetzen", "OK+Y setzt den unmittelbar gemeinten Posten an"),
    "9ad66e67803a12e745de": ("Posten zur Weiterbearbeitung ansetzen", "OK+CH+Y setzt einen eingehüllten Bearbeitungsposten an"),
    "7f68f60279efe6b28cd7": ("Waschgang abschließen", "RSHE+DY ist ein vollständiger geschlossener Waschgang"),
    "be0974b366c981dc1eef": ("Waschgang beginnen", "LSH eröffnet die folgende Waschsequenz"),
    "0ec6a45e2950e8e7061d": ("diese Zutat zur Stelle bringen", "HO+AL+Y trägt die aktuell ausgewählte Zutat zum Ziel"),
    "428a5e3662aa57b4b256": ("Zutat an die Arbeitsstelle geben", "HO+AL setzt eine neue Zutat an der Arbeitsstelle ab"),
    "bc4f1f5c006c74a4d26d": ("kurz absetzen lassen; Schluss", "SHED+Grad I schließt nach kurzem Absetzen"),
    "db167f8e9b53eefb58f8": ("Absetzgang ansetzen; Schluss", "OK+SHED setzt einen eigenen Absetzgang an"),
    "204b04837409088c48f9": ("bereiten Posten weiterführen", "OL+CTH+Y führt den aktuell bereiten Posten weiter"),
    "a8f891de626fc00028e9": ("bereitgestellten Gang fortsetzen", "CTH+OL setzt den bereitgestellten Gang als Ganzes fort"),
    "0bdc8b6db811b4e67a63": ("aus diesem Posten", "AR+Y verweist ausdrücklich auf den aktuellen Posten"),
    "4d4559019a961b834aa1": ("aus dem Ansatz", "freie AR-Quellkarte greift auf den aktiven Ansatz zurück"),
    "1b1ffdd869fb1429ad03": ("Fortsetzung abschließen", "OL+DY beendet die laufende Fortsetzung"),
    "28ffbc88b97772a75f1e": ("weiterüberführen; Schluss", "OL+CHED führt beim Fortsetzen zugleich über"),
    "9bb7122b386ebbc6138f": ("kurz weiterbearbeiten", "K+E+OL bezeichnet kurze fortgesetzte Bearbeitung"),
    "a06244ef1f2b37ca44c1": ("kurz weiterleiten", "T+E+OL bezeichnet kurze fortgesetzte Leitung"),
    "2c1a5fd92b9e3c762242": ("länger erwärmen und offen halten", "CHK+Grad II+offenes Y lässt den Wärmgang offen"),
    "f0db6d30cd34f4cb2a4d": ("diesen Posten länger warm halten", "CHK+Grad II bindet die Wärme an den aktuellen Posten"),
    "5e8441397e7c0faf042b": ("diesen Posten überführen", "CHED+CHY überführt den markierten Bearbeitungsposten"),
    "6f7ff8287eddf4da9fdb": ("laufenden Posten umsetzen", "CHD~CHED+Y setzt den allgemein laufenden Posten um"),
    "1496a731803a9f48d2e1": ("vom vorigen Gang weiterführen", "R+OL übernimmt aus dem vorausliegenden Gang"),
    "c205570c49d4d93c23d3": ("auf dem Arbeitsweg weiterleiten", "Q+OL+KY hält die Fortsetzung auf dem gebundenen Weg"),
}


def main() -> None:
    cards = read_tsv(MASTER / "MASTER_173_CARD_DICTIONARY.tsv")
    surfaces = read_tsv(MASTER / "SURFACE_230_READER_KEY.tsv")
    events = read_tsv(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    phrases = read_tsv(PROSE / "CLOSED_116_PHRASES.tsv")

    card_by_tuple = {row["joint_tuple_id"]: row for row in cards}
    master_id_by_tuple = {row["joint_tuple_id"]: row["master_card_id"] for row in cards}
    unique_by_tuple = {
        row["joint_tuple_id"]: REFINEMENTS.get(row["joint_tuple_id"], (row["short_meaning_de"], "bereits eindeutiger Werkstattwert"))[0]
        for row in cards
    }

    dictionary_rows: list[dict[str, object]] = []
    resolution_rows: list[dict[str, object]] = []
    for row in cards:
        tuple_id = row["joint_tuple_id"]
        changed = tuple_id in REFINEMENTS
        new_value, contrast = REFINEMENTS.get(tuple_id, (row["short_meaning_de"], "bereits eindeutiger Werkstattwert"))
        dictionary_rows.append({
            **row,
            "previous_short_meaning_de": row["short_meaning_de"],
            "unique_short_meaning_de": new_value,
            "gloss_revision": "DISAMBIGUATED_DUPLICATE" if changed else "UNCHANGED_UNIQUE",
            "teaching_contrast_de": contrast,
        })
        if changed:
            resolution_rows.append({
                "previous_duplicate_gloss_de": row["short_meaning_de"],
                "master_card_id": row["master_card_id"],
                "joint_tuple_id": tuple_id,
                "master_head_form": row["master_head_form"],
                "registered_surface_family": row["registered_surface_family"],
                "component_reading": row["component_reading"],
                "unique_short_meaning_de": new_value,
                "teaching_contrast_de": contrast,
                "observed_occurrences": row["observed_occurrences"],
                "dossiers": row["dossiers"],
            })
    dictionary_fields = list(cards[0]) + ["previous_short_meaning_de", "unique_short_meaning_de", "gloss_revision", "teaching_contrast_de"]
    resolution_fields = [
        "previous_duplicate_gloss_de", "master_card_id", "joint_tuple_id", "master_head_form",
        "registered_surface_family", "component_reading", "unique_short_meaning_de", "teaching_contrast_de",
        "observed_occurrences", "dossiers",
    ]
    write_tsv(OUT / "UNIQUE_173_MASTER_DICTIONARY.tsv", dictionary_rows, dictionary_fields)
    write_tsv(OUT / "THIRTY_NINE_GLOSS_DISAMBIGUATIONS.tsv", resolution_rows, resolution_fields)

    surface_rows: list[dict[str, object]] = []
    for row in surfaces:
        surface_rows.append({
            **row,
            "previous_short_meaning_de": row["short_meaning_de"],
            "unique_short_meaning_de": unique_by_tuple[row["joint_tuple_id"]],
            "gloss_revision": "DISAMBIGUATED_DUPLICATE" if row["joint_tuple_id"] in REFINEMENTS else "UNCHANGED_UNIQUE",
        })
    surface_fields = list(surfaces[0]) + ["previous_short_meaning_de", "unique_short_meaning_de", "gloss_revision"]
    write_tsv(OUT / "UNIQUE_230_SURFACE_READER_KEY.tsv", surface_rows, surface_fields)

    event_rows: list[dict[str, object]] = []
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        tuple_id = event["joint_tuple_id"]
        card = card_by_tuple[tuple_id]
        out = {
            "event_serial": event["event_serial"],
            "event_id": event["event_id"],
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "locus": event["locus"],
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "joint_tuple_id": tuple_id,
            "master_card_id": master_id_by_tuple[tuple_id],
            "surface_display": event["surface_display"],
            "master_head_form": card["master_head_form"],
            "component_reading": card["component_reading"],
            "previous_short_meaning_de": card["short_meaning_de"],
            "unique_short_meaning_de": unique_by_tuple[tuple_id],
            "gloss_revision": "DISAMBIGUATED_DUPLICATE" if tuple_id in REFINEMENTS else "UNCHANGED_UNIQUE",
            "step_closure_role": event["step_closure_role"],
        }
        event_rows.append(out)
        events_by_statement[event["statement_id"]].append(out)
    event_fields = [
        "event_serial", "event_id", "record_unit_id", "page", "locus", "field_id", "statement_id",
        "joint_tuple_id", "master_card_id", "surface_display", "master_head_form", "component_reading",
        "previous_short_meaning_de", "unique_short_meaning_de", "gloss_revision", "step_closure_role",
    ]
    write_tsv(OUT / "UNIQUE_381_EVENT_INTERLINEAR.tsv", event_rows, event_fields)

    statement_rows: list[dict[str, object]] = []
    for phrase in phrases:
        statement_events = events_by_statement[phrase["statement_id"]]
        changed = [row for row in statement_events if row["gloss_revision"] == "DISAMBIGUATED_DUPLICATE"]
        statement_rows.append({
            "statement_id": phrase["statement_id"],
            "record_unit_id": phrase["record_unit_id"],
            "page": phrase["page"],
            "loci": phrase["loci"],
            "event_count": phrase["event_count"],
            "surface_sequence": phrase["surface_sequence"],
            "master_head_sequence": " ".join(str(row["master_head_form"]) for row in statement_events),
            "unique_literal_sequence_de": " -> ".join(str(row["unique_short_meaning_de"]) for row in statement_events),
            "fluent_workshop_sentence_de": phrase["fluent_workshop_sentence_de"],
            "disambiguated_card_count": len(changed),
            "precision_notes_de": " | ".join(
                f"{row['master_head_form']}: {row['previous_short_meaning_de']} -> {row['unique_short_meaning_de']}" for row in changed
            ) or "keine Änderung",
            "statement_status": "UNIQUE_CARD_DEFAULTS_COMPLETE",
        })
    statement_fields = [
        "statement_id", "record_unit_id", "page", "loci", "event_count", "surface_sequence",
        "master_head_sequence", "unique_literal_sequence_de", "fluent_workshop_sentence_de",
        "disambiguated_card_count", "precision_notes_de", "statement_status",
    ]
    write_tsv(OUT / "UNIQUE_116_STATEMENT_EDITION.tsv", statement_rows, statement_fields)

    readable = [
        "# Elf Records mit eindeutigen Meisterwerten", "",
        "Jede Karte besitzt hier einen eigenen Werkstatt-Merkwert. Die flüssige Lesung bleibt gut lesbar; die Präzisionszeile zeigt, welche vormals gleichen Glossen nun unterschieden werden.", "",
    ]
    current_record = None
    for row in statement_rows:
        if row["record_unit_id"] != current_record:
            current_record = row["record_unit_id"]
            readable += [f"## {current_record} · {row['page']}", ""]
        readable += [
            f"### {row['statement_id']}", "",
            f"- Meisterfolge: `{row['master_head_sequence']}`",
            f"- Eindeutige Kartenwerte: {row['unique_literal_sequence_de']}",
            f"- Lesung: {row['fluent_workshop_sentence_de']}",
            f"- Präzisierung: {row['precision_notes_de']}", "",
        ]
    (OUT / "ELEVEN_RECORD_UNIQUE_MASTER_READING.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    group_counts = Counter(row["previous_duplicate_gloss_de"] for row in resolution_rows)
    affected_events = sum(1 for row in event_rows if row["gloss_revision"] == "DISAMBIGUATED_DUPLICATE")
    affected_statements = sum(1 for row in statement_rows if int(row["disambiguated_card_count"]) > 0)
    report = [
        "# Eindeutige Meisterglossen", "",
        "## Ergebnis", "",
        f"Das bisherige 173-Kartenbuch enthielt 18 breite Kurzglossen für 39 verschiedene Karten. Diese 21 Überschüsse sind nun als konkrete Werkstattnuancen aufgelöst. Alle 173 Meisterkarten besitzen einen eigenen kurzen Merkwert; keine Karte muss mehr dieselbe Defaultglosse wie eine andere tragen.", "",
        f"Die Änderung betrifft {affected_events} der 381 Prosaereignisse und {affected_statements} der 116 Aussagen. Oberfläche, Meisterkopf, Komponentenbau, Kartenfolge und bestehende flüssige Lesung bleiben stehen; nur der Merkzettel wird genauer.", "",
        "## Wichtigste neue Unterscheidungen", "",
        "- `os`, `oykchor` und `ly` sind Mischgefäß, Ansatzgefäß und Sammelgefäß.",
        "- `cheey/shey` ist der klare Auszug; `tshey` ist die Zugabe dieses Klarlaufs.",
        "- `lsho` beginnt den Waschgang; `rshedy` schließt ihn ab.",
        "- `choky` setzt den aktuellen Posten an; `chokchy` setzt ihn ausdrücklich zur Weiterbearbeitung an.",
        "- Die vier geschlossenen CHED/CHD-Karten unterscheiden allgemeines Überführen, Überführen eines angesetzten Inhalts, Ansetzen eines Umsetzgangs und Abschluss eines bereits weitergeführten Postens.", "",
        "## Werkstattgebrauch", "",
        "Diese Unterschiede sind als Lehrmeister-Merkwörter gedacht. Ein Lehrling kann damit ähnliche Karten auseinanderhalten und beim Rücklesen eine konkrete Handlung nennen, statt vier verschiedene Zeichen mit demselben deutschen Etikett zu lernen.", "",
        "Die Bedeutungen bleiben die kreative Arbeitstheorie dieser zehn Seiten. Die Eindeutigkeit ist eine bewusste Codebuchentscheidung, keine Behauptung, dass natürliche Sprache nie Synonyme haben dürfe.", "",
        f"Aufgelöste Altgruppen: {dict(group_counts)}.",
    ]
    (OUT / "UNIQUE_MASTER_GLOSS_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    content_names = [
        "UNIQUE_173_MASTER_DICTIONARY.tsv", "THIRTY_NINE_GLOSS_DISAMBIGUATIONS.tsv",
        "UNIQUE_230_SURFACE_READER_KEY.tsv", "UNIQUE_381_EVENT_INTERLINEAR.tsv",
        "UNIQUE_116_STATEMENT_EDITION.tsv", "ELEVEN_RECORD_UNIQUE_MASTER_READING.md",
        "UNIQUE_MASTER_GLOSS_REPORT.md",
    ]
    summary = {
        "status": "BUILT",
        "master_cards": len(dictionary_rows),
        "unique_master_glosses": len({row["unique_short_meaning_de"] for row in dictionary_rows}),
        "old_duplicate_groups": len(group_counts),
        "disambiguated_cards": len(resolution_rows),
        "affected_events": affected_events,
        "affected_statements": affected_statements,
        "surface_rows": len(surface_rows),
        "event_rows": len(event_rows),
        "statement_rows": len(statement_rows),
        "files_sha256": {name: sha(OUT / name) for name in content_names},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
