#!/usr/bin/env python3
"""Build a compact apprentice phrasebook from the selected ten-page lexicon."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_open_middle_lexicon"

DICT_IN = BASE / "SELECTED_173_OPEN_MIDDLE_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_OPEN_MIDDLE_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_OPEN_MIDDLE_SENTENCES.tsv"
CORE_IN = BASE / "OPEN_MIDDLE_CORE_16_DECK.tsv"
UNIFIED_IN = BASE / "UNIFIED_173_CARD_ARCHITECTURE.tsv"

CORE_OUT = HERE / "APPRENTICE_CORE_16.tsv"
WORDS_OUT = HERE / "APPRENTICE_68_WHOLE_WORD_DECK.tsv"
LOCAL_OUT = HERE / "APPRENTICE_55_LOCAL_HEADWORDS.tsv"
DRAWERS_OUT = HERE / "APPRENTICE_LEXICAL_DRAWERS.tsv"
TEMPLATES_OUT = HERE / "APPRENTICE_9_PHRASE_TEMPLATES.tsv"
PHRASES_OUT = HERE / "APPRENTICE_116_PHRASES.tsv"
RECORDS_OUT = HERE / "APPRENTICE_11_RECORDS.md"
CHECK_OUT = HERE / "BUILD_CHECK.json"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


# These are compact apprentice headwords, not claims that distinct exact cards
# have become the same encoded symbol. Context removed from the headword remains
# explicit in context_expansion_de.
LOCAL_META = {
    "otytchol": ("auffangen", "ACTION"),
    "tshey": ("Spülung", "MEDIUM_PREPARATION"),
    "rsheal": ("Warmwasser", "MEDIUM_PREPARATION"),
    "skar": ("ausgießen", "ACTION"),
    "schoal": ("Sud", "MEDIUM_PREPARATION"),
    "sheey": ("Ablauf", "FLOW_FITTING"),
    "lar": ("Ablauf", "FLOW_FITTING"),
    "lo": ("Ablauf", "FLOW_FITTING"),
    "ls": ("Düse", "FLOW_FITTING"),
    "keol": ("Gabe", "QUANTITY_TIME"),
    "os": ("Gefäß", "VESSEL"),
    "teol": ("Hahn", "FLOW_FITTING"),
    "chckhal": ("Zeit", "QUANTITY_TIME"),
    "cheedar": ("Becken", "VESSEL"),
    "solkaiin": ("Tuch", "TOOL"),
    "raly": ("Arm", "FLOW_FITTING"),
    "oykchor": ("Topf", "VESSEL"),
    "qotedaiin": ("Wanne", "VESSEL"),
    "chary": ("abkühlen", "ACTION"),
    "ral": ("abkühlen", "ACTION"),
    "kchal": ("abseihen", "ACTION"),
    "sotodan": ("anwenden", "ACTION"),
    "oltchy": ("anwärmen", "ACTION"),
    "qotchol": ("anwärmen", "ACTION"),
    "kchol": ("auflegen", "ACTION"),
    "shecthedchy": ("aufstreichen", "ACTION"),
    "cfhy": ("auswringen", "ACTION"),
    "dsheol": ("einreiben", "ACTION"),
    "cheeety": ("Spülung", "ACTION"),
    "octheol": ("gleichen", "ACTION"),
    "cphy": ("nachseihen", "ACTION"),
    "qoctholy": ("pressen", "ACTION"),
    "choy": ("waschen", "ACTION"),
    "kchey": ("zerreiben", "ACTION"),
    "sheckhy": ("Überlauf", "FLOW_FITTING"),
    "qockhey": ("Überlauf", "FLOW_FITTING"),
    "ytey": ("füllen", "ACTION"),
    "rol": ("warm", "STATE"),
    "tshol": ("Kraut", "PLANT_MATERIAL"),
    "shoyty": ("Reserve", "REFERENCE_MATERIAL"),
    "sh": ("Stängel", "PLANT_MATERIAL"),
    "dchey": ("Wurzel", "PLANT_MATERIAL"),
    "etyd": ("Rest", "REFERENCE_MATERIAL"),
    "ches": ("teilen", "ACTION"),
    "kchy": ("Trank", "MEDIUM_PREPARATION"),
    "talam": ("verwahren", "ACTION"),
    "sheckhal": ("Maß", "QUANTITY_TIME"),
    "shecthy": ("warm", "STATE"),
    "chealror": ("klar", "STATE"),
    "qekey": ("roh", "STATE"),
    "lol": ("warm", "STATE"),
    "qolky": ("Stelle", "LOCATION"),
    "ly": ("Schale", "VESSEL"),
    "qolchey": ("Becken", "VESSEL"),
    "lcheey": ("Stelle", "LOCATION"),
}

SPECIAL_META = {
    "cheey|shey": ("Klarlauf", "PRODUCT_STATE"),
    "dl": ("Zusatz", "ADDITIVE"),
    "dain": ("Tuch", "TOOL"),
    "chety|chty": ("zerkleinern", "ACTION"),
    "dchol|schol": ("Voriges", "REFERENCE_MATERIAL"),
    "tchody": ("abkühlen", "PROGRAM_ACTION"),
    "sshkchdy": ("schwenken", "PROGRAM_ACTION"),
    "rshedy": ("waschen", "PROGRAM_ACTION"),
    "cheeckhody": ("auftragen", "PROGRAM_ACTION"),
    "ody": ("kühlen", "PROGRAM_ACTION"),
    "lkedy": ("nachwaschen", "PROGRAM_ACTION"),
    "dshedy": ("Frischwasser", "MEDIUM_PREPARATION"),
    "qokylddy": ("befestigen", "PROGRAM_ACTION"),
}

DRAWER_RULES = {
    "ACTION": "Gelernte lokale Handlung in den Operationsslot einsetzen.",
    "ADDITIVE": "Zusatz zum aktuell aktiven Ansatz ergänzen.",
    "FLOW_FITTING": "Lokales Anschluss- oder Ablaufteil aus dem Bildbesitzer wählen.",
    "LOCATION": "Vom Bild bezeichnete Arbeitsstelle einsetzen.",
    "MEDIUM_PREPARATION": "Gelernte Flüssigkeit oder Zubereitung einsetzen.",
    "PLANT_MATERIAL": "Vom Pflanzenbild gelieferten Teil benennen.",
    "PRODUCT_STATE": "Gelernte Produkt- oder Zustandskarte einsetzen.",
    "PROGRAM_ACTION": "Ganze Spezialkarte ausführen und die Zelle schließen.",
    "QUANTITY_TIME": "Gelernte Maß-, Gabe- oder Zeitkarte einsetzen.",
    "REFERENCE_MATERIAL": "Auf den bereits aktiven oder zurückgelegten Stoff verweisen.",
    "STATE": "Gelernte Zustandskarte auf den aktiven Posten beziehen.",
    "TOOL": "Lokales Werkzeug aus Bild oder Exemplar einsetzen.",
    "VESSEL": "Lokales Gefäß aus Bild oder Exemplar einsetzen.",
}

TEMPLATE_META = {
    "P00_PROGRAM_ONLY": ("Direktprogramm", "PROGRAM+CLOSE", "Die ganze Schlusskarte als vollständigen Arbeitsbefehl ausführen."),
    "P01_ARGUMENT": ("Argument vor Programm", "ITEM|SOURCE|MEDIUM|TARGET -> PROGRAM/HANDOFF", "Den sichtbaren oder geerbten Posten einsetzen; danach Programm oder Übergabe lesen."),
    "P02_ACTION": ("Handlungskette", "ACTION|ORDER -> PROGRAM/HANDOFF", "Handlungen in Kartenfolge ausführen; die Schlusskarte beendet nur die lokale Zelle."),
    "P03_GRADED_ACTION": ("Gestufte Handlung", "ACTION -> GRADE/STATE -> PROGRAM", "Handlung und kurzen/längeren/vollen Grad gemeinsam lesen."),
    "P04_MEASURE_ACTION": ("Bemessene Handlung", "QUANTITY -> ACTION -> PROGRAM", "Maß oder Portion auf die folgende Handlung beziehen."),
    "P05_TARGET_ACTION": ("Zielhandlung", "TARGET -> ACTION -> PROGRAM", "Die Handlung an der sichtbaren oder bezeichneten Stelle ausführen."),
    "P06_TRANSFER": ("Lokaler Übergang", "SOURCE/MEDIUM -> FLOW -> TARGET -> PROGRAM", "Nur den lokalen sichtbaren Lauf lesen; keinen globalen Kreislauf ergänzen."),
    "P07_MATERIAL_PROCESS": ("Materialvorgang", "ITEM/SOURCE/PREPARATION -> ACTION/STATE -> PROGRAM", "Bildbesitzer oder Vorposten einsetzen und die folgende Bearbeitung lesen."),
    "P08_FULL_REGISTER": ("Vollständige Werkstattphrase", "OWNER -> SOURCE/PREPARATION -> QUANTITY -> TARGET/ORDER -> ACTION -> STATE -> PROGRAM", "Nur belegte Slots in sichtbarer Kartenfolge lesen; fehlende Slots bleiben elliptisch."),
}


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


def clean_program_headword(reading: str) -> str:
    return reading.split(";")[0].strip()


def classify_template(statement_events: list[dict[str, str]]) -> str:
    open_events = [row for row in statement_events if row["step_closure_role"] != "COMMIT_CELL"]
    slots = {slot for row in open_events for slot in row["workshop_slots"].split("+") if slot}
    if not open_events:
        return "P00_PROGRAM_ONLY"
    if len(slots) >= 5:
        return "P08_FULL_REGISTER"
    if ({"PREPARATION", "SOURCE", "OWNER_ITEM"} & slots) and "OPERATION" in slots and len(slots) >= 3:
        return "P07_MATERIAL_PROCESS"
    if "FLOW_TRANSFER" in slots and "OPERATION" in slots:
        return "P06_TRANSFER"
    if "TARGET" in slots and "OPERATION" in slots:
        return "P05_TARGET_ACTION"
    if "QUANTITY" in slots and "OPERATION" in slots:
        return "P04_MEASURE_ACTION"
    if "STATE_GRADE" in slots and "OPERATION" in slots:
        return "P03_GRADED_ACTION"
    if "OPERATION" in slots or "FLOW_TRANSFER" in slots:
        return "P02_ACTION"
    return "P01_ARGUMENT"


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentences = read_tsv(SENTENCE_IN)
    core = read_tsv(CORE_IN)
    unified = read_tsv(UNIFIED_IN)
    if (len(dictionary), len(events), len(sentences), len(core), len(unified)) != (173, 381, 116, 16, 173):
        raise AssertionError("unexpected input dimensions")

    dmap = {row["joint_tuple_id"]: row for row in dictionary}
    umap = {row["joint_tuple_id"]: row for row in unified}
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_card[row["joint_tuple_id"]].append(row)
        by_statement[row["statement_id"]].append(row)

    word_statuses = {"LOCAL_EXEMPLAR_SINGLETON", "MEMORIZED_RECURRENT_CARD", "TERMINAL_SPECIALIST_WHOLE_CARD"}
    word_cards = [row for row in unified if row["architecture_status"] in word_statuses]
    if len(word_cards) != 68:
        raise AssertionError("expected 68 whole-word cards")

    word_rows: list[dict[str, str]] = []
    for item in word_cards:
        surface = item["surface_family"]
        status = item["architecture_status"]
        if status == "LOCAL_EXEMPLAR_SINGLETON":
            if surface not in LOCAL_META:
                raise AssertionError(f"unmapped local word: {surface}")
            headword, drawer = LOCAL_META[surface]
        else:
            if surface not in SPECIAL_META:
                raise AssertionError(f"unmapped specialist word: {surface}")
            headword, drawer = SPECIAL_META[surface]
        card_events = by_card[item["joint_tuple_id"]]
        original = item["concrete_reading_de"]
        word_rows.append({
            "joint_tuple_id": item["joint_tuple_id"],
            "surface_family": surface,
            "occurrence_count": str(len(card_events)),
            "records": "|".join(dict.fromkeys(row["record_unit_id"] for row in card_events)),
            "pages": "|".join(dict.fromkeys(row["page"] for row in card_events)),
            "event_ids": "|".join(row["event_id"] for row in card_events),
            "word_class": status,
            "lexical_drawer": drawer,
            "apprentice_headword_de": headword,
            "context_expansion_de": original,
            "context_was_removed": "YES" if headword.casefold() != clean_program_headword(original).casefold() else "NO",
            "semantic_segmentation": item["semantic_segmentation"],
            "learning_rule_de": DRAWER_RULES[drawer],
        })
    word_rows.sort(key=lambda row: (row["word_class"], row["lexical_drawer"], row["apprentice_headword_de"], row["joint_tuple_id"]))
    word_map = {row["joint_tuple_id"]: row for row in word_rows}

    local_rows = [dict(row) for row in word_rows if row["word_class"] == "LOCAL_EXEMPLAR_SINGLETON"]
    if len(local_rows) != 55:
        raise AssertionError("expected 55 local words")

    drawer_rows: list[dict[str, str]] = []
    for drawer in sorted(DRAWER_RULES):
        selected = [row for row in word_rows if row["lexical_drawer"] == drawer]
        drawer_rows.append({
            "lexical_drawer": drawer,
            "exact_card_types": str(len(selected)),
            "occurrences": str(sum(int(row["occurrence_count"]) for row in selected)),
            "distinct_headwords": str(len({row["apprentice_headword_de"].casefold() for row in selected})),
            "headwords_de": "|".join(dict.fromkeys(row["apprentice_headword_de"] for row in selected)),
            "surface_families": "|".join(row["surface_family"] for row in selected),
            "apprentice_rule_de": DRAWER_RULES[drawer],
        })

    core_rows: list[dict[str, str]] = []
    for item in core:
        word = word_map.get(item["joint_tuple_id"])
        headword = word["apprentice_headword_de"] if word else item["concrete_reading_de"]
        core_rows.append({
            "core_rank": item["core_rank"],
            "joint_tuple_id": item["joint_tuple_id"],
            "surface_family": item["surface_family"],
            "occurrence_count": item["occurrence_count"],
            "apprentice_headword_de": headword,
            "composition": item["semantic_segmentation"],
            "slots": item["dominant_slots"],
            "learning_mode": "WHOLE_WORD" if word else "PRODUCTIVE_RULE",
            "cumulative_events": item["cumulative_events"],
            "cumulative_middle_coverage": item["cumulative_middle_coverage"],
        })

    core_ids = {row["joint_tuple_id"] for row in core}
    phrase_rows: list[dict[str, str]] = []
    template_examples: dict[str, list[str]] = defaultdict(list)
    template_counts: Counter[str] = Counter()
    for sentence in sentences:
        statement_events = by_statement[sentence["statement_id"]]
        template = classify_template(statement_events)
        template_counts[template] += 1
        template_examples[template].append(sentence["statement_id"])
        open_events = [row for row in statement_events if row["step_closure_role"] != "COMMIT_CELL"]
        heads: list[str] = []
        tagged: list[str] = []
        expansions: list[str] = []
        local_count = 0
        productive_count = 0
        core_count = 0
        for event in statement_events:
            word = word_map.get(event["joint_tuple_id"])
            head = word["apprentice_headword_de"] if word else clean_program_headword(event["concrete_word_reading_de"])
            is_close = event["step_closure_role"] == "COMMIT_CELL"
            heads.append(head + (" [SCHLUSS]" if is_close else ""))
            if is_close:
                tagged.append(f"[PROGRAM] {head} [SCHLUSS]")
            else:
                tagged.append(f"[{event['workshop_slots']}] {head}")
            if word and word["context_was_removed"] == "YES":
                expansions.append(f"{head}→{word['context_expansion_de']}")
            if event["open_middle_status"] == "LOCAL_EXEMPLAR_SINGLETON":
                local_count += 1
            if event["open_middle_status"].startswith("PRODUCTIVE"):
                productive_count += 1
            if event["joint_tuple_id"] in core_ids and not is_close:
                core_count += 1
        if not open_events:
            coverage = "DIRECT_PROGRAM_ONLY"
        elif all(row["joint_tuple_id"] in core_ids for row in open_events):
            coverage = "CORE_16_ONLY"
        elif all(row["open_middle_status"].startswith("PRODUCTIVE") for row in open_events):
            coverage = "PRODUCTIVE_EXTENDED"
        elif local_count == 0:
            coverage = "RECURRENT_WORD_DECK_NEEDED"
        else:
            coverage = "LOCAL_GLOSSARY_NEEDED"
        phrase_rows.append({
            "statement_id": sentence["statement_id"],
            "record_unit_id": sentence["record_unit_id"],
            "page": sentence["page"],
            "loci": sentence["loci"],
            "event_count": sentence["event_count"],
            "template_id": template,
            "template_name_de": TEMPLATE_META[template][0],
            "coverage_class": coverage,
            "open_event_count": str(len(open_events)),
            "core16_open_events": str(core_count),
            "productive_open_events": str(productive_count),
            "local_word_events": str(local_count),
            "headword_sequence_de": " → ".join(heads),
            "slot_tagged_sequence_de": " | ".join(tagged),
            "context_expansions_de": " | ".join(expansions) if expansions else "NONE",
            "fluent_workshop_sentence_de": sentence["workshop_sentence_de"],
            "physical_line_note": sentence["physical_line_note"],
        })

    template_rows: list[dict[str, str]] = []
    for template, (name, formula, rule) in TEMPLATE_META.items():
        examples = template_examples[template]
        template_rows.append({
            "template_id": template,
            "template_name_de": name,
            "statement_count": str(template_counts[template]),
            "canonical_formula": formula,
            "apprentice_rule_de": rule,
            "example_statement_ids": "|".join(examples[:8]),
        })

    lines = [
        "# Lehrlingsphrasebook: elf vollständige Records",
        "",
        "Die erste Zeile jeder Anweisung ist die knappe Kartenlesung. Die zweite ist die bisherige flüssige Werkstattexpansion.",
        "",
    ]
    phrase_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in phrase_rows:
        phrase_by_record[row["record_unit_id"]].append(row)
    for record in RECORD_ORDER:
        selected = phrase_by_record[record]
        lines.extend([f"## {record} — {selected[0]['page']}", ""])
        for row in selected:
            lines.append(f"- **{row['statement_id']} · {row['template_name_de']} · {row['coverage_class']}**")
            lines.append(f"  - Karten: {row['headword_sequence_de']}")
            lines.append(f"  - Lesung: {row['fluent_workshop_sentence_de']}")
        lines.append("")
    RECORDS_OUT.write_text("\n".join(lines), encoding="utf-8")

    write_tsv(CORE_OUT, core_rows)
    write_tsv(WORDS_OUT, word_rows)
    write_tsv(LOCAL_OUT, local_rows)
    write_tsv(DRAWERS_OUT, drawer_rows)
    write_tsv(TEMPLATES_OUT, template_rows)
    write_tsv(PHRASES_OUT, phrase_rows)

    coverage_counts = Counter(row["coverage_class"] for row in phrase_rows)
    checks = {
        "cards_173": len(dictionary) == 173,
        "events_381": len(events) == 381,
        "sentences_116": len(sentences) == 116,
        "records_11": len(phrase_by_record) == 11,
        "core_16": len(core_rows) == 16,
        "whole_word_types_68": len(word_rows) == 68,
        "whole_word_events_75": sum(int(row["occurrence_count"]) for row in word_rows) == 75,
        "local_types_55": len(local_rows) == 55,
        "local_events_55": sum(int(row["occurrence_count"]) for row in local_rows) == 55,
        "local_distinct_headwords_45": len({row["apprentice_headword_de"].casefold() for row in local_rows}) == 45,
        "drawers_13": len(drawer_rows) == 13,
        "templates_9": len(template_rows) == 9,
        "template_counts_exact": template_counts == Counter({
            "P00_PROGRAM_ONLY": 40,
            "P01_ARGUMENT": 9,
            "P02_ACTION": 8,
            "P03_GRADED_ACTION": 1,
            "P04_MEASURE_ACTION": 1,
            "P05_TARGET_ACTION": 2,
            "P06_TRANSFER": 2,
            "P07_MATERIAL_PROCESS": 26,
            "P08_FULL_REGISTER": 27,
        }),
        "coverage_counts_exact": coverage_counts == Counter({
            "DIRECT_PROGRAM_ONLY": 40,
            "CORE_16_ONLY": 13,
            "PRODUCTIVE_EXTENDED": 19,
            "RECURRENT_WORD_DECK_NEEDED": 2,
            "LOCAL_GLOSSARY_NEEDED": 42,
        }),
        "statements_without_local_74": sum(row["local_word_events"] == "0" for row in phrase_rows) == 74,
        "every_event_once": sum(int(row["event_count"]) for row in phrase_rows) == 381,
        "every_headword_nonempty": all(row["apprentice_headword_de"] for row in word_rows),
        "fixed_pages_only": {row["page"] for row in events} == ALLOWED_PAGES,
        "sealed_absent": not any(row["page"].startswith("f84") for row in events),
        "records_markdown_complete": all(f"## {record} —" in RECORDS_OUT.read_text(encoding="utf-8") for record in RECORD_ORDER),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "whole_word_types": len(word_rows),
            "whole_word_occurrences": sum(int(row["occurrence_count"]) for row in word_rows),
            "local_exact_types": len(local_rows),
            "local_distinct_headwords": len({row["apprentice_headword_de"].casefold() for row in local_rows}),
            "drawers": len(drawer_rows),
            "templates": len(template_rows),
            "template_counts": dict(sorted(template_counts.items())),
            "coverage_counts": dict(sorted(coverage_counts.items())),
        },
        "working_rule": "READ CORE RULES FIRST; OPEN A WHOLE-WORD DRAWER ONLY WHEN NEEDED; LET IMAGE/CONTEXT SUPPLY REMOVED DETAIL",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_paths = [CORE_OUT, WORDS_OUT, LOCAL_OUT, DRAWERS_OUT, TEMPLATES_OUT, PHRASES_OUT, RECORDS_OUT, CHECK_OUT]
    summary = {
        **result,
        "input_hashes": {path.name: sha256(path) for path in (DICT_IN, EVENT_IN, SENTENCE_IN, CORE_IN, UNIFIED_IN)},
        "output_hashes": {path.name: sha256(path) for path in output_paths},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
