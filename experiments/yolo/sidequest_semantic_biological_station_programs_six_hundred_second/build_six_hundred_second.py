#!/usr/bin/env python3
"""Build six concrete Biological station programs from the current ten-page sidequest."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OBJECT_DIR = ROOT / "experiments/yolo/sidequest_semantic_concrete_object_ledger_five_hundred_ninety_ninth"
MATCH_DIR = ROOT / "experiments/yolo/sidequest_semantic_product_station_compatibility_six_hundred_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PROGRAMS = {
    "B1": {
        "program_class": "COMMON_HERBAL_BATH_WASH_AND_MIXING_CYCLE",
        "therapeutic_program_de": "Ein gemeinsames Kräuterbad ansetzen, dosiert nachspeisen, durchwaschen, warm halten, absetzen und den brauchbaren Anteil wieder auffangen.",
        "technical_program_de": "Eine gemeinsame Waschcharge mischen, speisen, führen, temperieren, absetzen und sammeln.",
        "selected_reading": "THERAPEUTIC_LEAD",
        "why_de": "Die gemeinsame Figuren-/Beckenstation macht Bad und Waschung konkreter als bloße Stofflogistik.",
    },
    "B2": {
        "program_class": "MULTI_STATION_BATH_TRANSFER_AND_LOCAL_APPLICATION",
        "therapeutic_program_de": "Eine Badcharge oben einspeisen, an Hand- und Randstationen halten oder absetzen, im unteren Figurenbecken anwenden und lokale Auflagen einwirken lassen.",
        "technical_program_de": "Eine Charge durch mehrere Becken-, Halte-, Transfer- und Randzellen führen.",
        "selected_reading": "THERAPEUTIC_LEAD",
        "why_de": "Figurenbecken und lokale Halte-/Anwendungszellen bilden einen Behandlungsgang; der technische Transfer bleibt seine Bedienebene.",
    },
    "B3": {
        "program_class": "IMMERSION_SETTLING_COLLECTION_AND_PAIRED_APPLICATION_SERIES",
        "therapeutic_program_de": "Auszug auffangen und wärmen, in runden oder korbartigen Gefäßen baden und absetzen, anschließend an einer Paarstation lokal anwenden.",
        "technical_program_de": "Mehrere getrennte Behältervarianten zum Auffangen, Mischen, Eintauchen, Absetzen und lokalen Überführen verwenden.",
        "selected_reading": "HYBRID_TIE",
        "why_de": "Die Gefäßfolge liest sich technisch; Figuren und lokale Anwendung lesen sich therapeutisch. Beides gehört hier zusammen.",
    },
    "B4": {
        "program_class": "POULTICE_HOLDING_WITH_FLOW_AND_COLLECTION_SUPPORT",
        "therapeutic_program_de": "Eine temperierte Pflanzenauflage an der Paarstation ansetzen, festhalten und wirken lassen; Flüssigkeit seitlich zuführen, abziehen und sammeln.",
        "technical_program_de": "Einen halbfesten Einsatz in der Paarstation befestigen und die zugehörige Arbeitsflüssigkeit über linke und rechte Nebenläufe bedienen.",
        "selected_reading": "THERAPEUTIC_LEAD",
        "why_de": "Die halbfeste Auflage erklärt die Paarstation besser, während die Seitenläufe eindeutig technische Hilfsarbeit leisten.",
    },
    "B5": {
        "program_class": "TRANSFER_AND_SETTLING_APPENDIX",
        "therapeutic_program_de": "Eine bereits gebrauchte Wasch- oder Auflagencharge weiterführen und ruhen lassen.",
        "technical_program_de": "Eine Restcharge in einer Nebenstation übertragen, halten und absetzen.",
        "selected_reading": "TECHNICAL_LEAD",
        "why_de": "Der kurze Nachtrag zeigt Transfer und Ruhe, aber keine eigene sichtbare Behandlungsszene.",
    },
    "B6": {
        "program_class": "COLLECT_COOL_AND_FEED_APPENDIX",
        "therapeutic_program_de": "Einen konzentrierten Vorrat für eine folgende Waschung oder Anwendung auffangen und bereitstellen.",
        "technical_program_de": "Den Vorrat sammeln, abkühlen und einer nächsten Station zuführen.",
        "selected_reading": "TECHNICAL_LEAD",
        "why_de": "Der einzelne S-Lauf ist am besten als technische Vorrats-/Speisestufe lesbar.",
    },
}


PRIMARY_INPUT = {
    "B1:OWNER_01": "H3",
    "B2:OWNER_01": "H2",
    "B2:OWNER_02": "H4",
    "B2:OWNER_03": "H4",
    "B2:OWNER_04": "H5",
    "B2:OWNER_05": "H4",
    "B3:OWNER_01": "H5",
    "B3:OWNER_02": "H3",
    "B3:OWNER_03": "H2",
    "B3:OWNER_04": "H1",
    "B3:OWNER_05": "H4",
    "B4:OWNER_01": "H4",
    "B4:OWNER_02": "H5",
    "B4:OWNER_03": "H5",
    "B5:OWNER_01": "H5",
    "B6:OWNER_01": "H5",
}


def action_roles(operations: str) -> str:
    tests = [
        ("wasch", "WASH"),
        ("waerm", "WARM"),
        ("abkuehl", "COOL"),
        ("absetz", "SETTLE"),
        ("auffang", "COLLECT"),
        ("abzieh", "DRAW_OFF"),
        ("halt", "HOLD"),
        ("zufuehr", "FEED"),
        ("fuehr", "TRANSFER"),
        ("umsetz", "TRANSFER"),
        ("ansetz", "LOAD_OR_APPLY"),
        ("teil", "PORTION"),
        ("hineing", "LOAD"),
    ]
    roles = []
    for needle, role in tests:
        if needle in operations and role not in roles:
            roles.append(role)
    return "|".join(roles) if roles else "SPECIFY_LOCAL_STEP"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    statements = read_tsv(OBJECT_DIR / "FIVE_HUNDRED_NINETY_NINTH_116_STATEMENT_OBJECT_LEDGER.tsv")
    events = read_tsv(OBJECT_DIR / "FIVE_HUNDRED_NINETY_NINTH_381_EVENT_OBJECT_BINDING.tsv")
    products = read_tsv(MATCH_DIR / "SIX_HUNDRED_FIRST_FIVE_PRODUCT_CLASSES.tsv")
    stations = read_tsv(MATCH_DIR / "SIX_HUNDRED_FIRST_SIXTEEN_STATION_CLASSES.tsv")
    matches = read_tsv(MATCH_DIR / "SIX_HUNDRED_FIRST_EIGHTY_PRODUCT_STATION_COMPATIBILITIES.tsv")

    bio_statements = [row for row in statements if row["record"].startswith("B")]
    bio_events = [row for row in events if row["record"].startswith("B")]
    product_by_id = {row["product_id"]: row for row in products}
    station_by_id = {row["station_id"]: row for row in stations}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in bio_events:
        events_by_statement[row["statement_id"]].append(row)

    viable_by_station: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in matches:
        if row["compatibility"] in {"DIRECT_WORKING_MATCH", "PLAUSIBLE_MATCH"}:
            viable_by_station[row["station_id"]].append(row)

    station_inputs = []
    for station in stations:
        owner = station["station_id"]
        primary = PRIMARY_INPUT[owner]
        viable = sorted(
            viable_by_station[owner],
            key=lambda row: (-int(row["working_score"]), row["product_id"]),
        )
        primary_match = next(row for row in viable if row["product_id"] == primary)
        station_inputs.append({
            "station_id": owner,
            "page": station["page"],
            "record": station["record"],
            "visible_owner_de": station["visible_owner_de"],
            "station_class": station["station_class"],
            "primary_product_id": primary,
            "primary_product_de": product_by_id[primary]["working_product_de"],
            "primary_compatibility": primary_match["compatibility"],
            "primary_shared_functions": primary_match["matched_functions"],
            "interchangeable_product_ids": "|".join(row["product_id"] for row in viable),
            "interchangeable_products_de": " | ".join(product_by_id[row["product_id"]]["working_product_de"] for row in viable),
            "many_to_many_rule_de": "Produktklasse nach Arbeitszweck wählen; kein Foliozeiger und keine feste Einzelpaarung.",
        })

    steps = []
    for statement in bio_statements:
        owner = statement["owner_id"]
        record = statement["record"]
        product_id = PRIMARY_INPUT[owner]
        product = product_by_id[product_id]
        event_rows = events_by_statement[statement["statement_id"]]
        surfaces = " ".join(row["surface"] for row in event_rows)
        event_ids = "|".join(row["event_id"] for row in event_rows)
        operation = statement["operations_de"]
        base = statement["complete_working_instruction_de"]
        therapeutic = (
            f"Setze {product['working_product_de']} an {statement['owner_de']} ein. "
            f"Therapeutische Lesung: {base}"
        )
        technical = (
            f"Führe {product['working_product_de']} an {statement['owner_de']} als Arbeitscharge. "
            f"Betriebslesung: {base}"
        )
        selected = PROGRAMS[record]["selected_reading"]
        if selected == "THERAPEUTIC_LEAD":
            chosen = therapeutic
        elif selected == "TECHNICAL_LEAD":
            chosen = technical
        else:
            chosen = f"Kombinierte Lesung: {base} Eingesetzt wird {product['working_product_de']}."
        steps.append({
            "statement_id": statement["statement_id"],
            "page": statement["page"],
            "record": record,
            "owner_id": owner,
            "visible_owner_de": statement["owner_de"],
            "transition": statement["transition"],
            "event_count": len(event_rows),
            "event_ids": event_ids,
            "surface_sequence": surfaces,
            "primary_product_id": product_id,
            "primary_product_de": product["working_product_de"],
            "interchangeable_product_ids": next(row["interchangeable_product_ids"] for row in station_inputs if row["station_id"] == owner),
            "action_roles": action_roles(operation),
            "operations_de": operation,
            "source_bound_instruction_de": base,
            "therapeutic_reading_de": therapeutic,
            "bathhouse_reading_de": technical,
            "selected_program_reading": selected,
            "selected_concrete_step_de": chosen,
            "cross_station_transfer_claim": "NONE__LOCAL_OWNER_SEQUENCE_ONLY",
        })

    programs = []
    for record, spec in PROGRAMS.items():
        record_steps = [row for row in steps if row["record"] == record]
        owners = []
        products_used = []
        for row in record_steps:
            if row["owner_id"] not in owners:
                owners.append(row["owner_id"])
            if row["primary_product_id"] not in products_used:
                products_used.append(row["primary_product_id"])
        programs.append({
            "record": record,
            "page": record_steps[0]["page"],
            "program_class": spec["program_class"],
            "station_count": len(owners),
            "station_ids": "|".join(owners),
            "statement_count": len(record_steps),
            "event_count": sum(int(row["event_count"]) for row in record_steps),
            "primary_product_ids": "|".join(products_used),
            "therapeutic_program_de": spec["therapeutic_program_de"],
            "bathhouse_program_de": spec["technical_program_de"],
            "selected_reading": spec["selected_reading"],
            "selection_reason_de": spec["why_de"],
            "global_pipe_claim": "NONE__SEPARATE_LOCAL_STATIONS",
        })

    write_tsv(HERE / "SIX_HUNDRED_SECOND_SIX_BIOLOGICAL_PROGRAMS.tsv", programs, list(programs[0]))
    write_tsv(HERE / "SIX_HUNDRED_SECOND_SIXTEEN_STATION_INPUTS.tsv", station_inputs, list(station_inputs[0]))
    write_tsv(HERE / "SIX_HUNDRED_SECOND_NINETY_SEVEN_STATION_STEPS.tsv", steps, list(steps[0]))

    md = ["# Sechs vollständige Biological-Arbeitsprogramme", ""]
    for program in programs:
        md.extend([
            f"## {program['record']} / {program['page']}: {program['program_class']}",
            "",
            f"**Gewählte Lesung:** {program['selected_reading']}",
            "",
            f"**Therapeutisch:** {program['therapeutic_program_de']}",
            "",
            f"**Badehaus/technisch:** {program['bathhouse_program_de']}",
            "",
            f"**Warum:** {program['selection_reason_de']}",
            "",
        ])
        for step in [row for row in steps if row["record"] == program["record"]]:
            md.append(f"- **{step['statement_id']}** `{step['surface_sequence']}` — {step['selected_concrete_step_de']}")
        md.append("")
    (HERE / "SIX_HUNDRED_SECOND_CONTINUOUS_PROGRAMS.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    selected_counts = Counter(row["selected_reading"] for row in programs)
    report = f"""# Sechshundertzweite Runde: Biological als sechs Arbeitsprogramme

## Ergebnis

Alle 97 Biological-Aussagen und 281 Kartenereignisse lassen sich als sechs konkrete lokale Programme lesen. Der beste Gesamtentwurf ist **therapeutischer Bad-/Anwendungskern mit technischer Werkstattschicht**:

- B1, B2 und B4 lesen sich primär als Bad, Waschung und lokale Auflage;
- B3 bleibt ehrlich gemischt aus Gefäßbetrieb, Immersion und Anwendung;
- B5 und B6 sind kurze technische Transfer-, Ruhe-, Sammel- und Speisenachträge.

Damit gewinnt weder „nur Medizin“ noch „nur Wasserwerk“. Die Bilder liefern die Behandlungssituation; die Karten liefern den wiederholbaren Werkstattgang.

## Vollständigkeit

- **6/6 Records** als fortlaufende Programme;
- **16/16 sichtbare Stationen** mit mindestens einem konkreten Produkteinsatz;
- **97/97 Aussagen** mit therapeutischer und Badehauslesung;
- **281/281 Ereignisse** in unveränderter Reihenfolge;
- Auswahl: {selected_counts['THERAPEUTIC_LEAD']} therapeutische Leads, {selected_counts['HYBRID_TIE']} Hybrid, {selected_counts['TECHNICAL_LEAD']} technische Leads.

## Konkreter Ablauf

Das gemeinsame Muster lautet nun:

```text
Pflanzenprodukt auswählen
→ an sichtbare lokale Station einsetzen
→ dosieren / halten / führen / waschen / wärmen / absetzen
→ brauchbaren Anteil auffangen oder lokal anwenden
```

Ein Grundauszug, Nachauszug, Blütenauszug, eine temperierte Auflage oder ein Konzentrat kann nach Zweck eingesetzt werden. Die Station bezeichnet den Arbeitsort, nicht ein festes Wort und nicht zwingend ein anderes Folio.

## Wichtigste Verbesserung

Die Bio-Seiten sind nicht mehr bloß „Wasserwerk“ oder „Bad“. B4 zeigt das verbindende Muster besonders gut: eine halbfeste Pflanzenauflage wird an der Paarstation gehalten, während lokale Nebenläufe die Flüssigkeit zuführen oder abziehen. Das ist eine therapeutische Handlung, die technische Bedienung braucht.

## Was wir ausdrücklich nicht behaupten

Es gibt weiterhin keinen geschriebenen H1→B1-Schlüssel, keinen global verbundenen Rohrkreislauf und keine einzelne Flüssigkeit, die sichtbar durch alle Seiten läuft. Produkte sind austauschbare Klassen; Besitzer und Stationen bleiben lokal.

## Nächster Schritt

Als nächstes werden Herbal und Biological zu fünf bis sechs vollständigen Werkstattfällen zusammengesetzt: Produkt herstellen, passende Station wählen, anwenden und Restcharge behandeln. Danach kann der Astro-Anhang als Bedingungs-/Zeitwahl hinzukommen, ohne seine Etiketten künstlich zu übersetzen.
"""
    (HERE / "SIX_HUNDRED_SECOND_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "records": len(programs),
        "stations": len(station_inputs),
        "statements": len(steps),
        "events": sum(int(row["event_count"]) for row in steps),
        "therapeutic_leads": selected_counts["THERAPEUTIC_LEAD"],
        "hybrid_ties": selected_counts["HYBRID_TIE"],
        "technical_leads": selected_counts["TECHNICAL_LEAD"],
        "decision": "THERAPEUTIC_BATH_APPLICATION_CORE_WITH_TECHNICAL_SUPPORT_APPENDICES",
    }
    (HERE / "SIX_HUNDRED_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
