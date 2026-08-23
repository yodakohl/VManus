#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_creative_owner_resolution_hundred_seventh_edition/HUNDRED_SEVENTH_254_REVISED_OWNER_BINDING.tsv"
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_centennial_working_edition/HUNDREDTH_116_STATEMENT_TRANSLATION.tsv"


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


OWNER_LABEL = {
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": "die Arbeitsflüssigkeit der oberen Doppelbecken mit Mittelzylinder",
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": "die Charge des linken Mittelgeräts mit seinem Einzelknoten",
    "B2_MIDDLE_RIGHT_RECLINING_FIGURE_VESSEL": "die Portion für die liegende Figur im eigenständigen kleinen Liegebecken",
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": "den Ansatz des grünen Mehrpersonenbeckens",
    "B2_LOWER_POOL_EDGE_STATIONS": "die Rand- und Servicecharge des unteren Beckens",
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "die Charge der oberen offenen Fächerstation",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "die Charge des runden Randgefäßes",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "die Charge des unteren Korb-/Randgefäßes",
    "B3_LOCAL_TRANSITION_BATCH_FROM_EXEMPLAR": "den örtlichen Übergangsansatz aus dem Werkstattexemplar",
    "B3_MAIN_ARCH_LINKED_PAIR_WITH_INCOMING_BATCH": "den eingehenden Ansatz des sichtbar gekoppelten Hauptpaars",
    "B3_MAIN_ARCH_LINKED_PAIR": "den Ansatz des sichtbar gekoppelten Hauptpaars",
}


OVERRIDE = {
    "B2-S011": "Für die liegende Figur im kleinen Becken: Nimm aus dem gesetzten Ansatz eine Portion, gib eine weitere Portion zu, lasse sie länger einwirken und schließe den Schritt.",
    "B2-S012": "Ziehe den Arbeitsanteil aus dem kleinen Liegebecken ab. Wechsle ohne behauptete Leitungsverbindung zum grünen Mehrpersonenbecken: Nimm dort den Klarlauf, halte ihn kurz bereit, setze ihn länger an, führe ihn nach Sollmaß ab, vollende den Posten und schließe.",
    "B3-S016": "Führe die Charge des unteren Korbgefäßes ab. Beginne jenseits der Bildlücke einen eigenen Übergangsansatz, setze ihn um und schließe; die Lücke ist keine Leitung.",
    "B3-S017": "Den örtlichen Übergangsansatz länger ansetzen und schließen.",
    "B3-S018": "Den örtlichen Übergangsansatz kurz absetzen lassen und schließen.",
    "B3-S019": "Den örtlichen Übergangsansatz ansetzen, absetzen lassen und schließen.",
    "B3-S020": "Den örtlichen Übergangsansatz zur im Exemplar bezeichneten Stelle führen, dort abführen und schließen.",
    "B3-S021": "Am örtlichen Übergangsansatz das Sollmaß einstellen, ihn am bezeichneten Platz bereithalten, dort absetzen lassen, kurz prüfen, erneut bereitstellen, umsetzen und schließen.",
    "B3-S022": "Danach den nächsten Übergangsansatz umsetzen und schließen.",
    "B3-S023": "Den Übergangsansatz abführen und schließen.",
    "B3-S024": "Den Übergangsansatz umsetzen und schließen.",
    "B3-S025": "Den nächsten Übergangsansatz ansetzen, umsetzen und schließen.",
    "B3-S026": "Den Übergangsansatz von seinem gesetzten Ort umsetzen, bis zum Sollmaß absetzen lassen, erneut umsetzen, eine Portion zugeben und bereit halten. Dann ohne behauptete Leitung zum sichtbar gekoppelten Hauptpaar wechseln, den eingehenden Ansatz dort länger sammeln und schließen.",
}


def main():
    clauses = [r for r in load(CLAUSES) if r["record_unit_id"] in {"B2", "B3"}]
    source = [r for r in load(SOURCE) if r["record_unit_id"] in {"B2", "B3"}]
    by_statement = defaultdict(list)
    for row in clauses:
        by_statement[row["statement_id"]].append(row)

    rows = []
    for row in source:
        owners = list(dict.fromkeys(c["final_owner"] for c in by_statement[row["statement_id"]]))
        statuses = list(dict.fromkeys(c["final_owner_status"] for c in by_statement[row["statement_id"]]))
        if row["statement_id"] in OVERRIDE:
            reading = OVERRIDE[row["statement_id"]]
        elif len(owners) == 1:
            reading = f"Für {OWNER_LABEL[owners[0]]}: {row['card_near_workshop_reading_de'].rstrip('.')} .".replace(" .", ".")
        else:
            raise AssertionError((row["statement_id"], owners))
        if any("REGISTER" in status for status in statuses):
            rule = "LOCAL_EXEMPLAR_BATCH__NO_DRAWN_CONNECTION"
        elif any("FORWARD" in status for status in statuses):
            rule = "FORWARD_TO_DIRECT_VISIBLE_PAIR__NO_DIRECTION"
        elif len(owners) > 1:
            rule = "EXPLICIT_OWNER_RESET__NO_CARRY"
        else:
            rule = "SINGLE_LOCAL_OWNER"
        rows.append({
            "statement_order": row["statement_order"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "physical_loci": row["physical_loci"],
            "visible_surface_sequence": row["visible_surface_sequence"],
            "owner_sequence": "|".join(owners),
            "owner_status_sequence": "|".join(statuses),
            "literal_atom_reading_de": " || ".join(c["owner_expanded_literal_clause_de"] for c in by_statement[row["statement_id"]]),
            "creative_practical_reading_de": reading,
            "connection_rule": rule,
        })

    write_tsv(OUT / "HUNDRED_EIGHTH_56_BIO_STATEMENT_REWRITE.tsv", rows)
    record_rows = []
    by_record = defaultdict(list)
    for row in rows:
        by_record[row["record_unit_id"]].append(row)
    for record, members in by_record.items():
        record_rows.append({
            "record_unit_id": record,
            "page": members[0]["page"],
            "statement_count": str(len(members)),
            "statement_ids": "|".join(r["statement_id"] for r in members),
            "continuous_creative_reading_de": " ".join(r["creative_practical_reading_de"] for r in members),
            "visible_connection_ceiling": (
                "Fuenf lokale Stationsfamilien; das kleine Liegebecken ist nicht an die nahe Linie angeschlossen."
                if record == "B2" else
                "Drei Randstationen, ein exemplarischer Uebergangsansatz und ein lokal gekoppeltes Hauptpaar; kein globaler Kreislauf."
            ),
        })
    write_tsv(OUT / "HUNDRED_EIGHTH_TWO_CONTINUOUS_BIO_RECORDS.tsv", record_rows)

    md = ["# Hundertachte Runde: f82r und f83r neu gelesen", ""]
    for rec in record_rows:
        md += [f"## {rec['record_unit_id']} — {rec['page']}", "", rec["continuous_creative_reading_de"], "", f"Bildgrenze: {rec['visible_connection_ceiling']}", ""]
    (OUT / "HUNDRED_EIGHTH_COMPLETE_BIO_REWRITE.md").write_text("\n".join(md), encoding="utf-8")
    report = [
        "# Hundertachte Runde: konkrete Bio-Reparatur", "",
        "Die zwei größten Bio-Records sind jetzt vollständig mit den in R107 geschlossenen Besitzern rückgelesen.",
        "f82r hat fünf lokale Stationsfamilien. Besonders wichtig ist der Wechsel vom eigenständigen kleinen",
        "Liegebecken zum grünen Mehrpersonenbecken in B2-S012; er wird als Werkstattschritt, nicht als Leitung gelesen.", "",
        "f83r hat drei sichtbare Randstationen, danach einen im Exemplar gelernten Übergangsansatz und zuletzt",
        "das sichtbar gekoppelte Hauptpaar. Der Übergangsansatz ist eine echte Arbeitsannahme: Er macht die lange",
        "Textfolge handhabbar, behauptet aber weder Rohr noch Wasserlauf noch Richtung.", "",
        "Die Ausgabe umfasst 56 Aussagen: 22 in B2 und 34 in B3. Dreizehn frühere pauschale Besitzertexte wurden",
        "gezielt ersetzt; alle übrigen Aussagen erhalten die kleinste lokale sichtbare Stationsadresse.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_EIGHTH_BIO_REWRITE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE",
        "statements": len(rows),
        "B2": sum(r["record_unit_id"] == "B2" for r in rows),
        "B3": sum(r["record_unit_id"] == "B3" for r in rows),
        "manual_overrides": sum(r["statement_id"] in OVERRIDE for r in rows),
        "connection_rules": dict(Counter(r["connection_rule"] for r in rows)),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
