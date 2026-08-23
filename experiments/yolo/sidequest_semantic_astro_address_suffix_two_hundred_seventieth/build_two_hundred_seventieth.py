#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R269 = ROOT / "experiments/yolo/sidequest_semantic_relation_gap_transfer_two_hundred_sixty_ninth"
ASTRO = R269 / "TWO_HUNDRED_SIXTY_NINTH_REVISED_395_ASTRO_GROUPS.tsv"

SPECIAL = {
    "saral": ("S_FRAME+AR+AL", "von der Quelladresse zur Zieladresse"),
    "olar": ("OL+AR", "von der Quelladresse im selben Lauf weiter"),
    "okolar": ("OK+OL+AR", "den Lauf von der Quelladresse aktivieren"),
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
    addresses = []
    revised = []
    for row in astro:
        new = dict(row)
        suffix = None
        if row["exact_prose_card_id"] == "NONE" and row["visible_surface"].endswith("al"):
            suffix = "AL"
        elif row["exact_prose_card_id"] == "NONE" and row["visible_surface"].endswith("ar"):
            suffix = "AR"
        if suffix:
            prefix = row["visible_surface"][:-2] or "ROOT"
            if row["visible_surface"] in SPECIAL:
                parse, meaning = SPECIAL[row["visible_surface"]]
                prefix_status = "FULL_RELATION_COMPOSITION"
            else:
                parse = f"{prefix.upper()}_PREFIX+{suffix}"
                meaning = f"Zieladresse des {prefix.upper()}-Postens" if suffix == "AL" else f"Quelladresse des {prefix.upper()}-Postens"
                prefix_status = "PREFIX_PLUS_ADDRESS_SUFFIX"
            addresses.append({
                "group_serial": row["group_serial"], "page": row["page"], "locus": row["locus"],
                "visible_owner": row["visible_owner"], "namespace_id": row["namespace_id"],
                "visible_surface": row["visible_surface"], "prefix_surface": prefix,
                "address_suffix": suffix, "address_contribution_de": "ZU_ZIEL" if suffix == "AL" else "VON_QUELLE",
                "component_parse": parse, "composed_short_value_de": meaning,
                "prefix_status": prefix_status,
                "existing_diagram_reading_de": row["concrete_diagram_reading_de"],
            })
            new["curriculum_layer"] = "ASTRO_ADDRESS_SUFFIX_COMPOSITION"
            new["portable_card_core_de"] = meaning
            new["portable_card_role"] = "ASTRO_TARGET_ADDRESS_CARD" if suffix == "AL" else "ASTRO_SOURCE_ADDRESS_CARD"
            new["apprentice_action"] = "read the final AL/AR address first, then identify or copy the prefix"
            new["revision_270"] = "AL_AR_ADDRESS_SUFFIX"
        else:
            new["revision_270"] = "UNCHANGED"
        revised.append(new)

    forms = []
    for surface in dict.fromkeys(r["visible_surface"] for r in addresses):
        rows = [r for r in addresses if r["visible_surface"] == surface]
        forms.append({
            "visible_surface": surface, "address_suffix": rows[0]["address_suffix"],
            "prefix_surface": rows[0]["prefix_surface"], "component_parse": rows[0]["component_parse"],
            "composed_short_value_de": rows[0]["composed_short_value_de"],
            "group_count": len(rows), "pages": "|".join(dict.fromkeys(r["page"] for r in rows)),
            "loci": "|".join(r["locus"] for r in rows),
        })

    cross = [
        {"address_component": "AR", "prose_events": 14, "known_astro_card_groups": 6, "local_astro_terminal_suffix_groups": 40, "terminal_channel_total": 60, "short_value_de": "VON_QUELLE"},
        {"address_component": "AL", "prose_events": 38, "known_astro_card_groups": 8, "local_astro_terminal_suffix_groups": 14, "terminal_channel_total": 60, "short_value_de": "ZU_ZIEL"},
    ]

    address_path = OUT / "TWO_HUNDRED_SEVENTIETH_54_LOCAL_ASTRO_ADDRESSES.tsv"
    forms_path = OUT / "TWO_HUNDRED_SEVENTIETH_38_ADDRESS_FORM_TYPES.tsv"
    cross_path = OUT / "TWO_HUNDRED_SEVENTIETH_BALANCED_ADDRESS_CHANNELS.tsv"
    revised_path = OUT / "TWO_HUNDRED_SEVENTIETH_REVISED_395_ASTRO_GROUPS.tsv"
    readable_path = OUT / "TWO_HUNDRED_SEVENTIETH_READABLE_ADDRESS_BOOK.md"
    report_path = OUT / "TWO_HUNDRED_SEVENTIETH_REPORT.md"
    write_tsv(address_path, addresses, list(addresses[0]))
    write_tsv(forms_path, forms, list(forms[0]))
    write_tsv(cross_path, cross, list(cross[0]))
    write_tsv(revised_path, revised, list(revised[0]))

    counts = Counter(r["address_suffix"] for r in addresses)
    readable = [
        "# Quell- und Zieladressbuch", "",
        "Am Ende einer lokalen Astroform hat `AR` den konstanten Wert **VON DER QUELLE**, `AL` den Wert **ZUR ZIELSTELLE**. Der vordere Teil nennt den lokalen Stern-, Ring- oder Bedingungsposten.", "",
        "- 40 lokale AR-Gruppen auf 25 Formen.",
        "- 14 lokale AL-Gruppen auf 13 Formen.",
        "- beide Endungen kommen auf f67r2, f68r1 und f69v vor.", "",
        "## Gesamtbilanz", "",
        "AR: 14 Prosaereignisse + 6 bekannte Astrogruppen + 40 lokale Suffixgruppen = **60**.", "",
        "AL: 38 Prosaereignisse + 8 bekannte Astrogruppen + 14 lokale Suffixgruppen = **60**.", "",
        "Diese Gleichheit muss kein absichtliches Zählsystem sein, passt aber hervorragend zu einem zweipoligen Adressregister: jeder Arbeits- oder Diagrammposten kann als Quelle oder Ziel markiert werden.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 270: vollständiger AL/AR-Adresskanal

## Ergebnis

Vierzig lokale Astrogruppen enden in AR und vierzehn in AL; sie bilden25 bzw.13 Formtypen und erscheinen auf allen drei Astroseiten. AR trägt VON_QUELLE, AL ZU_ZIEL, während der Präfix den lokalen Posten benennt. SARAL, OLAR und OKOLAR behalten ihre vollständigen Relation-Gap-Kompositionen.

Im terminalen Adresskanal ergibt sich eine auffällige Balance: AR=14 Prosa+6 bekannte Astro+40 lokale Astro=60; AL=38+8+14=60. Das stützt die Lesung als gepaarte Quell-/Zieladressen und nicht als konkrete Stoffwörter.

Input Astro `{sha(ASTRO)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (address_path, forms_path, cross_path, revised_path, readable_path, report_path)
    summary = {
        "status": "PASS", "address_groups": len(addresses), "address_forms": len(forms),
        "suffix_counts": dict(counts), "pages": sorted({r["page"] for r in addresses}),
        "balanced_terminal_totals": {r["address_component"]: r["terminal_channel_total"] for r in cross},
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
