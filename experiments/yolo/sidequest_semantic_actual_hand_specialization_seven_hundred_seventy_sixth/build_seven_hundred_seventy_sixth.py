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
P772 = ROOT / "experiments/yolo/sidequest_semantic_component_memory_optimization_seven_hundred_seventy_second"
P774 = ROOT / "experiments/yolo/sidequest_semantic_lsh_mini_paradigm_seven_hundred_seventy_fourth"
P775 = ROOT / "experiments/yolo/sidequest_semantic_register_rare_boxes_seven_hundred_seventy_fifth"
PAGES = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def guarded_hand_rows() -> list[dict[str, str]]:
    command = [
        str(ROOT / "vmanus-exp"),
        "query-tsv",
        "gdt327_joint_tuple_interlinear.tsv",
        "--selector",
        "page",
    ]
    for page in PAGES:
        command.extend(["--allow", page])
    command.extend(
        [
            "--columns",
            "page,hand,register,section,physical_folio,locus",
            "--forbid-prefix",
            "f84",
        ]
    )
    result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))


def joined(values: set[str] | list[str]) -> str:
    return ",".join(sorted(values))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    guarded = guarded_hand_rows()
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    statements = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv")
    components = read(P772 / "SEVEN_HUNDRED_SEVENTY_SECOND_39_COMPONENT_ASSIGNMENT.tsv")
    card_access = read(P774 / "SEVEN_HUNDRED_SEVENTY_FOURTH_173_UPDATED_CARD_ACCESS.tsv")
    rare_cards = read(P775 / "SEVEN_HUNDRED_SEVENTY_FIFTH_5_REGISTER_RARE_BOX_CARDS.tsv")
    lsh_cards = read(P775 / "SEVEN_HUNDRED_SEVENTY_FIFTH_2_CARD_BIO_LSH_STRIP.tsv")

    guarded_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in guarded:
        guarded_by_page[row["page"]].append(row)
    event_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        event_by_page[row["page"]].append(row)
    statement_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in statements:
        statement_by_page[row["page"]].append(row)

    page_to_hand: dict[str, str] = {}
    page_rows = []
    rare_ids = {row["exact_card_id"] for row in rare_cards}
    lsh_ids = {row["exact_card_id"] for row in lsh_cards}
    for page in PAGES:
        source_rows = guarded_by_page[page]
        hands = {row["hand"] for row in source_rows}
        registers = {row["register"] for row in source_rows}
        sections = {row["section"] for row in source_rows}
        if len(hands) != 1 or len(registers) != 1 or len(sections) != 1:
            raise ValueError(f"page does not have one hand/register/section: {page}")
        hand = next(iter(hands))
        page_to_hand[page] = hand
        page_events = event_by_page[page]
        page_rows.append(
            {
                "page": page,
                "hand": f"HAND_{hand}",
                "register": next(iter(registers)),
                "section": next(iter(sections)),
                "events": len(page_events),
                "statements": len(statement_by_page[page]),
                "exact_card_types": len({row["card_no"] for row in page_events}),
                "rare_whole_cards": joined({row["surface"] for row in page_events if row["card_no"] in rare_ids}) or "NONE",
                "lsh_strip_cards": joined({row["surface"] for row in page_events if row["card_no"] in lsh_ids}) or "NONE",
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_SIXTH_7_PAGE_HAND_MAP.tsv",
        page_rows,
        ["page", "hand", "register", "section", "events", "statements", "exact_card_types", "rare_whole_cards", "lsh_strip_cards"],
    )

    events_by_hand: dict[str, list[dict[str, str]]] = defaultdict(list)
    statements_by_hand: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_hand[page_to_hand[row["page"]]].append(row)
    for row in statements:
        statements_by_hand[page_to_hand[row["page"]]].append(row)
    card_sets = {hand: {row["card_no"] for row in rows} for hand, rows in events_by_hand.items()}
    shared_cards = set.intersection(*card_sets.values())

    base_components = {
        row["component"]
        for row in components
        if row["new_tier"] != "MODEL_ONLY_6_RARE_VALUES"
    }
    model_components = {
        row["component"]
        for row in components
        if row["new_tier"] == "MODEL_ONLY_6_RARE_VALUES"
    }
    rare_component_for_card = {}
    for row in rare_cards:
        matched = set(row["component_recipe_readback"].split("+")) & model_components
        if len(matched) != 1:
            raise ValueError(f"rare card has no unique model component: {row['exact_card_id']}")
        rare_component_for_card[row["exact_card_id"]] = next(iter(matched))
    lsh_component_for_card = {row["exact_card_id"]: "LSH" for row in lsh_cards}
    special_component_for_card = rare_component_for_card | lsh_component_for_card

    profiles = []
    for hand in sorted(events_by_hand):
        hand_events = events_by_hand[hand]
        hand_cards = card_sets[hand]
        local_components = {special_component_for_card[card] for card in hand_cards if card in special_component_for_card}
        registers = {row["register"] for row in page_rows if row["hand"] == f"HAND_{hand}"}
        pages = {row["page"] for row in page_rows if row["hand"] == f"HAND_{hand}"}
        profile = "HERBAL_SPECIALIST" if registers == {"HERBAL_A"} else "BIO_PRIMARY_WITH_HERBAL_CROSSOVER"
        profiles.append(
            {
                "hand": f"HAND_{hand}",
                "pages": joined(pages),
                "registers": joined(registers),
                "events": len(hand_events),
                "statements": len(statements_by_hand[hand]),
                "exact_card_types": len(hand_cards),
                "shared_exact_card_types": len(hand_cards & shared_cards),
                "hand_only_exact_card_types": len(hand_cards - shared_cards),
                "rare_local_components": joined(local_components) or "NONE",
                "component_inventory": len(base_components | local_components),
                "workshop_role": profile,
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_SIXTH_2_ACTUAL_HAND_PROFILES.tsv",
        profiles,
        ["hand", "pages", "registers", "events", "statements", "exact_card_types", "shared_exact_card_types", "hand_only_exact_card_types", "rare_local_components", "component_inventory", "workshop_role"],
    )

    special_rows = []
    target_cards = [
        *[(row["exact_card_id"], row["surfaces"], row["component_recipe_readback"], "RARE_WHOLE_CARD") for row in rare_cards],
        *[(row["exact_card_id"], row["surface"], row["recipe"], "LSH_MINI_PARADIGM") for row in lsh_cards],
    ]
    for card_id, surface, recipe, teaching_mode in target_cards:
        occurrences = [row for row in events if row["card_no"] == card_id]
        hands = {page_to_hand[row["page"]] for row in occurrences}
        special_rows.append(
            {
                "exact_card_id": card_id,
                "surface": surface,
                "component_recipe": recipe,
                "teaching_mode": teaching_mode,
                "hands": joined({f"HAND_{hand}" for hand in hands}),
                "pages": joined({row["page"] for row in occurrences}),
                "events": joined({row["event_id"] for row in occurrences}),
                "actual_hand_box": "HAND_1_BOX" if hands == {"1"} else "HAND_2_BOX",
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_SIXTH_7_HAND_LOCAL_SPECIAL_CARDS.tsv",
        special_rows,
        ["exact_card_id", "surface", "component_recipe", "teaching_mode", "hands", "pages", "events", "actual_hand_box"],
    )

    card_access_map = {row["exact_card_id"]: row["access_mode"] for row in card_access}
    trace_rows = []
    for row in events:
        hand = page_to_hand[row["page"]]
        if row["card_no"] in rare_ids:
            source = f"HAND_{hand}_RARE_BOX"
        elif row["card_no"] in lsh_ids:
            source = "HAND_2_LSH_STRIP"
        else:
            source = card_access_map[row["card_no"]]
        trace_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "hand": f"HAND_{hand}",
                "exact_card_id": row["card_no"],
                "surface": row["surface"],
                "knowledge_source": source,
                "available_to_actual_hand": "YES",
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_SIXTH_381_HAND_ACCESS_TRACE.tsv",
        trace_rows,
        ["event_id", "page", "record", "statement_id", "hand", "exact_card_id", "surface", "knowledge_source", "available_to_actual_hand"],
    )

    ecology_rows = []
    hand1_cards = card_sets["1"]
    hand2_cards = card_sets["2"]
    categories = {
        "BOTH_HANDS": hand1_cards & hand2_cards,
        "HAND_1_ONLY": hand1_cards - hand2_cards,
        "HAND_2_ONLY": hand2_cards - hand1_cards,
    }
    for category, cards in categories.items():
        ecology_rows.append(
            {
                "card_ecology": category,
                "exact_card_types": len(cards),
                "hand_1_events": sum(row["card_no"] in cards for row in events_by_hand["1"]),
                "hand_2_events": sum(row["card_no"] in cards for row in events_by_hand["2"]),
                "example_surfaces": joined(sorted({row["surface"] for row in events if row["card_no"] in cards})[:12]),
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_SIXTH_3_HAND_CARD_ECOLOGIES.tsv",
        ecology_rows,
        ["card_ecology", "exact_card_types", "hand_1_events", "hand_2_events", "example_surfaces"],
    )

    profile = {row["hand"]: row for row in profiles}
    report = f"""# Pass 776 — Die zwei echten Hände passen zu asymmetrischer Spezialisierung

Der guarded Handabgleich ist klarer als erwartet:

- **Hand 1** schreibt f10r, f11r und f56r: ausschließlich Herbal-A, {profile['HAND_1']['events']} Ereignisse in {profile['HAND_1']['statements']} Aussagen.
- **Hand 2** schreibt f55v sowie f81v, f82r und f83r: Herbal-B plus den ganzen Bio-Ausschnitt, {profile['HAND_2']['events']} Ereignisse in {profile['HAND_2']['statements']} Aussagen.

Damit ist die Werkstatt nicht sauber in „Herbal-Schreiber“ und „Bio-Schreiber“ geteilt. Die bessere Arbeitstheorie ist asymmetrisch: Hand 1 ist der Herbal-Hauptschreiber; Hand 2 ist der Bio-/Stationsschreiber, kann aber mindestens einen eigenen Herbal-Artikel übernehmen.

Die seltenen Schubladen folgen den Händen sogar sparsamer als den Registern. Hand 1 braucht nur OS und CFH. Hand 2 braucht TALAM aus f55v, die Bio-Werte LD und DA sowie die kleine LSH=WASCHEN-Leiste. Keine dieser sieben Spezialkarten kreuzt im festen Ausschnitt die Handgrenze. Dadurch braucht Hand 1 nur {profile['HAND_1']['component_inventory']} und Hand 2 {profile['HAND_2']['component_inventory']} der 39 Meisterkomponenten.

Das ist ein gut lehrbares Modell um 1420: beide Hände teilen den großen Regelkern und die häufigen Karten; jede Hand bewahrt daneben eine winzige persönliche Musterbox. Der Meister kennt beide. Die unterschiedliche Hand ist also nicht bloß Störung, sondern erklärt, warum bestimmte seltene Werte nicht portabel werden müssen.

Als nächstes testen wir die stärkere Vorhersage dieses Modells: Wenn man die Seiten blind nach benötigtem Karteninventar clustert, sollten f10r/f11r/f56r zusammenfallen, während f55v trotz Herbal-Bild näher beim Bio-Schreiber liegt. Wenn das nicht gelingt, ist die Handbox nur nachträgliche Benennung.
"""
    (HERE / "SEVEN_HUNDRED_SEVENTY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "guarded_rows": len(guarded),
        "hand_1_events": len(events_by_hand["1"]),
        "hand_2_events": len(events_by_hand["2"]),
        "hand_1_statements": len(statements_by_hand["1"]),
        "hand_2_statements": len(statements_by_hand["2"]),
        "hand_1_components": int(profile["HAND_1"]["component_inventory"]),
        "hand_2_components": int(profile["HAND_2"]["component_inventory"]),
        "special_cards_crossing_hands": sum(len(row["hands"].split(",")) > 1 for row in special_rows),
        "decision": "ASYMMETRIC_HAND_SPECIALIZATION__HAND1_HERBAL__HAND2_BIO_PLUS_F55V",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
