#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
PAGES = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"]
HAND = {"f10r": "1", "f11r": "1", "f56r": "1", "f55v": "2", "f81v": "2", "f82r": "2", "f83r": "2"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def guarded_layout() -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", "gdt327_joint_tuple_interlinear.tsv", "--selector", "page"]
    for page in PAGES:
        command.extend(["--allow", page])
    command.extend(
        [
            "--columns",
            "page,locus,group_index,hand,observed_wrapper,line_first,prev_dy,joint_tuple_id",
            "--forbid-prefix",
            "f84",
        ]
    )
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))


def join(values: set[str] | list[str]) -> str:
    return ",".join(sorted(values))


def counter_text(counter: Counter[str]) -> str:
    return ",".join(f"{key}:{counter[key]}" for key in sorted(counter))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    layout = guarded_layout()
    events_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    layout_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_page[row["page"]].append(row)
    for row in layout:
        layout_by_page[row["page"]].append(row)
    joined_rows = []
    for page in PAGES:
        if len(events_by_page[page]) != len(layout_by_page[page]):
            raise ValueError(f"page alignment count mismatch: {page}")
        for event, formal in zip(events_by_page[page], layout_by_page[page]):
            if formal["hand"] != HAND[page]:
                raise ValueError(f"hand mismatch: {page}")
            joined_rows.append({**event, **formal})

    by_card_hand: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    by_recipe_hand: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in joined_rows:
        by_card_hand[row["card_no"]][row["hand"]].append(row)
        by_recipe_hand[row["component_recipe"]][row["hand"]].append(row)
    shared_cards = {card for card, hands in by_card_hand.items() if set(hands) == {"1", "2"}}
    shared_recipes = {recipe for recipe, hands in by_recipe_hand.items() if set(hands) == {"1", "2"}}

    card_rows = []
    for card in sorted(shared_cards):
        hand1 = by_card_hand[card]["1"]
        hand2 = by_card_hand[card]["2"]
        surfaces1 = {row["surface"] for row in hand1}
        surfaces2 = {row["surface"] for row in hand2}
        overlap = surfaces1 & surfaces2
        context_marked = any(row["line_first"] == "1" or row["prev_dy"] == "1" for row in hand1 + hand2)
        if overlap:
            status = "PORTABLE_SURFACE_EXISTS"
        elif context_marked:
            status = "DISJOINT_SURFACES__POSITION_AND_HAND_MIXED"
        else:
            status = "DISJOINT_SURFACES__HAND_OR_REGISTER_CANDIDATE"
        card_rows.append(
            {
                "exact_card_id": card,
                "component_recipe": hand1[0]["component_recipe"],
                "reading_de": hand1[0]["rebuilt_reading_de"],
                "hand_1_events": len(hand1),
                "hand_1_surfaces": join(surfaces1),
                "hand_1_wrappers": counter_text(Counter(row["observed_wrapper"] for row in hand1)),
                "hand_2_events": len(hand2),
                "hand_2_surfaces": join(surfaces2),
                "hand_2_wrappers": counter_text(Counter(row["observed_wrapper"] for row in hand2)),
                "surface_overlap": join(overlap) or "NONE",
                "variant_status": status,
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_EIGHTH_12_SHARED_CARD_VARIANTS.tsv",
        card_rows,
        ["exact_card_id", "component_recipe", "reading_de", "hand_1_events", "hand_1_surfaces", "hand_1_wrappers", "hand_2_events", "hand_2_surfaces", "hand_2_wrappers", "surface_overlap", "variant_status"],
    )

    shared_event_rows = []
    for row in joined_rows:
        if row["card_no"] not in shared_cards:
            continue
        shared_event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "hand": f"HAND_{row['hand']}",
                "locus": row["locus"],
                "group_index": row["group_index"],
                "line_first": row["line_first"],
                "prev_dy": row["prev_dy"],
                "exact_card_id": row["card_no"],
                "component_recipe": row["component_recipe"],
                "surface": row["surface"],
                "observed_wrapper": row["observed_wrapper"],
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_EIGHTH_106_SHARED_CARD_EVENTS.tsv",
        shared_event_rows,
        ["event_id", "page", "hand", "locus", "group_index", "line_first", "prev_dy", "exact_card_id", "component_recipe", "surface", "observed_wrapper"],
    )

    recipe_rows = []
    for recipe in sorted(shared_recipes):
        hand1 = by_recipe_hand[recipe]["1"]
        hand2 = by_recipe_hand[recipe]["2"]
        cards1 = {row["card_no"] for row in hand1}
        cards2 = {row["card_no"] for row in hand2}
        recipe_rows.append(
            {
                "component_recipe": recipe,
                "hand_1_exact_cards": join(cards1),
                "hand_1_surfaces": join({row["surface"] for row in hand1}),
                "hand_1_events": len(hand1),
                "hand_2_exact_cards": join(cards2),
                "hand_2_surfaces": join({row["surface"] for row in hand2}),
                "hand_2_events": len(hand2),
                "shared_exact_cards": join(cards1 & cards2) or "NONE",
                "relationship": "SHARED_EXACT_CARD_PRESENT" if cards1 & cards2 else "DISJOINT_EXACT_CARD_ALTERNANTS",
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_EIGHTH_13_SHARED_RECIPE_REALIZATIONS.tsv",
        recipe_rows,
        ["component_recipe", "hand_1_exact_cards", "hand_1_surfaces", "hand_1_events", "hand_2_exact_cards", "hand_2_surfaces", "hand_2_events", "shared_exact_cards", "relationship"],
    )

    crossover_cards = ["PROC009", "PROC016", "PROC019"]
    crossover_rows = []
    hand1_pages = {"f10r", "f11r", "f56r"}
    for card in crossover_cards:
        hand1 = [row for row in joined_rows if row["card_no"] == card and row["page"] in hand1_pages]
        f55 = [row for row in joined_rows if row["card_no"] == card and row["page"] == "f55v"]
        eligible1 = [row for row in hand1 if row["line_first"] == "0" and row["prev_dy"] == "0"]
        eligible2 = [row for row in f55 if row["line_first"] == "0" and row["prev_dy"] == "0"]
        crossover_rows.append(
            {
                "exact_card_id": card,
                "component_recipe": hand1[0]["component_recipe"],
                "hand_1_surfaces": join({row["surface"] for row in hand1}),
                "hand_1_nonentry_events": len(eligible1),
                "hand_1_nonentry_bare": sum(row["observed_wrapper"] == "NONE" for row in eligible1),
                "f55v_hand_2_surfaces": join({row["surface"] for row in f55}),
                "f55v_nonentry_events": len(eligible2),
                "f55v_nonentry_bare": sum(row["observed_wrapper"] == "NONE" for row in eligible2),
                "workshop_reading": "SAME_CARD__HAND2_ALLOWS_BARE_REALIZATION" if any(row["observed_wrapper"] == "NONE" for row in eligible2) else "SAME_CARD__PORTABLE_MARKED_REALIZATION",
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_EIGHTH_3_HERBAL_CROSSOVER_CARDS.tsv",
        crossover_rows,
        ["exact_card_id", "component_recipe", "hand_1_surfaces", "hand_1_nonentry_events", "hand_1_nonentry_bare", "f55v_hand_2_surfaces", "f55v_nonentry_events", "f55v_nonentry_bare", "workshop_reading"],
    )

    def profile(label: str, rows: list[dict[str, str]]) -> dict[str, object]:
        eligible = [row for row in rows if row["line_first"] == "0" and row["prev_dy"] == "0"]
        bare = sum(row["observed_wrapper"] == "NONE" for row in eligible)
        return {
            "profile": label,
            "eligible_events": len(eligible),
            "bare_events": bare,
            "bare_fraction": f"{bare / len(eligible):.6f}",
            "wrapper_counts": counter_text(Counter(row["observed_wrapper"] for row in eligible)),
        }

    shared_rows = [row for row in joined_rows if row["card_no"] in shared_cards]
    core_rows = [row for row in joined_rows if row["card_no"] in set(crossover_cards)]
    wrapper_profiles = [
        profile("HAND_1_ALL_SHARED_CARDS", [row for row in shared_rows if row["hand"] == "1"]),
        profile("HAND_2_ALL_SHARED_CARDS", [row for row in shared_rows if row["hand"] == "2"]),
        profile("HAND_1_HERBAL_CROSSOVER_CORE", [row for row in core_rows if row["page"] in hand1_pages]),
        profile("HAND_2_F55V_CROSSOVER_CORE", [row for row in core_rows if row["page"] == "f55v"]),
    ]
    write(
        "SEVEN_HUNDRED_SEVENTY_EIGHTH_4_WRAPPER_PROFILES.tsv",
        wrapper_profiles,
        ["profile", "eligible_events", "bare_events", "bare_fraction", "wrapper_counts"],
    )

    disjoint_surface_cards = sum(row["surface_overlap"] == "NONE" for row in card_rows)
    disjoint_recipe = [row for row in recipe_rows if row["relationship"] == "DISJOINT_EXACT_CARD_ALTERNANTS"]
    report = f"""# Pass 778 — Kleines Handvariantenlexikon

Beide Hände teilen13 Komponentenrezepturen mit114 Ereignissen. Zwölf exakte Karten treten in beiden Händen auf und tragen106 Ereignisse. Das Grundvokabular ist also real gemeinsam, seine sichtbare Schreibung aber nicht starr.

Bei {disjoint_surface_cards}/12 gemeinsamen Karten überlappen die sichtbaren Oberflächen der beiden Hände überhaupt nicht. Ein Teil davon hängt mit Zeilenanfang oder vorangehendem Schluss zusammen. Zwei Familien bleiben selbst ohne diese Umstände als klare Hand-/Registerkandidaten übrig. Noch anschaulicher ist der echte Herbal-Crossover f55v:

- AIIN: Hand 1 `daiin/taiin`, Hand 2 auf f55v `chaiin/daiin/aiin`;
- OR: Hand 1 `chor/shor`, Hand 2 auf f55v schlicht `or`;
- Y: Hand 1 `dy/chy/shy`, Hand 2 auf f55v schlicht `y`.

Die nackten f55v-Formen `or` und `y` stehen intern, nicht am Zeilenanfang und nicht nach einem Schluss. Damit kann die Kürzung nicht bloß aus der bekannten Randregel kommen. Im gemeinsamen Kartenkern sind nach Ausschluss dieser beiden Positionslagen bei Hand 1 nur4/33 Formen nackt, bei Hand 2 dagegen13/48. Im streng vergleichbaren Herbal-Kern sind es0/18 gegen2/3.

Arbeitsregel: **Hand 2 darf einfache Karten häufiger ohne Eintrittshülle schreiben; Hand 1 bevorzugt markierte `ch/d/sh`-Formen.** Das ändert keine Bedeutung. Es ist eine Schreiberallographie über demselben Komponenten- und Kartenlexikon.

Nur eine der13 gemeinsamen Rezepturen (`OK+OL`) verwendet vollständig getrennte exakte Karten: Hand 1 `okchol`, Hand 2 `qokol`. Sie bleibt ein besonders guter Kandidat für zwei gelernte Ganzkarten mit derselben Werkstattanweisung.

Als nächstes rendern wir kurze Passagen wechselseitig in der anderen Hand: f55v mit Hand-1-Vorzugsformen und einen f10r-Ausschnitt mit Hand-2-Vorzugsformen. Wenn die zugrunde liegende Lesung dabei unverändert und der sichtbare Stil deutlich verschieden bleibt, haben wir ein praktisch lehrbares Mehrschreibersystem.
"""
    (HERE / "SEVEN_HUNDRED_SEVENTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "shared_recipes": len(recipe_rows),
        "shared_recipe_events": sum(int(row["hand_1_events"]) + int(row["hand_2_events"]) for row in recipe_rows),
        "shared_exact_cards": len(card_rows),
        "shared_exact_card_events": len(shared_event_rows),
        "disjoint_surface_cards": disjoint_surface_cards,
        "disjoint_exact_card_recipe_alternants": len(disjoint_recipe),
        "decision": "SHARED_COMPONENT_LEXICON__HAND2_BARE_REALIZATION_BIAS__ONE_WHOLE_CARD_ALTERNANT",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
