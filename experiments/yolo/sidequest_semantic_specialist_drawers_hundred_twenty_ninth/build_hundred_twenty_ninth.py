#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R128 = ROOT / "experiments/yolo/sidequest_semantic_extension_core_revision_hundred_twenty_eighth"

TOKEN = {
    "ansetzen": "einsetzen", "umsetzen": "übertragen", "Schluss": "schließen",
    "Durchlass": "Durchgang", "bereit": "bereitstellen", "sammeln": "auffangen",
    "Quelle": "Ausgang", "Ziel": "Zielstelle", "Lauf": "Flüssigkeitslauf",
    "Ergebnis": "Klarlauf", "Stufe": "Arbeitsstufe", "vorher": "voriger Posten",
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def drawer(atoms, old):
    atom_set = set(atoms.split("+"))
    word_set = set(old.split("+"))
    if atom_set & {"CFH", "CPH", "CKHE", "WASH", "CKH", "CHEEY"} or word_set & {"seihen", "waschen", "Durchlass", "Ergebnis", "auswringen", "nachseihen"}:
        return "D2_FILTER_WASH_FLOW"
    if atom_set & {"DAN", "LDDY", "AM"} or word_set & {"anwenden", "festbinden", "verwahren"}:
        return "D7_APPLICATION_FASTEN_STORE"
    if atom_set & {"CHEO", "HO", "OR", "DCHE", "OS", "DAIN", "LOCAL_WHOLE"} or word_set & {"Zutat", "Ansatz", "Auszug", "Wurzel", "Gefäß", "Tuch"}:
        return "D1_MATERIAL_PRODUCT_VESSEL"
    if atom_set & {"CHK", "SHED", "CTH", "SOLK", "SH", "ODY", "E", "EE", "EEE"} or word_set & {"wärmen", "absetzen", "halten", "sammeln", "kühlen", "bereit", "kurz", "länger", "vollständig"}:
        return "D3_HEAT_SETTLE_STATE"
    if atom_set & {"CHD", "L", "P", "AL", "AR", "AIR", "SK"} or word_set & {"abführen", "zuführen", "umsetzen", "Quelle", "Ziel", "Lauf", "ausgießen"}:
        return "D4_TRANSFER_SOURCE_TARGET"
    if atom_set & {"AIIN", "AIN", "IIN", "TY"} or word_set & {"Sollmaß", "Anteil", "Teil", "Stufe"}:
        return "D5_QUANTITY_PART_STAGE"
    if atom_set & {"OT", "OL"} or word_set & {"danach", "weiter"}:
        return "D6_ORDER_CONTINUATION"
    return "D8_LOCAL_OPERATION"


def speak(old):
    pieces = old.split("+")
    close = pieces and pieces[-1] == "Schluss"
    if close:
        pieces = pieces[:-1]
    spoken = [TOKEN.get(piece, piece) for piece in pieces]
    phrase = " · ".join(spoken)
    if close:
        phrase = f"{phrase}; schließen" if phrase else "schließen"
    return phrase


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(R128 / "HUNDRED_TWENTY_EIGHTH_173_CARD_OVERLAY.tsv")
    events = read_tsv(R128 / "HUNDRED_TWENTY_EIGHTH_381_EVENT_OVERLAY.tsv")
    remaining = [row for row in cards if row["current_layer"] == "UNCHANGED_LEARNED_SECTION_CARD"]
    value_by_id = {}
    drawer_by_id = {}
    specialist_rows = []
    for row in remaining:
        value = speak(row["current_short_default_de"])
        card_drawer = drawer(row["semantic_atoms"], row["current_short_default_de"])
        value_by_id[row["master_card_id"]] = value
        drawer_by_id[row["master_card_id"]] = card_drawer
        specialist_rows.append({
            "drawer": card_drawer,
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "semantic_atoms_for_memory_only": row["semantic_atoms"],
            "old_telegraphic_default_de": row["current_short_default_de"],
            "spoken_whole_card_value_de": value,
            "event_count": row["event_count"],
            "records": row["records"],
            "learning_rule": "learn as one exact specialist card; do not promote a new universal stem",
        })
    specialist_rows.sort(key=lambda row: (row["drawer"], -int(row["event_count"]), row["master_card_id"]))
    write_tsv("HUNDRED_TWENTY_NINTH_132_SPECIALIST_CARDS.tsv", specialist_rows)

    drawer_counts = Counter(row["drawer"] for row in specialist_rows)
    drawer_events = Counter()
    for row in specialist_rows:
        drawer_events[row["drawer"]] += int(row["event_count"])
    drawer_rows = []
    descriptions = {
        "D1_MATERIAL_PRODUCT_VESSEL": "ingredients, preparations, extracts, vessels and cloth carriers",
        "D2_FILTER_WASH_FLOW": "passages, strainers, washing and clear-run results",
        "D3_HEAT_SETTLE_STATE": "warming, holding, settling, collection and readiness",
        "D4_TRANSFER_SOURCE_TARGET": "inward/outward transfer, source, target and liquid run",
        "D5_QUANTITY_PART_STAGE": "shares, parts, prescribed values and work stages",
        "D6_ORDER_CONTINUATION": "next step, continuation and carried sequence",
        "D7_APPLICATION_FASTEN_STORE": "application, fastening, storage and local completion",
        "D8_LOCAL_OPERATION": "remaining exact local workshop operation",
    }
    for name in descriptions:
        drawer_rows.append({
            "drawer": name,
            "teaching_description": descriptions[name],
            "card_types": str(drawer_counts[name]),
            "events": str(drawer_events[name]),
            "apprentice_instruction": "select by the local page exemplar and owner; copy the whole card",
        })
    write_tsv("HUNDRED_TWENTY_NINTH_EIGHT_SPECIALIST_DRAWERS.tsv", drawer_rows)

    full_cards = []
    for row in cards:
        if row["master_card_id"] in value_by_id:
            value = value_by_id[row["master_card_id"]]
            layer = "SPECIALIST_DRAWER_WHOLE_CARD"
            card_drawer = drawer_by_id[row["master_card_id"]]
        else:
            value = row["current_short_default_de"]
            layer = row["current_layer"]
            card_drawer = "ACTIVE_CORE"
        full_cards.append({
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "semantic_atoms": row["semantic_atoms"],
            "current_spoken_default_de": value,
            "teaching_layer": layer,
            "drawer": card_drawer,
            "event_count": row["event_count"],
            "records": row["records"],
        })
    write_tsv("HUNDRED_TWENTY_NINTH_COMPLETE_173_CARD_DICTIONARY.tsv", full_cards)

    card_lookup = {row["master_card_id"]: row for row in full_cards}
    event_rows = []
    statement_values = defaultdict(list)
    for row in events:
        card = card_lookup[row["master_card_id"]]
        event_rows.append({
            "event_serial": row["event_serial"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "current_spoken_default_de": card["current_spoken_default_de"],
            "teaching_layer": card["teaching_layer"],
            "drawer": card["drawer"],
        })
        statement_values[row["statement_id"]].append(card["current_spoken_default_de"])
    write_tsv("HUNDRED_TWENTY_NINTH_COMPLETE_381_EVENT_DICTIONARY.tsv", event_rows)

    statement_rows = []
    seen = set()
    for row in event_rows:
        if row["statement_id"] in seen:
            continue
        seen.add(row["statement_id"])
        statement_rows.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "complete_spoken_card_chain_de": " | ".join(statement_values[row["statement_id"]]),
        })
    write_tsv("HUNDRED_TWENTY_NINTH_COMPLETE_116_CARD_CHAINS.tsv", statement_rows)

    report = [
        "# Hundertneunundzwanzigste Runde: acht Schubladen für den seltenen Rest", "",
        "Die 132 seltenen Karten werden nicht zu 132 neuen Stämmen. Jede bleibt ein gelerntes Ganzwort mit",
        "einem kurzen gesprochenen Wert und liegt in einer von acht Schubladen: Material/Gefäß, Filtration/",
        "Waschen, Wärme/Zustand, Transfer/Adresse, Menge/Stufe, Reihenfolge, Anwendung/Lagerung oder lokale",
        "Operation.", "",
        "Ein Pluszeichen-Gloss wird nur in eine sprechbare Telegrammform verwandelt: etwa",
        "`halten · bearbeiten · übertragen; schließen`. Das ist ein Merkspruch für eine exakte Karte, keine",
        "Behauptung, dass jeder sichtbare Teil ein selbständiges Wort sei. Die Oberfläche wird aus dem",
        "Exemplar kopiert.", "",
        "Damit besitzt jede der 173 Prosekarten wieder genau einen kurzen Default, aber nur 41 Karten gehören",
        "zum aktiv generativen Lehrkern. Die vollständigen 381 Ereignisse und 116 Kartenketten sind neu",
        "ausgegeben. Nächster Schritt: aus den acht Schubladen je eine typische vollständige Fachanweisung",
        "rekonstruieren und prüfen, ob die Kategorien praktisch unterschiedliche Aufgaben tragen.",
    ]
    (OUT / "HUNDRED_TWENTY_NINTH_SPECIALIST_DRAWER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE",
        "active_core_cards": sum(row["drawer"] == "ACTIVE_CORE" for row in full_cards),
        "specialist_whole_cards": len(specialist_rows),
        "specialist_events": sum(int(row["event_count"]) for row in specialist_rows),
        "drawers": len(drawer_rows),
        "complete_cards": len(full_cards),
        "complete_events": len(event_rows),
        "complete_statements": len(statement_rows),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
