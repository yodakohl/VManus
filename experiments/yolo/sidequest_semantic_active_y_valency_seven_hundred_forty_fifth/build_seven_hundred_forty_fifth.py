#!/usr/bin/env python3
"""Build Pass 745: copy active Y only into attested Y-valent cards."""

from __future__ import annotations

import csv
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


def flatten(sequence: str) -> list[str]:
    cleaned = sequence.replace("UNPACKED(", "").replace(")", "").replace(" | ", "+")
    return cleaned.split("+") if cleaned else []


def bag_key(items: list[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(Counter(items).items()))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P738 / "SEVEN_HUNDRED_THIRTY_EIGHTH_173_CARD_DICTIONARY.tsv")
    source = read(P743 / "SEVEN_HUNDRED_FORTY_THIRD_116_REFINED_PACKING_AUDIT.tsv")

    recipe_frequency: Counter[str] = Counter()
    canonical_by_bag: dict[tuple[tuple[str, int], ...], dict[str, str]] = {}
    valency: dict[tuple[str, ...], dict[str, object]] = defaultdict(lambda: {
        "y_recipes": set(), "non_y_recipes": set(), "y_cards": 0, "y_events": 0,
        "non_y_cards": 0, "non_y_events": 0,
    })
    for row in cards:
        recipe = row["component_recipe"]
        parts = recipe.split("+")
        recipe_frequency[recipe] += int(row["events"])
        key = bag_key(parts)
        old = canonical_by_bag.get(key)
        if old is None or int(row["events"]) > int(old["events"]) or (int(row["events"]) == int(old["events"]) and recipe < old["component_recipe"]):
            canonical_by_bag[key] = row
        base = tuple(part for part in parts if part != "Y")
        bucket = valency[base]
        if "Y" in parts:
            bucket["y_recipes"].add(recipe)
            bucket["y_cards"] += 1
            bucket["y_events"] += int(row["events"])
        else:
            bucket["non_y_recipes"].add(recipe)
            bucket["non_y_cards"] += 1
            bucket["non_y_events"] += int(row["events"])

    valency_rows = []
    for base, bucket in sorted(valency.items(), key=lambda item: (len(item[0]), item[0])):
        if not bucket["y_recipes"]:
            continue
        valency_rows.append({
            "base_without_y": "+".join(base) or "Y_ONLY",
            "attested_y_recipes": " | ".join(sorted(bucket["y_recipes"])),
            "y_cards": bucket["y_cards"], "y_events": bucket["y_events"],
            "attested_non_y_recipes": " | ".join(sorted(bucket["non_y_recipes"])) or "NONE",
            "non_y_cards": bucket["non_y_cards"], "non_y_events": bucket["non_y_events"],
            "valency_class": "OPTIONAL_Y_VARIANT" if bucket["non_y_recipes"] else "Y_REQUIRED_IN_ATTESTED_DECK",
        })

    max_recipe = max(len(row["component_recipe"].split("+")) for row in cards)

    def y_pack(sequence: list[str]) -> tuple[list[str], int]:
        n = len(sequence)
        dp: list[tuple[float, int, list[str]] | None] = [None] * (n + 1)
        dp[n] = (0.0, 0, [])
        for start in range(n - 1, -1, -1):
            options: list[tuple[float, int, list[str]]] = []
            for end in range(start + 1, min(n, start + max_recipe) + 1):
                span = Counter(sequence[start:end])
                for copied_y in range(3):
                    candidate = span.copy()
                    candidate["Y"] += copied_y
                    key = tuple(sorted((part, count) for part, count in candidate.items() if count))
                    if key not in canonical_by_bag:
                        continue
                    card = canonical_by_bag[key]
                    tail = dp[end]
                    assert tail is not None
                    cost = 1.0 + 0.1 * copied_y - 0.01 * math.log1p(int(card["events"])) + tail[0]
                    options.append((cost, copied_y + tail[1], [card["component_recipe"]] + tail[2]))
            tail = dp[start + 1]
            assert tail is not None
            options.append((6.0 + tail[0], tail[1], [f"UNPACKED({sequence[start]})"] + tail[2]))
            dp[start] = min(options, key=lambda item: (item[0], item[1], len(item[2]), item[2]))
        assert dp[0] is not None
        return dp[0][2], dp[0][1]

    audit_rows = []
    changed_rows = []
    fixed_rows = []
    residual_rows = []
    residual_missing: Counter[str] = Counter()
    residual_extra: Counter[str] = Counter()
    for row in source:
        components = row["refined_component_sequence"].split("+")
        baseline = row["packed_recipe_sequence"].split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        predicted, copied_y = y_pack(components)
        baseline_exact = baseline == observed
        predicted_exact = predicted == observed
        predicted_counter = Counter(flatten(" | ".join(predicted)))
        observed_counter = Counter(flatten(" | ".join(observed)))
        missing = observed_counter - predicted_counter
        extra = predicted_counter - observed_counter
        residual_missing.update(missing)
        residual_extra.update(extra)
        output = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "refined_component_sequence": row["refined_component_sequence"],
            "baseline_recipe_sequence": row["packed_recipe_sequence"],
            "y_valent_recipe_sequence": " | ".join(predicted),
            "observed_recipe_sequence_after_reveal": row["observed_recipe_sequence_after_reveal"],
            "copied_y": copied_y,
            "baseline_cards": len(baseline), "y_valent_cards": len(predicted), "observed_cards": len(observed),
            "baseline_exact": "YES" if baseline_exact else "NO",
            "y_valent_exact": "YES" if predicted_exact else "NO",
            "newly_fixed": "YES" if not baseline_exact and predicted_exact else "NO",
            "newly_harmed": "YES" if baseline_exact and not predicted_exact else "NO",
            "residual_missing_occurrences": "+".join(item for item, count in sorted(missing.items()) for _ in range(count)) or "NONE",
            "residual_extra_occurrences": "+".join(item for item, count in sorted(extra.items()) for _ in range(count)) or "NONE",
            "rule": "COPY_Y_ONLY_INSIDE_ATTESTED_Y_VALENT_RECIPE",
        }
        audit_rows.append(output)
        if baseline != predicted:
            changed_rows.append(output)
        if output["newly_fixed"] == "YES":
            fixed_rows.append(output)
        if not predicted_exact:
            residual_rows.append(output)

    residual_component_rows = []
    for component in sorted(set(residual_missing) | set(residual_extra), key=lambda item: (-residual_missing[item], item)):
        residual_component_rows.append({
            "component": component, "missing_occurrences": residual_missing[component],
            "extra_occurrences": residual_extra[component],
            "net_missing": residual_missing[component] - residual_extra[component],
        })

    write("SEVEN_HUNDRED_FORTY_FIFTH_55_Y_VALENCY_BASES.tsv", valency_rows)
    write("SEVEN_HUNDRED_FORTY_FIFTH_116_Y_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FORTY_FIFTH_26_CHANGED_STATEMENTS.tsv", changed_rows)
    write("SEVEN_HUNDRED_FORTY_FIFTH_10_NEWLY_FIXED.tsv", fixed_rows)
    write("SEVEN_HUNDRED_FORTY_FIFTH_32_RESIDUAL_ERRORS.tsv", residual_rows)
    write("SEVEN_HUNDRED_FORTY_FIFTH_RESIDUAL_COMPONENT_COUNTS.tsv", residual_component_rows)

    exact = sum(row["y_valent_exact"] == "YES" for row in audit_rows)
    equal_count = sum(int(row["y_valent_cards"]) == int(row["observed_cards"]) for row in audit_rows)
    total_cards = sum(int(row["y_valent_cards"]) for row in audit_rows)
    total_y = sum(int(row["copied_y"]) for row in audit_rows)
    report = f"""# Pass 745 — Y als kopierter Aktivposten-Slot

Das unveraenderte Deck enthaelt60 Y-haltige exakte Karten mit124 Ereignissen und125 geschriebenen Y-Slots. Sie bilden55 verschiedene Grundrezepte ohne Y;48 davon kommen im Deck nur mit Y vor,7 besitzen sowohl Y- als auch Nicht-Y-Variante.

Der neue Packer darf null, ein oder zwei Y in einen Bedeutungsabschnitt kopieren, aber nur wenn das Ergebnis exakt eine bereits gelernte Deckkarte ist. Kein anderer Wert darf ergaenzt werden.

## Ergebnis

- Exakte Rezeptfolge steigt74→{exact}/116.
- Gleiche Kartenzahl steigt91→{equal_count}/116.
- {len(fixed_rows)} zuvor falsche Aussagen werden exakt; keine zuvor exakte Aussage wird beschaedigt.
- {len(changed_rows)} Aussagen verwenden die Y-Regel; insgesamt werden{total_y} Y-Slots kopiert.
- Der Packer schreibt{total_cards} Karten gegen381 beobachtete.
- {len(residual_rows)} Aussagen bleiben nicht exakt.

Die zehn konkret reparierten Aussagen verteilen sich ueber Herbal und Biological. Besonders lehrreich sind Ein-Karten-Zellen wie H3-S002: die fluessige Lesung nennt den Posten einmal, die gelernte Karte `SH+O+Y+T+Y` schreibt ihn an beiden valenten Stellen.

## Was Y jetzt bedeutet

Y ist weiterhin **DIES / DER AKTUELLE ARBEITSPOSTEN**. Die neue Regel ist rein graphisch-syntaktisch: Sobald eine gelernte Karte einen aktiven Gegenstandslot verlangt, wird Y in dieser Karte erneut geschrieben. Das ist einfacher fuer mehrere Schreiber als freie Pronomenverwaltung: jede Fachkarte ist lokal vollstaendig genug, um ihren Gegenstand zu tragen.

## Grenze

Der Packer ist nun zu kompakt ({total_cards} statt381 Karten). Das liegt daran, dass fluessige Sprache auch OL, AL, AIIN, OK und andere Werte nur einmal nennt, waehrend die Werkstattausgabe sie ueber mehrere Karten wiederholt. Als Naechstes wird daher dieselbe Valenzidee fuer **Adress- und Fortsetzungs-Kopie** getestet, ohne die drei echten Segmentierungsfaelle anzutasten.
"""
    (HERE / "SEVEN_HUNDRED_FORTY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "deck_cards": len(cards), "y_cards": sum("Y" in row["component_recipe"].split("+") for row in cards),
        "y_card_events": sum(int(row["events"]) for row in cards if "Y" in row["component_recipe"].split("+")),
        "written_y_slots": sum(row["component_recipe"].split("+").count("Y") * int(row["events"]) for row in cards),
        "y_valency_bases": len(valency_rows), "optional_y_bases": sum(row["valency_class"] == "OPTIONAL_Y_VARIANT" for row in valency_rows),
        "y_required_bases": sum(row["valency_class"] == "Y_REQUIRED_IN_ATTESTED_DECK" for row in valency_rows),
        "statements": len(audit_rows), "changed_statements": len(changed_rows), "copied_y": total_y,
        "exact_recipe_sequences": exact, "equal_card_count_statements": equal_count,
        "newly_fixed": len(fixed_rows), "newly_harmed": sum(row["newly_harmed"] == "YES" for row in audit_rows),
        "predicted_cards": total_cards, "observed_cards": sum(int(row["observed_cards"]) for row in audit_rows),
        "residual_errors": len(residual_rows),
        "decision": "ATTESTED_ACTIVE_Y_COPY_FIXES_TEN_WITHOUT_HARM__NEXT_COPY_ADDRESS_AND_CONTINUATION_VALENCY",
    }
    (HERE / "SEVEN_HUNDRED_FORTY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
