#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P971 = ROOT / "experiments/yolo/sidequest_semantic_canonical_compact_workshop_edition_nine_hundred_seventy_first"
P980 = ROOT / "experiments/yolo/sidequest_semantic_158_unit_image_owned_codebook_nine_hundred_eightieth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    lexicon = read(P980 / "PASS980_158_TEACHING_UNIT_CODEBOOK.tsv")
    address_rule = {
        "teaching_unit_id": "X001",
        "layer": "H_LOCAL_ADDRESS_COPY_RULE",
        "unit_type": "REGISTER_COPY_RULE",
        "recognition_forms": "ANY_GROUP_IN_IMAGE_LABEL_OR_DIAGRAM_ADDRESS_LOCUS",
        "spoken_value_de": "BILDADRESSE",
        "concrete_context_values_de": "Den benachbarten Bild-, Stern-, Ring- oder Stationsplatz benennen.",
        "specialist_surface_forms": "",
        "observed_specialist_events": "485",
        "pages": "f67r2|f68r1|f69v|f70v|f75r|f81v|f82r|f83r",
        "teaching_rule_de": "Am Labelort die ganze Kennung aus dem Meisterexemplar kopieren; sichtbare Wurzeln nur als Merkhilfe verwenden.",
    }
    lexicon.append(address_rule)
    write(HERE / "PASS983_159_TEACHING_UNIT_CODEBOOK.tsv", lexicon, list(lexicon[0]))

    bindings = read(P980 / "PASS980_2511_EVENT_TEACHING_BINDING.tsv")
    addresses = {r["event_id"]: r for r in read(P971 / "PASS971_501_LOCAL_ADDRESS_LEDGER.tsv")}
    rows = []
    for row in bindings:
        revised = dict(row)
        if row["primary_layer"] == "LOCAL_ADDRESS_COMPOSITION":
            address = addresses[row["event_id"]]
            revised["primary_layer"] = "LOCAL_ADDRESS_OR_KENNING"
            revised["mnemonic_common_unit_ids"] = row["primary_teaching_unit_ids"]
            revised["primary_teaching_unit_ids"] = "X001"
            revised["complete_working_reading_de"] = address["local_address_reading_de"]
        rows.append(revised)
    write(HERE / "PASS983_2511_EVENT_ADDRESS_AWARE_BINDING.tsv", rows, list(rows[0]))

    lines = [
        "# Pass 983 — adressbewusstes 159-Einheiten-Codebuch",
        "",
        "## Die Korrektur",
        "",
        "Das vorherige 158er-Codebuch las auch echte Bild- und Ringetiketten aus",
        "ihren sichtbaren Wurzeln. Das war zu grob. `cheody` kann im Pflanzenrezept",
        "an AUSZUG erinnern, ist im Widderring aber eine lokale Figurenkennung.",
        "",
        "Darum kommt genau eine Lehrregel hinzu:",
        "",
        "> **X001 BILDADRESSE:** Steht die Gruppe unmittelbar als Bildetikett oder",
        "> Diagrammadresse, kopiere ihren ganzen lokalen Namen. Benutze die sichtbaren",
        "> Wurzeln nur zum Wiederfinden, nicht zum Übersetzen.",
        "",
        "## Neue Gesamtgröße",
        "",
        "- 158 bisherige Bedeutungs-/Karten-Einheiten;",
        "- 1 Registerregel für 485 nicht-drogenspezifische lokale Adressen;",
        "- **159 Einheiten gesamt**.",
        "",
        "Die sechzehn f88r-Drogenetiketten behalten ihre konkreten Bildwerte. Die",
        "übrigen 485 Labelgruppen erhalten ihre Besitzerlesung aus Bild, Ring oder",
        "Station. Damit bleiben CHEO, CH, AIR und andere Werkstattwurzeln im laufenden",
        "Text stabil und werden nicht durch zufällig ähnlich gebaute Eigennamen verbogen.",
        "",
    ]
    (HERE / "PASS983_ADDRESS_AWARE_CODEBOOK_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "teaching_units": len(lexicon),
        "events": len(rows),
        "local_address_or_kenning_events": sum(r["primary_layer"] == "LOCAL_ADDRESS_OR_KENNING" for r in rows),
    }
    (HERE / "PASS983_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
