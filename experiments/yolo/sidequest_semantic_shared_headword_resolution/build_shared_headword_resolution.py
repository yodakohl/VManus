#!/usr/bin/env python3
"""Resolve the ten shared apprentice headwords into contextual workshop variants."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
PHRASEBOOK = HERE.parent / "sidequest_semantic_apprentice_phrasebook"
LEXICON = HERE.parent / "sidequest_semantic_open_middle_lexicon"

WORDS_IN = PHRASEBOOK / "APPRENTICE_68_WHOLE_WORD_DECK.tsv"
PHRASES_IN = PHRASEBOOK / "APPRENTICE_116_PHRASES.tsv"
EVENTS_IN = LEXICON / "SELECTED_381_OPEN_MIDDLE_INTERLINEAR.tsv"
SENTENCES_IN = LEXICON / "SELECTED_116_OPEN_MIDDLE_SENTENCES.tsv"

DECISIONS_OUT = HERE / "SHARED_HEADWORD_24_CARD_DECISIONS.tsv"
FAMILIES_OUT = HERE / "SHARED_HEADWORD_10_FAMILY_SUMMARY.tsv"
WORDS_OUT = HERE / "APPRENTICE_68_RESOLVED_WORD_DECK.tsv"
PHRASES_OUT = HERE / "APPRENTICE_116_RESOLVED_PHRASES.tsv"
RECORDS_OUT = HERE / "APPRENTICE_11_RESOLVED_RECORDS.md"
CHECK_OUT = HERE / "BUILD_CHECK.json"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


# surface -> family, base headword, resolved reading, axis, value,
# decision class, compact reason
DECISION_META = {
    "chary": ("F01_KUEHLEN", "kühlen", "antrocknen lassen", "PROCESS_PHASE", "COATING_DRY", "CONTEXTUAL_SUBTYPE", "Folgt direkt auf Aufstreichen am Korb-/Gefäßposten."),
    "ral": ("F01_KUEHLEN", "kühlen", "abkühlen lassen", "PROCESS_PHASE", "LIQUID_COOL", "CONTEXTUAL_SUBTYPE", "Folgt auf Portion, Durchleiten und Zusatz im gemeinsamen Pool."),
    "tchody": ("F01_KUEHLEN", "kühlen", "kalt stellen", "PROGRAM_SCOPE", "FINAL_PRODUCT_COOL", "TERMINAL_ROUTINE_VARIANT", "Schließt den Kräutersud unmittelbar nach dem Klarlauf."),
    "ody": ("F01_KUEHLEN", "kühlen", "kühlen", "PROGRAM_SCOPE", "PORTION_COOL", "TERMINAL_ROUTINE_VARIANT", "Schließt die bemessene Postenportion als Kühlprogramm."),
    "lar": ("F02_ABLAUF", "Ablauf", "Ablauf schließen", "POLARITY_AND_STATION", "CLOSE_LOWER_POOL", "STATION_LOCAL_SYNONYM", "Alleiniger Befehl am unteren Mehrfigurenpool."),
    "lo": ("F02_ABLAUF", "Ablauf", "Ablauf schließen", "POLARITY_AND_STATION", "CLOSE_MARGIN_STATION", "STATION_LOCAL_SYNONYM", "Eröffnet die Schließ-/Umsetzsequenz an der Randstation."),
    "sheey": ("F02_ABLAUF", "Ablauf", "Ablauf öffnen", "POLARITY_AND_STATION", "OPEN_MAIN_PAIR", "CONTEXTUAL_SUBTYPE", "Steht zwischen längerem Wärmen und kurzem Folgeprogramm."),
    "oltchy": ("F03_WAERME", "Wärme", "warm halten", "PROCESS_PHASE", "MAINTAIN", "CONTEXTUAL_SUBTYPE", "Folgt auf Zielsetzung und führt in den gehaltenen Ansatz."),
    "qotchol": ("F03_WAERME", "Wärme", "anwärmen", "PROCESS_PHASE", "ONSET", "CONTEXTUAL_SUBTYPE", "Folgt auf Ansetzen und geht der Fortsetzung voraus."),
    "cheedar": ("F04_BECKEN", "Becken", "Auffangbecken", "VESSEL_ROLE", "COLLECT", "CONTEXTUAL_SUBTYPE", "Beginnt die Absetz-/Sammelsequenz am Hauptbogenpaar."),
    "qolchey": ("F04_BECKEN", "Becken", "Arbeitsbecken", "VESSEL_ROLE", "WORK", "CONTEXTUAL_SUBTYPE", "Beginnt eine lokale Ansetzvariante am Hauptpaar."),
    "cheeety": ("F05_SPUEL", "Spülung", "Vorspülung", "PROCESS_ROLE", "PRIOR_PASS", "CONTEXTUAL_SUBTYPE", "Steht nach Fortsetzen und vor dem nächsten Kurzprogramm."),
    "tshey": ("F05_SPUEL", "Spülung", "Spülwasser", "PROCESS_ROLE", "MEDIUM", "CONTEXTUAL_SUBTYPE", "Besetzt ausdrücklich den Mediumslot."),
    "lcheey": ("F06_STELLE", "Stelle", "Körperstelle", "OWNER_DOMAIN", "FIGURE_POOL", "CONTEXTUAL_SUBTYPE", "Liegt im Besitzerwechsel zum unteren Mehrfigurenpool."),
    "qolky": ("F06_STELLE", "Stelle", "Station", "OWNER_DOMAIN", "APPARATUS_POOL", "CONTEXTUAL_SUBTYPE", "Liegt im technischen Auslass-/Auffangmodul des gemeinsamen Pools."),
    "solkaiin": ("F07_TUCH", "Tuch", "Seihtuch", "TOOL_ROLE", "FILTER", "CONTEXTUAL_SUBTYPE", "Steht unmittelbar vor Durchleiten in den oberen Paarbecken."),
    "dain": ("F07_TUCH", "Tuch", "Tuch", "TOOL_ROLE", "GENERAL_INSERT", "CONTEXTUAL_SUBTYPE", "Wird in zwei verschiedenen Stationen allgemein eingelegt."),
    "rol": ("F08_WARM", "warm", "weiter warm", "THERMAL_STATE", "CONTINUING", "CONTEXTUAL_SUBTYPE", "Trägt zugleich ORDER und STATE im langen Poolprogramm."),
    "lol": ("F08_WARM", "warm", "warm", "THERMAL_STATE", "GENERAL", "CONTEXTUAL_SUBTYPE", "Einfacher warmer Zustand zwischen Fortsetzung und Zielumsetzung."),
    "shecthy": ("F08_WARM", "warm", "handwarm", "THERMAL_STATE", "TOUCH_THRESHOLD", "CONTEXTUAL_SUBTYPE", "Folgt auf Absetzen und markiert die Berührungsschwelle."),
    "choy": ("F09_WASCH", "waschen", "abwaschen", "ACTION_SCOPE", "OPEN_TARGET_ACTION", "CONTEXTUAL_SUBTYPE", "Offene Herbal-Handlung an der bezeichneten Stelle."),
    "rshedy": ("F09_WASCH", "waschen", "Waschgang", "ACTION_SCOPE", "TERMINAL_PROGRAM", "TERMINAL_ROUTINE_VARIANT", "Alleinstehendes geschlossenes Biological-Programm."),
    "sheckhy": ("F10_UEBERLAUF", "Überlauf", "Überlauf", "STATION_ID", "UPPER_BASINS", "STATION_LOCAL_SYNONYM", "Lokales Zeichen der oberen Paarbecken-/Zylinderstation."),
    "qockhey": ("F10_UEBERLAUF", "Überlauf", "Überlauf", "STATION_ID", "LEFT_FRINGE", "STATION_LOCAL_SYNONYM", "Lokales Zeichen des linken offenen Fransenpostens."),
}

FAMILY_META = {
    "F01_KUEHLEN": ("kühlen", "PROCESS_PHASE_AND_PROGRAM_SCOPE", "Antrocknen, offenes Abkühlen und terminales Kaltstellen teilen nur den Kühlkern."),
    "F02_ABLAUF": ("Ablauf", "POLARITY_PLUS_LOCAL_SYNONYM", "LAR/LO schließen zwei lokale Abläufe; SHEEY öffnet den Ablauf des Hauptpaars."),
    "F03_WAERME": ("Wärme", "ONSET_VS_MAINTENANCE", "QOTCHOL startet Wärme, OLTCHY hält sie."),
    "F04_BECKEN": ("Becken", "VESSEL_FUNCTION", "CHEEDAR sammelt, QOLCHEY ist das Arbeitsbecken."),
    "F05_SPUEL": ("Spülung", "PROCESS_VS_MEDIUM", "CHEEETY bezeichnet den vorausgehenden Gang, TSHEY das Spülmedium."),
    "F06_STELLE": ("Stelle", "OWNER_DOMAIN", "LCHEEY gehört zur Figuren-/Körperstelle, QOLKY zur technischen Station."),
    "F07_TUCH": ("Tuch", "TOOL_SPECIALIZATION", "SOLKAIIN ist ausdrücklich Filtertuch; DAIN bleibt allgemeines Tuch."),
    "F08_WARM": ("warm", "THERMAL_GRADE", "ROL führt Wärme fort, LOL ist allgemein warm, SHECTHY ist handwarm."),
    "F09_WASCH": ("waschen", "OPEN_ACTION_VS_PROGRAM", "CHOY ist offenes Abwaschen; RSHEDY der ganze geschlossene Waschgang."),
    "F10_UEBERLAUF": ("Überlauf", "STATION_LOCAL_SYNONYM", "Zwei Stationskarten behalten dieselbe Grundbedeutung; keine zusätzliche Funktion ist nötig."),
}

SENTENCE_REVISIONS = {
    "H3-S001": "Bereite aus dem bildlich bestimmten Kraut einen Sud, wringe ihn aus, lass ihn bis zum Standmaß stehen, seih nach, nimm den Klarlauf und stelle ihn kalt.",
    "B3-S011": "Streiche den Posten auf, setze ihn an, setze um und lass die Auflage antrocknen.",
    "H4-S004": "Gib nach Sollmaß eine Ansatzportion dorthin, halte die Portion warm und belasse den Posten im Ansatz.",
    "B3-S026": "Stelle das Auffangbecken bereit, warte bis zum Absetzmaß, setze um, gib eine Portion zu, halte bereit, warte bis der Posten klar ist, sammle länger und schließe.",
    "B4-S002": "Bereite das Arbeitsbecken vor, setze länger und dann kurz an und schließe.",
    "B3-S029": "Führe nach der Vorspülung weiter, setze kurz an und schließe.",
    "B2-S012": "Ziehe den Posten ab, nimm den Klarlauf, halte ihn kurz bereit, setze ihn länger an der Körperstelle nach Sollmaß an, führe ihn vollständig aus und schließe.",
    "B1-S014": "Setze zur Station um, führe am Auslass ab und führe danach von dort weiter.",
    "B1-S002": "Stelle das Sollmaß ein, lass Beckenwasser zu, setze dort an, gib eine weitere Portion und Zusatz hinzu, halte den Fortsetzungsansatz weiter warm, führe ihn bis zum Maß weiter, stelle das Sollmaß ein, halte dort länger, prüfe erneut das Sollmaß, leite durch, setze um und schließe.",
    "H5-S002": "Wasche die bezeichnete Stelle ab, setze den vorbereiteten Zutatenansatz an und trage ihn auf.",
    "B2-S019": "Führe den Waschgang aus und schließe.",
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


def build() -> dict[str, object]:
    words = read_tsv(WORDS_IN)
    prior_phrases = read_tsv(PHRASES_IN)
    events = read_tsv(EVENTS_IN)
    sentences = read_tsv(SENTENCES_IN)
    if (len(words), len(prior_phrases), len(events), len(sentences)) != (68, 116, 381, 116):
        raise AssertionError("unexpected input dimensions")

    word_by_surface = {row["surface_family"]: row for row in words}
    if not set(DECISION_META) <= set(word_by_surface):
        raise AssertionError("decision surface missing from word deck")
    word_by_card = {row["joint_tuple_id"]: row for row in words}
    events_by_id = {row["event_id"]: row for row in events}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    sentence_map = {row["statement_id"]: row for row in sentences}

    decisions: list[dict[str, str]] = []
    for surface, meta in DECISION_META.items():
        family, base, resolved, axis, value, decision_class, reason = meta
        word = word_by_surface[surface]
        card_events = [events_by_id[event_id] for event_id in word["event_ids"].split("|")]
        neighbors = []
        owners = []
        statements = []
        for event in card_events:
            sequence = events_by_statement[event["statement_id"]]
            index = sequence.index(event)
            previous = sequence[index - 1]["concrete_word_reading_de"] if index else "START"
            following = sequence[index + 1]["concrete_word_reading_de"] if index + 1 < len(sequence) else "END"
            neighbors.append(f"{event['event_id']}:{previous}>{following}")
            owners.append(sentence_map[event["statement_id"]]["work_module_owner_sequence"])
            statements.append(event["statement_id"])
        decisions.append({
            "family_id": family,
            "base_headword_de": base,
            "joint_tuple_id": word["joint_tuple_id"],
            "surface_family": surface,
            "occurrence_count": word["occurrence_count"],
            "event_ids": word["event_ids"],
            "statement_ids": "|".join(dict.fromkeys(statements)),
            "pages": word["pages"],
            "owner_sequences": "|".join(dict.fromkeys(owners)),
            "neighbor_contexts_de": "|".join(neighbors),
            "previous_shared_headword_de": word["apprentice_headword_de"],
            "resolved_reading_de": resolved,
            "variant_axis": axis,
            "variant_value": value,
            "decision_class": decision_class,
            "reason_de": reason,
        })
    decision_by_card = {row["joint_tuple_id"]: row for row in decisions}

    resolved_words: list[dict[str, str]] = []
    for word in words:
        decision = decision_by_card.get(word["joint_tuple_id"])
        row = dict(word)
        row["shared_headword_family"] = decision["family_id"] if decision else "NONE"
        row["base_headword_de"] = decision["base_headword_de"] if decision else word["apprentice_headword_de"]
        row["resolved_reading_de"] = decision["resolved_reading_de"] if decision else word["apprentice_headword_de"]
        row["variant_axis"] = decision["variant_axis"] if decision else "NONE"
        row["variant_value"] = decision["variant_value"] if decision else "NONE"
        row["resolution_status"] = decision["decision_class"] if decision else "UNCHANGED_SINGLE_HEADWORD"
        resolved_words.append(row)
    resolved_word_map = {row["joint_tuple_id"]: row for row in resolved_words}

    family_rows: list[dict[str, str]] = []
    for family_id, (base, disposition, reading) in FAMILY_META.items():
        selected = [row for row in decisions if row["family_id"] == family_id]
        family_rows.append({
            "family_id": family_id,
            "base_headword_de": base,
            "exact_card_types": str(len(selected)),
            "occurrences": str(sum(int(row["occurrence_count"]) for row in selected)),
            "disposition": disposition,
            "resolved_readings_de": "|".join(dict.fromkeys(row["resolved_reading_de"] for row in selected)),
            "surface_families": "|".join(row["surface_family"] for row in selected),
            "working_reading_de": reading,
        })

    phrase_rows: list[dict[str, str]] = []
    for prior in prior_phrases:
        statement_events = events_by_statement[prior["statement_id"]]
        heads = []
        tagged = []
        changed_cards = []
        for event in statement_events:
            word = resolved_word_map.get(event["joint_tuple_id"])
            head = word["resolved_reading_de"] if word else clean_program_headword(event["concrete_word_reading_de"])
            is_close = event["step_closure_role"] == "COMMIT_CELL"
            heads.append(head + (" [SCHLUSS]" if is_close else ""))
            tagged.append(
                f"[PROGRAM] {head} [SCHLUSS]"
                if is_close
                else f"[{event['workshop_slots']}] {head}"
            )
            if event["joint_tuple_id"] in decision_by_card:
                changed_cards.append(event["joint_tuple_id"])
        revised_sentence = SENTENCE_REVISIONS.get(prior["statement_id"], prior["fluent_workshop_sentence_de"])
        phrase_rows.append({
            **prior,
            "previous_headword_sequence_de": prior["headword_sequence_de"],
            "resolved_headword_sequence_de": " → ".join(heads),
            "resolved_slot_sequence_de": " | ".join(tagged),
            "shared_headword_cards": "|".join(dict.fromkeys(changed_cards)) if changed_cards else "NONE",
            "shared_headword_card_count": str(len(changed_cards)),
            "previous_fluent_sentence_de": prior["fluent_workshop_sentence_de"],
            "resolved_fluent_sentence_de": revised_sentence,
            "sentence_revised": "YES" if revised_sentence != prior["fluent_workshop_sentence_de"] else "NO",
        })

    lines = [
        "# Elf Records nach Auflösung der gemeinsamen Stichwörter",
        "",
        "Die Kartenfolge benutzt die kontextuell aufgelösten Lesungen; darunter steht die flüssige Werkstattphrase.",
        "",
    ]
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in phrase_rows:
        by_record[row["record_unit_id"]].append(row)
    for record in RECORD_ORDER:
        selected = by_record[record]
        lines.extend([f"## {record} — {selected[0]['page']}", ""])
        for row in selected:
            marker = " · REVIDIERT" if row["sentence_revised"] == "YES" else ""
            lines.append(f"- **{row['statement_id']} · {row['template_name_de']}{marker}**")
            lines.append(f"  - Karten: {row['resolved_headword_sequence_de']}")
            lines.append(f"  - Lesung: {row['resolved_fluent_sentence_de']}")
        lines.append("")
    RECORDS_OUT.write_text("\n".join(lines), encoding="utf-8")

    write_tsv(DECISIONS_OUT, decisions)
    write_tsv(FAMILIES_OUT, family_rows)
    write_tsv(WORDS_OUT, resolved_words)
    write_tsv(PHRASES_OUT, phrase_rows)

    class_counts = Counter(row["decision_class"] for row in decisions)
    checks = {
        "families_10": len(family_rows) == 10,
        "target_cards_24": len(decisions) == 24,
        "target_occurrences_25": sum(int(row["occurrence_count"]) for row in decisions) == 25,
        "decision_classes_17_3_4": class_counts == Counter({"CONTEXTUAL_SUBTYPE": 17, "TERMINAL_ROUTINE_VARIANT": 3, "STATION_LOCAL_SYNONYM": 4}),
        "graphic_allographs_zero": not any(row["decision_class"] == "GRAPHIC_ALLOGRAPH" for row in decisions),
        "resolved_word_types_68": len(resolved_words) == 68,
        "base_headwords_54": len({row["base_headword_de"].casefold() for row in resolved_words}) == 54,
        "resolved_readings_66": len({row["resolved_reading_de"].casefold() for row in resolved_words}) == 66,
        "phrases_116": len(phrase_rows) == 116,
        "affected_statements_25": sum(row["shared_headword_card_count"] != "0" for row in phrase_rows) == 25,
        "revised_sentences_11": sum(row["sentence_revised"] == "YES" for row in phrase_rows) == 11,
        "all_events_bound": sum(int(row["event_count"]) for row in phrase_rows) == 381,
        "records_11": len(by_record) == 11,
        "records_markdown_complete": all(f"## {record} —" in RECORDS_OUT.read_text(encoding="utf-8") for record in RECORD_ORDER),
        "fixed_pages_only": {row["page"] for row in events} == ALLOWED_PAGES,
        "sealed_absent": not any(row["page"].startswith("f84") for row in events),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "shared_families": len(family_rows),
            "target_exact_cards": len(decisions),
            "target_occurrences": sum(int(row["occurrence_count"]) for row in decisions),
            "decision_classes": dict(sorted(class_counts.items())),
            "base_headwords": len({row["base_headword_de"].casefold() for row in resolved_words}),
            "resolved_readings": len({row["resolved_reading_de"].casefold() for row in resolved_words}),
            "affected_statements": sum(row["shared_headword_card_count"] != "0" for row in phrase_rows),
            "revised_sentences": sum(row["sentence_revised"] == "YES" for row in phrase_rows),
        },
        "working_rule": "SHARED HEADWORD IS A SEMANTIC BASE; EXACT CARD PLUS OWNER, PHASE, POLARITY, TOOL ROLE OR PROGRAM SCOPE SELECTS THE WORKSHOP READING",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_paths = [DECISIONS_OUT, FAMILIES_OUT, WORDS_OUT, PHRASES_OUT, RECORDS_OUT, CHECK_OUT]
    summary = {
        **result,
        "input_hashes": {path.name: sha256(path) for path in (WORDS_IN, PHRASES_IN, EVENTS_IN, SENTENCES_IN)},
        "output_hashes": {path.name: sha256(path) for path in output_paths},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
