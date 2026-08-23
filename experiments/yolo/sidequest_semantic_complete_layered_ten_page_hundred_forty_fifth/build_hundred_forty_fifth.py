#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R134 = ROOT / "experiments/yolo/sidequest_semantic_current_ten_page_edition_hundred_thirty_fourth"
R144 = ROOT / "experiments/yolo/sidequest_semantic_layered_current_edition_hundred_forty_fourth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(R144 / "HUNDRED_FORTY_FOURTH_173_LAYERED_DICTIONARY.tsv")
    prose = read_tsv(R144 / "HUNDRED_FORTY_FOURTH_381_LAYERED_EVENTS.tsv")
    statements = read_tsv(R144 / "HUNDRED_FORTY_FOURTH_116_LAYERED_STATEMENTS.tsv")
    moulds = read_tsv(R144 / "HUNDRED_FORTY_FOURTH_TEN_REVISED_MOULDS.tsv")
    owners = read_tsv(R144 / "HUNDRED_FORTY_FOURTH_ELEVEN_OWNER_REGISTERS.tsv")
    astro = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_395_ASTRO_GROUPS.tsv")
    old_unified = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_776_UNIFIED_LEDGER.tsv")
    jobs = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_FOUR_JOBS.tsv")

    write_tsv("HUNDRED_FORTY_FIFTH_173_LAYERED_DICTIONARY.tsv", cards)
    write_tsv("HUNDRED_FORTY_FIFTH_381_LAYERED_PROSE.tsv", prose)
    write_tsv("HUNDRED_FORTY_FIFTH_116_LAYERED_STATEMENTS.tsv", statements)
    write_tsv("HUNDRED_FORTY_FIFTH_395_OWNER_LOCAL_ASTRO.tsv", astro)

    prose_by_group = {f"E{int(row['event_serial']):03d}": row for row in prose}
    statement_by_id = {row["statement_id"]: row for row in statements}
    unified = []
    for row in old_unified:
        group = row["source_group_id"]
        if group.startswith("E"):
            event = prose_by_group[group]
            statement = statement_by_id[event["statement_id"]]
            unified.append({
                "unified_serial": row["unified_serial"], "job_id": row["job_id"],
                "phase": row["phase"], "page": row["page"], "local_unit": row["local_unit"],
                "source_group_id": group, "visible_owner": statement["owner_argument_de"],
                "visible_surface": event["visible_surface"],
                "portable_card_value_de": event["portable_card_value_de"],
                "owner_argument_de": statement["owner_argument_de"],
                "controlled_local_expansion_de": statement["controlled_fluent_de"],
                "meaning_provenance": "PROSE_CARD_PLUS_OWNER",
                "menu_status": "ACTIVE_PROSE", "orientation": "PROSE_ORDER", "crosspage_key": "NONE",
            })
        else:
            astro_row = next(a for a in astro if a["source_group_id"] == group)
            unified.append({
                "unified_serial": row["unified_serial"], "job_id": row["job_id"],
                "phase": row["phase"], "page": row["page"], "local_unit": row["local_unit"],
                "source_group_id": group, "visible_owner": astro_row["visible_owner"],
                "visible_surface": astro_row["visible_surface"],
                "portable_card_value_de": "NO_PROSE_CARD_VALUE",
                "owner_argument_de": astro_row["visible_owner"],
                "controlled_local_expansion_de": astro_row["local_astro_value_de"],
                "meaning_provenance": "ASTRO_OWNER_LOCAL_MENU",
                "menu_status": astro_row["menu_status"], "orientation": astro_row["orientation"],
                "crosspage_key": astro_row["crosspage_key"],
            })
    write_tsv("HUNDRED_FORTY_FIFTH_776_LAYERED_LEDGER.tsv", unified)

    job_rows = []
    for job in jobs:
        job_groups = [row for row in unified if row["job_id"] == job["job_id"]]
        prose_groups = [row for row in job_groups if row["meaning_provenance"] == "PROSE_CARD_PLUS_OWNER"]
        astro_groups = [row for row in job_groups if row["meaning_provenance"] == "ASTRO_OWNER_LOCAL_MENU"]
        selected = [row for row in astro_groups if row["menu_status"] != "UNSELECTED_REFERENCE_OPTION"]
        job_rows.append({
            "job_id": job["job_id"], "title_de": job["title_de"],
            "what_records": job["what_records"], "how_records": job["how_records"],
            "prose_groups": str(len(prose_groups)), "astro_menu_groups": str(len(astro_groups)),
            "selected_astro_groups": str(len(selected)),
            "owner_supplied_subject_de": "Bildpflanze oder lokale Station/Anwendung gemäß Record",
            "portable_instruction_boundary": "Nur Kartenwerte in der 173er Tabelle sind portabel",
            "optional_when_de": job["selected_when_condition_de"],
            "controlled_scenario_de": job["complete_job_instruction_de"],
            "claim_boundary": "CREATIVE_USE_SCENARIO__NO_WRITTEN_CROSSPAGE_POINTER",
        })
    write_tsv("HUNDRED_FORTY_FIFTH_FOUR_LAYERED_JOBS.tsv", job_rows)

    by_record = defaultdict(list)
    for row in statements:
        by_record[row["record_unit_id"]].append(row)
    readable = ["# Vollständige geschichtete Zehnseiten-Ausgabe", "", "## Prosa: Besitzer, Karten, Lesung", ""]
    for rid in [row["record_unit_id"] for row in owners]:
        rows = by_record[rid]
        readable += [f"### {rid} · {rows[0]['page']}", ""]
        for row in rows:
            readable += [f"- {row['statement_id']} · Besitzer: **{row['owner_argument_de']}**",
                         f"  - Karten: {row['portable_literal_chain_de']}",
                         f"  - Lesung: {row['controlled_fluent_de']}"]
        readable.append("")
    readable += ["## Astro: drei lokale Menüs", "",
                 "- f67r2: two visible wheels; every value remains tied to its sector/ring owner.",
                 "- f68r1: multipanel star menu; the 28 labels remain local station entries.",
                 "- f69v: three separate wheels; only the left wheel owns its 28-place inventory.",
                 "- No prose word, cyclic start, direction, rotation, or f68-to-f69 key is imported.", "",
                 "## Vier optionale Arbeitsszenarien", ""]
    for row in job_rows:
        readable += [f"### {row['job_id']} · {row['title_de']}", "", row["controlled_scenario_de"], "",
                     f"Optional WANN: {row['optional_when_de']}", ""]
    (OUT / "HUNDRED_FORTY_FIFTH_COMPLETE_LAYERED_EDITION.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertfünfundvierzigste Runde: die geschichtete Ausgabe umfasst wieder alle zehn Seiten", "",
        "The layered prose of R144 is now joined to the unchanged owner-local Astro menu. The edition contains",
        "173 prose cards, 381 prose events, 116 prose statements, 395 diagram groups and 776 visible groups.",
        "Each prose row exposes card value and owner separately. Each Astro row says NO_PROSE_CARD_VALUE and",
        "keeps its interpretation local to the visible diagram owner.", "",
        "The four WHAT/HOW/optional-WHEN scenarios remain useful readings, but none is allowed to rewrite the",
        "dictionary. Their plant, basin, vessel, cloth, station or celestial nouns are arguments supplied by",
        "pictures and registers. This is now the safest complete creative edition on which to improve the 132",
        "learned specialist cards without losing the readable ten-page story.", "",
        "Next examine the 132 specialist whole cards for accidental owner nouns or sentence-sized defaults and",
        "compress them into short learned meanings wherever the complete statement still reads naturally.",
    ]
    (OUT / "HUNDRED_FORTY_FIFTH_LAYERED_TEN_PAGE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "cards": len(cards), "prose_events": len(prose), "prose_statements": len(statements),
        "astro_groups": len(astro), "unified_groups": len(unified), "jobs": len(job_rows),
        "prose_portable_rows": sum(r["meaning_provenance"] == "PROSE_CARD_PLUS_OWNER" for r in unified),
        "astro_owner_local_rows": sum(r["meaning_provenance"] == "ASTRO_OWNER_LOCAL_MENU" for r in unified),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
