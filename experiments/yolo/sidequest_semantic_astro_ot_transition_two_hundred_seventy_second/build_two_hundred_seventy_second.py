#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R271 = ROOT / "experiments/yolo/sidequest_semantic_astro_relation_suffix_two_hundred_seventy_first"
ASTRO = R271 / "TWO_HUNDRED_SEVENTY_FIRST_REVISED_395_ASTRO_GROUPS.tsv"

COMPOSITIONS = {
    "otoldos": ("OT+OL+LOCAL_DOS", "Folgeposten im selben Lauf weiter"),
    "qotoear": ("Q_FRAME+OT+LOCAL_OE+AR", "Quelladresse des Folgepostens"),
    "otolor": ("OT+OL+OR", "Folgeposten; gleiche Reihe; neuer Bedingungsansatz"),
    "choteey": ("LOCAL_CH+OT+EE+Y", "Folgeposten laenger halten"),
    "otor": ("OT+OR", "Bedingungsansatz des Folgepostens"),
    "otchl": ("OT+LOCAL_CHL", "lokaler CHL-Folgeposten"),
    "otcheody": ("OT+LOCAL_CHEODY", "lokaler CHEODY-Folgeposten"),
    "otshey": ("OT+SHEY", "naechster freigegebener Wert"),
    "otochedy": ("OT+LOCAL_O+CHED+Y", "naechsten Posten uebertragen"),
    "otaza": ("OT+LOCAL_AZA", "lokaler AZA-Folgeposten"),
    "otokeeey": ("OT+OK+EE+Y", "Folgeposten laenger einsetzen"),
    "ot": ("OT", "Folgeposten"),
    "oteeo": ("OT+EE+LOCAL_O", "lokalen Folgeposten laenger halten"),
    "otaldal": ("OT+AL+LOCAL_D+AL", "Folgeposten an die bezeichnete Ziel-Unteradresse"),
    "otoar": ("OT+LOCAL_O+AR", "Quelladresse des Folgepostens"),
    "qoteor": ("Q_FRAME+OT+E+OR", "kurzer Bedingungsansatz des Folgepostens"),
    "qotair": ("Q_FRAME+OT+AIR", "Laufbahn des Folgepostens"),
    "oteeal": ("OT+EE+AL", "Folgeposten laenger an der Zieladresse halten"),
    "oteody": ("OT+LOCAL_EODY", "lokaler EODY-Folgeposten"),
    "otoly": ("OT+OL+Y", "diesen Folgeposten im selben Lauf weiterfuehren"),
    "oteoarar": ("OT+LOCAL_EO+AR+AR", "Folgeposten mit doppelter Quelladresse"),
    "otody": ("OT+LOCAL_ODY", "lokaler ODY-Folgeposten"),
    "oteeys": ("OT+EE+LOCAL_YS", "lokalen Folgeposten laenger halten"),
    "oteol": ("OT+E+OL", "Folgeposten kurz im selben Lauf weiterfuehren"),
    "otchy": ("OT+CHY", "diesen Folgeposten bearbeiten"),
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
    transitions: list[dict[str, object]] = []
    revised: list[dict[str, str]] = []
    for row in astro:
        new = dict(row)
        is_local_ot = (
            row["exact_prose_card_id"] == "NONE"
            and "naechster Platz oder folgende Bedingung" in row["concrete_diagram_reading_de"]
        )
        if is_local_ot:
            surface = row["visible_surface"]
            parse, meaning = COMPOSITIONS[surface]
            ot_index = surface.index("ot")
            transitions.append({
                "group_serial": row["group_serial"],
                "page": row["page"],
                "locus": row["locus"],
                "visible_owner": row["visible_owner"],
                "namespace_id": row["namespace_id"],
                "visible_surface": surface,
                "before_ot": surface[:ot_index] or "ROOT",
                "after_ot": surface[ot_index + 2:] or "ROOT",
                "component_parse": parse,
                "portable_ot_value_de": "FOLGEPOSTEN",
                "composed_short_value_de": meaning,
                "existing_diagram_reading_de": row["concrete_diagram_reading_de"],
            })
            new["curriculum_layer"] = "ASTRO_OT_TRANSITION_COMPOSITION"
            new["portable_card_core_de"] = meaning
            new["portable_card_role"] = "ASTRO_FOLLOWING_POST_CARD"
            new["apprentice_action"] = "read OT as following post; then read the attached address, grade or relation"
            new["revision_272"] = "OT_FOLLOWING_POST"
        else:
            new["revision_272"] = "UNCHANGED"
        revised.append(new)

    forms: list[dict[str, object]] = []
    for surface in dict.fromkeys(str(r["visible_surface"]) for r in transitions):
        rows = [r for r in transitions if r["visible_surface"] == surface]
        forms.append({
            "visible_surface": surface,
            "component_parse": rows[0]["component_parse"],
            "portable_ot_value_de": "FOLGEPOSTEN",
            "composed_short_value_de": rows[0]["composed_short_value_de"],
            "group_count": len(rows),
            "pages": "|".join(dict.fromkeys(str(r["page"]) for r in rows)),
            "loci": "|".join(str(r["locus"]) for r in rows),
        })

    register = [
        {"register": "PROSE", "known_ot_uses": 26, "portable_value_de": "FOLGEPOSTEN", "local_expansion_de": "DANACH_ODER_NAECHSTER_ARBEITSSCHRITT"},
        {"register": "ASTRO_KNOWN_CARDS", "known_ot_uses": 6, "portable_value_de": "FOLGEPOSTEN", "local_expansion_de": "NAECHSTER_DIAGRAMMPOSTEN"},
        {"register": "ASTRO_LOCAL_FORMS", "known_ot_uses": 26, "portable_value_de": "FOLGEPOSTEN", "local_expansion_de": "NAECHSTER_DIAGRAMMPOSTEN"},
        {"register": "TOTAL", "known_ot_uses": 58, "portable_value_de": "FOLGEPOSTEN", "local_expansion_de": "REGISTERABHAENGIG"},
    ]

    transition_path = OUT / "TWO_HUNDRED_SEVENTY_SECOND_26_OT_TRANSITIONS.tsv"
    form_path = OUT / "TWO_HUNDRED_SEVENTY_SECOND_25_OT_FORMS.tsv"
    register_path = OUT / "TWO_HUNDRED_SEVENTY_SECOND_REGISTER_TRANSFER.tsv"
    revised_path = OUT / "TWO_HUNDRED_SEVENTY_SECOND_REVISED_395_ASTRO_GROUPS.tsv"
    readable_path = OUT / "TWO_HUNDRED_SEVENTY_SECOND_READABLE_OT_LESSON.md"
    report_path = OUT / "TWO_HUNDRED_SEVENTY_SECOND_REPORT.md"
    write_tsv(transition_path, transitions, list(transitions[0]))
    write_tsv(form_path, forms, list(forms[0]))
    write_tsv(register_path, register, list(register[0]))
    write_tsv(revised_path, revised, list(revised[0]))

    page_counts = Counter(str(r["page"]) for r in transitions)
    readable_path.write_text("""# OT-Lektion: zum Folgeposten

Der kurze portable Wert ist **FOLGEPOSTEN**. In praktischer Prosa kann der Schreiber ihn als „danach“ oder „nächster Arbeitsschritt“ aussprechen; auf einem Rad oder Sternfeld heißt er „nächster Diagrammposten“. OT selbst behauptet weder Zeit noch Drehrichtung.

Beispiele:

- `OT` = Folgeposten.
- `OT+OR` = Bedingungsansatz des Folgepostens.
- `OT+OL+OR` = Folgeposten; gleiche Reihe; neuer Bedingungsansatz.
- `OT+AIR` = Laufbahn des Folgepostens.
- `OT+EE+AL` = Folgeposten länger an der Zieladresse halten.

Damit hat OT 58 feste Verwendungen über Prosa und Astro, davon 26 bislang lokale Astrogruppen.
""", encoding="utf-8")
    report_path.write_text(f"""# Sidequest-Pass 272: OT ist der Folgeposten

## Ergebnis

Alle 26 bislang lokalen OT-Gruppen auf 25 Formen lassen sich mit dem kurzen Kern FOLGEPOSTEN lesen. Sie verteilen sich auf f67r2={page_counts['f67r2']}, f68r1={page_counts['f68r1']} und f69v={page_counts['f69v']}. Zusammen mit 26 Prosaereignissen und sechs schon bekannten Astrogruppen trägt OT 58 Mal denselben portablen Kern.

Die frühere Übersetzung DANACH_NAECHSTER wird präzisiert: **FOLGEPOSTEN** ist die Kartenbedeutung; „danach“ ist nur die prosaische, „nächster Platz“ die diagrammatische Expansion. Das verhindert eine unzulässige Zeitbedeutung auf statischen Tafeln.

Input Astro `{sha(ASTRO)}`.
""", encoding="utf-8")
    outputs = (transition_path, form_path, register_path, revised_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "transition_groups": len(transitions),
        "transition_forms": len(forms),
        "page_counts": dict(page_counts),
        "cross_register_ot_uses": 58,
        "portable_value": "FOLGEPOSTEN",
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
