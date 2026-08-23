#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
POCKET = ROOT / "experiments/yolo/sidequest_semantic_post_centennial_handbook_hundred_tenth_edition"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_defaults_hundred_first_edition/HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv"

TABLETS = {
    "HERBAL_MATERIAL": "Bildpflanze, Wurzel, Zutat und Pflanzenteil",
    "EXTRACT_FILTER_VESSEL": "Auszug, Tuch, Trennen, Auswringen, Nachseihen, Gefäß und Verwahren",
    "SETTLE_COLLECT": "Absetzen und örtliches Sammeln mit Grad, Maß, Ziel oder Schluss",
    "WASH_APPLY_TRANSFER": "Waschen, Zuführen, Anwenden, Ausgießen, Kühlen und Festbinden",
    "RARE_LOCAL_VALUE": "seltene Vollgrad-, Teil- und lokale Zusatzkarten",
}


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tablet(atoms):
    parts = set(atoms.split("+"))
    if parts & {"HO", "DCHE", "DCHOL"}:
        return "HERBAL_MATERIAL"
    if parts & {"CHEO", "CKHE", "CFH", "CPH", "DAIN", "OS", "AM"}:
        return "EXTRACT_FILTER_VESSEL"
    if parts & {"SHED", "SOLK"}:
        return "SETTLE_COLLECT"
    if parts & {"WASH", "P", "DAN", "LDDY", "ODY", "SK"}:
        return "WASH_APPLY_TRANSFER"
    return "RARE_LOCAL_VALUE"


def main():
    cards = load(POCKET / "HUNDRED_TENTH_173_CARD_POCKET.tsv")
    card_map = {r["master_card_id"]: r for r in cards}
    specialists = [r for r in cards if r["teaching_tier"] == "SPECIALIST_OR_LEARNED_CARD"]
    events = load(EVENTS)
    by_statement = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    context = defaultdict(lambda: {"before": Counter(), "after": Counter(), "events": []})
    for statement, members in by_statement.items():
        for i, row in enumerate(members):
            if row["master_card_id"] not in {x["master_card_id"] for x in specialists}:
                continue
            target = context[row["master_card_id"]]
            target["events"].append(row["event_serial"])
            if i:
                prev = card_map[members[i-1]["master_card_id"]]
                target["before"][prev["short_default_de"]] += 1
            if i + 1 < len(members):
                nxt = card_map[members[i+1]["master_card_id"]]
                target["after"][nxt["short_default_de"]] += 1

    assignment = []
    for row in specialists:
        tab = tablet(row["semantic_atoms"])
        info = context[row["master_card_id"]]
        before = info["before"].most_common(3)
        after = info["after"].most_common(3)
        assignment.append({
            "tablet_id": tab,
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["all_registered_surfaces"],
            "semantic_atoms": row["semantic_atoms"],
            "short_default_de": row["short_default_de"],
            "event_count": row["event_count"],
            "records": row["records"],
            "event_serials": "|".join(info["events"]),
            "common_left_cues": "|".join(f"{x}:{n}" for x, n in before) if before else "STATEMENT_ENTRY",
            "common_right_cues": "|".join(f"{x}:{n}" for x, n in after) if after else "STATEMENT_END",
            "learning_rule": "memorize whole card; use atoms only where the registered card already licenses them",
        })
    write_tsv("HUNDRED_FOURTEENTH_46_SPECIALIST_CARD_ASSIGNMENTS.tsv", assignment)

    summary_rows = []
    for tablet_id, content in TABLETS.items():
        members = [r for r in assignment if r["tablet_id"] == tablet_id]
        summary_rows.append({
            "tablet_id": tablet_id,
            "teaching_content": content,
            "card_count": str(len(members)),
            "event_count": str(sum(int(r["event_count"]) for r in members)),
            "master_forms": "|".join(r["master_form"] for r in members),
            "records": "|".join(sorted({rec for r in members for rec in r["records"].split("|")})),
            "apprentice_instruction": "copy the whole registered card, recite its short default, then place it beside one familiar core cue",
        })
    write_tsv("HUNDRED_FOURTEENTH_FIVE_SPECIALIST_TABLETS.tsv", summary_rows)

    md = ["# Fünf Spezialtafeln für den Lehrling", ""]
    for tab in summary_rows:
        md += [f"## {tab['tablet_id']}", "", tab["teaching_content"], ""]
        for row in [r for r in assignment if r["tablet_id"] == tab["tablet_id"]]:
            md.append(f"- `{row['master_form']}` = {row['short_default_de']} ({row['event_count']}×; {row['records']})")
        md.append("")
    (OUT / "HUNDRED_FOURTEENTH_APPRENTICE_SPECIALIST_TABLETS.md").write_text("\n".join(md), encoding="utf-8")

    report = [
        "# Hundertvierzehnte Runde: die 46 Spezialkarten werden fünf Tafeln", "",
        "Die Spezialschicht ist keine ungeordnete Restekiste mehr. Zwölf Karten gehören zur Herbal-",
        "Materialtafel, elf zu Auszug/Filter/Gefäß, elf zu Absetzen/Sammeln, neun zu Waschen/Anwenden/",
        "Transfer und drei zu seltenen lokalen Vollwerten.", "",
        "Der Lehrling zerlegt diese Karten nicht frei. Er lernt die Ganzkarte, spricht den kurzen Default",
        "und setzt sie neben einen vertrauten Kernhinweis. Die Links-/Rechts-Cues zeigen für jede Karte",
        "die häufigsten unmittelbaren Nachbarn in den festen Aussagen.", "",
        "Damit besteht das System aus 70 Kernkarten, 57 Brückenkarten und fünf kleine Tafeln mit zusammen",
        "46 Spezialkarten. Das ist für mehrere Schreiber wesentlich glaubwürdiger als 46 isolierte",
        "Satzglossen oder ein universal produktives Alphabet.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_FOURTEENTH_SPECIALIST_TABLET_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    counts = Counter(r["tablet_id"] for r in assignment)
    summary = {"status": "COMPLETE", "specialist_cards": len(assignment), "tablets": len(summary_rows), "tablet_counts": dict(counts)}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
