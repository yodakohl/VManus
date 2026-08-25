#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("PASS946_2511_THREE_LAYER_EVENT_EDITION.tsv")
    pages = read("PASS946_14_PAGE_LAYER_COUNTS.tsv")
    counts = {layer: sum(row["codebook_layer"] == layer for row in events) for layer in {row["codebook_layer"] for row in events}}
    checks = [
        ("events_2511", len(events) == 2511, len(events)),
        ("pages_14", len(pages) == 14, len(pages)),
        ("productive_1008", counts.get("PRODUCTIVE_ABBREVIATION_COMPOSITION") == 1008, counts),
        ("learned_1002", counts.get("LEARNED_FORMULA_CARD") == 1002, counts),
        ("local_501", counts.get("LOCAL_NOMENCLATOR_OR_ADDRESS") == 501, counts),
        ("page_sum", sum(int(row["events"]) for row in pages) == 2511, sum(int(row["events"]) for row in pages)),
        ("layer_page_sum", sum(int(row["productive_compositions"]) + int(row["learned_formula_cards"]) + int(row["local_nomenclator_or_addresses"]) for row in pages) == 2511, "complete"),
        ("unique_events", len({row["event_id"] for row in events}) == 2511, len({row["event_id"] for row in events})),
        ("all_values", all(row["current_value_de"].strip() for row in events), "nonempty"),
        ("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in events + pages), "sealed"),
    ]
    targets = [OUT / "PASS946_2511_THREE_LAYER_EVENT_EDITION.tsv", OUT / "PASS946_14_PAGE_LAYER_COUNTS.tsv", OUT / "PASS946_THREE_LAYER_CODEBOOK_MANUAL.md"]
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    subprocess.run([sys.executable, str(OUT / "build_nine_hundred_forty_sixth.py")], check=True)
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    checks.append(("deterministic", before == after, len(targets)))
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS946_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
