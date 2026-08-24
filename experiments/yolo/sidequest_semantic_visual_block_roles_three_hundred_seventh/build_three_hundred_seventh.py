#!/usr/bin/env python3
"""Bind the eight procedure blocks to already inspected local visual owners."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOCKS = ROOT / "experiments/yolo/sidequest_semantic_procedure_blocks_three_hundred_sixth/THREE_HUNDRED_SIXTH_EIGHT_PROCEDURE_BLOCKS.tsv"
VISUAL = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_R3_97_STATEMENT_EDITION.tsv"


ROLE = {
    "PB01": {
        "role": "PAIRED_SHORT_BATH_PLACEMENTS",
        "reading": "Führe an zwei Plätzen desselben gemeinsamen Beckens je eine kurze Einwirkung aus",
        "object": "gemeinsames zweireihiges Becken-/Figurenfeld",
        "geometry": "eine gemeinsame grüne Umgrenzung mit zwei Figurenreihen; keine sichtbare Reihenfolge",
        "rival": "zwei bloße wiederholte Formularwerte ohne Badehandlung",
        "repair": 1,
    },
    "PB02": {
        "role": "UPPER_PAIR_BALANCE_AND_LINK_CHECK",
        "reading": "Gleiche die beiden oberen Becken lokal ab und prüfe beide Kontakte am Mittelzylinder",
        "object": "oberes Paar aus Figurenbecken und Mittelzylinder",
        "geometry": "zwei lokale Bogenkontakte; weder Einlass noch Auslass ist markiert",
        "rival": "vergleichende ikonographische Paarung ohne Flüssigkeit",
        "repair": 2,
    },
    "PB03": {
        "role": "LOWER_POOL_DISCHARGE_AND_RESTART",
        "reading": "Führe den verbrauchten Posten des unteren Mehrfigurenfeldes ab und eröffne den nächsten lokalen Aufnahmeplatz",
        "object": "unteres grünes Mehrfigurenfeld",
        "geometry": "örtliches Feld ohne gezeichnete Zuleitung aus den oberen Vignetten",
        "rival": "reine Platzzuweisung ohne physischen Abfluss",
        "repair": 2,
    },
    "PB04": {
        "role": "BASKET_DISCHARGE_THEN_UNASSIGNED_HANDOFF",
        "reading": "Entleere den korbartigen Randposten; setze nach der sichtbaren Lücke einen neuen, noch unzugeordneten Übergabeposten",
        "object": "untere korbartige Randstation plus bildlose Zwischenlücke",
        "geometry": "Besitzerwechsel über eine echte Lücke; keine verbindende Kante",
        "rival": "zwei unabhängige Formularzellen, die nur durch Seitenordnung benachbart sind",
        "repair": 3,
    },
    "PB05": {
        "role": "UNASSIGNED_SETTLING_LEDGER_PAIR",
        "reading": "Halte zwei Absetzvarianten im bildlosen Zwischenposten getrennt, bis ein neuer sichtbarer Besitzer beginnt",
        "object": "ungelöster Zwischenposten zwischen Randstapel und Hauptpaar",
        "geometry": "kein Bildobjekt und keine Kante; nur lokaler Recordplatz",
        "rival": "zwei Abschluss-/Kadenzmuster ohne Prozessinhalt",
        "repair": 3,
    },
    "PB06": {
        "role": "FOUR_OPTION_TRANSFER_PALETTE",
        "reading": "Wähle für den unzugeordneten Zwischenposten eine von vier Übergabevarianten: Folgeüberführung, Abführung, einfache Überführung oder neuer Einsatz",
        "object": "ungelöster Zwischenposten zwischen Randstapel und Hauptpaar",
        "geometry": "vier aufeinanderfolgende geschlossene Zellen ohne sichtbaren Leitungsweg",
        "rival": "Schreiberpalette aus vier Transfer-Kadenzmustern",
        "repair": 2,
    },
    "PB07": {
        "role": "TWIN_PASS_THROUGH_COMPARISON",
        "reading": "Prüfe an beiden Seiten des sichtbaren Bogenpaares je einen Durchlass unter gleicher Einstellung",
        "object": "sichtbar bogenverbundenes Hauptpaar",
        "geometry": "echte Paarverbindung, aber kein Medium, Pfeil oder Umlaufsinn",
        "rival": "bloßer Zustandsvergleich zweier gekoppelter Bildplätze",
        "repair": 1,
    },
    "PB08": {
        "role": "OPEN_FRINGE_BRANCH_START_AND_FLUSH",
        "reading": "Eröffne den linken offenen Fransenlauf mit einer Übergabe und reinige seine offenen Enden vor dem nächsten Record",
        "object": "linke offene Fransen-/Unterlaufstation",
        "geometry": "sichtbar offenes lokales Ende; kein Übergang zum rechten Lauf",
        "rival": "selbständiger Randvermerk ohne Anlagenbetrieb",
        "repair": 1,
    },
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    blocks = read(BLOCKS)
    visual = {r["statement_id"]: r for r in read(VISUAL)}
    role_rows = []
    statement_rows = []
    for block in blocks:
        spec = ROLE[block["block_id"]]
        statement_ids = block["statement_ids"].split("|")
        owners = []
        transitions = []
        constraints = []
        contradictions = []
        for statement_id in statement_ids:
            row = visual[statement_id]
            owners.append(row["owner_bindings"])
            transitions.append(row["owner_transition"])
            constraints.append(row["contact_direction_constraint"])
            contradictions.append(row["hardest_contradiction"])
            statement_rows.append({
                "block_id": block["block_id"],
                "statement_id": statement_id,
                "record_unit_id": block["record_unit_id"],
                "dominant_phase": block["dominant_phase"],
                "visual_owner_binding": row["owner_bindings"],
                "owner_transition": row["owner_transition"],
                "selected_station_role": spec["role"],
                "block_operational_reading_de": spec["reading"],
                "prior_visual_operational_statement_de": row["complete_concrete_operational_statement"],
                "contact_direction_constraint": row["contact_direction_constraint"],
                "role_repair_cost_0_3": spec["repair"],
            })
        role_rows.append({
            "block_id": block["block_id"],
            "record_unit_id": block["record_unit_id"],
            "statement_ids": block["statement_ids"],
            "statement_count": block["statement_count"],
            "process_phase": block["dominant_phase"],
            "selected_station_role": spec["role"],
            "selected_block_reading_de": spec["reading"],
            "visible_object_de": spec["object"],
            "visible_geometry_de": spec["geometry"],
            "owner_bindings": " || ".join(owners),
            "owner_transitions": " || ".join(transitions),
            "contact_constraints": " || ".join(dict.fromkeys(constraints)),
            "strongest_rival_de": spec["rival"],
            "repair_cost_0_3": spec["repair"],
            "hardest_visual_contradictions": " || ".join(dict.fromkeys(contradictions)),
        })
    role_path = HERE / "THREE_HUNDRED_SEVENTH_EIGHT_VISUAL_BLOCK_ROLES.tsv"
    statement_path = HERE / "THREE_HUNDRED_SEVENTH_18_STATEMENT_VISUAL_BINDINGS.tsv"
    write(role_path, role_rows)
    write(statement_path, statement_rows)

    lines = ["# Acht Prozessblöcke an sichtbare Stationen gebunden", "", "Die Rollen sind konkrete Arbeitslesungen der bereits betrachteten Bilder. Ein sichtbarer Kontakt erlaubt eine lokale Paarfunktion, aber nie automatisch Richtung, Kreislauf oder Verbindung zur nächsten Vignette.", ""]
    for row in role_rows:
        lines += [
            f"## {row['block_id']} — {row['selected_station_role']}", "",
            f"**Bildobjekt:** {row['visible_object_de']}.", "",
            f"**Arbeitslesung:** {row['selected_block_reading_de']}.", "",
            f"**Geometrie:** {row['visible_geometry_de']}.", "",
            f"**Stärkster Rivale:** {row['strongest_rival_de']}.", "",
            f"**Reparatur:** {row['repair_cost_0_3']}/3.", "",
        ]
    reading_path = HERE / "THREE_HUNDRED_SEVENTH_VISUAL_STATION_COPYBOOK.md"
    reading_path.write_text("\n".join(lines), encoding="utf-8")

    report_path = HERE / "THREE_HUNDRED_SEVENTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 307: die acht Blöcke bekommen Bildrollen\n\n"
        "Die acht Prozessblöcke sind jetzt an ihre bereits betrachteten lokalen Besitzer gebunden. Vier Lesungen sind unmittelbar anschaulich: zwei kurze Beckenplätze auf f81v, ein lokaler Vergleich der oberen f82r-Paarbecken, zwei Durchlassprüfungen am f83r-Bogenpaar und die Eröffnung/Reinigung des linken offenen Fransenlaufs. Zwei weitere sind plausible lokale Abführ-/Neustartvorgänge.\n\n"
        "Die wichtige kreative Korrektur betrifft PB04–PB06: Wo das Bild zwischen Randkorb und Hauptpaar tatsächlich abreißt, wird kein unsichtbares Rohr erfunden. Dort liest sich die Viererfolge am besten als gelernte Transferpalette für einen unzugeordneten Werkstattposten. Das ist inhaltlich konkreter als UNKNOWN, aber ehrlicher als ein imaginärer Gesamtwasserkreislauf.\n\n"
        "Als nächstes sollte diese Stationsgrammatik die 97 Bio-Aussagen vollständig in fünf Betriebsarten zerlegen: Beschicken, Behandeln, Absetzen, Durchlassen und Abführen.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "blocks": len(role_rows), "bound_statements": len(statement_rows),
        "repair_cost_distribution": {str(cost): sum(int(r["repair_cost_0_3"]) == cost for r in role_rows) for cost in range(4)},
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [BLOCKS, VISUAL]},
        "output_hashes": {p.name: sha(p) for p in [role_path, statement_path, reading_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
