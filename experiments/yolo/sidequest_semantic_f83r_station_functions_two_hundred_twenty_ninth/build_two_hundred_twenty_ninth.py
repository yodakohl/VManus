#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENT_SOURCE = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv"
STATEMENT_SOURCE = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_116_STATEMENT_PROSE.tsv"

STATIONS = {
    "F83_STATION_1": {
        "visible_owner": "obere offene Fächer-Randstation",
        "field_ids": ["F071", "F072", "F073", "F074"],
        "function_de": "SAMMEL- UND TEMPERIERSTELLE",
        "short_de": "Sammel-/Temperierstelle",
        "function_chain_de": "sammeln → temperieren → Sollwert halten → abführen oder bemessen weitergeben",
        "visual_limit": "Die offene Randform stützt eine lokale Station; Wärme und Flussrichtung stammen aus der Kartenlesung, nicht aus einem sichtbaren Pfeil.",
    },
    "F83_STATION_2": {
        "visible_owner": "mittlere runde Gefäß-Randstation",
        "field_ids": ["F075", "F076", "F077", "F078", "F079"],
        "function_de": "ÜBERGABE- UND HALTEGEFÄSS",
        "short_de": "Übergabe-/Haltegefäß",
        "function_chain_de": "überführen → am Ziel einsetzen → länger halten/einwirken → abführen",
        "visual_limit": "Die runde Gefäßform stützt einen lokalen Behälter; Inhalt, Dauer und Richtung werden nur aus der Kartenfolge ergänzt.",
    },
    "F83_STATION_3": {
        "visible_owner": "untere korbartige Gefäß-Randstation",
        "field_ids": ["F080", "F081", "F082", "F083", "F084", "F085", "F086"],
        "function_de": "PORTIONS- UND ABSETZGEFÄSS",
        "short_de": "Portions-/Absetzgefäß",
        "function_chain_de": "zuführen → Portion bemessen → kurz oder lang absetzen → abführen/abziehen",
        "visual_limit": "Die korbartige Gefäßform stützt einen lokalen Empfänger; Filter, Stoff und globale Netzrichtung bleiben unbestimmt.",
    },
}

STATEMENT_READINGS = {
    "B3-S001": "In der Sammelstelle länger sammeln; Schluss.",
    "B3-S002": "Zur Temperierstelle wechseln und dort länger wärmen; Schluss.",
    "B3-S003": "Diesen Bestand auf Sollwert setzen, als denselben Bestand halten und abführen; Schluss.",
    "B3-S004": "Davon bemessen und zur folgenden Stelle bringen.",
    "B3-S005": "In das runde Übergabegefäß überführen; Schluss.",
    "B3-S006": "Den Posten übertragen, am Ziel einsetzen und im Haltegefäß weiterführen; Schluss.",
    "B3-S007": "Bemessen, überführen und im Haltegefäß länger einwirken lassen; Schluss.",
    "B3-S008": "Aus dem Haltegefäß abführen; Schluss.",
    "B3-S009": "In den nächsten Gang einsetzen.",
    "B3-S010": "Dem Portionsgefäß zuführen und kurz fortsetzen; Schluss.",
    "B3-S011": "Die Vorbereitung übertragen, einsetzen und zum Quellposten weiterführen.",
    "B3-S012": "Den Ansatz im Gefäß kurz absetzen lassen; Schluss.",
    "B3-S013": "Eine Portion bemessen, kurz vorbereiten und kurz einwirken lassen; Schluss.",
    "B3-S014": "In den Lauf einsetzen und im Gefäß länger absetzen lassen; Schluss.",
    "B3-S015": "Aus dem Absetzgefäß abführen; Schluss.",
    "B3-S016": "Aus dem Absetzgefäß abziehen; danach wechselt der sichtbare Besitzer.",
}

PRIMARY_TERMS = {
    "F83_STATION_1": ("sammel", "wärm", "Sollwert", "abführ", "bemess"),
    "F83_STATION_2": ("überführ", "transfer", "dorthin", "einwirk", "abführ", "einsetz"),
    "F83_STATION_3": ("zuführ", "Portion", "absetz", "abführ", "Abzug", "bemess", "Laufeinsatz"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENT_SOURCE)
    statements = {row["statement_id"]: row for row in read(STATEMENT_SOURCE)}
    field_to_station = {
        field: station_id
        for station_id, spec in STATIONS.items()
        for field in spec["field_ids"]
    }

    station_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    for station_id, spec in STATIONS.items():
        selected = [row for row in events if row["field_id"] in spec["field_ids"]]
        station_rows.append({
            "station_id": station_id,
            "visible_owner": spec["visible_owner"],
            "field_range": f"{spec['field_ids'][0]}–{spec['field_ids'][-1]}",
            "field_count": len(spec["field_ids"]),
            "event_count": len(selected),
            "statement_count": len({row["statement_id"] for row in selected}),
            "selected_function_de": spec["function_de"],
            "function_chain_de": spec["function_chain_de"],
            "visual_limit": spec["visual_limit"],
        })
        for row in selected:
            value = row["portable_value_de"]
            fit = "PRIMARY_FUNCTION" if any(term.lower() in value.lower() for term in PRIMARY_TERMS[station_id]) else "SUPPORTING_CONTROL_OR_TRANSFER"
            event_rows.append({
                "station_id": station_id,
                "selected_function_de": spec["function_de"],
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "field_id": row["field_id"],
                "field_position": row["field_position"],
                "visible_surface": row["visible_surface"],
                "master_card_id": row["master_card_id"],
                "portable_value_de": value,
                "terminal_status": row["terminal_status"],
                "visible_owner": row["visible_owner"],
                "function_fit": fit,
                "station_realization_de": f"{value} — {spec['short_de']}",
            })

    statement_rows: list[dict[str, object]] = []
    for number in range(1, 17):
        statement_id = f"B3-S{number:03d}"
        source = statements[statement_id]
        owned = [row for row in event_rows if row["statement_id"] == statement_id]
        station_ids = list(dict.fromkeys(str(row["station_id"]) for row in owned))
        station_id = station_ids[0]
        statement_rows.append({
            "statement_id": statement_id,
            "station_id": station_id,
            "selected_function_de": STATIONS[station_id]["function_de"],
            "source_visible_sequence": source["visible_sequence"],
            "source_event_count": source["event_count"],
            "owned_event_ids": "|".join(str(row["event_id"]) for row in owned),
            "owned_event_count": len(owned),
            "owner_scope": "PARTIAL_BEFORE_OWNER_BREAK" if statement_id == "B3-S016" else "FULL_STATEMENT",
            "station_reading_de": STATEMENT_READINGS[statement_id],
            "strongest_limit": "E264 gehört bereits zum ungelösten Zwischenposten und wird nicht der Station zugeschlagen." if statement_id == "B3-S016" else STATIONS[station_id]["visual_limit"],
        })

    write(OUT / "TWO_HUNDRED_TWENTY_NINTH_THREE_STATION_FUNCTIONS.tsv", station_rows)
    write(OUT / "TWO_HUNDRED_TWENTY_NINTH_THIRTY_FIVE_OWNED_EVENTS.tsv", event_rows)
    write(OUT / "TWO_HUNDRED_TWENTY_NINTH_SIXTEEN_STATION_STATEMENT_READINGS.tsv", statement_rows)

    lines = [
        "# Drei konkrete f83r-Arbeitsstationen",
        "",
        "Die Namen sind Werkstattfunktionen, keine entschlüsselten historischen Wörter. Sie werden aus der lokalen Gefäßform und der bereits geltenden Kartenfolge gemeinsam gelesen.",
        "",
    ]
    for station in station_rows:
        station_id = str(station["station_id"])
        lines.extend([
            f"## {station['selected_function_de']}",
            "",
            f"**Bildbesitzer:** {station['visible_owner']} ({station['field_range']}; {station['event_count']} Karten).",
            "",
            f"**Arbeitsgang:** {station['function_chain_de']}.",
            "",
        ])
        for row in statement_rows:
            if row["station_id"] == station_id:
                lines.append(f"- {row['statement_id']}: {row['station_reading_de']}")
        lines.extend(["", f"**Grenze:** {station['visual_limit']}", ""])
    lines.extend([
        "## Fortlaufende Lesung",
        "",
        "Oben sammeln und länger temperieren; den Bestand auf Sollwert halten, abführen und eine bemessene Menge weitergeben. Im runden Übergabegefäß übernehmen, am Ziel einsetzen, länger halten und wieder abführen. Im unteren Portionsgefäß zuführen, Portion und Stufe einstellen, kurz oder lang absetzen und schließlich abziehen. Danach beginnt mit E264 ein anderer, noch ungelöster Bildposten.",
        "",
        "Das ist eine Folge lokaler Stationen, kein behaupteter geschlossener Wasserkreislauf.",
    ])
    (OUT / "TWO_HUNDRED_TWENTY_NINTH_THREE_READABLE_STATIONS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Pass 229 — konkrete Funktionen der ersten drei f83r-Stationen",
        "",
        "Die 35 Karten E229–E263 wurden ihren drei sichtbaren Besitzern vollständig zugeordnet. E264 wurde absichtlich ausgeschlossen, weil der Bildbesitzer mitten in B3-S016 wechselt.",
        "",
        "Die beste zusammenhängende Arbeitstheorie ist eine kleine Stationsfolge: Sammeln/Temperieren → Übergeben/Halten → Portionieren/Absetzen. Sie erklärt die wiederholten Übergabe-, Sollwert-, Dauer- und Abführkarten besser als drei bedeutungslose Randdekorationen, behauptet aber weder Filtermaterial noch eine sichtbare Flussrichtung.",
        "",
        "Der stärkste neue Gewinn ist die dritte Station: `Portion`, `bemessen`, kurzes und langes `absetzen`, `abführen` und `Abzug` stehen dort im selben lokalen Gefäßprogramm. Die zweite ist vor allem Übergabe/Halten; die erste sammelt, temperiert und gibt bemessen weiter.",
        "",
        "Nächster Schritt: dieselben exakten Karten an allen anderen Bildbesitzern prüfen. So lässt sich entscheiden, welche Werte portable Verben sind und welche nur durch diese drei Stationsbilder entstehen.",
    ]
    (OUT / "TWO_HUNDRED_TWENTY_NINTH_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "event_source_sha256": hashlib.sha256(EVENT_SOURCE.read_bytes()).hexdigest(),
        "statement_source_sha256": hashlib.sha256(STATEMENT_SOURCE.read_bytes()).hexdigest(),
        "stations": len(station_rows),
        "fields": sum(int(row["field_count"]) for row in station_rows),
        "owned_events": len(event_rows),
        "statements": len(statement_rows),
        "excluded_owner_break_event": "E264",
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
