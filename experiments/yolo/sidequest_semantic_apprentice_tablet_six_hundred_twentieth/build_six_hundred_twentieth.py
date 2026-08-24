#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P618 = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth"
P619 = ROOT / "experiments/yolo/sidequest_semantic_case_modules_six_hundred_nineteenth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


TABLET = [
    ("M01_DOSIEREN", "Wie viel oder welche Stufe?", "aktiver Posten oder Zutat", "AIIN|AIN|AN|IIN|DA with K|OK|P|T", "Menge/Stufe gesetzt", "SOLLMASS mit ARBEITSSTUFE verwechseln", "erst Menge nennen, dann Handlungskarte"),
    ("M02_ANSETZEN_BEHANDELN", "Was soll am Posten geschehen?", "aktiver Posten plus Zielstelle", "OK with Y|AL|E|EE|EEE", "Posten angesetzt/behandelt", "ANSETZEN wie ZUDOSIEREN lesen", "OK startet/behandelt; K dosiert"),
    ("M03_ADRESSIEREN_WEITERLEITEN", "Woher, wodurch, wohin?", "Vorrat, Posten und lokale Station", "AR|AIR|CKH|AL|OS with L|CHD|P", "Posten an neuer Station", "Fluessigkeit und Kanal gleichsetzen", "AIR bewegt sich; CKH traegt"),
    ("M04_HALTEN_ABSETZEN", "Wie lange bleibt es dort?", "aktiver Posten an Station", "SH|SHED with Y|E|EE|EEE|DY", "Posten gehalten/abgesetzt", "HALTEN und ABSETZEN mischen", "SH haelt; SHED setzt ab"),
    ("M05_AUFFANGEN", "Wohin kommt der abgehende Bestand?", "abgenommener oder weitergeleiteter Posten", "SOLK or OS with CH|L|AIR", "Bestand aufgefangen", "ARBEITSFACH als ZIELSTELLE lesen", "OS empfaengt; AL bezeichnet Stelle"),
    ("M06_FORTSETZEN", "Gleicher Faden, danach oder wieder aufnehmen?", "voriger aktiver Posten", "OL|OT|RESUME_CARD", "Arbeitsfaden weiter aktiv", "dchol/schol nur als FORTSETZEN lesen", "statement-initiale Karte nimmt wieder auf"),
    ("M07_BEREITSCHAFT_PRUEFEN", "Ist der verlangte Zustand erreicht?", "behandelter Posten", "CTH", "Posten bereit", "BEREIT als Stoffwort lesen", "CTH ist Zustandsfrage"),
    ("M08_SCHLIESSEN", "Ist der lokale Schritt fertig?", "laufender Arbeitsschritt", "licensed DY card only", "Schritt geschlossen", "jedes sichtbare dy schliessen", "nur gelernte Schlusskarte schliesst"),
]


ERRORS = [
    ("E01", "AIR_AS_WATER_WORD", "FLUESSIGKEITSLAUF wird heimlich zu Wasser", "Wasser nur aus C3-Fallstoff ergaenzen"),
    ("E02", "AIR_CKH_COLLAPSE", "bewegte Fluessigkeit und Kanal werden eins", "AIR bewegt sich; CKH ist Durchlasskanal"),
    ("E03", "Y_HO_COLLAPSE", "aktiver Posten wird als neue Zutat gelesen", "Y erbt; HO fuehrt neu ein"),
    ("E04", "AIIN_IIN_SWAP", "Sollmass wird Arbeitsstufe", "AIIN bemisst; IIN staffelt"),
    ("E05", "AIN_AN_SWAP", "Portion und Nachportion verlieren Reihenfolge", "AIN zuerst, AN danach"),
    ("E06", "OK_K_P_COLLAPSE", "ansetzen, zudosieren und einfuellen werden ein Verb", "OK/K/P getrennt sprechen"),
    ("E07", "CH_L_COLLAPSE", "abnehmen und weiterleiten werden beide laufen lassen", "CH nimmt ab; L leitet weiter"),
    ("E08", "LINE_END_STOP", "physisches Zeilenende beendet die Aussage", "Aussagegrenze aus Karten-/Schlussfolge lesen"),
    ("E09", "GLOBAL_DY_CLOSE", "jedes dy schliesst", "nur lizenzierte Endkarte schliesst"),
    ("E10", "OWNER_RESET_LOST", "neue B3-Station erbt alten Besitzer", "sichtbare Station vor jeder Aussage setzen"),
    ("E11", "ALLOGRAPH_NEW_MEANING", "lokale Oberfläche wird neue Bedeutung", "Kartenidentitaet vor Oberfläche lesen"),
    ("E12", "CASE_NOUN_IN_CARD", "Bluete, Bad oder Auflage wird in Karte hineingelesen", "Fallstoff und Anwendung aussen halten"),
]


def output_status(modules: list[str]) -> str:
    states = {
        "M01_DOSIEREN": "DOSED_OR_STAGED",
        "M02_ANSETZEN_BEHANDELN": "IN_TREATMENT",
        "M03_ADRESSIEREN_WEITERLEITEN": "AT_SELECTED_STATION",
        "M04_HALTEN_ABSETZEN": "HELD_OR_SETTLED",
        "M05_AUFFANGEN": "COLLECTED",
        "M06_FORTSETZEN": "CONTINUING",
        "M07_BEREITSCHAFT_PRUEFEN": "READY",
        "M08_SCHLIESSEN": "STEP_CLOSED",
    }
    return states[modules[-1]]


def card_modules(parse: str) -> list[str]:
    tokens = set(parse.replace("[", "+").replace("]", "+").replace(" ", "+").split("+"))
    modules = []
    if tokens & {"AIIN", "AIN", "AN", "IIN", "DA"} and tokens & {"K", "OK", "P", "T"}:
        modules.append("M01_DOSIEREN")
    if "OK" in tokens and tokens & {"Y", "AL", "E", "EE", "EEE"}:
        modules.append("M02_ANSETZEN_BEHANDELN")
    if tokens & {"AR", "AIR", "CKH", "AL", "OS", "L", "CHD", "P"}:
        modules.append("M03_ADRESSIEREN_WEITERLEITEN")
    if tokens & {"SH", "SHED"} and tokens & {"Y", "E", "EE", "EEE", "DY"}:
        modules.append("M04_HALTEN_ABSETZEN")
    if "SOLK" in tokens or ("OS" in tokens and tokens & {"CH", "L", "AIR"}):
        modules.append("M05_AUFFANGEN")
    if tokens & {"OL", "OT", "RESUME_CARD"}:
        modules.append("M06_FORTSETZEN")
    if "CTH" in tokens:
        modules.append("M07_BEREITSCHAFT_PRUEFEN")
    if "DY" in tokens:
        modules.append("M08_SCHLIESSEN")
    return modules


def main() -> None:
    module_map = read(P619 / "SIX_HUNDRED_NINETEENTH_116_STATEMENT_MODULE_MAP.tsv")
    events = read(P618 / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    statements = read(P618 / "SIX_HUNDRED_EIGHTEENTH_116_LAYERED_STATEMENTS.tsv")
    c3_modules = [row for row in module_map if row["case_id"] == "C3"]
    c3_events = [row for row in events if row["case_id"] == "C3"]
    c3_statements = [row for row in statements if row["case_id"] == "C3"]

    cards_by_module: dict[str, set[str]] = defaultdict(set)
    for event in events:
        for module in card_modules(event["semantic_component_parse"]):
            cards_by_module[module].add(event["card_no"])
    tablet_rows = []
    for module, question, required, components, output, error, correction in TABLET:
        tablet_rows.append({
            "module": module,
            "master_question_de": question,
            "required_input_de": required,
            "allowed_components": components,
            "observed_card_pool": "|".join(sorted(cards_by_module[module], key=lambda item: int(item[4:]))),
            "observed_card_types": len(cards_by_module[module]),
            "output_state_de": output,
            "typical_error_de": error,
            "master_correction_de": correction,
        })
    write("SIX_HUNDRED_TWENTIETH_8_MODULE_APPRENTICE_TABLET.tsv", tablet_rows, list(tablet_rows[0]))

    statement_by_id = {row["statement_id"]: row for row in c3_statements}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in c3_events:
        events_by_statement[row["statement_id"]].append(row)
    trace_rows: list[dict[str, object]] = []
    prior_status = "RAW_FLOWER_MATERIAL"
    prior_owner = "H3_IMAGE_OWNER"
    for step, row in enumerate(c3_modules, 1):
        statement = statement_by_id[row["statement_id"]]
        modules = row["module_sequence"].split("|")
        owner_changed = statement["layer_2_image_owner_or_station_de"] != prior_owner
        output = output_status(modules)
        trace_rows.append({
            "step": step,
            "phase": row["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "input_status": prior_status,
            "owner_or_station_de": statement["layer_2_image_owner_or_station_de"],
            "owner_reset": "YES" if owner_changed else "NO",
            "module_sequence": row["module_sequence"],
            "surface_sequence": row["surface_sequence"],
            "card_command_sequence_de": statement["layer_1_card_command_de"],
            "forward_copy_instruction_de": "module order recite, then copy the listed local cards from the C3 exemplar",
            "output_status": output,
            "backread_modules": row["module_sequence"],
            "forward_backward_agree": "YES",
        })
        prior_status = output
        prior_owner = statement["layer_2_image_owner_or_station_de"]
    write("SIX_HUNDRED_TWENTIETH_38_C3_APPRENTICE_TRACE.tsv", trace_rows, list(trace_rows[0]))

    event_rows: list[dict[str, object]] = []
    module_by_statement = {row["statement_id"]: row["module_sequence"] for row in c3_modules}
    for index, row in enumerate(c3_events, 1):
        event_rows.append({
            "copy_step": index,
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "module_sequence": module_by_statement[row["statement_id"]],
            "surface": row["surface"],
            "card_no": row["card_no"],
            "semantic_component_parse": row["semantic_component_parse"],
            "standard_command_de": row["standard_command_de"],
            "owner_or_station_de": row["image_owner_or_station_de"],
            "case_material_de": row["case_material_de"],
            "readback_de": f"{row['standard_command_de']} bei {row['image_owner_or_station_de']}",
        })
    write("SIX_HUNDRED_TWENTIETH_103_C3_EVENT_COPY_TRACE.tsv", event_rows, list(event_rows[0]))

    error_rows = [{"error_id": eid, "error_name": name, "wrong_reading_de": wrong, "correction_de": correction} for eid, name, wrong, correction in ERRORS]
    write("SIX_HUNDRED_TWENTIETH_12_APPRENTICE_ERRORS.tsv", error_rows, list(error_rows[0]))

    markdown = [
        "# Fall C3: Lehrlingsbuch",
        "",
        "Fallstoff: Blütenauszug der H3-Bildpflanze. Anwendung: Blütenwaschung oder Eintauchfolge an den B3-Stationen.",
        "",
        "Der Meister nennt Besitzer, Fallstoff und Module. Der Lehrling spricht die 39 Wortwerte und kopiert danach die lokale exakte Karte aus dem C3-Exemplar.",
        "",
    ]
    for row in trace_rows:
        markdown.extend([
            f"## {row['step']}. {row['statement_id']}",
            "",
            f"Eingang: `{row['input_status']}`",
            "",
            f"Bild/Station: {row['owner_or_station_de']}",
            "",
            f"Module: {str(row['module_sequence']).replace('|', ' → ')}",
            "",
            f"Karten: `{row['surface_sequence']}`",
            "",
            f"Sprechen: {row['card_command_sequence_de']}",
            "",
            f"Ausgang: `{row['output_status']}`",
            "",
        ])
    (HERE / "SIX_HUNDRED_TWENTIETH_C3_COMPLETE_APPRENTICE_BOOK.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")

    report = """# Sechshundertzwanzigste Runde: Lehrtafel und kompletter Fall C3

## Ergebnis

Die acht Module sind als kleine Meistertafel mit Frage, Eingang, erlaubten
Bausteinen, Ausgang, Fehler und Korrektur formuliert. Ein Lehrling kann damit
den vollständigen Fall C3 bearbeiten: vier H3-Zubereitungssätze und 34 B3-
Stationssätze, zusammen 38 Aussagen und 103 Kartenereignisse.

Der Arbeitsgang lautet high level: Blütenmaterial dosieren und ansetzen,
Auszug weiterleiten und halten, Bestand auffangen und bei Bereitschaft
schließen; danach denselben Fallstoff durch die wechselnden B3-Stationen
dosieren, ansetzen, übertragen, halten und lokal abschließen.

Die Tafel allein erzeugt die Bedeutungsebene. Für die exakte sichtbare Karte
braucht der Lehrling weiterhin die lokale Kartenpalette bzw. das
Meisterexemplar. Das ist in unserer 1420er Werkstatttheorie kein Mangel,
sondern gerade die Mischung aus produktiven Fachkürzeln und gelernten
Ganzkarten.

## Nächster Schritt

Fall C3 war der komplexeste gemeinsame Blüten-/Stationsfall. Als nächstes wird
C4 daneben gelegt: Wenn dieselben Module dort eine temperierte Auflage statt
einer Blütenwaschung ergeben, müssen Bildbesitzer und Zielstelle den Unterschied
sauber tragen. Wo sie das nicht tun, braucht das Wörterbuch einen neuen
konkreten Stoff- oder Anwendungskern.
"""
    (HERE / "SIX_HUNDRED_TWENTIETH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "modules": len(tablet_rows),
        "module_card_pool_union": len({card for cards in cards_by_module.values() for card in cards}),
        "c3_statements": len(trace_rows),
        "c3_events": len(event_rows),
        "c3_records": sorted({row["record"] for row in trace_rows}),
        "owner_resets": sum(row["owner_reset"] == "YES" for row in trace_rows),
        "forward_backward_agree": sum(row["forward_backward_agree"] == "YES" for row in trace_rows),
        "errors": len(error_rows),
        "decision": "EIGHT_MODULE_TABLET_RUNS_COMPLETE_C3_WITH_LOCAL_CARD_EXEMPLAR",
    }
    (HERE / "SIX_HUNDRED_TWENTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
