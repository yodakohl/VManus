#!/usr/bin/env python3
"""Build Pass 749: cluster recurring card fragments into phrase families."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P747 = ROOT / "experiments/yolo/sidequest_semantic_multicard_formula_inventory_seven_hundred_forty_seventh"
P748 = ROOT / "experiments/yolo/sidequest_semantic_context_bound_formula_completion_seven_hundred_forty_eighth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


FAMILIES = {
    "MEASURE_ADDRESS_FRAME": {
        "members": {"Y | AIIN", "AIIN | Y", "OK+Y | AIIN", "AIIN | OL", "OL | AIIN"},
        "teaching_rule_de": "SOLLMASS steht zwischen oder neben Posten, Ansetzen und Weiter; die Karte wiederholt die benoetigte Adresse.",
        "creative_reading_de": "gemessener Posten / nach Sollmass weiter",
    },
    "CURRENT_PREPARATION_FRAME": {
        "members": {"OR | Y"},
        "teaching_rule_de": "Nach ANSATZ kann eine eigene DIES-Karte den aktiven Ansatz wieder aufnehmen.",
        "creative_reading_de": "der Ansatz, dieser",
    },
    "CONTINUATION_FRAME": {
        "members": {"AL | OL", "OL | SHED+DY", "OL+K+AIN | AL", "OL+OR | OL"},
        "teaching_rule_de": "WEITER kann Ziel, Portion, Ansatz oder Schluss als eigene kleine Bruecke rahmen.",
        "creative_reading_de": "weiter am Ziel / mit weiterer Portion / weiter bis Schluss",
    },
    "STAGED_ACTIVATION_FRAME": {
        "members": {"OK+EE+Y | OK+Y", "OK+Y | OL"},
        "teaching_rule_de": "Langes Ansetzen wird als lange Stufe, normale Stufe und WEITER ausgeschrieben.",
        "creative_reading_de": "lange ansetzen, ansetzen, weiter",
    },
}


def main() -> None:
    inventory = read(P747 / "SEVEN_HUNDRED_FORTY_SEVENTH_14_FORMULA_INVENTORY.tsv")
    residual = read(P748 / "SEVEN_HUNDRED_FORTY_EIGHTH_29_RESIDUAL_ERRORS.tsv")
    bigrams = [row for row in inventory if row["card_length"] == "2"]
    family_for = {}
    for family, spec in FAMILIES.items():
        for member in spec["members"]:
            if member in family_for:
                raise AssertionError(member)
            family_for[member] = family
    assert set(family_for) == {row["cards"] for row in bigrams}

    active_hits: dict[str, list[dict[str, object]]] = defaultdict(list)
    context_rows = []
    for row in residual:
        sequence = row["observed_recipe_sequence_after_reveal"].split(" | ")
        for start in range(len(sequence) - 1):
            cards = " | ".join(sequence[start : start + 2])
            if cards not in family_for:
                continue
            family = family_for[cards]
            hit = {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "start_card_1_based": start + 1,
                "left_card": sequence[start - 1] if start else "START",
                "fragment_cards": cards,
                "right_card": sequence[start + 2] if start + 2 < len(sequence) else "END",
            }
            active_hits[family].append(hit)
            context_rows.append({
                "family": family,
                **hit,
                "local_reading_de": next(row2["atomic_reading_de"] for row2 in bigrams if row2["cards"] == cards),
            })

    fragment_rows = []
    for row in bigrams:
        family = family_for[row["cards"]]
        hits = [hit for hit in active_hits[family] if hit["fragment_cards"] == row["cards"]]
        fragment_rows.append({
            "formula_id": row["formula_id"],
            "family": family,
            "cards": row["cards"],
            "atomic_reading_de": row["atomic_reading_de"],
            "original_residual_occurrences": row["residual_occurrences"],
            "remaining_occurrences_after_pass748": len(hits),
            "remaining_statement_ids": ",".join(sorted({str(hit["statement_id"]) for hit in hits})) or "NONE",
            "family_contribution_de": FAMILIES[family]["creative_reading_de"],
        })

    family_rows = []
    for family, spec in FAMILIES.items():
        hits = active_hits[family]
        family_rows.append({
            "family": family,
            "member_fragments": len(spec["members"]),
            "members": " ; ".join(sorted(spec["members"])),
            "remaining_occurrences": len(hits),
            "remaining_statements": len({str(hit["statement_id"]) for hit in hits}),
            "remaining_pages": ",".join(sorted({str(hit["page"]) for hit in hits})) or "NONE",
            "remaining_records": ",".join(sorted({str(hit["record"]) for hit in hits})) or "NONE",
            "teaching_rule_de": spec["teaching_rule_de"],
            "creative_reading_de": spec["creative_reading_de"],
            "status": "CLOSED_BY_PASS748" if not hits else "ACTIVE_PHRASE_FAMILY",
        })

    write("SEVEN_HUNDRED_FORTY_NINTH_12_FRAGMENT_FAMILIES.tsv", fragment_rows)
    write("SEVEN_HUNDRED_FORTY_NINTH_4_PHRASE_FAMILIES.tsv", family_rows)
    write("SEVEN_HUNDRED_FORTY_NINTH_21_REMAINING_FRAGMENT_CONTEXTS.tsv", context_rows)

    report = """# Pass 749 — vier Phrasenfamilien

Die zwoelf wiederkehrenden Zweikartenfragmente sind keine zwoelf neue Regeln. Sie fallen in vier lehrbare Werkstattfamilien.

## 1. Sollmass und Adresse

Fuenf Fragmente verbinden `AIIN` mit `Y`, `OK+Y` oder `OL`. Die gemeinsame Lesung ist nicht fuenf verschiedene Verben, sondern **gemessener Posten / nach Sollmass weiter**. Elf aktive Fragmente bleiben. Hier muss der Schreiber oft den Posten oder die Weiterarbeit als eigene Karte nach dem Mass wiederholen.

## 2. Aktueller Ansatz

`OR | Y` erscheint dreimal. Die knappe Lesung ist **der Ansatz, dieser**: OR nennt den Ansatz, Y reaktiviert ihn fuer den folgenden Schritt. Das ist ein guter Kandidat fuer eine kleine Besitzer-/Postenformel.

## 3. Weiter-Bruecken

Vier Fragmente zeigen `OL` als Kartenbruecke um Ziel, Portion, Ansatz oder Abschluss. Sieben aktive Vorkommen bleiben. Die beste Lehrregel lautet: **WEITER kann eine Adresse oder einen neuen Arbeitsschritt beidseitig rahmen**, ohne dass OL zu einem frei kopierbaren Stamm wird.

## 4. Gestufte Aktivierung

Die beiden Aktivierungsfragmente sind nach Pass748 vollstaendig geschlossen. Sie gehoeren bereits zur Formel **lange ansetzen | ansetzen | weiter** und liefern keinen Restfehler mehr.

## Nächster Schritt

Die drei noch aktiven Familien liefern21 Fragmente in15 Restsaetzen. Als naechstes werden ihre vollstaendigen linken und rechten Umgebungen zu wenigen Ausgaberegeln verdichtet. Prioritaet hat `OR | Y`, danach die Massklammern und erst dann die OL-Bruecken.
"""
    (HERE / "SEVEN_HUNDRED_FORTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "bigram_fragments": len(fragment_rows),
        "phrase_families": len(family_rows),
        "remaining_fragment_occurrences": len(context_rows),
        "remaining_fragment_statements": len({row["statement_id"] for row in context_rows}),
        "active_families": sum(row["status"] == "ACTIVE_PHRASE_FAMILY" for row in family_rows),
        "closed_families": sum(row["status"] == "CLOSED_BY_PASS748" for row in family_rows),
        "semantic_changes": 0,
        "deck_changes": 0,
        "decision": "TWELVE_BIGRAMS_COLLAPSE_TO_FOUR_PHRASE_FAMILIES__THREE_ACTIVE__COMPLETE_OR_Y_NEXT",
    }
    (HERE / "SEVEN_HUNDRED_FORTY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
