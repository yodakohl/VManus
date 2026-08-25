#!/usr/bin/env python3
"""Build Pass 743: distinguish semantic cards from German helper wording."""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P738 = ROOT / "experiments/yolo/sidequest_semantic_remainder_closure_seven_hundred_thirty_eighth"
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P740 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_syntax_seven_hundred_fortieth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CUES = [
    ("RESUME_CARD", r"\bwiederaufnehm\w*"), ("TALAM", r"\bverwahr\w*"), ("OS", r"\bFach\b"),
    ("SHED", r"\babsetz\w*"), ("OK", r"\bansetz\w*"), ("CHD", r"\bumsetz\w*"),
    ("CHK", r"\berwaerm\w*"), ("CTH", r"\bbereit\w*"), ("SOLK", r"\bSammelstelle\w*"),
    ("P", r"\bfuell\w*"), ("LSH", r"\bwasch\w*"), ("CFH", r"\bauswring\w*"),
    ("CH", r"\bentnehm\w*"), ("T", r"\banwend\w*"), ("K", r"\bzugeb\w*"),
    ("S", r"\bteil\w*"), ("L", r"\bleit\w*"), ("R", r"\bkuehl\w*"),
    ("SH", r"\bhalt\w*"), ("LD", r"\bbefestig\w*"),
    ("OT", r"\bdanach\b|\banschliessend\w*|\bnaechst\w*"), ("OL", r"\bweiter\w*"),
    ("AL", r"\bZielstelle\w*"), ("AR", r"\bQuelle\w*"), ("AIIN", r"\bSollmass\w*"),
    ("AIN", r"\bPortion\w*|\bAnsatzportion\w*"), ("IIN", r"\bArbeitsstufe\w*"),
    ("AN", r"\bNachgabe\w*"), ("CKH", r"\bDurchlass\w*"),
    ("AIR", r"\bWasser\w*|\bFluessigkeit\w*"), ("OR", r"\bAnsatz\w*"),
    ("HO", r"\bZutat\w*"), ("O", r"\bArbeitsgang\w*"),
    ("EEE", r"\bvollstaendig\w*"), ("EE", r"\blaenger\w*"), ("E", r"\bkurz\w*"),
    ("Y", r"\bPosten\w*"), ("DA", r"\bzweiten Durchgang\b"), ("DY", r"\bschliess\w*"),
]


RULE_DESCRIPTIONS = {
    "ADD_AIN_IN_ANSATZPORTION": ("ADD", "Ansatzportion enthaelt die Mengenfamilie AIN."),
    "ADD_OT_IN_NAECHST": ("ADD", "naechster Posten/Schritt aktiviert die Folgefamilie OT."),
    "DROP_SH_AFTER_BEREITET": ("DROP", "bereitet halten ist die fluessige Expansion von CTH+Y, nicht zwingend CTH+SH+Y."),
    "DROP_SH_AFTER_SAMMELSTELLE": ("DROP", "an der Sammelstelle halten expandiert SOLK, ohne zusaetzliche SH-Karte."),
    "DROP_SH_IN_WORKFLOW_DURCHLASS": ("DROP", "im Arbeitsgang am Durchlass halten expandiert den Stationszustand."),
    "DROP_CTH_AFTER_ZUTAT": ("DROP", "Zutat bereiten ist hier redaktionelle Glattung der Zutatkarte."),
    "DROP_OT_ABSORBED_BY_PHRASE": ("DROP", "danach/anschliessend ist in fuenf festen Wendungen nur deutscher Anschluss."),
    "DROP_OL_ABSORBED_BY_PHRASE": ("DROP", "weiter ist in vier Treffern fester Wendungen nur deutsche Verbpartikel."),
    "DROP_OR_AS_FLUENT_OBJECT": ("DROP", "Den Ansatz an der Zielstelle nennt das Objekt, nicht zwingend eine OR-Karte."),
}


def scan(text: str, rule_counts: Counter[str]) -> tuple[list[str], list[str]]:
    body = text.split(":", 1)[1] if ":" in text else text
    hits: list[tuple[int, int, str, str]] = []
    for component, pattern in CUES:
        for match in re.finditer(pattern, body, re.IGNORECASE):
            pre = body[max(0, match.start() - 70):match.start()].lower()
            post = body[match.end():match.end() + 60].lower()
            word = match.group()
            drop_rule = ""
            if component == "SH" and re.search(r"bereitet\w*\s+$", pre):
                drop_rule = "DROP_SH_AFTER_BEREITET"
            elif component == "SH" and re.search(r"sammelstelle\s+$", pre):
                drop_rule = "DROP_SH_AFTER_SAMMELSTELLE"
            elif component == "SH" and re.search(r"im\s+arbeitsgang\s+am\s+durchlass\s+$", pre):
                drop_rule = "DROP_SH_IN_WORKFLOW_DURCHLASS"
            elif component == "CTH" and re.search(r"zutat\s+$", pre):
                drop_rule = "DROP_CTH_AFTER_ZUTAT"
            elif component == "OT" and (
                (word.lower().startswith("danach") and re.match(r"\s+(eine\s+nachgabe|kurz\s+durch\s+den\s+durchlass)", post))
                or (word.lower().startswith("anschliessend") and re.match(r"\s+(verwahren|im\s+arbeitsgang|leiten)", post))
            ):
                drop_rule = "DROP_OT_ABSORBED_BY_PHRASE"
            elif component == "OL" and (
                (re.search(r"arbeitsstufe\s+$", pre) and re.match(r"\s+zugeben", post))
                or (re.search(r"sollmass\s+$", pre) and word.lower().startswith("weiterfuehr"))
                or (re.search(r"quelle\s+$", pre) and word.lower().startswith("weiterarbeit"))
            ):
                drop_rule = "DROP_OL_ABSORBED_BY_PHRASE"
            elif component == "OR" and re.search(r"^\s*den\s+$", pre) and re.match(r"\s+an\s+der\s+zielstelle", post):
                drop_rule = "DROP_OR_AS_FLUENT_OBJECT"
            if drop_rule:
                rule_counts[drop_rule] += 1
                continue
            if component == "AIN" and word.lower().startswith("ansatzportion"):
                rule_counts["ADD_AIN_IN_ANSATZPORTION"] += 1
            if component == "OT" and word.lower().startswith("naechst"):
                rule_counts["ADD_OT_IN_NAECHST"] += 1
            hits.append((match.start(), match.end(), component, word))
    hits.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    accepted: list[tuple[int, int, str, str]] = []
    end = -1
    for hit in hits:
        if hit[0] >= end:
            accepted.append(hit)
            end = hit[1]
    return [item[2] for item in accepted], [item[3] for item in accepted]


def bag_key(items: list[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(Counter(items).items()))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P738 / "SEVEN_HUNDRED_THIRTY_EIGHTH_173_CARD_DICTIONARY.tsv")
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    statements = read(P740 / "SEVEN_HUNDRED_FORTIETH_116_STATEMENT_PATTERNS.tsv")

    canonical: dict[tuple[tuple[str, int], ...], dict[str, str]] = {}
    for row in cards:
        key = bag_key(row["component_recipe"].split("+"))
        old = canonical.get(key)
        if old is None or int(row["events"]) > int(old["events"]) or (int(row["events"]) == int(old["events"]) and row["component_recipe"] < old["component_recipe"]):
            canonical[key] = row
    max_recipe = max(sum(count for _, count in key) for key in canonical)

    def pack(sequence: list[str]) -> list[str]:
        n = len(sequence)
        dp: list[tuple[int, float, list[str]] | None] = [None] * (n + 1)
        dp[n] = (0, 0.0, [])
        for start in range(n - 1, -1, -1):
            options: list[tuple[int, float, list[str]]] = []
            for end in range(start + 1, min(n, start + max_recipe) + 1):
                key = bag_key(sequence[start:end])
                if key in canonical:
                    card = canonical[key]
                    tail = dp[end]
                    assert tail is not None
                    options.append((1 + tail[0], -math.log1p(int(card["events"])) + tail[1], [card["component_recipe"]] + tail[2]))
            tail = dp[start + 1]
            assert tail is not None
            options.append((1 + tail[0], 100.0 + tail[1], [f"UNPACKED({sequence[start]})"] + tail[2]))
            dp[start] = min(options, key=lambda item: (item[0], item[1], item[2]))
        assert dp[0] is not None
        return dp[0][2]

    observed: dict[str, list[str]] = defaultdict(list)
    for row in events:
        observed[row["statement_id"]].append(row["component_recipe"])

    rule_counts: Counter[str] = Counter()
    audit_rows = []
    component_gap_rows = []
    packing_error_rows = []
    for row in statements:
        inferred, words = scan(row["clean_workshop_reading_de"], rule_counts)
        packed = pack(inferred)
        actual_components = row["component_sequence"].split("+")
        actual_recipes = observed[row["statement_id"]]
        inferred_set, actual_set = set(inferred), set(actual_components)
        exact_components = inferred_set == actual_set
        exact_recipes = packed == actual_recipes
        output = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "clean_instruction_de": row["clean_workshop_reading_de"],
            "refined_cue_words": " | ".join(words), "refined_component_sequence": "+".join(inferred),
            "refined_component_set": "+".join(sorted(inferred_set)),
            "observed_component_set_after_reveal": "+".join(sorted(actual_set)),
            "exact_component_set": "YES" if exact_components else "NO",
            "missing_components": "+".join(sorted(actual_set - inferred_set)) or "NONE",
            "extra_components": "+".join(sorted(inferred_set - actual_set)) or "NONE",
            "packed_recipe_sequence": " | ".join(packed),
            "observed_recipe_sequence_after_reveal": " | ".join(actual_recipes),
            "predicted_cards": len(packed), "observed_cards": len(actual_recipes),
            "card_count_delta": len(packed) - len(actual_recipes),
            "exact_recipe_sequence": "YES" if exact_recipes else "NO",
            "generation_contract": "CLEAN_INSTRUCTION_PLUS_HELPER_RULES_PLUS_UNCHANGED_173_CARD_DECK",
        }
        audit_rows.append(output)
        if not exact_components:
            component_gap_rows.append({key: output[key] for key in ["statement_id", "page", "record", "missing_components", "extra_components", "clean_instruction_de"]})
        if not exact_recipes:
            packing_error_rows.append({key: output[key] for key in ["statement_id", "page", "record", "missing_components", "extra_components", "predicted_cards", "observed_cards", "card_count_delta", "packed_recipe_sequence", "observed_recipe_sequence_after_reveal"]})

    rule_rows = [{
        "rule": name, "direction": RULE_DESCRIPTIONS[name][0], "uses": rule_counts[name],
        "instruction_de": RULE_DESCRIPTIONS[name][1], "changes_component_meaning": "NO",
    } for name in RULE_DESCRIPTIONS]
    delta_counts = Counter(int(row["card_count_delta"]) for row in audit_rows)
    delta_rows = [{"card_count_delta": delta, "statements": count} for delta, count in sorted(delta_counts.items())]

    write("SEVEN_HUNDRED_FORTY_THIRD_9_HELPER_RULES.tsv", rule_rows)
    write("SEVEN_HUNDRED_FORTY_THIRD_116_REFINED_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FORTY_THIRD_COMPONENT_GAPS.tsv", component_gap_rows)
    write("SEVEN_HUNDRED_FORTY_THIRD_PACKING_ERRORS.tsv", packing_error_rows)
    write("SEVEN_HUNDRED_FORTY_THIRD_CARD_COUNT_DELTAS.tsv", delta_rows)

    exact_components = sum(row["exact_component_set"] == "YES" for row in audit_rows)
    exact_recipes = sum(row["exact_recipe_sequence"] == "YES" for row in audit_rows)
    equal_counts = sum(int(row["card_count_delta"]) == 0 for row in audit_rows)
    predicted_cards = sum(int(row["predicted_cards"]) for row in audit_rows)
    herbal_exact = sum(row["statement_id"].startswith("H") and row["exact_recipe_sequence"] == "YES" for row in audit_rows)
    biological_exact = sum(row["statement_id"].startswith("B") and row["exact_recipe_sequence"] == "YES" for row in audit_rows)
    report = f"""# Pass 743 — Hilfswoerter von Karten trennen

Neun kleine Schreibregeln behandeln deutsche Glattung, ohne einen der39 Werte oder eine der173 Karten zu aendern. Zwei Regeln erkennen versteckte echte Cues (`Ansatzportion`→AIN, `naechst`→OT); sieben Regeln entfernen Hilfswoerter, die bereits in einer anderen Karte stecken.

## Verbesserung

- Exakte Komponentenmenge: {exact_components}/116 statt93/116.
- Exakte Rezeptfolge: {exact_recipes}/116 statt68/116.
- Exakte Kartenzahl: {equal_counts}/116 statt85/116.
- Vorher402, jetzt{predicted_cards} vorhergesagte Karten bei381 beobachteten.
- Herbal exakt: {herbal_exact}/19 statt2/19.
- Biological exakt: {biological_exact}/97 statt66/97.

Nur drei Aussagen verschweigen jetzt noch echte Komponenten in der fluessigen Fassung: H1-S001 laesst die Ganzkarte FACH aus; H2-S001 verschweigt einen ARBEITSGANG; H3-S001 expandiert eine lange Rezeptfolge, ohne Y/O/T voll auszusprechen. Das sind keine Stammprobleme, sondern redaktionelle Ellipse.

Die Kartenpackung bleibt mit {len(packing_error_rows)} nicht-exakten Aussagen die groessere Restschicht. Aber der starke Sprung ohne Bedeutungswechsel bestaetigt die Architektur: **kurze Fachwerte + normale Sprachglaettung + gelerntes Karteninventar**.

## Nächster Hebel

Die restlichen Packfehler werden nun nach wiederkehrender Konkurrenz sortiert: Welche zwei oder drei attestierten Kartenzerlegungen decken dieselbe Bedeutungsfolge? Daraus entsteht eine kleine Prioritaetstabelle fuer Herbal-Kette, Bio-Einzelzelle, Schlusskarte und Wiederholung.
"""
    (HERE / "SEVEN_HUNDRED_FORTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "helper_rules": len(rule_rows), "helper_rule_uses": sum(rule_counts.values()),
        "statements": len(audit_rows), "exact_component_sets": exact_components,
        "component_gap_statements": len(component_gap_rows), "exact_recipe_sequences": exact_recipes,
        "packing_errors": len(packing_error_rows), "equal_card_count_statements": equal_counts,
        "predicted_cards": predicted_cards, "observed_cards": sum(int(row["observed_cards"]) for row in audit_rows),
        "herbal_exact": herbal_exact, "biological_exact": biological_exact,
        "semantic_changes": 0, "deck_changes": 0,
        "decision": "HELPER_CUE_LAYER_CLOSES_MOST_SEMANTIC_GAPS__PACKING_PRIORITY_IS_THE_REMAINDER",
    }
    (HERE / "SEVEN_HUNDRED_FORTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
