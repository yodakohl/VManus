"""Independently reconstruct and validate GDT1067's 32-map enumeration."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts" / "RESULT.json"
VALIDATION = ROOT / "artifacts" / "VALIDATION.json"


def expected() -> dict:
    # Reconstructed directly from the published source-method class formulae.
    source_classes = ["principal" if i % 4 == 0 else
                      "unused" if i % 4 == 2 else "collateral"
                      for i in range(16)]
    target_classes = ["blank" if i % 4 == 0 else
                      "green" if i % 4 == 2 else "blue"
                      for i in range(16)]
    correspondence = {"principal": "green", "unused": "blank", "collateral": "blue"}
    rows = []
    for hand in (1, -1):
        for offset in range(16):
            errors = sum(
                correspondence[source_classes[i]] != target_classes[(offset + hand * i) % 16]
                for i in range(16)
            )
            rows.append({"offset": offset, "handedness": hand,
                         "mismatch_count": errors, "exact": errors == 0})
    exact = [row for row in rows if row["exact"]]
    keys = {(row["offset"], row["handedness"]) for row in exact}
    partners = [{"offset": row["offset"], "handedness": row["handedness"],
                 "opposite_offset": (row["offset"] + 8) % 16,
                 "opposite_is_exact": ((row["offset"] + 8) % 16,
                                       row["handedness"]) in keys}
                for row in exact]
    return {"maps": rows, "opposite_partners": partners,
            "map_count": len(rows), "exact_count": len(exact),
            "all_exact_have_opposite": all(x["opposite_is_exact"] for x in partners)}


def main() -> None:
    found = json.loads(RESULT.read_text(encoding="utf-8"))
    want = expected()
    for key, value in want.items():
        assert found[key] == value, key
    assert found["experiment_id"] == "GDT1067"
    assert found["decision"] == "POLARITY_NONIDENTIFIABLE_UNDER_EXISTING_GEOMETRY"
    assert want["exact_count"] == 8
    assert set(x["offset"] for x in want["opposite_partners"]) == {2, 6, 10, 14}
    # A corrupted partner flag differs from the independently built inventory.
    bad = json.loads(json.dumps(found))
    bad["opposite_partners"][0]["opposite_is_exact"] = False
    assert bad["opposite_partners"] != want["opposite_partners"]
    output = {"experiment_id": "GDT1067", "status": "PASS",
              "checked_maps": want["map_count"], "exact": want["exact_count"],
              "partner_involution": all(
                  (row["opposite_offset"] + 8) % 16 == row["offset"]
                  for row in want["opposite_partners"])}
    assert output["partner_involution"]
    VALIDATION.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS", output["checked_maps"], output["exact"])


if __name__ == "__main__":
    main()
