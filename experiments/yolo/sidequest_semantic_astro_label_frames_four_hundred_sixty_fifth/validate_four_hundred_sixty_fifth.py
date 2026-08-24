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
    resolutions = read("FOUR_HUNDRED_SIXTY_FIFTH_36_LABEL_FRAME_RESOLUTIONS.tsv")
    groups = read("FOUR_HUNDRED_SIXTY_FIFTH_395_ASTRO_GROUP_LABEL_FRAMES.tsv")
    loci = read("FOUR_HUNDRED_SIXTY_FIFTH_142_ASTRO_LOCUS_LABEL_FRAMES.tsv")
    ledger = read("FOUR_HUNDRED_SIXTY_FIFTH_776_GROUP_LABEL_FRAME_LEDGER.tsv")
    types = read("FOUR_HUNDRED_SIXTY_FIFTH_98_LOCAL_TYPE_REGISTER.tsv")
    checks = {
        "resolutions_36": len(resolutions) == 36,
        "groups_395": len(groups) == 395,
        "loci_142": len(loci) == 142,
        "ledger_776": len(ledger) == 776,
        "local_types_98": len(types) == 98,
        "resolved_label_frames_36": sum(row["transfer_status"] == "ASTRO_LABEL_FRAME_RESOLVED_COMPONENT_SEQUENCE" for row in groups) == 36,
        "remaining_local_77": sum(row["transfer_status"] == "ASTRO_LOCAL_LABEL" for row in groups) == 77,
        "all_resolved_sources_were_local": all(row["surface"].endswith(("s", "d")) for row in resolutions),
        "label_values_exact": {row["label_frame"]: row["label_frame_value_de"] for row in resolutions} == {"S_LABEL": "Sternetikett", "D_LABEL": "Platzetikett"},
        "group_order": [row["group_serial"] for row in groups] == [str(n) for n in range(1, 396)],
        "locus_membership_once": sorted((serial for row in loci for serial in row["group_serials"].split("|")), key=int) == [str(n) for n in range(1, 396)],
        "ledger_partition": [sum(row["domain"] == domain for row in ledger) for domain in ("PROSE", "ASTRO")] == [381, 395],
        "all_defaults_present": all(row["atomic_default_de"] for row in ledger),
        "no_cross_join": all(row["cross_instrument_join"] == "NONE" for row in groups + loci),
        "fixed_astro_pages": {row["page"] for row in groups} == {"f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in groups),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
