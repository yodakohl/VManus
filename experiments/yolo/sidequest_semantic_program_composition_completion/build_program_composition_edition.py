#!/usr/bin/env python3
"""Build the creative compositional analysis of the 28 terminal program cards."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_variant_selector_completion"

DICT_IN = BASE / "SELECTED_173_VARIANT_SELECTOR_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_VARIANT_SELECTOR_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_VARIANT_SELECTOR_SENTENCES.tsv"
PROGRAM_IN = BASE / "PROGRAM_CARD_DECK.tsv"

DICT_OUT = HERE / "SELECTED_173_PROGRAM_COMPOSITION_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_PROGRAM_COMPOSITION_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_PROGRAM_COMPOSITION_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_PROGRAM_COMPOSITION_RECORDS.md"
REGISTER_OUT = HERE / "PROGRAM_COMPOSITION_REGISTER.tsv"
COMPONENT_OUT = HERE / "PROGRAM_COMPONENT_LEXICON.tsv"
FAMILY_OUT = HERE / "PROGRAM_FAMILY_GRID.tsv"
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


COMPONENTS = {
    "CORE_OK": ("OPERATION", "Arbeitsgang ansetzen", "Setzt den folgenden Kern oder Posten in den laufenden Arbeitsgang."),
    "CORE_CHED": ("OPERATION", "umsetzen", "CHD~CHED führt einen Posten in die nächste Arbeitsposition."),
    "CORE_SHED": ("OPERATION", "absetzen", "Lässt den aktuellen Posten ruhen oder sich absetzen."),
    "CORE_CKHE": ("OPERATION", "seihen", "Führt den Posten durch einen Durchlass oder Seihweg."),
    "CORE_CHK": ("OPERATION", "wärmen", "Markiert den lokalen Wärmegang; nicht mit CKHE verwechseln."),
    "CORE_OLK": ("OPERATION", "sammeln", "Hält oder sammelt den Posten an der lokalen Sammelstelle."),
    "DIR_L": ("DIRECTION", "nach außen", "Macht aus CHED/CKHE einen Auswärts-, Ablass- oder Abseihgang."),
    "DIR_P": ("DIRECTION", "nach innen", "Führt CHED zum lokalen Empfänger oder in die Arbeitsstelle."),
    "TARGET_AL": ("ADDRESS", "zur Zielstelle", "Bindet den Arbeitsgang an die bezeichnete Stelle."),
    "ORDER_OL": ("ORDER", "weiter", "Setzt denselben Arbeitsgang oder Vorposten fort."),
    "ORDER_OT": ("ORDER", "danach", "Wählt die folgende lokale Ausführung."),
    "MEDIUM_AIR": ("MEDIUM", "Wasserlauf", "Bezeichnet in dieser Ausgabe den laufenden Flüssigkeitsweg."),
    "GRADE_E": ("GRADE", "kurz", "Kurzer oder direkter Kontakt-/Folgegrad in lizenzierten Reihen."),
    "GRADE_EE": ("GRADE", "länger", "Anhaltender Kontakt-/Folgegrad in lizenzierten Reihen."),
    "CLOSE_EXACT": ("ENDPOINT", "Zelle schließen", "Formale Rolle der ganzen exakten Karte; kein global abtrennbares DY-Suffix."),
}


def comp(
    status: str,
    parse: str,
    components: str,
    core: str,
    order_direction: str,
    grade: str,
    reading: str,
    rationale: str,
    exception: str,
) -> dict[str, str]:
    return {
        "composition_status": status,
        "component_parse": parse,
        "component_ids": components,
        "action_core_de": core,
        "order_direction_de": order_direction,
        "grade_de": grade,
        "close_construction": "EXACT_CARD_CLOSE",
        "ignored_surface_elements": "RENDERER/FRAME AS MARKED IN PARSE" if "renderer" in parse or "frame" in parse else "KEINE",
        "composed_reading_de": reading,
        "composition_rationale_de": rationale,
        "exception_note_de": exception,
    }


# Keys are exact tuple IDs, never raw surface strings. Visible q/s/d/t wrappers are
# ignored only where alternate surfaces of the same exact card already demand it.
COMPOSITIONS = {
    "04a3877f0fc81b7597c9": comp("LICENSED_PARTIAL", "L + [ABZIEHEN] + CLOSE_EXACT", "DIR_L|CLOSE_EXACT", "gelernter Abziehbefehl", "nach außen", "KEIN", "nach außen abziehen; schließen", "L liefert nur die Auswärtsrichtung; die eigentliche Abziehhandlung bleibt gelernt.", "Kein sichtbarer CHED- oder CKHE-Kern."),
    "1b1ffdd869fb1429ad03": comp("PRODUCTIVE_COMPOSITION", "OL + CLOSE_EXACT", "ORDER_OL|CLOSE_EXACT", "fortsetzen", "weiter", "KEIN", "fortsetzen; schließen", "OL trägt den Fortsetzungswert auch außerhalb dieser Karte.", "Die Handlung ist im Ordnungsoperator selbst enthalten."),
    "259b2b3b0bf859882e2c": comp("PRODUCTIVE_COMPOSITION", "[S/D/T renderer] + CHED + CLOSE_EXACT", "CORE_CHED|CLOSE_EXACT", "umsetzen", "KEIN", "KEIN", "umsetzen; schließen", "Drei sichtbare Anlaute gehören derselben exakten Karte; CHED ist der gemeinsame Arbeitskern.", "S/D/T erhalten hier keinen eigenen Wert."),
    "28ffbc88b97772a75f1e": comp("PRODUCTIVE_COMPOSITION", "[Q renderer] + OL + CHED + CLOSE_EXACT", "ORDER_OL|CORE_CHED|CLOSE_EXACT", "umsetzen", "weiter", "KEIN", "weiter umsetzen; schließen", "OL und CHED sind unabhängig wiederkehrende Beiträge.", "Q ist innerhalb derselben exakten Karte wechselnd."),
    "2bc2ed2630dbdaaa6b59": comp("PRODUCTIVE_COMPOSITION", "[D frame] + AL + CHD + CLOSE_EXACT", "TARGET_AL|CORE_CHED|CLOSE_EXACT", "umsetzen", "zur Zielstelle", "KEIN", "zur Zielstelle umsetzen; schließen", "AL bindet die Zielstelle, CHD den Transfer.", "Der sichtbare D-Rahmen bekommt keinen Zusatzwert."),
    "3b70942557b3a40e8030": comp("PRODUCTIVE_COMPOSITION", "OLK + EE + CLOSE_EXACT", "CORE_OLK|GRADE_EE|CLOSE_EXACT", "sammeln", "KEIN", "länger", "länger sammeln; schließen", "OLK ist die Sammelstellenkarte, EE der lange Grad.", "OLK wird hier als ganzer Kern behandelt, nicht OL+K."),
    "4de12cf322dfb76ded1e": comp("PRODUCTIVE_COMPOSITION", "[Q renderer] + OT + CHED + CLOSE_EXACT", "ORDER_OT|CORE_CHED|CLOSE_EXACT", "umsetzen", "danach", "KEIN", "danach umsetzen; schließen", "OT liefert Folge, CHED Transfer.", "Q ist ohne eigenen Wert."),
    "54e32e9c1414b20640e9": comp("MEMORIZED_WHOLE_CARD", "[SCHWENKEN-GANZKARTE] + CLOSE_EXACT", "CLOSE_EXACT", "schwenken", "KEIN", "KEIN", "schwenken; schließen", "Ein einmaliger, stationsgebundener Spezialbefehl.", "SSHK/CHD wird nicht erzwungen zerlegt."),
    "601b77449028deed39de": comp("PRODUCTIVE_COMPOSITION", "OT + CHD + CLOSE_EXACT", "ORDER_OT|CORE_CHED|CLOSE_EXACT", "umsetzen", "danach", "KEIN", "danach umsetzen; schließen", "Kurze CHD-Realisierung derselben OT-Transferreihe.", "Kein eigener Wert für sichtbares H."),
    "65df3cd9e59060042d47": comp("PRODUCTIVE_COMPOSITION", "P + CHED + CLOSE_EXACT", "DIR_P|CORE_CHED|CLOSE_EXACT", "umsetzen", "nach innen", "KEIN", "in den Empfänger führen; schließen", "P bildet die Gegenrichtung zu L innerhalb des CHED-Rasters.", "P ist dünn belegt und bleibt auf diese Reihe beschränkt."),
    "78b3b3140714da19090d": comp("LICENSED_PARTIAL", "[D frame] + AL + [NEBENÖFFNUNG] + CLOSE_EXACT", "TARGET_AL|CLOSE_EXACT", "gelernte Öffnungshandlung", "an der Zielstelle", "KEIN", "Nebenöffnung an der Zielstelle setzen; schließen", "AL liefert nur die Ortsbindung.", "Die Öffnungshandlung besitzt keinen unabhängigen Kern."),
    "7d25241b0e56c836372a": comp("PRODUCTIVE_COMPOSITION", "[Q renderer] + OK + EE + CLOSE_EXACT", "CORE_OK|GRADE_EE|CLOSE_EXACT", "Arbeitsgang ansetzen", "KEIN", "länger", "länger ansetzen; schließen", "Direkter Partner von OK+E+CLOSE.", "EE bezeichnet keine genaue Zeit."),
    "7db18b2f0fb7ed0fcfd3": comp("PRODUCTIVE_COMPOSITION", "[Q renderer] + OK + E + CLOSE_EXACT", "CORE_OK|GRADE_E|CLOSE_EXACT", "Arbeitsgang ansetzen", "KEIN", "kurz", "kurz ansetzen; schließen", "Direkter Partner von OK+EE+CLOSE.", "E ist nur in diesem lizenzierten Rahmen ein Grad."),
    "7f68f60279efe6b28cd7": comp("MEMORIZED_WHOLE_CARD", "[WASCHUNG-GANZKARTE] + CLOSE_EXACT", "CLOSE_EXACT", "waschen", "KEIN", "KEIN", "Waschung ausführen; schließen", "Der Kartenwert widerspricht einer mechanischen SHED=Absetzen-Zerlegung.", "R bleibt ohne produktiven Beitrag."),
    "87411f84689b4f93a303": comp("PRODUCTIVE_COMPOSITION", "[Q renderer] + OK + CHD + CLOSE_EXACT", "CORE_OK|CORE_CHED|CLOSE_EXACT", "umsetzen", "Arbeitsgang ansetzen", "KEIN", "Umsetzgang ansetzen; schließen", "OK aktiviert den CHD-Transferkern.", "Q ist ohne eigenen Wert."),
    "8aedd154964a78e555d6": comp("LICENSED_PARTIAL", "[D frame] + AIR + [LAUF SCHLIESSEN] + CLOSE_EXACT", "MEDIUM_AIR|CLOSE_EXACT", "gelernte Lauf-Schließung", "am Wasserlauf", "KEIN", "Wasserlauf schließen", "AIR bezeichnet den Lauf; die Schließhandlung bleibt Teil der Ganzkarte.", "Das innere Y/DY wird nicht mechanisch zerlegt."),
    "a84fbe3ad380df345b97": comp("PRODUCTIVE_COMPOSITION", "CHK + EE + CLOSE_EXACT", "CORE_CHK|GRADE_EE|CLOSE_EXACT", "wärmen", "KEIN", "länger", "länger wärmen; schließen", "CHK bleibt vom umgestellten CKHE-Seihkern getrennt.", "Nur die lange Stufe ist in diesem Programmsatz belegt."),
    "b958a512ca6a3559e86e": comp("MEMORIZED_WHOLE_CARD", "[NACHWASCHEN-GANZKARTE] + CLOSE_EXACT", "CLOSE_EXACT", "nachwaschen", "KEIN", "KEIN", "nachwaschen; schließen", "Ein einzelner gelernter Waschbefehl.", "LK und E werden mangels eigener Reihe nicht abgetrennt."),
    "bc4f1f5c006c74a4d26d": comp("PRODUCTIVE_COMPOSITION", "[S/T renderer] + SHED + CLOSE_EXACT", "CORE_SHED|CLOSE_EXACT", "absetzen", "KEIN", "KEIN", "absetzen; schließen", "Zwölf Vorkommen derselben exakten Absetzkarte stützen den Kern.", "S/T sind Oberflächenrahmen derselben Karte."),
    "c1db6b0a28d5cbb5d3d2": comp("PRODUCTIVE_COMPOSITION", "L + CKHE + CLOSE_EXACT", "DIR_L|CORE_CKHE|CLOSE_EXACT", "seihen", "nach außen", "KEIN", "nach außen abseihen; schließen", "L spezifiziert den Ausgang des CKHE-Seihgangs.", "CHE gehört hier zum CKHE-Kern."),
    "c45ebac60774620561e2": comp("PRODUCTIVE_COMPOSITION", "OT + E + CLOSE_EXACT", "ORDER_OT|GRADE_E|CLOSE_EXACT", "Folge ausführen", "danach", "kurz", "kurze Folge; schließen", "Direkter Partner von OT+EE+CLOSE.", "Kein bestimmter Stoff oder Gegenstand ist enthalten."),
    "d68bc8de3bcee09db23c": comp("PRODUCTIVE_COMPOSITION", "[SH renderer] + CKHE + CLOSE_EXACT", "CORE_CKHE|CLOSE_EXACT", "seihen", "KEIN", "KEIN", "seihen; schließen", "CKHE ist der wiederkehrende Seihkern; SH bleibt Hülle.", "Nicht als SHED+CHD lesen."),
    "daa1347f456415fe8737": comp("PRODUCTIVE_COMPOSITION", "[S renderer] + OL + SHED + CLOSE_EXACT", "ORDER_OL|CORE_SHED|CLOSE_EXACT", "absetzen", "weiter", "KEIN", "weiter absetzen; schließen", "OL setzt den bereits laufenden SHED-Gang fort.", "Die sichtbare S-Grenze trägt keinen Zusatzwert."),
    "db167f8e9b53eefb58f8": comp("PRODUCTIVE_COMPOSITION", "[Q renderer] + OK + SHED + CLOSE_EXACT", "CORE_OK|CORE_SHED|CLOSE_EXACT", "absetzen", "Arbeitsgang ansetzen", "KEIN", "Absetzgang ansetzen; schließen", "OK aktiviert den SHED-Kern.", "Kein Wärmebeitrag."),
    "de7321bface5628e35d6": comp("PRODUCTIVE_COMPOSITION", "L + CHED + CLOSE_EXACT", "DIR_L|CORE_CHED|CLOSE_EXACT", "umsetzen", "nach außen", "KEIN", "abführen; schließen", "Stärkste Richtungsbildung des CHED-Rasters.", "Ablassen ist die lokale natürliche Ausführung von L+CHED."),
    "eb2e4bc143f623ee03ac": comp("MEMORIZED_WHOLE_CARD", "[BEFESTIGEN-GANZKARTE] + CLOSE_EXACT", "CLOSE_EXACT", "befestigen", "KEIN", "KEIN", "befestigen; schließen", "Ein einmaliger Apparate-/Auflagenbefehl.", "OK/Y/LDDY wird nicht rückwirkend zu einer freien Regel gemacht."),
    "f2af6326898fb5b490a4": comp("LICENSED_PARTIAL", "L + [REST-SELEKTOR O] + CHED + CLOSE_EXACT", "DIR_L|CORE_CHED|CLOSE_EXACT", "umsetzen", "nach außen; Rest", "KEIN", "Rest abführen; schließen", "L+CHED liefert Abführung; der Restwert bleibt ein gelernter Selektor.", "O wird nicht global als REST promoviert."),
    "ff178343c18e287ce3b7": comp("PRODUCTIVE_COMPOSITION", "[Q renderer] + OT + EE + CLOSE_EXACT", "ORDER_OT|GRADE_EE|CLOSE_EXACT", "Folge ausführen", "danach", "länger", "lange Folge; schließen", "Direkter Partner von OT+E+CLOSE.", "Q ist ohne eigenen Wert."),
}


FAMILIES = {
    "SET_GRADE": ("OK + E/EE + Schluss", "kurz oder länger ansetzen", ["7db18b2f0fb7ed0fcfd3", "7d25241b0e56c836372a"]),
    "FOLLOW_GRADE": ("OT + E/EE + Schluss", "kurze oder lange Folge", ["c45ebac60774620561e2", "ff178343c18e287ce3b7"]),
    "TRANSFER_GRID": ("Richtung/Folge + CHD~CHED + Schluss", "umsetzen, einführen, fortsetzen oder abführen", ["259b2b3b0bf859882e2c", "28ffbc88b97772a75f1e", "4de12cf322dfb76ded1e", "601b77449028deed39de", "65df3cd9e59060042d47", "87411f84689b4f93a303", "de7321bface5628e35d6", "2bc2ed2630dbdaaa6b59", "1b1ffdd869fb1429ad03"]),
    "SETTLING_GRID": ("OK/OL + SHED + Schluss", "absetzen, ansetzen oder weiter absetzen", ["bc4f1f5c006c74a4d26d", "db167f8e9b53eefb58f8", "daa1347f456415fe8737"]),
    "STRAIN_GRID": ("L oder Renderer + CKHE + Schluss", "seihen oder nach außen abseihen", ["d68bc8de3bcee09db23c", "c1db6b0a28d5cbb5d3d2"]),
    "PROCESS_GRADE": ("CHK/OLK + EE + Schluss", "länger wärmen oder sammeln", ["a84fbe3ad380df345b97", "3b70942557b3a40e8030"]),
    "PARTIAL_ADDRESS": ("bekannte Adresse + gelernter Innenwert + Schluss", "Abziehen, Nebenöffnung, Lauf schließen, Rest abführen", ["04a3877f0fc81b7597c9", "78b3b3140714da19090d", "8aedd154964a78e555d6", "f2af6326898fb5b490a4"]),
    "MEMORIZED_SPECIAL": ("unteilbare Spezialkarte + Schlussrolle", "Schwenken, Waschung, Nachwaschen, Befestigen", ["54e32e9c1414b20640e9", "7f68f60279efe6b28cd7", "b958a512ca6a3559e86e", "eb2e4bc143f623ee03ac"]),
}


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentences = read_tsv(SENTENCE_IN)
    programs = read_tsv(PROGRAM_IN)
    if (len(dictionary), len(events), len(sentences), len(programs)) != (173, 381, 116, 28):
        raise AssertionError("unexpected input dimensions")
    if {row["program_card_id"] for row in programs} != set(COMPOSITIONS):
        raise AssertionError("composition map must cover exactly the 28 program cards")

    event_count_by_card = Counter(row["joint_tuple_id"] for row in events)
    program_count_by_card = {row["program_card_id"]: int(row["occurrence_count"]) for row in programs}
    program_by_card = {row["program_card_id"]: row for row in programs}

    register_rows: list[dict[str, str]] = []
    for source in programs:
        card_id = source["program_card_id"]
        item = COMPOSITIONS[card_id]
        register_rows.append({
            **source,
            "all_ten_page_occurrences": str(event_count_by_card[card_id]),
            **item,
        })

    component_rows: list[dict[str, str]] = []
    for component_id, (component_type, value_de, rule_de) in COMPONENTS.items():
        cards = [row for row in register_rows if component_id in row["component_ids"].split("|")]
        component_rows.append({
            "component_id": component_id,
            "component_type": component_type,
            "value_de": value_de,
            "program_card_types": str(len(cards)),
            "all_ten_page_occurrences": str(sum(int(row["all_ten_page_occurrences"]) for row in cards)),
            "variant_selector_uses": str(sum(int(row["occurrence_count"]) for row in cards)),
            "program_cards": "|".join(row["surfaces"] for row in cards),
            "teaching_rule_de": rule_de,
        })

    family_rows: list[dict[str, str]] = []
    for family_id, (pattern, command, card_ids) in FAMILIES.items():
        rows_here = [next(row for row in register_rows if row["program_card_id"] == card_id) for card_id in card_ids]
        family_rows.append({
            "family_id": family_id,
            "productive_pattern": pattern,
            "apprentice_command_de": command,
            "program_card_types": str(len(rows_here)),
            "all_ten_page_occurrences": str(sum(int(row["all_ten_page_occurrences"]) for row in rows_here)),
            "variant_selector_uses": str(sum(int(row["occurrence_count"]) for row in rows_here)),
            "surfaces": "|".join(row["surfaces"] for row in rows_here),
            "status_inventory": "|".join(dict.fromkeys(row["composition_status"] for row in rows_here)),
        })

    out_dictionary: list[dict[str, str]] = []
    for original in dictionary:
        row = dict(original)
        item = COMPOSITIONS.get(row["joint_tuple_id"])
        if item:
            row["program_composition_status"] = item["composition_status"]
            row["program_composition_parse"] = item["component_parse"]
            row["program_component_ids"] = item["component_ids"]
            row["program_composed_reading_de"] = item["composed_reading_de"]
            row["program_composition_note"] = item["exception_note_de"]
        else:
            row["program_composition_status"] = "NOT_IN_28_CARD_PROGRAM_DECK"
            row["program_composition_parse"] = "NOT_APPLICABLE"
            row["program_component_ids"] = "NOT_APPLICABLE"
            row["program_composed_reading_de"] = "NOT_APPLICABLE"
            row["program_composition_note"] = "Kartenwert dieser Runde nicht neu zerlegt."
        out_dictionary.append(row)

    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        item = COMPOSITIONS.get(row["joint_tuple_id"])
        if item:
            row["program_composition_status"] = item["composition_status"]
            row["program_composition_parse"] = item["component_parse"]
            row["program_component_ids"] = item["component_ids"]
            row["program_composed_reading_de"] = item["composed_reading_de"]
            row["program_composition_role"] = "EXACT_PROGRAM_CARD_AT_CELL_COMMIT"
        else:
            row["program_composition_status"] = "NOT_IN_28_CARD_PROGRAM_DECK"
            row["program_composition_parse"] = "NOT_APPLICABLE"
            row["program_component_ids"] = "NOT_APPLICABLE"
            row["program_composed_reading_de"] = "NOT_APPLICABLE"
            row["program_composition_role"] = "NOT_APPLICABLE"
        out_events.append(row)

    out_sentences: list[dict[str, str]] = []
    for original in sentences:
        row = dict(original)
        item = COMPOSITIONS.get(row["step_ending_card_id"])
        if item:
            row["program_composition_status"] = item["composition_status"]
            row["program_composition_parse"] = item["component_parse"]
            row["program_component_command_de"] = item["composed_reading_de"]
            row["program_composition_note"] = item["exception_note_de"]
        elif row["step_ending_class"] == "COMMIT_CELL":
            row["program_composition_status"] = "OTHER_TERMINAL_CARD"
            row["program_composition_parse"] = "GELERNTE ANDERE SCHLUSSKARTE"
            row["program_component_command_de"] = row["step_ending_action_de"]
            row["program_composition_note"] = "Gehört nicht zum 28-Karten-Menü der lokalen Variantenmodule."
        elif row["step_ending_class"] == "RELEASE_RECORD":
            row["program_composition_status"] = "RECORD_LAYOUT_RELEASE"
            row["program_composition_parse"] = "RECORDLAYOUT"
            row["program_component_command_de"] = "Record freigeben"
            row["program_composition_note"] = "Kein terminaler Kartenbefehl."
        else:
            row["program_composition_status"] = "OPEN_HANDOFF"
            row["program_composition_parse"] = "KEIN SCHLUSSPROGRAMM"
            row["program_component_command_de"] = "Arbeitsstand weiterreichen"
            row["program_composition_note"] = "Offene Übergabe statt Zellschluss."
        out_sentences.append(row)

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(REGISTER_OUT, register_rows)
    write_tsv(COMPONENT_OUT, component_rows)
    write_tsv(FAMILY_OUT, family_rows)

    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        by_record[row["record_unit_id"]].append(row)
    lines = [
        "# Elf Records mit zerlegten Programmkarten",
        "",
        "Die deutsche Arbeitslesung bleibt erhalten. In Klammern steht nur der neue Lehrlingsbauplan der terminalen Karte.",
        "",
    ]
    for record in RECORD_ORDER:
        rows_here = by_record[record]
        lines.extend([f"## {record} — {rows_here[0]['page']}", ""])
        for row in rows_here:
            suffix = ""
            if row["program_composition_status"] in {"PRODUCTIVE_COMPOSITION", "LICENSED_PARTIAL", "MEMORIZED_WHOLE_CARD"}:
                suffix = f" **[PROGRAMM: {row['program_composition_parse']}]**"
            lines.append(f"- **{row['statement_id']}** — {row['workshop_sentence_de']}{suffix}")
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    mapped_events = [row for row in out_events if row["program_composition_status"] != "NOT_IN_28_CARD_PROGRAM_DECK"]
    card_status = Counter(row["composition_status"] for row in register_rows)
    event_status = Counter(row["program_composition_status"] for row in mapped_events)
    selected_status = Counter()
    for row in register_rows:
        selected_status[row["composition_status"]] += int(row["occurrence_count"])
    sentence_status = Counter(row["program_composition_status"] for row in out_sentences)
    checks = {
        "cards_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(out_sentences) == 116,
        "records_11": set(by_record) == set(RECORD_ORDER),
        "program_cards_28": len(register_rows) == 28,
        "components_15": len(component_rows) == 15,
        "families_8": len(family_rows) == 8,
        "card_status_20_4_4": card_status == Counter({"PRODUCTIVE_COMPOSITION": 20, "LICENSED_PARTIAL": 4, "MEMORIZED_WHOLE_CARD": 4}),
        "all_occurrence_status_69_5_4": event_status == Counter({"PRODUCTIVE_COMPOSITION": 69, "LICENSED_PARTIAL": 5, "MEMORIZED_WHOLE_CARD": 4}),
        "selector_use_status_55_5_4": selected_status == Counter({"PRODUCTIVE_COMPOSITION": 55, "LICENSED_PARTIAL": 5, "MEMORIZED_WHOLE_CARD": 4}),
        "mapped_events_78": len(mapped_events) == 78,
        "mapped_statements_78": sum(sentence_status[key] for key in ["PRODUCTIVE_COMPOSITION", "LICENSED_PARTIAL", "MEMORIZED_WHOLE_CARD"]) == 78,
        "other_terminal_cards_11": sentence_status["OTHER_TERMINAL_CARD"] == 11,
        "open_handoffs_19": sentence_status["OPEN_HANDOFF"] == 19,
        "record_releases_8": sentence_status["RECORD_LAYOUT_RELEASE"] == 8,
        "all_mapped_events_commit": all(row["step_closure_role"] == "COMMIT_CELL" for row in mapped_events),
        "all_mapped_events_statement_final": all(
            row["event_id"] == next(sentence for sentence in out_sentences if sentence["statement_id"] == row["statement_id"])["event_ids"].split("|")[-1]
            for row in mapped_events
        ),
        "close_component_all_28": all("CLOSE_EXACT" in row["component_ids"].split("|") for row in register_rows),
        "no_global_dy_claim": all(row["close_construction"] == "EXACT_CARD_CLOSE" for row in register_rows),
        "dictionary_unchanged": all(all(row[key] == old[key] for key in old) for row, old in zip(out_dictionary, dictionary)),
        "events_unchanged": all(all(row[key] == old[key] for key in old) for row, old in zip(out_events, events)),
        "sentences_unchanged": all(all(row[key] == old[key] for key in old) for row, old in zip(out_sentences, sentences)),
        "fixed_pages_only": {row["page"] for row in out_events} == ALLOWED_PAGES,
        "sealed_absent": not any(row["page"].startswith("f84") for row in out_events),
        "records_markdown_complete": all(f"## {record} —" in RECORD_OUT.read_text(encoding="utf-8") for record in RECORD_ORDER),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(out_dictionary),
            "events": len(out_events),
            "sentences": len(out_sentences),
            "records": len(by_record),
            "program_cards": len(register_rows),
            "mapped_program_occurrences": len(mapped_events),
            "program_components": len(component_rows),
            "program_families": len(family_rows),
            "card_status": dict(sorted(card_status.items())),
            "all_occurrence_status": dict(sorted(event_status.items())),
            "selector_use_status": dict(sorted(selected_status.items())),
        },
        "working_rule": "ACTION CORE + OPTIONAL DIRECTION/ORDER + OPTIONAL E-GRADE + EXACT-CARD CLOSE; FOUR SPECIALS REMAIN WHOLE",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, REGISTER_OUT, COMPONENT_OUT, FAMILY_OUT, CHECK_OUT]
    summary = {
        "status": result["status"],
        "counts": result["counts"],
        "input_hashes": {path.name: sha256(path) for path in [DICT_IN, EVENT_IN, SENTENCE_IN, PROGRAM_IN]},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "sealed": result["sealed"],
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise AssertionError(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
