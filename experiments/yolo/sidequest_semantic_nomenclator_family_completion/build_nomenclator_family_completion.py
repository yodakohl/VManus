#!/usr/bin/env python3
"""Compress the remaining local whole-card tail into workshop families."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
PREVIOUS = PARENT / "sidequest_semantic_singleton_composition_rescue"
OPEN = PARENT / "sidequest_semantic_open_middle_lexicon"

WORDS68_IN = PREVIOUS / "APPRENTICE_68_RECOMPOSED_WORD_DECK.tsv"
PHRASES_IN = PREVIOUS / "APPRENTICE_116_RECOMPOSED_PHRASES.tsv"
DICT173_IN = OPEN / "SELECTED_173_OPEN_MIDDLE_DICTIONARY.tsv"
EVENTS381_IN = OPEN / "SELECTED_381_OPEN_MIDDLE_INTERLINEAR.tsv"

TAIL_OUT = HERE / "REMAINING_27_FAMILY_DISPOSITION.tsv"
PARADIGMS_OUT = HERE / "KCH_TY_PARADIGMS.tsv"
FAMILIES_OUT = HERE / "COMPACT_FAMILY_DECKS.tsv"
DICT_OUT = HERE / "COMPACT_173_CARD_DICTIONARY.tsv"
EVENTS_OUT = HERE / "COMPACT_381_EVENT_INTERLINEAR.tsv"
PHRASES_OUT = HERE / "COMPACT_116_PHRASES.tsv"
RECORDS_OUT = HERE / "COMPACT_11_RECORDS.md"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


# surface -> disposition, family, parse, selected reading, confidence, reason
TAIL_DECISIONS = {
    "ral": ("PARTIAL_RECOMPOSITION", "TARGET_WORKFLOW", "R_LOCAL+AL_TO", "zur Zielstelle", "MEDIUM", "AL supplies the target and the final open card hands that target to the following transfer statement."),
    "kchal": ("PRODUCTIVE_RECOMPOSITION", "KCH_PROCESS", "KCH_PROCESS+AL_TO", "an der Zielstelle bearbeiten", "HIGH", "KCH plus target completes the four-member KCH operation grid."),
    "sotodan": ("PARTIAL_RECOMPOSITION", "ORDERED_APPLICATION", "OT_FOLLOW+DAN_APPLY", "danach anwenden", "MEDIUM", "OT supplies order while DAN remains the learned application core."),
    "kchol": ("PRODUCTIVE_RECOMPOSITION", "KCH_PROCESS", "KCH_PROCESS+OL_CONTINUE", "weiter bearbeiten", "HIGH", "KCH processing plus OL continuation predicts the operation between ingredient and following batch."),
    "skar": ("PARTIAL_RECOMPOSITION", "SOURCE_WORKFLOW", "SK_POUR+AR_FROM", "von dort ausgiessen", "MEDIUM", "AR supplies the source while SK remains a local pouring core."),
    "cfhy": ("WHOLE_RETAIN", "SEPARATION_SPECIALIST", "MEMORIZED_WHOLE_CARD", "auswringen", "LOCAL", "The first separator remains a learned specialist command paired with CPHY."),
    "dsheol": ("PRODUCTIVE_RECOMPOSITION", "REST_CONTINUATION", "SH_REST+E_SHORT+OL_CONTINUE", "kurz weiter ruhen lassen", "HIGH", "The selected rest family, short grade and continuation form a complete process state."),
    "ytey": ("WHOLE_RETAIN", "SPECIAL_ACTION", "MEMORIZED_WHOLE_CARD", "fuellen", "LOCAL", "No licensed component split predicts filling without making Y or TY drift."),
    "cphy": ("WHOLE_RETAIN", "SEPARATION_SPECIALIST", "MEMORIZED_WHOLE_CARD", "nachseihen", "LOCAL", "The second separator remains a learned specialist command paired with CFHY."),
    "ches": ("WHOLE_RETAIN", "SPECIAL_ACTION", "MEMORIZED_WHOLE_CARD", "teilen", "LOCAL", "Division remains a short learned command; it supports the part workflow without defining a new letter root."),
    "talam": ("PARTIAL_RECOMPOSITION", "TARGET_STORAGE", "AL_TO+TAM_STORE", "am Ziel verwahren", "MEDIUM", "AL supplies the target while TAM remains the learned storage core."),
    "kchey": ("PRODUCTIVE_RECOMPOSITION", "KCH_PROCESS", "KCH_PROCESS+E_SHORT+Y_CURRENT", "diesen Posten kurz bearbeiten", "HIGH", "KCH plus short grade and current item predicts a brief processing instruction."),
    "lo": ("PARTIAL_RECOMPOSITION", "OUTFLOW_WORKFLOW", "L_OUT+O_LOCAL", "abfuehren", "MEDIUM", "L contributes outward movement; the small local carrier is not generalized."),
    "ls": ("PARTIAL_RECOMPOSITION", "OUTFLOW_WORKFLOW", "L_OUT+S_PORT", "Auslass", "MEDIUM", "L contributes outward direction and S remains a learned port selector; DUESE was too specific."),
    "qolky": ("PARTIAL_RECOMPOSITION", "CONTINUATION_WORKFLOW", "OL_CONTINUE+KY_LOCAL", "weiterfuehren", "MEDIUM", "OL supplies continuation and the local KY carrier no longer has to mean STATION."),
    "tshey": ("PARTIAL_RECOMPOSITION", "CLEAR_FLOW_WORKFLOW", "T_LOCAL+SHEY_CLEAR_FLOW", "Klarlauf", "MEDIUM", "The learned SHEY clear-flow card survives under a local T carrier; SPUELWASSER was unnecessarily specific."),
    "kchy": ("PRODUCTIVE_RECOMPOSITION", "KCH_PROCESS", "KCH_PROCESS+Y_CURRENT", "diesen Posten bearbeiten", "HIGH", "The ungraded KCH member applies processing to the current item."),
    "tshol": ("PARTIAL_RECOMPOSITION", "INGREDIENT_WORKFLOW", "T_LOCAL+HO_INGREDIENT+L_OUT", "Zutat entnehmen", "MEDIUM", "HO supplies ingredient and L outward selection; T remains local."),
    "sh": ("WHOLE_RETAIN", "PLANT_PART_SPECIALIST", "MEMORIZED_WHOLE_CARD", "Staengel", "LOCAL", "The pictured-plant part remains a learned card."),
    "dchey": ("WHOLE_RETAIN", "PLANT_PART_SPECIALIST", "MEMORIZED_WHOLE_CARD", "Wurzel", "LOCAL", "The pictured-plant part remains a learned card rather than a forced D plus Y split."),
    "shoyty": ("PRODUCTIVE_RECOMPOSITION", "TY_PART", "HO_INGREDIENT+Y_CURRENT+TY_PART", "Zutatenteil", "HIGH", "The ingredient/current-item frame selects the newly coherent TY part unit."),
    "etyd": ("PRODUCTIVE_RECOMPOSITION", "TY_PART", "E_SHORT+TY_PART+D_LOCAL", "kleiner Restteil", "HIGH", "The short-grade TY unit at record end naturally preserves a small remainder."),
    "chealror": ("PARTIAL_RECOMPOSITION", "BATCH_DIRECTION", "AL_TO+R_LOCAL+OR_BATCH", "Ansatz von dort zur Zielstelle", "MEDIUM", "AL and OR are visible; the internal R carrier marks the local source transition but is not promoted globally."),
    "qekey": ("WHOLE_RETAIN", "SPECIAL_STATE", "MEMORIZED_WHOLE_CARD", "roh", "LOCAL", "The raw-state card remains learned; a KCH or E split would duplicate stronger cards."),
    "os": ("SHARED_WHOLE_HEADWORD", "VESSEL_NOMENCLATOR", "MEMORIZED_VESSEL_CARD", "Gefaess", "LOCAL", "General work vessel."),
    "ly": ("SHARED_WHOLE_HEADWORD", "VESSEL_NOMENCLATOR", "MEMORIZED_VESSEL_CARD", "Gefaess", "LOCAL", "The image selects the receiving shape; the card need not lexicalize SCHALE."),
    "oykchor": ("SHARED_WHOLE_HEADWORD", "VESSEL_NOMENCLATOR", "MEMORIZED_VESSEL_CARD", "Gefaess", "LOCAL", "The image selects the preparation vessel; the card need not lexicalize TOPF."),
}


# Revisions outside the 27-card tail which make the TY paradigm coherent.
SPECIAL_REVISIONS = {
    "chety|chty": ("PRODUCTIVE_COMPOSITION", "TY_PART", "CH_PARTITION+TY_PART", "Teil abtrennen", "HIGH", "Two occurrences turn the TY unit into an operation: form or remove a part."),
    "cheeety": ("PARTIAL_COMPOSITION", "TY_PART", "EEE_FULL+TY_PART", "ganzen Teilposten", "MEDIUM", "The full grade selects the complete TY part; the outer carrier remains local."),
    "otytchol": ("PARTIAL_COMPOSITION", "TY_PART", "OT_FOLLOW+TY_PART+OL_CONTINUE", "naechsten Teilposten weiterfuehren", "MEDIUM", "OT and OL order a following TY part while the carrier remains local."),
}


FAMILY_ROWS = [
    ("KCH_PROCESS", "4", "4", "KCH", "bearbeiten", "KCH+Y item; KCH+E+Y short item; KCH+AL target; KCH+OL continuation", "No material, tool or temperature is encoded in KCH itself."),
    ("TY_PART", "5", "6", "TY", "Teilposten oder Restanteil", "CH+TY separate; HO+Y+TY ingredient part; E+TY+D remainder; EEE+TY whole part; OT+TY+OL next part", "TY is bounded to this five-card grid, not every visible t or y."),
    ("WORKFLOW_PARTIALS", "10", "10", "known component plus local carrier", "target source order outflow continuation clear-flow ingredient batch", "RAL SOTODAN SKAR TALAM LO LS QOLKY TSHEY TSHOL CHEALROR", "The local carrier remains learned; only the known component is portable."),
    ("VESSEL_NOMENCLATOR", "3", "3", "three exact whole cards", "Gefaess", "OS general; LY receiver; OYKCHOR preparation vessel", "The image selects the subtype; the word deck keeps one shared headword."),
    ("SEPARATION_SPECIALISTS", "2", "2", "CFHY and CPHY", "auswringen; nachseihen", "first forceful separation then second fine separation", "They remain two learned whole commands, not invented F and P morphemes."),
    ("PLANT_PART_SPECIALISTS", "2", "2", "SH and DCHEY", "Staengel; Wurzel", "pictured owner supplies the article", "Exact cards remain learned and page-owned."),
    ("SPECIAL_ACTION_STATE", "3", "3", "YTEY CHES QEKEY", "fuellen; teilen; roh", "small terminal-independent specialist deck", "No forced internal parsing."),
]


SENTENCE_REVISIONS = {
    "H1-S001": "Nimm die Wurzel, bereite den Ansatz, trenne daraus einen Teil ab, gib ihn in das Gefaess, gib den Wasserzulauf zu, fuehre den naechsten Teilposten weiter, setze ihn nach Sollmass an und behalte einen kleinen Restteil.",
    "H2-S003": "Gib den weitergefuehrten Folgeansatz in das Gefaess, bearbeite diesen Posten bis zur Weichstufe und stelle das Zutatenmass ein.",
    "H3-S001": "Entnimm eine Zutat, gib sie dorthin, wringe aus, lass bis zum Standmass stehen, seih nach, nimm den Klarlauf und stelle ihn kalt.",
    "H3-S002": "Lege einen Zutatenteil zurueck.",
    "H3-S003": "Nimm den Vorposten, bearbeite diesen Posten und stelle sein Sollmass ein.",
    "H4-S002": "Setze den Posten nach Sollmass um und verwahre ihn am Ziel.",
    "H5-S001": "Bereite einen Zutatenansatz, gib die Zutat dorthin nach Sollmass, bearbeite die naechste Zutat weiter, beginne den Folgeansatz und setze den Posten dort an.",
    "H5-S003": "Nimm den Staengel als Zutat, bearbeite diesen Posten kurz und setze ihn erneut an.",
    "H5-S004": "Setze den Posten an, gib den Auszug zu und bearbeite ihn an der Zielstelle.",
    "H5-S005": "Setze den Ansatz als Zutat an, nimm den Auszug daraus und wende ihn danach an.",
    "B1-S006": "Gib eine Portion und den Zusatz zu, leite durch, fuehre zur Zielstelle und uebergib an den folgenden Umsetzschritt.",
    "B1-S014": "Setze um, fuehre weiter, leite am Auslass ab und fuehre danach von dort weiter.",
    "B1-S018": "Stelle das Gefaess bereit, lass den Posten kurz weiter ruhen, bringe ihn auf Sollstufe, sammle laenger und schliesse.",
    "B2-S010": "Setze laenger an, fuehre den Posten durch den Auslass und nimm den Klarlauf.",
    "B2-S015": "Halte den vorigen Ablauf geschlossen, gib den Klarlauf zu, setze laenger an und schliesse.",
    "B3-S016": "Fuehre ab, setze den Posten um und schliesse.",
    "B3-S026": "Setze von dort um, warte bis zum Absetzmass, setze erneut um, gib eine Portion zu, halte bereit, fuehre den Ansatz von dort zur Zielstelle, sammle laenger und schliesse.",
    "B3-S029": "Fuehre weiter, nimm den ganzen Teilposten, setze kurz an und schliesse.",
    "B3-S034": "Bringe auf Sollstufe, halte bereit, trenne einen Teil ab, stelle das Folgemass ein, fuehre zur unteren Zielstelle, lass absetzen und schliesse.",
    "B4-S016": "Gib eine weitere Portion dorthin, giesse sie von dort aus, lass absetzen und schliesse.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def architecture_from_source(value: str) -> str:
    if value == "PRODUCTIVE_COMPONENT_OR_COMPOSITION":
        return "PRODUCTIVE_COMPOSITION"
    if value == "LICENSED_PARTIAL_COMPOSITION":
        return "PARTIAL_COMPOSITION"
    return "MEMORIZED_WHOLE_CARD"


def head(reading: str) -> str:
    return reading.split(";")[0].strip()


def build() -> dict[str, object]:
    words68 = read_tsv(WORDS68_IN)
    prior_phrases = read_tsv(PHRASES_IN)
    dictionary = read_tsv(DICT173_IN)
    events = read_tsv(EVENTS381_IN)
    assert (len(words68), len(prior_phrases), len(dictionary), len(events)) == (68, 116, 173, 381)
    assert {row["page"] for row in events} <= ALLOWED_PAGES

    prior_word_map = {row["joint_tuple_id"]: row for row in words68}
    dictionary_by_surface = {row["surface_family"]: row for row in dictionary}
    tail_surfaces = {
        row["surface_family"] for row in words68
        if row["singleton_composition_status"] == "WHOLE_RETAIN"
    }
    assert tail_surfaces == set(TAIL_DECISIONS) and len(tail_surfaces) == 27

    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_card[event["joint_tuple_id"]].append(event)
        events_by_statement[event["statement_id"]].append(event)

    tail_rows: list[dict[str, str]] = []
    for surface in sorted(TAIL_DECISIONS):
        disposition, family, parse, reading, confidence, reason = TAIL_DECISIONS[surface]
        card = dictionary_by_surface[surface]
        occurrence = events_by_card[card["joint_tuple_id"]][0]
        tail_rows.append({
            "joint_tuple_id": card["joint_tuple_id"],
            "surface_family": surface,
            "event_id": occurrence["event_id"],
            "statement_id": occurrence["statement_id"],
            "page": occurrence["page"],
            "previous_reading_de": prior_word_map[card["joint_tuple_id"]]["recomposed_reading_de"],
            "family_disposition": disposition,
            "family_id": family,
            "selected_parse": parse,
            "compact_reading_de": reading,
            "confidence": confidence,
            "reason_en": reason,
        })
    tail_by_card = {row["joint_tuple_id"]: row for row in tail_rows}

    special_by_card: dict[str, tuple[str, str, str, str, str, str]] = {}
    for surface, meta in SPECIAL_REVISIONS.items():
        special_by_card[dictionary_by_surface[surface]["joint_tuple_id"]] = meta

    compact_dictionary: list[dict[str, str]] = []
    for card in dictionary:
        status = architecture_from_source(card["unified_lexicon_architecture"])
        parse = card["semantic_segmentation"]
        reading = card["concrete_word_reading_de"]
        family = "INHERITED_SELECTED_CARD"
        source = "OPEN_MIDDLE_SELECTED"

        prior_word = prior_word_map.get(card["joint_tuple_id"])
        if prior_word:
            reading = prior_word["recomposed_reading_de"]
            parse = prior_word["singleton_selected_composition"] if prior_word["singleton_selected_composition"] != "UNCHANGED" else prior_word["semantic_segmentation"]
            prior_status = prior_word["singleton_composition_status"]
            if prior_status == "PRODUCTIVE_RESCUE":
                status = "PRODUCTIVE_COMPOSITION"
            elif prior_status == "PARTIAL_RESCUE":
                status = "PARTIAL_COMPOSITION"
            else:
                status = "MEMORIZED_WHOLE_CARD"
            family = prior_word["shared_headword_family"] if prior_word["shared_headword_family"] != "NONE" else "PREVIOUS_WORD_DECK"
            source = "RECOMPOSED_68_WORD_DECK"

        if card["joint_tuple_id"] in tail_by_card:
            decision = tail_by_card[card["joint_tuple_id"]]
            reading = decision["compact_reading_de"]
            parse = decision["selected_parse"]
            family = decision["family_id"]
            status = (
                "PRODUCTIVE_COMPOSITION" if decision["family_disposition"] == "PRODUCTIVE_RECOMPOSITION"
                else "PARTIAL_COMPOSITION" if decision["family_disposition"] == "PARTIAL_RECOMPOSITION"
                else "MEMORIZED_WHOLE_CARD"
            )
            source = "REMAINING_27_FAMILY_PASS"

        if card["joint_tuple_id"] in special_by_card:
            status, family, parse, reading, _confidence, _reason = special_by_card[card["joint_tuple_id"]]
            source = "KCH_TY_SPECIAL_REVISION"

        compact_dictionary.append({
            **card,
            "pre_compact_segmentation": card["semantic_segmentation"],
            "pre_compact_reading_de": card["concrete_word_reading_de"],
            "compact_architecture": status,
            "compact_family": family,
            "compact_parse": parse,
            "compact_reading_de": reading,
            "compact_source": source,
        })
    compact_card_map = {row["joint_tuple_id"]: row for row in compact_dictionary}

    compact_events: list[dict[str, str]] = []
    for event in events:
        card = compact_card_map[event["joint_tuple_id"]]
        compact_events.append({
            **event,
            "pre_compact_reading_de": event["concrete_word_reading_de"],
            "compact_architecture": card["compact_architecture"],
            "compact_family": card["compact_family"],
            "compact_parse": card["compact_parse"],
            "compact_card_reading_de": card["compact_reading_de"],
            "compact_contextual_event_de": card["compact_reading_de"],
        })

    phrase_rows: list[dict[str, str]] = []
    for prior in prior_phrases:
        statement_events = events_by_statement[prior["statement_id"]]
        heads: list[str] = []
        tagged: list[str] = []
        changed_cards: list[str] = []
        for event in statement_events:
            card = compact_card_map[event["joint_tuple_id"]]
            reading = head(card["compact_reading_de"])
            close = event["step_closure_role"] == "COMMIT_CELL"
            heads.append(reading + (" [SCHLUSS]" if close else ""))
            tagged.append(f"[PROGRAM] {reading} [SCHLUSS]" if close else f"[{event['workshop_slots']}] {reading}")
            if reading != head(event["concrete_word_reading_de"]):
                changed_cards.append(event["joint_tuple_id"])
        fluent = SENTENCE_REVISIONS.get(prior["statement_id"], prior["recomposed_fluent_sentence_de"])
        phrase_rows.append({
            **prior,
            "pre_compact_headwords_de": prior["recomposed_headword_sequence_de"],
            "compact_headword_sequence_de": " -> ".join(heads),
            "compact_slot_sequence_de": " | ".join(tagged),
            "compact_changed_cards": "|".join(dict.fromkeys(changed_cards)) if changed_cards else "NONE",
            "compact_changed_card_count": str(len(dict.fromkeys(changed_cards))),
            "pre_compact_fluent_de": prior["recomposed_fluent_sentence_de"],
            "compact_fluent_sentence_de": fluent,
            "compact_statement_revised": "YES" if prior["statement_id"] in SENTENCE_REVISIONS else "NO",
        })

    paradigm_surfaces = ["kchy", "kchey", "kchal", "kchol", "chety|chty", "shoyty", "etyd", "cheeety", "otytchol"]
    paradigm_rows: list[dict[str, str]] = []
    for surface in paradigm_surfaces:
        card = dictionary_by_surface[surface]
        final = compact_card_map[card["joint_tuple_id"]]
        paradigm_rows.append({
            "paradigm": "KCH_PROCESS" if surface.startswith("kch") else "TY_PART",
            "joint_tuple_id": card["joint_tuple_id"],
            "surface_family": surface,
            "occurrences": card["occurrences"],
            "event_ids": "|".join(event["event_id"] for event in events_by_card[card["joint_tuple_id"]]),
            "compact_parse": final["compact_parse"],
            "compact_reading_de": final["compact_reading_de"],
            "prediction_role": (
                "argument or modifier selects one KCH processing instruction"
                if surface.startswith("kch")
                else "wrapper or modifier selects one TY part-unit instruction"
            ),
        })

    family_rows = [{
        "family_id": family,
        "exact_card_types": types,
        "occurrences": occurrences,
        "shared_form": shared_form,
        "shared_value_de": value,
        "members_or_rule": members,
        "important_limit": limit,
    } for family, types, occurrences, shared_form, value, members, limit in FAMILY_ROWS]

    lines = [
        "# Kompakte Elf-Record-Ausgabe nach Abschluss der Ganzwortfamilien",
        "",
        "Die Lesung benutzt KCH als Bearbeitungskern, TY als Teilposten und einen kleinen gelernten Gefaess-/Spezialwortsatz.",
        "",
    ]
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in phrase_rows:
        by_record[row["record_unit_id"]].append(row)
    for record in RECORD_ORDER:
        selected = by_record[record]
        lines.extend([f"## {record} - {selected[0]['page']}", ""])
        for row in selected:
            marker = " - NEU" if row["compact_statement_revised"] == "YES" else ""
            lines.append(f"- **{row['statement_id']}{marker}**")
            lines.append(f"  - Karten: {row['compact_headword_sequence_de']}")
            lines.append(f"  - Lesung: {row['compact_fluent_sentence_de']}")
        lines.append("")

    write_tsv(TAIL_OUT, tail_rows)
    write_tsv(PARADIGMS_OUT, paradigm_rows)
    write_tsv(FAMILIES_OUT, family_rows)
    write_tsv(DICT_OUT, compact_dictionary)
    write_tsv(EVENTS_OUT, compact_events)
    write_tsv(PHRASES_OUT, phrase_rows)
    RECORDS_OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    card_arch = Counter(row["compact_architecture"] for row in compact_dictionary)
    event_arch = Counter(row["compact_architecture"] for row in compact_events)
    open_event_arch = Counter(
        row["compact_architecture"] for row in compact_events
        if row["step_closure_role"] != "COMMIT_CELL"
    )
    tail_status = Counter(row["family_disposition"] for row in tail_rows)
    summary = {
        "status": "PASS",
        "tail_dispositions": dict(tail_status),
        "card_architecture": dict(card_arch),
        "event_architecture": dict(event_arch),
        "open_event_architecture": dict(open_event_arch),
        "dictionary_rows": len(compact_dictionary),
        "event_rows": len(compact_events),
        "phrase_rows": len(phrase_rows),
        "records": len(by_record),
        "revised_statements": sum(row["compact_statement_revised"] == "YES" for row in phrase_rows),
        "files": {},
    }
    for path in [TAIL_OUT, PARADIGMS_OUT, FAMILIES_OUT, DICT_OUT, EVENTS_OUT, PHRASES_OUT, RECORDS_OUT]:
        summary["files"][path.name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
