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
P550 = ROOT / "experiments/yolo/sidequest_semantic_argument_attachment_parser_five_hundred_fiftieth"

TARGET_ACTIONS = ("OK", "CHD", "L", "K")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sense(action: str, components: list[str]) -> tuple[str, str, str]:
    values = set(components)
    if action == "OK":
        if values & {"AIR", "CKH"}: return "FLOW_START", "einleiten", "OK plus Lauf/Durchlass"
        if values & {"AL", "OS"}: return "TARGET_APPLY", "anlegen", "OK plus Zielstelle/Arbeitsfach"
        if values & {"OR", "O", "HO"}: return "PREPARATION_START", "ansetzen", "OK plus Ansatz/Arbeitsgang/Gabe"
        if values & {"AIIN", "AIN"}: return "MEASURED_CHARGE", "einsetzen", "OK plus Maß/Portion"
        if values & {"E", "EE", "EEE"} and "DY" in values: return "TIMED_APPLICATION", "einwirken lassen", "OK plus Grad und Schluss"
        if values & {"E", "EE", "EEE"}: return "HOLD_ACTIVE", "wirken lassen", "OK plus Grad ohne Schluss"
        return "ACTIVATE", "einsetzen", "OK ohne engeren Adressrahmen"
    if action == "CHD":
        if values & {"AIR", "CKH"}: return "PATH_TRANSFER", "durchleiten", "CHD plus Lauf/Durchlass"
        if values & {"AL", "OS"}: return "TARGET_TRANSFER", "umfüllen", "CHD plus Ziel"
        if "AR" in values: return "SOURCE_TRANSFER", "abführen", "CHD plus Quelle"
        if values & {"AIIN", "AIN"}: return "MEASURED_TRANSFER", "abmessen und umsetzen", "CHD plus Maß/Portion"
        if "DY" in values: return "COMMIT_TRANSFER", "überführen", "CHD plus Schluss"
        return "TRANSFER", "umsetzen", "CHD ohne engeren Rahmen"
    if action == "L":
        if values & {"AIR", "CKH"}: return "PATH_GUIDE", "durchleiten", "L plus Lauf/Durchlass"
        if "AR" in values: return "SOURCE_DRAIN", "ableiten", "L plus Quelle"
        if values & {"AL", "OS"}: return "TARGET_GUIDE", "hinleiten", "L plus Ziel"
        if "DY" in values: return "CLOSED_DRAIN", "abführen", "L plus Schluss"
        return "GUIDE", "führen", "L ohne engeren Rahmen"
    if values & {"AIR", "CKH"}: return "PATH_FEED", "einspeisen", "K plus Lauf/Durchlass"
    if values & {"AL", "OS"}: return "TARGET_FEED", "zuführen", "K plus Ziel"
    if values & {"OR", "O", "HO"}: return "MATERIAL_ADD", "zugeben", "K plus Ansatz/Arbeitsgang/Gabe"
    if values & {"AIIN", "AIN"}: return "MEASURED_ADD", "dosiert zugeben", "K plus Maß/Portion"
    if "DY" in values: return "COMMIT_ADD", "zugeben", "K plus Schluss"
    return "ADD", "zugeben", "K ohne engeren Rahmen"


BASE_ACTION = {"CFH": "auswringen", "CH": "abziehen", "CHK": "wärmen", "LD": "befestigen", "LSH": "waschen", "P": "hineingeben", "R": "abkühlen", "S": "teilen", "SH": "halten", "SHED": "absetzen", "SOLK": "auffangen", "T": "eintragen", "TALAM": "verwahren"}


def realize(components: list[str]) -> tuple[str, list[tuple[str, str, str, str]]]:
    action_tokens = [c for c in components if c in BASE_ACTION or c in TARGET_ACTIONS]
    refinements = []
    action_words = []
    for action in action_tokens:
        if action in TARGET_ACTIONS:
            code, word, trigger = sense(action, components)
            refinements.append((action, code, word, trigger))
            action_words.append(word)
        else:
            action_words.append(BASE_ACTION[action])
    prefix = ["danach"] if "OT" in components else []
    if "Y" in components: obj = "den laufenden Posten"
    elif "OR" in components: obj = "den Ansatz"
    elif "HO" in components: obj = "die Gabe"
    elif "AIN" in components: obj = "eine Portion"
    else: obj = "den laufenden Posten"
    adjuncts = []
    if "OL" in components or "LS" in components: adjuncts.append("weiter")
    if "AR" in components: adjuncts.append("von dort")
    if "AIIN" in components: adjuncts.append("nach vorgeschriebenem Maß")
    if "AIN" in components and obj != "eine Portion": adjuncts.append("als Portion")
    if "AL" in components: adjuncts.append("an der bezeichneten Stelle")
    if "AIR" in components: adjuncts.append("im Lauf")
    if "CKH" in components: adjuncts.append("durch den Durchlass")
    if "O" in components: adjuncts.append("im Arbeitsgang")
    if "E" in components and "EE" in components: adjuncts.append("zunächst kurz, dann länger")
    elif "E" in components: adjuncts.append("kurz")
    elif "EE" in components: adjuncts.append("länger")
    if "EEE" in components: adjuncts.append("vollständig")
    if "CTH" in components: adjuncts.append("bis bereit")
    if "IIN" in components: adjuncts.append("bis zur " + ("zweiten " if "DA" in components else "") + "Sollstufe")
    if len(action_words) >= 2 and len(set(action_words)) == 1:
        action_text = "erneut " + action_words[0]
    else:
        action_text = " und ".join(action_words)
    text = " ".join(prefix + [obj] + adjuncts + [action_text])
    if "DY" in components: text += " und den Schritt schließen"
    return text, refinements


def main() -> None:
    profiles = {row["card_no"]: row for row in read_tsv(P549 / "FIVE_HUNDRED_FORTY_NINTH_ONE_HUNDRED_SEVENTY_THREE_CARD_ROLE_PROFILES.tsv")}
    old_clauses = read_tsv(P550 / "FIVE_HUNDRED_FIFTIETH_TWO_HUNDRED_FORTY_ONE_ACTION_BUNDLES.tsv")
    old_instructions = read_tsv(P550 / "FIVE_HUNDRED_FIFTIETH_NINETY_SEVEN_REPARSED_INSTRUCTIONS.tsv")
    article_base = {row["record"]: row for row in read_tsv(P546 / "FIVE_HUNDRED_FORTY_SIXTH_ELEVEN_CONTINUOUS_RECORD_ARTICLES.tsv")}
    action_rows = []
    revised_clauses = []
    for old in old_clauses:
        components = [component for card in old["member_card_nos"].split("|") for component in profiles[card]["component_parse"].split("+")]
        if old["attachment_status"] == "ELLIPTIC_INHERITED_ACTION":
            text = old["reparsed_clause_de"]
            refinements = []
        else:
            text, refinements = realize(components)
        for action, code, word, trigger in refinements:
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
                "member_card_nos": old["member_card_nos"],
                "source_position_ids": old["source_position_ids"],
                "component_values_changed": "NO",
                "action_gloss_refined": "YES",
            })
        revised_clauses.append({
            "clause_id": old["clause_id"],
            "instruction_id": old["instruction_id"],
            "record": old["record"],
            "page": old["page"],
            "member_card_nos": old["member_card_nos"],
            "source_position_ids": old["source_position_ids"],
            "visible_event_ids": old["visible_event_ids"],
            "old_reparsed_clause_de": old["reparsed_clause_de"],
            "frame_conditioned_clause_de": text,
            "refined_action_components": "|".join(f"{a}:{c}" for a, c, _, _ in refinements) or "NONE",
            "component_values_changed": "NO",
            "attachment_status": old["attachment_status"],
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
            "frame_conditioned_instruction_de": "; dann ".join(row["frame_conditioned_clause_de"] for row in clauses) + ".",
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
            body = row["frame_conditioned_instruction_de"].rstrip(".")
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
            "frame_conditioned_article_de": base["introduction_de"] + " " + " ".join(sentences),
        })

    frame_counts = Counter((row["action_component"], row["frame_code"], row["frame_conditioned_verb_de"], row["trigger"]) for row in action_rows)
    lexicon_rows = []
    for index, ((action, code, word, trigger), count) in enumerate(sorted(frame_counts.items()), 1):
        records_for = sorted({row["record"] for row in action_rows if row["action_component"] == action and row["frame_code"] == code})
        lexicon_rows.append({
            "frame_rule_no": f"AF{index:02d}",
            "action_component": action,
            "frame_code": code,
            "frame_conditioned_verb_de": word,
            "trigger": trigger,
            "occurrences": str(count),
            "records": "|".join(records_for),
        })

    write_tsv("FIVE_HUNDRED_FIFTY_FIRST_ACTION_FRAME_LEXICON.tsv", lexicon_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_FIRST_ONE_HUNDRED_SEVENTY_FIVE_ACTION_OCCURRENCES.tsv", action_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_FIRST_TWO_HUNDRED_FORTY_ONE_REVISED_BUNDLES.tsv", revised_clauses)
    write_tsv("FIVE_HUNDRED_FIFTY_FIRST_NINETY_SEVEN_REVISED_INSTRUCTIONS.tsv", instruction_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_FIRST_ELEVEN_REVISED_ARTICLES.tsv", article_rows)
    edition = ["# Elf rahmenpräzisierte Werkstattartikel", ""]
    for row in article_rows:
        edition.extend([f"## {row['record']} — {row['page']}", "", row["frame_conditioned_article_de"], ""])
    (HERE / "FIVE_HUNDRED_FIFTY_FIRST_COMPLETE_FRAME_CONDITIONED_EDITION.md").write_text("\n".join(edition), encoding="utf-8")

    old_broad = sum(len(re.findall(r"\b(?:ansetzen|umsetzen|führen|zuführen)\w*\b", row["old_reparsed_clause_de"], re.I)) for row in revised_clauses)
    new_broad = sum(len(re.findall(r"\b(?:ansetzen|umsetzen|führen|zuführen)\w*\b", row["frame_conditioned_clause_de"], re.I)) for row in revised_clauses)
    summary = {
        "status": "PASS",
        "action_occurrences": len(action_rows),
        "frame_rules": len(lexicon_rows),
        "revised_bundles": len(revised_clauses),
        "instructions": len(instruction_rows),
        "articles": len(article_rows),
        "broad_verb_tokens_before": old_broad,
        "broad_verb_tokens_after": new_broad,
        "reduction": old_broad - new_broad,
        "action_counts": dict(sorted(Counter(row["action_component"] for row in action_rows).items())),
        "sense_counts": dict(sorted(Counter(row["frame_code"] for row in action_rows).items())),
    }
    (HERE / "FIVE_HUNDRED_FIFTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhunderteinundfünfzigste Runde: rahmenabhängige Handlungen",
        "",
        "## Ergebnis",
        "",
        f"Die vier breiten Aktionskerne OK, CHD, L und K erscheinen {len(action_rows)} mal in den 241 Aktionsbündeln. Ihre Begleitkarten teilen sie in {len(lexicon_rows)} konkrete Werkstattlesungen. Die Bedeutungsachse bleibt gleich; die deutsche Handlung wird enger.",
        "",
        "- OK: einsetzen, anlegen, ansetzen, einleiten oder einwirken lassen.",
        "- CHD: umsetzen, umfüllen, durchleiten, abführen oder überführen.",
        "- L: führen, hinleiten, durchleiten, ableiten oder abführen.",
        "- K: zugeben, dosiert zugeben, zuführen oder einspeisen.",
        "",
        f"Die vier alten Sammelverben treten in der laufenden Ausgabe nur noch {new_broad} statt {old_broad} mal auf. {old_broad - new_broad} Stellen erhalten damit ein engeres Fachverb, ohne einen Kartenwert zu wechseln.",
        "",
        "Der stärkste neue Leseschlüssel ist OK+Grad+Schluss = einwirken lassen und schließen; OK+Ziel = anlegen; L+Schluss = abführen; K+Maß = dosiert zugeben. Das passt zugleich zu Behandlung, Bad, Behälter und Leitung, ohne eine einzige Domäne zu erzwingen.",
    ]
    (HERE / "FIVE_HUNDRED_FIFTY_FIRST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
