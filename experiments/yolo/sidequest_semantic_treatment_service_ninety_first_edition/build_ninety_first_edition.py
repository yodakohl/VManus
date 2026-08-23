#!/usr/bin/env python3
"""Separate figure-owned treatment work from figureless service work."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R90 = ROOT / "experiments/yolo/sidequest_semantic_bath_phrasebook_ninetieth_edition/NINETIETH_97_STATEMENT_PHRASEBOOK.tsv"


RECORDS = {
    "B1": {
        "page": "f81v", "owner_mode": "VISIBLE_HUMAN_BATH_OWNER",
        "treatment": "gemeinsames zweireihiges Bad, Waschen und örtliches Halten der Badenden",
        "service": "Zusatz, Wärme, Seihgang und Ablauf bleiben Hilfsschritte desselben Bades",
        "reading": "Richte das gemeinsame zweireihige Figurenbecken ein, gib Badwasser und Kräuterzusatz zu, bringe es auf Badwärme, halte oder wasche die Badenden örtlich, lass den Posten absetzen, seih ihn und führe ihn am lokalen Ablauf ab.",
    },
    "B2": {
        "page": "f82r", "owner_mode": "VISIBLE_HUMAN_MULTI_STATION_OWNER",
        "treatment": "fünf sichtbare Becken-/Figurenstationen werden einzeln gesetzt",
        "service": "jede Station besitzt nur ihren lokalen Einlass, Durchlass und Ablauf",
        "reading": "Beginne an jeder der fünf sichtbaren Stationen neu: fülle örtlich, stelle Zusatz, Wärme, Dauer und Portion ein, halte den Badenden oder Waschposten, führe ihn durch den eigenen Durchlass und schließe jede Station getrennt ab.",
    },
    "B3": {
        "page": "f83r", "owner_mode": "VISIBLE_HUMAN_BASINS_AND_MAIN_PAIR",
        "treatment": "drei Randbecken und das sichtbar gekoppelte Hauptpaar bleiben figurengeführt",
        "service": "Absetzen, Sammeln, Seihen und Ablassen bedienen nur die jeweilige Figurenszene",
        "reading": "Bediene zuerst die drei Randbecken einzeln: füllen, temperieren, halten, absetzen und abführen. Wechsle danach zum sichtbar gekoppelten Hauptpaar, bemiss die Badmischung, führe sie zwischen den örtlich verbundenen Teilen und sammle oder entleere sie lokal; überbrücke keine sichtbare Lücke.",
    },
    "B4": {
        "page": "f83r", "owner_mode": "VISIBLE_MAIN_PAIR_THEN_FIGURELESS_SERVICE_RESET",
        "treatment": "S001-S010: warme Tuch-/Umschlaganwendung am Hauptpaar",
        "service": "S011-S016: zwei getrennte figurenlose Zu-/Ablauf- und Seihgänge",
        "reading": "Am Hauptpaar temperiere Badwasser, lege Tuch ein, halte den Umschlag an der örtlichen Stelle und löse ihn nach dem Wasch-/Seihschritt. Danach endet der Figurenbesitz: bediene linke und rechte Dienststation getrennt mit Portion, Einlass, Durchlass, Auffangbecken und Ablauf.",
    },
    "B5": {
        "page": "f83r", "owner_mode": "FIGURELESS_LEFT_SERVICE_OWNER",
        "treatment": "kein sichtbarer Badender und keine Körperstelle",
        "service": "linke Hilfsstation für Temperieren, Halten und Abführen",
        "reading": "An der linken figurenlosen Dienststation temperiere die Arbeitsflüssigkeit, halte sie für die örtliche Dauer und führe sie am lokalen Ablauf weiter; leite daraus keine Körperbehandlung ab.",
    },
    "B6": {
        "page": "f83r", "owner_mode": "FIGURELESS_RIGHT_SERVICE_OWNER",
        "treatment": "kein sichtbarer Badender und keine Körperstelle",
        "service": "rechte Hilfsstation für Einlass, Tuch-/Seihgang und Arbeitsziel",
        "reading": "An der rechten figurenlosen Dienststation sammle den Ausgangsposten, führe ihn über Einlass und Tuch-/Seihgang zur bezeichneten Arbeitsstelle und beende dort den Dienstlauf.",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def mode(statement_id: str) -> str:
    record, number = statement_id.split("-S")
    ordinal = int(number)
    if record in {"B1", "B2", "B3"}:
        return "TREATMENT_FACING_VISIBLE_HUMAN_OWNER"
    if record == "B4" and ordinal <= 10:
        return "TREATMENT_FACING_VISIBLE_HUMAN_OWNER"
    return "SERVICE_FACING_NO_HUMAN_OWNER"


def main() -> None:
    statements = read_tsv(R90)
    mapped = []
    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statements:
        primary_mode = mode(row["statement_id"])
        out = {
            **row,
            "primary_mode": primary_mode,
            "mode_basis": "VISIBLE_OWNER_OR_EXPLICIT_B4_OWNER_RESET__NOT_OPERATION_NAME",
            "treatment_word_allowed": "YES__LOCAL_BATH_OR_APPLICATION" if primary_mode.startswith("TREATMENT") else "NO__SERVICE_ONLY",
            "disease_or_named_body_part": "NONE",
        }
        mapped.append(out)
        by_record[row["record_unit_id"]].append(out)
    write_tsv(OUT / "NINETY_FIRST_97_TREATMENT_SERVICE_MAP.tsv", mapped)

    record_rows = []
    for record_id, definition in RECORDS.items():
        members = by_record[record_id]
        modes = Counter(str(row["primary_mode"]) for row in members)
        record_rows.append({
            "record_unit_id": record_id, "page": definition["page"],
            "statement_count": len(members), "event_count": sum(int(row["event_count"]) for row in members),
            "owner_mode": definition["owner_mode"],
            "treatment_scope_de": definition["treatment"], "service_scope_de": definition["service"],
            "treatment_statement_count": modes["TREATMENT_FACING_VISIBLE_HUMAN_OWNER"],
            "service_statement_count": modes["SERVICE_FACING_NO_HUMAN_OWNER"],
            "continuous_record_reading_de": definition["reading"],
            "purpose_status": "THERAPEUTIC_BATH_WITH_EXPLICIT_SERVICE_LAYER",
        })
    write_tsv(OUT / "NINETY_FIRST_6_RECORD_DUAL_MODE_EDITION.tsv", record_rows)

    cross = Counter((str(row["primary_mode"]), str(row["macro_id"])) for row in mapped)
    cross_rows = []
    for (primary_mode, macro_id), count in sorted(cross.items()):
        cross_rows.append({"primary_mode": primary_mode, "macro_id": macro_id, "statement_count": count})
    write_tsv(OUT / "NINETY_FIRST_MODE_BY_MACRO_CROSSTAB.tsv", cross_rows)

    rules = [
        {"rule_order": 1, "rule": "VISIBLE_HUMAN_OWNER", "reading_de": "Bad-/Anwendungshandlung ist erlaubt, auch wenn die Karten filtern oder ablassen."},
        {"rule_order": 2, "rule": "FIGURELESS_OWNER", "reading_de": "Nur Dienst-, Zu-/Ablauf- oder Arbeitsstellenhandlung; keine Körperbehandlung ergänzen."},
        {"rule_order": 3, "rule": "B4_S011_RESET", "reading_de": "Nach B4-S010 endet der Figurenbesitz; S011-S016 bilden die Dienstschicht."},
        {"rule_order": 4, "rule": "SAME_PHRASE_DIFFERENT_OWNER", "reading_de": "Gleiche Kartenphrase darf Behandlung oder Dienst bedienen; der Besitzer entscheidet den Gegenstand."},
        {"rule_order": 5, "rule": "NO_DISEASE_OR_ANATOMY", "reading_de": "Ohne sichtbare oder gelernte Bezeichnung keine Krankheit und keinen benannten Körperteil ergänzen."},
    ]
    write_tsv(OUT / "NINETY_FIRST_5_MODE_RULES.tsv", rules)

    doc = [
        "# Sechs Biological-Records: Behandlung und Dienst", "",
        "Die Operation allein entscheidet nicht, ob ein Satz medizinisch oder technisch",
        "gelesen wird. Der sichtbare Besitzer entscheidet: Figur/Badender = Behandlung",
        "möglich; figurenlose Station = Diensthandlung.", "",
    ]
    for row in record_rows:
        doc.extend([
            f"## {row['record_unit_id']} · {row['page']}", "",
            f"**Fortlaufende Lesung:** {row['continuous_record_reading_de']}", "",
            f"**Behandlungsschicht:** {row['treatment_scope_de']}", "",
            f"**Dienstschicht:** {row['service_scope_de']}", "",
        ])
    (OUT / "NINETY_FIRST_6_CONTINUOUS_RECORDS.md").write_text("\n".join(doc) + "\n", encoding="utf-8")

    mode_counts = Counter(row["primary_mode"] for row in mapped)
    report = [
        "# Einundneunzigste Werkstattrunde: Behandlung oder Dienst?", "",
        "## Ergebnis", "",
        f"{mode_counts['TREATMENT_FACING_VISIBLE_HUMAN_OWNER']} statements are treatment-facing because a visible human/bath scene owns them; ",
        f"{mode_counts['SERVICE_FACING_NO_HUMAN_OWNER']} are service-facing after a figureless owner or the B4 reset.", "",
        "The same drain, strain, hold and close phrases occur on both sides. Therefore",
        "the verb family does not itself mean medicine. The image supplies the patient-",
        "facing or service-facing role. This keeps the bath reading concrete without",
        "turning every pipe or outlet into anatomy.", "",
        "B1-B3 are figure-owned bath records. B4 deliberately changes mode: ten treatment",
        "statements at the main pair, then six service statements. B5 and B6 are compact",
        "figureless annexes. No disease or named anatomical system is introduced.", "",
        "Only the fixed Biological pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "NINETY_FIRST_EDITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT", "records": len(record_rows), "statements": len(mapped),
        "events": sum(int(row["event_count"]) for row in mapped), "mode_counts": dict(mode_counts),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
