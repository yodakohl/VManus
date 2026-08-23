#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    contrasts = rows("HUNDRED_TWELFTH_EIGHT_ORDER_CONTRASTS.tsv")
    predictions = rows("HUNDRED_TWELFTH_TWELVE_ORDERED_PREDICTIONS.tsv")
    statements = rows("HUNDRED_TWELFTH_116_ORDER_ANNOTATED_STATEMENTS.tsv")
    checks = {
        "contrasts_8": len(contrasts) == 8,
        "predictions_12": len(predictions) == 12,
        "statements_116": len(statements) == 116,
        "one_way_6": sum(r["order_decision"] == "ONE_WAY_WORKSHOP_ORDER" for r in contrasts) == 6,
        "bidirectional_y_aiin": contrasts[0]["order_decision"] == "BIDIRECTIONAL_ATTACHMENT",
        "bidirectional_ol_or_frame": contrasts[7]["order_decision"] == "BIDIRECTIONAL_ATTACHMENT",
        "present_5": sum(r["current_status"] == "ALREADY_PRESENT" for r in predictions) == 5,
        "open_7": sum(r["current_status"] == "OPEN_FORWARD_SEQUENCE" for r in predictions) == 7,
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
