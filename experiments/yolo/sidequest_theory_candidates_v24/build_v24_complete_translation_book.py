#!/usr/bin/env python3
"""Render the complete 776-event working translation as a readable edition."""

from __future__ import annotations

import csv
import json
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
V22 = HERE.parent / "sidequest_theory_candidates_v22"
PAGES = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r",
         "f67r2", "f68r1", "f69v"]
GERMAN = {
    "f10r": "Die Wurzel der abgebildeten Pflanze in laufendem Wasser reinigen, zerstoßen, mit Rotwein bereiten und in üblicher Menge gegen Magenbeschwerden verwenden. Einen Teil warm anwenden, den Rest trocken lagern; später Sud und ausgepressten Saft bereiten und vor der Blüte sammeln.",
    "f11r": "Die Wurzel im Frühjahr sammeln, zerdrücken und zweimal durch Tuch klären. Den Saft abkühlen lassen und gegen Schwellung auflegen; aus den Blättern einen warmen Umschlag machen.",
    "f55v": "Ein breitblättriges Kraut in Weißwein auskochen, klären und als Wundwaschung verwenden. Eine zweite warme Mischung in einem verschlossenen Gefäß aufbewahren und frisch anwenden.",
    "f56r": "Nacheinander Wurzel, Blatt und Blüten- oder Samenkopf eines Feuchtstandort-Krauts verwenden. Teile in Wein oder Honig bereiten, örtlich auflegen, im Schatten trocknen und eine weitere Zubereitung gegen Magenbeschwerden verwenden.",
    "f81v": "Ein Becken füllen, die Arbeitsflüssigkeit temperieren, verbundene Teile beschicken, die bezeichnete Stelle eintauchen oder waschen, danach ablaufen lassen und die Leitung spülen.",
    "f82r": "Mehrere verbundene Becken mit temperiertem Kräutersud beschicken. Mengen mischen, Flüssigkeit durch Leitungen führen, Stellen baden oder spülen, verbrauchte Flüssigkeit ablassen und die Arbeitsschritte einzeln abschließen.",
    "f83r": "Varianten desselben Nassverfahrens: Mengen und Wärme einstellen, mischen, setzen lassen, filtern, salben, spülen, wiederholen und in ein unteres Auffanggefäß ableiten.",
    "f67r2": "Planet, Tierkreisbereich und regierten Körperteil bestimmen. Unter der gewählten warmen, kalten, trockenen oder feuchten Bedingung die erlaubte Anwendung wählen und invasive Behandlung des regierten Bereichs vermeiden.",
    "f68r1": "Unter dem Mond als Besitzer des Katalogs die gegenwärtige von achtundzwanzig Mondstationen anhand ihrer gezeichneten räumlichen Position identifizieren und ihre Regel konsultieren.",
    "f69v": "Für jede der achtundzwanzig Stationen die konkrete medizinische Wahlregel lesen: baden, kühl waschen, salben, ruhen, spülen, Flüssigkeit abziehen oder abseihen beziehungsweise eine riskante Behandlung unterlassen.",
}
EVASIVE = {"", "unknown", "opaque", "untranslated", "content", "payload"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    ledger = read(V22 / "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    assert len(ledger) == 776
    assert {row["page"] for row in ledger} == set(PAGES)
    assert all(row["default_English"].strip().lower() not in EVASIVE for row in ledger)

    interlinear = []
    for row in ledger:
        out = dict(row)
        out["translation_status"] = "SPECULATIVE_COMPLETE_DEFAULT"
        interlinear.append(out)
    with (HERE / "V24_COMPLETE_776_EVENT_INTERLINEAR.tsv").open(
            "w", encoding="utf-8", newline="") as handle:
        fields = list(interlinear[0])
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(interlinear)

    grouped: OrderedDict[tuple[str, str], list[dict[str, str]]] = OrderedDict()
    for row in ledger:
        grouped.setdefault((row["page"], row["locus"]), []).append(row)
    assert len(grouped) == 199
    loci = []
    for (page, locus), rows in grouped.items():
        loci.append({
            "page": page,
            "locus": locus,
            "visible_event_count": str(len(rows)),
            "visible_source_sequence": " ".join(row["surface"] for row in rows),
            "complete_literal_working_translation": "; ".join(
                row["default_English"] for row in rows
            ),
            "sentence_boundary_status": "NOT_FORCED_BY_PHYSICAL_LINE",
        })
    with (HERE / "V24_COMPLETE_199_LOCUS_TRANSLATION.tsv").open(
            "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(loci[0]), delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(loci)

    lines = [
        "# V24 complete ten-page working translation",
        "",
        "Status: complete speculative reading, not deciphered plaintext.",
        "Every visible event is represented below; physical lines do not force sentence ends.",
        "",
    ]
    for page in PAGES:
        lines.extend([f"## {page}", "", f"**Flüssige deutsche Lesung:** {GERMAN[page]}", ""])
        for row in (item for item in loci if item["page"] == page):
            lines.extend([
                f"### {row['locus']}", "",
                f"**Quelle:** `{row['visible_source_sequence']}`", "",
                f"**Vollständige wörtliche Arbeitslesung:** {row['complete_literal_working_translation']}.", "",
            ])
    (HERE / "V24_COMPLETE_TEN_PAGE_TRANSLATION.md").write_text(
        "\n".join(lines).rstrip() + "\n", encoding="utf-8"
    )

    result = {
        "schema": "SIDEQUEST_V24_COMPLETE_TRANSLATION_EDITION_V1",
        "status": "PASS",
        "pages": 10,
        "events": 776,
        "physical_line_or_diagram_loci": 199,
        "blank_or_evasive_defaults": 0,
        "german_page_paraphrases": 10,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
        "claim_ceiling": "Complete speculative edition, not confirmed translation.",
    }
    (HERE / "V24_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
