#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(OUT / "build_nine_hundred_forty_eighth.py")], check=True)
    events = rows("PASS948_10_TRIANGULAR_INSET_EVENTS.tsv")
    lines = rows("PASS948_7_INSET_LINES.tsv")
    checks = [
        ("events_10", len(events) == 10, len(events)),
        ("lines_7", len(lines) == 7, len(lines)),
        ("one_owner", len({row["corrected_owner_id"] for row in events}) == 1, "inset"),
        ("all_loci", {row["locus"] for row in events} == {f"f75r.{n}" for n in range(47, 54)}, "47-53"),
        ("all_local", all(row["codebook_layer"] == "LOCAL_NOMENCLATOR_OR_ADDRESS" for row in events), "local"),
        ("all_read", all(row["local_reading_de"].strip() for row in events), "read"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in events).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS948_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
