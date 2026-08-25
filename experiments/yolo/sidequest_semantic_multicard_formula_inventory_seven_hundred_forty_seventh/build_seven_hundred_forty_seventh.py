#!/usr/bin/env python3
"""Build Pass 747: recurring two- and three-card workshop formulas."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P745 = ROOT / "experiments/yolo/sidequest_semantic_active_y_valency_seven_hundred_forty_fifth"


def read(name: str) -> list[dict[str, str]]:
    with (P745 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


FORMULA_READINGS = {
    "Y | AIIN": ("MASSANSATZ_LINKS", "DIES | SOLLMASS", "fragment of measured-item bracket"),
    "AIIN | Y": ("MASSANSATZ_RECHTS", "SOLLMASS | DIES", "fragment of measured-item bracket"),
    "OR | Y": ("ANSATZ_POSTEN", "ANSATZ | DIES", "preparation followed by its current item"),
    "AIIN | OL": ("MASS_WEITER", "SOLLMASS | WEITER", "measure then continue"),
    "AL | OL": ("ZIEL_WEITER", "ZIELSTELLE | WEITER", "target then continuation"),
    "OK+EE+Y | OK+Y": ("LANG_NORMAL_ANSETZEN", "DIES LANG ANSETZEN | DIES ANSETZEN", "first two cards of staged activation"),
    "OK+Y | AIIN": ("ANSETZEN_MASS", "DIES ANSETZEN | SOLLMASS", "activation followed by prescribed measure"),
    "OK+Y | OL": ("ANSETZEN_WEITER", "DIES ANSETZEN | WEITER", "last two cards of staged activation"),
    "OL | AIIN": ("WEITER_MASS", "WEITER | SOLLMASS", "continuation followed by measure"),
    "OL | SHED+DY": ("WEITER_ABSETZEN", "WEITER | ABSETZEN; SCHLUSS", "continuation-close cadence"),
    "OL+K+AIN | AL": ("WEITER_PORTION_ZIEL", "WEITER PORTION ZUGEBEN | ZIELSTELLE", "transfer dose followed by target"),
    "OL+OR | OL": ("WEITER_ANSATZ_WEITER", "WEITER ANSATZ | WEITER", "continuation frame around preparation"),
    "OK+EE+Y | OK+Y | OL": ("GESTUFTE_AKTIVIERUNG", "DIES LANG ANSETZEN | DIES ANSETZEN | WEITER", "complete staged activation formula"),
    "Y | AIIN | Y": ("GEMESSENER_POSTEN", "DIES | SOLLMASS | DIES", "complete measured-item bracket"),
}


def windows(sequence: list[str], width: int):
    for start in range(len(sequence) - width + 1):
        yield start, tuple(sequence[start : start + width])


def main() -> None:
    residual = read("SEVEN_HUNDRED_FORTY_FIFTH_32_RESIDUAL_ERRORS.tsv")
    full = read("SEVEN_HUNDRED_FORTY_FIFTH_116_Y_PACKING_AUDIT.tsv")

    residual_hits: dict[tuple[str, ...], list[tuple[dict[str, str], int]]] = defaultdict(list)
    for row in residual:
        sequence = row["observed_recipe_sequence_after_reveal"].split(" | ")
        for width in (2, 3):
            for start, gram in windows(sequence, width):
                residual_hits[gram].append((row, start))

    formulas = {
        gram: hits
        for gram, hits in residual_hits.items()
        if len({row["statement_id"] for row, _ in hits}) >= 2
    }
    assert {" | ".join(gram) for gram in formulas} == set(FORMULA_READINGS)

    full_hits: dict[tuple[str, ...], list[tuple[dict[str, str], int]]] = defaultdict(list)
    for row in full:
        sequence = row["observed_recipe_sequence_after_reveal"].split(" | ")
        for gram in formulas:
            for start, window in windows(sequence, len(gram)):
                if window == gram:
                    full_hits[gram].append((row, start))

    formula_rows = []
    occurrence_rows = []
    for number, gram in enumerate(sorted(formulas, key=lambda item: (len(item), item)), start=1):
        formula = " | ".join(gram)
        name, reading, explanation = FORMULA_READINGS[formula]
        hits = formulas[gram]
        full_occurrences = full_hits[gram]
        statements = sorted({row["statement_id"] for row, _ in hits})
        pages = sorted({row["page"] for row, _ in hits})
        records = sorted({row["record"] for row, _ in hits})
        formula_id = f"F{number:02d}"
        is_trigram = len(gram) == 3
        formula_rows.append({
            "formula_id": formula_id,
            "cards": formula,
            "card_length": len(gram),
            "short_name": name,
            "atomic_reading_de": reading,
            "workshop_role": explanation,
            "residual_occurrences": len(hits),
            "residual_statements": len(statements),
            "residual_statement_ids": ",".join(statements),
            "all_116_occurrences": len(full_occurrences),
            "pages": ",".join(pages),
            "records": ",".join(records),
            "teaching_status": "TEACH_COMPLETE_MINI_FORMULA" if is_trigram else "TEACH_RECURRENT_FORMULA_OR_FRAGMENT",
        })
        for row, start in hits:
            occurrence_rows.append({
                "formula_id": formula_id,
                "short_name": name,
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "start_card_1_based": start + 1,
                "cards": formula,
                "atomic_reading_de": reading,
                "full_observed_recipe_sequence": row["observed_recipe_sequence_after_reveal"],
            })

    # Compress the residual teaching sheet greedily with longest formulas first.
    ordered = sorted(formulas, key=lambda gram: (-len(gram), gram))
    coverage_rows = []
    formula_uses: Counter[tuple[str, ...]] = Counter()
    total_cards = 0
    total_units = 0
    covered_statements = 0
    for row in residual:
        sequence = row["observed_recipe_sequence_after_reveal"].split(" | ")
        total_cards += len(sequence)
        units = []
        used = []
        cursor = 0
        while cursor < len(sequence):
            match = next(
                (gram for gram in ordered if tuple(sequence[cursor : cursor + len(gram)]) == gram),
                None,
            )
            if match is None:
                units.append(sequence[cursor])
                cursor += 1
                continue
            formula_id = next(row2["formula_id"] for row2 in formula_rows if row2["cards"] == " | ".join(match))
            units.append(f"<{formula_id}>")
            used.append(formula_id)
            formula_uses[match] += 1
            cursor += len(match)
        total_units += len(units)
        covered_statements += bool(used)
        coverage_rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "observed_cards": len(sequence),
            "formula_units": len(units),
            "saved_teaching_units": len(sequence) - len(units),
            "used_formula_ids": ",".join(used) or "NONE",
            "compressed_recipe_sequence": " | ".join(units),
        })

    for row in formula_rows:
        gram = tuple(row["cards"].split(" | "))
        row["greedy_teaching_uses"] = formula_uses[gram]
        row["greedy_status"] = "ACTIVE_MACRO" if formula_uses[gram] else "OVERLAPPED_FRAGMENT_ONLY"

    write("SEVEN_HUNDRED_FORTY_SEVENTH_14_FORMULA_INVENTORY.tsv", formula_rows)
    write("SEVEN_HUNDRED_FORTY_SEVENTH_32_FORMULA_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_FORTY_SEVENTH_32_RESIDUAL_FORMULA_COVERAGE.tsv", coverage_rows)

    report = f"""# Pass 747 — wiederkehrende Mini-Formeln

Die32 Restfehler wurden nicht nach neuen Einzelstämmen durchsucht, sondern nach wiederkehrenden Folgen aus bereits bekannten Kartenrezepten. Es gibt **14** solche Folgen:12 Zweikartenfragmente und2 vollständige Dreikartenformeln. Sie liegen in{covered_statements}/32 Restfällen.

## Zwei echte Lehrformeln

- `Y | AIIN | Y` = **DIES | SOLLMASS | DIES**. Das ist die kleinste lesbare Klammer für einen gemessenen aktuellen Posten. Sie steht in H2-S001 und B3-S003.
- `OK+EE+Y | OK+Y | OL` = **DIES LANG ANSETZEN | DIES ANSETZEN | WEITER**. Das ist eine gestufte Aktivierungsfolge in B2-S010 und B4-S003.

Die Zweierfolgen bleiben ebenfalls nützlich: `OL | SHED+DY` ist die wiederkehrende Kadenz **WEITER | ABSETZEN; SCHLUSS**, `OL+OR | OL` rahmt einen Ansatz mit Weiterarbeit, und `OL+K+AIN | AL` koppelt eine weitere Portion an ihre Zielstelle.

## Lehrlast

Die32 fehlerhaften Aussagen enthalten{total_cards} sichtbare Karten. Wenn der Lehrling immer die längste bekannte Mini-Formel als eine Einheit lernt, werden daraus{total_units} Lerneinheiten; das spart{total_cards - total_units} einzelne Kartenplätze. Dabei werden{sum(formula_uses.values())} Formeleinsätze aus12 tatsächlich gebrauchten Makros geschrieben. Zwei kurze Fragmente verschwinden nur deshalb, weil die längere Dreikartenformel Vorrang hat.

## Bedeutung für das Werkstattmodell

Das passt besser als weitere freie Kopierregister. Der Schreiber lernt:

1. kurze Bedeutungsstämme;
2. Y als wiederholten aktiven Postenslot;
3. einige feste Zwei-/Dreikartenwendungen;
4. den verbleibenden seltenen Rest als Ganzkartenfolge.

Als Nächstes werden nur die beiden Dreikartenformeln als aktive Ausgaberegeln auf die32 Restfälle gelegt. Sie dürfen nur auslösen, wenn ihre ganze semantische Umgebung passt; die zwölf Fragmente dienen zunächst als Lehr- und Suchhinweise.
"""
    (HERE / "SEVEN_HUNDRED_FORTY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "residual_statements": len(residual),
        "formulas": len(formula_rows),
        "bigrams": sum(int(row["card_length"]) == 2 for row in formula_rows),
        "trigrams": sum(int(row["card_length"]) == 3 for row in formula_rows),
        "formula_occurrences": len(occurrence_rows),
        "covered_residual_statements": covered_statements,
        "residual_cards": total_cards,
        "formula_teaching_units": total_units,
        "saved_teaching_units": total_cards - total_units,
        "greedy_formula_uses": sum(formula_uses.values()),
        "active_greedy_macros": sum(bool(count) for count in formula_uses.values()),
        "semantic_changes": 0,
        "deck_changes": 0,
        "decision": "TWO_COMPLETE_TRIGRAM_FORMULAS__TWELVE_RECURRENT_FRAGMENTS__TEST_WHOLE_FORMULA_COMPLETION_NEXT",
    }
    (HERE / "SEVEN_HUNDRED_FORTY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
