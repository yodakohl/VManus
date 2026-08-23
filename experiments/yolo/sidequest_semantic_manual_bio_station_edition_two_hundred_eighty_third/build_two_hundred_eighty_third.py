#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R281 = ROOT / "experiments/yolo/sidequest_semantic_eight_prose_formulas_two_hundred_eighty_first"
R74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74"
FORMULAS = R281 / "TWO_HUNDRED_EIGHTY_FIRST_116_FORMULA_ASSIGNMENTS.tsv"
OWNERS = R74 / "V74_R1_97_STATEMENT_EDITION.tsv"
BIO_PAGES = {"f81v", "f82r", "f83r"}

OWNER_LABELS = {
    "B1_SHARED_TWO_ROW_POOL": "gemeinsamen zweireihigen Figurenbecken",
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": "oberen Doppelbecken mit zylindrischem Anschluss",
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": "linken Mittelgerät mit eingefügtem Knoten",
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": "rechten mittleren Einzelplatz",
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": "unteren grünen Mehrpersonenbecken",
    "B2_LOWER_POOL_EDGE_STATIONS": "unteren Beckenrand mit mehreren Arbeitsplätzen",
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "oberen offenen Fächergefäß am Rand",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "runden Mittelgefäß am Rand",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "unteren korbartigen Randgefäß",
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": "Zwischenraum zwischen Randgefäßen und Hauptbogen",
    "B3_MAIN_ARCH_LINKED_PAIR": "sichtbar verbundenen Gefäßpaar des Hauptbogens",
    "B4_MAIN_ARCH_LINKED_PAIR": "sichtbar verbundenen Gefäßpaar des Hauptbogens",
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": "linken offenen Randplatz des Hauptfeldes",
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": "rechten S-förmigen Mehranschlusslauf",
    "B5_LEFT_OPEN_FRINGE_STATION": "linken offenen Randplatz des Nachtrags",
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": "rechten S-förmigen Mehranschlusslauf des Nachtrags",
}

FORMULA_TEXT = {
    "FLOW_TRANSFER_PROCESS": "Bearbeite den laufenden Posten und führe ihn durch den örtlichen Lauf oder in das bezeichnete Gefäß.",
    "FULL_ADDRESS_PROCESS": "Nimm den Posten aus der bezeichneten Quelle, bemiss ihn, führe ihn zur bezeichneten Stelle und vollziehe dort den Arbeitsgang.",
    "LINKED_PROCESS": "Verknüpfe diesen Posten mit dem vorherigen oder dem nächsten Stationsposten und führe den verbundenen Gang weiter.",
    "GRADED_PROCESS": "Führe den Arbeitsgang bis zur bezeichneten Stufe und halte den Posten dort entsprechend kurz, länger oder vollständig.",
    "QUANTIFIED_PROCESS": "Nimm die bezeichnete Portion oder Sollmenge und führe den örtlichen Arbeitsgang damit aus.",
    "SOURCED_PROCESS": "Nimm den Arbeitsstoff aus der örtlich bezeichneten Quelle und bearbeite ihn an dieser Station weiter.",
    "SIMPLE_OR_ELLIPTIC_PROCESS": "Vollziehe den bezeichneten örtlichen Arbeitsschritt; Gefäß, Stoff oder Körperstelle werden aus dem Bildplatz mitgelesen.",
    "TARGET_APPLICATION_PROCESS": "Setze den laufenden Posten an der bezeichneten Arbeits- oder Körperstelle an und führe die Anwendung dort aus.",
}

RECORDS = {
    "B1": {
        "title": "Gemeinsames Doppelbecken: ansetzen, bemessen, halten und abführen",
        "narrative": (
            "Die beiden Figurenreihen gehören zu einem gemeinsamen Bade- oder Waschplatz. "
            "Der Text setzt örtliche Portionen ein, bemisst sie, führt sie an Teilstellen, lässt sie stehen, "
            "temperiert und spült sie und führt verbrauchten Lauf wieder ab. Die vielen kurzen Zellen lesen "
            "sich wie Varianten desselben Stationsbetriebs, nicht wie ein einziger langer Satz."
        ),
        "content_wager": "THERAPEUTIC_SHARED_BATH_OR_WASH_STATION",
    },
    "B2": {
        "title": "Vier getrennte Arbeitsplätze auf f82r",
        "narrative": (
            "Oben werden zwei Becken mit einem Anschluss bedient; links in der Mitte folgt ein eigenes Gerät, "
            "rechts ein einzelner Übergabeplatz und unten ein Mehrpersonenbecken mit Randposten. Der Text beschreibt "
            "Füllen, Umsetzen, Bemessen, Halten, Spülen und Ablassen innerhalb dieser Plätze. Beim Wechsel vom rechten "
            "Mittelplatz zum unteren Becken läuft eine Aussage über die Bildgrenze weiter: Das ist eine ausgelassene "
            "Werkstattverknüpfung, keine gezeichnete Rohrleitung."
        ),
        "content_wager": "MULTI_STATION_BATH_WASH_AND_TRANSFER_SHEET",
    },
    "B3": {
        "title": "Randgefäße, Zwischenzone und verbundenes Hauptpaar",
        "narrative": (
            "Drei Randgefäße tragen getrennte Vorbereitungs- und Absetzfolgen. Danach führt der Text durch einen nicht "
            "gezeichnet verbundenen Zwischenraum zum Hauptfeld; erst dort ist ein Gefäßpaar wirklich sichtbar verbunden. "
            "Die plausible Werkstattlesung ist portionsweises Bereiten, Ruhen, Durchlassen, Auffangen und erneutes Einsetzen. "
            "Zwei textliche Besitzerwechsel über Bildlücken bleiben ausdrücklich Ellipsen und werden nicht zu einem Kreislauf ergänzt."
        ),
        "content_wager": "LOCAL_PREPARATION_CLARIFICATION_AND_APPLICATION_STATIONS",
    },
    "B4": {
        "title": "Geschlossene Anwendungen am Hauptbogen und am S-Lauf",
        "narrative": (
            "Die ersten zehn Zellen arbeiten am sichtbar verbundenen Paar, dann folgen ein linker offener Randplatz und "
            "ein rechter S-förmiger Mehranschlusslauf. Alle sechzehn Aussagen schließen ihren Arbeitsschritt. Das passt zu "
            "einer Reihe festgesetzter Anwendungen, Spülungen oder Einsätze; der Wechsel vom linken zum rechten Lauf ist "
            "textlich, aber nicht als durchgehende Bildkante gezeichnet."
        ),
        "content_wager": "COMMITTED_APPLICATION_AND_RINSE_CELLS",
    },
    "B5": {
        "title": "Linker technischer Übergabenachtrag",
        "narrative": (
            "Drei kurze Aussagen nehmen eine Quelle auf, verbinden den nächsten Posten und führen ihn an einen lokalen "
            "Arbeitsplatz. Zwei Schritte werden festgesetzt, der letzte bleibt für eine Fortsetzung offen. Das ist eher "
            "eine Bedien- oder Übergabenotiz als eine neue Therapiebeschreibung."
        ),
        "content_wager": "TECHNICAL_HANDOFF_ADDENDUM",
    },
    "B6": {
        "title": "Offener Mehranschluss-Nachtrag",
        "narrative": (
            "Die einzige lange Aussage adressiert Quelle, Maß, Ziel und Fortsetzung am rechten S-förmigen Lauf, bleibt aber "
            "offen. Am besten liest sie sich als vorbereitende Einstellung oder Zuweisung für den nächsten Arbeitsschritt, "
            "nicht als abgeschlossene Anwendung."
        ),
        "content_wager": "OPEN_MULTIPORT_SETUP_NOTE",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owner_text(owner_sequence: str) -> str:
    parts = owner_sequence.split(" > ")
    labels = [OWNER_LABELS[p] for p in parts]
    if len(labels) == 1:
        return labels[0]
    return f"{labels[0]}; danach ohne sichtbare Verbindung im {labels[1]}"


def close_text(status: str) -> str:
    if status == "CLOSED":
        return "Setze diesen Stationsschritt fest."
    return "Halte den Posten für die folgende Stationszelle offen."


def main() -> None:
    formula_rows = [r for r in read_tsv(FORMULAS) if r["page"] in BIO_PAGES]
    owner_rows = {r["statement_id"]: r for r in read_tsv(OWNERS)}
    assert len(formula_rows) == 97
    assert set(owner_rows) == {r["statement_id"] for r in formula_rows}

    rows: list[dict[str, object]] = []
    for source in formula_rows:
        owner = owner_rows[source["statement_id"]]
        local = source["local_sequence_de"].strip().rstrip(".")
        reset = owner["internal_owner_reset"] == "YES"
        translation = (
            f"Am {owner_text(owner['owner_sequence'])}: "
            f"{FORMULA_TEXT[source['formula_family']]} "
            f"Kartenlesung: {local}. {close_text(source['terminal_status'])}"
        )
        if reset:
            translation += " Die Aussage überschreitet dabei eine Bildbesitzergrenze ohne gezeichnete Verbindung."
        rows.append({
            "statement_id": source["statement_id"],
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "loci": source["loci"],
            "surface_sequence": source["surface_sequence"],
            "formula_family": source["formula_family"],
            "terminal_status": source["terminal_status"],
            "owner_sequence": owner["owner_sequence"],
            "owner_reading_de": owner_text(owner["owner_sequence"]),
            "internal_owner_reset": owner["internal_owner_reset"],
            "line_crossing": owner["line_crossing"],
            "family_sequence_de": source["family_sequence_de"],
            "station_translation_de": translation,
            "global_flow_policy": "LOCAL_STATION_ONLY__NO_GLOBAL_CIRCUIT",
        })

    narratives: list[dict[str, object]] = []
    for record, spec in RECORDS.items():
        selected = [r for r in rows if r["record_unit_id"] == record]
        narratives.append({
            "record_unit_id": record,
            "page": selected[0]["page"],
            "title_de": spec["title"],
            "statement_count": len(selected),
            "event_count": sum(len(str(r["surface_sequence"]).split(" · ")) for r in selected),
            "closed_statements": sum(r["terminal_status"] == "CLOSED" for r in selected),
            "open_statements": sum(r["terminal_status"] == "OPEN" for r in selected),
            "owner_reset_statements": sum(r["internal_owner_reset"] == "YES" for r in selected),
            "continuous_narrative_de": spec["narrative"],
            "strongest_content_wager": spec["content_wager"],
        })

    resets = [
        {
            "statement_id": r["statement_id"],
            "record_unit_id": r["record_unit_id"],
            "page": r["page"],
            "owner_sequence": r["owner_sequence"],
            "interpretation_de": "Text läuft weiter; Bildbesitzer wechselt; Verbindung ist ausgelassen und darf nicht als Rohr oder Flussrichtung ergänzt werden.",
        }
        for r in rows if r["internal_owner_reset"] == "YES"
    ]

    statement_path = OUT / "TWO_HUNDRED_EIGHTY_THIRD_97_STATION_TRANSLATIONS.tsv"
    narrative_path = OUT / "TWO_HUNDRED_EIGHTY_THIRD_SIX_BIO_NARRATIVES.tsv"
    reset_path = OUT / "TWO_HUNDRED_EIGHTY_THIRD_FOUR_OWNER_RESETS.tsv"
    readable_path = OUT / "TWO_HUNDRED_EIGHTY_THIRD_COMPLETE_BIO_EDITION.md"
    report_path = OUT / "TWO_HUNDRED_EIGHTY_THIRD_REPORT.md"
    write_tsv(statement_path, rows, list(rows[0]))
    write_tsv(narrative_path, narratives, list(narratives[0]))
    write_tsv(reset_path, resets, list(resets[0]))

    md = [
        "# Vollständige manuelle Bio-Stationsausgabe",
        "",
        "Die Figuren und Gefäße liefern lokale Besitzer. Ein Besitzerwechsel darf Textargumente erben, erzeugt aber keine unsichtbare Rohrleitung. Jede der 97 Aussagen bleibt unten sichtbar.",
        "",
    ]
    for narrative in narratives:
        md.extend([
            f"## {narrative['record_unit_id']} / {narrative['page']}: {narrative['title_de']}",
            "",
            str(narrative["continuous_narrative_de"]),
            "",
        ])
        for row in [r for r in rows if r["record_unit_id"] == narrative["record_unit_id"]]:
            md.append(f"- **{row['statement_id']}** — {row['station_translation_de']}")
        md.append("")
    readable_path.write_text("\n".join(md), encoding="utf-8")

    counts = Counter(r["formula_family"] for r in rows)
    report_path.write_text(
        "# Sidequest-Pass 283: sechs lokale Bio-Stationsgeschichten\n\n"
        "## Ergebnis\n\n"
        "Alle 97 Bio-Aussagen sind jetzt an den tatsächlich sichtbaren lokalen Bildbesitzer gebunden und als konkrete Werkstattgänge lesbar. "
        "B1 ist ein gemeinsames Doppelbecken; B2 zerfällt in vier Arbeitszonen; B3 führt von drei Randgefäßen über eine ungezeichnete Zwischenzone zu einem sichtbar verbundenen Paar; "
        "B4 enthält geschlossene Anwendungen am Paar und am S-Lauf; B5 und B6 sind technische Nachträge.\n\n"
        "Die vier aussageninternen Besitzerwechsel bleiben lesbar, werden aber nicht in erfundene Leitungen verwandelt. Damit ist die stärkste kreative Gesamtlesung ein lokales Bade-, Wasch-, Klär- und Übergaberegister. "
        "Es ist ausdrücklich keine einzige globale Maschine.\n\n"
        f"Formelverteilung: `{dict(counts)}`. Inputs `{sha(FORMULAS)}` und `{sha(OWNERS)}`.\n",
        encoding="utf-8",
    )

    outputs = (statement_path, narrative_path, reset_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "statements": len(rows),
        "events": sum(len(str(r["surface_sequence"]).split(" · ")) for r in rows),
        "records": len(narratives),
        "owner_resets": len(resets),
        "record_counts": dict(Counter(str(r["record_unit_id"]) for r in rows)),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
