#!/usr/bin/env python3
"""Build the complete Pass-1021 repeated-portable-core inventory."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EDITION = (
    ROOT
    / "experiments/yolo/sidequest_semantic_cross_register_core_revision_one_thousand_eighteenth"
    / "PASS1018_627_REVISED_CORE_EDITION.tsv"
)
DICTIONARY = (
    ROOT
    / "experiments/yolo/sidequest_semantic_cross_register_core_revision_one_thousand_eighteenth"
    / "PASS1018_19_CORE_DICTIONARY.tsv"
)
EVENTS = (
    ROOT
    / "experiments/yolo/sidequest_semantic_twenty_two_page_statement_consolidation_one_thousand_ninth"
    / "PASS1009_4581_EVENT_LEDGER.tsv"
)

EXPECTED_RUNNING_PAGES = {
    "f10r", "f11r", "f13r", "f17r", "f18r", "f55v", "f56r",
    "f67r2", "f68r1", "f71v", "f72r", "f75r",
    "f76r", "f77r", "f81v", "f82r", "f83r", "f88r", "f88v", "f89r",
}

RULE_EXPANSIONS = {
    "CH": "äußere Einheit nehmen; darin die aktive Untereinheit nehmen",
    "OL": "den äußeren Gang fortsetzen; darin den inneren Gang fortsetzen",
    "AR": "den äußeren Ausgang wählen; darin den lokalen Ausgang wählen",
    "AL": "den äußeren Zielort wählen; darin den lokalen Zielort wählen",
    "Y": "den Besitzerreferenten halten; darin den aktiven Unterreferenten halten",
    "OR": "die äußere Einheit öffnen; darin die aktive Untereinheit öffnen",
    "OK": "die äußere Einheit setzen; darin den aktiven Unterposten setzen",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary_rows = read_tsv(DICTIONARY)
    assert len(dictionary_rows) == 19
    core_values = {row["root"]: row["pass1018_value_de"] for row in dictionary_rows}
    portable_cores = set(core_values)

    event_rows = read_tsv(EVENTS)
    running_events = [row for row in event_rows if row["event_role"] == "RUNNING_STATEMENT"]
    assert len(running_events) == 3888
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in running_events:
        events_by_statement[row["statement_id"]].append(row)

    edition_rows = read_tsv(EDITION)
    assert len(edition_rows) == 627
    assert {row["physical_page"] for row in edition_rows} == EXPECTED_RUNNING_PAGES
    assert sum(int(row["event_count"]) for row in edition_rows) == 3888

    occurrences: list[dict[str, object]] = []
    duplicate_events = 0
    triple_count = 0
    aligned_events = 0

    for statement in edition_rows:
        statement_id = statement["statement_id"]
        surfaces = statement["surface_sequence"].split()
        recipes = statement["component_sequence"].split(" | ")
        ledger = events_by_statement[statement_id]
        assert len(surfaces) == len(recipes) == len(ledger) == int(statement["event_count"])
        assert all(row["physical_page"] == statement["physical_page"] for row in ledger)
        assert surfaces == [row["surface"] for row in ledger]
        aligned_events += len(surfaces)

        statement_has_duplicate = False
        for card_index, (surface, recipe, event) in enumerate(zip(surfaces, recipes, ledger)):
            atoms = recipe.split("+")
            card_pairs: list[tuple[int, str]] = []
            for atom_index in range(len(atoms) - 1):
                atom = atoms[atom_index]
                if atom == atoms[atom_index + 1] and atom in portable_cores:
                    card_pairs.append((atom_index, atom))
                    if atom_index + 2 < len(atoms) and atoms[atom_index + 2] == atom:
                        triple_count += 1
            if not card_pairs:
                continue
            duplicate_events += 1
            statement_has_duplicate = True
            assert len(card_pairs) == 1, (statement_id, surface, recipe, card_pairs)

            atom_index, core = card_pairs[0]
            marked_atoms = atoms[:atom_index] + [f"[{core}>{core}]"] + atoms[atom_index + 2 :]
            occurrences.append(
                {
                    "duplicate_id": "",
                    "core": core,
                    "core_value_de": core_values[core],
                    "double_scope_reading_de": RULE_EXPANSIONS[core],
                    "event_id": event["event_id"],
                    "physical_page": statement["physical_page"],
                    "register": statement["register"],
                    "statement_id": statement_id,
                    "locus": event["locus"],
                    "owner_de": statement["visible_owner_or_namespace_de"],
                    "card_ordinal_in_statement": card_index + 1,
                    "surface_card": surface,
                    "component_recipe": recipe,
                    "marked_duplicate_recipe": "+".join(marked_atoms),
                    "duplicate_atom_ordinal": atom_index + 1,
                    "left_atom": atoms[atom_index - 1] if atom_index else "CARD_START",
                    "right_atom": atoms[atom_index + 2] if atom_index + 2 < len(atoms) else "CARD_END",
                    "previous_card_surface": surfaces[card_index - 1] if card_index else "STATEMENT_START",
                    "previous_card_recipe": recipes[card_index - 1] if card_index else "STATEMENT_START",
                    "next_card_surface": surfaces[card_index + 1] if card_index + 1 < len(surfaces) else "STATEMENT_END",
                    "next_card_recipe": recipes[card_index + 1] if card_index + 1 < len(recipes) else "STATEMENT_END",
                    "f13r_s009_focus": "YES" if statement_id == "P1009-S009" else "NO",
                }
            )

    assert aligned_events == 3888
    assert duplicate_events == len(occurrences)
    assert triple_count == 0
    assert len(occurrences) == 40

    for index, row in enumerate(occurrences, start=1):
        row["duplicate_id"] = f"RC{index:03d}"

    occurrence_fields = [
        "duplicate_id", "core", "core_value_de", "double_scope_reading_de",
        "event_id", "physical_page", "register", "statement_id", "locus",
        "owner_de", "card_ordinal_in_statement", "surface_card", "component_recipe",
        "marked_duplicate_recipe", "duplicate_atom_ordinal", "left_atom", "right_atom",
        "previous_card_surface", "previous_card_recipe", "next_card_surface",
        "next_card_recipe", "f13r_s009_focus",
    ]
    write_tsv(OUT / "REPEATED_CORE_OCCURRENCES.tsv", occurrence_fields, occurrences)

    summary_rows: list[dict[str, object]] = []
    for core, count in Counter(row["core"] for row in occurrences).most_common():
        selected = [row for row in occurrences if row["core"] == core]
        summary_rows.append(
            {
                "core": core,
                "core_value_de": core_values[core],
                "occurrences": count,
                "surface_card_types": len({row["surface_card"] for row in selected}),
                "component_recipe_types": len({row["component_recipe"] for row in selected}),
                "statements": len({row["statement_id"] for row in selected}),
                "pages": len({row["physical_page"] for row in selected}),
                "registers": "|".join(sorted({str(row["register"]) for row in selected})),
                "card_start_count": sum(row["left_atom"] == "CARD_START" for row in selected),
                "card_end_count": sum(row["right_atom"] == "CARD_END" for row in selected),
                "left_atom_counts": "|".join(
                    f"{atom}:{n}" for atom, n in sorted(Counter(str(row["left_atom"]) for row in selected).items())
                ),
                "right_atom_counts": "|".join(
                    f"{atom}:{n}" for atom, n in sorted(Counter(str(row["right_atom"]) for row in selected).items())
                ),
                "double_scope_reading_de": RULE_EXPANSIONS[core],
            }
        )

    summary_fields = [
        "core", "core_value_de", "occurrences", "surface_card_types",
        "component_recipe_types", "statements", "pages", "registers",
        "card_start_count", "card_end_count", "left_atom_counts", "right_atom_counts",
        "double_scope_reading_de",
    ]
    write_tsv(OUT / "REPEATED_CORE_PATTERN_SUMMARY.tsv", summary_fields, summary_rows)

    core_counts = Counter(str(row["core"]) for row in occurrences)
    register_counts = Counter(str(row["register"]) for row in occurrences)
    pages = {str(row["physical_page"]) for row in occurrences}
    statements = {str(row["statement_id"]) for row in occurrences}
    surface_types = {str(row["surface_card"]) for row in occurrences}
    recipe_types = {str(row["component_recipe"]) for row in occurrences}
    absent_cores = [root for root in core_values if root not in core_counts]

    report = f"""# Pass 1021 — der wiederholte Kern als Doppelrahmen

## Vollständiges Inventar

In den 3.888 laufenden Karten stehen **40** unmittelbar verdoppelte gleiche
tragbare Kerne. Jede Doppelung liegt innerhalb einer einzelnen Kartenzerlegung;
Karten über einen sichtbaren Trenner hinweg werden nicht zusammengezogen. Es
gibt 40 betroffene Karten in {len(statements)} Aussagen auf {len(pages)} Seiten,
{len(surface_types)} sichtbare Kartentypen und {len(recipe_types)} verschiedene
Komponentenrezepte. Keine Karte enthält zwei Doppelpaare oder eine Dreifachform.

Die Register verteilen sich auf Herbal {register_counts['HERBAL']}, Biological
{register_counts['BIOLOGICAL']}, Celestial {register_counts['CELESTIAL']} und
Pharma {register_counts['PHARMA']}.

| Kern | Wert | Vorkommen | Kurzform des Doppelrahmens |
|---|---|---:|---|
"""
    for row in summary_rows:
        report += (
            f"| `{row['core']}` | {row['core_value_de']} | {row['occurrences']} | "
            f"{row['double_scope_reading_de']} |\n"
        )
    report += f"""

Die zwölf Kerne ohne unmittelbare Doppelung sind
`{' '.join(absent_cores)}`. Die Abwesenheit erzeugt keine Sonderregel; das Blatt
braucht sie für diese Konstruktion nur nicht.

## Vier mögliche Lesungen

### Bloße Wiederholung

Das passt teilweise zu `CH+CH`, `OK+OK` und `OL+OL`: eine Handlung wird noch
einmal ausgeführt. Es erklärt aber `AR+AR`, `AL+AL`, `OR+OR` und `Y+Y` schlecht,
weil dort nicht einfach eine Tätigkeit wiederholt wird.

### Plural

Zwei Ausgänge, Zielorte, Einheiten oder Posten wären möglich. Doch die
`CH+CH`-Karten stehen fast immer vor einem weiteren Kern wie `T`, `K`, `P` oder
`S`. Das sieht eher nach einem eingebetteten Arbeitsblock als nach einer
einfachen Zweizahl aus.

### Nachdruck

Nachdruck könnte eine einzelne Doppelkarte erklären, aber nicht, warum die
Doppelung bei Handlungen am Kartenanfang und bei Relationen häufig am Ende
eines Rahmens steht. Außerdem würde sie den sichtbaren Besitzerwechsel nicht
nutzen.

### Verschachtelung

Verschachtelung trägt alle sieben Kerne mit derselben Regel und erklärt die
Nachbarstruktur am sparsamsten. Bei `CH` folgen auf das Doppel stets
Handlungs- oder Einstellkerne; bei `AR`, `AL`, `OR` und `Y` werden dagegen zwei
Besitz- oder Adresslagen übereinandergelegt. `OL+OL` hält den äußeren und den
inneren Fortsetzungsgang zugleich offen.

## Die einheitliche Werkstattregel

Die beste Lehrregel heißt **DOPPELRAHMEN / EIN STUFENABSTIEG**:

> `X + X + Z` = `X_äußerer Besitzer ( X_aktive Untereinheit ( Z ) )`

Der erste Kern bindet den äußeren Bild-, Stations-, Ring- oder Gefäßbesitzer.
Der zweite gleiche Kern steigt genau eine Ebene zum aktiven Mitglied,
Teilposten oder Untergang hinab. Ein rechts folgender Kern `Z` füllt zuerst den
inneren Rahmen. Endet die Karte mit `X+X`, liefert der lokale Besitzer den
inneren Inhalt.

Dadurch darf die flüssige Sprache je nach Kern unterschiedlich klingen:

- bei Handlungen wie `CH` und `OK`: **am Besitzer und dann am Teilposten noch
  einmal ausführen**;
- bei `OL`: **äußeren und inneren Gang fortsetzen**;
- bei `AR` und `AL`: **Ausgang/Ziel innerhalb eines übergeordneten
  Ausgangs-/Zielrahmens**;
- bei `Y`: **Besitzerreferent und aktiver Unterreferent**;
- bei `OR`: **Einheit in Einheit**.

Wiederholung und Zweizahl können also als lokale deutsche Wirkung erscheinen,
sind aber nicht die Grundregel. Nachdruck ist für keine Karte erforderlich.

## f13r, P1009-S009

Die drei Karten lauten:

```text
sotchy            S + OT + Y
kchy              K + Y
okorory           OK + OR + OR + Y
```

Mit dem Doppelrahmen wird die letzte Karte rechtsgeschachtelt gelesen:

```text
SETZEN [äußere EINHEIT [innere EINHEIT [AKTIVER POSTEN]]]
```

Der Bildbesitzer zeigt eine ganze Pflanze mit deutlich getrennten Wurzel-,
Kronen-, Blatt- und Blütenposten. Die einfache lokale Expansion lautet:

> Danach den nächsten sichtbaren Pflanzenteil wählen und geben; ihn als
> Untereinheit in den laufenden Pflanzenartikel setzen. Offen weiterführen.

Damit bedeutet `OR+OR` weder zwei fertige Zubereitungen noch bloß
**sehr starke Einheit**. Die erste `OR` hält den Artikelrahmen, die zweite den
aktiven Teilrahmen. Das Blatt sagt weiterhin nicht, welcher Pflanzenteil gewählt
wird und ob der äußere Rahmen Artikel, Arbeitsgang oder Vorratsgruppe heißt;
genau diese Konkretisierung bleibt beim Besitzer.

## Was die Regel nicht erfindet

Der Doppelrahmen gibt keinem Kern einen zweiten Wörterbuchwert. Er benennt
keine Pflanzenart, Flüssigkeit, Körperstelle, Sternfigur oder Gefäßfüllung. Er
erklärt nur, warum derselbe bereits gelernte Kern unmittelbar zweimal stehen
kann: Der Schreiber führt dieselbe Funktion auf zwei benachbarten
Besitzerebenen aus.

Das vollständige Auftreten mit Karte, Aussage, Seite, Besitzer, inneren
Nachbaratomen sowie voriger und nächster Karte steht in
`REPEATED_CORE_OCCURRENCES.tsv`.
"""
    (OUT / "REPEATED_CORE_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "IMMEDIATE_DUPLICATE_CORE_IS_ONE_LEVEL_NESTED_OWNER_FRAME",
        "running_events_scanned": aligned_events,
        "duplicate_events": len(occurrences),
        "duplicate_pairs": len(occurrences),
        "triple_runs": triple_count,
        "core_counts": dict(core_counts),
        "register_counts": dict(register_counts),
        "pages_with_duplicate": len(pages),
        "statements_with_duplicate": len(statements),
        "surface_card_types": len(surface_types),
        "component_recipe_types": len(recipe_types),
        "f13r_s009_occurrences": sum(row["f13r_s009_focus"] == "YES" for row in occurrences),
    }
    (OUT / "REPEATED_CORE_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
