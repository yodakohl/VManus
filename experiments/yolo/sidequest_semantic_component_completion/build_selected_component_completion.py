#!/usr/bin/env python3
"""Build the selected creative component-completion edition.

The input is the already selected 173-card / 381-event paradigm closure.  This
builder applies only the bounded Y/CHY, P+CHED, repeated-OK, SH-rest,
CHK-warmth, and OLK~SOLK-station decisions audited in this directory.  It does
not read manuscript images, transcription sources, or sealed pages.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_paradigm_closure"

DICT_IN = SOURCE / "SELECTED_173_STEM_CONSISTENT_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_STEM_CONSISTENT_INTERLINEAR.tsv"
COMPONENT_IN = SOURCE / "SELECTED_COMPONENT_LEXICON.tsv"
UNRESOLVED_IN = SOURCE / "UNRESOLVED_COMPONENTS.tsv"

DICT_OUT = HERE / "SELECTED_173_COMPONENT_COMPLETE_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_COMPONENT_COMPLETE_INTERLINEAR.tsv"
STATEMENT_OUT = HERE / "SELECTED_116_COMPONENT_COMPLETE_STATEMENTS.tsv"
COMPONENT_OUT = HERE / "SELECTED_COMPONENT_LEXICON_V2.tsv"
UNRESOLVED_OUT = HERE / "REMAINING_UNRESOLVED.tsv"
SUMMARY_OUT = HERE / "SELECTED_BUILD_SUMMARY.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uniq(values: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(value for value in values if value))


def sentence_case(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def override(
    parse: str,
    nucleus: str,
    gloss: str,
    source: str,
    strength: str,
    note: str,
) -> dict[str, str]:
    return {
        "semantic_segmentation": parse,
        "stable_concrete_nucleus_de": nucleus,
        "concrete_word_reading_de": gloss,
        "reading_type": "SELECTED_COMPONENT_COMPLETION__" + source,
        "source": source,
        "strength": strength,
        "note": note,
    }


OVERRIDES = {
    # Y/CHY: a current referent, not an openness morpheme.
    "b921a237be883a820352": override(
        "Y_REFERENT_CARD",
        "Y=aktuell gemeinter Arbeitsposten; dies/es",
        "der laufende Posten; dies oder es",
        "Y_CHY",
        "SELECTED_PRODUCTIVE",
        "Visible chey|chy|dy|shy|sy|y are renderings of one exact card; the local owner supplies the noun.",
    ),
    "276a7c2d74d1143446f4": override(
        "OK+Y_REFERENT",
        "OK=in Arbeit setzen; Y=laufender Posten",
        "den laufenden Posten anwenden oder in Arbeit nehmen",
        "Y_CHY",
        "SELECTED_PRODUCTIVE",
        "Exact OKY card; kept distinct from the exact OKCHY card.",
    ),
    "9ad66e67803a12e745de": override(
        "OK+CHY[wrapped Y_REFERENT]",
        "OK=in Arbeit setzen; CHY=umhüllter Verweis auf den laufenden Posten",
        "den laufenden Posten anwenden oder in Arbeit nehmen",
        "Y_CHY",
        "SELECTED_PRODUCTIVE",
        "CHY carries the same referential contribution in this licensed family.",
    ),
    "08bd5ca0c2ad137a056d": override(
        "OK+E_GRADE_1+Y_REFERENT",
        "OK=in Arbeit setzen; E=kurzer Kontakt; Y=laufender Posten",
        "den laufenden Posten kurz anlegen oder benetzen",
        "Y_CHY",
        "SELECTED_PRODUCTIVE",
        "Y names the current referent; nonclosure follows from the absent terminal construction.",
    ),
    "0275fbf14e07935b0a45": override(
        "OK+E_GRADE_2+Y_REFERENT",
        "OK=in Arbeit setzen; EE=anhaltender Kontakt; Y=laufender Posten",
        "den laufenden Posten anhaltend in Kontakt halten",
        "Y_CHY",
        "SELECTED_PRODUCTIVE",
        "Y names the current referent; it does not itself mean open.",
    ),
    "5d5e0b288cf36864ed9d": override(
        "OT+E_GRADE_2+Y_REFERENT",
        "OT=danach; EE=anhaltender Kontakt; Y=laufender Posten",
        "den laufenden Posten danach anhaltend einwirken lassen",
        "Y_CHY",
        "SELECTED_CONTEXT_BOUND",
        "A two-event OT+EE+Y extension of the contact grid.",
    ),
    "6f7ff8287eddf4da9fdb": override(
        "CHD~CHED+Y_REFERENT",
        "CHD~CHED=umsetzen; Y=laufender Posten",
        "den laufenden Posten umsetzen oder durcharbeiten",
        "Y_CHY",
        "SELECTED_PRODUCTIVE",
        "All eleven events are nonterminal; visible final y is a referent, not a close.",
    ),
    "5e8441397e7c0faf042b": override(
        "CHED+CHY[wrapped Y_REFERENT]",
        "CHED=umsetzen oder zuführen; CHY=laufender Posten",
        "den laufenden Posten zuführen oder umsetzen",
        "Y_CHY",
        "SELECTED_CONTEXT_BOUND",
        "Singleton but compositionally licensed by the CHED and Y families.",
    ),
    "4a7a6326ac95a8809302": override(
        "OK+AL+Y_REFERENT",
        "OK=in Arbeit setzen; AL=Zielstelle; Y=laufender Posten",
        "den laufenden Posten an der Zielstelle einsetzen",
        "Y_CHY",
        "SELECTED_PARTIAL_COMPOSITION",
        "The components are stable; exact argument order is represented by this one card.",
    ),
    "1322bc176443fc2a8a86": override(
        "OK+OK+CHY[wrapped Y_REFERENT]",
        "OK+OK=erneuter Arbeitsaufruf; CHY=laufender Posten",
        "den laufenden Posten erneut in Arbeit nehmen",
        "Y_CHY",
        "SELECTED_PARTIAL_COMPOSITION",
        "Repeat, not intensity, is selected for this single doubled-OK card.",
    ),
    "eb2e4bc143f623ee03ac": override(
        "OK+Y_REFERENT+LDDY?",
        "OK=in Arbeit setzen; Y=laufender Posten; LDDY=opaker Schlussrest",
        "den laufenden Posten anwenden; den Schritt schließen",
        "Y_CHY",
        "SELECTED_PARTIAL_COMPOSITION",
        "Y is readable internally; LDDY remains a learned remainder.",
    ),
    "0ab57b7166de99db3a55": override(
        "LCH+Y_REFERENT",
        "LCH=abziehen; Y=laufender Posten",
        "den flüssigen Anteil des laufenden Postens abziehen",
        "Y_CHY",
        "SELECTED_THIN",
        "One licensed local frame; the fluid interpretation comes from the surrounding process.",
    ),
    # P+CHED: bounded destination/receiver contrast against L+CHED.
    "65df3cd9e59060042d47": override(
        "P+CHED+DY_TERMINAL",
        "P+CHED=in oder zum Empfänger führen; DY=Schlusskonstruktion",
        "in den Empfänger einführen; Schluss",
        "TRANSFER_ORDER",
        "SELECTED_CONTEXT_BOUND",
        "One terminal event at the lower-pool edge; no arrow direction is claimed.",
    ),
    "ba540da978ea132f6da5": override(
        "P+CHED+AL",
        "P+CHED=in oder zum Empfänger führen; AL=Stelle",
        "Einfüllstelle",
        "TRANSFER_ORDER",
        "SELECTED_CONTEXT_BOUND",
        "One event at the basket-like receiver station.",
    ),
    # Learned graded whole-card families.  These are not global letter roots.
    "bc4f1f5c006c74a4d26d": override(
        "SH_REST_FAMILY+E_GRADE_1+DY_TERMINAL",
        "gelernte Ruhefamilie; kurzer oder gewöhnlicher Grad; Schluss",
        "kurz oder gewöhnlich ruhen lassen; Schluss",
        "HOLD_CORES",
        "SELECTED_GRADED_WHOLE_CARD",
        "All twelve events are field- and statement-final; ch/sh/t vary inside one exact card.",
    ),
    "03626ca94cb17800d767": override(
        "SH_REST_FAMILY+E_GRADE_2+DY_TERMINAL",
        "gelernte Ruhefamilie; längerer Grad; Schluss",
        "länger ruhen oder nachwirken lassen; Schluss",
        "HOLD_CORES",
        "SELECTED_SINGLETON_GRADE",
        "A one-event extension of the selected rest family.",
    ),
    "d904bf7b044dd3922781": override(
        "CHK_WARMTH_PAIR+E_GRADE_1",
        "gelernte Wärmefamilie; kurzer oder milder Grad",
        "kurz oder mild erwärmen",
        "HOLD_CORES",
        "SELECTED_PRODUCTIVE_PAIR",
        "Only cheky/cheeky license this warmth pair; KY is not split as Y.",
    ),
    "2c1a5fd92b9e3c762242": override(
        "CHK_WARMTH_PAIR+E_GRADE_2",
        "gelernte Wärmefamilie; längerer Grad",
        "länger warm halten",
        "HOLD_CORES",
        "SELECTED_PRODUCTIVE_PAIR",
        "Only cheky/cheeky license this warmth pair; chkeey/chkeedy stay separate cards.",
    ),
    "42cdc187d5b9ffc60063": override(
        "OLK~SOLK_COLLECTION_STATION+GRADE_1",
        "gelernte lokale Sammelstellenfamilie; kurzer Grad",
        "Sammelstelle kurz öffnen oder aktiv halten",
        "HOLD_CORES",
        "SELECTED_LOCAL_STATION",
        "One open event at the right S-run/multiport owner; not a global SOLK root.",
    ),
    "1bfd786e6b8b63734a59": override(
        "OLK~SOLK_COLLECTION_STATION+GRADE_2",
        "gelernte lokale Sammelstellenfamilie; längerer Grad",
        "Sammelstelle länger offen halten",
        "HOLD_CORES",
        "SELECTED_LOCAL_STATION",
        "One open event at the same owner; not a global SOLK root.",
    ),
    "3b70942557b3a40e8030": override(
        "OLK~SOLK_COLLECTION_STATION+GRADE_2+DY_TERMINAL",
        "gelernte lokale Sammelstellenfamilie; längerer Grad; Schluss",
        "an der Sammelstelle stehen oder absetzen lassen; Schluss",
        "HOLD_CORES",
        "SELECTED_LOCAL_STATION",
        "Three terminal events; only local station portability is claimed.",
    ),
}


def build_component_lexicon() -> list[dict[str, str]]:
    rows = read_tsv(COMPONENT_IN)
    revised: list[dict[str, str]] = []
    for source in rows:
        row = dict(source)
        if row["component_id"] == "Y_STATE":
            row.update(
                component_id="Y_REFERENT",
                visible_realizations="y; licensed chy wrappers",
                working_meaning_de="aktuell gemeinter Arbeitsposten; dies oder es",
                status="FIXED_CONTEXT_BOUND",
                licensed_environment="OK-, OT- and CHD~CHED families audited in Y_CHY_PARADIGM.tsv",
                evidence_summary="58 productive events in 12 exact cards, separated from 65 terminal counterevents and five KY boundaries",
                important_limit="Y does not mean open; the owner supplies the concrete noun and a terminal construction supplies closure",
            )
        elif row["component_id"] == "DY_STATE":
            row.update(
                component_id="DY_TERMINAL_CONSTRUCTION",
                visible_realizations="dy only in licensed exact-card terminal frames",
                working_meaning_de="lokalen Arbeitsschritt abschließen",
                status="FIXED_CONTEXT_BOUND",
                licensed_environment="recognized OK-E and wrapped CHD~CHED terminal constructions",
                evidence_summary="terminal behavior remains stable after separating Y as a referent",
                important_limit="not a global D+Y decomposition; bare chdy|chedy remains nonterminal",
            )
        elif row["component_id"] == "P_CHED":
            row.update(
                working_meaning_de="ein- oder hineinführen; zum Empfänger führen",
                status="FIXED_CONTEXT_BOUND",
                evidence_summary="pchedy and pchedal form the receiver-side contrast to L+CHED",
                important_limit="two events only; no global P word or visible arrow direction",
            )
        revised.append(row)

    extra = [
        {
            "component_id": "SH_REST_GRADED_FAMILY",
            "visible_realizations": "cheedy|shedy|tedy; sheedy",
            "working_meaning_de": "ruhen oder nachwirken lassen",
            "status": "FIXED_LEARNED_FAMILY",
            "licensed_environment": "the two exact graded whole cards only",
            "evidence_summary": "12/12 short-grade events and 1/1 long-grade event are field- and statement-final",
            "important_limit": "not a global SH letter root",
        },
        {
            "component_id": "CHK_WARMTH_PAIR",
            "visible_realizations": "cheky; cheeky",
            "working_meaning_de": "kurz erwärmen; länger warm halten",
            "status": "FIXED_LEARNED_PAIR",
            "licensed_environment": "the exact cheky/cheeky pair only",
            "evidence_summary": "five open/internal events share an E/EE grade contrast",
            "important_limit": "KY is not Y; chkeey/chkeedy are different cards",
        },
        {
            "component_id": "OLK_SOLK_COLLECTION_STATION",
            "visible_realizations": "solkey; solkeey; olkeedy|solkeedy",
            "working_meaning_de": "lokale Sammel- oder Empfangsstelle",
            "status": "FIXED_LOCAL_FAMILY",
            "licensed_environment": "right S-run/multiport station on the fixed Biological pages",
            "evidence_summary": "two open grades and three terminal events at the same local owner class",
            "important_limit": "weak and owner-local; not a portable global SOLK word",
        },
        {
            "component_id": "OK_REDUPLICATION",
            "visible_realizations": "OK+OK in qokokchy",
            "working_meaning_de": "erneut in Arbeit nehmen",
            "status": "FIXED_SINGLE_CARD",
            "licensed_environment": "qokokchy only",
            "evidence_summary": "the repeated operator precedes the same wrapped Y referent",
            "important_limit": "one card; not a general reduplication rule",
        },
        {
            "component_id": "OK_AL_Y_ORDER",
            "visible_realizations": "OK+AL+Y in qokaly",
            "working_meaning_de": "den laufenden Posten an der Zielstelle einsetzen",
            "status": "FIXED_SINGLE_CARD",
            "licensed_environment": "qokaly only",
            "evidence_summary": "all three components already have selected bounded contributions",
            "important_limit": "one card; argument order is not independently replicated",
        },
    ]
    return revised + extra


def build_unresolved() -> list[dict[str, str]]:
    keep_ids = {
        "CHEO_IN_CHOKCHEO",
        "LDDY_IN_QOKYLDDY",
        "DAL_LO_SSHK_HULLS",
        "D_S_T_SURFACES",
        "GLOBAL_E",
        "AR_EXACT_CONTENT",
        "AIR_EXACT_CONTENT",
        "MEMORIZED_WHOLE_CARDS",
    }
    rows = [row for row in read_tsv(UNRESOLVED_IN) if row["candidate_component"] in keep_ids]
    rows.extend(
        [
            {
                "candidate_component": "GLOBAL_P",
                "current_best_constraint": "P+CHED points inward or toward a receiver in two fixed cards",
                "why_not_closed": "no independent P card or reversed minimal pair",
                "working_default_until_better_model": "use only inside pchedy and pchedal",
                "prediction_that_could_improve_it": "another P+CHED argument pair should retain receiver direction",
            },
            {
                "candidate_component": "GLOBAL_SH",
                "current_best_constraint": "two learned graded cards encode resting",
                "why_not_closed": "ch/sh/t vary inside one exact card and SH is not independently recurrent",
                "working_default_until_better_model": "rest only in the selected SH-rest family",
                "prediction_that_could_improve_it": "an independent SH base with the same rest contrast",
            },
            {
                "candidate_component": "GLOBAL_CHK",
                "current_best_constraint": "cheky/cheeky encode short versus longer warmth",
                "why_not_closed": "five events and no independent CHK card",
                "working_default_until_better_model": "warmth only in the selected pair",
                "prediction_that_could_improve_it": "another CHK argument should preserve warmth",
            },
            {
                "candidate_component": "GLOBAL_SOLK",
                "current_best_constraint": "three local cards behave as a graded collection-station family",
                "why_not_closed": "all support is owner-local",
                "working_default_until_better_model": "collection station only for these three cards",
                "prediction_that_could_improve_it": "a second owner should reuse the same open/terminal grades",
            },
            {
                "candidate_component": "GENERAL_OK_REDUPLICATION",
                "current_best_constraint": "qokokchy is read as repeat rather than intensity",
                "why_not_closed": "one doubled-OK card",
                "working_default_until_better_model": "repeat only in qokokchy",
                "prediction_that_could_improve_it": "a second OK+OK minimal pair should repeat its single-OK operation",
            },
            {
                "candidate_component": "GENERAL_OK_AL_Y_ORDER",
                "current_best_constraint": "qokaly composes as put current item at target",
                "why_not_closed": "one card and no reversed argument-order pair",
                "working_default_until_better_model": "use the selected whole construction",
                "prediction_that_could_improve_it": "another OK+AL+Y or OK+Y+AL card should clarify binding order",
            },
        ]
    )
    return rows


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    by_id = {row["joint_tuple_id"]: row for row in dictionary}
    missing = sorted(set(OVERRIDES) - set(by_id))
    if missing:
        raise ValueError(f"Override IDs absent from dictionary: {missing}")

    dict_fields = list(dictionary[0]) + [
        "component_completion_previous_segmentation",
        "component_completion_previous_nucleus_de",
        "component_completion_previous_gloss_de",
        "component_completion_source",
        "component_completion_strength",
        "component_completion_note",
    ]
    revised_dictionary: list[dict[str, str]] = []
    for source_row in dictionary:
        row = dict(source_row)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["component_completion_previous_segmentation"] = row["semantic_segmentation"]
            row["component_completion_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["component_completion_previous_gloss_de"] = row["concrete_word_reading_de"]
            for field in (
                "semantic_segmentation",
                "stable_concrete_nucleus_de",
                "concrete_word_reading_de",
                "reading_type",
            ):
                row[field] = selected[field]
            row["local_expansion_examples_de"] = "Komponentenfassung: " + selected["concrete_word_reading_de"]
            row["variation_note"] = row["variation_note"] + "; completion: " + selected["note"]
            row["component_completion_source"] = selected["source"]
            row["component_completion_strength"] = selected["strength"]
            row["component_completion_note"] = selected["note"]
        else:
            row["component_completion_previous_segmentation"] = ""
            row["component_completion_previous_nucleus_de"] = ""
            row["component_completion_previous_gloss_de"] = ""
            row["component_completion_source"] = "UNCHANGED"
            row["component_completion_strength"] = "UNCHANGED"
            row["component_completion_note"] = "NOT_APPLICABLE"
        revised_dictionary.append(row)

    revised_by_id = {row["joint_tuple_id"]: row for row in revised_dictionary}
    event_fields = list(events[0]) + [
        "component_completion_previous_segmentation",
        "component_completion_previous_nucleus_de",
        "component_completion_previous_gloss_de",
        "component_completion_previous_context_de",
        "component_completion_source",
        "component_completion_strength",
    ]
    revised_events: list[dict[str, str]] = []
    for source_row in events:
        row = dict(source_row)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        card = revised_by_id[row["joint_tuple_id"]]
        if selected:
            row["component_completion_previous_segmentation"] = row["semantic_segmentation"]
            row["component_completion_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["component_completion_previous_gloss_de"] = row["concrete_word_reading_de"]
            row["component_completion_previous_context_de"] = row["contextual_event_reading_de"]
            row["semantic_segmentation"] = card["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = card["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = card["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = sentence_case(card["concrete_word_reading_de"])
            row["component_completion_source"] = selected["source"]
            row["component_completion_strength"] = selected["strength"]
        else:
            row["component_completion_previous_segmentation"] = ""
            row["component_completion_previous_nucleus_de"] = ""
            row["component_completion_previous_gloss_de"] = ""
            row["component_completion_previous_context_de"] = ""
            row["component_completion_source"] = "UNCHANGED"
            row["component_completion_strength"] = "UNCHANGED"
        revised_events.append(row)

    statement_fields = [
        "statement_id",
        "record_unit_id",
        "page",
        "loci",
        "field_ids",
        "event_ids",
        "event_count",
        "revised_event_count",
        "surface_sequence",
        "component_consistent_card_sequence_de",
        "compact_component_consistent_reading_de",
        "physical_line_note",
    ]
    grouped: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in revised_events:
        grouped.setdefault(row["statement_id"], []).append(row)
    statements: list[dict[str, str]] = []
    for statement_id, rows in grouped.items():
        glosses = [row["concrete_word_reading_de"] for row in rows]
        statements.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "loci": "|".join(uniq([row["locus"] for row in rows])),
                "field_ids": "|".join(uniq([row["field_id"] for row in rows])),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "event_count": str(len(rows)),
                "revised_event_count": str(sum(row["component_completion_source"] != "UNCHANGED" for row in rows)),
                "surface_sequence": " · ".join(row["surface_display"] for row in rows),
                "component_consistent_card_sequence_de": " · ".join(glosses),
                "compact_component_consistent_reading_de": sentence_case("; ".join(glosses)),
                "physical_line_note": rows[-1]["statement_continuation"],
            }
        )

    components = build_component_lexicon()
    unresolved = build_unresolved()
    write_tsv(DICT_OUT, revised_dictionary, dict_fields)
    write_tsv(EVENT_OUT, revised_events, event_fields)
    write_tsv(STATEMENT_OUT, statements, statement_fields)
    write_tsv(COMPONENT_OUT, components, list(components[0]))
    write_tsv(UNRESOLVED_OUT, unresolved, list(unresolved[0]))

    changed_cards = [row for row in revised_dictionary if row["component_completion_source"] != "UNCHANGED"]
    changed_events = [row for row in revised_events if row["component_completion_source"] != "UNCHANGED"]
    summary: dict[str, object] = {
        "schema": "SIDEQUEST_SELECTED_COMPONENT_COMPLETION_SUMMARY_V1",
        "status": "PASS",
        "cards": len(revised_dictionary),
        "events": len(revised_events),
        "statements": len(statements),
        "changed_cards": len(changed_cards),
        "changed_events": len(changed_events),
        "changed_statements": sum(int(row["revised_event_count"]) > 0 for row in statements),
        "components": len(components),
        "remaining_unresolved_rows": len(unresolved),
        "source_card_counts": {
            source: sum(row["component_completion_source"] == source for row in changed_cards)
            for source in ("Y_CHY", "TRANSFER_ORDER", "HOLD_CORES")
        },
        "source_event_counts": {
            source: sum(row["component_completion_source"] == source for row in changed_events)
            for source in ("Y_CHY", "TRANSFER_ORDER", "HOLD_CORES")
        },
        "inputs": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (DICT_IN, EVENT_IN, COMPONENT_IN, UNRESOLVED_IN)
        },
        "outputs": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (DICT_OUT, EVENT_OUT, STATEMENT_OUT, COMPONENT_OUT, UNRESOLVED_OUT)
        },
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
