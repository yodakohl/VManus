#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P974 = ROOT / "experiments/yolo/sidequest_semantic_image_owned_fourteen_page_edition_nine_hundred_seventy_fourth"
P983 = ROOT / "experiments/yolo/sidequest_semantic_159_unit_address_aware_codebook_nine_hundred_eighty_third"


DISPLAY = {
    "R-Y": "POSTEN",
    "R-OR": "ARBEITSSATZ",
    "R-DY": "SCHLUSS",
    "R-CARRIER_Q": "START",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    lexicon = read(P983 / "PASS983_159_TEACHING_UNIT_CODEBOOK.tsv")
    events = read(P983 / "PASS983_2511_EVENT_ADDRESS_AWARE_BINDING.tsv")
    expansions = {r["entry_id"]: r for r in read(P974 / "PASS974_86_ENTRY_REGISTER_EXPANSIONS.tsv")}
    roots = [r for r in lexicon if r["unit_type"] == "ROOT_OR_LOCAL_SIGN"]
    local_ids = {"R-S_LABEL", "R-Z_ADDR", "R-LOCAL_CHAR_Z"}
    portable = [r for r in roots if r["teaching_unit_id"] not in local_ids]
    local = [r for r in roots if r["teaching_unit_id"] in local_ids]

    rows = []
    for root in portable:
        unit_id = root["teaching_unit_id"]
        form = root["recognition_forms"]
        hits = [r for r in events if form in r["component_recipe"].split("+")]
        content = [r for r in hits if r["primary_layer"] not in {"LOCAL_ADDRESS_OR_KENNING", "DRUG_LABEL_NOMENCLATOR"}]
        label = [r for r in hits if r["primary_layer"] == "LOCAL_ADDRESS_OR_KENNING"]
        surfaces = Counter(r["surface"] for r in content)
        expansion = expansions[unit_id]
        rows.append({
            "root_id": unit_id,
            "recognition_form": form,
            "atomic_meaning_de": DISPLAY.get(unit_id, root["spoken_value_de"]),
            "material_workshop_expansion_de": expansion["material_workshop_expansion_de"],
            "station_workshop_expansion_de": expansion["station_workshop_expansion_de"],
            "celestial_relational_expansion_de": expansion["celestial_lookup_expansion_de"],
            "content_events": str(len(content)),
            "content_pages": "|".join(sorted({r["physical_page"] for r in content})),
            "label_mnemonic_events": str(len(label)),
            "common_surface_examples": "|".join(surface for surface, _ in surfaces.most_common(6)),
        })
    write(HERE / "PASS984_53_PORTABLE_ROOT_DICTIONARY.tsv", rows, list(rows[0]))

    local_rows = []
    for root in local:
        local_rows.append({
            "sign_id": root["teaching_unit_id"],
            "recognition_form": root["recognition_forms"],
            "local_value_de": root["spoken_value_de"],
            "teaching_rule_de": root["teaching_rule_de"],
        })
    write(HERE / "PASS984_THREE_LOCAL_DIAGRAM_SIGNS.tsv", local_rows, list(local_rows[0]))

    lines = [
        "# Pass 984 — das kurze Stammwörterbuch",
        "",
        "## Kernbestand",
        "",
        "Es bleiben **53 portable Bedeutungswurzeln**. Drei weitere Zeichen sind",
        "rein lokale Diagrammzeichen und keine allgemeinen Wortstämme. Gelernte",
        "Fachwörter und Drogenetiketten stehen in eigenen Schubladen.",
        "",
        "Wichtigste sprachliche Bereinigung:",
        "",
        "- `Y` = **POSTEN** (der aktuell gemeinte Gegenstand), nicht das vage DIES;",
        "- `OR` = **ARBEITSSATZ** (Ansatz/Konfiguration/Klasse), nicht Satz im",
        "  grammatischen Sinn;",
        "- `DY` = **SCHLUSS** nur in den bereits gelernten Schlusskarten;",
        "- `AIR` = **LAUF**, im Bad ein Flüssigkeitslauf, im Rad ein Ringlauf;",
        "- `CHEO` = **AUSZUG** im laufenden Werkstatttext; an einer Bildetikette",
        "  wird die ganze Kennung kopiert und CHEO nicht übersetzt.",
        "",
        "## Alle 53 Wurzeln",
        "",
    ]
    for row in rows:
        lines.append(
            f"- `{row['recognition_form']}` — **{row['atomic_meaning_de']}** "
            f"({row['content_events']} laufende Textvorkommen)"
        )
    lines += [
        "",
        "## Leseregel",
        "",
        "> Ein kurzer Kern bleibt gleich; Bild und Register liefern nur sein",
        "> konkretes Objekt. ZIEL ist im Rezept das Zielgefäß, im Bad die",
        "> Aufnahmestelle und im Rad der Zielplatz. Das ist dieselbe Relation, kein",
        "> Bedeutungswechsel.",
        "",
    ]
    (HERE / "PASS984_PLAIN_ROOT_DICTIONARY.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "portable_roots": len(rows),
        "local_diagram_signs": len(local_rows),
        "content_root_uses": sum(int(r["content_events"]) for r in rows),
    }
    (HERE / "PASS984_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
