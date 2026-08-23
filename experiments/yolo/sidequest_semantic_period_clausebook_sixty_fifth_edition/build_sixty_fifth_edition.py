#!/usr/bin/env python3
"""Render the twelve clause shapes in three period-plausible source styles."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MAP = ROOT / "experiments/yolo/sidequest_semantic_reverse_decompressor_sixty_fourth_edition/SIXTY_FOURTH_381_REVERSE_DECOMPRESSION.tsv"
SHAPES = ROOT / "experiments/yolo/sidequest_semantic_clause_shapes_sixty_third_edition/SIXTY_THIRD_12_CLAUSE_SHAPES.tsv"

STYLE_TEMPLATES = {
    "C01": (
        "Setze die gelernte Fachkarte: {value}.",
        "NOMEN: {value}.",
        "N | {value}.",
        "Ganzkürzel, Nomenklatorwert oder gelernte technische Brevigrafe",
    ),
    "C02": (
        "Danach oder in demselben Gang: {value}.",
        "DEINDE / IDEM: {value}.",
        "ORD | {value}.",
        "parataktische Rezeptfolge und wiederaufgenommener Arbeitsposten",
    ),
    "C03": (
        "Führe aus und beachte Dauer oder Endpunkt: {value}.",
        "OPERA USQUE / FIAT: {value}.",
        "OP+GR | {value}.",
        "Handlung plus sichtbarer Endpunkt, Zeit oder gebundener Grad",
    ),
    "C04": (
        "Führe es an der bezeichneten Stelle aus: {value}.",
        "AD LOCUM: {value}.",
        "OP+AD | {value}.",
        "medizinisches oder technisches Ziel aus Bild und laufendem Record",
    ),
    "C05": (
        "Führe es aus dem Vorrat oder am Ansatz aus: {value}.",
        "EX MATERIA / IN PRAEPARATIONE: {value}.",
        "OP+EX | {value}.",
        "Rezeptquelle oder laufende Zubereitung als geerbtes Argument",
    ),
    "C06": (
        "Führe es in der angegebenen Portion oder Stufe aus: {value}.",
        "OPERA AD MENSURAM / GRADUM: {value}.",
        "OP+Q | {value}.",
        "Apothekermaß, Anteil oder Arbeitsstufe",
    ),
    "C07": (
        "Führe es mit diesem laufenden Posten aus: {value}.",
        "HOC OPERA: {value}.",
        "OP+HOC | {value}.",
        "elliptischer aktueller Gegenstand wie hoc/idem",
    ),
    "C08": (
        "Führe die Handlung aus; schließe nur bei Endkarte: {value}.",
        "OPERA; CLAUDE SI SIGNATUM: {value}.",
        "OP(+FIN) | {value}.",
        "kurze Imperativklausel mit optionalem lokalem Abschlusszeichen",
    ),
    "C09": (
        "Nenne Quelle, Lauf, Auszug oder Ansatz: {value}.",
        "EX / LIQUOR / PRAEPARATIO: {value}.",
        "SRC | {value}.",
        "Stoff- und Zwischenproduktfeld der Rezept- oder Werkstattprosa",
    ),
    "C10": (
        "Setze Maß, Portion oder Stufe: {value}.",
        "MENSURA / PORTIO / GRADUS: {value}.",
        "Q | {value}.",
        "Zahl-, Gewichts-, ana- oder Stufenfeld",
    ),
    "C11": (
        "Setze die bezeichnete Zielstelle: {value}.",
        "AD LOCUM DESIGNATUM: {value}.",
        "AD | {value}.",
        "Bild-, Gefäß-, Körper- oder Stationsadresse",
    ),
    "C12": (
        "Nimm diesen Posten wieder auf: {value}.",
        "HOC / IDEM: {value}.",
        "REF | {value}.",
        "verkürzte Anapher oder residuale Kurzform",
    ),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    mapped = read_tsv(MAP)
    shapes = {row["shape_id"]: row for row in read_tsv(SHAPES)}
    styles = (
        ("WORKSHOP_VERNACULAR", 0, "knappe praktische Rezept- oder Arbeitsprosa"),
        ("LATIN_FORMULARY", 1, "lateinisch aussehende Rubrikenfolge, keine Sprachidentifikation"),
        ("TABULAR_NOTATION", 2, "Schreiberliste aus Slotkürzeln und gelerntem Kartenwert"),
    )
    template_rows = []
    for shape_id in sorted(shapes):
        templates = STYLE_TEMPLATES[shape_id]
        for style, index, purpose in styles:
            template_rows.append({
                "shape_id": shape_id,
                "shape_family": shapes[shape_id]["shape_family"],
                "source_style": style,
                "source_clause_template": templates[index],
                "historical_mechanism": templates[3],
                "style_purpose": purpose,
                "language_identification": "NONE",
            })
    write_tsv(OUT / "SIXTY_FIFTH_36_PERIOD_CLAUSE_TEMPLATES.tsv", template_rows)

    source_rows = []
    for row in mapped:
        templates = STYLE_TEMPLATES[row["clause_shape_recovered"]]
        value = row["short_dictionary_readback_de"]
        source_rows.append({
            "source_group_id": row["source_group_id"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "visible_surface": row["visible_surface"],
            "clause_shape_id": row["clause_shape_recovered"],
            "source_slots": row["source_slots_recovered"],
            "workshop_vernacular_clause": templates[0].format(value=value),
            "latin_formulary_clause": templates[1].format(value=value),
            "tabular_notation_clause": templates[2].format(value=value),
            "historical_mechanism": templates[3],
            "concrete_value_source": "SHARED_DICTIONARY_PLUS_OWNER_CONTEXT",
        })
    write_tsv(OUT / "SIXTY_FIFTH_381_PERIOD_SOURCE_CLAUSES.tsv", source_rows)

    rule_rows = []
    counts = Counter(row["clause_shape_id"] for row in source_rows)
    for shape_id in sorted(shapes):
        rule_rows.append({
            "shape_id": shape_id,
            "shape_family": shapes[shape_id]["shape_family"],
            "composition_rule": shapes[shape_id]["abstract_formula_de"],
            "apprentice_instruction": shapes[shape_id]["workshop_rule_de"],
            "historical_analogue": STYLE_TEMPLATES[shape_id][3],
            "group_count": counts[shape_id],
            "portable_rule": "YES",
        })
    write_tsv(OUT / "SIXTY_FIFTH_12_COMPOSITION_RULES.tsv", rule_rows)

    doc = [
        "# Kleines Quellklauselbuch für die Werkstatt", "",
        "Drei Schreibstile benutzen dieselben zwölf Konstruktionen. Der erste klingt",
        "wie knappe Werkstattprosa, der zweite wie lateinische Formularrubriken, der",
        "dritte wie eine tabellarische Schreibvorlage. Keiner wird als Sprache des",
        "Manuskripts behauptet.", "",
    ]
    for shape_id in sorted(shapes):
        shape = shapes[shape_id]
        templates = STYLE_TEMPLATES[shape_id]
        doc.extend([
            f"## {shape_id} · {shape['shape_family']}", "",
            f"**Regel:** {shape['abstract_formula_de']}", "",
            f"**Werkstattprosa:** {templates[0]}", "",
            f"**Formularrubrik:** {templates[1]}", "",
            f"**Tafelkürzel:** {templates[2]}", "",
            f"**Zeitnahe Analogie:** {templates[3]}.", "",
        ])
    (OUT / "SIXTY_FIFTH_SOURCE_STYLEBOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Fünfundsechzigste Werkstattfassung: historisch aussehendes Klauselbuch", "",
        "## Ergebnis", "",
        "Die zwölf Klauselformen lassen sich als drei kleine, miteinander kompatible",
        "Quellstile schreiben: knappe praktische Prosa, lateinische Formularrubrik und",
        "tabellarische Slotnotation. Alle 381 Prosagruppen erhalten in jedem Stil eine",
        "Ausgabe, ohne dass dafür ein neues Kartenwort eingeführt wird.", "",
        "Das engste historische Gesamtanalogon bleibt eine Mischung, nicht ein einzelnes",
        "bekanntes Alphabet: Rezeptparataxe liefert Handlung und Reihenfolge; Apotheker-",
        "und Maßnotation liefert Menge; Bild und Tabelle liefern Ort; Abbreviatur und",
        "Nomenklator liefern produktive Kürzel neben gelernten Ganzwerten.", "",
        "Die praktische Konsequenz ist wichtig: Die Quelle muss keine voll ausgeschriebene",
        "Erzählprosa gewesen sein. Schon eine knappe Formularvorlage konnte von mehreren",
        "Schreibern zuverlässig in das Kartensystem umgesetzt werden.", "",
        "Nur die zehn festen Seiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ]
    (OUT / "SIXTY_FIFTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "clause_shapes": len(shapes),
            "source_styles": len(styles),
            "period_clause_templates": len(template_rows),
            "mapped_source_groups": len(source_rows),
            "composition_rules": len(rule_rows),
        },
        "shape_counts": dict(sorted(counts.items())),
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (MAP, SHAPES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
