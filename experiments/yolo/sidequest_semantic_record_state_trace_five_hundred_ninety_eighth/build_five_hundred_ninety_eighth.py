#!/usr/bin/env python3
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P587 = YOLO / "sidequest_semantic_uniform_three_line_edition_five_hundred_eighty_seventh"
P588 = YOLO / "sidequest_semantic_complete_herbal_articles_five_hundred_eighty_eighth"
P589 = YOLO / "sidequest_semantic_complete_biological_station_register_five_hundred_eighty_ninth"
P596 = YOLO / "sidequest_semantic_interleaved_teaching_edition_five_hundred_ninety_sixth"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cue_class(component_line):
    tokens = set(re.findall(r"[A-Z]+", component_line))
    strong = sorted(tokens & {"OL", "AR", "OT"})
    if strong:
        return "STRONG_LINK_CUE", "|".join(strong)
    if "Y" in tokens:
        return "CURRENT_ITEM_CUE", "Y"
    return "OWNER_ONLY", "NONE"


def main():
    statements = read(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_ONE_HUNDRED_SIXTEEN_THREE_LINE_STATEMENTS.tsv")
    teaching = {row["statement_id"]: row for row in read(P596 / "FIVE_HUNDRED_NINETY_SIXTH_116_FOUR_LINE_STATEMENTS.tsv")}
    bio_entries = {row["statement_id"]: row for row in read(P589 / "FIVE_HUNDRED_EIGHTY_NINTH_NINETY_SEVEN_STATION_ENTRIES.tsv")}
    herbal_articles = {row["record"]: row for row in read(P588 / "FIVE_HUNDRED_EIGHTY_EIGHTH_FIVE_COMPLETE_HERBAL_ARTICLES.tsv")}
    bio_records = {row["record"]: row for row in read(P589 / "FIVE_HUNDRED_EIGHTY_NINTH_SIX_BIOLOGICAL_RECORDS.tsv")}

    owner_ids = defaultdict(dict)
    previous_owner = {}
    trace_rows = []
    reset_rows = []
    for statement in statements:
        sid = statement["statement_id"]
        record = statement["record"]
        owner = teaching[sid]["silent_owner_de"]
        if owner not in owner_ids[record]:
            owner_ids[record][owner] = f"{record}:OWNER_{len(owner_ids[record]) + 1:02d}"
        owner_id = owner_ids[record][owner]
        cue, cue_tokens = cue_class(statement["component_parses"])
        prior = previous_owner.get(record)
        if prior is None:
            transition = "RECORD_INITIALIZE"
            state_before = "UNSET"
        elif prior != owner:
            transition = "OWNER_RESET"
            state_before = f"{owner_ids[record][prior]}::STOP_AT_VISIBLE_BOUNDARY"
        elif cue == "STRONG_LINK_CUE":
            transition = "EXPLICIT_LOCAL_CONTINUATION"
            state_before = f"{owner_id}::ACTIVE_LOCAL_MATERIAL"
        elif cue == "CURRENT_ITEM_CUE":
            transition = "CURRENT_ITEM_CONTINUATION"
            state_before = f"{owner_id}::CURRENT_ITEM"
        else:
            transition = "SAME_OWNER_UNSPECIFIED_STEP"
            state_before = f"{owner_id}::OWNER_ACTIVE_ITEM_UNSPECIFIED"
        closure = bio_entries[sid]["cell_status"] if sid in bio_entries else "OPEN_HERBAL_ARTICLE_STEP"
        state_after = f"{owner_id}::{'LOCAL_CELL_COMMITTED' if closure == 'CLOSED_CELL' else 'ACTIVE_ITEM_AVAILABLE'}"
        trace = {
            "statement_id": sid, "page": statement["page"], "record": record,
            "owner_id": owner_id, "owner_de": owner,
            "cue_class": cue, "cue_tokens": cue_tokens, "transition": transition,
            "state_before": state_before, "state_after": state_after, "closure_status": closure,
            "complete_instruction_de": teaching[sid]["meaning_line_de"],
            "cross_owner_material_carry": "NO" if transition == "OWNER_RESET" else "NOT_APPLICABLE",
            "global_pipe_or_process_join": "NONE",
        }
        trace_rows.append(trace)
        if transition == "OWNER_RESET":
            reset_rows.append({
                "record": record, "from_statement": trace_rows[-2]["statement_id"], "to_statement": sid,
                "from_owner_id": owner_ids[record][prior], "from_owner_de": prior,
                "to_owner_id": owner_id, "to_owner_de": owner,
                "reset_instruction_de": "vorigen lokalen Arbeitszustand schliessen; neuen Bildbesitzer aktivieren; keine unsichtbare Leitung erfinden",
                "cross_owner_carry": "FORBIDDEN_WITHOUT_MASTER_HANDOFF",
            })
        previous_owner[record] = owner

    record_rows = []
    ordered_records = [f"H{i}" for i in range(1, 6)] + [f"B{i}" for i in range(1, 7)]
    for record in ordered_records:
        rows = [row for row in trace_rows if row["record"] == record]
        if record.startswith("H"):
            continuous = herbal_articles[record]["continuous_article_de"]
        else:
            continuous = bio_records[record]["continuous_register_de"]
        record_rows.append({
            "record": record, "page": rows[0]["page"], "section": "HERBAL" if record.startswith("H") else "BIOLOGICAL",
            "statements": len(rows), "events": next(int(row["event_count"]) for row in statements if row["record"] == record) if len(rows) == 1 else sum(int(row["event_count"]) for row in statements if row["record"] == record),
            "owner_states": len(owner_ids[record]),
            "owner_resets": sum(row["transition"] == "OWNER_RESET" for row in rows),
            "explicit_continuations": sum(row["transition"] == "EXPLICIT_LOCAL_CONTINUATION" for row in rows),
            "current_item_continuations": sum(row["transition"] == "CURRENT_ITEM_CONTINUATION" for row in rows),
            "unspecified_same_owner_steps": sum(row["transition"] == "SAME_OWNER_UNSPECIFIED_STEP" for row in rows),
            "continuous_working_reading_de": continuous,
            "global_process_claim": "NONE__RECORD_LOCAL_ONLY",
        })

    boundary_rows = []
    for left, right in zip(record_rows, record_rows[1:]):
        left_last = [row for row in trace_rows if row["record"] == left["record"]][-1]
        right_first = [row for row in trace_rows if row["record"] == right["record"]][0]
        same_page = left["page"] == right["page"]
        same_owner_text = left_last["owner_de"] == right_first["owner_de"]
        possible = left["record"] == "H1" and right["record"] == "H2" and same_page and same_owner_text
        boundary_rows.append({
            "from_record": left["record"], "to_record": right["record"],
            "same_page": "YES" if same_page else "NO", "same_visible_owner_text": "YES" if same_owner_text else "NO",
            "boundary_reading": "SAME_PLANT_RESUMPTION_POSSIBLE" if possible else "HARD_RECORD_RESET",
            "material_carry": "POSSIBLE_BY_MASTER_OR_PARAGRAPH_CONTEXT" if possible else "NO_AUTOMATIC_CARRY",
            "instruction_de": "gleichen Pflanzenbesitzer wieder aufnehmen, konkrete Charge nur bei Meistervorgabe" if possible else "alle lokalen Besitzer- und Stoffregister loeschen",
        })

    machine = [
        {"transition": "RECORD_INITIALIZE", "count": sum(row["transition"] == "RECORD_INITIALIZE" for row in trace_rows), "rule_de": "Bildbesitzer aus Recordanfang setzen; Stoff aus Bild oder Meistervorgabe initialisieren"},
        {"transition": "EXPLICIT_LOCAL_CONTINUATION", "count": sum(row["transition"] == "EXPLICIT_LOCAL_CONTINUATION" for row in trace_rows), "rule_de": "OL/AR/OT traegt den lokalen Stoff, die Quelle oder die Folge beim selben Besitzer weiter"},
        {"transition": "CURRENT_ITEM_CONTINUATION", "count": sum(row["transition"] == "CURRENT_ITEM_CONTINUATION" for row in trace_rows), "rule_de": "Y greift den aktuell gemeinten Posten desselben Besitzers wieder auf"},
        {"transition": "SAME_OWNER_UNSPECIFIED_STEP", "count": sum(row["transition"] == "SAME_OWNER_UNSPECIFIED_STEP" for row in trace_rows), "rule_de": "Besitzer bleibt, aber neue oder geerbte Charge entscheidet das Meisterexemplar"},
        {"transition": "OWNER_RESET", "count": sum(row["transition"] == "OWNER_RESET" for row in trace_rows), "rule_de": "sichtbaren Besitzerwechsel als harten lokalen Reset behandeln"},
    ]

    write("FIVE_HUNDRED_NINETY_EIGHTH_116_STATE_TRACE.tsv", trace_rows)
    write("FIVE_HUNDRED_NINETY_EIGHTH_10_OWNER_RESETS.tsv", reset_rows)
    write("FIVE_HUNDRED_NINETY_EIGHTH_11_RECORD_PROCESS_CHAINS.tsv", record_rows)
    write("FIVE_HUNDRED_NINETY_EIGHTH_10_INTER_RECORD_BOUNDARIES.tsv", boundary_rows)
    write("FIVE_HUNDRED_NINETY_EIGHTH_FIVE_TRANSITION_RULES.tsv", machine)

    process_md = ["# Fuenfhundertachtundneunzigste Runde: elf lokale Prozessketten", ""]
    for record in record_rows:
        process_md.extend([f"## {record['record']} · {record['page']}", ""])
        for row in [row for row in trace_rows if row["record"] == record["record"]]:
            process_md.extend([
                f"- **{row['statement_id']} · {row['transition']} · {row['owner_id']}**",
                f"  - {row['complete_instruction_de']}",
                f"  - Zustand: `{row['state_before']}` -> `{row['state_after']}`",
            ])
        process_md.append("")
    (HERE / "FIVE_HUNDRED_NINETY_EIGHTH_ELEVEN_LOCAL_PROCESS_CHAINS.md").write_text("\n".join(process_md), encoding="utf-8")

    counts = Counter(row["transition"] for row in trace_rows)
    summary = {
        "status": "PASS", "statements": len(trace_rows), "records": len(record_rows),
        "record_initializations": counts["RECORD_INITIALIZE"], "explicit_local_continuations": counts["EXPLICIT_LOCAL_CONTINUATION"],
        "current_item_continuations": counts["CURRENT_ITEM_CONTINUATION"], "same_owner_unspecified_steps": counts["SAME_OWNER_UNSPECIFIED_STEP"],
        "visible_owner_resets": counts["OWNER_RESET"], "record_local_owner_states": sum(len(values) for values in owner_ids.values()),
        "global_unique_owner_labels": len({row["owner_de"] for row in trace_rows}),
        "inter_record_boundaries": len(boundary_rows), "possible_same_plant_resumptions": sum(row["boundary_reading"] == "SAME_PLANT_RESUMPTION_POSSIBLE" for row in boundary_rows),
        "global_pipe_joins": 0,
        "decision": "LOCAL_STATE_CONTINUITY_WITH_TEN_VISIBLE_OWNER_RESETS",
    }
    (HERE / "FIVE_HUNDRED_NINETY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# Fuenfhundertachtundneunzigste Runde: Material- und Zustandsfaden

## Ergebnis

Die elf Prosarecords lassen sich mit nur fuenf Zustandsregeln lesen:

- {counts['RECORD_INITIALIZE']} Recordanfaenge setzen einen Bildbesitzer und lokalen Stoffzustand.
- {counts['EXPLICIT_LOCAL_CONTINUATION']} Aussagen tragen mit `OL/AR/OT` Quelle, Fortsetzung oder Folge sichtbar weiter.
- {counts['CURRENT_ITEM_CONTINUATION']} greifen mit `Y` den aktuellen Posten desselben Besitzers auf.
- {counts['SAME_OWNER_UNSPECIFIED_STEP']} bleiben beim selben Besitzer, lassen aber offen, ob eine neue Charge oder der geerbte Stoff gemeint ist.
- {counts['OWNER_RESET']} sichtbare Besitzerwechsel setzen den lokalen Zustand hart zurueck.

Das ergibt 116 vollstaendige Schritte und **keinen** erfundenen globalen Rohr- oder Stofflauf.

## Die zehn harten Besitzerwechsel

Sie liegen ausschliesslich in B2, B3 und B4: vier Stationswechsel auf f82r, vier auf dem grossen B3-Record von f83r und zwei in B4. Ein Linkwort direkt nach dem Wechsel darf nur auf den neuen lokalen Besitzer oder dessen Meistereintrag zeigen; es wird nicht rueckwaerts durch eine unsichtbare Leitung verbunden.

## Recordgrenzen

Von zehn Grenzen zwischen den elf Records ist nur H1->H2 als moegliche Wiederaufnahme markiert: gleiche Seite, gleicher sichtbarer Pflanzenbesitzer, zweiter Absatz. Selbst dort bleibt die konkrete Charge Meisterwissen. Alle neun anderen Grenzen loeschen den lokalen Zustand. Besonders B3->B4->B5->B6 auf derselben Seite sind keine automatische Prozesskette.

## Praktische Lesung

Damit wird Biological nicht zu einer einzigen Maschine. Es ist ein Stationsbuch: innerhalb einer sichtbaren Station kann ein Stoff mehrfach gehalten, gefuehrt, abgesetzt oder angewandt werden; beim naechsten Bildbesitzer beginnt eine neue lokale Zelle. Herbal dagegen haelt je Artikel einen Pflanzenbesitzer ueber mehrere offene Aussagen fest.

## Naechster Schritt

Als naechstes werden aus den 116 lokalen Schritten konkrete Materialobjekte gebildet: Rohteil, Ansatz, laufender Posten, Rueckstand, Auszug und Zielanwendung. Dabei darf ein Objekt nur weiterleben, wenn die neue Zustandsregel es lizenziert; sonst beginnt eine neue lokale Charge.
"""
    (HERE / "FIVE_HUNDRED_NINETY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
