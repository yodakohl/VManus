#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FAMILIES = ROOT / "experiments/yolo/sidequest_semantic_renderer_consolidated_card_deck_nine_hundred_forty_second/PASS942_47_LEARNED_CARD_FAMILIES.tsv"
PREDICTIONS = ROOT / "experiments/yolo/sidequest_semantic_predictive_paradigm_grid_nine_hundred_thirty_third/PASS933_MISSING_CELL_PREDICTIONS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RULES = [
    ("L01", "BILD", "Zuerst Bildbesitzer und Sachregister bestimmen; sie liefern Pflanze, Station, Gefäß, Figur oder Ringplatz."),
    ("L02", "KANAL", "Laufende Prosa spricht Arbeitsgänge; Text direkt an Figur oder Kreis spricht Adresse und Wert."),
    ("L03", "KARTENFAMILIE", "Die Komponentenfolge normalisieren; q-, s-, ch- und d-Schreiblagen dürfen dieselbe Karte darstellen."),
    ("L04", "GANZKARTE", "Ist die Komponentenfolge im 47-Karten-Deck, zuerst den gelernten Ganzkartenwert sprechen."),
    ("L05", "ZERLEGUNG", "Ist sie nicht im Deck, die 56 Kürzel von links nach rechts zusammensetzen."),
    ("L06", "REFERENT", "Y hält den aktuell gemeinten Posten; es schließt allein nichts ab."),
    ("L07", "SCHLUSS", "Nur die lizenzierte DY-Konstruktion beendet den aktuellen Zellenauftrag."),
    ("L08", "GRAD", "E, EE, EEE heißen kurz, länger, vollständig; derselbe Grad wirkt auf verschiedene Arbeitskerne."),
    ("L09", "START", "OK setzt den folgenden Posten oder Vorgang in Gang."),
    ("L10", "WAHL", "CH wählt den Teil oder die Klasse; S wählt eine Variante."),
    ("L11", "ZUTEILUNG", "K teilt Stoff oder Wert zu; AIN ist Einheit, AIIN Sollwert, IIN Stufe."),
    ("L12", "WEG", "AR nennt die Quelle, AL das Ziel, L die Verbindung und AIR den Lauf."),
    ("L13", "FOLGE", "OL setzt denselben Zug fort; OT nimmt den nächsten Zug oder Posten."),
    ("L14", "ZUSTAND", "SH hält, SHED setzt ab, CTH führt bis bereit, CHK bezeichnet eine Behandlung."),
    ("L15", "BILDREGISTER", "Im Bildkanal werden START, WAHL, ZIEL, QUELLE und GRAD als Platz- und Tabellenwerte gesprochen."),
    ("L16", "PROSA", "In Prosa Besitzer und Mengen zuerst, Handlung danach, Ziel/Lauf und Grad beim passenden Vorgang ergänzen."),
    ("L17", "ZEILE", "Eine Aussage darf über die physische Zeile hinausgehen; Zeilenbruch ist kein Pflichtschluss."),
    ("L18", "EXEMPLAR", "Seltene Sachnamen werden aus dem Seitenexemplar kopiert, ohne die produktiven Kürzel umzudeuten."),
    ("L19", "NEUBILDUNG", "Für eine neue Karte Stamm, Grad und Y oder DY wählen; ihre Bedeutung steht vor der Oberflächenform fest."),
    ("L20", "RUECKLESEN", "Zur Kontrolle den abstrakten Kartenwert zurücklesen und erst dann die bildgebundene Sachform einsetzen."),
]

DEMONSTRATIONS = [
    ("D01", "einen kurzen Stationsauftrag ansetzen und schließen", "OK+E+DY", "qokedy|okedy", "KURZ ANSETZEN; ENDE"),
    ("D02", "denselben Auftrag länger halten und schließen", "OK+EE+DY", "qokeedy|okeedy", "LAENGER ANSETZEN; ENDE"),
    ("D03", "eine Portion in Gang setzen", "OK+AIN", "qokain|okain|chokain", "EINE PORTION ANSETZEN"),
    ("D04", "aus der Quelle ansetzen", "OK+AR", "okar|qokar", "AUS DER QUELLE ANSETZEN"),
    ("D05", "den Posten zum Ziel bringen und dort ansetzen", "OK+AL", "qokal|okal|chokal", "AN DER ZIELSTELLE ANSETZEN"),
    ("D06", "den aktuellen Posten umsetzen", "CHD+Y", "chedy|chdy|chedchy", "DIESEN POSTEN UMSETZEN"),
    ("D07", "die folgende Einheit länger halten", "OT+EE+Y", "oteey|qoteey", "NAECHSTEN POSTEN LAENGER HALTEN"),
    ("D08", "denselben Zug beenden", "OL+DY", "oldy|qoldy", "DAMIT FORTFAHREN; ENDE"),
]


def main() -> None:
    families = read_tsv(FAMILIES)
    predictions = read_tsv(PREDICTIONS)
    rule_rows = [{"lesson": lesson, "short_name": name, "teaching_rule_de": rule} for lesson, name, rule in RULES]
    write_tsv(OUT / "PASS943_20_TEACHING_RULES.tsv", rule_rows, list(rule_rows[0]))

    demo_rows = [
        {
            "demonstration_id": ident,
            "source_prompt_de": prompt,
            "component_recipe": recipe,
            "licensed_surface_variants": surfaces,
            "readback_de": readback,
        }
        for ident, prompt, recipe, surfaces, readback in DEMONSTRATIONS
    ]
    write_tsv(OUT / "PASS943_8_COMPOSITION_DEMONSTRATIONS.tsv", demo_rows, list(demo_rows[0]))

    prediction_rows: list[dict[str, object]] = []
    for row in predictions:
        if row["status"] not in {"STRONG_PREDICTION", "WORKING_PREDICTION"}:
            continue
        prediction_rows.append({
            "root": row["root"],
            "grade": row["grade"],
            "endpoint": row["endpoint"],
            "component_recipe": row["component_recipe"],
            "strength": row["status"],
            "candidate_bare_surface": row["candidate_bare_surface"],
            "candidate_entry_surface": row["candidate_q_entry_surface"],
            "workshop_reading_de": row["workshop_prediction_de"],
            "image_reading_de": row["owner_address_prediction_de"],
            "apprentice_instruction_de": "Bedeutung aus der Komponentenfolge lesen; Oberflächenform erst danach nach Schreibplatz wählen.",
        })
    write_tsv(OUT / "PASS943_27_FORWARD_COMPOSITIONS.tsv", prediction_rows, list(prediction_rows[0]))

    book = [
        "# Ein kleines Werkstatt-Codebuch um 1420 — kreative Rekonstruktion",
        "",
        "Dieses Lehrblatt verbindet drei zeittypische Mechanismen: produktive Brevigraphen, häufige gelernte Fachformeln und eine örtliche Nomenklatorschicht für Bildnamen. Es ist keine Buchstabenchiffre: derselbe abstrakte Kartenwert wird in Prosa und Diagramm sachgerecht erweitert.",
        "",
        "## Unterricht in zwanzig Regeln",
        "",
    ]
    for row in rule_rows:
        book.append(f"{row['lesson']}. **{row['short_name']}** — {row['teaching_rule_de']}")
    book.extend(["", "## Die 47 gelernten Formelkarten", ""])
    for row in families:
        book.append(f"- `{row['component_recipe']}` → **{row['workshop_learned_value_de']}**; Formen: `{row['surface_variants']}`")
    book.extend(["", "## Acht Schreibübungen", ""])
    for row in demo_rows:
        book.append(f"- {row['source_prompt_de']} → `{row['component_recipe']}` → `{row['licensed_surface_variants']}` → **{row['readback_de']}**")
    (OUT / "PASS943_CA1420_HYBRID_TEACHING_BOOK.md").write_text("\n".join(book) + "\n", encoding="utf-8")

    report = f"""# Pass 943 — historisch plausible Lehrform des aktuellen Systems

## Arbeitsmodell

Das passendste Modell ist jetzt konkret: **Brevigraphe + gelernte Formelkarten +
örtlicher Bildnomenklator**. Ein Schreiber lernt zwanzig Regeln, 56 Kurzwerte
und 47 häufige Kartenfamilien. Das entspricht der Bauart gemischter
Kanzleicodes, medizinischer Kürzelpraxis und regelhaften Gradzeichen, ohne eine
dieser historischen Schriften direkt zu kopieren.

## Vorhersagefähigkeit

Die Regel erzeugt {len(prediction_rows)} derzeit fehlende, aber lesbare
Kompositionen. Beispielsweise ergibt `CHK+E+DY` schon vor einer Oberfläche
„kurz behandeln; Schritt schließen“; mögliche Schreibungen wären `chekedy`
oder `qchekedy`. Ebenso ergibt `SH+EEE+Y` „diesen Posten vollständig halten“.
Damit ist die Theorie nicht mehr nur ein rückwärts erfundenes Wörterbuch: Sie
kann neue Formelkarten bilden und lesen.

## Praktische Konsequenz

Der längere gelernte Kartenwert hat beim Sprechen Vorrang, doch seine
Komponenten bleiben für Neubildungen verfügbar. Bildbesitzer liefern konkrete
Pflanze, Station, Gefäß oder Himmelsplatz; sie müssen nicht als Textwort
wiederholt werden.
"""
    (OUT / "PASS943_REPORT.md").write_text(report, encoding="utf-8")
    summary = {"rules": len(rule_rows), "families": len(families), "demonstrations": len(demo_rows), "forward_compositions": len(prediction_rows), "outputs": {}}
    for path in sorted(OUT.glob("PASS943_*")):
        summary["outputs"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "PASS943_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
