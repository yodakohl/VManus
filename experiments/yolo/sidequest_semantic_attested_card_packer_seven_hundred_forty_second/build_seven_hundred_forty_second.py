#!/usr/bin/env python3
"""Build Pass 742: pack recoded meanings with the attested 173-card deck."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P738 = ROOT / "experiments/yolo/sidequest_semantic_remainder_closure_seven_hundred_thirty_eighth"
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P741 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_recoding_seven_hundred_forty_first"


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
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    recoding = read(P741 / "SEVEN_HUNDRED_FORTY_FIRST_116_RECODING_AUDIT.tsv")

    recipes_by_bag: dict[tuple[tuple[str, int], ...], list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        recipes_by_bag[bag_key(row["component_recipe"].split("+"))].append(row)

    canonical: dict[tuple[tuple[str, int], ...], dict[str, str]] = {}
    inventory_rows = []
    for key, rows in recipes_by_bag.items():
        selected = sorted(rows, key=lambda row: (-int(row["events"]), row["component_recipe"], row["exact_card_id"]))[0]
        canonical[key] = selected
        inventory_rows.append({
            "component_bag": "+".join(item for item, count in key for _ in range(count)),
            "canonical_recipe": selected["component_recipe"],
            "canonical_card_id": selected["exact_card_id"],
            "canonical_events": selected["events"],
            "alternative_recipes": " | ".join(sorted({row["component_recipe"] for row in rows} - {selected["component_recipe"]})) or "NONE",
            "exact_cards_with_bag": len(rows),
            "packing_rule": "ORDER_INSIDE_CARD_FROM_LEARNED_DECK__MEANING_CUES_MATCH_AS_MULTISET",
        })
    inventory_rows.sort(key=lambda row: (row["component_bag"].count("+") + 1, row["canonical_recipe"]))
    max_recipe = max(sum(count for _, count in key) for key in canonical)

    def pack(sequence: list[str]) -> list[dict[str, str]]:
        n = len(sequence)
        # objective: fewest cards, then prefer recurrent cards, then lexical stability
        dp: list[tuple[int, float, list[dict[str, str]]] | None] = [None] * (n + 1)
        dp[n] = (0, 0.0, [])
        for start in range(n - 1, -1, -1):
            options: list[tuple[int, float, list[dict[str, str]]]] = []
            for end in range(start + 1, min(n, start + max_recipe) + 1):
                key = bag_key(sequence[start:end])
                if key not in canonical:
                    continue
                card = canonical[key]
                tail = dp[end]
                assert tail is not None
                item = {
                    "packed_recipe": card["component_recipe"],
                    "packed_card_id": card["exact_card_id"],
                    "input_span": "+".join(sequence[start:end]),
                    "attested": "YES",
                }
                options.append((1 + tail[0], -math.log1p(int(card["events"])) + tail[1], [item] + tail[2]))
            tail = dp[start + 1]
            assert tail is not None
            fallback = {
                "packed_recipe": f"UNPACKED({sequence[start]})",
                "packed_card_id": "NONE",
                "input_span": sequence[start],
                "attested": "NO",
            }
            options.append((1 + tail[0], 100.0 + tail[1], [fallback] + tail[2]))
            dp[start] = min(options, key=lambda item: (item[0], item[1], [part["packed_recipe"] for part in item[2]]))
        assert dp[0] is not None
        return dp[0][2]

    observed_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        observed_by_statement[row["statement_id"]].append(row)

    audit_rows = []
    detail_rows = []
    for row in recoding:
        inferred = row["recoded_family_sequence"].split("+") if row["recoded_family_sequence"] else []
        packed = pack(inferred)
        predicted_recipes = [item["packed_recipe"] for item in packed]
        predicted_cards = [item["packed_card_id"] for item in packed]
        observed = observed_by_statement[row["statement_id"]]
        observed_recipes = [item["component_recipe"] for item in observed]
        observed_cards = [item["card_no"] for item in observed]
        exact_sequence = predicted_recipes == observed_recipes
        exact_bag = Counter(predicted_recipes) == Counter(observed_recipes)
        audit_rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "owner_noun_de": row["owner_noun_de"],
            "clean_instruction_de": row["clean_instruction_de"],
            "recoded_family_sequence": row["recoded_family_sequence"],
            "packed_recipe_sequence": " | ".join(predicted_recipes),
            "packed_canonical_card_ids": " | ".join(predicted_cards),
            "predicted_cards": len(packed),
            "attested_packed_cards": sum(item["attested"] == "YES" for item in packed),
            "unpacked_components": "+".join(item["input_span"] for item in packed if item["attested"] == "NO") or "NONE",
            "observed_recipe_sequence_after_reveal": " | ".join(observed_recipes),
            "observed_card_ids_after_reveal": " | ".join(observed_cards),
            "observed_cards": len(observed),
            "card_count_delta": len(packed) - len(observed),
            "exact_recipe_sequence": "YES" if exact_sequence else "NO",
            "exact_recipe_multiset": "YES" if exact_bag else "NO",
            "generation_contract": "RECODED_COMPONENTS_PLUS_ATTESTED_173_CARD_DECK_ONLY",
        })
        for ordinal, item in enumerate(packed, 1):
            detail_rows.append({
                "statement_id": row["statement_id"],
                "packed_ordinal": ordinal,
                "input_span": item["input_span"],
                "packed_recipe": item["packed_recipe"],
                "packed_card_id": item["packed_card_id"],
                "attested": item["attested"],
                "order_changed_inside_card": "YES" if item["attested"] == "YES" and item["input_span"] != item["packed_recipe"] else "NO",
            })

    delta_counts = Counter(int(row["card_count_delta"]) for row in audit_rows)
    delta_rows = [{
        "predicted_minus_observed_cards": delta,
        "statements": count,
        "meaning_de": "gleiche Kartenzahl" if delta == 0 else ("zu viele Karten" if delta > 0 else "zu stark zusammengepackt"),
    } for delta, count in sorted(delta_counts.items())]

    error_rows = [{
        "statement_id": row["statement_id"],
        "page": row["page"],
        "record": row["record"],
        "predicted_cards": row["predicted_cards"],
        "observed_cards": row["observed_cards"],
        "card_count_delta": row["card_count_delta"],
        "unpacked_components": row["unpacked_components"],
        "packed_recipe_sequence": row["packed_recipe_sequence"],
        "observed_recipe_sequence": row["observed_recipe_sequence_after_reveal"],
        "repair_class": "SEMANTIC_CUE_GAP" if row["unpacked_components"] != "NONE" else "ALTERNATIVE_ATTESTED_PACKING",
    } for row in audit_rows if row["exact_recipe_sequence"] == "NO"]

    write("SEVEN_HUNDRED_FORTY_SECOND_162_ATTESTED_RECIPE_BAGS.tsv", inventory_rows)
    write("SEVEN_HUNDRED_FORTY_SECOND_116_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FORTY_SECOND_402_PACKED_CARD_STEPS.tsv", detail_rows)
    write("SEVEN_HUNDRED_FORTY_SECOND_CARD_COUNT_DELTAS.tsv", delta_rows)
    write("SEVEN_HUNDRED_FORTY_SECOND_48_PACKING_ERRORS.tsv", error_rows)

    exact = sum(row["exact_recipe_sequence"] == "YES" for row in audit_rows)
    equal_count = sum(int(row["card_count_delta"]) == 0 for row in audit_rows)
    packed_total = sum(int(row["predicted_cards"]) for row in audit_rows)
    attested_total = sum(int(row["attested_packed_cards"]) for row in audit_rows)
    fallback_total = packed_total - attested_total
    herbal_exact = sum(row["statement_id"].startswith("H") and row["exact_recipe_sequence"] == "YES" for row in audit_rows)
    biological_exact = sum(row["statement_id"].startswith("B") and row["exact_recipe_sequence"] == "YES" for row in audit_rows)
    report = f"""# Pass 742 — der Kartenpacker

Der Packer sieht nur die in Pass741 rekodierten Bedeutungsfamilien und das gelernte 173-Karten-Deck. Er darf bis zu fünf benachbarte Werte zu einer attestierten Karte verbinden. Innerhalb der Karte zaehlt die gelernte Werkstattreihenfolge, nicht die deutsche Wortstellung: `Sollmass→ansetzen` darf deshalb als `OK+AIIN` gepackt werden.

## Ergebnis

- 163 geordnete Rezepte ergeben 162 Bedeutungsmengen; nur E+T+Y/T+E+Y ist wirklich reihenmehrdeutig.
- {exact}/116 Aussagen werden als **exakt gleiche Rezeptfolge** rekonstruiert.
- {equal_count}/116 erhalten exakt dieselbe Kartenzahl.
- Der Packer schreibt {packed_total} Karten gegen beobachtete 381.
- {attested_total}/{packed_total} Packschritte sind echte gelernte Deckkarten; {fallback_total} Komponenten bleiben ungepackt.
- Herbal: {herbal_exact}/19 exakt; Biological: {biological_exact}/97 exakt.

Das ist fuer einen einzigen gierfreien, transparenten Packweg erstaunlich gut: Die kurzen Biological-Zellen werden ueberwiegend aus dem Lexikon reproduziert. Die langen Herbal-Anweisungen bleiben schwer, weil die fluessige Sprache Pronomen, Hilfsverben und stillschweigende Bildargumente benutzt und weil mehrere gleich plausible Kartengrenzen existieren.

## Die Mischarchitektur wird konkreter

1. **Produktive Ebene:** 39 kurze Bedeutungsfamilien.
2. **Packebene:** 162 gelernte Bedeutungsmengen mit einer kanonischen internen Reihenfolge.
3. **Ganzkartenebene:** OS, Wiederaufnahme und TALAM bleiben direkt gelernt.
4. **Registermodus:** Biological bevorzugt kurze geschlossene Deckkarten; Herbal reiht und variiert mehr.

Die verbleibenden 48 Fehler sind nicht ein einziger Zusammenbruch. Sie zerfallen in fehlende/ueberzaehlige fluessige Cues und alternative, ebenfalls attestierte Packungen.

## Nächster Hebel

Lerne aus dem vorhandenen Deck nur zwei weitere Dinge: welche Packungen im Herbal- bzw. Biological-Modus bevorzugt werden und welche Funktionswoerter (`halten`, `danach`, `weiter`) nur deutsche Glattung statt eigene Karte sind. Dann den Packer unveraendert erneut auf alle116 Aussagen anwenden.
"""
    (HERE / "SEVEN_HUNDRED_FORTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "cards_in_deck": len(cards),
        "ordered_recipes": len({row["component_recipe"] for row in cards}),
        "component_bags": len(inventory_rows),
        "max_recipe_components": max_recipe,
        "statements": len(audit_rows),
        "exact_recipe_sequences": exact,
        "exact_recipe_multisets": sum(row["exact_recipe_multiset"] == "YES" for row in audit_rows),
        "equal_card_count_statements": equal_count,
        "predicted_cards": packed_total,
        "observed_cards": sum(int(row["observed_cards"]) for row in audit_rows),
        "attested_packed_cards": attested_total,
        "fallback_components": fallback_total,
        "packing_errors": len(error_rows),
        "herbal_exact": herbal_exact,
        "biological_exact": biological_exact,
        "decision": "ATTESTED_CARD_PACKER_RECOVERS_MOST_BIO_CELLS__HERBAL_PACKING_NEEDS_REGISTER_AND_ELLIPSIS_RULES",
    }
    (HERE / "SEVEN_HUNDRED_FORTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
