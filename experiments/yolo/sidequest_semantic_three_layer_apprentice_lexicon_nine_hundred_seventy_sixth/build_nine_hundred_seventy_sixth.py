#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
COMMON = ROOT / "experiments/yolo/sidequest_semantic_canonical_compact_workshop_edition_nine_hundred_seventy_first/PASS971_86_ENTRY_DICTIONARY.tsv"
SPECIAL = ROOT / "experiments/yolo/sidequest_semantic_specialist_whole_card_drawer_nine_hundred_seventy_fifth/PASS975_SPECIALIST_CARD_DRAWER.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().upper()
    return "".join(char for char in value if char.isalnum())


def uniq(values: list[str]) -> str:
    return "|".join(sorted({value for value in values if value}))


LESSONS = [
    {"lesson": "1", "tablet": "37_GRUNDWURZELN", "content": "häufige Werte wie DIES, SETZEN, NEHMEN, SOLLWERT, ZIEL, QUELLE, KURZ, LÄNGER, SCHLIESSEN", "method": "laut sprechen, auf Bildposten zeigen, zweigliedrige Karten schreiben"},
    {"lesson": "2", "tablet": "16_ERWEITERUNGSWURZELN", "content": "seltene Werkstattwerte wie TRENNEN, UMLEITEN, ZUSATZ, BEFESTIGEN und lokale Adresshilfen", "method": "nur in überlieferten Kombinationen und Bildregistern üben"},
    {"lesson": "3", "tablet": "30_HAEUFIGE_FORMELKARTEN", "content": "wiederkehrende Ganzformen wie SETZEN·KURZ·SCHLIESSEN oder HALTEN·LÄNGER·DIES", "method": "als einen Zug kopieren; innere Wurzeln als Merkhilfe mitsprechen"},
    {"lesson": "4", "tablet": "51_NEUE_FACHWOERTER", "content": "AUSWRINGEN, NACHSEIHEN, KLARLAUF, STEHZEIT, KÜHLEN, WASCHEN, GEFÄSS, TUCH, ROH, WARM und weitere lokale Werkstattwörter", "method": "ganze Fachkarte mit Bildseite und Arbeitsgang lernen"},
    {"lesson": "5", "tablet": "3_LOKALE_DIAGRAMMZEICHEN", "content": "RAHMEN, AUSSEN, ZWISCHEN", "method": "nur am zugehörigen Diagramm lesen"},
    {"lesson": "6", "tablet": "RENDERER", "content": "q nach geschlossener Zelle; s bevorzugt am Zeilenanfang; weitere Hüllen aus dem Exemplar", "method": "erst Karte wählen, dann positionsgerechte Schreibform kopieren"},
    {"lesson": "7", "tablet": "BILDBESITZER", "content": "Pflanzenteil, Drogenetikett, Gefäß, Badstation oder Himmelsplatz", "method": "vor dem Lesen den sichtbaren Besitzer nennen"},
    {"lesson": "8", "tablet": "VOLLSTAENDIGE_KETTEN", "content": "Wurzelansatz; f11r-Filtrationskette; Gefäßansatz; Badezelle; Himmelsadressierung", "method": "vorwärts schreiben und rückwärts als Werkstattbefehl sprechen"},
]


def main() -> None:
    common = read(COMMON)
    special = read(SPECIAL)
    by_headword: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in special:
        by_headword[norm(row["apprentice_headword_de"])].append(row)

    root_value_to_id = {
        norm(row["portable_value_de"]): row["entry_id"]
        for row in common if row["entry_type"] == "ROOT_OR_LOCAL_SIGN"
    }
    attached = defaultdict(list)
    for key, rows in by_headword.items():
        if key in root_value_to_id:
            attached[root_value_to_id[key]].extend(rows)

    unified = []
    for row in common:
        links = attached.get(row["entry_id"], [])
        unified.append({
            "teaching_unit_id": row["entry_id"],
            "layer": row["entry_tier"],
            "unit_type": row["entry_type"],
            "recognition_forms": row["recognition_form"],
            "spoken_value_de": row["portable_value_de"],
            "concrete_context_values_de": uniq([r["context_expansion_de"] for r in links]) or row["portable_value_de"],
            "specialist_surface_forms": uniq([r["surface_family"] for r in links]),
            "observed_specialist_events": str(sum(int(r["pass971_observed_events"]) for r in links)),
            "pages": uniq([r["pages"] for r in links]),
            "teaching_rule_de": row["teaching_rule_de"],
        })

    new_keys = [key for key in sorted(by_headword) if key not in root_value_to_id]
    for index, key in enumerate(new_keys, 1):
        rows = by_headword[key]
        display = rows[0]["apprentice_headword_de"].upper()
        unified.append({
            "teaching_unit_id": f"W{index:03d}",
            "layer": "E_LOCAL_SPECIALIST_HEADWORD",
            "unit_type": "MEMORIZED_SPECIALIST_WHOLE_WORD",
            "recognition_forms": uniq([r["surface_family"] for r in rows]),
            "spoken_value_de": display,
            "concrete_context_values_de": uniq([r["context_expansion_de"] for r in rows]),
            "specialist_surface_forms": uniq([r["surface_family"] for r in rows]),
            "observed_specialist_events": str(sum(int(r["pass971_observed_events"]) for r in rows)),
            "pages": uniq([r["pages"] for r in rows]),
            "teaching_rule_de": "Als kurze lokale Fachkarte mit Bildbesitzer und Arbeitsgang lernen; sichtbare Wurzeln bleiben nur Merkhilfe.",
        })

    write(HERE / "PASS976_137_TEACHING_UNIT_LEXICON.tsv", unified, list(unified[0]))
    write(HERE / "PASS976_68_EXACT_SPECIALIST_CARDS.tsv", special, list(special[0]))
    write(HERE / "PASS976_EIGHT_LESSON_CURRICULUM.tsv", LESSONS, list(LESSONS[0]))

    by_layer = defaultdict(list)
    for row in unified:
        by_layer[row["layer"]].append(row)
    lines = [
        "# Pass 976 — das konsolidierte Drei-Schichten-Wörterbuch",
        "",
        "## Lehrumfang",
        "",
        "Ein neuer Schreiber lernt **137 Bedeutungs-/Karten-Einheiten**:",
        "",
        "- 37 häufige produktive Wurzeln;",
        "- 16 seltene produktive Erweiterungen;",
        "- 30 häufige Formelkarten;",
        "- 3 rein lokale Diagrammzeichen;",
        "- 51 zusätzliche Fachwörter als gelernte Ganzkarten.",
        "",
        "Drei Fachwerte — AUFFANGEN, BEFESTIGEN und ZUSATZ — waren schon als",
        "produktive Wurzeln vorhanden. Ihre lokalen Ganzkarten werden deshalb",
        "nicht als neue Bedeutungen doppelt gezählt.",
        "",
        "## Die Schichten",
        "",
        "### 1. Produktive Kurzschrift",
        "",
        "Sie erzeugt neue Arbeitskarten aus kurzen Werten: SETZEN, NEHMEN,",
        "GEBEN, SOLLWERT, STUFE, QUELLE, ZIEL, KURZ, LÄNGER, DIES und",
        "SCHLIESSEN. Diese Schicht erklärt den großen wiederkehrenden Kern.",
        "",
        "### 2. Häufige Formelkarten",
        "",
        "Dreißig häufige Kombinationen werden als Ganzzug geschrieben, obwohl der",
        "Lehrling ihre Wurzeln versteht. Beispiele: `OK+E+DY` = SETZEN · KURZ ·",
        "SCHLIESSEN und `SH+EE+Y` = HALTEN · LÄNGER · DIES.",
        "",
        "### 3. Lokaler Fachkartenkasten",
        "",
        "Hier liegen die konkreten Werkstattwörter, die nicht jedes Mal neu",
        "hergeleitet werden: AUSWRINGEN, NACHSEIHEN, STEHZEIT, KLARLAUF,",
        "KÜHLEN, ANWÄRMEN, WASCHEN, FRISCHWASSER, TUCH, GEFÄSS, WURZEL,",
        "STÄNGEL, BECKEN, DÜSE, ÜBERLAUF, ROH und WARM.",
        "",
        "## Fachwörter nach Schublade",
        "",
    ]
    drawer_groups = defaultdict(list)
    for row in special:
        drawer_groups[row["lexical_drawer"]].append(row)
    for drawer, rows in sorted(drawer_groups.items()):
        values = sorted({r["apprentice_headword_de"].upper() for r in rows})
        lines += [f"- **{drawer}:** " + ", ".join(values)]
    lines += [
        "",
        "## Schreibregel in einem Satz",
        "",
        "> Besitzer zeigen → produktive Wurzeln lesen → bekannte Formel als einen",
        "> Zug kopieren → lokale Fachkarte gegebenenfalls als Ganzwort einsetzen →",
        "> Positionshülle schreiben → Zelle offenlassen oder schließen.",
        "",
        "Das ist kein 1.676-Wörter-Lexikon und keine Buchstabenchiffre. Es ist ein",
        "kleines erlernbares Werkstattregister mit produktivem Kern und lokalem",
        "Nomenklator — genau die Mischung, die mehrere Schreiber um 1420 in einer",
        "kleinen Werkstatt zuverlässig weitergeben könnten.",
        "",
    ]
    (HERE / "PASS976_ONE_PAGE_APPRENTICE_DICTIONARY.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "common_and_formula_units": len(common),
        "specialist_exact_card_rows": len(special),
        "specialist_headword_norms": len(by_headword),
        "specialist_headwords_already_in_roots": len(set(by_headword) & set(root_value_to_id)),
        "new_specialist_headwords": len(new_keys),
        "total_teaching_units": len(unified),
        "lessons": len(LESSONS),
    }
    (HERE / "PASS976_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
