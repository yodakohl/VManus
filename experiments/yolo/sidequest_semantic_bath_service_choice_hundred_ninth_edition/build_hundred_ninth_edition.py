#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_bio_rewrite_hundred_eighth_edition/HUNDRED_EIGHTH_56_BIO_STATEMENT_REWRITE.tsv"


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


STATIONS = [
    ("B2_UPPER_PAIRED_BASINS_AND_CYLINDER", "ZUBEREITUNG_SERVICE", "Doppelbecken und Zylinder zeigen Arbeitsgefäße, aber keinen bestimmten Körperkontakt."),
    ("B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE", "ZUBEREITUNG_SERVICE", "Gerät und Einzelknoten tragen Durchlauf-, Absetz- und Klarlaufhandlungen."),
    ("B2_MIDDLE_RIGHT_RECLINING_FIGURE_VESSEL", "KOERPER_BAD_ANWENDUNG", "Eine liegende Figur befindet sich unmittelbar im eigenen kleinen Becken."),
    ("B2_LOWER_GREEN_MULTI_FIGURE_POOL", "KOERPER_BAD_ANWENDUNG", "Mehrere Figuren besitzen gemeinsam das grüne Becken."),
    ("B2_LOWER_POOL_EDGE_STATIONS", "KOERPER_BAD_ANWENDUNG", "Die Randstationen bedienen das sichtbar figurenbezogene untere Becken."),
    ("B3_UPPER_MARGIN_OPEN_FAN_STATION", "ZUBEREITUNG_SERVICE", "Offene Fächerstation ohne eindeutigen Körperkontakt."),
    ("B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION", "ZUBEREITUNG_SERVICE", "Rundes Einzelgefäß mit Dosier- und Umsetzschritten."),
    ("B3_LOWER_MARGIN_BASKET_VESSEL_STATION", "ZUBEREITUNG_SERVICE", "Korb-/Randgefäß eignet sich als Vorbereitungs- oder Siebstation."),
    ("B3_LOCAL_TRANSITION_BATCH_FROM_EXEMPLAR", "ZUBEREITUNG_SERVICE", "Kein Bildkontakt; der Batch muss aus dem gelernten Werkstattexemplar kommen."),
    ("B3_MAIN_ARCH_LINKED_PAIR_WITH_INCOMING_BATCH", "KOERPER_BAD_ANWENDUNG", "Der Ansatz wird ausdrücklich an das sichtbar gekoppelte Hauptpaar übergeben."),
    ("B3_MAIN_ARCH_LINKED_PAIR", "KOERPER_BAD_ANWENDUNG", "Das lokal gekoppelte Figurenpaar ist der stärkste Körper-/Badebesitzer."),
]
CHOICE = {owner: role for owner, role, _ in STATIONS}
REASON = {owner: reason for owner, _, reason in STATIONS}


def medical(text):
    replacements = [
        ("Arbeitsflüssigkeit", "Bad- oder Behandlungsflüssigkeit"),
        ("Arbeitsanteil", "Anwendungsanteil"),
        ("Arbeitsgang", "Anwendungsgang"),
        ("Charge", "Badansatz"),
        ("Übergangsansatz", "vorbereiteter Badansatz"),
        ("Rand- und Servicecharge", "Randcharge des Bades"),
        ("Hauptpaars", "behandelten Hauptpaars"),
        ("Hauptpaar", "behandelte Hauptpaar"),
    ]
    for old, new in replacements:
        text = text.replace(old, new).replace(old.lower(), new.lower())
    return "Körper-/Badelesung: " + text


def service(text):
    replacements = [
        ("für die liegende Figur", "für den Betrieb des kleinen Liegebeckens"),
        ("grünen Mehrpersonenbecken", "grünen Sammelbecken"),
        ("liegenden Posten", "laufenden Posten"),
        ("Badansatz", "Arbeitsansatz"),
        ("Hauptpaars", "gekoppelten Hauptstation"),
        ("Hauptpaar", "gekoppelte Hauptstation"),
    ]
    for old, new in replacements:
        text = text.replace(old, new).replace(old.capitalize(), new.capitalize())
    return "Service-/Betriebslesung: " + text


def main():
    source = load(SOURCE)
    rows = []
    for row in source:
        owners = row["owner_sequence"].split("|")
        roles = [CHOICE[o] for o in owners]
        if "KOERPER_BAD_ANWENDUNG" in roles and row["statement_id"] not in {"B3-S016"}:
            selected = "KOERPER_BAD_ANWENDUNG"
        else:
            selected = "ZUBEREITUNG_SERVICE"
        med = medical(row["creative_practical_reading_de"])
        srv = service(row["creative_practical_reading_de"])
        selected_text = med.removeprefix("Körper-/Badelesung: ") if selected == "KOERPER_BAD_ANWENDUNG" else srv.removeprefix("Service-/Betriebslesung: ")
        rows.append({
            "statement_order": row["statement_order"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "owner_sequence": row["owner_sequence"],
            "visible_surface_sequence": row["visible_surface_sequence"],
            "medical_bath_expansion_de": med,
            "service_maintenance_expansion_de": srv,
            "selected_local_role": selected,
            "selected_reading_de": selected_text,
            "selection_reason": " | ".join(REASON[o] for o in owners),
            "connection_rule": row["connection_rule"],
        })
    write_tsv("HUNDRED_NINTH_56_BATH_VS_SERVICE_CHOICES.tsv", rows)

    station_rows = []
    for owner, role, reason in STATIONS:
        members = [r for r in rows if owner in r["owner_sequence"].split("|")]
        station_rows.append({
            "owner": owner,
            "selected_local_role": role,
            "statement_count": str(len(members)),
            "statement_ids": "|".join(r["statement_id"] for r in members),
            "why": reason,
            "strongest_rival": "KOERPER_BAD_ANWENDUNG" if role == "ZUBEREITUNG_SERVICE" else "ZUBEREITUNG_SERVICE",
        })
    write_tsv("HUNDRED_NINTH_STATION_ROLE_TABLE.tsv", station_rows)

    by_record = defaultdict(list)
    for row in rows:
        by_record[row["record_unit_id"]].append(row)
    record_rows = []
    for record, members in by_record.items():
        record_rows.append({
            "record_unit_id": record,
            "page": members[0]["page"],
            "service_statement_count": str(sum(r["selected_local_role"] == "ZUBEREITUNG_SERVICE" for r in members)),
            "body_bath_statement_count": str(sum(r["selected_local_role"] == "KOERPER_BAD_ANWENDUNG" for r in members)),
            "continuous_selected_reading_de": " ".join(r["selected_reading_de"] for r in members),
        })
    write_tsv("HUNDRED_NINTH_TWO_SELECTED_HYBRID_RECORDS.tsv", record_rows)

    counts = Counter(r["selected_local_role"] for r in rows)
    report = [
        "# Hundertneunte Runde: Bad und Betrieb gehören zusammen", "",
        "Die Bildbesitzer erzwingen keine reine Medizin und kein reines Wasserwerk. Die beste konkrete",
        "Arbeitsfassung ist ein therapeutischer Badebetrieb, in dem dieselben Schreiber sowohl Zubereitungs-",
        "und Servicechargen als auch körperbezogene Badeanwendungen notieren.", "",
        f"Von 56 Aussagen werden {counts['ZUBEREITUNG_SERVICE']} zunächst als Zubereitung/Service und",
        f"{counts['KOERPER_BAD_ANWENDUNG']} als Körper-/Badeanwendung gelesen. Das ist keine vorsichtige",
        "Enthaltung, sondern eine konkrete Aufgabenteilung nach sichtbarem Besitzer.", "",
        "Die Randgefäße und der f83r-Übergangsansatz tragen Vorbereitung, Dosierung, Durchlauf, Absetzen",
        "und Übergabe. Das kleine f82r-Liegebecken, das grüne Figurenbecken, seine Randstationen und das",
        "f83r-Hauptpaar tragen die Anwendung. Wo eine Aussage beide Bereiche kreuzt, wird der Wechsel",
        "ausgeschrieben und keine Leitung ergänzt.", "",
        "Aktueller Inhaltslead: THERAPEUTISCHER_BADEBETRIEB_MIT_EIGENER_ZUBEREITUNG_UND_WARTUNG.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_NINTH_BATH_SERVICE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "statements": len(rows), "roles": dict(counts), "station_families": len(station_rows)}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
