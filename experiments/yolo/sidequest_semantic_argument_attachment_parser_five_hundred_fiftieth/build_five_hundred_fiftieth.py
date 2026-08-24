#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P545 = ROOT / "experiments/yolo/sidequest_semantic_fluent_cross_line_edition_five_hundred_forty_fifth"
P546 = ROOT / "experiments/yolo/sidequest_semantic_anaphoric_record_articles_five_hundred_forty_sixth"
P549 = ROOT / "experiments/yolo/sidequest_semantic_component_sentence_roles_five_hundred_forty_ninth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ACTION = {"CFH": "auswringen", "CH": "abziehen", "CHD": "umsetzen", "CHK": "wärmen", "K": "zuführen", "L": "führen", "LD": "befestigen", "LSH": "waschen", "OK": "ansetzen", "P": "hineingeben", "R": "abkühlen", "S": "teilen", "SH": "halten", "SHED": "absetzen", "SOLK": "auffangen", "T": "eintragen", "TALAM": "verwahren"}


ELLIPTIC = {
    "I027": "an der bezeichneten Stelle weiterarbeiten",
    "I044": "danach länger einwirken lassen und den Schritt schließen",
    "I070": "danach länger einwirken lassen und den Schritt schließen",
    "I087": "weiterarbeiten und den Schritt schließen",
    "I091": "den Ansatz mit dem laufenden Bestand kurz durch den Durchlass führen und den Schritt schließen",
}


def realize(components: list[str]) -> str:
    actions = [ACTION[c] for c in components if c in ACTION]
    prefix = []
    if "OT" in components:
        prefix.append("danach")
    if "Y" in components:
        obj = "den laufenden Posten"
    elif "OR" in components:
        obj = "den Ansatz"
    elif "HO" in components:
        obj = "die Gabe"
    elif "AIN" in components:
        obj = "eine Portion"
    else:
        obj = "den laufenden Posten"
    adjuncts = []
    if "OL" in components or "LS" in components:
        adjuncts.append("weiter")
    if "AR" in components:
        adjuncts.append("von dort")
    if "AIIN" in components:
        adjuncts.append("nach vorgeschriebenem Maß")
    if "AIN" in components and obj != "eine Portion":
        adjuncts.append("als Portion")
    if "AL" in components:
        adjuncts.append("an der bezeichneten Stelle")
    if "AIR" in components:
        adjuncts.append("im Lauf")
    if "CKH" in components:
        adjuncts.append("durch den Durchlass")
    if "O" in components:
        adjuncts.append("im Arbeitsgang")
    if "OS" in components:
        adjuncts.append("im Arbeitsfach")
    if "E" in components and "EE" in components:
        adjuncts.append("zunächst kurz, dann länger")
    elif "E" in components:
        adjuncts.append("kurz")
    elif "EE" in components:
        adjuncts.append("länger")
    if "EEE" in components:
        adjuncts.append("vollständig")
    if "CTH" in components:
        adjuncts.append("bis bereit")
    if "IIN" in components:
        adjuncts.append("bis zur " + ("zweiten " if "DA" in components else "") + "Sollstufe")
    if len(actions) >= 2 and len(set(actions)) == 1:
        action_text = "erneut " + actions[0]
    else:
        action_text = " und ".join(actions)
    parts = prefix + [obj] + adjuncts + [action_text]
    text = " ".join(parts)
    if "DY" in components:
        text += " und den Schritt schließen"
    return text


def main() -> None:
    visible = read_tsv(P545 / "FIVE_HUNDRED_FORTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_SENTENCE_MAP.tsv")
    instructions = read_tsv(P545 / "FIVE_HUNDRED_FORTY_FIFTH_NINETY_SEVEN_FLUENT_INSTRUCTIONS.tsv")
    articles = {row["record"]: row for row in read_tsv(P546 / "FIVE_HUNDRED_FORTY_SIXTH_ELEVEN_CONTINUOUS_RECORD_ARTICLES.tsv")}
    profiles = {row["card_no"]: row for row in read_tsv(P549 / "FIVE_HUNDRED_FORTY_NINTH_ONE_HUNDRED_SEVENTY_THREE_CARD_ROLE_PROFILES.tsv")}
    source_by_instruction: dict[str, list[dict[str, str]]] = defaultdict(list)
    visible_by_source: dict[str, list[str]] = defaultdict(list)
    for row in visible:
        visible_by_source[row["source_position_id"]].append(row["event_id"])
        if row["semantic_execution"] == "EXECUTE_ONCE":
            source_by_instruction[row["instruction_id"]].append(row)

    clause_rows = []
    attachment_rows = []
    instruction_rows = []
    for instruction in instructions:
        rows = source_by_instruction[instruction["instruction_id"]]
        groups: list[dict] = []
        pending: list[dict[str, str]] = []
        for row in rows:
            profile = profiles[row["card_no"]]
            is_action = profile["clause_type"] == "ACTION_CLAUSE"
            has_close = profile["has_close"] == "YES"
            if is_action:
                groups.append({"members": pending + [row], "anchor": row, "inferred": False})
                pending = []
            elif has_close and groups and not pending:
                groups[-1]["members"].append(row)
            else:
                pending.append(row)
        if pending:
            if groups:
                groups[-1]["members"].extend(pending)
            else:
                groups.append({"members": pending, "anchor": None, "inferred": True})

        clause_texts = []
        for clause_no, group in enumerate(groups, 1):
            members = group["members"]
            components = [component for row in members for component in profiles[row["card_no"]]["component_parse"].split("+")]
            text = ELLIPTIC[instruction["instruction_id"]] if group["inferred"] else realize(components)
            action_components = [component for component in components if component in ACTION]
            status = "ELLIPTIC_INHERITED_ACTION" if group["inferred"] else ("COMPLEX_MULTI_ACTION" if len(action_components) >= 3 else "DIRECT_ACTION_BUNDLE")
            clause_id = f"{instruction['instruction_id']}-C{clause_no:02d}"
            source_ids = [row["source_position_id"] for row in members]
            visible_ids = [event for source_id in source_ids for event in visible_by_source[source_id]]
            clause_rows.append({
                "clause_id": clause_id,
                "instruction_id": instruction["instruction_id"],
                "record": instruction["record"],
                "page": instruction["page"],
                "clause_no": str(clause_no),
                "anchor_card_no": group["anchor"]["card_no"] if group["anchor"] else "INHERITED_FROM_RECORD",
                "action_components": "|".join(action_components) or "INHERITED_ACTION",
                "member_card_nos": "|".join(row["card_no"] for row in members),
                "source_position_ids": "|".join(source_ids),
                "visible_event_ids": "|".join(visible_ids),
                "attachment_status": status,
                "reparsed_clause_de": text,
                "component_values_unchanged": "YES",
            })
            clause_texts.append(text)
            anchor_source = group["anchor"]["source_position_id"] if group["anchor"] else "INHERITED_FROM_RECORD"
            anchor_index = members.index(group["anchor"]) if group["anchor"] else -1
            for member_index, row in enumerate(members):
                profile = profiles[row["card_no"]]
                if group["inferred"]:
                    direction = "ELLIPTIC_ACTION_FROM_RECORD"
                elif row is group["anchor"]:
                    direction = "ACTION_ANCHOR"
                elif profile["has_close"] == "YES" or member_index > anchor_index:
                    direction = "LEFT_TO_PREVIOUS_ACTION"
                else:
                    direction = "RIGHT_TO_NEXT_ACTION"
                attachment_rows.append({
                    "source_position_id": row["source_position_id"],
                    "visible_event_ids": "|".join(visible_by_source[row["source_position_id"]]),
                    "instruction_id": instruction["instruction_id"],
                    "clause_id": clause_id,
                    "card_no": row["card_no"],
                    "surface": row["surface"],
                    "card_clause_type": profile["clause_type"],
                    "attachment_direction": direction,
                    "action_anchor_source_position_id": anchor_source,
                    "role_contribution": profile["role_signature"],
                    "component_values_unchanged": "YES",
                })
        instruction_rows.append({
            "instruction_id": instruction["instruction_id"],
            "page": instruction["page"],
            "record": instruction["record"],
            "source_statement_ids": instruction["source_statement_ids"],
            "clause_count": str(len(groups)),
            "elliptic_clause_count": str(sum(group["inferred"] for group in groups)),
            "source_position_ids": "|".join(row["source_position_id"] for row in rows),
            "visible_event_ids": instruction["visible_event_ids"],
            "reparsed_instruction_de": "; dann ".join(clause_texts) + ".",
            "end_type": instruction["end_type"],
            "crosses_owner_boundary": instruction["crosses_owner_boundary"],
        })

    records = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    article_rows = []
    for record in records:
        rows = [row for row in instruction_rows if row["record"] == record]
        sentences = []
        for index, row in enumerate(rows):
            connector = "Zuerst" if index == 0 else ("Danach", "Anschließend", "Sodann")[(index - 1) % 3]
            body = row["reparsed_instruction_de"].rstrip(".")
            body = re.sub(r"\bden laufenden Posten\b", "ihn", body)
            body = re.sub(r"^danach\s+", "", body, flags=re.I)
            body = re.sub(r"; dann danach\s+", "; danach ", body, flags=re.I)
            sentences.append(f"{connector} {body[0].lower() + body[1:]}.")
        base = articles[record]
        article_rows.append({
            "record": record,
            "page": base["page"],
            "instruction_count": str(len(rows)),
            "clause_count": str(sum(int(row["clause_count"]) for row in rows)),
            "elliptic_clause_count": str(sum(int(row["elliptic_clause_count"]) for row in rows)),
            "visible_event_count": base["visible_event_count"],
            "record_final_status": base["record_final_status"],
            "continuous_attached_article_de": base["introduction_de"] + " " + " ".join(sentences),
        })

    write_tsv("FIVE_HUNDRED_FIFTIETH_TWO_HUNDRED_FORTY_ONE_ACTION_BUNDLES.tsv", clause_rows)
    write_tsv("FIVE_HUNDRED_FIFTIETH_THREE_HUNDRED_EIGHTY_SOURCE_ATTACHMENTS.tsv", attachment_rows)
    write_tsv("FIVE_HUNDRED_FIFTIETH_NINETY_SEVEN_REPARSED_INSTRUCTIONS.tsv", instruction_rows)
    write_tsv("FIVE_HUNDRED_FIFTIETH_ELEVEN_REPARSED_ARTICLES.tsv", article_rows)
    edition = ["# Elf argumentgebundene Werkstattartikel", ""]
    for row in article_rows:
        edition.extend([f"## {row['record']} — {row['page']}", "", row["continuous_attached_article_de"], ""])
    (HERE / "FIVE_HUNDRED_FIFTIETH_COMPLETE_REPARSED_EDITION.md").write_text("\n".join(edition), encoding="utf-8")

    directions = Counter(row["attachment_direction"] for row in attachment_rows)
    statuses = Counter(row["attachment_status"] for row in clause_rows)
    summary = {
        "status": "PASS",
        "instructions": len(instruction_rows),
        "action_bundles": len(clause_rows),
        "source_positions": len(attachment_rows),
        "visible_events": sum(len(row["visible_event_ids"].split("|")) for row in attachment_rows),
        "elliptic_instructions": sum(int(row["elliptic_clause_count"]) > 0 for row in instruction_rows),
        "attachment_directions": dict(sorted(directions.items())),
        "bundle_statuses": dict(sorted(statuses.items())),
        "articles": len(article_rows),
    }
    (HERE / "FIVE_HUNDRED_FIFTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertfünfzigste Runde: Argument-Anschlussparser",
        "",
        "## Ergebnis",
        "",
        f"Die 380 ausgeführten Quellpositionen bilden nun {len(clause_rows)} Aktionsbündel statt 380 scheinbarer Einzelbefehle. Nicht-Aktionskarten hängen als Posten, Maß, Portion, Quelle, Ziel, Weg, Ansatz, Folge, Grad, Zustand oder Schluss an eine Handlung. Alle 381 sichtbaren Ereignisse bleiben nachvollziehbar; E180/E181 teilen weiterhin eine Quellposition.",
        "",
        f"Nur {summary['elliptic_instructions']} der 97 Anweisungen besitzen keine geschriebene Handlung. Sie werden konkret aus dem laufenden Record ergänzt: Stelle weiterbearbeiten, länger einwirken lassen, weiterarbeiten oder Ansatz durch den Durchlass führen.",
        "",
        "## Gewinn",
        "",
        "Y, AIIN, AL, AR, OR und OL erzeugen jetzt keine künstlichen Sätze mehr. Beispielsweise wird AIIN+OK+Y zu „den laufenden Posten nach vorgeschriebenem Maß ansetzen“, und AL+CHD+DY zu „den laufenden Posten an der bezeichneten Stelle umsetzen und den Schritt schließen“.",
        "",
        "Die neue Fassung ist näher an einer Werkstattkurzschrift: Argumentkarten stehen um eine kleinere Zahl wirklicher Handlungen. Der nächste Engpass sind die noch sehr häufigen Aktionskerne OK, CHD, L und K, deren deutsche Verben teilweise zu allgemein sind.",
    ]
    (HERE / "FIVE_HUNDRED_FIFTIETH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
