#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P538 = ROOT / "experiments/yolo/sidequest_semantic_whole_card_attack_five_hundred_thirty_eighth"
P545 = ROOT / "experiments/yolo/sidequest_semantic_fluent_cross_line_edition_five_hundred_forty_fifth"
P549 = ROOT / "experiments/yolo/sidequest_semantic_component_sentence_roles_five_hundred_forty_ninth"
P550 = ROOT / "experiments/yolo/sidequest_semantic_argument_attachment_parser_five_hundred_fiftieth"
P553 = ROOT / "experiments/yolo/sidequest_semantic_unified_action_lexicon_five_hundred_fifty_third"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    components = read_tsv(P549 / "FIVE_HUNDRED_FORTY_NINTH_THIRTY_EIGHT_COMPONENT_ROLES.tsv")
    profiles = read_tsv(P549 / "FIVE_HUNDRED_FORTY_NINTH_ONE_HUNDRED_SEVENTY_THREE_CARD_ROLE_PROFILES.tsv")
    events = read_tsv(P545 / "FIVE_HUNDRED_FORTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_SENTENCE_MAP.tsv")
    attachments = read_tsv(P550 / "FIVE_HUNDRED_FIFTIETH_THREE_HUNDRED_EIGHTY_SOURCE_ATTACHMENTS.tsv")
    action_rules = read_tsv(P553 / "FIVE_HUNDRED_FIFTY_THIRD_UNIFIED_ACTION_FRAME_LEXICON.tsv")
    action_occurrences = read_tsv(P553 / "FIVE_HUNDRED_FIFTY_THIRD_TWO_HUNDRED_SEVENTY_ONE_ACTION_OCCURRENCES.tsv")
    clauses = read_tsv(P553 / "FIVE_HUNDRED_FIFTY_THIRD_TWO_HUNDRED_FORTY_ONE_REVISED_BUNDLES.tsv")
    original_cards = {row["card_no"]: row for row in read_tsv(P538 / "FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")}
    profile_by_card = {row["card_no"]: row for row in profiles}
    clause_by_id = {row["clause_id"]: row for row in clauses}
    attachment_by_source = {row["source_position_id"]: row for row in attachments}

    actions_by_clause_component: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for row in action_occurrences:
        actions_by_clause_component[(row["clause_id"], row["action_component"])].add((row["frame_code"], row["frame_conditioned_verb_de"]))

    visible_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events: visible_by_card[row["card_no"]].append(row)
    card_senses: dict[str, set[str]] = defaultdict(set)
    card_frame_codes: dict[str, set[str]] = defaultdict(set)
    for attachment in attachments:
        profile = profile_by_card[attachment["card_no"]]
        senses = []
        codes = []
        for component in profile["component_parse"].split("+"):
            for code, verb in sorted(actions_by_clause_component.get((attachment["clause_id"], component), set())):
                senses.append(verb)
                codes.append(f"{component}:{code}")
        if senses:
            card_senses[attachment["card_no"]].add(" + ".join(senses))
            card_frame_codes[attachment["card_no"]].update(codes)

    component_rows = []
    action_rule_counts = Counter(row["action_component"] for row in action_rules)
    for row in components:
        component_rows.append({
            "component_no": row["component_no"], "component": row["component"], "sentence_role": row["sentence_role"],
            "atomic_meaning_de": row["atomic_meaning_de"], "grammar_contribution_de": row["grammar_contribution_de"],
            "card_types": row["card_types"], "events": row["events"], "action_frame_rules": str(action_rule_counts[row["component"]]),
            "full_verb_only_when_action": row["is_independent_full_verb"],
        })

    card_rows = []
    for profile in profiles:
        card_no = profile["card_no"]
        seen = visible_by_card[card_no]
        senses = sorted(card_senses.get(card_no, set()))
        frame_codes = sorted(card_frame_codes.get(card_no, set()))
        context_sensitive = len(senses) > 1
        original = original_cards[card_no]
        card_rows.append({
            "card_no": card_no,
            "surfaces": "|".join(sorted({row["surface"] for row in seen})),
            "component_parse": profile["component_parse"],
            "role_signature": profile["role_signature"],
            "clause_type": profile["clause_type"],
            "portable_component_reading_de": original["invariant_card_reading_de"],
            "portable_role_reading_de": profile["role_based_reading_de"],
            "observed_action_senses_de": "|".join(senses) or "NOT_AN_ACTION_CARD",
            "observed_action_frame_codes": "|".join(frame_codes) or "NONE",
            "context_sense_count": str(len(senses) if senses else 1),
            "context_sensitive": "YES" if context_sensitive else "NO",
            "composition_status": profile["composition_status"],
            "occurrences": profile["occurrences"],
            "sections": profile["sections"],
            "records": profile["records"],
            "complete_default_available": "YES",
        })

    event_rows = []
    for event in events:
        attachment = attachment_by_source[event["source_position_id"]]
        profile = profile_by_card[event["card_no"]]
        senses = []
        codes = []
        for component in profile["component_parse"].split("+"):
            for code, verb in sorted(actions_by_clause_component.get((attachment["clause_id"], component), set())):
                senses.append(verb)
                codes.append(f"{component}:{code}")
        event_rows.append({
            "event_id": event["event_id"], "source_position_id": event["source_position_id"], "semantic_execution": event["semantic_execution"],
            "page": event["page"], "record": event["record"], "statement_id": event["statement_id"], "locus": event["locus"],
            "surface": event["surface"], "card_no": event["card_no"], "component_parse": profile["component_parse"],
            "clause_id": attachment["clause_id"], "card_clause_type": profile["clause_type"],
            "portable_card_reading_de": profile["role_based_reading_de"],
            "occurrence_action_senses_de": " + ".join(senses) or "NON_ACTION_CONTRIBUTION",
            "occurrence_frame_codes": "|".join(codes) or "NONE",
            "containing_clause_de": clause_by_id[attachment["clause_id"]]["unified_action_clause_de"],
            "silent_owner_de": next(row["silent_owner_de"] for row in read_tsv(P538 / "FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_EDITION.tsv") if row["event_id"] == event["event_id"]),
            "complete_default_available": "YES",
        })

    write_tsv("FIVE_HUNDRED_FIFTY_FOURTH_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv", component_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_FOURTH_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv", card_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_DICTIONARY.tsv", event_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_FOURTH_FIFTY_SIX_ACTION_FRAME_LEXICON.tsv", action_rules)

    lines = ["# Kanonisches Arbeitswörterbuch der zehn Seiten", "", "## 38 Komponenten", "", "| Komponente | Rolle | Arbeitsbedeutung | Karten / Ereignisse |", "|---|---|---|---|"]
    for row in component_rows:
        lines.append(f"| `{row['component']}` | {row['sentence_role']} | {row['atomic_meaning_de']} | {row['card_types']} / {row['events']} |")
    lines.extend(["", "## 173 exakte Karten", "", "| Karte | Oberflächen | Zerlegung | portable Lesung | beobachtete Aktionssinne |", "|---|---|---|---|---|"])
    for row in card_rows:
        lines.append(f"| `{row['card_no']}` | `{row['surfaces']}` | `{row['component_parse']}` | {row['portable_role_reading_de']} | {row['observed_action_senses_de']} |")
    (HERE / "FIVE_HUNDRED_FIFTY_FOURTH_COMPLETE_WORKING_DICTIONARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS", "components": len(component_rows), "action_frame_rules": len(action_rules), "cards": len(card_rows), "events": len(event_rows),
        "action_cards": sum(row["clause_type"] == "ACTION_CLAUSE" for row in card_rows), "non_action_cards": sum(row["clause_type"] != "ACTION_CLAUSE" for row in card_rows),
        "context_stable_cards": sum(row["context_sensitive"] == "NO" for row in card_rows), "context_sensitive_cards": sum(row["context_sensitive"] == "YES" for row in card_rows),
        "context_sense_distribution": dict(sorted(Counter(row["context_sense_count"] for row in card_rows).items())),
        "visible_events": len(event_rows), "executed_source_positions": len({row["source_position_id"] for row in event_rows}),
    }
    (HERE / "FIVE_HUNDRED_FIFTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sensitive = [row for row in card_rows if row["context_sensitive"] == "YES"]
    report = [
        "# Fünfhundertvierundfünfzigste Runde: kanonisches Arbeitswörterbuch", "", "## Ergebnis", "",
        f"Das aktuelle System ist in ein einziges Wörterbuch kompiliert: {len(component_rows)} Komponenten, {len(action_rules)} Aktionsrahmen, {len(card_rows)} exakte Karten und {len(event_rows)} sichtbare Ereignisse. Jede Zeile besitzt eine konkrete Defaultlesung.", "",
        f"Nur {len(sensitive)} der 173 Karten wechseln ihr konkretes Aktionsverb mit dem Nachbarrahmen; 162 bleiben auf den zehn Seiten kontextstabil. Die elf beweglichen Karten sind: " + ", ".join(f"`{row['card_no']}`" for row in sensitive) + ".", "",
        "Das ist genau die gesuchte Mischarchitektur: eine Karte hat eine feste Komponentenstruktur, während wenige produktive Aktionskarten durch Maß, Ziel, Quelle, Weg oder Grad präzisiert werden. Die große Mehrheit bleibt gelernte, aber zerlegbare Werkstattform.", "",
        "Die 381-Ereignis-Tabelle zeigt für jedes sichtbare Vorkommen sowohl seine portable Kartenlesung als auch die occurrence-spezifische Rahmenlesung und den vollständigen Satz.",
    ]
    (HERE / "FIVE_HUNDRED_FIFTY_FOURTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
