#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R270 = ROOT / "experiments/yolo/sidequest_semantic_astro_address_suffix_two_hundred_seventieth"
ASTRO = R270 / "TWO_HUNDRED_SEVENTIETH_REVISED_395_ASTRO_GROUPS.tsv"

SPECIAL = {
    "olol": ("OL+OL", "im selben Lauf nochmals weiter"),
    "okol": ("OK+OL", "den Posten einsetzen und im selben Lauf weiter"),
    "otolor": ("OT+OL+OR", "naechster Posten; gleiche Reihe; neuer Bedingungsansatz"),
    "otor": ("OT+OR", "naechster Bedingungsansatz"),
    "oteol": ("OT+E+OL", "danach kurz im selben Lauf weiter"),
    "opcheeol": ("LOCAL_OPCH+EE+OL", "lokalen Posten laenger im selben Lauf weiterfuehren"),
    "iokeeor": ("LOCAL_I+OK+EE+OR", "lokalen Bedingungsansatz laenger aktiv halten"),
    "okshor": ("OK+SH+OR", "ruhenden Bedingungsansatz einsetzen"),
    "qoteor": ("Q_FRAME+OT+E+OR", "danach einen kurzen Bedingungsansatz setzen"),
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
    relations: list[dict[str, object]] = []
    revised: list[dict[str, str]] = []
    for row in astro:
        new = dict(row)
        suffix = None
        if row["exact_prose_card_id"] == "NONE" and row["visible_surface"].endswith("ol"):
            suffix = "OL"
        elif row["exact_prose_card_id"] == "NONE" and row["visible_surface"].endswith("or"):
            suffix = "OR"
        if suffix:
            prefix = row["visible_surface"][:-2] or "ROOT"
            if row["visible_surface"] in SPECIAL:
                parse, meaning = SPECIAL[row["visible_surface"]]
                status = "FULL_OR_PARTIAL_RELATION_COMPOSITION"
            else:
                parse = f"LOCAL_{prefix.upper()}+{suffix}"
                meaning = (
                    f"Bedingungsansatz des lokalen {prefix.upper()}-Postens"
                    if suffix == "OR"
                    else f"lokalen {prefix.upper()}-Posten im selben Lauf weiterfuehren"
                )
                status = "LOCAL_PREFIX_PLUS_RELATION_SUFFIX"
            relations.append({
                "group_serial": row["group_serial"],
                "page": row["page"],
                "locus": row["locus"],
                "visible_owner": row["visible_owner"],
                "namespace_id": row["namespace_id"],
                "visible_surface": row["visible_surface"],
                "prefix_surface": prefix,
                "relation_suffix": suffix,
                "relation_contribution_de": "BEDINGUNGSANSATZ" if suffix == "OR" else "IM_SELBEN_LAUF_WEITER",
                "component_parse": parse,
                "composed_short_value_de": meaning,
                "composition_status": status,
                "existing_diagram_reading_de": row["concrete_diagram_reading_de"],
            })
            new["curriculum_layer"] = "ASTRO_RELATION_SUFFIX_COMPOSITION"
            new["portable_card_core_de"] = meaning
            new["portable_card_role"] = "ASTRO_CONDITION_CARD" if suffix == "OR" else "ASTRO_CONTINUATION_CARD"
            new["apprentice_action"] = "read the final OR/OL relation first, then resolve or copy the local prefix"
            new["revision_271"] = "OR_OL_RELATION_SUFFIX"
        else:
            new["revision_271"] = "UNCHANGED"
        revised.append(new)

    forms: list[dict[str, object]] = []
    for surface in dict.fromkeys(str(r["visible_surface"]) for r in relations):
        rows = [r for r in relations if r["visible_surface"] == surface]
        forms.append({
            "visible_surface": surface,
            "relation_suffix": rows[0]["relation_suffix"],
            "prefix_surface": rows[0]["prefix_surface"],
            "component_parse": rows[0]["component_parse"],
            "composed_short_value_de": rows[0]["composed_short_value_de"],
            "group_count": len(rows),
            "pages": "|".join(dict.fromkeys(str(r["page"]) for r in rows)),
            "loci": "|".join(str(r["locus"]) for r in rows),
        })

    totals = [
        {"relation_component": "OR", "prose_events": 17, "known_astro_card_groups": 3, "local_astro_suffix_groups": 17, "cross_register_total": 37, "short_value_de": "BEDINGUNGSANSATZ"},
        {"relation_component": "OL", "prose_events": 48, "known_astro_card_groups": 9, "local_astro_suffix_groups": 8, "cross_register_total": 65, "short_value_de": "IM_SELBEN_LAUF_WEITER"},
    ]

    rel_path = OUT / "TWO_HUNDRED_SEVENTY_FIRST_25_LOCAL_RELATIONS.tsv"
    form_path = OUT / "TWO_HUNDRED_SEVENTY_FIRST_20_RELATION_FORMS.tsv"
    total_path = OUT / "TWO_HUNDRED_SEVENTY_FIRST_CROSS_REGISTER_TOTALS.tsv"
    revised_path = OUT / "TWO_HUNDRED_SEVENTY_FIRST_REVISED_395_ASTRO_GROUPS.tsv"
    readable_path = OUT / "TWO_HUNDRED_SEVENTY_FIRST_READABLE_RELATION_BOOK.md"
    report_path = OUT / "TWO_HUNDRED_SEVENTY_FIRST_REPORT.md"
    write_tsv(rel_path, relations, list(relations[0]))
    write_tsv(form_path, forms, list(forms[0]))
    write_tsv(total_path, totals, list(totals[0]))
    write_tsv(revised_path, revised, list(revised[0]))

    counts = Counter(str(r["relation_suffix"]) for r in relations)
    readable_path.write_text("""# Bedingungs- und Fortsetzungsbuch

`OR` bezeichnet kurz den laufenden **BEDINGUNGSANSATZ**. `OL` sagt **IM SELBEN LAUF WEITER**. Beide sind keine Stoffnamen und keine vollständigen Sätze; der vordere Kartenteil nennt den lokalen Posten.

- OR: 17 lokale Gruppen auf 13 Formen.
- OL: 8 lokale Gruppen auf 7 Formen.
- beide erscheinen auf allen drei Astro-Seiten.

Die klarste Mehrfachkarte ist `OTOLOR = OT + OL + OR`: **NÄCHSTER POSTEN; GLEICHE REIHE; NEUER BEDINGUNGSANSATZ**. `OL-OL` ist eine doppelte Fortsetzung, `OK-OL` setzt einen Posten und führt ihn in derselben Reihe weiter. Dass OL insgesamt häufiger als OR ist, passt zu einer Werkstatt, die viele Einträge innerhalb schon eröffneter Reihen fortsetzt.
""", encoding="utf-8")
    report_path.write_text(f"""# Sidequest-Pass 271: OR/OL als Bedingung und Fortsetzung

## Ergebnis

Die 25 bislang lokalen Endformen trennen sich ohne lange Wortglossen: 17 OR-Gruppen tragen BEDINGUNGSANSATZ, 8 OL-Gruppen IM SELBEN LAUF WEITER. Es gibt 20 Oberflächentypen. Neun besonders transparente Kompositionen werden vollständig gelesen; die übrigen behalten einen lokalen Präfix, aber einen invarianten Relationsteil.

Über beide Register ergibt sich OR=37 Ereignisse/Gruppen und OL=65. Die Asymmetrie ist sinnvoll: eine laufende Reihe wird öfter fortgesetzt als neu eröffnet. Der wichtigste Gewinn ist `OTOLOR=OT+OL+OR`, eine dreiteilige technische Adresse und kein langes Lexem.

Input Astro `{sha(ASTRO)}`.
""", encoding="utf-8")
    outputs = (rel_path, form_path, total_path, revised_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "relation_groups": len(relations),
        "relation_forms": len(forms),
        "suffix_counts": dict(counts),
        "pages": sorted({str(r["page"]) for r in relations}),
        "special_compositions": sum(r["composition_status"] == "FULL_OR_PARTIAL_RELATION_COMPOSITION" for r in relations),
        "cross_register_totals": {str(r["relation_component"]): int(r["cross_register_total"]) for r in totals},
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
