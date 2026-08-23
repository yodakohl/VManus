#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SCENARIO = ROOT / "experiments/yolo/sidequest_semantic_herbal_source_nomination_hundred_sixty_eighth/HUNDRED_SIXTY_EIGHTH_53_EVENT_H3_TO_B4_SCENARIO.tsv"
H3_EXPANSION = ROOT / "experiments/yolo/sidequest_semantic_f11r_material_class_hundred_sixty_ninth/HUNDRED_SIXTY_NINTH_17_EVENT_F11R_MATERIAL_READING.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CLAUSES = [
    ("H3-S001", "H3", "MAKE_WASH_EXTRACT", "Kochgut | Sudansatz | Auswringen | Stehzeit | Nachseihen | Klarauszug | Endzugabe; Schluss", "Koche das bestimmte blau bluehende Waschkraut in Wasser. Druecke es durch ein Leinentuch aus, lass die Fluessigkeit im Gefaess stehen, seihe sie nochmals klar und gib den vorgesehenen Endzusatz bei.", "A01|A02|A03|A04|A05|A06|A07"),
    ("H3-S002", "H3", "RESERVE_ADDITIVE", "Zugabeteil", "Lege einen weiteren Teil des vorgesehenen Zusatzes bereit.", "A07"),
    ("H3-S003", "H3", "MEASURE_BATCH", "vom vorigen | dies | Bearbeiten | dies | Sollmass", "Nimm vom vorigen klaren Ansatz, arbeite diesen Anteil durch und bringe ihn auf das vorgeschriebene Mass.", "A08"),
    ("H3-S004", "H3", "READY_BATCH", "Folgeposten | Weiterverarbeitung | bereit | dies", "Bereite auch den Folgeanteil fertig und halte den klaren Waschauszug fuer die Stationsarbeit bereit.", "A08"),
    ("B4-S004", "B4", "PREPARE_STATION", "Festsetzen; Schluss", "Fixiere die Waschstation fuer die betroffene Stelle.", "A09|A10|A11"),
    ("B4-S005", "B4", "CHARGE_INSERT", "Einlage | ueberfuehren | lange einwirken; Schluss", "Setze die Leineneinlage ein, traenke sie mit dem vorbereiteten Auszug und lasse die Charge laenger darin einwirken.", "A08|A09"),
    ("B4-S006", "B4", "FIRST_PASS", "durchlassen; Schluss", "Lasse den Auszug einmal durch die Einlage in das Aufnahmebecken laufen.", "A09|A10"),
    ("B4-S007", "B4", "SECOND_PASS", "durchlassen; Schluss", "Fuehre denselben Auszug ein zweites Mal durch dieselbe Einlage.", "A09|A10"),
    ("B4-S008", "B4", "HOLD_MEASURED_CHARGE", "Sollmass | laenger bearbeiten | Langhalt | kurz einwirken; Schluss", "Bemiss den doppelt durchgelassenen Auszug, halte ihn in der Arbeitsstation und lasse ihn kurz auf die Einlage einwirken.", "A08|A09"),
    ("B4-S009", "B4", "SETTLE", "kurz absetzen; Schluss", "Lass den behandelten Auszug kurz im Becken absetzen.", "A05"),
    ("B4-S010", "B4", "MARK_READY", "fertig", "Markiere die geklaerte Waschcharge als fertig.", "A08"),
    ("B4-S011", "B4", "WARM_AND_DRAW_LEFT", "Sollmass | kurz waermen | Langfortsetzung | Anteil zugeben | ueberfuehren | weiter | Kurzabzug; Schluss", "Bemiss an der linken Unterlaufstation eine Teilmenge, waerme sie kurz, gib den reservierten Zusatz bei und ziehe eine kleine Fraktion in das untere Gefaess ab.", "A07|A10"),
    ("B4-S012", "B4", "DRAIN_LEFT", "abfuehren; Schluss", "Fuehre den verbleibenden Posten am linken Unterlauf ab.", "A10"),
    ("B4-S013", "B4", "SETTLE_CONTINUATION", "Weiter einsetzen | kurz absetzen; Schluss", "Setze die Weiterfraktion in das naechste Becken und lass sie kurz absetzen.", "A05|A10"),
    ("B4-S014", "B4", "SHORT_RUN", "Ansatz | dies | Kurzdurchgang | Laufschluss", "Fuehre diesen Ansatz durch den kurzen Lauf bis in den naechsten Empfaenger.", "A10"),
    ("B4-S015", "B4", "APPLY_CLEAR_WASH", "Anteil zugeben | Klarauszug | Anteil | Zielpassage | Kurzsammlung | abfuehren; Schluss", "Gib an der rechten Station eine Portion Klarauszug zu, fuehre sie zur bezeichneten Koerperstelle, wasche die gereizte Stelle und lass die gebrauchte Fluessigkeit ablaufen.", "A08|A10|A11|A12"),
    ("B4-S016", "B4", "FINAL_RINSE", "weiterer Anteil | dorthin | Quellausguss | kurz absetzen; Schluss", "Bringe einen weiteren Anteil an dieselbe Zielstelle, spuele mit frischem Wasser nach und lass den Ablauf kurz im letzten Becken stehen.", "A02|A10|A11|A12"),
]


SUPPLIES = [
    ("A01", "blue flowering wash herb", "blau bluehendes Waschkraut", "PICTURE_OWNER", "DIRECT_VISIBLE_CLASS", "Art bleibt offen"),
    ("A02", "water solvent", "Wasser als Koch- und Nachspuelfluessigkeit", "WORKSHOP_DEFAULT", "SELECTED_CONCRETE_DEFAULT", "Wein bleibt moeglicher Rezepttausch"),
    ("A03", "cooking vessel", "Kochgefaess", "OPERATION_IMPLIED", "NECESSARY_TOOL", "Form nicht sichtbar"),
    ("A04", "linen pressing cloth", "Leinentuch zum Ausdruecken", "OPERATION_IMPLIED", "SELECTED_TOOL", "Handpresse oder Sieb bleibt moeglich"),
    ("A05", "settling vessel", "Absetzbecken oder Gefaess", "OPERATION_AND_IMAGE", "NECESSARY_CONTAINER", "genaue Gefaessgrenze lokal offen"),
    ("A06", "fine straining cloth", "feineres Leinentuch zum Nachseihen", "OPERATION_IMPLIED", "SELECTED_TOOL", "anderes Siebmaterial moeglich"),
    ("A07", "final additive", "vorgesehener Zusatz", "CARD_LICENSED_IDENTITY_SILENT", "MASTER_EXEMPLAR_REQUIRED", "Stoffname fehlt"),
    ("A08", "same prepared batch", "derselbe f11r-Klarauszug in B4", "CROSS_PAGE_WORKSHOP_SCENARIO", "SELECTED_HANDOFF", "kein sichtbarer Querverweis"),
    ("A09", "linen insert", "Leineneinlage oder Filterpolster", "CARD_PLUS_APPARATUS", "SELECTED_OBJECT", "Material nicht ausgeschrieben"),
    ("A10", "local flow direction", "lokaler Weg von Station zu Empfaenger", "IMAGE_GEOMETRY", "LOCAL_ONLY", "keine globale Flussrichtung"),
    ("A11", "affected body target", "bezeichnete gereizte Koerperstelle", "HUMAN_FIGURE_OWNER", "SELECTED_TARGET", "Anatomie und Leiden fehlen"),
    ("A12", "wound or inflammation wash", "aeussere Wund- oder Reizwaschung", "HISTORICAL_AND_PROCESS_EXPANSION", "SELECTED_PURPOSE", "kein einzelnes Kartenwort bedeutet Wunde"),
]


def main() -> None:
    scenario = read_tsv(SCENARIO)
    h3_exp = {row["event_serial"]: row for row in read_tsv(H3_EXPANSION)}
    clause_rows = [
        {
            "sequence": index,
            "statement_id": statement_id,
            "record_unit_id": record,
            "recipe_phase": phase,
            "unchanged_atomic_chain_de": chain,
            "continuous_recipe_de": recipe,
            "silent_supply_ids": supplies,
        }
        for index, (statement_id, record, phase, chain, recipe, supplies) in enumerate(CLAUSES, 1)
    ]
    write_tsv(OUT / "HUNDRED_SEVENTIETH_17_CLAUSE_RECIPE.tsv", clause_rows)

    clause_by_id = {row["statement_id"]: row for row in clause_rows}
    event_rows = []
    for row in scenario:
        clause = clause_by_id[row["statement_id"]]
        serial = row["event_serial"]
        local_expansion = h3_exp[serial]["material_expansion_de"] if row["source_record"] == "H3" else clause["continuous_recipe_de"]
        event_rows.append(
            {
                "combined_order": row["combined_order"],
                "source_record": row["source_record"],
                "page": row["page"],
                "event_serial": serial,
                "statement_id": row["statement_id"],
                "visible_surface": row["visible_surface"],
                "master_card_id": row["master_card_id"],
                "unchanged_atomic_value_de": row["atomic_value_de"],
                "recipe_phase": clause["recipe_phase"],
                "concrete_recipe_expansion_de": local_expansion,
                "silent_supply_ids": clause["silent_supply_ids"],
                "dictionary_change": "NO",
            }
        )
    write_tsv(OUT / "HUNDRED_SEVENTIETH_53_EVENT_CONTINUOUS_RECIPE.tsv", event_rows)

    supply_rows = [
        {
            "supply_id": sid,
            "silent_noun_en": noun,
            "selected_value_de": value,
            "licensed_by": licensed,
            "working_status": status,
            "live_substitution_de": rival,
        }
        for sid, noun, value, licensed, status, rival in SUPPLIES
    ]
    write_tsv(OUT / "HUNDRED_SEVENTIETH_12_SILENT_SUPPLIES.tsv", supply_rows)

    summary = {
        "scenario_sha256": hashlib.sha256(SCENARIO.read_bytes()).hexdigest(),
        "material_expansion_sha256": hashlib.sha256(H3_EXPANSION.read_bytes()).hexdigest(),
        "events": len(event_rows),
        "clauses": len(clause_rows),
        "silent_supplies": len(supply_rows),
        "dictionary_changes": 0,
        "selected_purpose": "EXTERNAL_ASTRINGENT_WASH_THROUGH_LOCAL_STATIONS",
        "cross_page_pointer_claim": False,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
