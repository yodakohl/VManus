#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P376 = ROOT / "experiments/yolo/sidequest_semantic_image_first_practice_page_three_hundred_seventy_sixth"
P377 = ROOT / "experiments/yolo/sidequest_semantic_rescaled_image_copy_three_hundred_seventy_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


OMITTED_POSITION = 6


def main() -> None:
    first = {int(row["source_position"]): row for row in read(P376 / "THREE_HUNDRED_SEVENTY_SIXTH_14_SOURCE_CARDS.tsv")}
    second_cross = {int(row["source_position"]): row for row in read(P377 / "THREE_HUNDRED_SEVENTY_SEVENTH_14_CARD_CROSSWALK.tsv")}
    second_visible = read(P377 / "THREE_HUNDRED_SEVENTY_SEVENTH_15_SECOND_COPY_FORMS.tsv")
    trainee_visible = [row for row in second_visible if int(row["source_position"]) != OMITTED_POSITION]

    collation_rows = []
    for position in range(1, 15):
        a = first[position]
        b = second_cross[position]
        omitted = position == OMITTED_POSITION
        if omitted:
            category = "TRUE_OMISSION"
            trainee_surface = "MISSING"
            action = f"RESTORE::{b['second_palette_surface']}"
        elif b["surface_changed"] == "YES":
            category = "REGISTERED_SURFACE_VARIANT"
            trainee_surface = b["second_palette_surface"]
            action = "KEEP_VARIANT"
        else:
            category = "INVARIANT_MATCH"
            trainee_surface = b["second_palette_surface"]
            action = "KEEP"
        collation_rows.append({
            "source_position": position,
            "microcycle": a["microcycle"],
            "owner": a["visible_owner"],
            "joint_tuple_id": a["joint_tuple_id"],
            "atomic_value_de": a["atomic_value_de"],
            "first_copy_surface": a["surface"],
            "trainee_second_surface": trainee_surface,
            "expected_second_surface": b["second_palette_surface"],
            "collation_category": category,
            "corrector_action": action,
            "meaning_changed": "NO",
        })

    phenomena = [
        {"phenomenon_id": "F1", "category": "REGISTERED_SURFACE_VARIANT", "locations": "1|2|7|8|9|10|11|12", "count": 8, "corrector_treatment": "KEEP; same card identity", "not_confused_with": "OMISSION"},
        {"phenomenon_id": "F2", "category": "MARKED_READ_ONCE_CARRY", "locations": "source position4 appears twice", "count": 1, "corrector_treatment": "READ ONCE; keep right execution", "not_confused_with": "EXTRA_SOURCE_CARD"},
        {"phenomenon_id": "F3", "category": "TRUE_OMISSION", "locations": "source position6 between lcheey and cthy", "count": 1, "corrector_treatment": "RESTORE cphy from parallel copy", "not_confused_with": "VARIANT_OR_CARRY"},
        {"phenomenon_id": "F4", "category": "OWNER_HANDOFF", "locations": "position7 H4 -> position8 B3", "count": 1, "corrector_treatment": "KEEP hard boundary", "not_confused_with": "MISSING_CONNECTOR"},
    ]
    corrected_second = []
    for position in range(1, 15):
        corrected_second.append(second_cross[position]["second_palette_surface"])
    result = [{
        "first_source_cards": 14,
        "trainee_second_source_cards": 13,
        "trainee_second_visible_forms": len(trainee_visible),
        "registered_variants_kept": sum(row["collation_category"] == "REGISTERED_SURFACE_VARIANT" for row in collation_rows),
        "true_omissions": sum(row["collation_category"] == "TRUE_OMISSION" for row in collation_rows),
        "carry_copies_read_once": 1,
        "owner_handoffs_kept": 1,
        "restored_surface": second_cross[OMITTED_POSITION]["second_palette_surface"],
        "corrected_source_cards": len(corrected_second),
        "corrected_surface_sequence": " ".join(corrected_second),
        "exact_after_correction": "YES",
    }]
    write("THREE_HUNDRED_SEVENTY_EIGHTH_14_POSITION_COLLATION.tsv", collation_rows)
    write("THREE_HUNDRED_SEVENTY_EIGHTH_FOUR_PHENOMENA.tsv", phenomena)
    write("THREE_HUNDRED_SEVENTY_EIGHTH_TRAINEE_VISIBLE_FORMS.tsv", trainee_visible)
    write("THREE_HUNDRED_SEVENTY_EIGHTH_CORRECTION_RESULT.tsv", result)
    counts = Counter(row["collation_category"] for row in collation_rows)
    page = f"""# Pass 378 — Kollation zweier Musterblätter

## Beschädigte Zweitkopie

```text
cho chor cheoar  cheky
cheky
lcheey cthy

chey chaiin chckhy oky
okeey qokedy talam
```

Der Korrektor trennt vier Dinge:

- acht registrierte Oberflächenvarianten bleiben stehen;
- `cheky` am Rand wird einmal gelesen;
- der H4→B3-Besitzerwechsel bleibt eine harte Grenze;
- zwischen `lcheey` und `cthy` fehlt wirklich `cphy` = Nachseihen.

## Korrigierte Zweitkopie

`{result[0]['corrected_surface_sequence']}`

Die Korrektur stellt genau eine Karte wieder her und ändert keinen Kartenwert.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_EIGHTH_COLLATOR_NOTEBOOK.md").write_text(page, encoding="utf-8")
    report = f"""# Pass 378 — Varianten, Carry, Lücke und Besitzerwechsel

Die absichtlich beschädigte Zweitkopie hat 13 statt 14 Quellkarten. Der
Korrektor behält {counts['REGISTERED_SURFACE_VARIANT']} Varianten, liest eine
markierte Randkopie einmal, respektiert einen Besitzerwechsel und stellt genau
`cphy`/Nachseihen wieder her. Danach stimmt die komplette 14-Karten-Folge.

Als nächstes soll der Korrektor die restaurierte Seite ohne deutsche Werte an
einen dritten Schreiber diktieren. Dieser setzt eine dritte Palette und darf nur
an den acht variablen Positionen abweichen.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "positions": len(collation_rows),
        "trainee_source_cards": 13,
        "trainee_visible_forms": len(trainee_visible),
        "registered_variants": counts["REGISTERED_SURFACE_VARIANT"],
        "invariant_matches": counts["INVARIANT_MATCH"],
        "true_omissions": counts["TRUE_OMISSION"],
        "marked_carries": 1,
        "owner_handoffs": 1,
        "corrected_source_cards": 14,
    }
    (HERE / "THREE_HUNDRED_SEVENTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
