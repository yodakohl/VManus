#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_EIGHTY_FOURTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_eighty_fourth.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    states = read(f"{PREFIX}_19_BATCH_STATES.tsv")
    transitions = read(f"{PREFIX}_15_BATCH_TRANSITIONS.tsv")
    chains = read(f"{PREFIX}_4_OWNER_BATCH_CHAINS.tsv")
    stock = read(f"{PREFIX}_10_STOCK_READY_HANDLES.tsv")
    supplies = read(f"{PREFIX}_6_EXPLAINED_SUPPLY_LINKS.tsv")
    events = read(f"{PREFIX}_100_EVENT_BATCH_BINDING.tsv")
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "states_19": len(states) == 19 and len({row["product_handle"] for row in states}) == 19,
        "transitions_15": len(transitions) == 15,
        "chains_4": len(chains) == 4 and sum(int(row["states"]) for row in chains) == 19 and sum(int(row["transitions"]) for row in chains) == 15,
        "stock_10": len(stock) == 10 and all(row["availability_reason"] != "NONE" for row in stock),
        "six_original_supplies_ready": len(supplies) == 6 and all(row["supply_link_changed"] == "NO" for row in supplies),
        "events_100": len(events) == 100 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 101)],
        "events_bound_once": sum(int(row["cards"]) for row in states) == 100 and len({row["event_id"] for row in events}) == 100,
        "predecessors_resolve": all(row["revised_predecessor"] == "NONE" or row["revised_predecessor"] in {state["product_handle"] for state in states} for row in states),
        "four_roots": sum(row["revised_predecessor"] == "NONE" for row in states) == 4,
        "selected_handles_present": {row["internal_product_handle"] for row in supplies} == {"A.G2", "B.X2", "C.W2", "D.P1"},
        "no_new_card_meanings": summary["new_card_meanings"] == 0,
        "fixed_pages": summary["fixed_pages"] == ["f10r", "f11r", "f55v", "f56r"],
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
