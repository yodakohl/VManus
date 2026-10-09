"""Account for a fixed conditional body/cap projection; no glyph recognition."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "HAND_WRITER_SPATIAL_REVIEW_CONTRACT_20261005.json"
OBSERVATION = HERE / "HAND_WRITER_SPATIAL_OBSERVATION_20261005.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    contract = json.loads(CONTRACT.read_text())
    for name, expected in contract["inputs"].items():
        if digest(HERE / name) != expected:
            raise ValueError(f"Changed input: {name}")
    if digest(HERE / contract["image"]) != contract["image_sha256"]:
        raise ValueError("Changed image")
    records = json.loads(
        (HERE / "HAND_WRITER_NATIVE_ACCOUNT_20261004.json").read_text()
    )["records"]
    if any(r["locus"] not in {"f25v.1", "f25v.2"} for r in records):
        raise ValueError("Out-of-scope account row")
    result = {
        "status": "CONDITIONAL_ONE_CAP_PROJECTION_NO_SUPPORTED_VOWEL_OR_EMPTY_CARRIER_BINDING",
        "contract_sha256": digest(CONTRACT),
        "source_sha256": digest(Path(__file__)),
        "observation_sha256": digest(OBSERVATION),
        "input_hashes_verified": True,
        "readers": {},
        "limits": contract["limits"],
        "decision": "No vowel key or CV decoder. Reject only observed body-as-K assignments under this projection; leave the unbound writer inconclusive.",
    }
    for edition in dict.fromkeys(r["edition"] for r in records):
        retained, excluded = [], []
        occurrences = defaultdict(list)
        for r in records:
            if r["edition"] != edition:
                continue
            row = {k: r[k] for k in (
                "locus", "source_group_index", "ivtff_group_raw",
                "left_separator", "right_separator", "native_caution"
            )}
            if not (
                r["left_separator"] in {"LINE_START", "DEFINITE_SPACE"}
                and r["right_separator"] in {"LINE_END", "DEFINITE_SPACE"}
            ):
                excluded.append(row)
                continue
            row["cells"] = [
                {"source_surface": unit["surface"],
                 "body": "ch" if unit["surface"] == "sh" else unit["surface"],
                 "marks": ["CAP"] if unit["surface"] == "sh" else []}
                for unit in r["G1_post_application_extension"]
            ]
            for index, cell in enumerate(row["cells"]):
                occurrences[cell["body"]].append({
                    "locus": r["locus"], "group": r["source_group_index"],
                    "raw": r["ivtff_group_raw"], "zero_based_index": index,
                    "mark_count": len(cell["marks"]),
                    "violations_if_K": (["not_first"] if index else [])
                    + ([] if cell["marks"] else ["empty_stack"]),
                })
            retained.append(row)
        cells = [c for r in retained for c in r["cells"]]
        candidates = [
            body for body, cases in occurrences.items()
            if all(not case["violations_if_K"] for case in cases)
        ]
        body_count = len(cells)
        mark_count = sum(len(c["marks"]) for c in cells)
        result["readers"][edition] = {
            "eligible_groups": len(retained), "excluded_groups": len(excluded),
            "body_tokens": body_count, "body_types": len(occurrences),
            "upper_mark_tokens": mark_count,
            "stack_height_histogram": dict(sorted(Counter(len(c["marks"]) for c in cells).items())),
            "groups_with_marks": sum(any(c["marks"] for c in r["cells"]) for r in retained),
            "observed_legal_empty_carrier_candidates": candidates,
            "conditional_source_letter_counts_if_all_bodies_ordinary": {
                "consonants": body_count, "vowels": mark_count,
                "total": body_count + mark_count,
                "caution": "Hypothetical categories only. No observed body satisfies K rules; an unobserved K remains possible. No language inference.",
            },
            "occurrences_by_body_with_K_countercases": dict(sorted(occurrences.items())),
            "retained": retained, "excluded": excluded,
        }
    target = HERE / "HAND_WRITER_SPATIAL_REVIEW_RESULT_20261005.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        edition: {k: v for k, v in data.items()
                  if k not in {"retained", "excluded", "occurrences_by_body_with_K_countercases"}}
        for edition, data in result["readers"].items()
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
