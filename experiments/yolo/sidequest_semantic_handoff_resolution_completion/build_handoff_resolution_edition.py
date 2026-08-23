#!/usr/bin/env python3
"""Resolve the 19 open work-cell handoffs in the creative ten-page edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_step_closure_completion"

DICT_IN = BASE / "SELECTED_173_STEP_CLOSURE_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_STEP_CLOSURE_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_STEP_CLOSURE_SENTENCES.tsv"
ENDING_IN = BASE / "STATEMENT_ENDINGS.tsv"

DICT_OUT = HERE / "SELECTED_173_HANDOFF_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_HANDOFF_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_HANDOFF_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_HANDOFF_RECORDS.md"
REGISTER_OUT = HERE / "HANDOFF_REGISTER.tsv"
RELEASE_OUT = HERE / "RECORD_RELEASE_REGISTER.tsv"
CHECK_OUT = HERE / "BUILD_CHECK.json"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def handoff(source: str, target: str, category: str, carried: str, target_reading: str, reason: str) -> dict[str, str]:
    return {
        "source_statement_id": source,
        "target_statement_id": target,
        "handoff_category": category,
        "carried_register_de": carried,
        "target_reading_de": target_reading,
        "workshop_reason_de": reason,
    }


HANDOFFS = [
    handoff("H1-S001", "H1-S002", "DIRECT_MATERIAL", "bemessener Wurzelauszug", "Setze den bemessenen Wurzelauszug an, wärme ihn an, führe ihn weiter und halte ihn bereit", "Der aktive Auszug wird weiterbehandelt; der zuletzt notierte Wurzelrest bleibt nur Reserve."),
    handoff("H2-S001", "H2-S002", "DIRECT_MATERIAL", "bemessener Pflanzenansatz", "Führe den bemessenen Pflanzenansatz als Folgeansatz samt seinem Fortsetzungsposten weiter und nimm daraus das Sollmaß", "Der gewonnene und bemessene Posten wird zum Folgeansatz."),
    handoff("H2-S002", "H2-S003", "DIRECT_MATERIAL", "weitergeführter Folgeansatz", "Gib den weitergeführten Folgeansatz in den Topf, bearbeite ihn bis zur Weichstufe und entnimm das Zutatenmaß", "Der offene Folgeansatz wird im Topf weiterbearbeitet."),
    handoff("H3-S002", "H3-S003", "NAMED_RESERVE", "Blütenreserve", "Bereite aus der Blütenreserve einen Trank nach Sollmaß", "Die ausdrücklich zurückgelegte Reserve ist der Vorposten der nächsten Zelle."),
    handoff("H3-S003", "H3-S004", "NAMED_RESERVE", "restliche Blütenreserve", "Nimm die restliche Blütenreserve als Folgeposten, setze die Fortsetzung an und halte sie bereit", "Neben dem erzeugten Trank bleibt der benannte Reservegriff aktiv und wird erneut gewählt."),
    handoff("H4-S002", "H4-S003", "DIRECT_MATERIAL", "verwahrter Ansatz", "Nimm den Auszug aus dem verwahrten Ansatz nach Postenmaß, wärme ihn länger und schließe die Fortsetzung", "Die nächste Zelle entnimmt ausdrücklich daraus."),
    handoff("H5-S001", "H5-S002", "DIRECT_MATERIAL", "vorbereiteter Zutatenansatz", "Wasche die bezeichnete Stelle, setze den vorbereiteten Zutatenansatz an und trage ihn auf", "Der vorbereitete Ansatz wird zur lokalen Anwendung weitergereicht."),
    handoff("H5-S003", "H5-S004", "DIRECT_MATERIAL", "zerriebene Stängel", "Setze die zerriebenen Stängel an, gib den Auszug zu und seih ab", "Das unmittelbar zerriebene Pflanzenmaterial geht in den Auszugsschritt."),
    handoff("H5-S004", "H5-S005", "DIRECT_MATERIAL", "geseihter Ansatz", "Setze den geseihten Ansatz als Zutat an, nimm den Auszug daraus und wende ihn an", "Der geseihte Ansatz wird zum Gebrauchsauszug weiterverarbeitet."),
    handoff("H5-S005", "H5-S006", "DIRECT_MATERIAL", "Anwendungsauszug", "Wähle für die nächste Gabe diesen Anwendungsauszug als Folgeposten und das Sollmaß", "Die folgende Gabe wird aus demselben Anwendungsauszug bemessen."),
    handoff("B1-S006", "B1-S007", "DIRECT_MATERIAL", "abgekühlte Badmischung", "Setze die abgekühlte Badmischung um und schließe", "Portion und Badzusatz bilden nach Durchlauf und Abkühlen den aktiven Posten."),
    handoff("B1-S011", "B1-S012", "DIRECT_MATERIAL", "durchgeleiteter Waschposten", "Beginne mit dem durchgeleiteten Waschposten den Waschgang, setze kurz an, wasche und schließe", "Der am Durchlass angesetzte Posten speist den nächsten Waschgang."),
    handoff("B1-S014", "B1-S015", "DIRECT_MATERIAL", "abgeleitete Arbeitsflüssigkeit", "Fülle das Gefäß mit der abgeleiteten Arbeitsflüssigkeit, setze den Inhalt um und schließe", "Was am Auslass abgeführt wurde, wird im folgenden Gefäß aufgefangen."),
    handoff("B2-S006", "B2-S007", "DIRECT_MATERIAL", "weitergeführter Überlaufposten", "Gib dem weitergeführten Überlaufposten Frischwasser zu und schließe", "Frischwasser ergänzt den am Überlauf offen weitergeführten Posten."),
    handoff("B2-S010", "B2-S011", "DIRECT_MATERIAL", "Klarflüssigkeit", "Gib der Klarflüssigkeit eine Portion zu, nimm daraus eine weitere Portion, setze länger an und schließe", "Die an der Düse gewonnene Klarflüssigkeit ist Quelle der nächsten Portionen."),
    handoff("B2-S014", "B2-S015", "APPARATUS_STATE", "Bodenablauf geschlossen", "Halte den Bodenablauf geschlossen, gib Spülwasser zu, setze länger an und schließe", "Hier wird kein Stoff, sondern die geschlossene Gerätestellung weitergereicht."),
    handoff("B3-S004", "B3-S005", "DIRECT_MATERIAL", "entnommene Sollmaßportion", "Setze die entnommene Sollmaßportion um und schließe", "Die nach Sollmaß entnommene Portion ist der Posten der kurzen Folgezelle."),
    handoff("B3-S009", "B3-S010", "DIRECT_MATERIAL", "angesetzter Posten", "Führe den angesetzten Posten am Einlass zu, nimm die kurze Folge und schließe", "Der offene Ansatz wird unmittelbar am Einlass weitergeführt."),
    handoff("B3-S011", "B3-S012", "DIRECT_MATERIAL", "aufgestrichener und abgekühlter Ansatz", "Lass den aufgestrichenen und abgekühlten Ansatz absetzen und schließe", "Der behandelte Posten geht ohne neuen Materialwechsel in die Absetzphase."),
]


RELEASE_OBJECTS = {
    "H1-S002": "bereiter Wurzelauszug",
    "H2-S003": "weich bearbeiteter Folgeansatz mit Zutatenmaß",
    "H3-S004": "bereitgehaltene Blütenreserve/Folgeposten",
    "H4-S004": "angewärmte Ansatzportion am Ziel",
    "H5-S006": "nächste Gabe mit Sollmaß vorgemerkt",
    "B1-S021": "nächster Posten am Ziel",
    "B5-S003": "Gerätestellung und umgesetzter Posten",
    "B6-S001": "Posten am Endziel",
}


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentences = read_tsv(SENTENCE_IN)
    endings = read_tsv(ENDING_IN)
    if (len(dictionary), len(events), len(sentences), len(endings)) != (173, 381, 116, 116):
        raise AssertionError("unexpected input dimensions")

    sentence_map = {row["statement_id"]: row for row in sentences}
    ending_map = {row["statement_id"]: row for row in endings}
    source_map = {row["source_statement_id"]: row for row in HANDOFFS}
    target_map = {row["target_statement_id"]: row for row in HANDOFFS}
    if len(source_map) != 19 or len(target_map) != 19:
        raise AssertionError("handoff endpoints must be unique")
    for source, row in source_map.items():
        ending = ending_map[source]
        if ending["ending_class"] != "HANDOFF_OPEN" or ending["next_statement_id"] != row["target_statement_id"]:
            raise AssertionError(f"invalid handoff edge {source}")

    out_dictionary: list[dict[str, str]] = []
    for original in dictionary:
        row = dict(original)
        row["handoff_layer"] = "CARD_VALUE_UNCHANGED__RESOLUTION_AT_STATEMENT_EDGE"
        out_dictionary.append(row)

    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        source = source_map.get(row["statement_id"])
        target = target_map.get(row["statement_id"])
        row["handoff_out_category"] = source["handoff_category"] if source else ""
        row["handoff_out_register_de"] = source["carried_register_de"] if source else ""
        row["handoff_out_target_statement_id"] = source["target_statement_id"] if source else ""
        row["handoff_in_category"] = target["handoff_category"] if target else ""
        row["handoff_in_register_de"] = target["carried_register_de"] if target else ""
        row["handoff_in_source_statement_id"] = target["source_statement_id"] if target else ""
        row["handoff_layer_note"] = "STATEMENT_EDGE_ONLY__CARD_VALUE_UNCHANGED"
        out_events.append(row)

    out_sentences: list[dict[str, str]] = []
    for original in sentences:
        row = dict(original)
        source = source_map.get(row["statement_id"])
        target = target_map.get(row["statement_id"])
        row["handoff_previous_workshop_sentence_de"] = original["workshop_sentence_de"]
        if target:
            row["workshop_sentence_de"] = target["target_reading_de"]
        row["handoff_out_category"] = source["handoff_category"] if source else ""
        row["handoff_out_register_de"] = source["carried_register_de"] if source else ""
        row["handoff_out_target_statement_id"] = source["target_statement_id"] if source else ""
        row["handoff_in_category"] = target["handoff_category"] if target else ""
        row["handoff_in_register_de"] = target["carried_register_de"] if target else ""
        row["handoff_in_source_statement_id"] = target["source_statement_id"] if target else ""
        row["handoff_resolution"] = "TARGET_REWRITTEN" if target else "UNCHANGED"
        out_sentences.append(row)

    handoff_rows: list[dict[str, str]] = []
    for index, item in enumerate(HANDOFFS, 1):
        source = sentence_map[item["source_statement_id"]]
        target = sentence_map[item["target_statement_id"]]
        handoff_rows.append({
            "handoff_id": f"H{index:02d}",
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            **item,
            "source_event_ids": source["event_ids"],
            "target_event_ids": target["event_ids"],
            "source_reading_de": source["workshop_sentence_de"],
            "previous_target_reading_de": target["workshop_sentence_de"],
        })

    release_rows: list[dict[str, str]] = []
    for statement_id, released in RELEASE_OBJECTS.items():
        sentence = next(row for row in out_sentences if row["statement_id"] == statement_id)
        release_rows.append({
            "statement_id": statement_id,
            "record_unit_id": sentence["record_unit_id"],
            "page": sentence["page"],
            "released_register_de": released,
            "release_effect_de": "Record-Ende: Besitzer, Posten, Quelle, Ziel und Arbeitsgang entlassen",
            "workshop_sentence_de": sentence["workshop_sentence_de"],
        })

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(REGISTER_OUT, handoff_rows)
    write_tsv(RELEASE_OUT, release_rows)

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        records[row["record_unit_id"]].append(row)
    lines = [
        "# Elf Records mit aufgelösten Übergaben",
        "",
        "Die Klammermarken stammen aus der vorigen Runde; fett gesetzte Übergaben benennen den konkret mitgeführten Registerinhalt.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = records[record]
        lines.extend([f"## {record} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            incoming = f" **[ÜBERNIMMT: {row['handoff_in_register_de']}]**" if row["handoff_in_register_de"] else ""
            outgoing = f" **[REICHT WEITER: {row['handoff_out_register_de']}]**" if row["handoff_out_register_de"] else ""
            lines.append(
                f"{index}. **{row['statement_id']}** — {row['workshop_sentence_de'].rstrip('.')} "
                f"{row['step_editor_label']}{incoming}{outgoing}"
            )
        lines.extend(["", "### Fortlaufend", ""])
        lines.append(" ".join(
            f"{row['workshop_sentence_de'].rstrip('.')} {row['step_editor_label']}"
            for row in rows
        ))
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    category_counts = Counter(row["handoff_category"] for row in HANDOFFS)
    checks = {
        "cards_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(out_sentences) == 116,
        "records_11": set(records) == set(RECORD_ORDER),
        "handoffs_19": len(handoff_rows) == 19,
        "target_rewrites_19": sum(row["handoff_resolution"] == "TARGET_REWRITTEN" for row in out_sentences) == 19,
        "direct_material_16": category_counts["DIRECT_MATERIAL"] == 16,
        "named_reserve_2": category_counts["NAMED_RESERVE"] == 2,
        "apparatus_state_1": category_counts["APPARATUS_STATE"] == 1,
        "record_releases_8": len(release_rows) == 8,
        "source_edges_exact": {row["statement_id"] for row in out_sentences if row["step_ending_class"] == "HANDOFF_OPEN"} == set(source_map),
        "dictionary_values_unchanged": all(
            row["concrete_word_reading_de"] == original["concrete_word_reading_de"]
            for row, original in zip(out_dictionary, dictionary)
        ),
        "event_values_unchanged": all(
            row["concrete_word_reading_de"] == original["concrete_word_reading_de"]
            for row, original in zip(out_events, events)
        ),
        "all_target_readings_concrete": all(row["target_reading_de"] for row in HANDOFFS),
        "only_fixed_pages": {row["page"] for row in out_events} == ALLOWED_PAGES,
        "sealed_absent": not any(row["page"].startswith("f84") for row in out_events),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(out_dictionary),
            "events": len(out_events),
            "sentences": len(out_sentences),
            "records": len(records),
            "handoffs": len(handoff_rows),
            "handoff_categories": dict(sorted(category_counts.items())),
            "rewritten_targets": sum(row["handoff_resolution"] == "TARGET_REWRITTEN" for row in out_sentences),
            "record_releases": len(release_rows),
        },
        "working_rule": "CARRY ACTIVE MATERIAL; PRESERVE NAMED RESERVES; ONCE CARRY APPARATUS STATE",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, REGISTER_OUT, RELEASE_OUT, CHECK_OUT]
    summary = {
        "status": result["status"],
        "counts": result["counts"],
        "input_hashes": {path.name: sha256(path) for path in [DICT_IN, EVENT_IN, SENTENCE_IN, ENDING_IN]},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "sealed": result["sealed"],
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)
