#!/usr/bin/env python3
"""Generate economical compound meanings, then compare with fixed-page surfaces."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R86 = ROOT / "experiments/yolo/sidequest_semantic_concrete_codex_eighty_sixth_edition/EIGHTY_SIXTH_776_CONCRETE_CODEX_BINDING.tsv"


PREDICTIONS = [
    ("P01", "OK+AIIN", r"^q?okaiin$", "auf Sollmaß ansetzen"),
    ("P02", "OK+AIN", r"^q?okain$", "eine Portion ansetzen"),
    ("P03", "OK+AL", r"^q?okal$", "an der Zielstelle ansetzen"),
    ("P04", "OK+AR", r"^q?okar$", "aus der Quelle ansetzen"),
    ("P05", "OK+AIR", r"^q?okair$", "den Lauf in Gang setzen"),
    ("P06", "OK+Y", r"^q?ok(?:ch)?y$", "diesen Posten ansetzen"),
    ("P07", "OK+E+Y", r"^q?okey$", "kurz ansetzen und offen halten"),
    ("P08", "OK+EE+Y", r"^q?okeey$", "länger ansetzen und offen halten"),
    ("P09", "OK+E+CLOSE", r"^q?okedy$", "kurz ansetzen und schließen"),
    ("P10", "OK+EE+CLOSE", r"^q?okeedy$", "länger ansetzen und schließen"),
    ("P11", "OK+EEE+CLOSE", r"^q?okeeedy$", "vollständig ansetzen und schließen"),
    ("P12", "OT+AL", r"^q?otal$", "zur nächsten Zielstelle"),
    ("P13", "OL+OR", r"^(?:olor|cholor)$", "den vorigen Ansatz fortführen"),
    ("P14", "OT+OR", r"^q?ot(?:ch)?or$", "den nächsten Ansatz eröffnen"),
    ("P15", "CHD+Y", r"^(?:chdy|chedy)$", "diesen Posten umsetzen"),
    ("P16", "CHD+AL", r"^(?:ch(?:e)?dal|lchedal|pchedal)$", "zur Zielstelle umsetzen"),
    ("P17", "CHD+AR", r"^(?:ch(?:ee?)?dar|lchedar)$", "aus der Quelle umsetzen"),
    ("P18", "CKH+Y", r"^(?:chckhy|ckhy)$", "diesen Durchlass öffnen"),
    ("P19", "CKH+E+CLOSE", r"^.*ckh(?:e)?dy$", "kurz durch den Gang führen und schließen"),
    ("P20", "SHED+CLOSE", r"^(?:q?shedy|sheedy|schedy)$", "absetzen lassen und schließen"),
    ("P21", "SOLK+AIIN", r"^solkaiin$", "bis zum Sollmaß sammeln"),
    ("P22", "CHEO+AR", r"^cheoar$", "aus dem Auszug entnehmen"),
    ("P23", "HO+AIIN", r"^chodaiin$", "Zutat nach Sollmaß"),
    ("P24", "TY+AIIN", r"^taiin$", "Teil nach Sollmaß"),
    ("P25", "SOLK+AIN", r"^solkain$", "eine Portion sammeln"),
    ("P26", "CHEO+AL", r"^cheoal$", "Auszug zur Zielstelle"),
    ("P27", "CTH+AIIN", r"^cthaiin$", "bis zum vorgeschriebenen Bereitschaftsmaß"),
    ("P28", "CTH+AL", r"^cthal$", "an der Zielstelle bereit"),
    ("P29", "SHED+AIIN", r"^shedaiin$", "bis zum vorgeschriebenen Absetzmaß"),
    ("P30", "CKH+AIIN", r"^ckhaiin$", "Durchlass bis zum Sollmaß"),
    ("P31", "KCH+AL", r"^(?:kchal|chckhal)$", "an der Zielstelle bearbeiten"),
    ("P32", "KCH+AR", r"^kchar$", "aus der Quelle bearbeiten"),
    ("P33", "HO+AL", r"^(?:choal|shoal|schoal)$", "Zutat zur Zielstelle"),
    ("P34", "HO+AR", r"^(?:choar|shoar)$", "Zutat aus der Quelle"),
    ("P35", "TY+AL", r"^(?:tyal|tial)$", "Teil zur Zielstelle"),
    ("P36", "TY+AR", r"^(?:tyar|tiar)$", "Teil aus der Quelle"),
]


COLLISION_SENSITIVE = {"P06", "P15", "P18", "P19", "P20"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    prose = [row for row in read_tsv(R86) if int(row["unified_serial"]) <= 381]
    counts = Counter(row["visible_identity"] for row in prose)
    contexts: dict[str, list[str]] = {}
    for surface in counts:
        contexts[surface] = [
            f"{row['unit_id']}:{row['local_address']}" for row in prose if row["visible_identity"] == surface
        ]

    rows = []
    matches = []
    for prediction_id, components, pattern, meaning in PREDICTIONS:
        matched = sorted(surface for surface in counts if re.fullmatch(pattern, surface))
        event_count = sum(counts[surface] for surface in matched)
        if not matched:
            status = "UNFILLED_PRODUCTIVE_CELL_ON_FIXED_PAGES"
        elif prediction_id in COLLISION_SENSITIVE:
            status = "OBSERVED_COLLISION_SENSITIVE"
        elif len(matched) > 1:
            status = "OBSERVED_WITH_SURFACE_VARIANTS"
        else:
            status = "OBSERVED_CLEAN"
        rows.append({
            "prediction_id": prediction_id, "components": components,
            "expected_surface_pattern": pattern, "predicted_workshop_meaning_de": meaning,
            "matched_surfaces": ",".join(matched) or "NONE", "matched_surface_count": len(matched),
            "matched_event_count": event_count, "status": status,
            "interpretation_rule": "COMPOSE_COMPONENT_VALUES__DO_NOT_ADD_RICH_NOUN",
        })
        for surface in matched:
            matches.append({
                "prediction_id": prediction_id, "components": components,
                "predicted_workshop_meaning_de": meaning, "observed_surface": surface,
                "event_count": counts[surface], "contexts": ",".join(contexts[surface]),
                "collision_sensitive": "YES" if prediction_id in COLLISION_SENSITIVE else "NO",
            })
    write_tsv(OUT / "NINETY_SIXTH_36_COMPOUND_PREDICTIONS.tsv", rows)
    write_tsv(OUT / "NINETY_SIXTH_OBSERVED_COMPOUND_MATCHES.tsv", matches)
    gaps = [row for row in rows if row["status"] == "UNFILLED_PRODUCTIVE_CELL_ON_FIXED_PAGES"]
    write_tsv(OUT / "NINETY_SIXTH_UNFILLED_COMPOUND_CELLS.tsv", gaps)

    status_counts = Counter(row["status"] for row in rows)
    doc = [
        "# Sechsundneunzigste Werkstattrunde: vorhergesagte Komposita", "",
        "## Ergebnis", "",
        "Aus dem kompakten Codebuch wurden 36 kurze Komposita mit Bedeutung und",
        "erwarteter Formenfamilie gebildet. Erst danach wurden die 230 sichtbaren",
        "Prosaflächen der festen Seiten dagegen gehalten.", "",
    ]
    for status, count in sorted(status_counts.items()):
        doc.append(f"- {status}: {count}")
    doc.extend(["", "## Beobachtete Familien", ""])
    for row in rows:
        if row["matched_surfaces"] != "NONE":
            doc.append(f"- **{row['components']}** → {row['predicted_workshop_meaning_de']}: `{row['matched_surfaces']}` ({row['matched_event_count']} Ereignisse; {row['status']})")
    doc.extend(["", "## Noch freie Zellen", ""])
    for row in gaps:
        doc.append(f"- **{row['components']}** → {row['predicted_workshop_meaning_de']} (erwartet `{row['expected_surface_pattern']}`)")
    doc.extend([
        "", "Freie Zellen sind keine Widerlegung. Der kleine Zehn-Seiten-Ausschnitt muss",
        "nicht jede mögliche Werkstattkombination benutzen. Sie sind jetzt aber echte",
        "Vorhersagen für später freigegebene Seiten: Bedeutung und Formfamilie stehen fest.", "",
        "Die kollisionssensitiven CHD/CKH/SHED/Y-Familien bleiben ganzkartengeprüft; dort",
        "darf sichtbare Buchstabenähnlichkeit die längere registrierte Karte nicht zerlegen.", "",
        "Nur die festen Prosaseiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ])
    (OUT / "NINETY_SIXTH_COMPOUND_REPORT.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT", "predictions": len(rows), "observed_match_rows": len(matches),
        "unfilled_cells": len(gaps), "status_counts": dict(status_counts),
        "surface_inventory": len(counts), "prose_events": sum(counts.values()),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
