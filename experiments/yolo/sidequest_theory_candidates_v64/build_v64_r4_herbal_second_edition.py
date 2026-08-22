#!/usr/bin/env python3
"""Build R4's complete five-record Herbal second edition."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V60 = ROOT / "experiments/yolo/sidequest_theory_candidates_v60"
V63 = ROOT / "experiments/yolo/sidequest_theory_candidates_v63"
EVENTS_IN = V60 / "V60_SELECTED_381_EVENT_LEDGER.tsv"
TEMPLATE_EVENTS_IN = V63 / "V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv"
FIELDS_IN = V63 / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv"
HERBAL = {"f10r", "f11r", "f55v", "f56r"}

FIELD_READING = {
    "F001": "Nimm den gereinigten unteren Wurzelstock, zerstoße ihn, ziehe ihn in Wasser und Wein aus, gebrauche ein vorgeschriebenes Maß und verwahre den Rest.",
    "F002": "Bereite aus demselben Ansatz eine zweite, nur gelinde erwärmte Anwendung.",
    "F003": "Nimm vor voller Blüte die oberen Teile, zerquetsche sie und gewinne einen Ansatz; halte ein vorgeschriebenes Maß bereit.",
    "F004": "Verbinde einen Anteil dieses Ansatzes mit dem Vorigen und derselben Maßvorgabe.",
    "F005": "Bearbeite die beiden angesetzten Fraktionen mit Öl und verwahre sie als äußerliche Bereitung.",
    "F006": "Sammle junge Blätter und Blüten am schattigen Ort, presse den Auszug zweimal durch Tuch und prüfe ihn auf Klarheit.",
    "F007": "Behalte einen Teil der Blütenkrone getrennt zurück.",
    "F008": "Nimm vom abgebildeten Simplex ein Maß und binde den warmen Brei auf eine geschwollene Stelle.",
    "F009": "Bereite die übrigen Teile als warmen Umschlag und wende sie an, sobald sie bereit sind.",
    "F010": "Setze ein vorgeschriebenes Maß frischer breiter Blätter in Wein oder Wasser an und lasse es ausziehen.",
    "F011": "Rühre den Auszug gleichmäßig und wasche damit die wunde Stelle.",
    "F012": "Führe die weiche Blattfraktion durch Tuch und verwahre sie getrennt.",
    "F013": "Mische ein Maß mit Honig oder Öl zum Ansatz und gebrauche ihn frisch als Auflage.",
    "F014": "Sammle im Frühjahr den dünnen unteren Teil des feucht wachsenden Krauts in vorgeschriebenem Maß.",
    "F015": "Ziehe ihn vor voller Blüte in mildem Wein oder Wasser aus, wende den Anteil am Ziel an.",
    "F016": "Vom abgebildeten Kraut selbst verwende die feuchte Frischbereitung und lasse die Auflage trocknen.",
    "F017": "Trenne den nächsten sichtbaren Pflanzenteil und setze daraus einen zweiten Arbeitsgang an.",
    "F018": "Bewahre diesen Teil als eigene kleine Fraktion auf.",
    "F019": "Trockne Blätter, Köpfe und Stängel getrennt für einen späteren Ansatz.",
    "F020": "Wähle einen Anteil der hellen geöffneten Blüte und dosiere ihn nach dem vorgeschriebenen Maß.",
}

RECORDS = {
    "H1": {
        "owner": "abgebildete skabiosen-/Teufelsabbiss-artige Wurzelpflanze",
        "primary_plant": "Teufelsabbiss- oder Skabiosenfamilie",
        "rival_plant": "beliebige tiefwurzelnde Wiesen-Arzneipflanze",
        "genre": "Simplexartikel: Wurzel, innerer Gebrauch, warmer Zweitgebrauch",
        "translation": "Von der abgebildeten Wurzelpflanze nimm den unteren Stock, reinige und zerstoße ihn. Ziehe ihn in Wasser und etwas Wein aus. Gebrauche ein vorgeschriebenes Maß und verwahre den Rest. Aus demselben Ansatz bereite eine zweite, nur gelinde erwärmte Anwendung.",
        "technical_rival": "Wurzelrohstoff reinigen, extrahieren, eine Standardcharge buchen und den Rest warm weiterverarbeiten.",
    },
    "H2": {
        "owner": "zweite Rubrik derselben f10r-Bildpflanze, jetzt obere Teile",
        "primary_plant": "dieselbe Skabiosen-/Teufelsabbiss-Verwandtschaft",
        "rival_plant": "separater, bildnah nicht unterscheidbarer Simplexartikel",
        "genre": "Simplexartikel: oberirdische Teile und äußerliche Ölbereitung",
        "translation": "Vor voller Blüte sammle die oberen Teile, zerquetsche sie und gewinne Saft oder Sud. Halte ein vorgeschriebenes Maß bereit. Verbinde einen Anteil mit dem vorigen Ansatz, bearbeite beide Fraktionen sanft mit Öl und verwahre die Bereitung zum äußerlichen Gebrauch.",
        "technical_rival": "Obere Pflanzenfraktion separat ausziehen, mit der Vorcharge verbinden und als öligen Werkstoff lagern.",
    },
    "H3": {
        "owner": "kleine schattenliebende Blütenpflanze auf f11r",
        "primary_plant": "Veilchen-artiger Simplex",
        "rival_plant": "kleine Dolden- oder Wurzelpflanze",
        "genre": "Blüten-/Blätterauszug mit warmer Auflage",
        "translation": "Sammle junge Blätter und Blüten am schattigen Ort, presse den Auszug zweimal durch Tuch und prüfe ihn auf Klarheit. Behalte einen Blütenanteil getrennt. Aus einem vorgeschriebenen Maß des übrigen Krauts bereite einen warmen Brei; lege ihn auf die geschwollene Stelle, sobald er bereit ist.",
        "technical_rival": "Schattenkraut in klare Flüssig- und weiche Festfraktion trennen und getrennt verwahren.",
    },
    "H4": {
        "owner": "breitblättriges Kraut auf f55v",
        "primary_plant": "Wegerich-artige Wundpflanze",
        "rival_plant": "Allium-/Bärlauch-artiges Blattkraut",
        "genre": "Wundwaschung plus frische Blattauflage",
        "translation": "Setze ein vorgeschriebenes Maß frischer breiter Blätter in Wein oder Wasser an und lasse es ziehen. Rühre und seihe den Auszug; wasche damit die wunde Stelle. Mische die warme Blattfraktion mit wenig Honig oder Öl und gebrauche den frischen Ansatz als Auflage.",
        "technical_rival": "Breitblatt-Rohstoff in Waschflotte und gebundene weiche Restfraktion aufteilen.",
    },
    "H5": {
        "owner": "feuchtlandliebendes, drüsig-borstiges Kraut auf f56r",
        "primary_plant": "Sonnentau-artiger Simplex",
        "rival_plant": "anderes klebriges Feuchtlandkraut",
        "genre": "klein dosierter Auszug, Frischauflage und getrocknete Teilvorräte",
        "translation": "Sammle im Frühjahr eine kleine Menge des feuchten Krauts. Ziehe den unteren Teil vor voller Blüte in mildem Wein oder Wasser aus; wende den Anteil am bezeichneten Ziel an und lasse die Auflage trocknen. Trenne danach weitere Teile, trockne Blätter, Köpfe und Stängel getrennt und dosiere die helle Blüte nach dem vorgeschriebenen Maß.",
        "technical_rival": "Seltenes klebriges Feuchtlandmaterial in Frischcharge und mehrere trockene Teilposten zerlegen.",
    },
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    events = [row for row in read(EVENTS_IN) if row["page"] in HERBAL]
    template_by_event = {row["event_serial"]: row for row in read(TEMPLATE_EVENTS_IN) if row["page"] in HERBAL}
    fields = [row for row in read(FIELDS_IN) if row["page"] in HERBAL]
    event_rows = []
    for row in events:
        template = template_by_event[row["event_serial"]]
        local = row["LOCAL_IATROMEDICAL_EXPANSION"]
        replacements = {
            "Die aktive Portion verwenden": "Den aktiven Anteil anwenden",
            "Die bereitete Arbeitsflüssigkeit": "Der aktive Ansatz",
            "An die bezeichnete Zielstelle führen": "Das bezeichnete Ziel",
            "Aus dem vorigen Ansatz entnehmen": "Das Vorige wiederaufnehmen",
            "Nimm den bezeichneten Anteil": "Den bezeichneten Anteil wählen",
        }
        local = replacements.get(local, local)
        event_rows.append({
            "event_serial": row["event_serial"],
            "page": row["page"],
            "record_unit_id": row["record_unit_id"],
            "locus": row["locus"],
            "field_id": row["field_id"],
            "statement_id": template["statement_id"],
            "surface_display_only": row["surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "selected_exact_mnemonic": row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
            "v63_event_template": template["event_template"],
            "v63_event_parse_status": template["event_parse_status"],
            "v64_r4_local_source_expansion": local,
            "expansion_source": "V60_SELECTED_MNEMONIC" if row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN" else "IMAGE_GENRE_OR_LOCAL_EXEMPLAR",
            "semantic_status": "CREATIVE_HERBAL_SECOND_EDITION_NOT_CARD_GLOSS",
        })

    field_rows = []
    for row in fields:
        field_rows.append({
            "field_id": row["field_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "statement_id": row["statement_id"],
            "v63_parse_status": row["parse_status"],
            "v63_primary_template": row["primary_template"],
            "selected_source_clause": FIELD_READING[row["field_id"]],
            "technical_rival": RECORDS[row["record_unit_id"]]["technical_rival"],
            "unsupported_nouns": "plant identity|plant part|medium|application site|ailment|quantity unit",
            "status": "COMPLETE_CREATIVE_FIELD_READING",
        })

    record_rows = []
    for record, data in RECORDS.items():
        record_fields = [row["field_id"] for row in field_rows if row["record_unit_id"] == record]
        record_events = [row["event_serial"] for row in event_rows if row["record_unit_id"] == record]
        record_rows.append({
            "record_unit_id": record,
            "page": next(row["page"] for row in field_rows if row["record_unit_id"] == record),
            "field_ids": "|".join(record_fields),
            "event_serials": "|".join(record_events),
            "pictured_owner": data["owner"],
            "primary_plant_wager": data["primary_plant"],
            "strongest_plant_rival": data["rival_plant"],
            "article_genre": data["genre"],
            "complete_selected_translation": data["translation"],
            "complete_technical_rival": data["technical_rival"],
            "strongest_contradiction": "Image identity and every concrete material, action, ailment and body target remain ungrounded by exact cards.",
            "revision_status": "SECOND_EDITION_RECONCILED_WITH_V60_V63",
        })

    assumptions = [
        {"assumption_id": "A01", "scope": "H1|H2", "assumption": "f10r depicts one skabiosen/Teufelsabbiss-like medicinal simple with root and aerial-part uses", "cost": "HIGH", "alternative": "two unrelated rubric texts or generic root-stock exemplar"},
        {"assumption_id": "A02", "scope": "H3", "assumption": "f11r is violet-like and supports a warm poultice", "cost": "HIGH", "alternative": "small umbellifer/root simple and nonmedical fractionation"},
        {"assumption_id": "A03", "scope": "H4", "assumption": "f55v is plantain-like and the fluid is a wound wash", "cost": "HIGH", "alternative": "Allium-like raw material and technical wash liquor"},
        {"assumption_id": "A04", "scope": "H5", "assumption": "f56r is sundew-like and parts are separately dried", "cost": "VERY_HIGH", "alternative": "unidentified sticky wetland plant and stock register"},
        {"assumption_id": "A05", "scope": "ALL", "assumption": "water/wine/oil/honey are plausible local media", "cost": "HIGH", "alternative": "anonymous carrier media"},
        {"assumption_id": "A06", "scope": "ALL", "assumption": "ailments and application sites are supplied by lost exemplar knowledge", "cost": "VERY_HIGH", "alternative": "nonmedical plant processing"},
    ]
    outputs = {
        "events": HERE / "V64_R4_100_EVENT_HERBAL_INTERLINEAR.tsv",
        "fields": HERE / "V64_R4_20_FIELD_HERBAL_EDITION.tsv",
        "records": HERE / "V64_R4_5_RECORD_HERBAL_EDITION.tsv",
        "assumptions": HERE / "V64_R4_UNSUPPORTED_ASSUMPTIONS.tsv",
    }
    write(outputs["events"], event_rows)
    write(outputs["fields"], field_rows)
    write(outputs["records"], record_rows)
    write(outputs["assumptions"], assumptions)
    checks = {
        "events_100": len(event_rows) == 100,
        "fields_20": len(field_rows) == 20,
        "records_5": len(record_rows) == 5,
        "all_fields_have_clause": set(FIELD_READING) == {row["field_id"] for row in field_rows},
        "all_events_once": len({row["event_serial"] for row in event_rows}) == 100,
        "only_herbal_pages": {row["page"] for row in event_rows} == HERBAL,
        "no_f84": all(not row["page"].startswith("f84") for row in event_rows),
        "v60_values_unchanged": all(row["selected_exact_mnemonic"] in {"UNKNOWN", "MASS?", "ANWENDEN?", "BEREIT?", "ANSATZ?", "ZIEL?", "KLAR?", "VORIGES?", "ANTEIL?", "TEMPERIEREN?", "SPÜLEN?", "ABLASSEN?"} for row in event_rows),
    }
    validation = {
        "schema": "SIDEQUEST_V64_R4_HERBAL_SECOND_EDITION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (EVENTS_IN, TEMPLATE_EVENTS_IN, FIELDS_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs.values()},
    }
    (HERE / "V64_R4_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit("V64 R4 validation failed")


if __name__ == "__main__":
    main()
