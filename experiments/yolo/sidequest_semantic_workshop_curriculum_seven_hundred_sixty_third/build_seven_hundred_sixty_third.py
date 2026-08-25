#!/usr/bin/env python3
"""Build Pass 763: a plausible multi-scribe workshop curriculum."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P738 = ROOT / "experiments/yolo/sidequest_semantic_remainder_closure_seven_hundred_thirty_eighth"
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P760 = ROOT / "experiments/yolo/sidequest_semantic_parameterized_apprentice_rules_seven_hundred_sixtieth"
P761 = ROOT / "experiments/yolo/sidequest_semantic_large_formula_parameterization_seven_hundred_sixty_first"
P757 = ROOT / "experiments/yolo/sidequest_semantic_large_formula_motifs_seven_hundred_fifty_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def domain(page: str) -> str:
    return "HERBAL" if page in {"f10r", "f11r", "f55v", "f56r"} else "BIO"


def scope_from_statements(statement_ids: str) -> str:
    scopes = {"HERBAL" if item.startswith("H") else "BIO" for item in statement_ids.split(",") if item}
    if scopes == {"HERBAL", "BIO"}:
        return "COMMON_HERBAL_BIO"
    return next(iter(scopes)) + "_SPECIALIST"


def main() -> None:
    components = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_39_COMPONENT_DICTIONARY.tsv")
    cards = read(P738 / "SEVEN_HUNDRED_THIRTY_EIGHTH_173_CARD_DICTIONARY.tsv")
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    rules = read(P760 / "SEVEN_HUNDRED_SIXTIETH_9_PARAMETERIZED_RULES.tsv")
    motifs = read(P757 / "SEVEN_HUNDRED_FIFTY_SEVENTH_8_SHARED_CARD_MOTIFS.tsv")
    tails = read(P761 / "SEVEN_HUNDRED_SIXTY_FIRST_19_LOCAL_TAIL_STRIPS.tsv")

    ranked_components = sorted(components, key=lambda row: (-int(row["events"]), row["component"]))
    component_rows = []
    for rank, row in enumerate(ranked_components, start=1):
        if rank <= 12:
            lesson = "L02_CORE_POSTEN_FLOW"
            tier = "ALL_SCRIBES_FAST_CORE"
        elif rank <= 27:
            lesson = "L03_OPERATIONS_MATERIAL_ADDRESSES"
            tier = "ALL_PROSE_SCRIBES_WORKING_CORE"
        else:
            lesson = "L04_RARE_COMMANDS"
            tier = "RECOGNIZE_WITH_MODEL_SHEET"
        component_rows.append({
            "rank": rank, "component": row["component"], "short_value_de": row["short_value_de"],
            "events": row["events"], "exact_cards": row["exact_cards"], "lesson": lesson,
            "learning_tier": tier, "drill": "read value, point to owner, compose one known card",
        })

    card_domains: dict[str, set[str]] = defaultdict(set)
    card_events: dict[str, int] = defaultdict(int)
    for row in events:
        card_domains[row["card_no"]].add(domain(row["page"]))
        card_events[row["card_no"]] += 1
    card_rows = []
    for row in sorted(cards, key=lambda item: (-int(item["events"]), item["exact_card_id"])):
        scopes = card_domains[row["exact_card_id"]]
        if scopes == {"HERBAL", "BIO"}:
            deck = "COMMON_17_CARD_DECK"
            lesson = "L05_COMMON_CARD_DECK"
        elif scopes == {"HERBAL"}:
            deck = "HERBAL_49_CARD_EXTENSION"
            lesson = "L08_SPECIALIST_CARD_DECK"
        else:
            deck = "BIO_107_CARD_EXTENSION"
            lesson = "L08_SPECIALIST_CARD_DECK"
        frequency_tier = "A_RECURRENT" if int(row["events"]) >= 5 else ("B_LOW_RECURRENT" if int(row["events"]) >= 2 else "C_SINGLE_EXEMPLAR")
        card_rows.append({
            "exact_card_id": row["exact_card_id"], "registered_surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"], "rebuilt_reading_de": row["rebuilt_reading_de"],
            "events": card_events[row["exact_card_id"]], "deck_assignment": deck,
            "frequency_tier": frequency_tier, "lesson": lesson,
            "copy_drill": "copy surface from model, cover model, reconstruct component recipe",
        })

    rule_rows = []
    for order, row in enumerate(rules, start=1):
        rule_rows.append({
            "rule_order": order, "meta_rule_id": row["meta_rule_id"], "name_de": row["name_de"],
            "apprentice_instruction_de": row["apprentice_instruction_de"],
            "registered_variants": row["registered_variants"], "forward_uses": row["forward_uses"],
            "lesson": "L06_NINE_HAND_RULES", "drill": "master demonstrates one variant; apprentice copies all registered variants",
        })

    token_rows = []
    for row in motifs:
        token_rows.append({
            "token": row["motif_id"], "token_kind": "SHARED_MOTIF", "content": row["card_recipe"],
            "scope": scope_from_statements(row["statement_ids"]), "uses": row["formula_occurrences"],
            "lesson": "L09_MOTIF_TAIL_LAYOUTS", "drill": "insert motif into its family layout from memory",
        })
    for row in tails:
        token_rows.append({
            "token": row["tail_id"], "token_kind": "LOCAL_TAIL_STRIP", "content": row["card_sequence"],
            "scope": scope_from_statements(row["statement_ids"]), "uses": row["formula_uses"],
            "lesson": "L09_MOTIF_TAIL_LAYOUTS", "drill": "copy strip three times, then restore it between neighboring M tokens",
        })

    lessons = [
        ("L01_OWNER_AND_SPACE", "picture owner, field boundary, line continuation", 4, 4, 4, 4, "copy a page skeleton before any cards"),
        ("L02_CORE_POSTEN_FLOW", "top12 values: item, close, set, grade, transfer, continue, measure, target", 8, 8, 8, 0, "oral prompt to component and back"),
        ("L03_OPERATIONS_MATERIAL_ADDRESSES", "next15 recurrent operations/material/address values", 8, 8, 8, 0, "compose twenty common recipes"),
        ("L04_RARE_COMMANDS", "twelve rare/contextual values with model sheet", 4, 4, 4, 0, "recognition, not unaided invention"),
        ("L05_COMMON_CARD_DECK", "17 cross-register exact cards covering136 events", 8, 8, 8, 0, "surface-card flash copying"),
        ("L06_NINE_HAND_RULES", "nine parameterized packing handgrips", 8, 8, 8, 0, "apply each handgrip to its variants"),
        ("L07_COMMON_COPY_DRILLS", "short Bio cells and long Herbal clauses", 8, 8, 8, 0, "forward and backward copy without correction marks"),
        ("L08_HERBAL_SPECIALIZATION", "49 Herbal-only cards", 12, 12, 0, 0, "owner/material article drills"),
        ("L08_BIO_SPECIALIZATION", "107 Bio-only cards", 20, 0, 20, 0, "station-cell and close drills"),
        ("L09_HERBAL_MOTIF_TAIL_LAYOUTS", "6 relevant motifs,8 tail strips,4 layouts", 6, 6, 0, 0, "rebuild four bound Herbal formulas"),
        ("L09_BIO_MOTIF_TAIL_LAYOUTS", "7 relevant motifs,11 tail strips,3 layouts", 8, 0, 8, 0, "rebuild three bound Bio formulas"),
        ("L10_CORRECTION_AND_CATCH", "spot wrong card boundary, missing Y, misplaced grade and repeated card", 4, 4, 4, 4, "correct ten planted errors"),
        ("L11_ASTRO_LOCAL_TABLE_COPY", "separate page-local wheel and star-label copying; no prose dictionary import", 12, 0, 0, 12, "copy one fixed diagram namespace at a time"),
        ("L12_MASTER_EXAM", "one complete owner-addressed unit from oral instruction/model", 4, 4, 4, 4, "master checks order, card identity and layout"),
    ]
    lesson_rows = [
        {
            "lesson": lesson, "content": content, "master_hours": master, "herbal_hours": herbal,
            "bio_hours": bio, "astro_hours": astro, "exercise": exercise,
        }
        for lesson, content, master, herbal, bio, astro, exercise in lessons
    ]

    role_rows = [
        {"role": "MASTER_CORRECTOR", "background": "knows both prose registers and the separate diagram-copy module", "shared_components": 39, "exact_cards": 173, "motif_tail_tokens": 27, "layouts": 7, "curriculum_hours": sum(row[2] for row in lessons), "may_specialize": "NO"},
        {"role": "HERBAL_SCRIBE", "background": "copies plant-owner clauses and their material/preparation echoes", "shared_components": 39, "exact_cards": 66, "motif_tail_tokens": 14, "layouts": 4, "curriculum_hours": sum(row[3] for row in lessons), "may_specialize": "YES"},
        {"role": "BIO_STATION_SCRIBE", "background": "copies compact station cells, addresses, closes and continuation bridges", "shared_components": 39, "exact_cards": 124, "motif_tail_tokens": 18, "layouts": 3, "curriculum_hours": sum(row[4] for row in lessons), "may_specialize": "YES"},
        {"role": "ASTRO_TABLE_SCRIBE", "background": "copies page-local diagram namespaces from model sheets", "shared_components": 0, "exact_cards": 0, "motif_tail_tokens": 0, "layouts": 0, "curriculum_hours": sum(row[5] for row in lessons), "may_specialize": "YES"},
    ]

    write("SEVEN_HUNDRED_SIXTY_THIRD_39_COMPONENT_LESSONS.tsv", component_rows)
    write("SEVEN_HUNDRED_SIXTY_THIRD_173_CARD_SPECIALIZATION.tsv", card_rows)
    write("SEVEN_HUNDRED_SIXTY_THIRD_9_RULE_CURRICULUM.tsv", rule_rows)
    write("SEVEN_HUNDRED_SIXTY_THIRD_27_MOTIF_TAIL_ASSIGNMENT.tsv", token_rows)
    write("SEVEN_HUNDRED_SIXTY_THIRD_14_LESSON_CURRICULUM.tsv", lesson_rows)
    write("SEVEN_HUNDRED_SIXTY_THIRD_4_SCRIBE_ROLES.tsv", role_rows)

    report = """# Pass 763 — Werkstattlehre fuer mehrere Schreiber

Das System ist in einer kleinen Werkstatt lernbar, wenn nicht jeder alles gleich tief beherrschen muss.

## Gemeinsamer Kern

Alle Prosa-Schreiber lernen39 kurze Werte und neun Packhandgriffe. Sie lernen zuerst17 registeruebergreifende exakte Karten; diese17 Karten tragen136/381 sichtbare Ereignisse. Danach teilt sich die Ausbildung.

## Spezialisierung

- Der Herbal-Schreiber braucht49 weitere Herbal-Karten, also66 Karten insgesamt, dazu4 grosse Layouts,6 relevante Motive und8 lokale Reststreifen. Lehrzeit:74 Stunden.
- Der Bio-Schreiber braucht107 weitere Bio-Karten, also124 Karten insgesamt, dazu3 Layouts,7 relevante Motive und11 Reststreifen. Lehrzeit:84 Stunden.
- Der Astro-Schreiber lernt nicht das Prosa-Woerterbuch, sondern Seiten-/Diagrammnamensraeume durch Kopieren vom Modellblatt. Lehrzeit im kleinen Modul:24 Stunden.
- Der Meister/Korrektor lernt beide Prosa-Spezialisierungen plus das Astro-Modul:114 Stunden.

## Warum mehrere Haende trotzdem aehnlich schreiben

Die39 Bedeutungswerte, neun Handgriffe und17 gemeinsamen Karten werden von allen Prosa-Schreibern geteilt. Unterschiede duerfen in Spezialkarten, lokalen Reststreifen und Rendererwahl liegen. Ein Bio-Schreiber muss deshalb nicht alle seltenen Herbal-Folgen auswendig kennen, und umgekehrt.

Als naechstes wird fuer jede Rolle eine kleine praktische Abschlussprobe erzeugt: eine Herbal-Klausel, eine Bio-Zelle und ein Astro-Layout, jeweils mit typischen Lehrlingsfehlern und Korrekturzeichen.
"""
    (HERE / "SEVEN_HUNDRED_SIXTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")
    deck_counts = defaultdict(int)
    deck_events = defaultdict(int)
    for row in card_rows:
        deck_counts[row["deck_assignment"]] += 1
        deck_events[row["deck_assignment"]] += int(row["events"])
    summary = {
        "status": "PASS", "components": len(component_rows), "cards": len(card_rows), "meta_rules": len(rule_rows),
        "motif_tail_tokens": len(token_rows), "lessons": len(lesson_rows), "scribe_roles": len(role_rows),
        "common_cards": deck_counts["COMMON_17_CARD_DECK"], "common_card_events": deck_events["COMMON_17_CARD_DECK"],
        "herbal_only_cards": deck_counts["HERBAL_49_CARD_EXTENSION"], "bio_only_cards": deck_counts["BIO_107_CARD_EXTENSION"],
        "master_hours": next(row["curriculum_hours"] for row in role_rows if row["role"] == "MASTER_CORRECTOR"),
        "herbal_hours": next(row["curriculum_hours"] for row in role_rows if row["role"] == "HERBAL_SCRIBE"),
        "bio_hours": next(row["curriculum_hours"] for row in role_rows if row["role"] == "BIO_STATION_SCRIBE"),
        "astro_hours": next(row["curriculum_hours"] for row in role_rows if row["role"] == "ASTRO_TABLE_SCRIBE"),
        "decision": "MULTI_SCRIBE_CURRICULUM__COMMON_39_VALUES_9_RULES_17_CARDS__REGISTER_SPECIALIZATION",
    }
    (HERE / "SEVEN_HUNDRED_SIXTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
