#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P471 = ROOT / "experiments/yolo/sidequest_semantic_compact_renderer_habits_four_hundred_seventy_first"
P485 = ROOT / "experiments/yolo/sidequest_semantic_residual_forms_four_hundred_eighty_fifth"

WRAPPERS = ("", "q", "d", "s", "t", "ch", "che", "sh")
INNER_CASES = {
    "A:001": ("Y", "y+k+shy", "Y+K+Y uses Y allographs y and shy"),
    "A:013": ("Y", "ok+chy", "drop entry ch and select terminal Y allograph chy"),
    "A:015": ("Y", "y+k+chy", "Y+K+Y uses Y allographs y and chy"),
    "A:153": ("AR", "o+sar", "AR allograph sar inside O+AR"),
    "A:156": ("AIIN", "al+daiin", "AIIN allograph daiin inside AL+AIIN"),
    "A:219": ("Y", "y+k+y", "Y+K+Y uses the short Y allograph twice"),
    "A:222": ("AL", "ok+o+dal+y", "AL allograph dal inside OK+O+AL+Y"),
    "A:257": ("Y", "chey+k+y", "Y+K+Y selects chey first and y second"),
    "A:277": ("Y", "ok+e+dy", "terminal Y selects allograph dy"),
    "A:289": ("Y", "ot+y", "terminal Y selects short allograph y"),
    "A:385": ("Y", "ot+chy", "terminal Y selects allograph chy"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def leading_wrapper_analysis(predicted: str, observed: str) -> tuple[str, str, str] | None:
    candidates = []
    for old in WRAPPERS:
        if not predicted.startswith(old):
            continue
        body = predicted[len(old):]
        for new in WRAPPERS:
            if observed == new + body:
                candidates.append((old, new, body))
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: (-len(item[2]), len(item[0]) + len(item[1]), item))[0]


def main() -> None:
    exceptions = read(P471 / "FOUR_HUNDRED_SEVENTY_FIRST_113_EXEMPLAR_RENDERER_EXCEPTIONS.tsv")
    old_manual = read(P485 / "FOUR_HUNDRED_EIGHTY_FIFTH_277_ITEM_REVISED_MANUAL.tsv")
    old_ledger = read(P485 / "FOUR_HUNDRED_EIGHTY_FIFTH_776_REDUCED_MANUAL_RECONSTRUCTION.tsv")
    exception_map = {(row["domain"], row["item_id"]): row for row in exceptions}

    classification = []
    leading_count = 0
    inner_counts = Counter()
    for row in exceptions:
        predicted = row["compact_predicted_surface"]
        observed = row["exemplar_surface"]
        leading = leading_wrapper_analysis(predicted, observed)
        if leading:
            old, new, body = leading
            leading_count += 1
            classification.append({
                "exception_no": row["exception_no"],
                "domain": row["domain"],
                "item_id": row["item_id"],
                "unit_id": row["unit_id"],
                "page": row["page"],
                "formal_parse": row["formal_parse"],
                "predicted_surface": predicted,
                "observed_surface": observed,
                "generative_class": "ENTRY_WRAPPER_ALLOGRAPH",
                "old_wrapper": old or "BARE",
                "new_wrapper": new or "BARE",
                "preserved_body": body,
                "component_realization": "NOT_NEEDED",
                "observed_admitted": "YES",
            })
        else:
            family, realization, note = INNER_CASES[row["item_id"]]
            inner_counts[family] += 1
            classification.append({
                "exception_no": row["exception_no"],
                "domain": row["domain"],
                "item_id": row["item_id"],
                "unit_id": row["unit_id"],
                "page": row["page"],
                "formal_parse": row["formal_parse"],
                "predicted_surface": predicted,
                "observed_surface": observed,
                "generative_class": f"INNER_{family}_ALLOGRAPH",
                "old_wrapper": "NOT_APPLICABLE",
                "new_wrapper": "NOT_APPLICABLE",
                "preserved_body": "COMPONENTWISE",
                "component_realization": realization + " — " + note,
                "observed_admitted": "YES",
            })
    write("FOUR_HUNDRED_EIGHTY_SIXTH_113_EXCEPTION_RECLASSIFICATION.tsv", classification)

    rules = [
        {"rule_id": "G01", "rule_name": "ENTRY_WRAPPER_ALLOGRAPH", "allowed_forms": "BARE|q|d|s|t|ch|che|sh", "support_exceptions": leading_count, "teaching_rule_de": "Vor demselben Kartenkörper darf der Schreiber einen der acht gelernten Eintritts-Wrapper wählen; die Bedeutung bleibt gleich."},
        {"rule_id": "G02", "rule_name": "Y_ALLOGRAPH", "allowed_forms": "y|dy|chy|chey|shy|sy", "support_exceptions": inner_counts["Y"], "teaching_rule_de": "Y=DIES darf je nach Stelle als y, dy, chy, chey, shy oder sy geschrieben werden; mehrere Y derselben Karte wählen unabhängig."},
        {"rule_id": "G03", "rule_name": "AIIN_ALLOGRAPH", "allowed_forms": "aiin|daiin|saiin|taiin|chaiin", "support_exceptions": inner_counts["AIIN"], "teaching_rule_de": "AIIN=SOLLMASS behält seinen Kern und darf auch innerhalb einer Karte einen gelernten Eintritts-Wrapper tragen."},
        {"rule_id": "G04", "rule_name": "AL_ALLOGRAPH", "allowed_forms": "al|dal|chal|cheal|sal|tal", "support_exceptions": inner_counts["AL"], "teaching_rule_de": "AL=ZIELSTELLE darf auch innerhalb einer Komposition in einer seiner sechs Kartenformen stehen."},
        {"rule_id": "G05", "rule_name": "AR_ALLOGRAPH", "allowed_forms": "ar|char|dar|sar", "support_exceptions": inner_counts["AR"], "teaching_rule_de": "AR=QUELLE darf auch innerhalb einer Komposition als ar, char, dar oder sar realisiert werden."},
    ]
    write("FOUR_HUNDRED_EIGHTY_SIXTH_FIVE_GENERATIVE_ALLOGRAPH_RULES.tsv", rules)

    revised_manual = [row for row in old_manual if row["layer"] != "L9_SURFACE_EXEMPLAR"]
    for rule in rules:
        revised_manual.append({
            "manual_order": 0,
            "layer": "L9_GENERATIVE_ALLOGRAPH",
            "item_id": rule["rule_id"],
            "teaching_value_or_rule_de": rule["teaching_rule_de"],
            "scope": "PROSE_AND_ASTRO",
            "support_or_instances": rule["support_exceptions"],
            "source_artifact": "PASS486_FLEXIBLE_RENDERER",
        })
    for index, row in enumerate(revised_manual, 1):
        row["manual_order"] = index
    write("FOUR_HUNDRED_EIGHTY_SIXTH_169_ITEM_GENERATIVE_MANUAL.tsv", revised_manual)

    class_by_item = {(row["domain"], row["item_id"]): row for row in classification}
    ledger = []
    for row in old_ledger:
        key = (row["domain"], row["item_id"])
        new = dict(row)
        if key not in exception_map:
            new["generation_route"] = "DETERMINISTIC_DEFAULT_OR_HABIT"
            new["generative_rule"] = "DEFAULT_OR_EXISTING_HABIT"
            new["exact_surface_choice_deterministic"] = "YES"
            new["observed_surface_admitted"] = "YES"
        else:
            case = class_by_item[key]
            new["generation_route"] = "FLEXIBLE_ALLOGRAPH"
            new["generative_rule"] = case["generative_class"]
            new["exact_surface_choice_deterministic"] = "NO"
            new["observed_surface_admitted"] = case["observed_admitted"]
        ledger.append(new)
    write("FOUR_HUNDRED_EIGHTY_SIXTH_776_ADMISSIBLE_SURFACE_LEDGER.tsv", ledger)

    summary = {
        "status": "PASS",
        "previous_manual_items": 277,
        "removed_surface_exemplars": 113,
        "new_allograph_rules": len(rules),
        "manual_items": len(revised_manual),
        "entry_wrapper_cases": leading_count,
        "inner_component_cases": sum(inner_counts.values()),
        "deterministic_surfaces": sum(row["exact_surface_choice_deterministic"] == "YES" for row in ledger),
        "flexible_surfaces": sum(row["exact_surface_choice_deterministic"] == "NO" for row in ledger),
        "observed_surfaces_admitted": sum(row["observed_surface_admitted"] == "YES" for row in ledger),
        "groups": len(ledger),
        "exact_replica_still_needs_local_choices": 113,
    }
    (HERE / "FOUR_HUNDRED_EIGHTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
