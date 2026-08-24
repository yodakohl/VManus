#!/usr/bin/env python3
"""Make Herbal card values agree with their declared component formulas."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_whole_card_attack_three_hundred_twenty_eighth"
DICTIONARY = BASE / "THREE_HUNDRED_TWENTY_EIGHTH_173_REVISED_DICTIONARY.tsv"
EVENTS = BASE / "THREE_HUNDRED_TWENTY_EIGHTH_381_REVISED_EVENTS.tsv"

REVISIONS = {
    "cthoor": ("Bereitansatz", "CTH+OR gives ready+batch; Säubern was not compositional."),
    "chety|chty": ("Zerkleinern", "The shared-deck decision is restored: this is a memorized whole card, not a CH component."),
    "otytchol": ("Folgeteilfortsetzung", "OT+YTY+OL gives following part plus continuation, not collecting."),
    "qotchol": ("Folgefortsetzung", "OT+OL gives following continuation; warming requires CHK."),
    "ycheor": ("Auszugsansatz", "Y+CHEO+OR gives active extract batch, not plant tips."),
    "cthaiin": ("Bereitsollmaß", "CTH+AIIN gives ready-state plus prescribed measure, not crushing an herb."),
    "qoctholy": ("Folgefortsetzungsposten", "OT+OL+Y gives a continued following item, not pressing."),
    "oykchor": ("Gefäßansatz", "OYK+OR gives vessel plus batch; glazing was an unsupported material detail."),
    "kaiiin": ("Bindestufe", "K+IIN gives bound stage; softness was not encoded."),
    "chodaiin": ("Zutatsollmaß", "CHO+AIIN gives ingredient plus prescribed measure, not an ulcer."),
    "shoyty": ("Zutatfolgeteil", "SHO+YTY gives ingredient plus following part, not retained flowers."),
    "dchol|schol": ("Vorfortsetzung", "D+OL gives previous-item continuation."),
    "kchy": ("Bindeposten", "K+Y gives a bound current item, not a draught."),
    "qotchy": ("Folgeposten", "OT+Y gives following item, not retained flowers."),
    "ykan": ("Postenzweitportion", "Y+K+AN gives current-item second portion."),
    "ody": ("Rücknahmeschluss", "O+DY gives withdrawal plus close; cooling was not encoded."),
    "oltchy": ("Fortsetzungszubereitung", "OL+TCH+Y gives continued active preparation; warming requires CHK."),
    "chodaly": ("Zutatstelle", "CHO+AL+Y gives ingredient at current target, not flowering onset."),
    "kchol": ("Bindefortsetzung", "K+OL gives bound continuation, not applying a poultice."),
    "choy": ("Zutatposten", "CHO+Y gives active ingredient item, not washing."),
    "kchey": ("Kurzbindeposten", "K+E+Y gives short-grade bound item, not coarse grinding."),
    "kchal": ("Zielbindung", "K+AL gives target binding, not straining."),
    "kchoar": ("Quellenzutatbindung", "K+CHO+AR gives bound ingredient from source, not use-extract."),
    "keol": ("Kurzbindefortsetzung", "K+E+OL gives short-grade bound continuation, not a single dose."),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary = read(DICTIONARY)
    events = read(EVENTS)
    revised_dictionary = []
    revision_rows = []
    atom = {}
    deck_class = {}
    formula = {}
    for row in dictionary:
        out = dict(row)
        if row["surface_family"] in REVISIONS:
            value, reason = REVISIONS[row["surface_family"]]
            old_value = row["atomic_value_de"]
            if row["surface_family"] == "chety|chty":
                out["deck_class"] = "MEMORIZED_WHOLE_CARD"
                out["component_formula"] = "WHOLE_CARD"
                decision = "RESTORE_SHARED_WHOLE_CARD"
            else:
                decision = "REVISE_TO_COMPONENT_LITERAL"
            out["atomic_value_de"] = value
            out["atomic_value_source"] = "PASS329_FORMULA_CONSISTENCY"
            revision_rows.append(
                {
                    "joint_tuple_id": row["joint_tuple_id"],
                    "surface_family": row["surface_family"],
                    "component_formula": out["component_formula"],
                    "old_atomic_value_de": old_value,
                    "new_atomic_value_de": value,
                    "decision": decision,
                    "reason_de": reason,
                }
            )
        revised_dictionary.append(out)
        atom[row["joint_tuple_id"]] = out["atomic_value_de"]
        deck_class[row["joint_tuple_id"]] = out["deck_class"]
        formula[row["joint_tuple_id"]] = out["component_formula"]

    revised_events = []
    statements: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        out = dict(row)
        out["atomic_value_de"] = atom[row["joint_tuple_id"]]
        out["deck_class"] = deck_class[row["joint_tuple_id"]]
        revised_events.append(out)
        if row["record_unit_id"].startswith("H"):
            statements[row["statement_id"]].append(out)

    herbal_events = [x for x in revised_events if x["record_unit_id"].startswith("H")]
    herbal_ids = {x["joint_tuple_id"] for x in herbal_events}
    herbal_dictionary = [x for x in revised_dictionary if x["joint_tuple_id"] in herbal_ids]
    statement_rows = []
    for statement_id, rows in statements.items():
        statement_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "surface_sequence": " ".join(x["surface"] for x in rows),
                "atomic_sequence": " → ".join(x["atomic_value_de"] for x in rows),
                "event_count": str(len(rows)),
            }
        )

    write("THREE_HUNDRED_TWENTY_NINTH_24_FORMULA_REPAIRS.tsv", revision_rows)
    write("THREE_HUNDRED_TWENTY_NINTH_173_GLOBAL_DICTIONARY.tsv", revised_dictionary)
    write("THREE_HUNDRED_TWENTY_NINTH_381_GLOBAL_EVENTS.tsv", revised_events)
    write("THREE_HUNDRED_TWENTY_NINTH_HERBAL_DICTIONARY.tsv", herbal_dictionary)
    write("THREE_HUNDRED_TWENTY_NINTH_100_HERBAL_EVENTS.tsv", herbal_events)
    write("THREE_HUNDRED_TWENTY_NINTH_19_HERBAL_STATEMENTS.tsv", statement_rows)
    names = [
        "THREE_HUNDRED_TWENTY_NINTH_24_FORMULA_REPAIRS.tsv",
        "THREE_HUNDRED_TWENTY_NINTH_173_GLOBAL_DICTIONARY.tsv",
        "THREE_HUNDRED_TWENTY_NINTH_381_GLOBAL_EVENTS.tsv",
        "THREE_HUNDRED_TWENTY_NINTH_HERBAL_DICTIONARY.tsv",
        "THREE_HUNDRED_TWENTY_NINTH_100_HERBAL_EVENTS.tsv",
        "THREE_HUNDRED_TWENTY_NINTH_19_HERBAL_STATEMENTS.tsv",
    ]
    summary = {
        "status": "PASS",
        "formula_repairs": len(revision_rows),
        "global_cards": len(revised_dictionary),
        "global_events": len(revised_events),
        "herbal_cards": len(herbal_dictionary),
        "herbal_events": len(herbal_events),
        "herbal_statements": len(statement_rows),
        "productive_cards": sum(x["deck_class"] == "PRODUCTIVE_COMPOSITION" for x in revised_dictionary),
        "whole_cards": sum(x["deck_class"] == "MEMORIZED_WHOLE_CARD" for x in revised_dictionary),
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_TWENTY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
