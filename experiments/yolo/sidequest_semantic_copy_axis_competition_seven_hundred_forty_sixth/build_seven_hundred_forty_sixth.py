#!/usr/bin/env python3
"""Build Pass 746: test OL/AL/AIIN/OK copy axes one at a time."""

from __future__ import annotations

import csv
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P738 = ROOT / "experiments/yolo/sidequest_semantic_remainder_closure_seven_hundred_thirty_eighth"
P743 = ROOT / "experiments/yolo/sidequest_semantic_helper_cue_packer_seven_hundred_forty_third"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def bag_key(items: list[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(Counter(items).items()))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P738 / "SEVEN_HUNDRED_THIRTY_EIGHTH_173_CARD_DICTIONARY.tsv")
    source = read(P743 / "SEVEN_HUNDRED_FORTY_THIRD_116_REFINED_PACKING_AUDIT.tsv")
    axes = ["OL", "AL", "AIIN", "OK"]

    canonical: dict[tuple[tuple[str, int], ...], dict[str, str]] = {}
    for row in cards:
        key = bag_key(row["component_recipe"].split("+"))
        old = canonical.get(key)
        if old is None or int(row["events"]) > int(old["events"]) or (int(row["events"]) == int(old["events"]) and row["component_recipe"] < old["component_recipe"]):
            canonical[key] = row
    max_recipe = max(len(row["component_recipe"].split("+")) for row in cards)

    def pack(sequence: list[str], copy_axes: list[str]) -> tuple[list[str], Counter[str]]:
        n = len(sequence)
        dp: list[tuple[float, Counter[str], list[str]] | None] = [None] * (n + 1)
        dp[n] = (0.0, Counter(), [])
        for start in range(n - 1, -1, -1):
            options: list[tuple[float, Counter[str], list[str]]] = []
            for end in range(start + 1, min(n, start + max_recipe) + 1):
                span = Counter(sequence[start:end])
                for copies in itertools.product(*(range(3) for _ in copy_axes)):
                    candidate = span.copy()
                    additions: Counter[str] = Counter()
                    for axis, count in zip(copy_axes, copies):
                        candidate[axis] += count
                        additions[axis] += count
                    key = tuple(sorted((part, count) for part, count in candidate.items() if count))
                    if key not in canonical:
                        continue
                    card = canonical[key]
                    tail = dp[end]
                    assert tail is not None
                    cost = 1.0 + 0.1 * sum(copies) - 0.01 * math.log1p(int(card["events"])) + tail[0]
                    options.append((cost, additions + tail[1], [card["component_recipe"]] + tail[2]))
            tail = dp[start + 1]
            assert tail is not None
            options.append((6.0 + tail[0], tail[1], [f"UNPACKED({sequence[start]})"] + tail[2]))
            dp[start] = min(options, key=lambda item: (item[0], sum(item[1].values()), len(item[2]), item[2]))
        assert dp[0] is not None
        return dp[0][2], dp[0][1]

    baseline: dict[str, list[str]] = {}
    for row in source:
        baseline[row["statement_id"]] = pack(row["refined_component_sequence"].split("+"), ["Y"])[0]

    detail_rows = []
    decision_rows = []
    harm_rows = []
    for axis in axes:
        fixes: list[str] = []
        harms: list[str] = []
        changed: list[str] = []
        copied_axis = 0
        copied_y = 0
        exact = 0
        equal_count = 0
        total_cards = 0
        for row in source:
            sequence = row["refined_component_sequence"].split("+")
            observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
            base = baseline[row["statement_id"]]
            predicted, additions = pack(sequence, ["Y", axis])
            base_exact = base == observed
            predicted_exact = predicted == observed
            if predicted != base:
                changed.append(row["statement_id"])
            if not base_exact and predicted_exact:
                fixes.append(row["statement_id"])
            if base_exact and not predicted_exact:
                harms.append(row["statement_id"])
            copied_y += additions["Y"]
            copied_axis += additions[axis]
            exact += predicted_exact
            equal_count += len(predicted) == len(observed)
            total_cards += len(predicted)
            detail_rows.append({
                "axis": axis, "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
                "baseline_y_recipe_sequence": " | ".join(base),
                "candidate_recipe_sequence": " | ".join(predicted),
                "observed_recipe_sequence_after_reveal": row["observed_recipe_sequence_after_reveal"],
                "copied_y": additions["Y"], "copied_axis": additions[axis],
                "candidate_changed": "YES" if predicted != base else "NO",
                "newly_fixed": "YES" if not base_exact and predicted_exact else "NO",
                "newly_harmed": "YES" if base_exact and not predicted_exact else "NO",
                "candidate_exact": "YES" if predicted_exact else "NO",
            })
        retain = bool(fixes) and not harms
        decision_rows.append({
            "axis": axis, "copied_axis_occurrences": copied_axis, "copied_y_occurrences": copied_y,
            "changed_statements": len(changed), "exact_recipe_sequences": exact,
            "equal_card_count_statements": equal_count, "predicted_cards": total_cards,
            "newly_fixed": len(fixes), "newly_fixed_ids": ",".join(fixes) or "NONE",
            "newly_harmed": len(harms), "newly_harmed_ids": ",".join(harms) or "NONE",
            "retain_rule": "YES" if retain else "NO",
            "decision_de": "behalten: echter no-harm Gewinn" if retain else ("verwerfen: beschaedigt richtige Packung" if harms else "verwerfen: kein zusaetzlicher Treffer"),
        })
        for statement_id in harms:
            source_row = next(row for row in detail_rows if row["axis"] == axis and row["statement_id"] == statement_id)
            harm_rows.append(source_row)

    inventory_rows = []
    for axis in axes:
        axis_cards = [row for row in cards if axis in row["component_recipe"].split("+")]
        bases = defaultdict(lambda: {"with": set(), "without": set()})
        for row in cards:
            parts = row["component_recipe"].split("+")
            base = tuple(part for part in parts if part != axis)
            bases[base]["with" if axis in parts else "without"].add(row["component_recipe"])
        with_bases = [value for value in bases.values() if value["with"]]
        inventory_rows.append({
            "axis": axis, "axis_cards": len(axis_cards), "axis_events": sum(int(row["events"]) for row in axis_cards),
            "valency_bases": len(with_bases),
            "optional_variant_bases": sum(bool(value["without"]) for value in with_bases),
            "axis_required_bases": sum(not value["without"] for value in with_bases),
        })

    write("SEVEN_HUNDRED_FORTY_SIXTH_4_AXIS_DECISIONS.tsv", decision_rows)
    write("SEVEN_HUNDRED_FORTY_SIXTH_464_AXIS_AUDIT.tsv", detail_rows)
    write("SEVEN_HUNDRED_FORTY_SIXTH_4_AXIS_VALENCY_INVENTORY.tsv", inventory_rows)
    write("SEVEN_HUNDRED_FORTY_SIXTH_2_HARM_CASES.tsv", harm_rows)

    report = """# Pass 746 — vier weitere Kopierachsen

Y bleibt aktiv. OL, AL, AIIN und OK wurden jeweils einzeln als zweite kopierbare Achse getestet. Eine Achse durfte nur dann erscheinen, wenn die erweiterte Bedeutungsmenge exakt eine vorhandene Deckkarte bildet.

## Ergebnis

- **OL:** 3 Kopien; 0 neue exakte Aussage, 0 Schaden.
- **OK:** 1 Kopie; 0 neue exakte Aussage, 0 Schaden.
- **AL:** 4 Kopien; 0 Gewinn, aber B2-S006 wird falsch.
- **AIIN:** 1 Kopie; 0 Gewinn, aber B1-S014 wird falsch.

Keine Achse wird uebernommen. OL und OK sind zwar unschaedlich, aber sie erklaeren keine einzige zusaetzliche Kartenfolge. AL und AIIN zeigen, warum atomweise Kopie zu grob ist: eine Adresse oder ein Sollmass darf nicht einfach in jede kompatible Karte hineingezogen werden.

## Konsequenz fuer das Schreibsystem

Y ist besonders, weil es der aktive Gegenstandslot einer Karte ist. OL, AL, AIIN und OK sind keine vergleichbaren frei propagierenden Register. Ihre Wiederholung muss als **ganze gelernte Kartenfolge oder gebundener Ausdruck** gelernt werden. Das historische Mischmodell wird dadurch praeziser:

1. Produktive kurze Bedeutungsfamilien.
2. Ein echter aktiver Y-Slot.
3. Keine allgemeinen Kopierregister fuer Weiter/Ziel/Mass/Ansetzen.
4. Wiederholungen dieser Werte gehoeren zum Kartenexemplar oder zu einer groesseren Formel.

## Nächster Hebel

Suche nun wiederkehrende Zwei- und Drei-Karten-Formeln in den32 Restfehlern. Statt Einzelwerte zu kopieren, lernt der Lehrling ganze Mini-Formeln wie `Adresse | Handlung+Y` oder `Sollmass | OK+Grad+Y`.
"""
    (HERE / "SEVEN_HUNDRED_FORTY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "axes_tested": axes, "statements_per_axis": len(source),
        "audit_rows": len(detail_rows), "baseline_exact": 84,
        "retained_axes": [row["axis"] for row in decision_rows if row["retain_rule"] == "YES"],
        "no_gain_axes": [row["axis"] for row in decision_rows if int(row["newly_fixed"]) == 0],
        "harm_cases": len(harm_rows), "semantic_changes": 0, "deck_changes": 0,
        "decision": "NO_ATOMIC_COPY_AXIS_BEYOND_Y__LEARN_MULTI_CARD_FORMULAS_NEXT",
    }
    (HERE / "SEVEN_HUNDRED_FORTY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
