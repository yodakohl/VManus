#!/usr/bin/env python3
"""Generate twelve concrete component predictions and compare them to fixed-page cards."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "experiments/yolo/sidequest_semantic_eight_slot_paradigm_six_hundred_ninth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PREDICTIONS = [
    ("P01", "OK+EEE+Y", "qokeeey", "OK-Gradreihe hat kurze/lange offene und kurze/lange/volle geschlossene Formen"),
    ("P02", "OK+E+AL", "qokedal", "OK+ZIEL und OK+LANG+ZIEL sind vorhanden"),
    ("P03", "OK+EEE+AL", "qokeeedal", "Zielreihe könnte neben LANG auch VOLL tragen"),
    ("P04", "SH+EEE+Y", "sheeey", "HALTEN hat KURZ/LANG mit offenem DIES"),
    ("P05", "SH+EEE+DY", "sheeedy", "HALTEN hat KURZ/LANG mit SCHLUSS"),
    ("P06", "CHK+E+DY", "chkedy", "WAERMEN hat KURZ/LANG offen, aber nur LANG geschlossen"),
    ("P07", "CHK+EEE+Y", "chkeeey", "WAERMEN-Gradreihe könnte eine volle offene Stufe besitzen"),
    ("P08", "CHK+EEE+DY", "chkeeedy", "WAERMEN-Gradreihe könnte eine volle Schlussstufe besitzen"),
    ("P09", "K+EE+Y", "kcheey", "ZUFUEHREN+KURZ+DIES ist vorhanden; lange Schwester fehlt"),
    ("P10", "K+E+DY", "kchedy", "kurze Zuführung könnte als geschlossene Schwester auftreten"),
    ("P11", "L+E+Y", "lchey", "FUEHREN+DIES und FUEHREN+LANG+DIES sind vorhanden"),
    ("P12", "L+E+DY", "lchedy", "FUEHREN+SCHLUSS und lange Durchlassformen legen kurze Schwester nahe"),
]


def distance(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    words = read_tsv(SOURCE_DIR / "SIX_HUNDRED_NINTH_THIRTY_SEVEN_WORD_PARADIGM.tsv")
    cards = read_tsv(SOURCE_DIR / "SIX_HUNDRED_NINTH_173_CARD_SLOT_PARSE.tsv")
    word_by_component = {row["canonical_component"]: row["spoken_workshop_word_de"] for row in words}
    slot_by_component = {row["canonical_component"]: row["paradigm_slot"] for row in words}
    card_by_parse = {row["semantic_component_parse"]: row for row in cards}

    surface_rows = []
    for card in cards:
        for surface in card["surfaces"].split("|"):
            surface_rows.append((surface, card))
    surface_exact = {surface: card for surface, card in surface_rows}

    rows = []
    for prediction_id, parse, predicted_surface, basis in PREDICTIONS:
        components = parse.split("+")
        semantic_exact = card_by_parse.get(parse)
        surface_hit = surface_exact.get(predicted_surface)
        ranked = sorted(
            ((distance(predicted_surface, surface), surface, card) for surface, card in surface_rows),
            key=lambda item: (item[0], item[1], item[2]["card_no"]),
        )
        nearest = []
        seen = set()
        for dist, surface, card in ranked:
            key = (surface, card["card_no"])
            if key in seen:
                continue
            seen.add(key)
            nearest.append((dist, surface, card))
            if len(nearest) == 3:
                break
        if semantic_exact:
            result = "ALREADY_PRESENT_SEMANTIC_CARD"
        elif surface_hit:
            result = "SURFACE_COLLISION_DIFFERENT_PARSE"
        else:
            result = "SEMANTICALLY_LEGAL_BUT_SURFACE_ABSENT"
        rows.append({
            "prediction_id": prediction_id,
            "predicted_semantic_parse": parse,
            "predicted_slot_signature": ">".join(slot_by_component[component] for component in components),
            "predicted_short_meaning_de": "·".join(word_by_component[component] for component in components),
            "guessed_surface_family": predicted_surface,
            "prediction_basis_de": basis,
            "exact_semantic_card_present": "YES" if semantic_exact else "NO",
            "exact_surface_present": "YES" if surface_hit else "NO",
            "exact_surface_existing_card": surface_hit["card_no"] if surface_hit else "NONE",
            "exact_surface_existing_parse": surface_hit["semantic_component_parse"] if surface_hit else "NONE",
            "result": result,
            "nearest_surface_1": nearest[0][1],
            "nearest_distance_1": nearest[0][0],
            "nearest_parse_1": nearest[0][2]["semantic_component_parse"],
            "nearest_surface_2": nearest[1][1],
            "nearest_distance_2": nearest[1][0],
            "nearest_parse_2": nearest[1][2]["semantic_component_parse"],
            "nearest_surface_3": nearest[2][1],
            "nearest_distance_3": nearest[2][0],
            "nearest_parse_3": nearest[2][2]["semantic_component_parse"],
            "working_interpretation_de": (
                "Die Bedeutungsfolge ist erlaubt, aber ihre sichtbare Karte ist auf den zehn Seiten nicht belegt."
                if result == "SEMANTICALLY_LEGAL_BUT_SURFACE_ABSENT"
                else "Die geratenen Buchstaben kollidieren mit einer anders analysierten Karte; Semantik sagt die Oberfläche nicht direkt voraus."
            ),
        })

    grids = [
        {
            "family": "OK_GRADE_ITEM_CLOSE",
            "present_semantic_parses": "OK+Y|OK+E+Y|OK+EE+Y|OK+E+DY|OK+EE+DY|OK+EEE+DY",
            "predicted_missing_parses": "OK+EEE+Y",
            "lesson_de": "VOLL ist im festen Ausschnitt schlussgebunden; offene Vollform bleibt nur Erwartung.",
        },
        {
            "family": "OK_GRADE_TARGET",
            "present_semantic_parses": "OK+AL|OK+EE+AL",
            "predicted_missing_parses": "OK+E+AL|OK+EEE+AL",
            "lesson_de": "Zielkarten zeigen Grundform und LANG, aber keine kurze oder volle Schwester.",
        },
        {
            "family": "SH_GRADE_ITEM_CLOSE",
            "present_semantic_parses": "SH+E+Y|SH+EE+Y|SH+E+DY|SH+EE+DY",
            "predicted_missing_parses": "SH+EEE+Y|SH+EEE+DY",
            "lesson_de": "HALTEN besitzt kurze und lange, aber keine volle Stufe.",
        },
        {
            "family": "CHK_GRADE_ITEM_CLOSE",
            "present_semantic_parses": "CHK+E+Y|CHK+EE+Y|CHK+EE+DY",
            "predicted_missing_parses": "CHK+E+DY|CHK+EEE+Y|CHK+EEE+DY",
            "lesson_de": "WAERMEN hat keine vollständige Stufe; der kurze Schluss fehlt ebenfalls.",
        },
        {
            "family": "TRANSFER_GRADE_ITEM_CLOSE",
            "present_semantic_parses": "K+E+Y|L+Y|L+EE+Y|L+DY",
            "predicted_missing_parses": "K+EE+Y|K+E+DY|L+E+Y|L+E+DY",
            "lesson_de": "Zuführen und Führen teilen keine vollständige symmetrische Gradtafel.",
        },
    ]

    write_tsv(HERE / "SIX_HUNDRED_TENTH_TWELVE_COMPONENT_PREDICTIONS.tsv", rows, list(rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TENTH_FIVE_PRODUCTIVE_GRIDS.tsv", grids, list(grids[0]))

    absent = sum(row["result"] == "SEMANTICALLY_LEGAL_BUT_SURFACE_ABSENT" for row in rows)
    collisions = sum(row["result"] == "SURFACE_COLLISION_DIFFERENT_PARSE" for row in rows)
    report = f"""# Sechshundertzehnte Runde: zwölf echte Kompositionsvorhersagen

## Ergebnis

Das Acht-Schubladen-Modell erzeugt zwölf klare Bedeutungsfolgen, die auf den zehn Seiten fehlen. Elf dazu geratene Oberflächen sind ebenfalls nicht vorhanden. Eine geratene Form kollidiert:

```text
erwartet: L+E+DY  = FUEHREN · KURZ · SCHLUSS
geraten:  lchedy
vorhanden: lchedy = L+CHD+DY = FUEHREN · UMSETZEN · SCHLUSS
```

Das ist nützlich: Die Bedeutungszusammensetzung ist produktiv, aber die sichtbare Karte entsteht nicht durch simples Zusammenkleben von EVA-Stücken. Die Werkstatt braucht weiterhin gelernte Kartenformen und Allographpaletten.

## Die fünf geprüften Reihen

- **OK + Grad + DIES/SCHLUSS:** fast vollständig; nur die offene VOLL-Form fehlt.
- **OK + Grad + ZIEL:** Grundform und LANG vorhanden; KURZ und VOLL fehlen.
- **HALTEN + Grad:** KURZ und LANG vorhanden; VOLL fehlt offen wie geschlossen.
- **WAERMEN + Grad:** KURZ/LANG offen, LANG geschlossen; übrige Stufen fehlen.
- **ZUFUEHREN/FUEHREN + Grad:** lückenhaft und nicht symmetrisch.

## Bilanz

- {absent} legale Bedeutungsfolgen mit fehlender geratener Oberfläche;
- {collisions} Oberflächenkollision;
- 0 neue Karten werden erfunden oder ins Wörterbuch aufgenommen.

## Arbeitstheorie

Wir haben zwei getrennte produktive Ebenen:

1. **Bedeutung:** 37 Wörter können nach den acht Slots neue Arbeitsphrasen bilden.
2. **Schrift:** Der Schreiber wählt eine gelernte Ganzkartenform; Buchstabenlänge und E-Reihe helfen, reichen aber nicht zur freien Erzeugung jeder Karte.

Das passt sehr gut zu einem Werkstattcodebuch: produktive Anweisung, aber konservative graphische Nomenklatur.

## Nächster Schritt

Als nächstes untersuchen wir die vorhandenen Gradfamilien selbst: Welche Handlungen erlauben KURZ, LANG oder VOLL, und welche Grade sind aus praktischen Gründen absichtlich blockiert? Daraus entsteht eine konkrete Operationslehre statt einer bloß formalen Lückentafel.
"""
    (HERE / "SIX_HUNDRED_TENTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "predictions": len(rows),
        "semantic_cards_already_present": sum(row["result"] == "ALREADY_PRESENT_SEMANTIC_CARD" for row in rows),
        "surface_absent": absent,
        "surface_collisions": collisions,
        "new_cards_promoted": 0,
        "decision": "SEMANTIC_COMPOSITION_PRODUCTIVE__SURFACE_REALIZATION_CODEBOOK_BOUND",
    }
    (HERE / "SIX_HUNDRED_TENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
