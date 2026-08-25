#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("SEVEN_HUNDRED_NINETIETH_57_QUANTITY_EVENTS.tsv")
    cards = read("SEVEN_HUNDRED_NINETIETH_18_QUANTITY_CARDS.tsv")
    pairs = read("SEVEN_HUNDRED_NINETIETH_3_PAIRED_PARADIGMS.tsv")
    rungs = read("SEVEN_HUNDRED_NINETIETH_6_ATTESTED_QUANTITY_RUNGS.tsv")
    counterparts = read("SEVEN_HUNDRED_NINETIETH_12_UNPAIRED_COUNTERPARTS.tsv")
    predictions = read("SEVEN_HUNDRED_NINETIETH_14_PREDICTED_SURFACES.tsv")
    withheld = read("SEVEN_HUNDRED_NINETIETH_1_WITHHELD_SURFACE.tsv")
    teaching = read("SEVEN_HUNDRED_NINETIETH_3_TEACHING_PAIRS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_NINETIETH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_57_18_3_6_12_14_1_3": (len(events), len(cards), len(pairs), len(rungs), len(counterparts), len(predictions), len(withheld), len(teaching)) == (57, 18, 3, 6, 12, 14, 1, 3),
        "aiin39_ain18": sum(row["quantity_token"] == "AIIN" for row in events) == 39 and sum(row["quantity_token"] == "AIN" for row in events) == 18,
        "transparent56_opaque1": sum(row["surface_transparency"] == "TRANSPARENT" for row in events) == 56 and sum(row["surface_transparency"] == "OPAQUE_WHOLE_ALLOGRAPH" for row in events) == 1,
        "opaque_is_sotodan": [(row["surface"], row["component_recipe"]) for row in events if row["surface_transparency"] == "OPAQUE_WHOLE_ALLOGRAPH"] == [("sotodan", "OT+O+AIN")],
        "three_pairs_exact": {row["quantity_signature"] for row in pairs} == {"QTY", "OK+QTY", "Y+K+QTY"},
        "paired_events40": sum(int(row["total_events"]) for row in pairs) == 40,
        "all_predictions_unseen": all(row["fixed_page_collision"] == "NO" for row in predictions),
        "withheld_only_sotodan": len(withheld) == 1 and withheld[0]["source_surface"] == "sotodan",
        "readings_invariant": all(row["quantity_reading_de"] == ("SOLLMASS" if row["quantity_token"] == "AIIN" else "PORTION") for row in events),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (events, cards, pairs, rungs, counterparts, predictions, withheld, teaching) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["decision"] == "AIIN_SOLLMASS_AND_AIN_PORTION_FORM_PRODUCTIVE_MINIMAL_PAIRS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETIETH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
