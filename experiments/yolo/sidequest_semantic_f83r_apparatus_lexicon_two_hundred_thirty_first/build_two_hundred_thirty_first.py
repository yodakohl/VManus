#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LOCAL_SOURCE = ROOT / "experiments/yolo/sidequest_semantic_station_card_portability_two_hundred_thirtieth/TWO_HUNDRED_THIRTIETH_TWENTY_SEVEN_CARD_PORTABILITY.tsv"
EVENT_SOURCE = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv"

ANALYSES = {
    "MC110": ("chkeedy", "CHK + EE + DY", "WÄRMEN + LÄNGER + SCHLUSS", "länger wärmen; Schluss", "RESIDENCE", "cheky|cheeky|chkeey", "FULLY_COMPOSITIONAL"),
    "MC064": ("chedchy", "CHED + Y", "ÜBERFÜHREN + DIES", "diesen Posten übertragen", "HANDOFF", "chdy|chedy|dchedy|schedy", "FULLY_COMPOSITIONAL"),
    "MC126": ("pchedal", "P + CHED + AL", "HINEIN + ÜBERFÜHREN + ZIEL", "zum Ziel zuführen", "INPUT", "pchedy|lchedal|lchedy", "FULLY_COMPOSITIONAL"),
    "MC043": ("shecthedchy", "CTH + CHED + Y", "BEREIT + ÜBERFÜHREN + DIES", "diesen vorbereiteten Posten übertragen", "INPUT", "cthy|chdy|chedchy", "COMPOSITIONAL_WITH_RENDERER_HULL"),
    "MC009": ("chary", "AR + Y", "VON/QUELLE + DIES", "dieser Quellposten", "SOURCE_SELECTION", "char|dar|sar|lchedar", "COMPOSITIONAL_WITH_RENDERER_HULL"),
    "MC081": ("okair", "OK + AIR", "EINSETZEN + LAUFMEDIUM", "Laufmedium einsetzen", "INPUT", "chair|kair|schedair|dairydy", "FULLY_COMPOSITIONAL"),
    "MC003": ("sheedy", "SHED + EE + DY", "ABSETZEN + LÄNGER + SCHLUSS", "länger absetzen; Schluss", "RESIDENCE", "shedy|cheedy|solshedy", "FULLY_COMPOSITIONAL"),
    "MC030": ("lo", "LO", "GELERNTES GANZWORT", "Abzug", "OUTPUT", "ldy|lar|lchedy", "LEARNED_WHOLE_CARD"),
}

RULES = [
    ("CHK + E/EE + Y/DY", "Wärmehandlung + Dauergrad + offener Posten/Schluss", "cheky|cheeky|chkeey|chkeedy", "kurz wärmen | länger warmhalten | länger wärmen; Schluss"),
    ("P/L + CHED + AL/AR/Y/DY", "Ein-/Ausgang + Transfer + Ziel/Quelle/Posten/Schluss", "pchedal|pchedy|lchedal|lchedar|lchedy|chedchy", "zuführen | abführen | Posten übertragen"),
    ("OK + AIR", "Aktivieren + Laufmedium", "okair", "Laufmedium einsetzen"),
    ("SHED + E/EE + DY", "Absetzen + Dauergrad + Schluss", "shedy|sheedy", "kurz oder länger absetzen; Schluss"),
    ("AR + Y", "Quellbezug + aktueller Posten", "chary", "Quellposten"),
    ("LO", "gelernte lokale Ausgabe-Karte", "lo", "Abzug"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    local_rows = [row for row in read(LOCAL_SOURCE) if row["portability_class"] == "LOCAL_LEARNED_WHOLE_CARD"]
    events = {row["master_card_id"]: row for row in read(EVENT_SOURCE) if row["master_card_id"] in ANALYSES}
    rows: list[dict[str, object]] = []
    for source in local_rows:
        card_id = source["master_card_id"]
        surface, segmentation, literal, value, phase, neighbors, status = ANALYSES[card_id]
        event = events[card_id]
        rows.append({
            "master_card_id": card_id,
            "event_id": event["event_id"],
            "visible_surface": surface,
            "station_id": source["target_station_ids"],
            "old_exact_type_status": "LOCAL_LEARNED_WHOLE_CARD",
            "component_segmentation": segmentation,
            "literal_component_sum_de": literal,
            "selected_short_value_de": value,
            "apparatus_phase": phase,
            "supporting_paradigm_surfaces": neighbors,
            "new_analysis_status": status,
            "whole_word_residue": value if status == "LEARNED_WHOLE_CARD" else "NONE",
        })
    rows.sort(key=lambda row: int(str(row["event_id"])[1:]))
    write(OUT / "TWO_HUNDRED_THIRTY_FIRST_EIGHT_LOCAL_CARD_ANALYSES.tsv", rows)

    rule_rows = [
        {"productive_template": template, "workshop_contribution_de": contribution, "attested_surfaces": surfaces, "predicted_reading_range_de": reading}
        for template, contribution, surfaces, reading in RULES
    ]
    write(OUT / "TWO_HUNDRED_THIRTY_FIRST_APPARATUS_COMPOSITION_RULES.tsv", rule_rows)

    phases = [
        ("1_SOURCE", "chary", "Quellposten wählen", "Source is a relation, not a named substance."),
        ("2_INPUT", "pchedal | shecthedchy | okair", "zum Ziel zuführen; vorbereiteten Posten übertragen; Laufmedium einsetzen", "Three different input modes share no forced material noun."),
        ("3_HANDOFF", "chedchy", "diesen Posten übertragen", "The same transfer core can move between visible stations."),
        ("4_RESIDENCE", "chkeedy | sheedy", "länger wärmen; länger absetzen", "Duration grade and close are compositional."),
        ("5_OUTPUT", "lo", "Abzug", "Only this local output card remains a memorized whole word."),
    ]
    phase_rows = [
        {"phase_order": order, "surfaces": surfaces, "apparatus_reading_de": reading, "scope_limit": limit}
        for order, surfaces, reading, limit in phases
    ]
    write(OUT / "TWO_HUNDRED_THIRTY_FIRST_FIVE_PHASE_APPARATUS_LEXICON.tsv", phase_rows)

    readable = [
        "# Kleines f83r-Apparaturlexikon",
        "",
        "Die acht nur einmal belegten exakten Karten sind nicht acht willkürliche Wörter. Sieben lassen sich aus derselben Werkstattkomposition lesen, die auch häufigere Karten bildet; nur `lo` bleibt als gelerntes Ganzwort.",
        "",
        "## Eingang bis Ausgang",
        "",
        "1. `chary` — **dieser Quellposten** (`AR + Y`).",
        "2. `pchedal` — **zum Ziel zuführen** (`P + CHED + AL`).",
        "3. `shecthedchy` — **diesen vorbereiteten Posten übertragen** (`CTH + CHED + Y`).",
        "4. `okair` — **Laufmedium einsetzen** (`OK + AIR`).",
        "5. `chedchy` — **diesen Posten übertragen** (`CHED + Y`).",
        "6. `chkeedy` — **länger wärmen; Schluss** (`CHK + EE + DY`).",
        "7. `sheedy` — **länger absetzen; Schluss** (`SHED + EE + DY`).",
        "8. `lo` — **Abzug** (gelerntes Ganzwort).",
        "",
        "## Werkstattlesung",
        "",
        "Vom Quellposten zum Ziel zuführen; den vorbereiteten Posten und das Laufmedium einsetzen; an die nächste Station übergeben; dort länger wärmen oder länger absetzen; schließlich über den Abzug ausgeben.",
        "",
        "Das ist erstmals genau die gesuchte Mischform: ein kleines produktives Kürzelsystem für Relation, Transfer, Grad und Abschluss plus ein gelerntes lokales Ganzwort für eine besondere Vorrichtung.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_FIRST_READABLE_APPARATUS_LEXICON.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Pass 231 — aus acht Einmalformen wird ein Apparaturparadigma",
        "",
        "Der bloße Exact-Type-Test aus Pass 230 war zu grob. Sieben der acht nur einmal belegten Typen sind durch bekannte Komponenten vorhersagbar. Der neue Status ist daher 5 vollständig kompositionelle Karten, 2 kompositionelle Karten mit Schreiberhülle und 1 gelernte Ganzkarte.",
        "",
        "Das Apparaturparadigma hat fünf Plätze: Quelle → Eingang → Übergabe → Aufenthalt → Ausgang. Die Komponenten sagen nicht, welches Material fließt und beweisen keinen gerichteten Bildkreislauf; sie liefern aber eine einfache, lernbare Handlungsgrammatik.",
        "",
        "Die stärksten echten Vorhersagen sind die Parallelpaare `CHK+EE+Y` offen gegenüber `CHK+EE+DY` geschlossen, `SHED+E/EE+DY` kurz/lang geschlossen sowie `P/L+CHED+AL/AR/DY` hinein/hinaus mit Ziel, Quelle oder Abschluss.",
        "",
        "Nächster Schritt: die komplette f83r-Stationsfolge als Quelle–Eingang–Aufenthalt–Ausgang-Graph schreiben und prüfen, wo sichtbare Besitzerwechsel die sprachliche Kette unterbrechen.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_FIRST_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    summary = {
        "local_source_sha256": hashlib.sha256(LOCAL_SOURCE.read_bytes()).hexdigest(),
        "event_source_sha256": hashlib.sha256(EVENT_SOURCE.read_bytes()).hexdigest(),
        "cards_reanalyzed": len(rows),
        "fully_compositional": sum(row["new_analysis_status"] == "FULLY_COMPOSITIONAL" for row in rows),
        "compositional_with_renderer_hull": sum(row["new_analysis_status"] == "COMPOSITIONAL_WITH_RENDERER_HULL" for row in rows),
        "learned_whole_cards": sum(row["new_analysis_status"] == "LEARNED_WHOLE_CARD" for row in rows),
        "apparatus_phases": len(phase_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
