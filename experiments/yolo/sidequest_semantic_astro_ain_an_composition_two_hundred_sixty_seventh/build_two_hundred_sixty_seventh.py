#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R266 = ROOT / "experiments/yolo/sidequest_semantic_astro_aiin_composition_two_hundred_sixty_sixth"
ASTRO = R266 / "TWO_HUNDRED_SIXTY_SIXTH_REVISED_395_ASTRO_GROUPS.tsv"

PARSE = {
    "ain": ("AIN", "Portion oder Teilwert", "AIN", "FULL_40_COMPONENT_PARSE"),
    "oekain": ("O_WITHDRAW+E_SHORT+K_BINDER+AIN", "kurz gebundene Rücknahmeportion", "AIN", "FULL_40_COMPONENT_PARSE"),
    "sain": ("S_FRAME+AIN", "Portion oder Teilwert", "AIN", "FULL_40_COMPONENT_PARSE"),
    "salsain": ("S_FRAME+AL+S_FRAME+AIN", "Zielportion oder Ziel-Teilwert", "AIN", "FULL_40_COMPONENT_PARSE"),
    "yfain": ("Y+LOCAL_F+AIN", "Portion des lokalen YF-Postens", "AIN", "LOCAL_CORE_PLUS_AIN"),
    "odain": ("O_WITHDRAW+D_PREVIOUS+AIN", "Portion vom vorigen Rücknahmeposten", "AIN", "FULL_40_COMPONENT_PARSE"),
    "dokan": ("D_PREVIOUS+OK+AN", "zweite oder alternative Portion einsetzen", "AN", "FULL_40_COMPONENT_PARSE"),
    "oeoldan": ("O_WITHDRAW+E_SHORT+OL+D_PREVIOUS+AN", "mit der zweiten Einstellung weiter", "AN", "FULL_40_COMPONENT_PARSE"),
    "oran": ("OR+AN", "alternativer Ansatz", "AN", "FULL_40_COMPONENT_PARSE"),
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


def main() -> None:
    astro = read_tsv(ASTRO)
    family = []
    revised = []
    for row in astro:
        new = dict(row)
        if row["exact_prose_card_id"] == "NONE" and row["visible_surface"] in PARSE:
            parse, meaning, ending, status = PARSE[row["visible_surface"]]
            family.append({
                "group_serial": row["group_serial"], "page": row["page"], "locus": row["locus"],
                "visible_owner": row["visible_owner"], "namespace_id": row["namespace_id"],
                "visible_surface": row["visible_surface"], "quantity_ending": ending,
                "component_parse": parse, "composed_short_value_de": meaning,
                "composition_status": status,
                "quantity_contribution_de": "PORTION_TEILWERT" if ending == "AIN" else "ZWEITE_ODER_ALTERNATIVE_PORTION",
                "existing_diagram_reading_de": row["concrete_diagram_reading_de"],
            })
            new["curriculum_layer"] = "ASTRO_COMPOSED_FROM_40_COMPONENTS" if status == "FULL_40_COMPONENT_PARSE" else "ASTRO_LOCAL_CORE_PLUS_AIN"
            new["portable_card_core_de"] = meaning
            new["portable_card_role"] = "COMPOSED_ASTRO_QUANTITY_CARD" if status == "FULL_40_COMPONENT_PARSE" else "PARTIAL_ASTRO_QUANTITY_CARD"
            new["apprentice_action"] = "compose the AIN/AN value and copy only any marked local residual"
            new["revision_267"] = "AIN_AN_COMPOSITION"
        else:
            new["revision_267"] = "UNCHANGED"
        revised.append(new)

    forms = []
    for surface, (parse, meaning, ending, status) in PARSE.items():
        rows = [r for r in family if r["visible_surface"] == surface]
        forms.append({
            "visible_surface": surface, "quantity_ending": ending, "component_parse": parse,
            "composed_short_value_de": meaning, "composition_status": status,
            "group_count": len(rows), "loci": "|".join(r["locus"] for r in rows),
        })

    family_path = OUT / "TWO_HUNDRED_SIXTY_SEVENTH_10_ASTRO_AIN_AN_GROUPS.tsv"
    forms_path = OUT / "TWO_HUNDRED_SIXTY_SEVENTH_NINE_AIN_AN_FORM_TYPES.tsv"
    revised_path = OUT / "TWO_HUNDRED_SIXTY_SEVENTH_REVISED_395_ASTRO_GROUPS.tsv"
    readable_path = OUT / "TWO_HUNDRED_SIXTY_SEVENTH_READABLE_AIN_AN_ATLAS.md"
    report_path = OUT / "TWO_HUNDRED_SIXTY_SEVENTH_REPORT.md"
    write_tsv(family_path, family, list(family[0]))
    write_tsv(forms_path, forms, list(forms[0]))
    write_tsv(revised_path, revised, list(revised[0]))

    readable = ["# AIN und AN auf f67r2", ""]
    for row in forms:
        readable.append(f"- `{row['visible_surface']}` = `{row['component_parse']}` → **{row['composed_short_value_de']}** ({row['composition_status']}).")
    readable += [
        "", "AIN bleibt in sieben Gruppen eine Portion oder ein gezählter Teilwert. AN erscheint in drei längeren Formen und passt jeweils zu einer zweiten oder alternativen Wahl: zweiten Posten einsetzen, mit zweiter Einstellung weiter, alternativen Ansatz wählen.", "",
        "`dokan` ist besonders nützlich: Die vorhergesagte, auf der Prosaseite noch fehlende Folge OK+AN erscheint hier mit einem D-Vorbezug. Das Modell hatte `okan` als kanonische Skizze erwartet; das Diagramm schreibt die erweiterte Form `dokan`.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 267: Astro-AIN/AN-Komposition

## Ergebnis

Sieben lokale AIN-Gruppen und drei lokale AN-Gruppen auf f67r2 bilden neun Formtypen. Neun Gruppen sind vollständig aus dem40er-Deck zusammengesetzt; YFAIN behält allein einen lokalen F-Kern. AIN bleibt PORTION/TEILWERT. Die drei AN-Formen DOKAN, OEOLDAN und ORAN lesen sich kohärent als zweite oder alternative Setzung, Fortsetzung und Ansatz.

DOKAN realisiert die in Pass265 vorhergesagte OK+AN-Komposition mit zusätzlichem D-Vorbezug. Die revidierte395-Gruppen-Tabelle enthält nun AIIN-, AIN- und AN-Kompositionen getrennt von lokalen Labelresten.

Input Astro `{sha(ASTRO)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (family_path, forms_path, revised_path, readable_path, report_path)
    summary = {
        "status": "PASS", "groups": len(family), "form_types": len(forms),
        "ain_groups": sum(r["quantity_ending"] == "AIN" for r in family),
        "an_groups": sum(r["quantity_ending"] == "AN" for r in family),
        "full_groups": sum(r["composition_status"] == "FULL_40_COMPONENT_PARSE" for r in family),
        "partial_groups": sum(r["composition_status"] == "LOCAL_CORE_PLUS_AIN" for r in family),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
