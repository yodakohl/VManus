#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P388 = ROOT / "experiments/yolo/sidequest_semantic_boardless_layered_reading_three_hundred_eighty_eighth"

DECISIONS = {
    "807591efc3d3f7ddbfab": {
        "surface": "cheoar",
        "old_route": "WHOLE_CARD_MEMORY",
        "new_route": "COMPONENT_DIRECT",
        "composition": "CHEO+AR",
        "short_value": "Auszugnahme",
        "evidence": "CHEO=Auszug also occurs in chokcheo; AR=aus/von is independently used as source address",
        "boundary": "exact extraction method remains picture/local-practice dependent",
    },
    "d904bf7b044dd3922781": {
        "surface": "cheky",
        "old_route": "WHOLE_CARD_MEMORY",
        "new_route": "COMPONENT_DIRECT",
        "composition": "CHK+E+Y",
        "short_value": "Kurzwärme",
        "evidence": "CHEKY/CHKEEY family supports CHK warmth plus short/long grade and open Y endpoint",
        "boundary": "warming object comes from the current owner",
    },
    "5fca8fc3dee57e1d8c1f": {
        "surface": "lcheey",
        "old_route": "WHOLE_CARD_MEMORY",
        "new_route": "WHOLE_CARD_MEMORY",
        "composition": "LCHEEY_WHOLE",
        "short_value": "benetzte Stelle",
        "evidence": "single B2 occurrence sits with measure/current-item/full-soak sequence",
        "boundary": "L+CHEEY would yield Klarabzug and conflicts with the local card value; decomposition rejected",
    },
    "deb377381ceaf55ea310": {
        "surface": "cphy",
        "old_route": "WHOLE_CARD_MEMORY",
        "new_route": "WHOLE_CARD_MEMORY",
        "composition": "CPHY_WHOLE",
        "short_value": "Nachseihen",
        "evidence": "single H3 operator follows standing time; CFHY is a different preceding wringing operation",
        "boundary": "no independent C or PHY value predicts the distinction",
    },
    "e026af581c99322fbd46": {
        "surface": "talam",
        "old_route": "WHOLE_CARD_MEMORY",
        "new_route": "WHOLE_CARD_MEMORY",
        "composition": "TALAM_WHOLE",
        "short_value": "Verwahren",
        "evidence": "single H4 storage card after preparation; no transferable TAL or AM series",
        "boundary": "AL-looking interior is not licensed as the AL target card",
    },
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    prior = read(P388 / "THREE_HUNDRED_EIGHTY_EIGHTH_14_LAYERED_READINGS.tsv")
    decision_rows = []
    revised_rows = []
    for joint_id, decision in DECISIONS.items():
        prior_rows = [row for row in prior if row["joint_tuple_id"] == joint_id]
        decision_rows.append({
            "joint_tuple_id": joint_id,
            **decision,
            "practice_page_occurrences": len(prior_rows),
            "portable_component": "YES" if decision["new_route"] == "COMPONENT_DIRECT" else "NO",
        })
    for row in prior:
        revised = dict(row)
        decision = DECISIONS.get(row["joint_tuple_id"])
        if decision:
            revised["read_route"] = decision["new_route"]
            revised["strict_composition_or_whole_card"] = decision["composition"]
            revised["atomic_reading_de"] = decision["short_value"]
            if row["joint_tuple_id"] == "5fca8fc3dee57e1d8c1f":
                revised["owner_expanded_reading_de"] = "Für die benetzte Zielstelle des H4-Arbeitsgangs"
        revised_rows.append(revised)
    write("THREE_HUNDRED_EIGHTY_NINTH_FIVE_CARD_DECISIONS.tsv", decision_rows)
    write("THREE_HUNDRED_EIGHTY_NINTH_REVISED_14_LAYERED_READINGS.tsv", revised_rows)

    boundaries = [
        {"tempting_split": "L+CHEEY", "predicted_value": "Klarabzug", "actual_selected_value": "benetzte Stelle", "decision": "REJECT_SPLIT_KEEP_LCHEEY_WHOLE"},
        {"tempting_split": "C+PHY", "predicted_value": "none without invented roots", "actual_selected_value": "Nachseihen", "decision": "KEEP_CPHY_WHOLE"},
        {"tempting_split": "T+AL+AM", "predicted_value": "target plus unknown remainder", "actual_selected_value": "Verwahren", "decision": "KEEP_TALAM_WHOLE"},
    ]
    write("THREE_HUNDRED_EIGHTY_NINTH_THREE_WHOLE_CARD_BOUNDARIES.tsv", boundaries)

    edition = """# Pass 389 — korrigierte Rücklesung des Fünferrests

## Neue Teilung

- `cheoar` = **CHEO Auszug + AR aus/von** → Auszugnahme.
- `cheky` = **CHK Wärme + E kurz + Y offen** → Kurzwärme.
- `lcheey` = **gelernte Ganzkarte** → benetzte Stelle.
- `cphy` = **gelernte Ganzkarte** → Nachseihen.
- `talam` = **gelernte Ganzkarte** → Verwahren.

Damit besitzt die Seite elf komponierbare Karten und drei gelernte Ganzkarten.

## Revidierte H4-Lesung

Von der abgebildeten Pflanze eine Zutat in den Ansatz nehmen; aus dem Ansatz
einen Auszug nehmen und kurz wärmen. Für die benetzte Zielstelle nachseihen und
bereitstellen.

Die Formulierung ist elliptisch, aber ehrlicher als das frühere `lcheey =
Klarabzug`. Das klare Abziehen bleibt eine mögliche lokale Handlung; es ist
nicht länger der Default dieser exakten Karte.

## B3 bleibt unverändert

Diesen Posten im Sollmaß durch die sichtbare Verbindung leiten und einsetzen;
länger in Kontakt halten, kurz abschließen und verwahren.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_NINTH_REVISED_BOARDLESS_EDITION.md").write_text(edition, encoding="utf-8")
    report = """# Pass 389 — zwei Zerlegungen gewonnen, eine falsche zurückgenommen

Von fünf gelernten Karten lassen sich CHEOAR und CHEKY nun mit bereits
unabhängig verwendeten Komponenten lesen. LCHEEY widersteht dagegen gerade der
oberflächlich hübschen Zerlegung: L+CHEEY würde Klarabzug ergeben, sein realer
B2-Satz verlangt eher die benetzte Zielstelle. CPHY und TALAM bleiben ebenfalls
kurze Ganzkarten.

Der boardlose Anteil steigt dadurch von neun auf elf komponierbare Karten;
nur drei müssen auswendig gelernt werden. Zugleich wird eine frühere
Übersetzungsstelle korrigiert statt durch eine immer kompliziertere Glosse
gerettet.

Als nächstes sollen die drei Ganzkarten nicht orthographisch, sondern als
Nomenklatorfunktionen verglichen werden: Ergebnis/Ziel, Nachbearbeitung und
Aufbewahrung. Gesucht werden echte funktionale Schwesterkarten auf den zehn
Seiten, nicht erfundene Buchstabenstämme.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "cards_reanalysed": len(decision_rows),
        "new_component_direct": sum(row["new_route"] == "COMPONENT_DIRECT" for row in decision_rows),
        "retained_whole": sum(row["new_route"] == "WHOLE_CARD_MEMORY" for row in decision_rows),
        "page_component_direct": sum(row["read_route"] == "COMPONENT_DIRECT" for row in revised_rows),
        "page_whole_cards": sum(row["read_route"] == "WHOLE_CARD_MEMORY" for row in revised_rows),
        "meaning_corrections": 1,
    }
    (HERE / "THREE_HUNDRED_EIGHTY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
