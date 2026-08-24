#!/usr/bin/env python3
"""Build a three-person apprentice workday for all six ten-page cases."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CASE_DIR = ROOT / "experiments/yolo/sidequest_semantic_complete_workshop_cases_six_hundred_third"
ASTRO_DIR = ROOT / "experiments/yolo/sidequest_semantic_astro_case_interface_six_hundred_fourth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


DAY_PHASE = {
    "C1": "FRUEHER_MORGEN",
    "C2": "VORMITTAG",
    "C3": "MITTAG",
    "C4": "NACHMITTAG",
    "C5": "SPAETER_NACHMITTAG",
    "C6": "ABENDABSCHLUSS",
}

PRODUCT_SHORT = {
    "H1": "milden Grundauszug",
    "H2": "stärkeren Nachauszug",
    "H3": "Blütenauszug",
    "H4": "temperierte Auflage",
    "H5": "konzentrierten Vorrat",
}


ROLES = [
    {
        "person_id": "P1",
        "role_de": "Lehrmeister und Korrektor",
        "learned_inventory_de": "sechs Falltypen; fünf Produktklassen; sechzehn Stationen; dreizehn Astro-Namensräume",
        "daily_job_de": "Bildbesitzer und Fall wählen, optionalen Himmelsplatz zeigen, schwierige Ganzkarten vorsagen, Schluss rücklesen",
        "may_change_meaning": "YES__ONLY_PERSON_WHO_SELECTS_LOCAL_MEANING",
    },
    {
        "person_id": "P2",
        "role_de": "Zubereiter und erster Schreiber",
        "learned_inventory_de": "Produktkarten, Maß-/Quell-/Zielkarten, kurze/lange/vollständige Grade, Herbal-Exemplare",
        "daily_job_de": "Pflanzenmaterial bereiten, Kartenfolge schreiben, Produkt beschriften, später Bio-Arbeit gegenlesen",
        "may_change_meaning": "NO__FOLLOWS_MASTER_AND_EXEMPLAR",
    },
    {
        "person_id": "P3",
        "role_de": "Bad-/Anwendungsbediener und zweiter Schreiber",
        "learned_inventory_de": "Stationsbilder, Bad-/Wasch-/Auflage-/Transferkarten, lokale Astro-Kopierformen",
        "daily_job_de": "Station bedienen, lokale Marke kopieren, Bio-Folge schreiben, Herbal-Charge gegenlesen",
        "may_change_meaning": "NO__FOLLOWS_MASTER_AND_EXEMPLAR",
    },
]


RULES = [
    (1, "Zuerst das Bild zeigen; es setzt Pflanze oder Station stillschweigend."),
    (2, "Den Fall C1 bis C6 nennen; dadurch ist das grobe Arbeitsziel bekannt."),
    (3, "Nur eine der fünf Produktklassen als Hauptcharge wählen."),
    (4, "Maß, Quelle, Ziel, Folge und Grad aus den gemeinsamen Karten bauen."),
    (5, "Spezialhandlung als gelernte Ganzkarte aus dem Exemplar übernehmen."),
    (6, "Y/CHY meint den laufenden Posten; es ist nicht automatisch Schluss."),
    (7, "Schluss nur mit der gelernten terminalen Karte setzen."),
    (8, "Eine Aussage darf über die physische Zeile weiterlaufen."),
    (9, "Bei sichtbarem Besitzerwechsel den Arbeitsgegenstand neu setzen."),
    (10, "Biological-Stationen lokal lesen; niemals alle Röhren zu einem Netz verbinden."),
    (11, "Bei Bedarf genau ein Astro-Instrument wählen; nicht alle drei erzwingen."),
    (12, "Astro-Marke vollständig am Bildplatz kopieren; nicht in Prosa-Stämme zerlegen."),
    (13, "f67, f68 und f69 behalten getrennte Namensräume."),
    (14, "Restcharge nur dann weitertragen, wenn der Fall sie ausdrücklich als Vorrat setzt."),
    (15, "Der zweite Schreiber liest Produkt, Station, Grad und Schluss rückwärts vor."),
]


ERRORS = [
    ("E01", "Bildbesitzer ausgelassen", "falsche Pflanze oder Station", "vor dem ersten Zeichen auf das Bild zeigen"),
    ("E02", "Zeilenende als Satzende gelesen", "Arbeitsgang wird zu früh getrennt", "Aussage bis zur terminalen Karte weiterlesen"),
    ("E03", "jedes sichtbare dy als Schluss behandelt", "offene Y-Karte wird falsch geschlossen", "exakte Kartenidentität prüfen"),
    ("E04", "Y als Stoffname statt laufenden Posten gelesen", "Bezug wechselt unbemerkt", "aktuellen Posten im Record halten"),
    ("E05", "o überall als Wasser gelesen", "unverwandte Karten werden stofflich überladen", "Wasser nur als Fall-/Artikelmedium setzen"),
    ("E06", "Auflage an reine Flüssigkeitsstation gesetzt", "Form passt nicht zur Station", "Produktform vor Funktionswahl prüfen"),
    ("E07", "alle Bio-Leitungen verbunden", "lokale Szenen werden zu einer erfundenen Maschine", "bei jedem sichtbaren Owner resetten"),
    ("E08", "f68-Sternslot als f69-Tag benutzt", "zwei Instrumente erhalten erfundenen Schlüssel", "Namensraum mitkopieren"),
    ("E09", "Astro-Marke wie Prosawort zerlegt", "lokale Etikette bekommt falsche Wortstämme", "ganze Marke kopieren"),
    ("E10", "alle drei Astro-Seiten pro Fall konsultiert", "Werkstattgang wird unnötig schwer", "nur primäres Instrument, zweites nur bei Bedarf"),
    ("E11", "Restcharge über Recordgrenze fortgesetzt", "neuer Besitzer erbt falsches Material", "nur C6 übernimmt ausdrücklich H5-Vorrat"),
    ("E12", "Schreiber erfindet neue Kartenform", "gemeinsames System zerfällt", "Defaultform oder gelernte lokale Variante kopieren"),
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cases = read_tsv(CASE_DIR / "SIX_HUNDRED_THIRD_SIX_COMPLETE_CASES.tsv")
    statements = read_tsv(CASE_DIR / "SIX_HUNDRED_THIRD_116_STATEMENT_CASE_EDITION.tsv")
    events = read_tsv(CASE_DIR / "SIX_HUNDRED_THIRD_381_EVENT_CASE_BINDING.tsv")
    plans = read_tsv(ASTRO_DIR / "SIX_HUNDRED_FOURTH_SIX_CASE_CONDITION_PLANS.tsv")
    plan_by_case = {row["case_id"]: row for row in plans}

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)

    trace = []
    serial = 0
    for case in cases:
        case_id = case["case_id"]
        plan = plan_by_case[case_id]
        case_statements = [row for row in statements if row["case_id"] == case_id]
        prep = [row for row in case_statements if row["phase"] == "PREPARE_PRODUCT"]
        operate = [row for row in case_statements if row["phase"] == "OPERATE_OR_APPLY"]
        for row in prep:
            serial += 1
            ev = events_by_statement[row["statement_id"]]
            trace.append({
                "workday_step": serial,
                "day_phase": DAY_PHASE[case_id],
                "case_id": case_id,
                "task_phase": "PREPARE_PRODUCT",
                "source_id": row["statement_id"],
                "acting_person": "P2",
                "recording_or_checking_person": "P3",
                "visible_owner_or_instrument": row["owner_or_station"],
                "spoken_instruction_de": row["concrete_case_step_de"],
                "written_surface_sequence": " ".join(item["surface"] for item in ev),
                "written_group_count": len(ev),
                "master_check_de": "Pflanzenbild, Produktklasse, Maß und Reihenfolge bestätigen.",
                "learning_mode": "COMPOSE_COMMON_CARDS_PLUS_COPY_WHOLE_EXCEPTIONS",
            })
        serial += 1
        trace.append({
            "workday_step": serial,
            "day_phase": DAY_PHASE[case_id],
            "case_id": case_id,
            "task_phase": "OPTIONAL_ASTRO_CONDITION",
            "source_id": plan["primary_astro_namespace"],
            "acting_person": "P1",
            "recording_or_checking_person": "P3",
            "visible_owner_or_instrument": plan["primary_astro_namespace"],
            "spoken_instruction_de": plan["master_question_de"],
            "written_surface_sequence": "MASTER_SELECTS_ONE_LOCAL_LABEL",
            "written_group_count": "VARIABLE_LOCAL_LABEL",
            "master_check_de": "Richtigen Bildplatz und Namensraum zeigen; keine Prosa-Zerlegung zulassen.",
            "learning_mode": "COPY_COMPLETE_LOCAL_ASTRO_LABEL",
        })
        for row in operate:
            serial += 1
            ev = events_by_statement[row["statement_id"]]
            spoken = (
                f"Arbeite mit dem {PRODUCT_SHORT[row['input_product_id']]} an "
                f"{row['owner_or_station']}: {row['source_operations_de']}."
            )
            trace.append({
                "workday_step": serial,
                "day_phase": DAY_PHASE[case_id],
                "case_id": case_id,
                "task_phase": "OPERATE_OR_APPLY",
                "source_id": row["statement_id"],
                "acting_person": "P3",
                "recording_or_checking_person": "P2",
                "visible_owner_or_instrument": row["owner_or_station"],
                "spoken_instruction_de": spoken,
                "written_surface_sequence": " ".join(item["surface"] for item in ev),
                "written_group_count": len(ev),
                "master_check_de": "Produkt, lokale Station, Arbeitsgrad, Ownerreset und Schluss bestätigen.",
                "learning_mode": "COMPOSE_COMMON_CARDS_PLUS_COPY_WHOLE_EXCEPTIONS",
            })

    role_rows = [{**row} for row in ROLES]
    rule_rows = [{"rule_no": no, "apprentice_rule_de": rule} for no, rule in RULES]
    error_rows = [
        {"error_id": error_id, "apprentice_error_de": error, "damage_de": damage, "correction_de": correction}
        for error_id, error, damage, correction in ERRORS
    ]
    write_tsv(HERE / "SIX_HUNDRED_FIFTH_THREE_PERSON_WORKSHOP.tsv", role_rows, list(role_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTH_FIFTEEN_APPRENTICE_RULES.tsv", rule_rows, list(rule_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTH_122_STEP_WORKDAY_TRACE.tsv", trace, list(trace[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTH_TWELVE_COMMON_ERRORS.tsv", error_rows, list(error_rows[0]))

    md = ["# Ein vollständiger Arbeitstag der Dreipersonen-Werkstatt", ""]
    for case in cases:
        case_id = case["case_id"]
        md.extend([
            f"## {DAY_PHASE[case_id]} — {case_id}: {case['title_de']}",
            "",
            case["continuous_case_de"],
            "",
        ])
        for row in [item for item in trace if item["case_id"] == case_id]:
            md.append(
                f"- **{row['workday_step']} / {row['acting_person']} / {row['task_phase']}** — "
                f"{row['spoken_instruction_de']} Schrift: `{row['written_surface_sequence']}`"
            )
        md.append("")
    (HERE / "SIX_HUNDRED_FIFTH_COMPLETE_WORKDAY.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    report = """# Sechshundertfünfte Runde: ein Arbeitstag mit drei Personen

## Ergebnis

Das System ist als kleine Werkstatt lehrbar. Drei Personen genügen:

- der Lehrmeister setzt Bildbesitzer, Fall und gegebenenfalls Himmelsplatz;
- der erste Schreiber bereitet Produkte und schreibt die Herbal-Karten;
- der zweite bedient Bad-/Anwendungsstationen, schreibt Biological und kopiert Astro-Marken.

Beide Schreiber lesen die Arbeit des anderen zurück. Niemand außer dem Lehrmeister muss freie Bedeutungen erfinden.

## Der Tag

Der Durchlauf hat 122 Schritte: 19 Zubereitungsaussagen, sechs optionale Astro-Wahlen und 97 Stationsaussagen. Früh beginnt die milde Waschcharge; vormittags folgt der stärkere Mehrstationsgang; mittags die Blütenwaschung; nachmittags die Auflage; danach werden Restcharge und Vorrat behandelt.

## Warum mehrere Hände kein Problem sind

Die Schreiber teilen nicht zwingend dieselbe sichtbare Vorliebe, aber sie teilen dieselben Kartenwerte und Falltypen. Die Oberfläche darf einer gelernten lokalen Variante folgen. Der Korrektor prüft nur vier Dinge: richtiger Bildbesitzer, richtige Produktklasse, richtige lokale Station und richtiger Schluss.

## Wichtigste Lehrlingsfallen

Die größten Fehler wären: Zeilenende als Satzende lesen, jedes dy als Schluss nehmen, Y als Stoffnamen lesen, alle Röhren verbinden, o überall zu Wasser machen, oder Astro-Marken wie Prosawörter zerlegen. Die zwölf Fehlerkorrekturen bilden ein sehr kurzes Curriculum.

## Ergebnis für die Arbeitstheorie

Unser Schreibsystem braucht keine komplizierte Geheimgrammatik. Es braucht:

1. eine kleine gemeinsame Komponentenlehre;
2. gelernte Ganzkarten für Fachhandlungen;
3. stille Bildargumente;
4. lokale Astro-Etiketten aus dem Muster;
5. einen Lehrmeister, der den konkreten Fall auswählt.

## Nächster Schritt

Jetzt kürzen wir das aktive Wörterbuch auf echte Werkstattwörter. Jede Primärglosse, die noch wie ein ganzer Satz klingt, wird auf ein kurzes Wort oder eine kurze Handlung reduziert; die ausführliche Bedeutung bleibt nur in der Falllesung.
"""
    (HERE / "SIX_HUNDRED_FIFTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "people": len(role_rows),
        "rules": len(rule_rows),
        "workday_steps": len(trace),
        "preparation_steps": sum(row["task_phase"] == "PREPARE_PRODUCT" for row in trace),
        "astro_choices": sum(row["task_phase"] == "OPTIONAL_ASTRO_CONDITION" for row in trace),
        "station_steps": sum(row["task_phase"] == "OPERATE_OR_APPLY" for row in trace),
        "written_prose_groups": sum(int(row["written_group_count"]) for row in trace if str(row["written_group_count"]).isdigit()),
        "decision": "THREE_PERSON_MASTER_GUIDED_WORKSHOP_IS_TEACHABLE",
    }
    (HERE / "SIX_HUNDRED_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
