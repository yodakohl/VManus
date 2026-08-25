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
    families = read("PASS942_47_LEARNED_CARD_FAMILIES.tsv")
    variants = read("PASS942_97_SURFACE_VARIANTS.tsv")
    events = read("PASS942_2511_RENDERER_CONSOLIDATED_READINGS.tsv")
    checks = [
        ("families_47", len(families) == 47, len(families)),
        ("variants_97", len(variants) == 97, len(variants)),
        ("events_2511", len(events) == 2511, len(events)),
        ("family_unique", len({row["learned_card_id"] for row in families}) == 47, len({row["learned_card_id"] for row in families})),
        ("variant_unique", len({row["surface"] for row in variants}) == 97, len({row["surface"] for row in variants})),
        ("family_event_sum", sum(int(row["events"]) for row in families) == 1137, sum(int(row["events"]) for row in families)),
        ("event_route_sum", sum(row["reading_route"] == "LEARNED_CARD_FAMILY" for row in events) == 1137, sum(row["reading_route"] == "LEARNED_CARD_FAMILY" for row in events)),
        ("all_spoken", all(row["spoken_value_de"].strip() for row in events), "nonempty"),
        ("all_pages", len({row["physical_page"] for row in events}) == 14, len({row["physical_page"] for row in events})),
        ("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in events), "sealed"),
    ]
    targets = [OUT / "PASS942_47_LEARNED_CARD_FAMILIES.tsv", OUT / "PASS942_97_SURFACE_VARIANTS.tsv", OUT / "PASS942_2511_RENDERER_CONSOLIDATED_READINGS.tsv"]
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    subprocess.run([sys.executable, str(OUT / "build_nine_hundred_forty_second.py")], check=True)
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    checks.append(("deterministic", before == after, len(targets)))
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS942_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
