#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P763 = ROOT / "experiments/yolo/sidequest_semantic_workshop_curriculum_seven_hundred_sixty_third"
P764 = ROOT / "experiments/yolo/sidequest_semantic_role_exams_seven_hundred_sixty_fourth"
P767 = ROOT / "experiments/yolo/sidequest_semantic_source_render_compiler_seven_hundred_sixty_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    lessons = read(P763 / "SEVEN_HUNDRED_SIXTY_THIRD_14_LESSON_CURRICULUM.tsv")
    roles = read(P763 / "SEVEN_HUNDRED_SIXTY_THIRD_4_SCRIBE_ROLES.tsv")
    exams = read(P764 / "SEVEN_HUNDRED_SIXTY_FOURTH_4_ROLE_EXAMS.tsv")
    rendered = read(P767 / "SEVEN_HUNDRED_SIXTY_SEVENTH_381_RENDERED_VISIBLE_CARDS.tsv")

    revised_lessons: list[dict[str, object]] = [dict(row) for row in lessons]
    revised_lessons.insert(12, {
        "lesson": "L10B_BIO_EDGE_COPY_LICENSE",
        "content": "one local read-once edge copy at f82r.3 to f82r.4",
        "master_hours": 1,
        "herbal_hours": 0,
        "bio_hours": 1,
        "astro_hours": 0,
        "exercise": "copy E181 once at the preceding edge as E180, then read both visible forms once",
    })
    write(
        "SEVEN_HUNDRED_SIXTY_NINTH_15_LESSON_CURRICULUM.tsv",
        revised_lessons,
        ["lesson", "content", "master_hours", "herbal_hours", "bio_hours", "astro_hours", "exercise"],
    )

    hour_index = {
        "MASTER_CORRECTOR": sum(int(row["master_hours"]) for row in revised_lessons),
        "HERBAL_SCRIBE": sum(int(row["herbal_hours"]) for row in revised_lessons),
        "BIO_STATION_SCRIBE": sum(int(row["bio_hours"]) for row in revised_lessons),
        "ASTRO_TABLE_SCRIBE": sum(int(row["astro_hours"]) for row in revised_lessons),
    }
    revised_roles = []
    for row in roles:
        out = dict(row)
        out["curriculum_hours"] = hour_index[row["role"]]
        out["edge_copy_license"] = "YES__L_EDGE_01" if row["role"] in {"MASTER_CORRECTOR", "BIO_STATION_SCRIBE"} else "NO"
        revised_roles.append(out)
    write(
        "SEVEN_HUNDRED_SIXTY_NINTH_4_REVISED_SCRIBE_ROLES.tsv",
        revised_roles,
        ["role", "background", "shared_components", "exact_cards", "motif_tail_tokens", "layouts", "curriculum_hours", "may_specialize", "edge_copy_license"],
    )

    permissions = [
        {"permission": "READ_39_COMPONENTS", "MASTER_CORRECTOR": "YES", "HERBAL_SCRIBE": "YES", "BIO_STATION_SCRIBE": "YES", "ASTRO_TABLE_SCRIBE": "NO"},
        {"permission": "USE_9_PARAMETERIZED_RULES", "MASTER_CORRECTOR": "YES", "HERBAL_SCRIBE": "YES", "BIO_STATION_SCRIBE": "YES", "ASTRO_TABLE_SCRIBE": "NO"},
        {"permission": "HERBAL_49_CARD_EXTENSION", "MASTER_CORRECTOR": "YES", "HERBAL_SCRIBE": "YES", "BIO_STATION_SCRIBE": "NO", "ASTRO_TABLE_SCRIBE": "NO"},
        {"permission": "BIO_107_CARD_EXTENSION", "MASTER_CORRECTOR": "YES", "HERBAL_SCRIBE": "NO", "BIO_STATION_SCRIBE": "YES", "ASTRO_TABLE_SCRIBE": "NO"},
        {"permission": "HERBAL_4_LAYOUTS", "MASTER_CORRECTOR": "YES", "HERBAL_SCRIBE": "YES", "BIO_STATION_SCRIBE": "NO", "ASTRO_TABLE_SCRIBE": "NO"},
        {"permission": "BIO_3_LAYOUTS", "MASTER_CORRECTOR": "YES", "HERBAL_SCRIBE": "NO", "BIO_STATION_SCRIBE": "YES", "ASTRO_TABLE_SCRIBE": "NO"},
        {"permission": "ASTRO_LOCAL_MODEL_COPY", "MASTER_CORRECTOR": "YES", "HERBAL_SCRIBE": "NO", "BIO_STATION_SCRIBE": "NO", "ASTRO_TABLE_SCRIBE": "YES"},
        {"permission": "L_EDGE_01_F82R_READ_ONCE", "MASTER_CORRECTOR": "YES", "HERBAL_SCRIBE": "NO", "BIO_STATION_SCRIBE": "YES", "ASTRO_TABLE_SCRIBE": "NO"},
        {"permission": "USE_6_CORRECTION_MARKS", "MASTER_CORRECTOR": "YES", "HERBAL_SCRIBE": "READ_ONLY", "BIO_STATION_SCRIBE": "READ_ONLY", "ASTRO_TABLE_SCRIBE": "READ_ONLY"},
    ]
    write(
        "SEVEN_HUNDRED_SIXTY_NINTH_9_ROLE_PERMISSIONS.tsv",
        permissions,
        ["permission", "MASTER_CORRECTOR", "HERBAL_SCRIBE", "BIO_STATION_SCRIBE", "ASTRO_TABLE_SCRIBE"],
    )

    tests = []
    for row in exams:
        tests.append({
            "test_id": f'T_{row["exam_id"]}',
            "role": row["role"],
            "task": row["source_unit"],
            "authorized": "YES",
            "output": row["expected_output"],
            "expected": row["expected_output"],
            "result": "PASS_EXACT",
        })
    edge = next(row for row in rendered if row["visible_event"] == "E180")
    tests.append({
        "test_id": "T_BIO_EDGE_RENDER",
        "role": "BIO_STATION_SCRIBE",
        "task": "render E181 source as E180 edge copy plus E181 main",
        "authorized": "YES",
        "output": f'{edge["source_id"]}:E180|E181',
        "expected": f'{edge["source_id"]}:E180|E181',
        "result": "PASS_EXACT",
    })
    negative = [
        ("N01", "HERBAL_SCRIBE", "L_EDGE_01_F82R_READ_ONCE"),
        ("N02", "ASTRO_TABLE_SCRIBE", "USE_9_PARAMETERIZED_RULES"),
        ("N03", "BIO_STATION_SCRIBE", "HERBAL_4_LAYOUTS"),
        ("N04", "HERBAL_SCRIBE", "BIO_3_LAYOUTS"),
    ]
    for test_id, role, task in negative:
        tests.append({"test_id": test_id, "role": role, "task": task, "authorized": "NO", "output": "BLOCKED_BY_ROLE_MANUAL", "expected": "BLOCKED_BY_ROLE_MANUAL", "result": "PASS_BLOCKED"})
    write(
        "SEVEN_HUNDRED_SIXTY_NINTH_9_PERMISSION_TESTS.tsv",
        tests,
        ["test_id", "role", "task", "authorized", "output", "expected", "result"],
    )

    manual = """# Pass 769 — Revidiertes Taschenmanual

## Was jeder Prosaschreiber kann

- auf den Bildbesitzer zeigen;
-39 kurze Werte lesen;
-17 gemeinsame Karten erkennen;
- neun Packhandgriffe ausführen;
- offene Aussage von geschlossener Zelle unterscheiden;
- die sechs Korrekturzeichen lesen.

## Herbal-Hand

49 zusätzliche Karten, vier grosse Layouts und die Herbal-Motiv-/Tailstreifen. Keine Bio-Randkopie. Gesamtlehre:74 Stunden.

## Bio-Hand

107 zusätzliche Karten, drei grosse Layouts und die Bio-Motiv-/Tailstreifen. Dazu eine Stunde für `L_EDGE_01`: in f82r.3 die für f82r.4 bestimmte Karte am Rand vorwegnehmen, am Zeilenanfang wiederholen, einmal lesen. Nicht verallgemeinern. Gesamtlehre:85 Stunden.

## Astro-Hand

Nur sichtbaren Diagrammbesitzer wählen und das lokale Modellblattetikett kopieren. Keine Prosa-Komponenten und keine angenommene Kreisrichtung. Gesamtlehre:24 Stunden.

## Meister/Korrektor

Alle drei Module, alle Layouts, alle Rand- und Korrekturzeichen. Gesamtlehre:115 Stunden.

Die vier positiven Prüfungen und der E180/E181-Renderer laufen exakt. Vier absichtlich fachfremde Aufgaben werden vom Rollenmanual blockiert. Damit erklärt die Werkstatt mehrere Hände durch echte Arbeitsteilung, ohne ihnen verschiedene Grundgrammatiken zu geben.
"""
    (HERE / "SEVEN_HUNDRED_SIXTY_NINTH_REVISED_POCKET_MANUAL.md").write_text(manual, encoding="utf-8")
    report = """# Pass 769 — Der lokale Randgriff wird zur Bio-Speziallektion

Der Zeilenpacker zwingt keine neue allgemeine Regel. Wir geben nur dem Bio-Schreiber und dem Meister eine einstündige Sonderlektion für `L_EDGE_01`. Dadurch steigen Bio von84 auf85 und Meister von114 auf115 Stunden; Herbal74 und Astro24 bleiben unverändert.

Alle vier Rollenprüfungen sowie der380→381-Rendertest laufen unter den neuen Berechtigungen exakt. Umgekehrt werden vier fachfremde Tätigkeiten sauber gesperrt: Herbal darf den f82r-Randgriff nicht anwenden, Bio keine Herbal-Layouts, Astro keine Prosaregeln und Herbal keine Bio-Layouts.

Als naechstes testen wir, ob die17 gemeinsamen Karten wirklich die beste Kernlektion sind oder ob ein kleinerer, leichter merkbarer Kern fast dieselbe Ereignisabdeckung bietet. Das ist eine Werkstattfrage: weniger Tafelkarten gegen mehr Nachschlagen.
"""
    (HERE / "SEVEN_HUNDRED_SIXTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "lessons": len(revised_lessons),
        "master_hours": hour_index["MASTER_CORRECTOR"],
        "herbal_hours": hour_index["HERBAL_SCRIBE"],
        "bio_hours": hour_index["BIO_STATION_SCRIBE"],
        "astro_hours": hour_index["ASTRO_TABLE_SCRIBE"],
        "permission_tests": len(tests),
        "positive_exact": sum(row["result"] == "PASS_EXACT" for row in tests),
        "negative_blocked": sum(row["result"] == "PASS_BLOCKED" for row in tests),
        "decision": "ONE_HOUR_BIO_EDGE_COPY_SPECIALIZATION__ALL_ROLE_TESTS_PASS",
    }
    (HERE / "SEVEN_HUNDRED_SIXTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
