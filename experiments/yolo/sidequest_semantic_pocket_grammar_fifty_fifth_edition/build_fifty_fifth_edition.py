#!/usr/bin/env python3
"""Build the one-page desk grammar for a workshop apprentice."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
HIERARCHY = ROOT / "experiments/yolo/sidequest_semantic_hierarchical_dictionary_fifty_fourth_edition/FIFTY_FOURTH_89_HIERARCHICAL_ENTRIES.tsv"
BOUNDARIES = ROOT / "experiments/yolo/sidequest_semantic_hierarchical_dictionary_fifty_fourth_edition/FIFTY_FOURTH_12_BOUNDARY_EXAMPLES.tsv"
TRACES = ROOT / "experiments/yolo/sidequest_semantic_simulated_master_exemplar_fifty_third_edition/FIFTY_THIRD_12_APPRENTICE_TRACES.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    hierarchy = read_tsv(HIERARCHY)
    boundaries = read_tsv(BOUNDARIES)
    traces = read_tsv(TRACES)
    rules = [
        ("A01", "VORBEREITEN", "OWNER", "Zuerst Bild, Becken, Tuch, Rad oder Werkstück als Besitzer setzen."),
        ("A02", "VORBEREITEN", "ACTIVE", "Den gerade bearbeiteten Posten setzen und bis zum echten Wechsel behalten."),
        ("A03", "VORBEREITEN", "TARGET", "Ziel nur bei AL oder sichtbarer Zielstation setzen; bei neuem Gang löschen."),
        ("A04", "VORBEREITEN", "PREVIOUS", "Beim Postenwechsel genau den unmittelbar vorigen Posten merken."),
        ("B01", "LESEN", "LONGEST", "Zuerst den längsten gelernten Fachkörper oder die ganze Karte lesen."),
        ("B02", "LESEN", "ORDER", "Dann Reihenfolge lesen: OT folgend, OL fortsetzen, OK ansetzen."),
        ("B03", "LESEN", "ACTION", "Danach Handlung: CHD umsetzen, CKH durchführen, CKHE trennen, CHK wärmen, SHED absetzen, SOLK sammeln."),
        ("B04", "LESEN", "SOURCE", "AR nennt die Quelle; AIR den Lauf oder die Bahn."),
        ("B05", "LESEN", "QUANTITY", "AIIN ist Sollwert, AIN Portion, IIN Stufe."),
        ("B06", "LESEN", "TARGET", "AL nennt das Ziel; der Besitzer sagt, welches konkrete Ziel."),
        ("B07", "LESEN", "GRADE", "E kurz, EE länger, EEE vollständig – nur in der lizenzierten Familie."),
        ("B08", "LESEN", "REFERENT", "Y heißt dieser Posten; ACTIVE sagt, welcher."),
        ("B09", "LESEN", "CLOSE", "Nur eine gelernte Schlusskarte schließt; sichtbares dy allein tut es nicht."),
        ("C01", "SATZ", "LINE", "Zeilenende beendet keinen Satz und löscht kein Merkfach."),
        ("C02", "SATZ", "OWNER_SWITCH", "Ein sichtbarer Szenenwechsel darf OWNER mitten im Satz umschalten."),
        ("C03", "SATZ", "MACRO", "Wiederkehrende Zwei-/Dreiklauselzüge als Arbeitsmakro merken, nie als Wort."),
        ("C04", "SATZ", "OWNER_NOUN", "Konkrete Pflanze, Flüssigkeit, Schale, Tuch oder Sternstelle kommt vom Besitzer."),
        ("D01", "SCHREIBEN", "WHOLE", "Wenn eine ganze registrierte Karte existiert, genau diese abschreiben."),
        ("D02", "SCHREIBEN", "ANALYTIC", "Sonst Basis und Endung als zwei Karten schreiben, wenn beide existieren."),
        ("D03", "SCHREIBEN", "PARAPHRASE", "Sonst die gelernte Umschreibung benutzen und ihre Zusatznuance mitsprechen."),
        ("D04", "SCHREIBEN", "MASTER", "Sonst beim Meister nachfragen; keine sichtbare Form erfinden."),
        ("E01", "ASTRO", "LOCAL", "Jedes Rad, Paneel und jeder Sternplatz bleibt in seinem lokalen Namensraum."),
        ("E02", "ASTRO", "ORIENTATION", "Ohne sichtbaren Zeiger weder Start noch Richtung noch Rotation einsetzen."),
        ("E03", "ASTRO", "NO_JOIN", "f68 und f69 nicht koppeln; lokale Werte nur aus dem jeweiligen Exemplar ergänzen."),
    ]
    rule_rows = [
        {"teaching_order": index, "rule_id": rule_id, "desk_phase": phase, "cue": cue, "apprentice_rule_de": text}
        for index, (rule_id, phase, cue, text) in enumerate(rules, 1)
    ]
    write_tsv(OUT / "FIFTY_FIFTH_24_DESK_RULES.tsv", rule_rows)

    examples = []
    for index, trace in enumerate(traces, 1):
        boundary = boundaries[(index - 1) % len(boundaries)]
        examples.append({
            "example_no": index,
            "lesson_branch": trace["lesson_branch"],
            "source_instruction_de": trace["source_instruction_de"],
            "lookup_atom_sequence": trace["lookup_atom_sequence"],
            "written_sequence": trace["written_sequence"],
            "readback_de": trace["readback_de"],
            "boundary_reminder_de": boundary["why_not_one_word_de"],
            "result": trace["roundtrip_status"],
        })
    write_tsv(OUT / "FIFTY_FIFTH_12_POCKET_EXAMPLES.tsv", examples)

    roots = [row for row in hierarchy if row["hierarchy_level"] == "L1_ATOMIC_ROOT"]
    root_line = "; ".join(f"{row['surface_symbol_or_pattern']}={row['short_value_de']}" for row in roots)
    doc = [
        "# Taschengrammatik für den Schreibertisch",
        "",
        "## Die 28 kurzen Kartenwerte",
        "",
        root_line + ".",
        "",
        "## Vor jedem Satz",
        "",
        "Bildbesitzer setzen → aktuellen Posten setzen → Ziel nur bei Bedarf setzen →",
        "genau einen vorigen Posten merken.",
        "",
        "## Karte lesen",
        "",
        "Längsten gelernten Körper zuerst. Dann: Reihenfolge → Handlung → Quelle/Lauf →",
        "Menge/Stufe → Ziel → Grad → dieser Posten → gelernter Schluss.",
        "",
        "Eine Zeile ist nur Platz. Ein Bildwechsel kann den Besitzer ändern. Der Besitzer",
        "liefert konkrete Dinge; die Karte liefert nur ihren kurzen Arbeitswert.",
        "",
        "## Karte schreiben",
        "",
        "1. Ganze Registerkarte. 2. Zwei vorhandene Karten. 3. Gelernte Umschreibung",
        "mit ausgesprochener Zusatznuance. 4. Sonst Meister fragen.",
        "",
        "## Astro",
        "",
        "Rad und Paneel lokal halten. Keine unsichtbare Startstelle, Richtung oder Rotation.",
        "f68 und f69 nicht koppeln.",
        "",
        "## Vier Muster",
        "",
    ]
    pocket_examples = []
    for branch in ("OBSERVED_FUSED", "ANALYTIC_OBSERVED", "ANALYTIC_MASTER", "CONTROLLED_PARAPHRASE"):
        pocket_examples.append(next(row for row in examples if row["lesson_branch"] == branch))
    for row in pocket_examples:
        doc.append(f"- {row['source_instruction_de']} → `{row['written_sequence']}` → {row['readback_de']}.")
    (OUT / "FIFTY_FIFTH_ONE_PAGE_POCKET_GRAMMAR.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "desk_rules": len(rule_rows),
            "pocket_examples": len(examples),
            "atomic_roots_listed": len(roots),
            "pocket_lines": len(doc),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (HIERARCHY, BOUNDARIES, TRACES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
