#!/usr/bin/env python3
"""Extend the creative component language over the remaining prose cards."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FIRST = ROOT / "experiments/yolo/sidequest_semantic_portable_component_grammar"
UNIQUE = ROOT / "experiments/yolo/sidequest_semantic_unique_master_glosses"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SECOND_ATOMS = [
    ("B01", "SHED", "ABSETZEN", "STATE", "cheedy / shedal / sheedy"),
    ("B02", "L", "ABFÜHREN", "DIRECTION_OPERATION", "lchedy / ldy / lar"),
    ("B03", "CTH", "BEREIT", "STATE", "checthy / cthaiin / cthoor"),
    ("B04", "CKH", "DURCHLEITEN", "OPERATION", "chckhy / sheckhy / qockhey"),
    ("B05", "CKHE", "SEIHEN", "OPERATION", "shckhedy / lcheckhedy"),
    ("B06", "CHK", "WÄRMEN", "OPERATION", "cheky / cheeky / chkeedy"),
    ("B07", "SOLK", "SAMMELN", "OPERATION", "solkey / solkeey / olkeedy"),
    ("B08", "WASH", "WASCHEN", "OPERATION", "lsho / lshedy / rshedy"),
    ("B09", "IIN", "STUFE", "ARGUMENT", "oiiin / daiiin / kaiiin"),
    ("B10", "TY", "TEIL", "OBJECT", "cheeety / etyd / otytchol"),
    ("B11", "AIR", "WASSERLAUF", "MEDIUM_PATH", "chair / kair / okair / schedair"),
    ("B12", "CHEO", "AUSZUG", "PRODUCT", "cheoar / chokcheo / ycheor"),
    ("B13", "P", "EINFÜHREN", "DIRECTION_OPERATION", "pchedal / pchedy"),
    ("B14", "PARTITION", "TRENNEN", "OPERATION", "ches / chety"),
]


SECOND_RING = {
    "cheedy": ("SHED+E+CLOSE", "KURZ ABSETZEN; SCHLUSS", "SHED_STATE"),
    "shedal": ("SHED+AL", "AM ZIEL ABSETZEN", "SHED_STATE"),
    "sheedy": ("SHED+EE+CLOSE", "LÄNGER ABSETZEN; SCHLUSS", "SHED_STATE"),
    "qokshedy": ("OK+SHED+CLOSE", "ABSETZGANG SETZEN; SCHLUSS", "SHED_STATE"),
    "solshedy": ("OL+SHED+CLOSE", "WEITER ABSETZEN; SCHLUSS", "SHED_STATE"),
    "chldaiin": ("SHED+AIIN", "ABSETZWERT", "SHED_STATE"),
    "checthy": ("CTH+Y", "BEREITER POSTEN", "CTH_READY"),
    "qcthey": ("CTH+E+Y", "KURZ BEREITHALTEN", "CTH_READY"),
    "cthaiin": ("CTH+AIIN", "BEREITWERT", "CTH_READY"),
    "cthoor": ("CTH+OR", "BEREITER ANSATZ", "CTH_READY"),
    "octheol": ("CTH+OL", "BEREIT FORTSETZEN", "CTH_READY"),
    "oltchy": ("OL+CTH+Y", "BEREITEN POSTEN FORTSETZEN", "CTH_READY"),
    "qoctholy": ("CTH+OL+Y", "BEREITEN POSTEN FORTSETZEN", "CTH_READY"),
    "shecthedchy": ("CTH+CHD+Y", "BEREITEN POSTEN ÜBERTRAGEN", "CTH_READY"),
    "shecthy": ("CTH+E+Y", "KURZ BEREITHALTEN", "CTH_READY"),
    "chckhy": ("CKH+Y", "AKTUELLEN POSTEN DURCHLEITEN", "CKH_PATH"),
    "chckhal": ("CKH+AL", "ZUM ZIEL DURCHLEITEN", "CKH_PATH"),
    "lcheckhy": ("L+CKH+Y", "POSTEN DURCH AUSGANG FÜHREN", "CKH_PATH"),
    "qockhey": ("OK+CKH+E+Y", "KURZEN DURCHLAUF SETZEN", "CKH_PATH"),
    "sheckhal": ("CKH+E+AL", "KURZ ZUM ZIEL DURCHLEITEN", "CKH_PATH"),
    "sheckhy": ("CKH+E+Y", "KURZ DURCHLEITEN", "CKH_PATH"),
    "shckhedy": ("CKHE+CLOSE", "SEIHEN; SCHLUSS", "CKHE_STRAIN"),
    "lcheckhedy": ("L+CKHE+CLOSE", "ABSEIHEN; SCHLUSS", "CKHE_STRAIN"),
    "cheky": ("CHK+E+Y", "KURZ WÄRMEN", "CHK_WARM"),
    "cheeky": ("CHK+EE+Y", "LÄNGER WÄRMEN", "CHK_WARM"),
    "chkeedy": ("CHK+EE+CLOSE", "LÄNGER WÄRMEN; SCHLUSS", "CHK_WARM"),
    "chkeey": ("CHK+EE+Y", "LÄNGER WÄRMEN", "CHK_WARM"),
    "olkeedy": ("SOLK+EE+CLOSE", "LÄNGER SAMMELN; SCHLUSS", "SOLK_COLLECT"),
    "solkaiin": ("SOLK+AIIN", "BIS VORGABEWERT SAMMELN", "SOLK_COLLECT"),
    "solkeey": ("SOLK+EE+Y", "LÄNGER SAMMELN", "SOLK_COLLECT"),
    "solkey": ("SOLK+E+Y", "KURZ SAMMELN", "SOLK_COLLECT"),
    "lchedy": ("L+CHD+CLOSE", "ABFÜHREN; SCHLUSS", "L_OUT"),
    "ldy": ("L+CLOSE", "ABFÜHREN; SCHLUSS", "L_OUT"),
    "lar": ("L+AR", "VOM AUSGANG ABFÜHREN", "L_OUT"),
    "lched": ("L+CHD", "ABFÜHREN", "L_OUT"),
    "lchedal": ("L+CHD+AL", "ZUM ZIEL ABFÜHREN", "L_OUT"),
    "lchedar": ("L+CHD+AR", "VOM AUSGANG ABFÜHREN", "L_OUT"),
    "lcheey": ("L+CHEEY", "FREIGEGEBENEN WERT ABFÜHREN", "L_OUT"),
    "lchy": ("L+Y", "AKTUELLEN POSTEN ABZIEHEN", "L_OUT"),
    "lol": ("L+OL", "ABFÜHRUNG FORTSETZEN", "L_OUT"),
    "ls": ("L", "AUSLASS", "L_OUT"),
    "lshedy": ("WASH+CLOSE", "WASCHEN; SCHLUSS", "WASH"),
    "lsho": ("WASH", "WASCHGANG", "WASH"),
    "rshedy": ("WASH+CLOSE", "WASCHEN; SCHLUSS", "WASH"),
    "oiiin": ("IIN", "STUFE", "IIN_STAGE"),
    "daiiin": ("IIN", "STUFE", "IIN_STAGE"),
    "kaiiin": ("IIN", "STUFE", "IIN_STAGE"),
    "cheeety": ("EEE+TY", "GANZER TEIL", "TY_PART"),
    "etyd": ("E+TY", "KURZER TEIL", "TY_PART"),
    "otytchol": ("OT+TY+OL", "NÄCHSTEN TEIL FORTSETZEN", "TY_PART"),
    "shoyty": ("HO+Y+TY", "TEIL DES EINGANGSPOSTENS", "TY_PART"),
    "chair": ("AIR", "WASSERLAUF", "AIR_FLOW"),
    "kair": ("AIR", "WASSERLAUF", "AIR_FLOW"),
    "okair": ("OK+AIR", "WASSERLAUF SETZEN", "AIR_FLOW"),
    "schedair": ("AIR", "WASSERLAUF", "AIR_FLOW"),
    "dairydy": ("AIR+Y+CLOSE", "WASSERLAUF SCHLIESSEN", "AIR_FLOW"),
    "cheoar": ("CHEO+AR", "AUSZUG VOM AUSGANG", "CHEO_EXTRACT"),
    "chokcheo": ("OK+CHEO", "AUSZUG SETZEN", "CHEO_EXTRACT"),
    "kchoar": ("CHEO+AR", "AUSZUG VOM AUSGANG", "CHEO_EXTRACT"),
    "ycheor": ("Y+CHEO+OR", "AUSZUGSANSATZ", "CHEO_EXTRACT"),
    "pchedal": ("P+CHD+AL", "ZUM ZIEL EINFÜHREN", "P_IN"),
    "pchedy": ("P+CHD+CLOSE", "EINFÜHREN; SCHLUSS", "P_IN"),
    "ches": ("PARTITION", "TRENNEN", "PARTITION"),
    "chety": ("PARTITION+TY", "TEIL ABTRENNEN", "PARTITION"),
    "chealror": ("AL+OR", "ANSATZ ZUM ZIEL", "KNOWN_ATOMS_LOCAL_FRAME"),
    "chedchy": ("CHD+Y", "AKTUELLEN POSTEN ÜBERTRAGEN", "KNOWN_ATOMS_LOCAL_FRAME"),
    "daldy": ("AL+CLOSE", "ZIEL SCHLIESSEN", "KNOWN_ATOMS_LOCAL_FRAME"),
    "ldalor": ("AL", "ENDZIEL", "KNOWN_ATOMS_LOCAL_FRAME"),
    "lo": ("L", "ABFÜHREN", "KNOWN_ATOMS_LOCAL_FRAME"),
    "lochedy": ("L+CHD+CLOSE", "REST ABFÜHREN; SCHLUSS", "KNOWN_ATOMS_LOCAL_FRAME"),
    "olsaly": ("AL+Y", "POSTEN ZUR UNTEREN ZIELSTELLE", "KNOWN_ATOMS_LOCAL_FRAME"),
    "qokeedal": ("OK+EE+AL", "LÄNGER AM ZIEL HALTEN", "KNOWN_ATOMS_LOCAL_FRAME"),
    "qokokchy": ("OK+OK+Y", "AKTUELLEN POSTEN ERNEUT SETZEN", "KNOWN_ATOMS_LOCAL_FRAME"),
    "qokol": ("OK+OL", "FORTSETZUNG SETZEN", "KNOWN_ATOMS_LOCAL_FRAME"),
    "qolky": ("OL", "AUF DEM ARBEITSWEG FORTSETZEN", "KNOWN_ATOMS_LOCAL_FRAME"),
    "shfydaiin": ("SH+AIIN", "HALTEWERT", "KNOWN_ATOMS_LOCAL_FRAME"),
    "tshey": ("CHEEY", "FREIGEGEBENER WERT", "KNOWN_ATOMS_LOCAL_FRAME"),
    "tshol": ("HO+L", "EINGANGSPOSTEN ENTNEHMEN", "KNOWN_ATOMS_LOCAL_FRAME"),
    "ykan": ("Y+AIN", "AKTUELLER ANTEIL", "KNOWN_ATOMS_LOCAL_FRAME"),
}


PASSAGE_READINGS = {
    "H1-S001": "Nimm die Wurzel, halte den Ansatz bereit, nimm vom Ausgang, trenne einen Teil, gib ihn in den Träger, öffne den Wasserlauf, führe den nächsten Teil weiter und setze den aktuellen Posten auf den Vorgabewert.",
    "B2-S005": "Setze den aktuellen Posten am Ziel, sammle bis zum Vorgabewert, leite durch, setze zweimal auf Vorgabewert, führe bereit fort, wärme länger, führe ab und schließe.",
    "B2-S016": "Führe zum Ziel und vom Ausgang ab, trenne, setze den Vorgabewert, nimm den langen Folgeposten, setze kurz, führe ein und schließe.",
    "B3-S034": "Setze die Stufe, halte bereit, trenne einen Teil, setze den Folgewert, führe zur unteren Zielstelle, setze kurz ab und schließe.",
}


def main() -> None:
    first_components = read_tsv(FIRST / "PORTABLE_17_ATOMS_AND_4_WHOLE_CARDS.tsv")
    first_seeds = read_tsv(FIRST / "SEED_29_MASTER_CARD_COMPOSITIONS.tsv")
    first_predictions = read_tsv(FIRST / "PREDICTED_ADDITIONAL_PROSE_CARDS.tsv")
    first_reader = read_tsv(FIRST / "TEN_PAGE_776_PORTABLE_COMPONENT_READER.tsv")
    dictionary = read_tsv(UNIQUE / "UNIQUE_173_MASTER_DICTIONARY.tsv")
    events = read_tsv(UNIQUE / "UNIQUE_381_EVENT_INTERLINEAR.tsv")
    statements = read_tsv(UNIQUE / "UNIQUE_116_STATEMENT_EDITION.tsv")

    dictionary_by_mc = {row["master_card_id"]: row for row in dictionary}
    dictionary_by_head = {row["master_head_form"]: row for row in dictionary}
    if len(dictionary_by_mc) != 173 or len(dictionary_by_head) != 173:
        raise ValueError("master dictionary is not uniquely keyed")
    first_seed_mcs = {row["master_card_id"] for row in first_seeds}
    first_prediction_mcs = {row["master_card_id"] for row in first_predictions}
    if not set(SECOND_RING).issubset(dictionary_by_head):
        raise ValueError(f"missing second-ring heads: {sorted(set(SECOND_RING) - set(dictionary_by_head))}")
    second_mcs = {dictionary_by_head[head]["master_card_id"] for head in SECOND_RING}
    if len(second_mcs) != 79 or second_mcs & (first_seed_mcs | first_prediction_mcs):
        raise ValueError("second-ring inventory overlaps or collapses")

    second_atom_rows = []
    for component_id, symbol, meaning, component_class, examples in SECOND_ATOMS:
        second_atom_rows.append({
            "component_id": component_id,
            "symbol": symbol,
            "short_meaning_de": meaning,
            "component_class": component_class,
            "observed_examples": examples,
            "apprentice_rule_de": f"{symbol} heißt kurz {meaning}; alte Atome liefern Argument, Grad, Richtung und Schluss",
        })
    write_tsv(
        OUT / "SECOND_RING_14_ATOMS.tsv",
        second_atom_rows,
        ["component_id", "symbol", "short_meaning_de", "component_class", "observed_examples", "apprentice_rule_de"],
    )

    event_counts = Counter(row["master_card_id"] for row in events)
    second_rows = []
    second_by_mc: dict[str, tuple[str, str, str]] = {}
    for head in sorted(SECOND_RING):
        atoms, nucleus, family = SECOND_RING[head]
        card = dictionary_by_head[head]
        mc = card["master_card_id"]
        second_by_mc[mc] = (atoms, nucleus, family)
        second_rows.append({
            "master_card_id": mc,
            "master_head_form": head,
            "registered_surface_family": card["registered_surface_family"],
            "second_ring_family": family,
            "atom_sequence": atoms,
            "portable_nucleus_de": nucleus,
            "current_concrete_default_de": card["unique_short_meaning_de"],
            "source_component_formula": card["component_reading"],
            "prose_event_count": event_counts[mc],
            "reading_rule_de": "zweiter Kern plus bereits gelernte Atome; Besitzer liefert die konkrete Werkstattausprägung",
        })
    write_tsv(
        OUT / "SECOND_RING_79_CARD_COMPOSITIONS.tsv",
        second_rows,
        ["master_card_id", "master_head_form", "registered_surface_family", "second_ring_family", "atom_sequence", "portable_nucleus_de", "current_concrete_default_de", "source_component_formula", "prose_event_count", "reading_rule_de"],
    )

    covered_mcs = first_seed_mcs | first_prediction_mcs | second_mcs
    remaining_rows = []
    for card in dictionary:
        mc = card["master_card_id"]
        if mc in covered_mcs:
            continue
        component = card["component_reading"]
        if "WHOLE" in component or "MEMORIZED" in component:
            whole_class = "LEARNED_OBJECT_OR_SPECIAL_COMMAND"
        else:
            whole_class = "LEARNED_LOCAL_COMPOUND"
        remaining_rows.append({
            "master_card_id": mc,
            "master_head_form": card["master_head_form"],
            "registered_surface_family": card["registered_surface_family"],
            "concrete_default_de": card["unique_short_meaning_de"],
            "source_component_formula": component,
            "prose_event_count": event_counts[mc],
            "whole_card_class": whole_class,
            "apprentice_rule_de": "exakte Karte mit kurzer Bedeutung aus dem lokalen Exemplar lernen",
        })
    remaining_rows.sort(key=lambda row: (-int(row["prose_event_count"]), row["master_head_form"]))
    write_tsv(
        OUT / "REMAINING_19_LEARNED_WHOLE_CARDS.tsv",
        remaining_rows,
        ["master_card_id", "master_head_form", "registered_surface_family", "concrete_default_de", "source_component_formula", "prose_event_count", "whole_card_class", "apprentice_rule_de"],
    )

    first_seed_by_mc = {row["master_card_id"]: (row["atom_sequence"], row["portable_nucleus_de"]) for row in first_seeds}
    first_prediction_by_mc = {row["master_card_id"]: (row["atom_sequence"], row["predicted_nucleus_de"]) for row in first_predictions}
    complete_dictionary_rows = []
    for card in dictionary:
        mc = card["master_card_id"]
        if mc in first_seed_by_mc:
            layer = "FIRST_RING_SHARED_SEED"
            atoms, nucleus = first_seed_by_mc[mc]
        elif mc in first_prediction_by_mc:
            layer = "FIRST_RING_PREDICTED"
            atoms, nucleus = first_prediction_by_mc[mc]
        elif mc in second_by_mc:
            layer = "SECOND_RING_COMPOSED"
            atoms, nucleus, _ = second_by_mc[mc]
        else:
            layer = "LEARNED_LOCAL_WHOLE"
            atoms = "LOCAL_WHOLE"
            nucleus = card["unique_short_meaning_de"].upper()
        complete_dictionary_rows.append({
            "master_card_id": mc,
            "master_head_form": card["master_head_form"],
            "registered_surface_family": card["registered_surface_family"],
            "composition_layer": layer,
            "atom_sequence": atoms,
            "portable_nucleus_de": nucleus,
            "concrete_default_de": card["unique_short_meaning_de"],
            "prose_event_count": event_counts[mc],
            "teaching_mode_de": "zusammensetzen" if layer != "LEARNED_LOCAL_WHOLE" else "exakte Ganzkarte lernen",
        })
    write_tsv(
        OUT / "COMPLETE_173_EXTENDED_CARD_DICTIONARY.tsv",
        complete_dictionary_rows,
        ["master_card_id", "master_head_form", "registered_surface_family", "composition_layer", "atom_sequence", "portable_nucleus_de", "concrete_default_de", "prose_event_count", "teaching_mode_de"],
    )

    complete_by_mc = {row["master_card_id"]: row for row in complete_dictionary_rows}
    prose_event_rows = []
    for event in events:
        card = complete_by_mc[event["master_card_id"]]
        prose_event_rows.append({
            **event,
            "composition_layer": card["composition_layer"],
            "atom_sequence": card["atom_sequence"],
            "portable_nucleus_de": card["portable_nucleus_de"],
            "final_concrete_reading_de": event["unique_short_meaning_de"],
        })
    write_tsv(
        OUT / "PROSE_381_EXTENDED_COMPONENT_READER.tsv",
        prose_event_rows,
        list(events[0]) + ["composition_layer", "atom_sequence", "portable_nucleus_de", "final_concrete_reading_de"],
    )

    event_by_id = {row["event_id"]: row for row in events}
    unified_rows = []
    for row in first_reader:
        if row["register"] == "PROSE":
            event = event_by_id[row["source_group_id"]]
            card = complete_by_mc[event["master_card_id"]]
            layer = card["composition_layer"]
            atoms = card["atom_sequence"]
            nucleus = card["portable_nucleus_de"]
        elif row["portable_component_status"] == "SHARED_SEED_CARD":
            layer = "FIRST_RING_SHARED_SEED"
            atoms = row["portable_atom_sequence"]
            nucleus = row["portable_nucleus_de"]
        else:
            layer = "LOCAL_ASTRO_CARD"
            atoms = "LOCAL_OWNER_VALUE"
            nucleus = row["final_local_expansion_de"]
        unified_rows.append({
            **row,
            "extended_composition_layer": layer,
            "extended_atom_sequence": atoms,
            "extended_portable_nucleus_de": nucleus,
            "extended_final_local_reading_de": row["final_local_expansion_de"],
        })
    write_tsv(
        OUT / "TEN_PAGE_776_EXTENDED_COMPONENT_READER.tsv",
        unified_rows,
        list(first_reader[0]) + ["extended_composition_layer", "extended_atom_sequence", "extended_portable_nucleus_de", "extended_final_local_reading_de"],
    )

    statement_by_id = {row["statement_id"]: row for row in statements}
    passage_lines = [
        "# Vier Passagen der zweiten Atomschicht", "",
        "Die neuen Kerne benennen konkrete Werkstatthandlungen. Bereits bekannte Atome liefern Richtung, Wert, Grad, Posten und Schluss.", "",
    ]
    for statement_id, fluent in PASSAGE_READINGS.items():
        statement = statement_by_id[statement_id]
        passage_lines += [f"## {statement_id} · {statement['page']} · {statement['loci']}", "", f"**Sichtbar:** `{statement['surface_sequence']}`", "", "**Kartenweise:**", ""]
        for event in (row for row in events if row["statement_id"] == statement_id):
            card = complete_by_mc[event["master_card_id"]]
            passage_lines.append(f"- `{event['surface_display']}` → `{card['atom_sequence']}` → **{card['portable_nucleus_de']}** ({card['composition_layer']})")
        passage_lines += ["", f"**Neue flüssige Lesung:** {fluent}", "", f"**Bisherige Lesung:** {statement['fluent_workshop_sentence_de']}", ""]
    (OUT / "FOUR_SECOND_RING_PASSAGES.md").write_text("\n".join(passage_lines).rstrip() + "\n", encoding="utf-8")

    layer_counts = Counter(row["composition_layer"] for row in complete_dictionary_rows)
    prose_layer_counts = Counter(row["composition_layer"] for row in prose_event_rows)
    unified_layer_counts = Counter(row["extended_composition_layer"] for row in unified_rows)
    second_events = prose_layer_counts["SECOND_RING_COMPOSED"]
    composed_prose = len(events) - prose_layer_counts["LEARNED_LOCAL_WHOLE"]
    composed_unified = len(unified_rows) - unified_layer_counts["LEARNED_LOCAL_WHOLE"] - unified_layer_counts["LOCAL_ASTRO_CARD"]
    report = f"""# Zweite Werkstattgrammatik: Stoff, Zustand und Weg

## Ergebnis

Die erste Ringsprache erklärte 75 von 173 Prosakarten. Vierzehn neue Sachkerne ziehen 64 der verbliebenen 98 Karten in dieselbe Kompositionsmaschine: **SHED absetzen, L abführen, CTH bereit, CKH durchleiten, CKHE seihen, CHK wärmen, SOLK sammeln, WASH waschen, IIN Stufe, TY Teil, AIR Wasserlauf, CHEO Auszug, P einführen und PARTITION trennen**. Weitere 15 Karten bestehen bereits vollständig aus bekannten Atomen; dort trägt nur ein lokaler Schreibrahmen eine engere Ausprägung wie unten, Rest oder Arbeitsweg.

Diese zweite Schicht deckt {second_events} weitere Prosaereignisse. Insgesamt sind damit {len(dictionary) - len(remaining_rows)} von 173 Kartentypen und {composed_prose} von 381 Prosaereignissen zusammengesetzt. Nur {len(remaining_rows)} Kartentypen mit {sum(int(row['prose_event_count']) for row in remaining_rows)} Vorkommen bleiben gelernte lokale Ganzkarten. Im vollständigen Zehnseitenreader tragen {composed_unified} von 776 Gruppen eine gemeinsame Atomfolge; die übrigen Diagrammwerte bleiben an ihren sichtbaren Besitzer gebunden.

## Was jetzt wirklich wie ein System aussieht

- `SHED+E+CLOSE` und `SHED+EE+CLOSE` sind kurzes und längeres Absetzen mit Schluss.
- `CKH+Y`, `CKH+AL`, `CKH+E+Y` sind Durchleiten des aktuellen Postens, zum Ziel und kurz.
- `CKHE+CLOSE` und `L+CKHE+CLOSE` sind Seihen und Abseihen.
- `CHK+E+Y`, `CHK+EE+Y`, `CHK+EE+CLOSE` sind kurz wärmen, länger wärmen und länger wärmen mit Schluss.
- `SOLK+E+Y`, `SOLK+EE+Y`, `SOLK+EE+CLOSE` bilden den kurzen, langen und abgeschlossenen Sammelgang.
- `L+CHD`, `L+CHD+AL`, `L+CHD+AR`, `L+CHD+CLOSE` bilden einen vollständigen Abführungsweg.
- `AIR`, `OK+AIR`, `AIR+Y+CLOSE` sind Wasserlauf, Wasserlauf setzen und Wasserlauf schließen.
- `CHEO+AR`, `OK+CHEO`, `Y+CHEO+OR` sind Auszug vom Ausgang, Auszug setzen und Auszugsansatz.

## Die verbleibenden Ganzkarten

Die letzten {len(remaining_rows)} Typen werden nicht künstlich weiter zerlegt. Sie tragen weiterhin kurze konkrete Werte wie Wurzel, Zusatz, Gefäß, auswringen, nachseihen, auftragen, befestigen, kalt stellen, ausgießen, verwahren oder anwenden. Fast alle kommen nur einmal vor. Das ergibt nun genau die gesuchte Werkstattmischung: eine große produktive Kürzelschicht und ein kleiner lokaler Nomenklator.

## Lehrregel

Der Lehrling liest zuerst Reihenfolge und Operation, dann Quelle oder Ziel, danach Wert, Grad und aktuellen Posten, zuletzt einen lizenzierten Schluss. `AIR`, `CHEO`, `TY` und `IIN` nennen Arbeitsmedium, Produkt, Teil und Stufe; Besitzer und Bild entscheiden erst danach, welche konkrete Flüssigkeit, Pflanze, Öffnung oder Station gemeint ist.
"""
    (OUT / "SECOND_RING_GRAMMAR_REPORT.md").write_text(report, encoding="utf-8")

    pocket_lines = ["# Taschenkarte der zweiten Atomschicht", "", "## Vierzehn neue Kerne", ""]
    for row in second_atom_rows:
        pocket_lines.append(f"- `{row['symbol']}` = **{row['short_meaning_de']}** — {row['observed_examples']}")
    pocket_lines += ["", "## Neue produktive Reihen", "", "- `SHED + E/EE + CLOSE` → kurz/länger absetzen und schließen", "- `CKH + E + Y/AL` → kurz durchleiten / kurz zum Ziel durchleiten", "- `CHK + E/EE + Y/CLOSE` → kurz/länger wärmen, offen oder geschlossen", "- `SOLK + E/EE + Y/CLOSE` → kurz/länger sammeln, offen oder geschlossen", "- `L + CHD + AR/AL/CLOSE` → vom Ausgang / zum Ziel / abschließend abführen", "- `AIR`, `OK+AIR`, `AIR+Y+CLOSE` → Wasserlauf lesen, setzen, schließen", ""]
    (OUT / "SECOND_RING_POCKET_CARD.md").write_text("\n".join(pocket_lines), encoding="utf-8")

    content_names = [
        "SECOND_RING_14_ATOMS.tsv", "SECOND_RING_79_CARD_COMPOSITIONS.tsv",
        "REMAINING_19_LEARNED_WHOLE_CARDS.tsv", "COMPLETE_173_EXTENDED_CARD_DICTIONARY.tsv",
        "PROSE_381_EXTENDED_COMPONENT_READER.tsv", "TEN_PAGE_776_EXTENDED_COMPONENT_READER.tsv",
        "FOUR_SECOND_RING_PASSAGES.md", "SECOND_RING_GRAMMAR_REPORT.md", "SECOND_RING_POCKET_CARD.md",
    ]
    summary = {
        "status": "BUILT",
        "first_ring_atoms": 17,
        "first_ring_bridge_cards": 4,
        "second_ring_atoms": len(SECOND_ATOMS),
        "first_ring_card_types": len(first_seed_mcs | first_prediction_mcs),
        "second_ring_card_types": len(second_mcs),
        "composed_prose_card_types": len(covered_mcs),
        "remaining_learned_whole_card_types": len(remaining_rows),
        "first_ring_prose_events": sum(event_counts[mc] for mc in first_seed_mcs | first_prediction_mcs),
        "second_ring_prose_events": second_events,
        "composed_prose_events": composed_prose,
        "remaining_learned_whole_events": prose_layer_counts["LEARNED_LOCAL_WHOLE"],
        "astro_shared_events": unified_layer_counts["FIRST_RING_SHARED_SEED"] - prose_layer_counts["FIRST_RING_SHARED_SEED"],
        "composed_unified_groups": composed_unified,
        "complete_unified_groups": len(unified_rows),
        "rewritten_passages": len(PASSAGE_READINGS),
        "composition_layer_card_counts": dict(layer_counts),
        "source_sha256": {
            "first_29_seeds": sha256(FIRST / "SEED_29_MASTER_CARD_COMPOSITIONS.tsv"),
            "first_predictions": sha256(FIRST / "PREDICTED_ADDITIONAL_PROSE_CARDS.tsv"),
            "first_776_reader": sha256(FIRST / "TEN_PAGE_776_PORTABLE_COMPONENT_READER.tsv"),
            "unique_173_dictionary": sha256(UNIQUE / "UNIQUE_173_MASTER_DICTIONARY.tsv"),
            "unique_381_events": sha256(UNIQUE / "UNIQUE_381_EVENT_INTERLINEAR.tsv"),
        },
        "output_sha256": {name: sha256(OUT / name) for name in content_names},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
