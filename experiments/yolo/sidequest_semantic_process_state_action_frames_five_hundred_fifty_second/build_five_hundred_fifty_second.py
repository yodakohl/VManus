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

OLD_WORD = {"CH": "abziehen", "SH": "halten", "SHED": "absetzen", "CHK": "wärmen", "R": "abkühlen"}
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
    if action == "CH":
        if values & {"AIR", "CKH"}: return "PATH_DRAW", "ablaufen lassen", "CH plus Lauf/Durchlass", True
        if "AR" in values: return "SOURCE_TAKE", "entnehmen", "CH plus Quelle", True
        if values & {"OR", "O", "HO"}: return "PREPARATION_DRAW", "abziehen", "CH plus Ansatz/Arbeitsgang/Gabe", False
        return "TAKE_OFF", "abnehmen", "CH ohne Stoffrahmen", True
    if action == "SH":
        if values & {"AIR", "CKH"}: return "PATH_HOLD", "zurückhalten", "SH plus Lauf/Durchlass", True
        if values & {"E", "EE", "EEE"} and "DY" in values: return "TIMED_REST", "ruhen lassen", "SH plus Grad und Schluss", True
        if values & {"E", "EE", "EEE"}: return "TIMED_HOLD", "halten", "SH plus Grad ohne Schluss", False
        if values & {"AL", "OS"}: return "TARGET_HOLD", "an Ort halten", "SH plus Ziel", True
        return "HOLD", "halten", "SH ohne engeren Rahmen", False
    if action == "SHED":
        if values & {"AL", "OS"}: return "TARGET_DEPOSIT", "ablagern", "SHED plus Ziel", True
        if values & {"E", "EE", "EEE"} and "DY" not in values: return "SETTLE", "ruhen lassen", "SHED plus Grad ohne Schluss", True
        if "DY" in values: return "COMMIT_SETTLE", "absetzen lassen", "SHED plus Schluss", True
        return "DEPOSIT", "absetzen", "SHED ohne engeren Rahmen", False
    if action == "CHK":
        if values & {"AL", "OS"}: return "TARGET_WARM", "anwärmen", "CHK plus Ziel", True
        if "DY" in values: return "COMMIT_TEMPER", "temperieren", "CHK plus Schluss", True
        if values & {"E", "EE", "EEE"}: return "HOLD_WARM", "warm halten", "CHK plus Grad", True
        return "WARM", "wärmen", "CHK ohne engeren Rahmen", False
    if values & {"AL", "OS"}: return "TARGET_COOL", "abkühlen lassen", "R plus Ziel", True
    if "DY" in values: return "COMMIT_COOL", "auskühlen lassen", "R plus Schluss", True
    return "COOL", "abkühlen", "R ohne engeren Rahmen", False


def main() -> None:
    profiles = {row["card_no"]: row for row in read_tsv(P549 / "FIVE_HUNDRED_FORTY_NINTH_ONE_HUNDRED_SEVENTY_THREE_CARD_ROLE_PROFILES.tsv")}
    old_clauses = read_tsv(P551 / "FIVE_HUNDRED_FIFTY_FIRST_TWO_HUNDRED_FORTY_ONE_REVISED_BUNDLES.tsv")
    old_instructions = read_tsv(P551 / "FIVE_HUNDRED_FIFTY_FIRST_NINETY_SEVEN_REVISED_INSTRUCTIONS.tsv")
    article_base = {row["record"]: row for row in read_tsv(P546 / "FIVE_HUNDRED_FORTY_SIXTH_ELEVEN_CONTINUOUS_RECORD_ARTICLES.tsv")}
    action_rows = []
    revised_clauses = []
    for old in old_clauses:
        components = [component for card in old["member_card_nos"].split("|") for component in profiles[card]["component_parse"].split("+")]
        text = old["frame_conditioned_clause_de"]
        refinements = []
        for action in TARGET:
            for _ in range(components.count(action)):
                code, word, trigger, narrowed = sense(action, components)
                pattern = re.compile(rf"\b{re.escape(OLD_WORD[action])}\b", re.I)
                text, substitutions = pattern.subn(word, text, count=1)
                if substitutions != 1:
                    raise ValueError(f"cannot replace {action} in {old['clause_id']}: {text}")
                action_rows.append({
                    "occurrence_no": str(len(action_rows) + 1),
                    "clause_id": old["clause_id"],
                    "instruction_id": old["instruction_id"],
                    "record": old["record"],
                    "page": old["page"],
                    "action_component": action,
                    "frame_code": code,
                    "frame_conditioned_verb_de": word,
                    "trigger": trigger,
                    "narrowed_from_base": "YES" if narrowed else "NO",
                    "member_card_nos": old["member_card_nos"],
                    "source_position_ids": old["source_position_ids"],
                    "component_values_changed": "NO",
                })
                refinements.append(f"{action}:{code}")
        revised_clauses.append({
            "clause_id": old["clause_id"],
            "instruction_id": old["instruction_id"],
            "record": old["record"],
            "page": old["page"],
            "member_card_nos": old["member_card_nos"],
            "source_position_ids": old["source_position_ids"],
            "visible_event_ids": old["visible_event_ids"],
            "pass551_clause_de": old["frame_conditioned_clause_de"],
            "process_state_clause_de": text,
            "new_refinements": "|".join(refinements) or "NONE",
            "component_values_changed": "NO",
        })

    clauses_by_instruction = {}
    for row in revised_clauses:
        clauses_by_instruction.setdefault(row["instruction_id"], []).append(row)
    instruction_rows = []
    for old in old_instructions:
        clauses = clauses_by_instruction[old["instruction_id"]]
        instruction_rows.append({
            "instruction_id": old["instruction_id"],
            "page": old["page"],
            "record": old["record"],
            "clause_count": old["clause_count"],
            "source_position_ids": old["source_position_ids"],
            "visible_event_ids": old["visible_event_ids"],
            "process_state_instruction_de": "; dann ".join(row["process_state_clause_de"] for row in clauses) + ".",
            "end_type": old["end_type"],
            "crosses_owner_boundary": old["crosses_owner_boundary"],
        })

    records = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    article_rows = []
    for record in records:
        rows = [row for row in instruction_rows if row["record"] == record]
        sentences = []
        for index, row in enumerate(rows):
            connector = "Zuerst" if index == 0 else ("Danach", "Anschließend", "Sodann")[(index - 1) % 3]
            body = row["process_state_instruction_de"].rstrip(".")
            body = re.sub(r"\bden laufenden Posten\b", "ihn", body)
            body = re.sub(r"^danach\s+", "", body, flags=re.I)
            body = re.sub(r"; dann danach\s+", "; danach ", body, flags=re.I)
            sentences.append(f"{connector} {body[0].lower() + body[1:]}.")
        base = article_base[record]
        article_rows.append({
            "record": record,
            "page": base["page"],
            "instruction_count": str(len(rows)),
            "clause_count": str(sum(int(row["clause_count"]) for row in rows)),
            "visible_event_count": base["visible_event_count"],
            "record_final_status": base["record_final_status"],
            "process_state_article_de": base["introduction_de"] + " " + " ".join(sentences),
        })

    frame_counts = Counter((row["action_component"], row["frame_code"], row["frame_conditioned_verb_de"], row["trigger"], row["narrowed_from_base"]) for row in action_rows)
    lexicon_rows = []
    for index, ((action, code, word, trigger, narrowed), count) in enumerate(sorted(frame_counts.items()), 1):
        lexicon_rows.append({
            "frame_rule_no": f"PS{index:02d}",
            "action_component": action,
            "frame_code": code,
            "frame_conditioned_verb_de": word,
            "trigger": trigger,
            "occurrences": str(count),
            "narrowed_from_base": narrowed,
        })
    write_tsv("FIVE_HUNDRED_FIFTY_SECOND_PROCESS_STATE_FRAME_LEXICON.tsv", lexicon_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_SECOND_SIXTY_NINE_ACTION_OCCURRENCES.tsv", action_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_SECOND_TWO_HUNDRED_FORTY_ONE_REVISED_BUNDLES.tsv", revised_clauses)
    write_tsv("FIVE_HUNDRED_FIFTY_SECOND_NINETY_SEVEN_REVISED_INSTRUCTIONS.tsv", instruction_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_SECOND_ELEVEN_REVISED_ARTICLES.tsv", article_rows)
    edition = ["# Elf prozess- und zustandspräzisierte Werkstattartikel", ""]
    for row in article_rows:
        edition.extend([f"## {row['record']} — {row['page']}", "", row["process_state_article_de"], ""])
    (HERE / "FIVE_HUNDRED_FIFTY_SECOND_COMPLETE_PROCESS_STATE_EDITION.md").write_text("\n".join(edition), encoding="utf-8")

    summary = {
        "status": "PASS",
        "action_occurrences": len(action_rows),
        "frame_rules": len(lexicon_rows),
        "narrowed_occurrences": sum(row["narrowed_from_base"] == "YES" for row in action_rows),
        "unchanged_base_occurrences": sum(row["narrowed_from_base"] == "NO" for row in action_rows),
        "action_counts": dict(sorted(Counter(row["action_component"] for row in action_rows).items())),
        "sense_counts": dict(sorted(Counter(row["frame_code"] for row in action_rows).items())),
        "clauses": len(revised_clauses),
        "instructions": len(instruction_rows),
        "articles": len(article_rows),
    }
    (HERE / "FIVE_HUNDRED_FIFTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertzweiundfünfzigste Runde: Prozess- und Zustandsrahmen",
        "",
        "## Ergebnis",
        "",
        f"CH, SH, SHED, CHK und R treten {len(action_rows)} mal auf. Sechzehn Rahmenregeln präzisieren {summary['narrowed_occurrences']} davon; {summary['unchanged_base_occurrences']} behalten das schlichte Grundverb.",
        "",
        "- CH wird mit Lauf/Durchlass zu `ablaufen lassen`, mit Quelle zu `entnehmen`, beim Ansatz zu `abziehen`, sonst zu `abnehmen`.",
        "- SH wird am Durchlass zu `zurückhalten`, mit Grad+Schluss zu `ruhen lassen`, sonst bleibt es `halten`.",
        "- SHED+Schluss wird `absetzen lassen`; SHED+Ziel wird `ablagern`.",
        "- CHK wird je nach Rahmen `warm halten`, `temperieren` oder `anwärmen`.",
        "- R wird am Ziel `abkühlen lassen`, mit Schluss `auskühlen lassen`.",
        "",
        "Damit entstehen echte Prozessketten: zuführen → einwirken lassen → ruhen/absetzen lassen → abführen oder auffangen. Die gleiche Kurzschrift bleibt für Körperanwendung, Becken und Behälter lesbar.",
    ]
    (HERE / "FIVE_HUNDRED_FIFTY_SECOND_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
