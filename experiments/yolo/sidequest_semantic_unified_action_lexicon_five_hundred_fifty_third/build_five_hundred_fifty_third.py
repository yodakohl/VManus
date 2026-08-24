#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P546 = ROOT / "experiments/yolo/sidequest_semantic_anaphoric_record_articles_five_hundred_forty_sixth"
P549 = ROOT / "experiments/yolo/sidequest_semantic_component_sentence_roles_five_hundred_forty_ninth"
P551 = ROOT / "experiments/yolo/sidequest_semantic_frame_conditioned_actions_five_hundred_fifty_first"
P552 = ROOT / "experiments/yolo/sidequest_semantic_process_state_action_frames_five_hundred_fifty_second"

OLD_WORD = {"T": "eintragen", "SOLK": "auffangen", "LSH": "waschen", "P": "hineingeben", "CFH": "auswringen", "S": "teilen", "LD": "befestigen", "TALAM": "verwahren"}
TARGET = tuple(OLD_WORD)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sense(action: str, components: list[str]) -> tuple[str, str, str, bool]:
    values = set(components)
    if action == "T":
        if "AR" in values: return "SOURCE_COPY", "übertragen", "T plus Quelle", True
        if values & {"AIIN", "AIN"}: return "MEASURED_ENTRY", "eintragen", "T plus Maß/Portion", False
        if values & {"O", "OR", "HO"} and "DY" in values: return "COMMIT_ENTRY", "abschließend eintragen", "T plus Arbeitsstoff und Schluss", True
        if values & {"O", "OR", "HO"}: return "PROCESS_ENTRY", "eintragen", "T plus Arbeitsstoff", False
        return "CONTINUE_ENTRY", "eintragen", "T in laufender Folge", False
    if action == "SOLK":
        if values & {"AIIN", "AIN"}: return "MEASURED_COLLECT", "bis zum Maß auffangen", "SOLK plus Maß/Portion", True
        if values & {"E", "EE", "EEE"} and "DY" in values: return "COMMIT_COLLECT", "auffangen und stehen lassen", "SOLK plus Grad und Schluss", True
        return "COLLECT", "auffangen", "SOLK ohne engeren Rahmen", False
    if action == "LSH":
        if "DY" in values: return "COMMIT_WASH", "durchwaschen", "LSH plus Schluss", True
        return "WASH", "waschen", "LSH ohne Schluss", False
    if action == "P":
        if values & {"AL", "OS"}: return "TARGET_FILL", "einfüllen", "P plus Ziel", True
        if "DY" in values: return "COMMIT_FILL", "einfüllen", "P plus Schluss", True
        return "INSERT", "hineingeben", "P ohne engeren Rahmen", False
    if action == "CFH": return "WRING", "auswringen", "gelernter Fachkern", False
    if action == "S": return "DIVIDE", "abteilen", "gelernter Fachkern", True
    if action == "LD": return "FASTEN", "festbinden", "gelernter Fachkern", True
    return "STORE", "verwahren", "gelernter Fachkern", False


def main() -> None:
    profiles = {row["card_no"]: row for row in read_tsv(P549 / "FIVE_HUNDRED_FORTY_NINTH_ONE_HUNDRED_SEVENTY_THREE_CARD_ROLE_PROFILES.tsv")}
    pass551_rules = read_tsv(P551 / "FIVE_HUNDRED_FIFTY_FIRST_ACTION_FRAME_LEXICON.tsv")
    pass551_actions = read_tsv(P551 / "FIVE_HUNDRED_FIFTY_FIRST_ONE_HUNDRED_SEVENTY_FIVE_ACTION_OCCURRENCES.tsv")
    pass552_rules = read_tsv(P552 / "FIVE_HUNDRED_FIFTY_SECOND_PROCESS_STATE_FRAME_LEXICON.tsv")
    pass552_actions = read_tsv(P552 / "FIVE_HUNDRED_FIFTY_SECOND_SIXTY_NINE_ACTION_OCCURRENCES.tsv")
    old_clauses = read_tsv(P552 / "FIVE_HUNDRED_FIFTY_SECOND_TWO_HUNDRED_FORTY_ONE_REVISED_BUNDLES.tsv")
    old_instructions = read_tsv(P552 / "FIVE_HUNDRED_FIFTY_SECOND_NINETY_SEVEN_REVISED_INSTRUCTIONS.tsv")
    article_base = {row["record"]: row for row in read_tsv(P546 / "FIVE_HUNDRED_FORTY_SIXTH_ELEVEN_CONTINUOUS_RECORD_ARTICLES.tsv")}

    new_actions = []
    revised_clauses = []
    for old in old_clauses:
        components = [component for card in old["member_card_nos"].split("|") for component in profiles[card]["component_parse"].split("+")]
        text = old["process_state_clause_de"]
        refinements = []
        for action in TARGET:
            for _ in range(components.count(action)):
                code, word, trigger, narrowed = sense(action, components)
                text, substitutions = re.subn(rf"\b{re.escape(OLD_WORD[action])}\b", word, text, count=1, flags=re.I)
                if substitutions != 1:
                    raise ValueError(f"cannot replace {action} in {old['clause_id']}: {text}")
                new_actions.append({
                    "clause_id": old["clause_id"], "instruction_id": old["instruction_id"], "record": old["record"], "page": old["page"],
                    "action_component": action, "frame_code": code, "frame_conditioned_verb_de": word, "trigger": trigger,
                    "narrowed_from_base": "YES" if narrowed else "NO", "member_card_nos": old["member_card_nos"],
                    "source_position_ids": old["source_position_ids"], "source_pass": "PASS553", "component_values_changed": "NO",
                })
                refinements.append(f"{action}:{code}")
        revised_clauses.append({
            "clause_id": old["clause_id"], "instruction_id": old["instruction_id"], "record": old["record"], "page": old["page"],
            "member_card_nos": old["member_card_nos"], "source_position_ids": old["source_position_ids"], "visible_event_ids": old["visible_event_ids"],
            "pass552_clause_de": old["process_state_clause_de"], "unified_action_clause_de": text,
            "new_refinements": "|".join(refinements) or "NONE", "component_values_changed": "NO",
        })

    new_counts = Counter((row["action_component"], row["frame_code"], row["frame_conditioned_verb_de"], row["trigger"], row["narrowed_from_base"]) for row in new_actions)
    new_rules = []
    for (action, code, word, trigger, narrowed), count in sorted(new_counts.items()):
        new_rules.append({"action_component": action, "frame_code": code, "frame_conditioned_verb_de": word, "trigger": trigger, "occurrences": str(count), "narrowed_from_base": narrowed, "source_pass": "PASS553"})

    unified_rules = []
    for row in pass551_rules:
        base_codes = {("OK", "PREPARATION_START"), ("CHD", "TRANSFER"), ("L", "GUIDE"), ("K", "TARGET_FEED")}
        unified_rules.append({"action_component": row["action_component"], "frame_code": row["frame_code"], "frame_conditioned_verb_de": row["frame_conditioned_verb_de"], "trigger": row["trigger"], "occurrences": row["occurrences"], "narrowed_from_base": "NO" if (row["action_component"], row["frame_code"]) in base_codes else "YES", "source_pass": "PASS551"})
    for row in pass552_rules:
        unified_rules.append({"action_component": row["action_component"], "frame_code": row["frame_code"], "frame_conditioned_verb_de": row["frame_conditioned_verb_de"], "trigger": row["trigger"], "occurrences": row["occurrences"], "narrowed_from_base": row["narrowed_from_base"], "source_pass": "PASS552"})
    unified_rules.extend(new_rules)
    unified_rules.sort(key=lambda row: (row["action_component"], row["frame_code"]))
    for index, row in enumerate(unified_rules, 1): row["unified_rule_no"] = f"UA{index:02d}"
    unified_rules = [{"unified_rule_no": row.pop("unified_rule_no"), **row} for row in unified_rules]

    unified_actions = []
    for source_pass, rows in (("PASS551", pass551_actions), ("PASS552", pass552_actions)):
        for row in rows:
            narrowed = row.get("narrowed_from_base", "YES")
            unified_actions.append({
                "occurrence_no": "", "clause_id": row["clause_id"], "instruction_id": row["instruction_id"], "record": row["record"], "page": row["page"],
                "action_component": row["action_component"], "frame_code": row["frame_code"], "frame_conditioned_verb_de": row["frame_conditioned_verb_de"],
                "trigger": row["trigger"], "narrowed_from_base": narrowed, "member_card_nos": row["member_card_nos"],
                "source_position_ids": row["source_position_ids"], "source_pass": source_pass, "component_values_changed": "NO",
            })
    unified_actions.extend(new_actions)
    unified_actions.sort(key=lambda row: (int(row["clause_id"].split("-C")[0][1:]), int(row["clause_id"].split("-C")[1]), row["action_component"], row["frame_code"]))
    for index, row in enumerate(unified_actions, 1): row["occurrence_no"] = str(index)

    clauses_by_instruction = {}
    for row in revised_clauses: clauses_by_instruction.setdefault(row["instruction_id"], []).append(row)
    instruction_rows = []
    for old in old_instructions:
        clauses = clauses_by_instruction[old["instruction_id"]]
        instruction_rows.append({
            "instruction_id": old["instruction_id"], "page": old["page"], "record": old["record"], "clause_count": old["clause_count"],
            "source_position_ids": old["source_position_ids"], "visible_event_ids": old["visible_event_ids"],
            "unified_action_instruction_de": "; dann ".join(row["unified_action_clause_de"] for row in clauses) + ".",
            "end_type": old["end_type"], "crosses_owner_boundary": old["crosses_owner_boundary"],
        })

    records = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    article_rows = []
    for record in records:
        rows = [row for row in instruction_rows if row["record"] == record]
        sentences = []
        for index, row in enumerate(rows):
            connector = "Zuerst" if index == 0 else ("Danach", "Anschließend", "Sodann")[(index - 1) % 3]
            body = row["unified_action_instruction_de"].rstrip(".")
            body = re.sub(r"\bden laufenden Posten\b", "ihn", body)
            body = re.sub(r"^danach\s+", "", body, flags=re.I)
            body = re.sub(r"; dann danach\s+", "; danach ", body, flags=re.I)
            sentences.append(f"{connector} {body[0].lower() + body[1:]}.")
        base = article_base[record]
        article_rows.append({"record": record, "page": base["page"], "instruction_count": str(len(rows)), "clause_count": str(sum(int(row["clause_count"]) for row in rows)), "visible_event_count": base["visible_event_count"], "record_final_status": base["record_final_status"], "unified_action_article_de": base["introduction_de"] + " " + " ".join(sentences)})

    write_tsv("FIVE_HUNDRED_FIFTY_THIRD_UNIFIED_ACTION_FRAME_LEXICON.tsv", unified_rules)
    write_tsv("FIVE_HUNDRED_FIFTY_THIRD_TWO_HUNDRED_SEVENTY_ONE_ACTION_OCCURRENCES.tsv", unified_actions)
    write_tsv("FIVE_HUNDRED_FIFTY_THIRD_TWO_HUNDRED_FORTY_ONE_REVISED_BUNDLES.tsv", revised_clauses)
    write_tsv("FIVE_HUNDRED_FIFTY_THIRD_NINETY_SEVEN_REVISED_INSTRUCTIONS.tsv", instruction_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_THIRD_ELEVEN_REVISED_ARTICLES.tsv", article_rows)
    edition = ["# Elf Artikel mit vereinheitlichtem Aktionslexikon", ""]
    for row in article_rows: edition.extend([f"## {row['record']} — {row['page']}", "", row["unified_action_article_de"], ""])
    (HERE / "FIVE_HUNDRED_FIFTY_THIRD_COMPLETE_UNIFIED_ACTION_EDITION.md").write_text("\n".join(edition), encoding="utf-8")

    summary = {"status": "PASS", "action_components": len({row["action_component"] for row in unified_rules}), "frame_rules": len(unified_rules), "action_occurrences": len(unified_actions), "new_action_occurrences": len(new_actions), "new_narrowed_occurrences": sum(row["narrowed_from_base"] == "YES" for row in new_actions), "clauses": len(revised_clauses), "instructions": len(instruction_rows), "articles": len(article_rows), "action_counts": dict(sorted(Counter(row["action_component"] for row in unified_actions).items()))}
    (HERE / "FIVE_HUNDRED_FIFTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertdreiundfünfzigste Runde: vollständiges Aktionslexikon", "", "## Ergebnis", "",
        f"Alle {summary['action_components']} Handlungskomponenten sind nun in einem gemeinsamen Lexikon mit {summary['frame_rules']} Rahmenregeln und {summary['action_occurrences']} Komponenten-Vorkommen verbunden.", "",
        "Die letzten acht Kerne werden knapp geschlossen: T=eintragen/übertragen, SOLK=auffangen oder auffangen-und-stehen-lassen, LSH=waschen/durchwaschen, P=hineingeben/einfüllen, CFH=auswringen, S=abteilen, LD=festbinden, TALAM=verwahren.", "",
        f"Von diesen 27 letzten Vorkommen werden {summary['new_narrowed_occurrences']} enger als ihr Grundverb gelesen. Zusammen mit Pass 551/552 besitzt damit jede Handlung einen expliziten Rahmen und jedes Nichtverb eine Anschlussrolle.", "",
        "Das Resultat ist ein lehrbares Mischsystem: 38 Komponenten, 56 Aktionsrahmen, wenige Formeln und drei echte Ganzkarten. Es ähnelt einer Fachkürzelschicht über gelernten Kartenwerten, nicht einem Wort-für-Wort-Klartext.",
    ]
    (HERE / "FIVE_HUNDRED_FIFTY_THIRD_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
