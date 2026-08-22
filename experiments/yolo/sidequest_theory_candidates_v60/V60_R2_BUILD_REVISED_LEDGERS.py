#!/usr/bin/env python3
"""Build the V60 R2 exact-card competition and revised full prose ledgers.

Inputs are restricted to canonical V59 R1 end artifacts. Page-bearing TSVs are
materialized through the selector-first guarded query command. No PAGE_HOST,
substring, sound, or language assignment is used.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
ROOT = OUT_DIR.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_theory_candidates_v59"
ALLOWED_PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")

DECISIONS = {
    "AIIN": {
        "id": "2f1c5e56e8f0ff459065",
        "v59": "MASS?",
        "winner": "MASS?",
        "rival1": "VORGABE?",
        "rival2": "MENGE?",
        "word_class": "SUBSTANTIV_ODER_MASS_SIGLE",
        "decision": "KEEP",
        "confidence": ".58",
        "historical_use": "Kurze Rezept- oder Registersigle fuer mensura/quantitas beziehungsweise das vorgeschriebene Mass eines Bestandteils; Analogie, keine Sprachzuweisung.",
        "all_fit": "20/20 Kontexte erlauben einen breiten Mass-/Parameterhinweis; 6 FIRST, 9 MIDDLE, 5 LAST und kein Schlussvorkommen.",
        "counter": "Kein Kontext zeigt Einheit oder Skala; dieselbe Mobilitaet traegt VORGABE oder blossen Wertslot, und nur sichtbares daiin besitzt den strengeren Parameterlead.",
    },
    "OKY": {
        "id": "276a7c2d74d1143446f4",
        "v59": "VERWENDEN?",
        "winner": "VERWENDEN?",
        "rival1": "NEHMEN?",
        "rival2": "ANWENDEN?",
        "word_class": "VERB_INFINITIV_ODER_IMPERATIV",
        "decision": "KEEP",
        "confidence": ".60",
        "historical_use": "Knappes Rezeptverb fuer gebrauchen/utere nach bild- oder rubrikgeliefertem Objekt; als Ganzbrevigraf lehrbar, nicht zerlegbar.",
        "all_fit": "10/10 Kontexte in Herbal und Bio lassen ein generisches Gebrauchsverb zu; 1 FIRST, 6 MIDDLE, 2 LAST, 1 ONLY.",
        "counter": "In den Biozellen kann dieselbe Karte ebenso einen Posten ausfuehren oder fortsetzen; das verwendete Objekt ist immer still ergaenzt.",
    },
    "CTHY": {
        "id": "e0b630cb1b5df5e7105b",
        "v59": "BEREIT?",
        "winner": "BEREIT?",
        "rival1": "DANN?",
        "rival2": "FERTIG?",
        "word_class": "ZUSTANDSADJEKTIV_ODER_TEMPORALPRAEDIKAT",
        "decision": "KEEP",
        "confidence": ".48",
        "historical_use": "Statuskuerzel fuer paratus beziehungsweise eine Formel wie wenn bereit; brauchbar in Rezeptfortsetzung und Arbeitszelle.",
        "all_fit": "7/7 Kontexte dulden Bereitschaft als lokalen Zustand; 6 MIDDLE und 1 LAST, in drei Herbal- und einem Bio-Record.",
        "counter": "Mehrere Vorkommen stehen nicht am Prozessende, besonders f10r_R2 vor einem Bereitungsnomen; DANN oder ein formaler Statusslot bleibt fast gleich gut.",
    },
    "OR": {
        "id": "7a4bb8136330ee4e6e56",
        "v59": "BEREITUNG?",
        "winner": "BEREITUNG?",
        "rival1": "FLÜSSIGKEIT?",
        "rival2": "POSTEN?",
        "word_class": "SACHNOMEN",
        "decision": "KEEP",
        "confidence": ".42",
        "historical_use": "Nomen oder Fachsigle fuer praeparatio/confectio, also ein bereits bearbeitetes Werkstueck oder Praeparat ohne festgelegtes Medium.",
        "all_fit": "7/7 Kontexte erlauben ein bereitetes Arbeitsobjekt; 2 FIRST und 5 MIDDLE ueber Herbal und Bio.",
        "counter": "Die direkte Doppelung in f10r_R2 ist als zweimal Bereitung sprachlich schwer; kein Beleg trennt Praeparat, Fluessigkeit, Posten oder formale Kategorie.",
    },
    "AL": {
        "id": "dd0ecaf5e27d81befffc",
        "v59": "AN?",
        "winner": "AN?",
        "rival1": "DORT?",
        "rival2": "DAZU?",
        "word_class": "PRAEPOSITION_ODER_RELATIONSPARTIKEL",
        "decision": "KEEP",
        "confidence": ".43",
        "historical_use": "Kurzer ad-locum-Bezug in bildadressierten Rezepten und Stationslisten; das Ziel wird aus Zeichnung oder laufender Rubrik ergaenzt.",
        "all_fit": "10/10 Kontexte koennen einen lokalen Zielbezug tragen; 4 FIRST, 3 MIDDLE, 2 LAST und 1 ONLY.",
        "counter": "FIRST-, LAST- und besonders das Ein-Karten-Feld verlangen ein unsichtbares Komplement; DORT als deiktisches Adverb waere dort grammatisch selbstaendiger.",
    },
    "EY": {
        "id": "b5df9126607030b95175",
        "v59": "KLAR?",
        "winner": "KLAR?",
        "rival1": "FERTIG?",
        "rival2": "SAUBER?",
        "word_class": "ZUSTANDSADJEKTIV",
        "decision": "KEEP",
        "confidence": ".39",
        "historical_use": "Qualitaetsprädikat clarus fuer geseihte Fluessigkeit oder klaren Lauf; in Rezepten als Schwellenzustand verwendbar.",
        "all_fit": "4/4 Kontexte lassen einen Klarheitszustand zu; 1 FIRST, 2 MIDDLE, 1 LAST auf einer Herbal- und zwei Bioeinheiten.",
        "counter": "f83r.39 steht zwischen abgemessenem Zusatz und Anteil ohne sichtbaren Klaervorgang; zwei von vier V51-Rollen hatten den Wert bereits abgelehnt.",
    },
    "OLOR": {
        "id": "dec401773c1f0347793d",
        "v59": "ZUVOR?",
        "winner": "VORIGES?",
        "rival1": "DAVON?",
        "rival2": "ZUVOR?",
        "word_class": "ANAPHORISCHES_PRONOMEN_ODER_SUBSTANTIVIERTES_ADJEKTIV",
        "decision": "REVISE",
        "confidence": ".36",
        "historical_use": "Anaphorische Rezeptkuerzung fuer praedictum/idem, das Vorige beziehungsweise Vorgenannte; verweist auf aktiven Ansatz statt nur auf fruehere Zeit.",
        "all_fit": "2/2 Kontexte verweisen auf einen vorigen Arbeitsbestand, einmal FIRST und einmal MIDDLE, je einmal Herbal und Bio.",
        "counter": "Nur zwei Belege und kein sichtbarer Antezedent; DAVON, ZUVOR und ein formaler Rueckverweis bleiben praktisch untrennbar.",
    },
    "OTCHEY": {
        "id": "faf321940aed922846a9",
        "v59": "TEIL?",
        "winner": "NIMM?",
        "rival1": "TEIL?",
        "rival2": "DIES?",
        "word_class": "REZEPTIMPERATIV",
        "decision": "REVISE",
        "confidence": ".44",
        "historical_use": "Als unteilbares Rezept-Ganzzeichen kann es eine recipe-/nimm-Formel vertreten; der folgende Bild- oder Recordkontext liefert das Objekt.",
        "all_fit": "2/2 Vorkommen stehen feldinitial und leiten eine Objekt-/Zustandsfolge ein; NIMM spart den in beiden lokalen Expansionen ohnehin ergaenzten Imperativ.",
        "counter": "Zwei Belege reichen nicht, um Handlung von markiertem Teil zu trennen; FRAME_OT kann eine formale Auswahl statt eines Verbs tragen.",
    },
    "OKEEY": {
        "id": "0275fbf14e07935b0a45",
        "v59": "WARM?",
        "winner": "WARM?",
        "rival1": "LAUWARM?",
        "rival2": "ERWÄRMEN?",
        "word_class": "TEMPERATURADJEKTIV",
        "decision": "KEEP",
        "confidence": ".52",
        "historical_use": "Temperaturstatus calidus/tepidus fuer Bad, Auflage oder Arbeitsfluessigkeit; als knapper Zustandsvermerk in einer Badezelle plausibel.",
        "all_fit": "7/7 Bio-Kontexte lassen einen warmen Zustand zu; 3 FIRST und 4 MIDDLE, haeufig vor SPUELEN oder VERWENDEN.",
        "counter": "Kein Herbal-Vorkommen und kein unabhaengiges Temperaturzeichen; technische Rivaltexte expandieren mehrere Stellen als Fuellen, Bewegen oder Weitergeben.",
    },
    "OKE": {
        "id": "7db18b2f0fb7ed0fcfd3",
        "v59": "SPÜLEN?",
        "winner": "SPÜLEN?",
        "rival1": "WASCHEN?",
        "rival2": "SCHLIESSEN?",
        "word_class": "HANDLUNGSVERB_IN_TERMINALFORMEL",
        "decision": "KEEP",
        "confidence": ".31",
        "historical_use": "Kurze lavare-/abluere-Handlung in Bade-, Wasch- oder Irrigationspraxis, fest mit dem lokalen Zellschluss kopiert.",
        "all_fit": "8/8 Bio-Vorkommen koennen einen Spuelgang abschliessen; 5 LAST, 3 ONLY und 8/8 formal TERMINAL.",
        "counter": "Absolute CLOSE-Konfundierung: Aus den Vorkommen laesst sich SPUELEN nicht von WASCHEN, irgendeiner Endhandlung oder bloss selektiertem Terminalwert isolieren.",
    },
    "LCHE": {
        "id": "de7321bface5628e35d6",
        "v59": "ABLASSEN?",
        "winner": "ABLASSEN?",
        "rival1": "LEEREN?",
        "rival2": "SCHLIESSEN?",
        "word_class": "HANDLUNGSVERB_IN_TERMINALFORMEL",
        "decision": "KEEP",
        "confidence": ".34",
        "historical_use": "Kurzes effundere-/evacuare-Konzept fuer verbrauchte Fluessigkeit oder ein Gefaess, stets gemeinsam mit Zellabschluss gelernt.",
        "all_fit": "8/8 Bio-Vorkommen koennen einen Ablassschritt tragen; 3 LAST, 5 ONLY und 8/8 formal TERMINAL.",
        "counter": "Absolute CLOSE-Konfundierung und kein sichtbarer Ablauf an jedem Ort; LEEREN oder ein anonymer terminaler Arbeitswert passt formal ebenso.",
    },
}


def guarded_rows(path: Path, columns: list[str], expected: int):
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in ALLOWED_PAGES:
        cmd.extend(["--allow", page])
    cmd.extend(["--columns", ",".join(columns), "--forbid-prefix", "f84"])
    proc = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    stdout_lines = proc.stdout.splitlines()
    stat_lines = [line for line in proc.stderr.splitlines() + stdout_lines if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise RuntimeError(f"missing guard stats for {path}")
    stats = json.loads(stat_lines[0][len("GUARD_STATS ") :])
    if stats["selected"] != expected or stats["skipped_forbidden"] != 0:
        raise RuntimeError(f"guard mismatch for {path}: {stats}")
    data_lines = [line for line in stdout_lines if not line.startswith("GUARD_STATS ")]
    rows = list(csv.DictReader(io.StringIO("\n".join(data_lines) + "\n"), delimiter="\t"))
    return rows, stats


def direct_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def file_sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def occurrence_pressure(card: str, row: dict[str, str], position: str):
    serial = int(row["event_serial"])
    if card == "AIIN":
        return "NO_VISIBLE_UNIT_OR_SCALE;SURFACE_DAIIN_STRICTER" if row["surface"] == "daiin" else "NO_VISIBLE_UNIT_OR_SCALE"
    if card == "OKY":
        return "OBJECT_SUPPLIED_BY_PICTURE_OR_ACTIVE_RECORD" + (";ELLIPTIC_ONLY_FIELD" if position == "ONLY" else "")
    if card == "CTHY":
        return "READINESS_NOT_INDEPENDENTLY_VISIBLE" + (";EARLY_BEFORE_PREPARATION_NOUN" if serial == 16 else "")
    if card == "OR":
        return "ADJACENT_DUPLICATION_PRESSURE" if serial in {33, 34} else "PREPARATION_VS_ITEM_UNRESOLVED"
    if card == "AL":
        return "MISSING_OVERT_COMPLEMENT" if position in {"FIRST", "LAST", "ONLY"} else "TARGET_IS_CONTEXT_SUPPLIED"
    if card == "EY":
        return "NO_CLEARING_PROCESS_IN_FIELD" if serial == 353 else "CLARITY_NOT_INDEPENDENTLY_VISIBLE"
    if card == "OLOR":
        return "ONLY_TWO_OCCURRENCES;ANTECEDENT_INHERITED"
    if card == "OTCHEY":
        return "ONLY_TWO_OCCURRENCES;IMPERATIVE_VS_MARKED_PART_UNRESOLVED"
    if card == "OKEEY":
        return "BIO_LOCAL;TEMPERATURE_NOT_INDEPENDENTLY_VISIBLE"
    if card in {"OKE", "LCHE"}:
        return "ABSOLUTE_CLOSE_CONFOUND"
    raise KeyError(card)


def context_grade(card: str, row: dict[str, str], position: str):
    if card in {"OKE", "LCHE"}:
        return "COMPATIBLE_ONLY_AS_CLOSE_CONFOUNDED_LOCAL_ACTION"
    if card == "AL" and position in {"FIRST", "LAST", "ONLY"}:
        return "COMPATIBLE_ONLY_WITH_ELLIPTIC_PICTURE_OR_RECORD_COMPLEMENT"
    if card == "OR" and int(row["event_serial"]) in {33, 34}:
        return "COMPATIBLE_BUT_ADJACENT_REPETITION_AWKWARD"
    if card == "EY" and int(row["event_serial"]) == 353:
        return "WEAK_CONTEXTUAL_FIT"
    if card in {"OLOR", "OTCHEY"}:
        return "COMPATIBLE_AND_SUPPORTS_REVISION_BUT_N_IS_TWO"
    return "COMPATIBLE_AT_SELECTED_BROAD_CONCEPT_LEVEL"


def main():
    dictionary_path = BASE / "V59_R1_FINAL_173_CARD_DICTIONARY.tsv"
    events_path = BASE / "V59_R1_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
    fields_path = BASE / "V59_R1_FINAL_135_FIELD_EDITION.tsv"
    validation_path = BASE / "V59_R1_VALIDATION.json"

    dictionary = direct_rows(dictionary_path)
    with validation_path.open(encoding="utf-8") as handle:
        base_validation = json.load(handle)
    if base_validation["status"] != "PASS" or len(dictionary) != 173:
        raise RuntimeError("canonical V59 R1 baseline is not valid")

    event_columns = [
        "event_serial", "page", "locus", "record", "record_unit_id", "field_id",
        "field_ordinal_in_locus", "event_index_in_locus", "event_index_in_record",
        "surface", "joint_tuple_id", "formal_formula_opaque", "FORMAL_VALUE",
        "terminal_status", "strict_control_prompt", "ATOMIC_OR_WHOLE_CARD_MNEMONIC",
        "mnemonic_scope", "LOCAL_IATROMEDICAL_EXPANSION", "NONMEDICAL_RIVAL",
        "UNKNOWN_EXEMPLAR_STATUS", "source_lineage",
    ]
    field_columns = [
        "field_serial", "field_id", "page", "record", "record_unit_id", "locus",
        "field_ordinal_in_locus", "field_ordinal_in_record", "event_count",
        "surface_sequence", "formal_sequence_opaque", "FORMAL_VALUE",
        "ATOMIC_OR_WHOLE_CARD_MNEMONIC", "LOCAL_IATROMEDICAL_EXPANSION",
        "NONMEDICAL_RIVAL", "UNKNOWN_EXEMPLAR_STATUS", "closure_status", "source_lineage",
    ]
    events, event_guard = guarded_rows(events_path, event_columns, 381)
    fields, field_guard = guarded_rows(fields_path, field_columns, 135)
    field_by_id = {row["field_id"]: row for row in fields}
    events_by_field = defaultdict(list)
    for row in events:
        events_by_field[row["field_id"]].append(row)

    id_to_card = {item["id"]: card for card, item in DECISIONS.items()}
    if len(id_to_card) != 11:
        raise RuntimeError("target IDs are not unique")

    baseline_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    for card, item in DECISIONS.items():
        row = baseline_by_id.get(item["id"])
        if row is None or row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != item["v59"]:
            raise RuntimeError(f"baseline mismatch for {card}")

    observed = Counter(row["joint_tuple_id"] for row in events if row["joint_tuple_id"] in id_to_card)
    expected_counts = {item["id"]: int(baseline_by_id[item["id"]]["occurrences"]) for item in DECISIONS.values()}
    if dict(observed) != expected_counts or sum(observed.values()) != 85:
        raise RuntimeError(f"target occurrence mismatch: {observed}")

    positions = Counter()
    terminals = Counter()
    pages = defaultdict(set)
    units = defaultdict(set)
    occurrence_rows = []
    for row in events:
        card = id_to_card.get(row["joint_tuple_id"])
        if card is None:
            continue
        siblings = events_by_field[row["field_id"]]
        index = next(i for i, sibling in enumerate(siblings) if sibling["event_serial"] == row["event_serial"])
        if len(siblings) == 1:
            position = "ONLY"
        elif index == 0:
            position = "FIRST"
        elif index == len(siblings) - 1:
            position = "LAST"
        else:
            position = "MIDDLE"
        previous = "<FIELD_START>" if index == 0 else (
            siblings[index - 1]["surface"] + ":" + siblings[index - 1]["LOCAL_IATROMEDICAL_EXPANSION"]
        )
        following = "<FIELD_END>" if index == len(siblings) - 1 else (
            siblings[index + 1]["surface"] + ":" + siblings[index + 1]["LOCAL_IATROMEDICAL_EXPANSION"]
        )
        item = DECISIONS[card]
        positions[(card, position)] += 1
        terminals[(card, row["terminal_status"])] += 1
        pages[card].add(row["page"])
        units[card].add(row["record_unit_id"])
        occurrence_rows.append({
            "card": card,
            "joint_tuple_id": row["joint_tuple_id"],
            "v59_mnemonic": item["v59"],
            "v60_r2_winner": item["winner"],
            "rival_1": item["rival1"],
            "rival_2": item["rival2"],
            "event_serial": row["event_serial"],
            "page": row["page"],
            "locus": row["locus"],
            "record_unit_id": row["record_unit_id"],
            "field_id": row["field_id"],
            "field_position": position,
            "event_index_in_record": row["event_index_in_record"],
            "terminal_status": row["terminal_status"],
            "surface": row["surface"],
            "field_surface_sequence": field_by_id[row["field_id"]]["surface_sequence"],
            "previous_local_context": previous,
            "target_local_iatromedical_expansion": row["LOCAL_IATROMEDICAL_EXPANSION"],
            "next_local_context": following,
            "whole_field_iatromedical_expansion": field_by_id[row["field_id"]]["LOCAL_IATROMEDICAL_EXPANSION"],
            "whole_field_nonmedical_rival": field_by_id[row["field_id"]]["NONMEDICAL_RIVAL"],
            "winner_context_assessment": context_grade(card, row, position),
            "strongest_occurrence_pressure": occurrence_pressure(card, row, position),
            "scope_rule": "EXACT_ID_ONLY;LOCAL_EXPANSIONS_ARE_CONTEXT_NOT_CARD_EVIDENCE",
        })
    occurrence_rows.sort(key=lambda row: int(row["event_serial"]))
    write_tsv(OUT_DIR / "V60_R2_85_OCCURRENCE_AUDIT.tsv", list(occurrence_rows[0]), occurrence_rows)

    decision_rows = []
    for card in ("AIIN", "OKY", "CTHY", "OR", "AL", "EY", "OLOR", "OTCHEY", "OKEEY", "OKE", "LCHE"):
        item = DECISIONS[card]
        decision_rows.append({
            "card": card,
            "joint_tuple_id": item["id"],
            "occurrences": str(observed[item["id"]]),
            "pages": "|".join(sorted(pages[card])),
            "record_units": "|".join(sorted(units[card])),
            "position_census": ";".join(
                f"{name}={positions[(card, name)]}" for name in ("FIRST", "MIDDLE", "LAST", "ONLY")
            ),
            "terminal_occurrences": str(terminals[(card, "TERMINAL")]),
            "v59_r1_mnemonic": item["v59"],
            "v60_r2_winner": item["winner"],
            "rival_1": item["rival1"],
            "rival_2": item["rival2"],
            "source_word_class": item["word_class"],
            "decision": item["decision"],
            "all_occurrence_context_result": item["all_fit"],
            "historical_workshop_use": item["historical_use"],
            "strongest_counterevidence": item["counter"],
            "confidence": item["confidence"],
            "binding_rule": "UNSPLIT_EXACT_CARD_ONLY;NO_PAGE_HOST_OR_SUBSTRING_SEMANTICS",
        })
    write_tsv(OUT_DIR / "V60_R2_EXACT_CARD_DECISIONS.tsv", list(decision_rows[0]), decision_rows)

    revised_dictionary = []
    for row in dictionary:
        out = dict(row)
        old = row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        card = id_to_card.get(row["joint_tuple_id"])
        if card is None:
            out.update({
                "V59_R1_MNEMONIC": old,
                "V60_R2_WORD_CLASS": "NOT_TARGETED",
                "V60_R2_RIVAL_1": "NOT_TARGETED",
                "V60_R2_RIVAL_2": "NOT_TARGETED",
                "V60_R2_DECISION": "UNCHANGED_NOT_TARGETED",
                "V60_R2_CONFIDENCE": "NOT_TARGETED",
            })
            out["source_lineage"] = row["source_lineage"] + ">V60_R2_UNCHANGED"
        else:
            item = DECISIONS[card]
            out["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] = item["winner"]
            out.update({
                "V59_R1_MNEMONIC": old,
                "V60_R2_WORD_CLASS": item["word_class"],
                "V60_R2_RIVAL_1": item["rival1"],
                "V60_R2_RIVAL_2": item["rival2"],
                "V60_R2_DECISION": item["decision"],
                "V60_R2_CONFIDENCE": item["confidence"],
            })
            out["source_lineage"] = row["source_lineage"] + ">V60_R2_EXACT_CARD_COMPETITION"
        revised_dictionary.append(out)
    dictionary_fields = list(dictionary[0])
    insert_at = dictionary_fields.index("ATOMIC_OR_WHOLE_CARD_MNEMONIC")
    dictionary_fields[insert_at:insert_at] = ["V59_R1_MNEMONIC"]
    dictionary_fields.extend([
        "V60_R2_WORD_CLASS", "V60_R2_RIVAL_1", "V60_R2_RIVAL_2",
        "V60_R2_DECISION", "V60_R2_CONFIDENCE",
    ])
    write_tsv(OUT_DIR / "V60_R2_REVISED_173_CARD_DICTIONARY.tsv", dictionary_fields, revised_dictionary)

    revised_events = []
    changed_event_count = 0
    for row in events:
        out = dict(row)
        old = row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        card = id_to_card.get(row["joint_tuple_id"])
        if card is None:
            out.update({
                "V59_R1_MNEMONIC": old,
                "V60_R2_WORD_CLASS": "NOT_TARGETED",
                "V60_R2_DECISION": "UNCHANGED_NOT_TARGETED",
                "V60_R2_CONFIDENCE": "NOT_TARGETED",
            })
            out["source_lineage"] = row["source_lineage"] + ">V60_R2_UNCHANGED"
        else:
            item = DECISIONS[card]
            out["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] = item["winner"]
            out.update({
                "V59_R1_MNEMONIC": old,
                "V60_R2_WORD_CLASS": item["word_class"],
                "V60_R2_DECISION": item["decision"],
                "V60_R2_CONFIDENCE": item["confidence"],
            })
            out["source_lineage"] = row["source_lineage"] + ">V60_R2_EXACT_CARD_COMPETITION"
            changed_event_count += int(item["winner"] != old)
        revised_events.append(out)
    event_fields = list(events[0])
    event_insert_at = event_fields.index("ATOMIC_OR_WHOLE_CARD_MNEMONIC")
    event_fields[event_insert_at:event_insert_at] = ["V59_R1_MNEMONIC"]
    event_fields.extend(["V60_R2_WORD_CLASS", "V60_R2_DECISION", "V60_R2_CONFIDENCE"])
    write_tsv(OUT_DIR / "V60_R2_REVISED_381_EVENT_LEDGER.tsv", event_fields, revised_events)

    output_paths = {
        "decisions": OUT_DIR / "V60_R2_EXACT_CARD_DECISIONS.tsv",
        "occurrences": OUT_DIR / "V60_R2_85_OCCURRENCE_AUDIT.tsv",
        "dictionary": OUT_DIR / "V60_R2_REVISED_173_CARD_DICTIONARY.tsv",
        "events": OUT_DIR / "V60_R2_REVISED_381_EVENT_LEDGER.tsv",
    }
    winner_counts = Counter(row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] for row in revised_events if row["joint_tuple_id"] in id_to_card)
    expected_winner_counts = {DECISIONS[card]["winner"]: observed[DECISIONS[card]["id"]] for card in DECISIONS}
    validation = {
        "status": "PASS",
        "role": "R2_HISTORICAL_MEDICAL_HERBAL_SCRIBE",
        "scope": {
            "target_exact_cards": 11,
            "target_occurrences": 85,
            "canonical_dictionary_cards": 173,
            "canonical_prose_events": 381,
            "allowed_pages": list(ALLOWED_PAGES),
        },
        "counts": {
            "decision_rows": len(decision_rows),
            "occurrence_audit_rows": len(occurrence_rows),
            "revised_dictionary_rows": len(revised_dictionary),
            "revised_event_rows": len(revised_events),
            "kept_cards": sum(item["decision"] == "KEEP" for item in DECISIONS.values()),
            "revised_cards": sum(item["decision"] == "REVISE" for item in DECISIONS.values()),
            "events_with_changed_mnemonic": changed_event_count,
            "events_with_unchanged_target_mnemonic": 85 - changed_event_count,
            "non_target_events_unchanged": 381 - 85,
        },
        "per_card_occurrences": {card: observed[item["id"]] for card, item in DECISIONS.items()},
        "winner_event_counts": dict(sorted(winner_counts.items())),
        "expected_winner_event_counts": dict(sorted(expected_winner_counts.items())),
        "guards": {
            "event_query": event_guard,
            "field_query": field_guard,
            "forbidden_prefix": "f84",
            "v60_sibling_files_read": 0,
            "new_voynich_pages_opened": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
        "assertions": {
            "exact_id_binding_only": True,
            "page_host_semantics_absent": True,
            "substring_semantics_absent": True,
            "sound_or_language_assignment_absent": True,
            "each_card_has_one_winner_and_two_one_token_rivals": all(
                len(item["winner"].split()) == len(item["rival1"].split()) == len(item["rival2"].split()) == 1
                for item in DECISIONS.values()
            ),
            "formal_values_unchanged": all(
                revised_events[i]["FORMAL_VALUE"] == events[i]["FORMAL_VALUE"] for i in range(381)
            ),
            "local_iatromedical_expansions_unchanged": all(
                revised_events[i]["LOCAL_IATROMEDICAL_EXPANSION"] == events[i]["LOCAL_IATROMEDICAL_EXPANSION"]
                for i in range(381)
            ),
            "nonmedical_rivals_unchanged": all(
                revised_events[i]["NONMEDICAL_RIVAL"] == events[i]["NONMEDICAL_RIVAL"] for i in range(381)
            ),
            "surface_and_exact_ids_unchanged": all(
                revised_events[i]["surface"] == events[i]["surface"]
                and revised_events[i]["joint_tuple_id"] == events[i]["joint_tuple_id"]
                for i in range(381)
            ),
            "winner_counts_match_expected": dict(winner_counts) == expected_winner_counts,
        },
        "source_sha256": {
            "v59_r1_dictionary": file_sha256(dictionary_path),
            "v59_r1_events": file_sha256(events_path),
            "v59_r1_fields": file_sha256(fields_path),
            "v59_r1_validation": file_sha256(validation_path),
        },
        "output_sha256": {name: file_sha256(path) for name, path in output_paths.items()},
        "decision": "KEEP_NINE__REVISE_OLOR_TO_VORIGES__REVISE_OTCHEY_TO_NIMM",
    }
    expected_counts_summary = {
        "decision_rows": 11,
        "occurrence_audit_rows": 85,
        "revised_dictionary_rows": 173,
        "revised_event_rows": 381,
        "kept_cards": 9,
        "revised_cards": 2,
        "events_with_changed_mnemonic": 4,
        "events_with_unchanged_target_mnemonic": 81,
        "non_target_events_unchanged": 296,
    }
    if validation["counts"] != expected_counts_summary:
        raise RuntimeError(f"count mismatch: {validation['counts']}")
    if not all(validation["assertions"].values()):
        raise RuntimeError(f"assertion failure: {validation['assertions']}")
    with (OUT_DIR / "V60_R2_VALIDATION.json").open("w", encoding="utf-8") as handle:
        json.dump(validation, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
