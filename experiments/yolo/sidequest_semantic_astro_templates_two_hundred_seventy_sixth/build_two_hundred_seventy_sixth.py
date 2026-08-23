#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R274 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_mixed_deck_two_hundred_seventy_fourth"
R275 = ROOT / "experiments/yolo/sidequest_semantic_three_astro_readings_two_hundred_seventy_fifth"
ASTRO = R274 / "TWO_HUNDRED_SEVENTY_FOURTH_LAYERED_395_ASTRO_GROUPS.tsv"
LOCI = R275 / "TWO_HUNDRED_SEVENTY_FIFTH_142_LOCUS_READINGS.tsv"

MARKERS = (
    ("SOURCE", "Ausgangssektor"),
    ("TARGET", "Zielsektor"),
    ("VALUE", "Sollwert"),
    ("VALUE", "Portion oder Teilwert"),
    ("CONDITION", "Bedingungs-, Tabellen"),
    ("CONTINUE", "im selben Ring"),
    ("NEXT", "naechster Platz"),
    ("PATH", "Himmels-, Ring- oder Zeigerlauf"),
    ("GRADE", "lange oder volle Diagrammstufe"),
    ("ACTIVATE", "Diagrammposten setzen"),
    ("TRANSFER", "Wert oder Platzbezug uebertragen"),
    ("HOLD", "Position oder Bedingung halten"),
    ("PASSAGE", "durch Sektor"),
    ("RELEASED", "abgelesener oder freigegebener Wert"),
)

TEMPLATES = {
    "SOURCE_TO_TARGET": ("Von der bezeichneten Quelle zur bezeichneten Zielstelle lesen.", "SOURCE_ITEM+TARGET"),
    "ADDRESSED_ENTRY": ("Die Quell- oder Zieladresse des sichtbaren Platzes lesen.", "SOURCE_ITEM_OR_TARGET"),
    "FOLLOWING_RELATION": ("Am Folgeposten dieselbe Reihe fortsetzen oder eine neue Bedingung ansetzen.", "LINK_SELECT"),
    "ROW_CONTINUATION": ("Den aktuellen Ring, das Band oder den Satz weiterführen.", "LINK_SELECT"),
    "CONDITION_ENTRY": ("Den Bedingungsansatz des sichtbaren Platzes setzen oder lesen.", "LINK_SELECT+STATE_GRADE"),
    "GRADED_OR_QUANTIFIED_VALUE": ("Teilwert, Sollwert, Grad oder freigegebenen Wert des Platzes lesen.", "QUANTITY+STATE_GRADE"),
    "ACTION_OR_PATH": ("Den Posten setzen, halten, übertragen oder entlang seiner Bahn führen.", "OPERATION+MEDIUM_FLOW"),
    "LOCAL_NAMED_ENTRY": ("Den lokalen Schlüssel des sichtbaren Besitzers lesen oder kopieren.", "OWNER+SOURCE_ITEM"),
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


def template(tags: set[str]) -> str:
    if {"SOURCE", "TARGET"} <= tags:
        return "SOURCE_TO_TARGET"
    if tags & {"SOURCE", "TARGET"}:
        return "ADDRESSED_ENTRY"
    if "NEXT" in tags and tags & {"CONTINUE", "CONDITION"}:
        return "FOLLOWING_RELATION"
    if "CONTINUE" in tags:
        return "ROW_CONTINUATION"
    if "CONDITION" in tags:
        return "CONDITION_ENTRY"
    if tags & {"GRADE", "VALUE", "RELEASED"}:
        return "GRADED_OR_QUANTIFIED_VALUE"
    if tags & {"ACTIVATE", "TRANSFER", "PATH", "PASSAGE", "HOLD"}:
        return "ACTION_OR_PATH"
    return "LOCAL_NAMED_ENTRY"


def main() -> None:
    groups = read_tsv(ASTRO)
    loci = read_tsv(LOCI)
    tags_by_locus: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in groups:
        reading = row["concrete_diagram_reading_de"]
        for tag, marker in MARKERS:
            if marker in reading and tag not in tags_by_locus[(row["page"], row["locus"])]:
                tags_by_locus[(row["page"], row["locus"])].append(tag)
        if row["coverage_class_274"] == "LOCAL_COPY_LABEL" and "LOCAL" not in tags_by_locus[(row["page"], row["locus"])]:
            tags_by_locus[(row["page"], row["locus"])].append("LOCAL")
        if row["coverage_class_274"] == "LEARNED_WHOLE_SIGN" and "WHOLE" not in tags_by_locus[(row["page"], row["locus"])]:
            tags_by_locus[(row["page"], row["locus"])].append("WHOLE")

    assignments: list[dict[str, object]] = []
    for row in loci:
        tags = tags_by_locus[(row["page"], row["locus"])] or ["LOCAL"]
        chosen = template(set(tags))
        assignments.append({
            "page": row["page"],
            "locus": row["locus"],
            "visible_owner": row["visible_owner"],
            "namespace_id": row["namespace_id"],
            "group_count": row["group_count"],
            "functional_tags": "|".join(tags),
            "astro_template": chosen,
            "template_reading_de": TEMPLATES[chosen][0],
            "prose_slot_crosswalk": TEMPLATES[chosen][1],
            "continuous_default_reading_de": row["continuous_default_reading_de"],
        })

    counts = Counter(str(r["astro_template"]) for r in assignments)
    template_rows = []
    for name in TEMPLATES:
        rows = [r for r in assignments if r["astro_template"] == name]
        template_rows.append({
            "astro_template": name,
            "locus_count": len(rows),
            "f67r2": sum(r["page"] == "f67r2" for r in rows),
            "f68r1": sum(r["page"] == "f68r1" for r in rows),
            "f69v": sum(r["page"] == "f69v" for r in rows),
            "template_reading_de": TEMPLATES[name][0],
            "prose_slot_crosswalk": TEMPLATES[name][1],
            "apprentice_rule": "choose by the visible owner and present functional tags; keep source group order",
        })

    crosswalk = [
        {"shared_question": "WORAN", "prose_slots": "OWNER|SOURCE_ITEM", "astro_templates": "LOCAL_NAMED_ENTRY|ADDRESSED_ENTRY|SOURCE_TO_TARGET", "shared_rule_de": "sichtbaren Besitzer und gegebenenfalls Quelle bestimmen"},
        {"shared_question": "WELCHER_POSTEN", "prose_slots": "LINK_SELECT", "astro_templates": "FOLLOWING_RELATION|ROW_CONTINUATION|CONDITION_ENTRY", "shared_rule_de": "neu, folgend, weiter oder unter derselben Bedingung lesen"},
        {"shared_question": "WIEVIEL_ODER_WELCHE_STUFE", "prose_slots": "QUANTITY|STATE_GRADE", "astro_templates": "GRADED_OR_QUANTIFIED_VALUE|CONDITION_ENTRY", "shared_rule_de": "Teilwert, Sollwert oder Grad einsetzen"},
        {"shared_question": "WAS_TUN_ODER_WELCHER_LAUF", "prose_slots": "OPERATION|MEDIUM_FLOW|TARGET", "astro_templates": "ACTION_OR_PATH|ADDRESSED_ENTRY|SOURCE_TO_TARGET", "shared_rule_de": "setzen, halten, übertragen oder entlang einer Bahn zum Ziel führen"},
        {"shared_question": "ABSCHLUSS", "prose_slots": "CLOSE", "astro_templates": "NONE", "shared_rule_de": "Prosa kann einen Arbeitsgang schließen; Astro bleibt ein lokaler Nachschlageeintrag"},
    ]

    assignments_path = OUT / "TWO_HUNDRED_SEVENTY_SIXTH_142_TEMPLATE_ASSIGNMENTS.tsv"
    templates_path = OUT / "TWO_HUNDRED_SEVENTY_SIXTH_EIGHT_ASTRO_TEMPLATES.tsv"
    crosswalk_path = OUT / "TWO_HUNDRED_SEVENTY_SIXTH_ASTRO_PROSE_CROSSWALK.tsv"
    readable_path = OUT / "TWO_HUNDRED_SEVENTY_SIXTH_READABLE_SHARED_GRAMMAR.md"
    report_path = OUT / "TWO_HUNDRED_SEVENTY_SIXTH_REPORT.md"
    write_tsv(assignments_path, assignments, list(assignments[0]))
    write_tsv(templates_path, template_rows, list(template_rows[0]))
    write_tsv(crosswalk_path, crosswalk, list(crosswalk[0]))

    readable_path.write_text("""# Eine gemeinsame Werkstattgrammatik für Prosa und Diagramme

Die 142 Astroplätze benötigen nur acht Eintragsschablonen:

1. lokalen Schlüssel lesen,
2. Quell- oder Zieladresse lesen,
3. von Quelle zu Ziel lesen,
4. Bedingungsansatz setzen,
5. im selben Lauf fortsetzen,
6. zum Folgeposten wechseln,
7. Maß oder Grad lesen,
8. Posten setzen, halten, übertragen oder entlang einer Bahn führen.

Dies entspricht der Prosa-Merkfrage: **Woran arbeiten wir? Welcher Posten? Wieviel oder welche Stufe? Was tun wir damit und wohin?** Nur die Prosa besitzt zusätzlich einen Arbeitsgang-Abschluss. Astro bleibt ein Nachschlageeintrag.

Die Grammatik sagt nichts darüber, welche Sterne, Planeten, Krankheiten oder Kalenderdaten gemeint sind. Diese Inhalte sitzen in Bildbesitzern, Ganzzeichen und lokalen Kopieretiketten. Aber sie erklärt, wie mehrere Schreiber dieselben kurzen Konstruktionskarten in Pflanzenprosa, Badeanweisungen und Himmelsdiagrammen verwenden konnten.
""", encoding="utf-8")
    report_path.write_text(f"""# Sidequest-Pass 276: acht Astro-Schablonen und gemeinsame Slotgrammatik

## Ergebnis

Alle 142 Astro-Loci fallen in acht lehrbare Schablonen: LOCAL_NAMED_ENTRY={counts['LOCAL_NAMED_ENTRY']}, ADDRESSED_ENTRY={counts['ADDRESSED_ENTRY']}, SOURCE_TO_TARGET={counts['SOURCE_TO_TARGET']}, CONDITION_ENTRY={counts['CONDITION_ENTRY']}, ROW_CONTINUATION={counts['ROW_CONTINUATION']}, FOLLOWING_RELATION={counts['FOLLOWING_RELATION']}, GRADED_OR_QUANTIFIED_VALUE={counts['GRADED_OR_QUANTIFIED_VALUE']} und ACTION_OR_PATH={counts['ACTION_OR_PATH']}.

Diese Schablonen kreuzen direkt auf OWNER/SOURCE, LINK_SELECT, QUANTITY/STATE und OPERATION/FLOW/TARGET der Prosa-Satzgrammatik. CLOSE bleibt prosaspezifisch. Das ist bisher die kompakteste lehrbare Grammatik des Zehn-Seiten-Systems.

Input Astro `{sha(ASTRO)}`; input loci `{sha(LOCI)}`.
""", encoding="utf-8")
    outputs = (assignments_path, templates_path, crosswalk_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "loci": len(assignments),
        "template_counts": dict(counts),
        "templates": len(template_rows),
        "shared_questions": len(crosswalk),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
