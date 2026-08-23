#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R248 = ROOT / "experiments/yolo/sidequest_semantic_astro_native_card_values_two_hundred_forty_eighth"
ASTRO = R248 / "TWO_HUNDRED_FORTY_EIGHTH_REVISED_395_GROUP_MANUAL.tsv"

PARSE = {
    "alaiin": ("AL+AIIN", "Ziel-Sollwert", "FULL_40_COMPONENT_PARSE"),
    "ytoaiin": ("Y+LOCAL_TO+AIIN", "Sollwert des lokalen YTO-Postens", "LOCAL_CORE_PLUS_AIIN"),
    "chedaiin": ("CHED+AIIN", "Übertragungs-Sollwert", "FULL_40_COMPONENT_PARSE"),
    "todaiin": ("LOCAL_TO+D+AIIN", "Sollwert des lokalen TOD-Postens", "LOCAL_CORE_PLUS_AIIN"),
    "dadaiin": ("LOCAL_DA+D+AIIN", "Sollwert des lokalen DAD-Postens", "LOCAL_CORE_PLUS_AIIN"),
    "aldaiin": ("AL+D_PREVIOUS+AIIN", "voriger Ziel-Sollwert", "FULL_40_COMPONENT_PARSE"),
    "ydaiin": ("Y+D_PREVIOUS+AIIN", "Sollwert dieses vorigen Postens", "FULL_40_COMPONENT_PARSE"),
    "ykoaiin": ("Y+K_BINDER+O_WITHDRAW+AIIN", "gebundener Sollwert dieses Postens", "FULL_40_COMPONENT_PARSE"),
    "oaiin": ("O_WITHDRAW+AIIN", "Rücknahmewert", "FULL_40_COMPONENT_PARSE"),
    "qokoaiin": ("OK+O_WITHDRAW+AIIN", "Rücknahmewert setzen", "FULL_40_COMPONENT_PARSE"),
    "osdaiin": ("OS_RECEIVER+D_PREVIOUS+AIIN", "voriger Aufnahmewert", "FULL_40_COMPONENT_PARSE"),
    "choaiin": ("CHO_INPUT+AIIN", "Eingabe-Sollwert", "FULL_40_COMPONENT_PARSE"),
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
            parse, meaning, status = PARSE[row["visible_surface"]]
            family.append({
                "group_serial": row["group_serial"], "page": row["page"], "locus": row["locus"],
                "visible_owner": row["visible_owner"], "namespace_id": row["namespace_id"],
                "visible_surface": row["visible_surface"], "component_parse": parse,
                "composed_short_value_de": meaning, "composition_status": status,
                "aiin_contribution_de": "SOLLWERT_ODER_GRAD",
                "existing_diagram_reading_de": row["concrete_diagram_reading_de"],
            })
            new["curriculum_layer"] = "ASTRO_COMPOSED_FROM_40_COMPONENTS" if status == "FULL_40_COMPONENT_PARSE" else "ASTRO_LOCAL_CORE_PLUS_AIIN"
            new["portable_card_core_de"] = meaning
            new["portable_card_role"] = "COMPOSED_ASTRO_VALUE_CARD" if status == "FULL_40_COMPONENT_PARSE" else "PARTIAL_ASTRO_VALUE_CARD"
            new["apprentice_action"] = "compose the short value; copy only the local residual core if present"
            new["revision_266"] = "AIIN_COMPOSITION"
        else:
            new["revision_266"] = "UNCHANGED"
        revised.append(new)

    family_path = OUT / "TWO_HUNDRED_SIXTY_SIXTH_13_ASTRO_AIIN_GROUPS.tsv"
    revised_path = OUT / "TWO_HUNDRED_SIXTY_SIXTH_REVISED_395_ASTRO_GROUPS.tsv"
    forms_path = OUT / "TWO_HUNDRED_SIXTY_SIXTH_12_AIIN_FORM_TYPES.tsv"
    readable_path = OUT / "TWO_HUNDRED_SIXTY_SIXTH_READABLE_AIIN_ATLAS.md"
    report_path = OUT / "TWO_HUNDRED_SIXTY_SIXTH_REPORT.md"
    write_tsv(family_path, family, list(family[0]))
    write_tsv(revised_path, revised, list(revised[0]))
    forms = []
    for surface, (parse, meaning, status) in PARSE.items():
        rows = [r for r in family if r["visible_surface"] == surface]
        forms.append({
            "visible_surface": surface, "component_parse": parse, "composed_short_value_de": meaning,
            "composition_status": status, "group_count": len(rows),
            "pages": "|".join(dict.fromkeys(r["page"] for r in rows)),
            "loci": "|".join(r["locus"] for r in rows),
        })
    write_tsv(forms_path, forms, list(forms[0]))

    readable = [
        "# AIIN als Astro-Sollwert", "",
        "Zwölf verschiedene lokale Formen tragen AIIN; zusammen stehen sie dreizehnmal auf f67r2, f68r1 und f69v.", "",
    ]
    for row in forms:
        readable.append(f"- `{row['visible_surface']}` = `{row['component_parse']}` → **{row['composed_short_value_de']}** ({row['composition_status']}).")
    readable += [
        "", "Neun Formtypen mit zehn Gruppen sind vollständig aus dem40er-Deck gebaut. Drei Formtypen behalten einen lokalen YTO/TOD/DAD-Namenskern, aber der AIIN-Beitrag bleibt auch dort Sollwert oder Grad.", "",
        "Die Familie verbindet alle drei Astroseiten: f67 liefert Ziel-, Transfer-, Ring- und Rücknahmewerte; f68 einen Aufnahmewert; f69 einen Eingabewert. Das ist die bisher klarste registerübergreifende Kompositionsfamilie.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 266: Astro-AIIN-Komposition

## Ergebnis

Dreizehn zuvor lokale Astrogruppen auf zwölf Formen enden in AIIN. Zehn Gruppen/neun Formen werden vollständig vom40-Komponenten-Deck erzeugt; drei behalten je einen lokalen Namenskern, während AIIN=SOLLWERT/GRAD invariant bleibt. Die Familie erscheint auf f67r2, f68r1 und f69v.

ALAIIN und CHEDAIIN bestätigen die prospektiven Vorhersagen aus Pass265. Weitere vollständige Formen sind ALDAIIN, YDAIIN, YKOAIIN, OAIIN, QOKOAIIN, OSDAIIN und CHOAIIN. Die überarbeitete395-Gruppen-Tabelle trennt vollständige Komposition von lokalem Kern plus AIIN.

Input Astro `{sha(ASTRO)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (family_path, forms_path, revised_path, readable_path, report_path)
    summary = {
        "status": "PASS", "aiin_groups": len(family), "aiin_form_types": len(forms),
        "full_groups": sum(r["composition_status"] == "FULL_40_COMPONENT_PARSE" for r in family),
        "partial_groups": sum(r["composition_status"] == "LOCAL_CORE_PLUS_AIIN" for r in family),
        "pages": sorted({r["page"] for r in family}), "revised_astro_groups": len(revised),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
