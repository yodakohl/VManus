#!/usr/bin/env python3
"""Build the selected source-path-target creative sidequest edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_component_completion"

DICT_IN = SOURCE / "SELECTED_173_COMPONENT_COMPLETE_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_COMPONENT_COMPLETE_INTERLINEAR.tsv"
COMPONENT_IN = SOURCE / "SELECTED_COMPONENT_LEXICON_V2.tsv"
UNRESOLVED_IN = SOURCE / "REMAINING_UNRESOLVED.tsv"

DICT_OUT = HERE / "SELECTED_173_DIRECTIONAL_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_DIRECTIONAL_INTERLINEAR.tsv"
STATEMENT_OUT = HERE / "SELECTED_116_DIRECTIONAL_STATEMENTS.tsv"
RECORD_OUT = HERE / "SELECTED_11_RECORD_READINGS.md"
COMPONENT_OUT = HERE / "SELECTED_DIRECTIONAL_COMPONENT_LEXICON.tsv"
UNRESOLVED_OUT = HERE / "REMAINING_UNRESOLVED_AFTER_DIRECTION.tsv"
SUMMARY_OUT = HERE / "SELECTED_BUILD_SUMMARY.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sentence_case(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def uniq(values: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(value for value in values if value))


def ov(parse: str, nucleus: str, gloss: str, source: str, strength: str, note: str) -> dict[str, str]:
    return {
        "semantic_segmentation": parse,
        "stable_concrete_nucleus_de": nucleus,
        "concrete_word_reading_de": gloss,
        "reading_type": "SELECTED_DIRECTIONAL_COMPLETION__" + source,
        "source": source,
        "strength": strength,
        "note": note,
    }


OVERRIDES = {
    # AR: source/origin.
    "4d4559019a961b834aa1": ov("AR_SOURCE", "AR=Quelle oder Vorrat; aus/von", "aus demselben Vorrat", "DIRECTION_WORKSHOP", "SELECTED_RECURRENT", "Five occurrences preserve a source contribution across Herbal and Biological records."),
    "807591efc3d3f7ddbfab": ov("CHEO_EXTRACT_LIQUID+AR_SOURCE", "CHEO=Auszugsflüssigkeit; AR=aus", "Auszug daraus entnehmen", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "CHEO is concrete but not forced to water, oil, or wine."),
    "883a6708116c342cb10b": ov("SK_LEARNED+AR_SOURCE", "AR=aus; SK supplies the learned warm-medium value", "erwärmtes Medium ausgießen", "DIRECTION_WORKSHOP", "SELECTED_CONTEXT_BOUND", "Outward direction is retained; the exact medium remains locally learned."),
    "b6b654722e55729cc947": ov("OT+AR_SOURCE", "OT=danach; AR=aus", "danach auslassen", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "No fixed lower outlet is built into AR."),
    "3ae9a121ba0045b913e8": ov("Q_RENDERER+OK+AR_SOURCE", "OK=in Arbeit nehmen; AR=aus der Quelle", "daraus in den Arbeitsgang nehmen", "DIRECTION_WORKSHOP", "SELECTED_THIN", "One event, but its contribution matches the recurrent source card."),
    "0f15effeca7ab10bb026": ov("L+CHED+AR_SOURCE", "L+CHED=hinausführen; AR=Quelle", "aus der Quelle hinausführen", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "The former temperature value is removed."),

    # AIR: the moving liquid in a run, neither pure water nor an empty path.
    "12efe866f335461823a6": ov("CH_LEARNED+AIR_FLOW", "AIR=fließende Flüssigkeit im Lauf", "Flüssigkeitszulauf", "DIRECTION_WORKSHOP", "SELECTED_THIN", "The Herbal owner does not draw water; liquid is a workshop default."),
    "22fb87a5a83e5c3fb510": ov("K_LEARNED+AIR_FLOW", "AIR=fließende Flüssigkeit im Lauf", "laufende Beckenflüssigkeit", "DIRECTION_WORKSHOP", "SELECTED_THIN", "No visible arrow licenses the narrower old return-flow direction."),
    "7d2404c835b10a2c06af": ov("OK+AIR_FLOW", "OK=in Gang setzen; AIR=fließende Flüssigkeit im Lauf", "Flüssigkeit in den Lauf bringen", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "No upper/lower direction is encoded."),
    "b154ff779abe5f196c80": ov("S_RENDERER+CHED+AIR_FLOW", "CHED=führen; AIR=fließende Flüssigkeit im Lauf", "fließende Flüssigkeit durch den Lauf führen", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "Clear and drain are not independently visible in this card."),
    "8aedd154964a78e555d6": ov("D_RENDERER+AIR_FLOW+Y_REFERENT+DY_TERMINAL", "AIR=Flüssigkeitslauf; Y=laufender Posten; DY=Schluss", "den Flüssigkeitslauf abschließen", "DIRECTION_EXTENSION", "SELECTED_PREDICTED_COMPOSITION", "This prediction replaces the unrelated whole-card gloss immediately use."),

    # AL: target address.
    "dd0ecaf5e27d81befffc": ov("AL_TARGET", "AL=Ziel- oder Arbeitsstelle; an/zu", "Zielstelle", "DIRECTION_WORKSHOP", "SELECTED_RECURRENT", "Ten occurrences share one exact address card despite surface wrappers."),
    "97ddca78c9ebcc956d04": ov("LD_OR_LEARNED+AL_TARGET", "AL=Zielstelle", "bezeichnete Zielstelle", "DIRECTION_WORKSHOP", "SELECTED_EMBEDDED", "The learned hull supplies marked; AL supplies target."),
    "7811a7daff25d476e28d": ov("OLS_LEARNED+AL_TARGET+Y_SURFACE", "AL=Zielstelle", "untere Zielstelle", "DIRECTION_WORKSHOP", "SELECTED_EMBEDDED", "Lower belongs to the learned hull, not to AL."),
    "90bcf0a9ec0ef56399e6": ov("OT+AL_TARGET", "OT=danach; AL=Zielstelle", "danach zur Zielstelle", "DIRECTION_WORKSHOP", "SELECTED_RECURRENT_COMPOSITION", "The old fixed outlet is demoted to a local possible target."),
    "308e8ea2d5d190c498e8": ov("Q_RENDERER+OK+AL_TARGET", "OK=in Arbeit setzen; AL=Zielstelle", "an der Zielstelle einsetzen", "DIRECTION_WORKSHOP", "SELECTED_RECURRENT_COMPOSITION", "Six events retain the same target application contribution."),
    "4a7a6326ac95a8809302": ov("Q_RENDERER+OK+AL_TARGET+Y_REFERENT", "OK=in Arbeit setzen; AL=Ziel; Y=laufender Posten", "den laufenden Posten an der Zielstelle einsetzen", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "Preserves the prior Y/CHY completion."),
    "93f69c38fdedee1598e9": ov("Q_RENDERER+OK+E_GRADE_2+AL_TARGET", "OK=in Arbeit setzen; EE=anhaltend; AL=Zielstelle", "an der Zielstelle anhaltend in Kontakt halten", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "Target and duration are separated."),
    "00d8ebe3c68294eeac39": ov("CHD+AL_TARGET", "CHD=umsetzen; AL=Zielstelle", "an der Zielstelle umsetzen", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "No separate stir value is required."),
    "433713294b25b0a12f66": ov("L+CHED+AL_TARGET", "L+CHED=hinausführen; AL=Auslassstelle", "Auslassstelle", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "Pairs directly with P+CHED+AL."),
    "ba540da978ea132f6da5": ov("P+CHED+AL_TARGET", "P+CHED=hineinführen; AL=Empfangsstelle", "Einfüllstelle", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "Pairs directly with L+CHED+AL."),

    # In/out transfer pair.
    "ba8142680851f24c9ff2": ov("L+CHED", "L=hinaus; CHED=führen", "hinausführen", "DIRECTION_WORKSHOP", "SELECTED_COMPOSITIONAL", "The old next-basin noun is removed."),
    "de7321bface5628e35d6": ov("L+CHED+DY_TERMINAL", "L=hinaus; CHED=führen; DY=Schluss", "hinausführen; Schluss", "DIRECTION_WORKSHOP", "SELECTED_STRONG", "Eight terminal events make this the strongest direction card."),
    "65df3cd9e59060042d47": ov("P+CHED+DY_TERMINAL", "P=hinein; CHED=führen; DY=Schluss", "hineinführen; Schluss", "DIRECTION_WORKSHOP", "SELECTED_THIN_CONTRAST", "The one event forms the exact opposite of L+CHED+DY."),
    "f2af6326898fb5b490a4": ov("LO_LEARNED+CHED+DY_TERMINAL", "local LO hull; CHED=hinausführen; DY=Schluss", "den Rest hinausführen; Schluss", "DIRECTION_EXTENSION", "SELECTED_LOCAL_EXTENSION", "A learned LO hull supplies rest/remainder; the outward close is retained."),

    # CHEO and LDDY: concrete creative defaults.
    "087a47b5423438cd6b6a": ov("CH_RENDERER+OK+CHEO_EXTRACT_LIQUID", "OK=in Arbeit setzen; CHEO=Auszugsflüssigkeit", "Auszugsflüssigkeit zugeben", "CHEO_LDDY", "SELECTED_PROVISIONAL_CORE", "Water, oil, and wine remain possible local realizations; the dictionary uses the broader concrete carrier."),
    "eb2e4bc143f623ee03ac": ov("Q_RENDERER+OK+Y_REFERENT+LDDY_APPLICATION_CLOSE", "OK+Y=dies anwenden; LDDY=als Auflage befestigen und schließen", "den laufenden Posten als Auflage befestigen; Schluss", "CHEO_LDDY", "SELECTED_SINGLE_CARD_CORE", "The visible arch has no direction; the application close is a learned workshop default."),

    # Seven recurrent cards newly explained by the component system.
    "d665560c8ff80799a82c": ov("CH_RENDERER+OL", "OL=mit dem vorigen Posten", "vom vorigen Posten nehmen", "RECURRENT_COMPOSITION", "SELECTED_RECURRENT_COMPOSITION", "The d/s alternation stays renderer-like."),
    "2c82523794dcb7d2b343": ov("O_S_RENDERER+IIN_GRADE", "IIN=vorgeschriebener Grad oder Stand", "vorgeschriebener Grad", "RECURRENT_COMPOSITION", "SELECTED_PROVISIONAL_COMPOSITION", "Two contexts admit a parameter grade and do not require a clarity word."),
    "94df4847b7b16c98394a": ov("Q_RENDERER+OL+KAIN[AIN_PORTION]", "OL=weiter; KAIN=abgemessene Portion", "mit einer weiteren Portion fortfahren", "RECURRENT_COMPOSITION", "SELECTED_RECURRENT_COMPOSITION", "The two image owners are not one uniquely lower basin."),
    "faf321940aed922846a9": ov("OT+CHEY[wrapped Y_REFERENT]", "OT=nächster; CHEY=Postenverweis", "den nächsten Posten wählen", "RECURRENT_COMPOSITION", "SELECTED_RECURRENT_COMPOSITION", "Two records preserve the next-item contribution."),
    "10488b911aae52b3b334": ov("Q_RENDERER+OT+CH_RENDERER+OR_PREPARATION", "OT=nächste; OR=Zubereitung", "die nächste Zubereitung", "RECURRENT_COMPOSITION", "SELECTED_RECURRENT_COMPOSITION", "Removes a separate selection root."),
    "6b89d6dd70635bc60fe0": ov("Q_S_RENDERER+CTH_READY+E_HOLD+Y_REFERENT", "CTH=bereit; E=halten; Y=laufender Posten", "den laufenden Posten bereit halten", "RECURRENT_COMPOSITION", "SELECTED_PROVISIONAL_COMPOSITION", "Both contexts lie between quantity setup and application."),
    "abb23e5e6936b4147f76": ov("SHED_REST+AL_TARGET", "SHED=ruhen oder absetzen; AL=Zielstelle", "Ruhe- oder Absetzstelle", "RECURRENT_COMPOSITION", "SELECTED_RECURRENT_COMPOSITION", "Two f83r records support a station rather than an abstract duration."),
}


def build_components() -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for source in read_tsv(COMPONENT_IN):
        row = dict(source)
        if row["component_id"] == "AR":
            row.update(working_meaning_de="Quelle oder Vorrat; aus oder von", status="FIXED_IN_WORKING_MODEL", licensed_environment="base AR card plus OK/OT/CHEO/L+CHED compounds", evidence_summary="six exact cards and ten events across Herbal and Biological records", important_limit="does not name a specific vessel, material, height, or direction arrow")
        elif row["component_id"] == "AIR":
            row.update(working_meaning_de="fließende Flüssigkeit im Lauf", status="FIXED_CONTEXT_BOUND", licensed_environment="chair|kair|okair|schedair and predicted dairydy", evidence_summary="five cards form inlet/current/activate/conduct/close readings", important_limit="not necessarily pure water and not a bare pipe or visible arrow")
        elif row["component_id"] == "AL":
            row.update(working_meaning_de="Ziel- oder Arbeitsstelle; an oder zu", status="FIXED_IN_WORKING_MODEL", licensed_environment="base address card and OK/OT/CHED/P/L compounds", evidence_summary="ten base-card events and sixteen compound events", important_limit="lower, outlet, skin, basin, or plant part must come from the local owner or learned hull")
        elif row["component_id"] == "L_CHED":
            row.update(working_meaning_de="hinaus- oder wegführen", status="FIXED_CONTEXT_BOUND", evidence_summary="lched/lchedy/lchedal/lchedar plus local lochedy", important_limit="only licensed before the CHED family")
        elif row["component_id"] == "P_CHED":
            row.update(working_meaning_de="hinein- oder zum Empfänger führen", status="FIXED_CONTEXT_BOUND", evidence_summary="pchedal and pchedy form the thin opposite of L+CHED", important_limit="two events only; only licensed before CHED")
        elif row["component_id"] == "AIN":
            row.update(visible_realizations="ain; kain in licensed cards", licensed_environment="base card, OK+AIN, and OL+KAIN", evidence_summary="base/OK family plus the two recurrent OLKAIN events")
        elif row["component_id"] == "SH_REST_GRADED_FAMILY":
            row.update(component_id="SHED_REST_FAMILY", visible_realizations="cheedy|shedy|tedy; sheedy; shedal", working_meaning_de="ruhen, nachwirken oder sich absetzen", status="FIXED_LEARNED_FAMILY", licensed_environment="the two terminal rest cards and SHED+AL station card", evidence_summary="thirteen terminal rest events plus two SHED+AL station events", important_limit="not a global meaning of every visible sh or shed substring")
        result.append(row)

    result.extend(
        [
            {"component_id": "OR_PREPARATION", "visible_realizations": "or|chor|shor|sor", "working_meaning_de": "Zubereitung oder bereiteter Ansatz", "status": "FIXED_IN_WORKING_MODEL", "licensed_environment": "base exact card and OT+OR", "evidence_summary": "seven base events and two OTCHOR events", "important_limit": "not every internal or is this root"},
            {"component_id": "IIN_GRADE", "visible_realizations": "oiiin|soiiin", "working_meaning_de": "vorgeschriebener Grad oder Stand", "status": "PROVISIONAL_RECURRENT", "licensed_environment": "the exact two-event OIIIN card only", "evidence_summary": "both contexts precede readiness, processing, or a terminal station", "important_limit": "relation to AIIN is a working composition, not a phonetic derivation"},
            {"component_id": "CTH_READY", "visible_realizations": "cthy exact family; qcthey|shcthey", "working_meaning_de": "bereit oder in Bereitschaft", "status": "PROVISIONAL_RECURRENT", "licensed_environment": "base CTHY and the two CTHEY events", "evidence_summary": "the CTHEY pair lies between setup and application", "important_limit": "warmth and equality are not inherent in CTH"},
            {"component_id": "CHEO_EXTRACT_LIQUID", "visible_realizations": "chokcheo; cheoar", "working_meaning_de": "Auszugs- oder Trägerflüssigkeit", "status": "PROVISIONAL_TWO_CARD_CORE", "licensed_environment": "OK+CHEO before cloth filtering and CHEO+AR in a second Herbal record", "evidence_summary": "two different Herbal pages support carrier/extract liquid", "important_limit": "does not distinguish water, oil, wine, or another liquid"},
            {"component_id": "LDDY_APPLICATION_CLOSE", "visible_realizations": "qokylddy", "working_meaning_de": "als Auflage befestigen und schließen", "status": "SELECTED_SINGLE_CARD_CORE", "licensed_environment": "the one exact qokylddy card", "evidence_summary": "one closed cell at the local f83r arch-linked pair", "important_limit": "learned whole terminal core; not portable morphology yet"},
        ]
    )
    return result


def build_unresolved() -> list[dict[str, str]]:
    remove = {"AR_EXACT_CONTENT", "AIR_EXACT_CONTENT", "CHEO_IN_CHOKCHEO", "LDDY_IN_QOKYLDDY"}
    result = [row for row in read_tsv(UNRESOLVED_IN) if row["candidate_component"] not in remove]
    result.extend(
        [
            {"candidate_component": "AIR_EXACT_SUBSTANCE", "current_best_constraint": "moving liquid in a run", "why_not_closed": "the drawings show no arrows and the Herbal owner shows no liquid", "working_default_until_better_model": "flowing liquid without specifying pure water", "prediction_that_could_improve_it": "another AIR card should preserve motion while allowing a different liquid"},
            {"candidate_component": "CHEO_EXACT_LIQUID", "current_best_constraint": "extract or carrier liquid", "why_not_closed": "two Herbal events do not distinguish water oil wine or decoction", "working_default_until_better_model": "extract liquid", "prediction_that_could_improve_it": "another CHEO compound should preserve carrier/extract behavior"},
            {"candidate_component": "LDDY_PORTABILITY", "current_best_constraint": "application close read as fastening a poultice", "why_not_closed": "one exact card at one local owner", "working_default_until_better_model": "learned qokylddy construction only", "prediction_that_could_improve_it": "a second LDDY carrier should close an application rather than a transfer"},
            {"candidate_component": "IIN_GRADE_PORTABILITY", "current_best_constraint": "the recurrent OIIIN card means prescribed grade", "why_not_closed": "two events and no independent IIN base card", "working_default_until_better_model": "grade only in oiiin|soiiin", "prediction_that_could_improve_it": "another IIN compound should occupy a parameter slot"},
        ]
    )
    return result


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    by_id = {row["joint_tuple_id"]: row for row in dictionary}
    missing = sorted(set(OVERRIDES) - set(by_id))
    if missing:
        raise ValueError(f"Missing override IDs: {missing}")

    dict_fields = list(dictionary[0]) + [
        "direction_previous_segmentation",
        "direction_previous_nucleus_de",
        "direction_previous_gloss_de",
        "direction_revision_source",
        "direction_revision_strength",
        "direction_revision_note",
    ]
    revised_dictionary: list[dict[str, str]] = []
    for source_row in dictionary:
        row = dict(source_row)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["direction_previous_segmentation"] = row["semantic_segmentation"]
            row["direction_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["direction_previous_gloss_de"] = row["concrete_word_reading_de"]
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
                row[key] = selected[key]
            row["local_expansion_examples_de"] = "Richtungsfassung: " + selected["concrete_word_reading_de"]
            row["variation_note"] += "; direction: " + selected["note"]
            row["direction_revision_source"] = selected["source"]
            row["direction_revision_strength"] = selected["strength"]
            row["direction_revision_note"] = selected["note"]
        else:
            row["direction_previous_segmentation"] = ""
            row["direction_previous_nucleus_de"] = ""
            row["direction_previous_gloss_de"] = ""
            row["direction_revision_source"] = "UNCHANGED"
            row["direction_revision_strength"] = "UNCHANGED"
            row["direction_revision_note"] = "NOT_APPLICABLE"
        revised_dictionary.append(row)

    revised_by_id = {row["joint_tuple_id"]: row for row in revised_dictionary}
    event_fields = list(events[0]) + [
        "direction_previous_segmentation",
        "direction_previous_nucleus_de",
        "direction_previous_gloss_de",
        "direction_previous_context_de",
        "direction_revision_source",
        "direction_revision_strength",
    ]
    revised_events: list[dict[str, str]] = []
    for source_row in events:
        row = dict(source_row)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        card = revised_by_id[row["joint_tuple_id"]]
        if selected:
            row["direction_previous_segmentation"] = row["semantic_segmentation"]
            row["direction_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["direction_previous_gloss_de"] = row["concrete_word_reading_de"]
            row["direction_previous_context_de"] = row["contextual_event_reading_de"]
            row["semantic_segmentation"] = card["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = card["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = card["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = sentence_case(card["concrete_word_reading_de"])
            row["direction_revision_source"] = selected["source"]
            row["direction_revision_strength"] = selected["strength"]
        else:
            row["direction_previous_segmentation"] = ""
            row["direction_previous_nucleus_de"] = ""
            row["direction_previous_gloss_de"] = ""
            row["direction_previous_context_de"] = ""
            row["direction_revision_source"] = "UNCHANGED"
            row["direction_revision_strength"] = "UNCHANGED"
        revised_events.append(row)

    statement_fields = [
        "statement_id", "record_unit_id", "page", "loci", "field_ids",
        "event_ids", "event_count", "revised_event_count", "surface_sequence",
        "directional_card_sequence_de", "compact_directional_reading_de",
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
                "revised_event_count": str(sum(row["direction_revision_source"] != "UNCHANGED" for row in rows)),
                "surface_sequence": " · ".join(row["surface_display"] for row in rows),
                "directional_card_sequence_de": " · ".join(glosses),
                "compact_directional_reading_de": sentence_case("; ".join(glosses)),
                "physical_line_note": rows[-1]["statement_continuation"],
            }
        )

    records: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in statements:
        records.setdefault(row["record_unit_id"], []).append(row)
    markdown = [
        "# Complete eleven-record directional working edition",
        "",
        "Every statement is retained in exact card order. The German lines are",
        "compact workshop expansions, not literal plaintext or sentence-boundary claims.",
        "",
    ]
    for record_id, rows in records.items():
        markdown.extend([f"## {record_id} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            markdown.append(f"{index}. **{row['statement_id']}** — {row['compact_directional_reading_de']}.")
        markdown.append("")
    RECORD_OUT.write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")

    components = build_components()
    unresolved = build_unresolved()
    write_tsv(DICT_OUT, revised_dictionary, dict_fields)
    write_tsv(EVENT_OUT, revised_events, event_fields)
    write_tsv(STATEMENT_OUT, statements, statement_fields)
    write_tsv(COMPONENT_OUT, components, list(components[0]))
    write_tsv(UNRESOLVED_OUT, unresolved, list(unresolved[0]))

    changed_cards = [row for row in revised_dictionary if row["direction_revision_source"] != "UNCHANGED"]
    changed_events = [row for row in revised_events if row["direction_revision_source"] != "UNCHANGED"]
    summary: dict[str, object] = {
        "schema": "SIDEQUEST_SELECTED_DIRECTIONAL_COMPLETION_SUMMARY_V1",
        "status": "PASS",
        "cards": len(revised_dictionary),
        "events": len(revised_events),
        "statements": len(statements),
        "records": len(records),
        "changed_cards": len(changed_cards),
        "changed_events": len(changed_events),
        "changed_statements": sum(int(row["revised_event_count"]) > 0 for row in statements),
        "components": len(components),
        "remaining_unresolved_rows": len(unresolved),
        "source_card_counts": {source: sum(row["direction_revision_source"] == source for row in changed_cards) for source in ("DIRECTION_WORKSHOP", "DIRECTION_EXTENSION", "CHEO_LDDY", "RECURRENT_COMPOSITION")},
        "source_event_counts": {source: sum(row["direction_revision_source"] == source for row in changed_events) for source in ("DIRECTION_WORKSHOP", "DIRECTION_EXTENSION", "CHEO_LDDY", "RECURRENT_COMPOSITION")},
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (DICT_IN, EVENT_IN, COMPONENT_IN, UNRESOLVED_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha256(path) for path in (DICT_OUT, EVENT_OUT, STATEMENT_OUT, RECORD_OUT, COMPONENT_OUT, UNRESOLVED_OUT)},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
