#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ROOTS = ROOT / "experiments/yolo/sidequest_semantic_cross_register_core_normalization_nine_hundred_sixty_second/PASS962_56_PORTABLE_ROOT_CORES.tsv"
FORMULAS = ROOT / "experiments/yolo/sidequest_semantic_deduplicated_root_formula_codebook_nine_hundred_fifty_seventh/PASS957_66_TRUE_MULTICOMPONENT_FORMULAS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_canonical_122_entry_edition_nine_hundred_fifty_eighth/PASS958_2511_CANONICAL_EVENT_DICTIONARY.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    roots = read_tsv(ROOTS)
    formulas = read_tsv(FORMULAS)
    events = read_tsv(EVENTS)
    productive_counts = Counter(
        component
        for row in events if row["codebook_layer"] == "PRODUCTIVE_ABBREVIATION_COMPOSITION"
        for component in row["component_recipe"].split("+")
    )
    all_counts = Counter(component for row in events for component in row["component_recipe"].split("+"))
    pages_by_component: dict[str, set[str]] = {row["component"]: set() for row in roots}
    for event in events:
        for component in event["component_recipe"].split("+"):
            pages_by_component[component].add(event["physical_page"])

    entry_rows: list[dict[str, object]] = []
    for row in roots:
        component = row["component"]
        productive = productive_counts[component]
        if productive >= 10:
            tier = "A_COMMON_PRODUCTIVE_ROOT"
            teaching = "Grundtafel: frei zusammensetzen."
        elif productive:
            tier = "B_RARE_PRODUCTIVE_EXTENSION"
            teaching = "Erweiterungstafel: nur in belegten Fachverbindungen verwenden."
        else:
            tier = "D_LOCAL_DIAGRAM_SIGN"
            teaching = "Nur auf der lokalen Bild-/Diagrammtafel lernen; kein allgemeiner Wortstamm."
        entry_rows.append({
            "entry_id": f"R-{component}", "entry_tier": tier, "entry_type": "ROOT_OR_LOCAL_SIGN",
            "recognition_form": component, "portable_value_de": row["portable_core_de"],
            "productive_composition_uses": productive, "all_atom_uses": all_counts[component],
            "physical_pages": "|".join(sorted(pages_by_component[component])),
            "teaching_rule_de": teaching,
        })
    for row in formulas:
        entry_rows.append({
            "entry_id": row["formula_card_id"], "entry_tier": "C_LEARNED_FORMULA_CARD", "entry_type": "FORMULA_CARD",
            "recognition_form": row["component_recipe"], "portable_value_de": row["workshop_formula_de"],
            "productive_composition_uses": 0, "all_atom_uses": row["events_including_local"],
            "physical_pages": row["physical_pages"],
            "teaching_rule_de": "Als ganze Karte lernen; innere Stämme nur als Merkhilfe.",
        })
    write_tsv(OUT / "PASS964_TIERED_122_ENTRY_CODEBOOK.tsv", entry_rows)

    lesson_rows = [
        {"phase": 1, "tier": "A_COMMON_PRODUCTIVE_ROOT", "entries": 37, "purpose_de": "gemeinsame produktive Grundgrammatik", "instruction_de": "Erst diese 37 häufigen Stämme frei setzen und rücklesen."},
        {"phase": 2, "tier": "C_LEARNED_FORMULA_CARD", "entries": 66, "purpose_de": "schnelle feste Werkstattwendungen", "instruction_de": "Formelkarten als Bilder erkennen, nicht jedes Mal ausbuchstabieren."},
        {"phase": 3, "tier": "B_RARE_PRODUCTIVE_EXTENSION", "entries": 16, "purpose_de": "seltene Fachoperationen", "instruction_de": "Nur zusammen mit ihren belegten Nachbarkarten üben."},
        {"phase": 4, "tier": "D_LOCAL_DIAGRAM_SIGN", "entries": 3, "purpose_de": "lokale Diagrammadressen", "instruction_de": "Mit der betreffenden Ring- oder Sterntafel kopieren."},
    ]
    write_tsv(OUT / "PASS964_FOUR_PHASE_TRAINING.tsv", lesson_rows)

    tiers = Counter(row["entry_tier"] for row in entry_rows)
    local_only = [row["recognition_form"] for row in entry_rows if row["entry_tier"] == "D_LOCAL_DIAGRAM_SIGN"]
    report = f"""# Pass 964 — 119 gemeinsame Einträge plus drei lokale Diagrammzeichen

Das 122er-Inventar war noch falsch bezeichnet: Nicht alle 56 kurzen Zeichen
sind produktive Wortstämme. `LOCAL_CHAR_Z`, `S_LABEL` und `Z_ADDR` kommen nie
in der produktiven Prosaschicht vor; sie gehören ausschließlich zu Bild- und
Diagrammadressen.

Die bessere Lehrordnung lautet:

- **37 häufige produktive Stämme**,
- **66 gelernte Formelkarten**,
- **16 seltene produktive Erweiterungen**,
- **3 lokale Diagrammzeichen** ({', '.join(local_only)}).

Damit hat die gemeinsame Werkstatt **119 lehrbare Einträge**; die drei
Diagrammzeichen stehen auf der jeweiligen Zusatztafel. Das Gesamtinventar
bleibt 122, aber ein Pflanzen- oder Badeschreiber muss nicht so tun, als seien
RAHMEN, AUSSEN und das lokale ZWISCHEN-Zeichen gewöhnliche Wörter.

Die neue Staffelung ist {dict(tiers)}. Ein Anfänger lernt also zuerst nur 37
Stämme. Mit dem 66er-Deck beherrscht er danach den größten wiederkehrenden Teil;
die 19 Erweiterungen kommen erst mit den Fachseiten hinzu.
"""
    (OUT / "PASS964_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS964_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {"entries": len(entry_rows), "tiers": tiers, "general_entries": len(entry_rows) - 3, "local_diagram_signs": local_only, "outputs": outputs}
    (OUT / "PASS964_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
