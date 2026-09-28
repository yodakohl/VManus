"""Enumerate the frozen f69r wind-polarity symmetry question."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "SOURCE.json"
RESULT = ROOT / "artifacts" / "RESULT.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    size = source["sectors"]
    historical = {
        i: name
        for name, positions in source["historical_classes"].items()
        for i in positions
    }
    target = {
        i: name
        for name, positions in source["voynich_classes"].items()
        for i in positions
    }
    assert len(historical) == len(target) == size
    rows = []
    for handedness in (1, -1):
        for offset in range(size):
            mismatches = [
                i
                for i in range(size)
                if source["class_correspondence"][historical[i]]
                != target[(offset + handedness * i) % size]
            ]
            rows.append({
                "offset": offset,
                "handedness": handedness,
                "mismatch_count": len(mismatches),
                "exact": not mismatches,
            })
    exact = [row for row in rows if row["exact"]]
    exact_keys = {(row["offset"], row["handedness"]) for row in exact}
    partners = [{
        "offset": row["offset"],
        "handedness": row["handedness"],
        "opposite_offset": (row["offset"] + source["polarity_shift"]) % size,
        "opposite_is_exact": (
            (row["offset"] + source["polarity_shift"]) % size,
            row["handedness"],
        ) in exact_keys,
    } for row in exact]
    result = {
        "experiment_id": "GDT1067",
        "source": str(SOURCE.relative_to(ROOT)),
        "map_count": len(rows),
        "exact_count": len(exact),
        "maps": rows,
        "opposite_partners": partners,
        "all_exact_have_opposite": all(p["opposite_is_exact"] for p in partners),
        "decision": (
            "POLARITY_NONIDENTIFIABLE_UNDER_EXISTING_GEOMETRY"
            if partners and all(p["opposite_is_exact"] for p in partners)
            else "ASYMMETRY_REQUIRES_REVIEW"
        ),
    }
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["decision"], result["exact_count"], "/", result["map_count"])


if __name__ == "__main__":
    main()
