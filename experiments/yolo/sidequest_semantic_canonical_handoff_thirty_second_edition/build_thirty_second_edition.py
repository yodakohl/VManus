#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


SOURCES = {
    "surface_dictionary": ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_487_SURFACE_DICTIONARY.tsv",
    "event_ledger": ROOT / "experiments/yolo/sidequest_semantic_stem_aligned_twentieth_edition/TWENTIETH_776_EVENT_BINDING.tsv",
    "reading_units": ROOT / "experiments/yolo/sidequest_semantic_stem_aligned_twentieth_edition/TWENTIETH_258_UNIT_TRANSLATIONS.tsv",
    "owner_statements": ROOT / "experiments/yolo/sidequest_semantic_owner_filled_twenty_first_edition/TWENTY_FIRST_116_OWNER_FILLED_PROSE.tsv",
    "component_deck": ROOT / "experiments/yolo/sidequest_semantic_apprentice_roundtrip_twenty_third_edition/TWENTY_THIRD_COMPONENT_DECK.tsv",
    "source_clauses": ROOT / "experiments/yolo/sidequest_semantic_clause_chain_twenty_fifth_edition/TWENTY_FIFTH_254_SOURCE_CLAUSES.tsv",
    "noun_load": ROOT / "experiments/yolo/sidequest_semantic_noun_load_twenty_sixth_edition/TWENTY_SIXTH_116_NOUN_LOAD_AUDIT.tsv",
    "balanced_records": ROOT / "experiments/yolo/sidequest_semantic_balanced_continuous_twenty_seventh_edition/TWENTY_SEVENTH_11_BALANCED_RECORDS.tsv",
    "event_idioms": ROOT / "experiments/yolo/sidequest_semantic_idiom_phrasebook_twenty_eighth_edition/TWENTY_EIGHTH_EVENT_IDIOMS.tsv",
    "scribe_copies": ROOT / "experiments/yolo/sidequest_semantic_scribe_idiom_copybook_twenty_ninth_edition/TWENTY_NINTH_68_SCRIBE_IDIOM_COPIES.tsv",
    "new_dictations": ROOT / "experiments/yolo/sidequest_semantic_new_dictations_thirtieth_edition/THIRTIETH_12_NEW_DICTATIONS.tsv",
    "balanced_dossiers": ROOT / "experiments/yolo/sidequest_semantic_balanced_dossiers_thirty_first_edition/THIRTY_FIRST_FOUR_BALANCED_DOSSIERS.tsv",
}

purposes = {
    "surface_dictionary": "487 sichtbare Formen und ihre aktuelle Karten-/Kernlesung",
    "event_ledger": "vollständige Bindung aller 776 sichtbaren Gruppen",
    "reading_units": "116 Prosa-Aussagen plus 142 Astro-Loci",
    "owner_statements": "sichtbarer Besitzer für jede Prosa-Aussage",
    "component_deck": "56 Einträge des Lehrkastens",
    "source_clauses": "254 kurze Handlungsklauseln",
    "noun_load": "Trennung von Karten-, Besitzer- und Kreativnomen",
    "balanced_records": "bevorzugte elf fortlaufende Prosa-Records",
    "event_idioms": "17 wiederkehrende Kartenwendungen",
    "scribe_copies": "vier Schreiberprofile auf den Wendungen",
    "new_dictations": "zwölf neue, nur aus vorhandenen Karten gebaute Übungen",
    "balanced_dossiers": "vier WHEN-WHAT-HOW-Gesamtfälle",
}

artifact_rows = []
for name, path in SOURCES.items():
    rows = read(path)
    artifact_rows.append(
        {
            "layer": name,
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": digest(path),
            "data_rows": len(rows),
            "purpose_de": purposes[name],
        }
    )
write(HERE / "THIRTY_SECOND_ACTIVE_LAYER_MAP.tsv", list(artifact_rows[0]), artifact_rows)

deck = read(SOURCES["component_deck"])
idioms = read(SOURCES["event_idioms"])
records = read(SOURCES["balanced_records"])
dossiers = read(SOURCES["balanced_dossiers"])

quick = [
    "# Schnellkarte der aktuellen Schreibertheorie",
    "",
    "## Schreibweg",
    "",
    "1. sichtbaren Besitzer zeigen; 2. längste gelernte Karte prüfen;",
    "3. Handlung, Ordnung, Menge, Richtung und Grad setzen; 4. häufige Wendung",
    "sprechen; 5. lokale Schreiberoberfläche wählen; 6. nur an Karten- oder",
    "Besitzergrenze abschließen.",
    "",
]
by_layer = defaultdict(list)
for row in deck:
    by_layer[row["layer"]].append(row)
for layer in ("COMMON", "BOUND", "PROCESS", "TABLE_LOCAL", "LEARNED_BODY", "WHOLE_CARD"):
    quick.extend([f"## {layer}", ""])
    quick.append("; ".join(f"`{row['symbol']}`={row['atomic_value_de']}" for row in by_layer[layer]) + ".")
    quick.append("")
quick.extend(["## Siebzehn häufige Kartenwendungen", ""])
for row in idioms:
    quick.append(f"- `{row['pattern']}` — {row['spoken_idiom_de']}")
quick.extend(
    [
        "",
        "## Vier Schreiber",
        "",
        "Bare Meisterhand; q-Zellenschreiber; s-Zeilenschreiber; kompakte Mischhand.",
        "Alle wählen zuerst dieselbe Exact-Karte und erst danach ihre registrierte Oberfläche.",
        "",
    ]
)
(HERE / "THIRTY_SECOND_QUICK_REFERENCE.md").write_text("\n".join(quick).rstrip() + "\n", encoding="utf-8")

theory = [
    "# Beste aktuelle Arbeitstheorie der zehn Seiten",
    "",
    "## In einem Satz",
    "",
    "Eine kleine Werkstatt benutzt ein bildgetragenes Fachregister aus produktiven",
    "Brevigrafen, gebundenen Stufen, wiederkehrenden Arbeitswendungen und gelernten",
    "Ganzkarten; Herbal nennt den sichtbaren Stoff, Biological den örtlichen Arbeitsgang",
    "und die Kreisblätter eine getrennte sichtbare Bedingungs- oder Nachschlageadresse.",
    "",
    "## Was ein Schreiber tut",
    "",
    "Der Meister zeigt zuerst Pflanze, Becken, Station, Stern, Ring oder Feld. Der",
    "Schreiber lässt diesen Besitzer unausgesprochen, wählt eine Exact-Karte oder baut",
    "eine bekannte Kernfolge, hängt Portion, Sollwert, Quelle, Ziel, Lauf, Grad und",
    "lokalen Schluss an und wählt erst danach die q-/s-/bare Schreiberform. Eine",
    "physische Zeile darf mitten durch denselben Arbeitsgang laufen.",
    "",
    "## Warum es lernbar bleibt",
    "",
    "Der Lehrkasten hat 56 kurze Werte, doch nur ein Teil ist global produktiv.",
    "Seltene Pflanzen-, Geräte- und Sternwerte werden aus dem Bild oder Meisterexemplar",
    "gelernt. Siebzehn häufige Kartenwendungen machen die Komposition sprechbar. Vier",
    "Schreiberprofile verändern die Oberfläche, nicht die Karte oder Bedeutung.",
    "",
    "## Elf bevorzugte Prosa-Records",
    "",
]
for row in records:
    theory.extend(
        [
            f"### {row['record_id']} — {row['title_de']}",
            "",
            row["balanced_continuous_reading_de"],
            "",
        ]
    )
theory.extend(["## Vier Benutzungsfälle", ""])
for row in dossiers:
    theory.extend(
        [
            f"### {row['dossier_id']} — {row['title_de']}",
            "",
            f"WHEN: {row['visible_condition_de']}",
            "",
            f"Ausgabe: {row['workshop_output_de']}",
            "",
            f"Rivale: {row['strongest_nonmedical_rival_de']}",
            "",
        ]
    )
theory.extend(
    [
        "## Was als Nächstes verbessert werden darf",
        "",
        "Neue Bedeutungen sollen entweder eine wiederkehrende Kartenfamilie kürzer",
        "machen, mehrere Klauseln desselben Records verbinden oder eine sichtbare",
        "Bildadresse besser nutzen. Sie sollen nicht bloß ein austauschbares Arznei-,",
        "Krankheits- oder Sternnomen hinzufügen. Neue Übungen dürfen vorhandene Karten",
        "kombinieren; weitere Manuskriptseiten bleiben außerhalb dieses Arbeitssets.",
    ]
)
(HERE / "THIRTY_SECOND_CANONICAL_WORKING_THEORY.md").write_text("\n".join(theory).rstrip() + "\n", encoding="utf-8")

summary = {
    "status": "PASS",
    "counts": {
        "bound_layers": len(artifact_rows),
        "deck_entries": len(deck),
        "event_idioms": len(idioms),
        "balanced_records": len(records),
        "balanced_dossiers": len(dossiers),
        "visible_surfaces": len(read(SOURCES["surface_dictionary"])),
        "visible_groups": len(read(SOURCES["event_ledger"])),
        "reading_units": len(read(SOURCES["reading_units"])),
        "source_clauses": len(read(SOURCES["source_clauses"])),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
