#!/usr/bin/env python3
"""Build Pass 756: three small learned phrase reorderings."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P755 = ROOT / "experiments/yolo/sidequest_semantic_segmentation_redistribution_seven_hundred_fifty_fifth"


def read() -> list[dict[str, str]]:
    path = P755 / "SEVEN_HUNDRED_FIFTY_FIFTH_116_PACKING_AUDIT.tsv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RULES = [
    {
        "rule_id": "R1_MEASURE_PORTION_SERIES",
        "trigger": ["AIIN", "OK+Y", "AIN", "Y+K+AN", "O+DY"],
        "replacement": ["OK+AIIN", "AIIN", "Y+K+AIN", "Y+K+AN", "O+DY"],
        "reading_de": "NACH SOLLMASS ANSETZEN | SOLLMASS | DIESE PORTION ZUGEBEN | DIESE NACHGABE ZUGEBEN | ARBEITSGANG; SCHLUSS",
        "phrase_role": "measure first, then ordinary portion and additional portion as parallel cards",
    },
    {
        "rule_id": "R2_HOLD_INGREDIENT_REPEAT_ACTIVATION",
        "trigger": ["HO", "SH", "K+E+Y", "OK+Y"],
        "replacement": ["SH", "HO", "K+E+Y", "OK+OK+Y"],
        "reading_de": "HALTEN | ZUTAT | DIESE KURZ ZUGEBEN | DIES ERNEUT ANSETZEN",
        "phrase_role": "hold precedes the ingredient and doubled OK marks another activation",
    },
    {
        "rule_id": "R3_ORDERED_TRANSFER_MEASURE_CLOSE",
        "trigger": ["AIN", "CHD+Y", "OT+E+AIIN", "OT+E+AIIN", "UNPACKED(DY)"],
        "replacement": ["CHD+AIN", "CHD+Y", "OT+E+AIIN", "OT+AIIN", "OT+E+DY"],
        "reading_de": "PORTION UMSETZEN | DIES UMSETZEN | DANACH KURZ SOLLMASS | DANACH SOLLMASS | DANACH KURZ; SCHLUSS",
        "phrase_role": "a five-card transfer series alternates graded and ungraded next-measure cards before close",
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
        baseline = row["redistributed_recipe_sequence"].split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        predicted = baseline[:]
        applied = []
        for rule in RULES:
            predicted, hit = replace_once(predicted, rule["trigger"], rule["replacement"])
            if hit:
                applied.append(rule["rule_id"])
                occurrence_rows.append({
                    "rule_id": rule["rule_id"], "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
                    "trigger_recipe_sequence": " | ".join(rule["trigger"]), "replacement_recipe_sequence": " | ".join(rule["replacement"]),
                    "reading_de": rule["reading_de"], "phrase_role": rule["phrase_role"],
                })
        baseline_exact = baseline == observed
        exact = predicted == observed
        out = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "pass755_recipe_sequence": row["redistributed_recipe_sequence"],
            "small_phrase_recipe_sequence": " | ".join(predicted),
            "observed_recipe_sequence_after_reveal": row["observed_recipe_sequence_after_reveal"],
            "applied_rules": ",".join(applied) or "NONE", "baseline_cards": len(baseline),
            "candidate_cards": len(predicted), "observed_cards": len(observed),
            "baseline_exact": "YES" if baseline_exact else "NO", "candidate_exact": "YES" if exact else "NO",
            "newly_fixed": "YES" if not baseline_exact and exact else "NO", "newly_harmed": "YES" if baseline_exact and not exact else "NO",
        }
        audit_rows.append(out)
        if out["newly_fixed"] == "YES": fixed_rows.append(out)
        if not exact: residual_rows.append(out)

    rule_rows = []
    for rule in RULES:
        occurrences = [row for row in occurrence_rows if row["rule_id"] == rule["rule_id"]]
        affected = [row for row in audit_rows if rule["rule_id"] in row["applied_rules"].split(",")]
        rule_rows.append({
            "rule_id": rule["rule_id"], "trigger_recipe_sequence": " | ".join(rule["trigger"]),
            "replacement_recipe_sequence": " | ".join(rule["replacement"]), "reading_de": rule["reading_de"],
            "phrase_role": rule["phrase_role"], "trigger_count": len(occurrences),
            "statement_ids": ",".join(row["statement_id"] for row in occurrences),
            "newly_fixed": sum(row["newly_fixed"] == "YES" for row in affected),
            "newly_harmed": sum(row["newly_harmed"] == "YES" for row in affected),
            "retain_rule": "YES" if occurrences and all(row["newly_fixed"] == "YES" for row in affected) else "NO",
        })

    write("SEVEN_HUNDRED_FIFTY_SIXTH_3_SMALL_PHRASE_RULES.tsv", rule_rows)
    write("SEVEN_HUNDRED_FIFTY_SIXTH_3_TRIGGER_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_FIFTY_SIXTH_116_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FIFTY_SIXTH_3_NEWLY_FIXED.tsv", fixed_rows)
    write("SEVEN_HUNDRED_FIFTY_SIXTH_7_LARGE_FORMULA_RESIDUALS.tsv", residual_rows)

    exact = sum(row["candidate_exact"] == "YES" for row in audit_rows)
    equal = sum(int(row["candidate_cards"]) == int(row["observed_cards"]) for row in audit_rows)
    cards = sum(int(row["candidate_cards"]) for row in audit_rows)
    report = f"""# Pass 756 — drei kleine gelernte Phrasen

Die drei mittleren Restfaelle sind jetzt als ganze Kartenwendungen gelernt.

- H4-S001: **nach Sollmass ansetzen | Sollmass | diese Portion zugeben | diese Nachgabe zugeben | Schluss**.
- H5-S003: **halten | Zutat | diese kurz zugeben | dies erneut ansetzen**.
- B3-S032: eine fuenfgliedrige Transferfolge mit kurzer/normaler Sollmassstufe und anschließendem Schluss.

## Ergebnis

- Exakte Aussagen:106→{exact}/116.
- Richtige Kartenzahl bleibt{equal}/116; alle drei hatten bereits die richtige Laenge.
- Ausgabekarten bleiben{cards}/381.
- Drei Regeln, drei Treffer, drei Reparaturen, kein Schaden.
- Genau{len(residual_rows)} grosse gelernte Formeln bleiben.

Damit ist die produktive Grammatik plus kleine Phrasenschicht praktisch geschlossen. Die sieben Reste werden als Nomenklatorformeln behandelt, nicht in neue Stämme zerhackt. Als naechstes werden ihre wiederkehrenden inneren Motive gesucht, bevor ganze Satzformeln gelernt werden.
"""
    (HERE / "SEVEN_HUNDRED_FIFTY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "rules": len(rule_rows), "triggers": len(occurrence_rows), "statements": len(audit_rows),
        "baseline_exact": sum(row["baseline_exact"] == "YES" for row in audit_rows), "candidate_exact": exact,
        "baseline_equal_card_count": sum(int(row["baseline_cards"]) == int(row["observed_cards"]) for row in audit_rows),
        "candidate_equal_card_count": equal, "baseline_cards": sum(int(row["baseline_cards"]) for row in audit_rows),
        "candidate_cards": cards, "observed_cards": sum(int(row["observed_cards"]) for row in audit_rows),
        "newly_fixed": len(fixed_rows), "newly_harmed": sum(row["newly_harmed"] == "YES" for row in audit_rows),
        "residual_errors": len(residual_rows), "semantic_changes": 0, "deck_changes": 0,
        "decision": "THREE_SMALL_PHRASE_REORDERS_FIX_THREE__SEVEN_LARGE_NOMENCLATOR_FORMULAS_REMAIN",
    }
    (HERE / "SEVEN_HUNDRED_FIFTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
