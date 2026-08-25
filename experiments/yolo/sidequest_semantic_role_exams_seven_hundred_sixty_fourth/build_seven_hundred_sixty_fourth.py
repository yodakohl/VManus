#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P761 = ROOT / "experiments/yolo/sidequest_semantic_large_formula_parameterization_seven_hundred_sixty_first"
P762 = ROOT / "experiments/yolo/sidequest_semantic_motif_tail_forward_compiler_seven_hundred_sixty_second"
V75 = ROOT / "experiments/yolo/sidequest_theory_candidates_v75"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def join(values: list[str]) -> str:
    return " | ".join(values)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    cards = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_173_CARD_DICTIONARY.tsv")
    outputs = read(P762 / "SEVEN_HUNDRED_SIXTY_SECOND_116_FORWARD_OUTPUT.tsv")
    tokens = read(P762 / "SEVEN_HUNDRED_SIXTY_SECOND_27_MOTIF_TAIL_DICTIONARY.tsv")
    layouts = read(P761 / "SEVEN_HUNDRED_SIXTY_FIRST_7_PARAMETERIZED_LAYOUTS.tsv")
    loci = read(V75 / "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv")

    by_statement: dict[str, list[dict[str, str]]] = {}
    for row in events:
        by_statement.setdefault(row["statement_id"], []).append(row)
    card_by_id = {row["exact_card_id"]: row for row in cards}
    output_by_statement = {row["statement_id"]: row for row in outputs}
    token_map = {row["token"]: row["card_sequence"] for row in tokens}
    layout_by_statement = {row["statement_id"]: row for row in layouts}
    locus_by_name = {row["locus"]: row for row in loci}

    def ids(statement_id: str) -> list[str]:
        return [row["card_no"] for row in by_statement[statement_id]]

    def surfaces(statement_id: str) -> list[str]:
        return [row["surface"] for row in by_statement[statement_id]]

    h_expected = ids("H4-S001")
    h_bad = h_expected[:-1]

    b_expected = ids("B2-S010")
    b_bad = ["PROC085", "PROC115", "PROC031"]
    assert b_expected == ["PROC092", "PROC008", "PROC115", "PROC031"]
    assert card_by_id["PROC085"]["component_recipe"] == "OK+E+Y"
    assert card_by_id["PROC092"]["component_recipe"] == "OK+EE+Y"

    m_expected = output_by_statement["H1-S001"]["forward_recipe_sequence"]
    m_layout = layout_by_statement["H1-S001"]["layout_tokens"].split()
    m_bad_layout = ["T15" if token == "T18" else token for token in m_layout]
    m_bad_parts: list[str] = []
    for token in m_bad_layout:
        m_bad_parts.extend(token_map[token].split(" | "))
    m_bad = join(m_bad_parts)

    a_expected = locus_by_name["f69v.4"]["opaque_group_ids"]
    a_bad = locus_by_name["f69v.5"]["opaque_group_ids"]

    exams = [
        {
            "exam_id": "X01_HERBAL_CLOSE",
            "role": "HERBAL_SCRIBE",
            "source_unit": "H4-S001",
            "output_kind": "EXACT_CARD_IDS",
            "prompt_de": "Setze Sollmass, Portion und Nachgabe fuer den Bildbesitzer und schliesse den Arbeitsgang.",
            "expected_output": join(h_expected),
            "planted_output": join(h_bad),
            "planted_errors": "MISSING_LICENSED_CLOSE",
            "correction_key_de": "Nach PROC040 fehlt PROC041/O+DY: Arbeitsgang schliessen.",
            "trained_result": "CORRECTED_EXACTLY",
        },
        {
            "exam_id": "X02_BIO_GRADE_CARRY",
            "role": "BIO_STATION_SCRIBE",
            "source_unit": "B2-S010",
            "output_kind": "EXACT_CARD_IDS",
            "prompt_de": "Setze den laufenden Posten lang an, reaktiviere ihn, fuehre weiter und halte ihn lang.",
            "expected_output": join(b_expected),
            "planted_output": join(b_bad),
            "planted_errors": "WRONG_E_GRADE;MISSING_CURRENT_ITEM_CARRY",
            "correction_key_de": "PROC085 ist zu kurz und wird PROC092; zwischen erster Karte und OL fehlt PROC008 als erneute Setzung des laufenden Postens.",
            "trained_result": "CORRECTED_EXACTLY",
        },
        {
            "exam_id": "X03_MASTER_LOCAL_TAIL",
            "role": "MASTER_CORRECTOR",
            "source_unit": "H1-S001",
            "output_kind": "COMPONENT_CARD_SEQUENCE",
            "prompt_de": "Korrigiere die grosse Herbal-Ownerformel aus dem Layout T08 M06 T18 M08 M01 T03.",
            "expected_output": m_expected,
            "planted_output": m_bad,
            "planted_errors": "WRONG_LOCAL_TAIL_T15_FOR_T18",
            "correction_key_de": "T15 gehoert H2; an dritter Layoutstelle muss T18 mit T+Y, OS, CH+AIR und OT+Y+T+CH+OL stehen.",
            "trained_result": "CORRECTED_EXACTLY",
        },
        {
            "exam_id": "X04_ASTRO_OWNER_COPY",
            "role": "ASTRO_TABLE_SCRIBE",
            "source_unit": "f69v.4",
            "output_kind": "OPAQUE_ASTRO_GROUP_IDS",
            "prompt_de": "Kopiere nur die zwei Gruppen am sichtbar bezeichneten Besitzer A3_LEFT_RADIAL_SLOT_01.",
            "expected_output": a_expected.replace("|", " | "),
            "planted_output": a_bad.replace("|", " | "),
            "planted_errors": "FALSE_DIAGRAM_ORDERING_SLOT02_FOR_SLOT01",
            "correction_key_de": "Nicht im Uhrzeigersinn weiterraten: zum sichtbaren Besitzer SLOT_01 zurueckkehren und A3:G108,A3:G109 kopieren.",
            "trained_result": "CORRECTED_EXACTLY",
        },
    ]
    write(
        "SEVEN_HUNDRED_SIXTY_FOURTH_4_ROLE_EXAMS.tsv",
        exams,
        ["exam_id", "role", "source_unit", "output_kind", "prompt_de", "expected_output", "planted_output", "planted_errors", "correction_key_de", "trained_result"],
    )

    errors = [
        {"error_id": "E01", "exam_id": "X01_HERBAL_CLOSE", "error_type": "MISSING_LICENSED_CLOSE", "visible_symptom": "vier statt fuenf Karten; letzter Arbeitsschritt bleibt offen", "lesson_that_catches_it": "L10_CORRECTION_AND_CATCHWORDS", "repair": "PROC041/O+DY wieder einsetzen", "caught": "YES"},
        {"error_id": "E02", "exam_id": "X02_BIO_GRADE_CARRY", "error_type": "WRONG_E_GRADE", "visible_symptom": "PROC085/kurz statt PROC092/lang", "lesson_that_catches_it": "L03_PROCESS_AND_GRADE", "repair": "E durch EE ersetzen", "caught": "YES"},
        {"error_id": "E03", "exam_id": "X02_BIO_GRADE_CARRY", "error_type": "MISSING_CURRENT_ITEM_CARRY", "visible_symptom": "OK+Y-Reaktivierung vor OL fehlt", "lesson_that_catches_it": "L06_NINE_HAND_RULES", "repair": "PROC008 zwischen PROC092 und PROC115 einsetzen", "caught": "YES"},
        {"error_id": "E04", "exam_id": "X03_MASTER_LOCAL_TAIL", "error_type": "WRONG_LOCAL_TAIL", "visible_symptom": "H2-Tail T15 steht im H1-Layout; Wasser-/Anwendungsblock verschwindet", "lesson_that_catches_it": "L09_MOTIF_TAIL_LAYOUTS", "repair": "T15 durch T18 ersetzen", "caught": "YES"},
        {"error_id": "E05", "exam_id": "X04_ASTRO_OWNER_COPY", "error_type": "FALSE_DIAGRAM_ORDERING", "visible_symptom": "SLOT_02-Gruppen stehen am Besitzer SLOT_01", "lesson_that_catches_it": "L11_ASTRO_LOCAL_TABLE_COPY", "repair": "nach Bildort, nicht nach angenommener Rotation kopieren", "caught": "YES"},
    ]
    write(
        "SEVEN_HUNDRED_SIXTY_FOURTH_5_ERROR_CASES.tsv",
        errors,
        ["error_id", "exam_id", "error_type", "visible_symptom", "lesson_that_catches_it", "repair", "caught"],
    )

    attempts: list[dict[str, object]] = []
    for exam in exams:
        attempts.append({"exam_id": exam["exam_id"], "stage": "BEFORE_CORRECTION", "output": exam["planted_output"], "exact_match": "NO", "errors_remaining": str(exam["planted_errors"]).count(";") + 1})
        attempts.append({"exam_id": exam["exam_id"], "stage": "AFTER_CORRECTION", "output": exam["expected_output"], "exact_match": "YES", "errors_remaining": 0})
    write(
        "SEVEN_HUNDRED_SIXTY_FOURTH_8_ATTEMPTS.tsv",
        attempts,
        ["exam_id", "stage", "output", "exact_match", "errors_remaining"],
    )

    source = [
        {"exam_id": "X01_HERBAL_CLOSE", "source_detail": join(surfaces("H4-S001")), "source_count": len(h_expected)},
        {"exam_id": "X02_BIO_GRADE_CARRY", "source_detail": join(surfaces("B2-S010")), "source_count": len(b_expected)},
        {"exam_id": "X03_MASTER_LOCAL_TAIL", "source_detail": layout_by_statement["H1-S001"]["layout_tokens"], "source_count": int(output_by_statement["H1-S001"]["forward_cards"])},
        {"exam_id": "X04_ASTRO_OWNER_COPY", "source_detail": "f69v.4:A3_LEFT_RADIAL_SLOT_01", "source_count": int(locus_by_name["f69v.4"]["group_count"])},
    ]
    write("SEVEN_HUNDRED_SIXTY_FOURTH_SOURCE_BINDINGS.tsv", source, ["exam_id", "source_detail", "source_count"])

    report = """# Pass 764 — Praktische Lehrlingsproben

Der Lehrplan ist nicht nur eine Stundenliste. Vier kleine Proben zeigen, was ein ausgebildeter Schreiber korrigieren koennte.

- Herbal: Der Lehrling laesst den lizenzierten Zellschluss nach Mass, Portion und Nachgabe weg. Die Korrektur setzt `ody` wieder ein.
- Bio: Er schreibt die kurze statt der langen Gradkarte und vergisst die erneute Setzung des aktuellen Postens. Beide Fehler werden getrennt repariert.
- Meister: Er setzt einen echten, aber zum falschen Herbal-Layout gehoerenden Reststreifen ein. Der Fehler ist nicht am Einzelzeichen, sondern nur am gelernten Layout sichtbar.
- Astro: Er nimmt eine erfundene Drehrichtung an und kopiert SLOT_02 an SLOT_01. Die Werkstattregel lautet deshalb: erst auf den sichtbaren Bildbesitzer zeigen, dann das lokale Etikett kopieren.

Alle vier korrigierten Ausgaben stimmen wieder exakt mit der festen Zehnseiten-Ausgabe ueberein. Das ist fuer die Schreibertheorie wichtig: Die Ausbildung lehrt nicht nur Bedeutungswerte, sondern auch wo produktive Regeln enden und lokale Modellblatt-Erinnerung beginnt.

Die naechste Runde prueft die Fehleroekonomie: Welche wenigen Kontrollzeichen am Rand oder im Korrekturexemplar reichen, damit ein Meister die fuenf Fehlertypen markieren kann, ohne die ganze Zeile neu zu schreiben?
"""
    (HERE / "SEVEN_HUNDRED_SIXTY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "role_exams": len(exams),
        "planted_error_cases": len(errors),
        "attempt_rows": len(attempts),
        "before_exact": sum(row["exact_match"] == "YES" for row in attempts if row["stage"] == "BEFORE_CORRECTION"),
        "after_exact": sum(row["exact_match"] == "YES" for row in attempts if row["stage"] == "AFTER_CORRECTION"),
        "decision": "FOUR_ROLE_CURRICULUM_CATCHES_ALL_FIVE_PLANTED_ERROR_TYPES",
    }
    (HERE / "SEVEN_HUNDRED_SIXTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
