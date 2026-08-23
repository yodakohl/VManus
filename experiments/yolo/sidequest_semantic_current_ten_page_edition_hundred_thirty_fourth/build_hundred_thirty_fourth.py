#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R121 = ROOT / "experiments/yolo/sidequest_semantic_complete_working_edition_hundred_twenty_first"
R123 = ROOT / "experiments/yolo/sidequest_semantic_two_register_source_grammar_hundred_twenty_third"
R125 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_master_codebook_hundred_twenty_fifth"
R126 = ROOT / "experiments/yolo/sidequest_semantic_shared_card_meaning_revision_hundred_twenty_sixth"
R127 = ROOT / "experiments/yolo/sidequest_semantic_revised_continuous_prose_hundred_twenty_seventh"
R128 = ROOT / "experiments/yolo/sidequest_semantic_extension_core_revision_hundred_twenty_eighth"
R129 = ROOT / "experiments/yolo/sidequest_semantic_specialist_drawers_hundred_twenty_ninth"
R133 = ROOT / "experiments/yolo/sidequest_semantic_optional_when_jobs_hundred_thirty_third"


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
    cards = read_tsv(R129 / "HUNDRED_TWENTY_NINTH_COMPLETE_173_CARD_DICTIONARY.tsv")
    surfaces = read_tsv(R121 / "HUNDRED_TWENTY_FIRST_230_SURFACE_INDEX.tsv")
    events = read_tsv(R129 / "HUNDRED_TWENTY_NINTH_COMPLETE_381_EVENT_DICTIONARY.tsv")
    literal_statements = read_tsv(R129 / "HUNDRED_TWENTY_NINTH_COMPLETE_116_CARD_CHAINS.tsv")
    fluent_statements = read_tsv(R127 / "HUNDRED_TWENTY_SEVENTH_116_REVISED_STATEMENTS.tsv")
    records = read_tsv(R127 / "HUNDRED_TWENTY_SEVENTH_ELEVEN_REVISED_RECORDS.tsv")
    astro = read_tsv(R133 / "HUNDRED_THIRTY_THIRD_395_ASTRO_JOB_MENU.tsv")
    ledger = read_tsv(R133 / "HUNDRED_THIRTY_THIRD_776_JOB_LEDGER.tsv")
    jobs = read_tsv(R133 / "HUNDRED_THIRTY_THIRD_FOUR_WHAT_HOW_WHEN_JOBS.tsv")
    shared = read_tsv(R126 / "HUNDRED_TWENTY_SIXTH_SEVENTEEN_REVISED_MEANINGS.tsv")
    extension = read_tsv(R128 / "HUNDRED_TWENTY_EIGHTH_TWENTY_FOUR_EXTENSION_DECISIONS.tsv")
    drawers = read_tsv(R129 / "HUNDRED_TWENTY_NINTH_EIGHT_SPECIALIST_DRAWERS.tsv")
    templates = read_tsv(R123 / "HUNDRED_TWENTY_THIRD_EIGHT_SOURCE_TEMPLATES.tsv")
    hands = read_tsv(R125 / "HUNDRED_TWENTY_FIFTH_FOUR_HAND_CARD_TABLE.tsv")

    write_tsv("HUNDRED_THIRTY_FOURTH_173_CARD_DICTIONARY.tsv", cards)

    card_by_id = {row["master_card_id"]: row for row in cards}
    surface_rows = []
    for row in surfaces:
        card = card_by_id[row["master_card_id"]]
        surface_rows.append({
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "renderer_gesture": row["renderer_gesture"],
            "family_class": row["family_class"],
            "semantic_atoms": card["semantic_atoms"],
            "current_spoken_default_de": card["current_spoken_default_de"],
            "teaching_layer": card["teaching_layer"],
            "drawer": card["drawer"],
        })
    write_tsv("HUNDRED_THIRTY_FOURTH_230_SURFACE_REVERSE_KEY.tsv", surface_rows)
    write_tsv("HUNDRED_THIRTY_FOURTH_381_PROSE_EVENTS.tsv", events)

    fluent_by_id = {row["statement_id"]: row for row in fluent_statements}
    statement_rows = []
    for row in literal_statements:
        fluent = fluent_by_id[row["statement_id"]]
        statement_rows.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_surface_sequence": fluent["visible_surface_sequence"],
            "complete_spoken_card_chain_de": row["complete_spoken_card_chain_de"],
            "continuous_working_reading_de": fluent["revised_continuous_reading_de"],
            "shared_kernel_de": fluent["revised_shared_kernel_de"],
        })
    write_tsv("HUNDRED_THIRTY_FOURTH_116_PROSE_STATEMENTS.tsv", statement_rows)
    write_tsv("HUNDRED_THIRTY_FOURTH_395_ASTRO_GROUPS.tsv", astro)
    write_tsv("HUNDRED_THIRTY_FOURTH_776_UNIFIED_LEDGER.tsv", ledger)
    write_tsv("HUNDRED_THIRTY_FOURTH_FOUR_JOBS.tsv", jobs)

    md = ["# Aktuelle vollständige Zehnseiten-Ausgabe", "", "## Vier Arbeitsaufträge", ""]
    for job in jobs:
        md += [f"### {job['job_id']}: {job['title_de']}", "", f"WANN: {job['selected_when_condition_de']}", "",
               f"WAS: {job['what_records']}; WIE: {job['how_records']}", "", job["complete_job_instruction_de"], ""]
    md += ["## Elf fortlaufende Prosa-Records", ""]
    for record in records:
        md += [f"### {record['record_unit_id']} · {record['page']}", "", record["continuous_record_de"], ""]
    md += ["## Drei Himmelsinstrumente", "",
           "f67r2: zwei getrennte sichtbare Räder für Platz, Aspekt, Bedingung und Grad.",
           "f68r1: Mehrpaneel-Sternatlas mit 28 sichtbaren lokalen Adressen.",
           "f69v: drei getrennte Räder; nur das linke besitzt die lokale 28-Platz-Inventur.",
           "Alle Diagrammwerte werden am sichtbaren Besitzer gewählt; es gibt keine erzwungene Richtung oder gemeinsamen Schlüssel."]
    (OUT / "HUNDRED_THIRTY_FOURTH_COMPLETE_TEN_PAGE_EDITION.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    pocket = ["# Taschenheft der aktuellen Werkstatt", "", "## Lesen", "",
              "1. Auf den sichtbaren Besitzer zeigen.",
              "2. Oberfläche im 230er Schlüssel zur Masterkarte zurückführen.",
              "3. Einen der 41 aktiven Werte lesen oder die seltene Karte in ihrer Fachschublade nachschlagen.",
              "4. Herbal als Artikelkette, Biological als Arbeitszelle lesen.",
              "5. Y-AIIN-Y und OL-(OL+OR)-OL als Klammern behandeln.",
              "6. Zeilenende ignorieren; nur die gelernte Schlusskarte schließt.",
              "7. Astro nur am sichtbaren Ort lesen; WANN ist optional.", "", "## Siebzehn gemeinsame Karten", ""]
    for row in shared:
        pocket.append(f"- `{row['master_form']}` — {row['revised_portable_default_de']} — Formen `{row['registered_surfaces']}`")
    pocket += ["", "## Vierundzwanzig häufige Fachkarten", ""]
    for row in extension:
        pocket.append(f"- `{row['master_form']}` — {row['revised_short_default_de']} ({row['section']})")
    pocket += ["", "## Acht seltene Schubladen", ""]
    for row in drawers:
        pocket.append(f"- {row['drawer']}: {row['card_types']} Karten / {row['events']} Vorkommen — {row['teaching_description']}")
    pocket += ["", "## Schreiben", "",
               "Bedeutung wählen -> Masterkarte setzen -> Registerfolge prüfen -> Besitzer erben -> eigene Handform schreiben -> gegen den Schlüssel rücklesen."]
    (OUT / "HUNDRED_THIRTY_FOURTH_POCKET_MANUAL.md").write_text("\n".join(pocket).rstrip() + "\n", encoding="utf-8")

    theory = [
        "# Hundertvierunddreißigste Runde: aktuelle beste Arbeitstheorie", "",
        "The ten fixed pages are best read as an illustrated practical workshop compendium. Plant pages name",
        "material and preparation; figure/basin pages route and change an inherited work item; celestial pages",
        "offer optional owner-selected conditions. The strongest content expansion remains therapeutic bathing",
        "and plant preparation, with a material/bathhouse technical book as a close practical rival.", "",
        "The writing system is a mixed technical codebook: 41 actively learned recurrent cards cover 239 prose",
        "events, while 132 low-frequency exact specialist cards cover 142. The 173 master cards have 230 visible",
        "registered forms. Seventeen cards cross Herbal and Biological; two register orders and two bracket",
        "formulas make them speakable. Four hand habits alter the surface only after card choice.", "",
        "Four optional WHEN→WHAT→HOW jobs organize every one of the 381 prose events and retain all 395 Astro",
        "groups as a menu. Only 21 Astro groups are activated in the four sample jobs. This is the current most",
        "coherent creative reading of the ten pages, not a claim that the manuscript has been historically",
        "deciphered.",
    ]
    (OUT / "HUNDRED_THIRTY_FOURTH_CURRENT_THEORY.md").write_text("\n".join(theory) + "\n", encoding="utf-8")

    component_rows = [
        {"component": "SHARED_DECK", "rows": str(len(shared)), "active_use": "portable meanings across Herbal and Biological"},
        {"component": "EXTENSION_CORE", "rows": str(len(extension)), "active_use": "frequent Herbal/Bio specialist actions"},
        {"component": "SPECIALIST_DRAWERS", "rows": str(sum(int(row["card_types"]) for row in drawers)), "active_use": "rare exact learned cards"},
        {"component": "SOURCE_TEMPLATES", "rows": str(len(templates)), "active_use": "two register orders and two frames"},
        {"component": "HAND_TABLE", "rows": str(len(hands)), "active_use": "surface variation after semantic card choice"},
        {"component": "PROSE_EVENTS", "rows": str(len(events)), "active_use": "complete fixed prose"},
        {"component": "ASTRO_MENU", "rows": str(len(astro)), "active_use": "visible-owner optional conditions"},
    ]
    write_tsv("HUNDRED_THIRTY_FOURTH_EDITION_COMPONENTS.tsv", component_rows)

    report = [
        "# Hundertvierunddreißigste Runde: eine neue aktuelle Gesamtausgabe", "",
        "R121-R133 are now consolidated. The release contains a current 173-card dictionary, 230-surface reverse",
        "key, 381 prose events, 116 complete statements, eleven continuous records, 395 Astro menu groups, all",
        "776 visible groups, four optional jobs and one pocket manual.", "",
        "The active semantic economy is explicit: seventeen common cards plus 24 frequent extension cards",
        "cover 239 events. The 132 rare cards are whole-card entries in eight drawers. No visible spelling is",
        "left without a default, but rarity is not disguised as productive grammar.", "",
        "Next work should attack the content rather than rebuild infrastructure: compare the four job texts with",
        "specific ca. 1400 recipe and bathhouse phrase orders, then revise only meanings whose clause placement",
        "suggests a better concrete medieval workshop word.",
    ]
    (OUT / "HUNDRED_THIRTY_FOURTH_COMPLETE_EDITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "cards": len(cards), "surfaces": len(surface_rows), "prose_events": len(events),
               "prose_statements": len(statement_rows), "records": len(records), "astro_groups": len(astro),
               "unified_groups": len(ledger), "jobs": len(jobs), "active_cards": sum(row["teaching_layer"] != "SPECIALIST_DRAWER_WHOLE_CARD" for row in cards)}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
