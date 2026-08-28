#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
ART = EXP / "artifacts"
SPLITS = ART / "reference_splits"

INPUTS = {
    "merge_tree": (
        ROOT / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv",
        "2098c71be9da13b483cf2561e06412276d8c60aa32e72520e8877f8f5d53090a",
    ),
    "model": (
        ROOT / "experiments/yolo/gdt609_historical_mixed_abbreviation_prior/artifacts/model_v1.json",
        "0c9219bd02e063758806b58a174cbf546fdf0f3c5853ed3c98dcfa422abbe5f0",
    ),
    "latin": (
        ROOT / "experiments/yolo/gdt612_historical_fst34_target_attack/artifacts/latin_real_words.txt",
        "82adaef7c8fa937e90a376a24a2cfce171150b1ef33f83f6585809d83dda3f26",
    ),
    "units": (
        ROOT / "experiments/yolo/gdt612_historical_fst34_target_attack/artifacts/units.tsv",
        "8fc32a38dbe47a5d738698ccccd7289fe3d533e9e5d870624da11f0fc5d19180",
    ),
    "primitives": (
        ROOT / "experiments/yolo/gdt612_historical_fst34_target_attack/artifacts/primitives.tsv",
        "3a5e89dbd89c5c833db4884cadff0ccbdc438e9ce8e832be0bc1b7e3df636ae6",
    ),
}

LENGTHS = {
    "literal_carrier": [1] * 18,
    "syllabic_carrier": [1, 2, 2, 3],
    "prefix_operator": [1, 2, 3],
    "suffix_operator": [1, 2, 3],
    "connector": [1, 2],
    "context_abbreviation_mark": [1, 2],
    "wholeform_logogram": [4],
    "null_layout": [0],
}
OVERRIDE_LENGTHS = {
    "short": [2, 2, 3, 3],
    "wholeform": [3, 4, 5, 6],
}
SPLIT_NAMES = ("lm_fit", "lm_confirm", "synthetic_train", "synthetic_held")
SPLIT_FRACTIONS = (0.40, 0.20, 0.30, 0.10)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def token_windows(words, width=8):
    return {tuple(words[index:index + width]) for index in range(len(words) - width + 1)}


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    SPLITS.mkdir(parents=True, exist_ok=True)
    for name, (path, expected) in INPUTS.items():
        observed = sha256(path)
        if observed != expected:
            raise RuntimeError(f"input drift {name}: {observed}")

    model = json.loads(INPUTS["model"][0].read_text(encoding="utf-8"))
    if model["model_id"] != "HISTORICAL_MIXED_ABBREVIATION_FST_34_V1":
        raise RuntimeError("unexpected model id")
    buckets = {
        row["role"]: int(row["count"])
        for row in model["primitive_capacity"]["buckets"]
    }
    expected_buckets = {role: len(lengths) for role, lengths in LENGTHS.items()}
    if buckets != expected_buckets or sum(buckets.values()) != 34:
        raise RuntimeError(f"capacity mismatch: {buckets}")
    if model["frequent_compounds"]["observed_merge_nodes"] != 64:
        raise RuntimeError("model does not bind 64 merge nodes")
    if model["frequent_compounds"]["lexicalized_override_max"] != 8:
        raise RuntimeError("model does not bind eight cards")
    if model["frequent_compounds"]["wholeform_override_max"] != 4:
        raise RuntimeError("model does not bind four whole cards")

    units = read_tsv(INPUTS["units"][0])
    primitives = read_tsv(INPUTS["primitives"][0])
    if len(units) != 98 or len(primitives) != 34:
        raise RuntimeError("unexpected unit inventory")
    merges = [row for row in units if row["is_primitive"] == "0"]
    if len(merges) != 64:
        raise RuntimeError("unexpected merge inventory")
    unit_by_name = {row["unit"]: row for row in units}
    merge_source = read_tsv(INPUTS["merge_tree"][0])
    if len(merge_source) != 64:
        raise RuntimeError("unexpected GDT608 merge source")
    compiled_merges = []
    for source in merge_source:
        target = unit_by_name.get(source["merged"])
        if target is None or target["is_primitive"] != "0":
            raise RuntimeError(f"missing compiled merge {source['merged']}")
        left = units[int(target["left_unit_id"])]["unit"]
        right = units[int(target["right_unit_id"])]["unit"]
        if (
            left != source["left"]
            or right != source["right"]
            or int(target["merge_rank"]) != int(source["rank"])
            or target["leaves"].replace(",", " ") != source["leaf_sequence"]
        ):
            raise RuntimeError(f"merge-tree mismatch {source['merged']}")
        compiled_merges.append(
            {
                "rank": int(source["rank"]),
                "unit_id": int(target["unit_id"]),
                "unit": source["merged"],
                "left_unit_id": int(target["left_unit_id"]),
                "left": left,
                "right_unit_id": int(target["right_unit_id"]),
                "right": right,
                "leaves": source["leaf_sequence"].split(),
            }
        )
    qok_family = sorted(row["unit"] for row in units if row["unit"].startswith("qok"))

    primitive_cards = []
    for role, lengths in LENGTHS.items():
        for ordinal, length in enumerate(lengths, 1):
            primitive_cards.append(
                {
                    "card_id": f"{role}:{ordinal}",
                    "role": role,
                    "output_length": length,
                }
            )
    override_cards = []
    for kind, lengths in OVERRIDE_LENGTHS.items():
        for ordinal, length in enumerate(lengths, 1):
            override_cards.append(
                {
                    "card_id": f"{kind}:{ordinal}",
                    "type": kind,
                    "output_length": length,
                }
            )

    compiled = {
        "schema": "gdt613-compiled-fst34-v1",
        "source_model_id": model["model_id"],
        "source_model_sha256": INPUTS["model"][1],
        "primitive_cards": primitive_cards,
        "override_cards": override_cards,
        "override_transitions": {
            "short": "syllabic_carrier",
            "wholeform": "wholeform_logogram",
            "note": "GDT609 defines paid nonwhole residual cards but not a separate FST state; GDT613 types each nonwhole card as one CORE syllabic carrier.",
        },
        "grammar": model["composition"],
        "null_policy": model["null_policy"],
        "frequent_compounds": model["frequent_compounds"],
        "structural_anchor_priors": model["structural_anchor_priors"],
        "qok_family": qok_family,
        "unit_count": len(units),
        "merge_count": len(merges),
        "merges": compiled_merges,
    }
    (ART / "compiled_model.json").write_text(
        json.dumps(compiled, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (ART / "length_card_profile.json").write_text(
        json.dumps(
            {
                "primitive": LENGTHS,
                "override": OVERRIDE_LENGTHS,
                "primitive_card_count": len(primitive_cards),
                "override_card_count": len(override_cards),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    words = INPUTS["latin"][0].read_text(encoding="ascii").splitlines()
    total = len(words)
    cuts = [0, round(0.40 * total), round(0.60 * total), round(0.90 * total), total]
    partitions = {
        name: words[cuts[index]:cuts[index + 1]]
        for index, name in enumerate(SPLIT_NAMES)
    }
    windows = {name: token_windows(values) for name, values in partitions.items()}
    overlaps = {
        f"{left}__{right}": len(windows[left] & windows[right])
        for left, right in combinations(SPLIT_NAMES, 2)
    }
    if any(overlaps.values()):
        raise RuntimeError(f"eight-token split overlap: {overlaps}")

    rows = []
    for name in SPLIT_NAMES:
        path = SPLITS / f"{name}.txt"
        path.write_text("\n".join(partitions[name]) + "\n", encoding="ascii")
        rows.append(
            {
                "partition": name,
                "start_token": cuts[SPLIT_NAMES.index(name)],
                "end_token_exclusive": cuts[SPLIT_NAMES.index(name) + 1],
                "tokens": len(partitions[name]),
                "types": len(set(partitions[name])),
                "letters": sum(map(len, partitions[name])),
                "sha256": sha256(path),
            }
        )
    with (ART / "reference_split_manifest.tsv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "schema": "gdt613-prepared-v1",
        "input_hashes": {
            path.relative_to(ROOT).as_posix(): expected
            for path, expected in INPUTS.values()
        },
        "reference_tokens": total,
        "split_fractions": dict(zip(SPLIT_NAMES, SPLIT_FRACTIONS)),
        "split_token_cuts": cuts,
        "eight_token_window_overlaps": overlaps,
        "primitive_cards": len(primitive_cards),
        "override_cards": len(override_cards),
        "qok_family": qok_family,
    }
    (ART / "PREPARED_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
