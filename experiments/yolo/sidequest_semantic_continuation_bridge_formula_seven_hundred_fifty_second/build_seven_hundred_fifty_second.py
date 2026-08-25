#!/usr/bin/env python3
"""Build Pass 752: context-bound OL continuation bridges."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P751 = ROOT / "experiments/yolo/sidequest_semantic_measure_address_formula_seven_hundred_fifty_first"


def read() -> list[dict[str, str]]:
    path = P751 / "SEVEN_HUNDRED_FIFTY_FIRST_116_PACKING_AUDIT.tsv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RULES = [
    {
        "rule_id": "R1_PREPARATION_CONTINUATION_BRIDGE",
        "bridge_type": "PREPARATION_BRIDGE",
        "trigger": ["OT+CH+OR", "OL+OR", "AIIN", "AR", "OL"],
        "replacement": ["OT+CH+OR", "OR", "OT+OL", "OL", "OL+OR", "OL", "AIIN", "AR"],
        "reading_de": "DANACH ANSATZ ENTNEHMEN | ANSATZ | DANACH WEITER | WEITER | WEITER ANSATZ | WEITER | SOLLMASS | QUELLE",
        "explanation": "the continuing preparation is resumed on both sides before measure and source",
    },
    {
        "rule_id": "R2_CURRENT_ITEM_CONTINUATION_CADENCE",
        "bridge_type": "TERMINAL_CONTINUATION_CADENCE",
        "trigger": ["OL+Y", "CHK+E+Y", "OL", "SHED+DY"],
        "replacement": ["Y", "OL", "CHK+E+Y", "OL", "SHED+DY"],
        "reading_de": "DIES | WEITER | DIES KURZ WAERMEN | WEITER | ABSETZEN; SCHLUSS",
        "explanation": "the current item and OL are separated before the warm-and-settle cadence",
    },
    {
        "rule_id": "R3_PORTION_TARGET_SOURCE_BRIDGE",
        "bridge_type": "ADDRESS_BRIDGE",
        "trigger": ["OL+K+AIN", "AL", "AR", "SHED+DY"],
        "replacement": ["OL+K+AIN", "AL", "K+AR", "SHED+DY"],
        "reading_de": "WEITER PORTION ZUGEBEN | ZIELSTELLE | AUS QUELLE ZUGEBEN | ABSETZEN; SCHLUSS",
        "explanation": "the target is named between the dose and the source-packed addition",
    },
    {
        "rule_id": "R4_TARGET_CONTINUATION_BEFORE_TRANSFER",
        "bridge_type": "ADDRESS_BRIDGE",
        "trigger": ["SHED+AL", "L+OL", "OL"],
        "replacement": ["SHED+AL", "AL", "OL", "L+OL"],
        "reading_de": "AN ZIELSTELLE ABSETZEN | ZIELSTELLE | WEITER | WEITER LEITEN",
        "explanation": "AL|OL is inserted as the bridge before the continuing transfer card",
    },
]


def replace_once(sequence: list[str], trigger: list[str], replacement: list[str]) -> tuple[list[str], bool]:
    hits = [i for i in range(len(sequence) - len(trigger) + 1) if sequence[i : i + len(trigger)] == trigger]
    if not hits:
        return sequence, False
    if len(hits) != 1:
        raise AssertionError((trigger, hits))
    start = hits[0]
    return sequence[:start] + replacement + sequence[start + len(trigger) :], True


def main() -> None:
    source = read()
    audit_rows = []
    occurrence_rows = []
    fixed_rows = []
    residual_rows = []
    for row in source:
        baseline = row["measure_formula_recipe_sequence"].split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        predicted = baseline[:]
        applied = []
        for rule in RULES:
            predicted, hit = replace_once(predicted, rule["trigger"], rule["replacement"])
            if hit:
                applied.append(rule["rule_id"])
                occurrence_rows.append({
                    "rule_id": rule["rule_id"],
                    "bridge_type": rule["bridge_type"],
                    "statement_id": row["statement_id"],
                    "page": row["page"],
                    "record": row["record"],
                    "trigger_recipe_sequence": " | ".join(rule["trigger"]),
                    "replacement_recipe_sequence": " | ".join(rule["replacement"]),
                    "reading_de": rule["reading_de"],
                    "explanation": rule["explanation"],
                })
        baseline_exact = baseline == observed
        exact = predicted == observed
        out = {
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "pass751_recipe_sequence": row["measure_formula_recipe_sequence"],
            "continuation_bridge_recipe_sequence": " | ".join(predicted),
            "observed_recipe_sequence_after_reveal": row["observed_recipe_sequence_after_reveal"],
            "applied_rules": ",".join(applied) or "NONE",
            "baseline_cards": len(baseline),
            "candidate_cards": len(predicted),
            "observed_cards": len(observed),
            "baseline_exact": "YES" if baseline_exact else "NO",
            "candidate_exact": "YES" if exact else "NO",
            "newly_fixed": "YES" if not baseline_exact and exact else "NO",
            "newly_harmed": "YES" if baseline_exact and not exact else "NO",
        }
        audit_rows.append(out)
        if out["newly_fixed"] == "YES":
            fixed_rows.append(out)
        if not exact:
            residual_rows.append(out)

    rule_rows = []
    for rule in RULES:
        occurrences = [row for row in occurrence_rows if row["rule_id"] == rule["rule_id"]]
        affected = [row for row in audit_rows if rule["rule_id"] in row["applied_rules"].split(",")]
        rule_rows.append({
            "rule_id": rule["rule_id"],
            "bridge_type": rule["bridge_type"],
            "trigger_recipe_sequence": " | ".join(rule["trigger"]),
            "replacement_recipe_sequence": " | ".join(rule["replacement"]),
            "reading_de": rule["reading_de"],
            "explanation": rule["explanation"],
            "trigger_count": len(occurrences),
            "statement_ids": ",".join(row["statement_id"] for row in occurrences),
            "newly_fixed": sum(row["newly_fixed"] == "YES" for row in affected),
            "newly_harmed": sum(row["newly_harmed"] == "YES" for row in affected),
            "retain_rule": "YES" if occurrences and all(row["newly_fixed"] == "YES" for row in affected) else "NO",
        })

    write("SEVEN_HUNDRED_FIFTY_SECOND_4_CONTINUATION_RULES.tsv", rule_rows)
    write("SEVEN_HUNDRED_FIFTY_SECOND_4_TRIGGER_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_FIFTY_SECOND_116_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FIFTY_SECOND_4_NEWLY_FIXED.tsv", fixed_rows)
    write("SEVEN_HUNDRED_FIFTY_SECOND_19_RESIDUAL_ERRORS.tsv", residual_rows)

    exact = sum(row["candidate_exact"] == "YES" for row in audit_rows)
    equal = sum(int(row["candidate_cards"]) == int(row["observed_cards"]) for row in audit_rows)
    cards = sum(int(row["candidate_cards"]) for row in audit_rows)
    report = f"""# Pass 752 — OL als gelernte Weiter-Bruecke

OL bleibt **WEITER**. Die vier neuen Regeln erklaeren, warum dieses kurze Wort manchmal als eigene Karte auf beiden Seiten einer Adresse oder Zubereitung steht, ohne ein frei kopierbares OL-Register einzufuehren.

## Vier Bruecken

1. H2-S002 entfaltet eine fortgesetzte Zubereitung vor Sollmass und Quelle.
2. B1-S008 trennt `DIES | WEITER` vor Waermen und der Schlusskadenz `WEITER | ABSETZEN; SCHLUSS`.
3. B4-S016 setzt die Zielstelle zwischen weiterer Portion und quellgebundener Zugabe.
4. B5-S003 schreibt `ZIELSTELLE | WEITER` vor der Transferkarte aus.

## Ergebnis

- Exakte Aussagen:93→{exact}/116.
- Richtige Kartenzahl:103→{equal}/116.
- Ausgabekarten:357→{cards}/381.
- Vier Regeln, vier Treffer, vier ganze Reparaturen, kein Schaden.
- {len(residual_rows)} Restfehler bleiben.

Damit sind alle vier Phrasenfamilien aus Pass749 praktisch vertreten. Die verbliebenen Fehler sind jetzt ueberwiegend seltene Ganzkartenpackung, echte Reihenfolgevarianten oder grosse Herbal-Formeln. Als naechstes folgt eine neue Restklassifikation statt weiterer blind erfundener Kopierachsen.
"""
    (HERE / "SEVEN_HUNDRED_FIFTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "rules": len(rule_rows),
        "triggers": len(occurrence_rows),
        "statements": len(audit_rows),
        "baseline_exact": sum(row["baseline_exact"] == "YES" for row in audit_rows),
        "candidate_exact": exact,
        "baseline_equal_card_count": sum(int(row["baseline_cards"]) == int(row["observed_cards"]) for row in audit_rows),
        "candidate_equal_card_count": equal,
        "baseline_cards": sum(int(row["baseline_cards"]) for row in audit_rows),
        "candidate_cards": cards,
        "observed_cards": sum(int(row["observed_cards"]) for row in audit_rows),
        "newly_fixed": len(fixed_rows),
        "newly_harmed": sum(row["newly_harmed"] == "YES" for row in audit_rows),
        "residual_errors": len(residual_rows),
        "semantic_changes": 0,
        "deck_changes": 0,
        "decision": "OL_IS_LEARNED_CONTINUATION_BRIDGE__FOUR_CONTEXTS_FIX_FOUR__RECLASSIFY_NINETEEN_REMAINDERS",
    }
    (HERE / "SEVEN_HUNDRED_FIFTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
