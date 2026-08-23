#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    skeletons = rows("HUNDRED_TWENTY_SECOND_116_SHARED_CARD_SKELETONS.tsv")
    edges = rows("HUNDRED_TWENTY_SECOND_DIRECTED_SHARED_NETWORK.tsv")
    profiles = rows("HUNDRED_TWENTY_SECOND_SEVENTEEN_NETWORK_PROFILES.tsv")
    slots = rows("HUNDRED_TWENTY_SECOND_EIGHT_SLOT_SOURCE_ORDER.tsv")
    checks = {
        "skeletons_116": len(skeletons) == 116,
        "profiles_17": len(profiles) == 17,
        "slots_8": len(slots) == 8,
        "profile_cards_unique": len({r["master_card_id"] for r in profiles}) == 17,
        "shared_statements_57": sum(r["shared_card_count"] != "0" for r in skeletons) == 57,
        "edges_nonempty": len(edges) > 20,
        "paired_measure_present": any("chey aiin chey" in r["shared_surface_skeleton"] for r in skeletons),
        "ol_or_frame_present": any("cheol cholor cheol" in r["shared_surface_skeleton"] for r in skeletons),
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in skeletons),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
