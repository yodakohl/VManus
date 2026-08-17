#!/usr/bin/env python3
"""Enumerate simple stable f57 decoders and their exact alignment null."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
QUALITY = ROOT / "gdt179_quality_decoder.tsv"
G179 = ROOT / "gdt179_result.json"
G180 = ROOT / "gdt180_result.json"
METHOD = ROOT / "GDT182_F57_DECODER_MULTIPLICITY_METHOD.md"
REPORT = ROOT / "GDT182_F57_DECODER_MULTIPLICITY_REPORT.md"

PREDICATES = ROOT / "gdt182_predicates.tsv"
PAIRS = ROOT / "gdt182_decoder_pairs.tsv"
SHARED = ROOT / "gdt182_shared_predicates.tsv"
NULL = ROOT / "gdt182_permutation_null.tsv"
COUNTER = ROOT / "gdt182_counterexamples.tsv"
RESULT = ROOT / "gdt182_result.json"

POSITIONS = ["NORTHEAST", "SOUTHEAST", "SOUTHWEST", "NORTHWEST"]
EDITIONS = ["ZL3b", "IT2a", "RF1b"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    assert rows
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode()


def variants(surface: str) -> tuple[str, ...]:
    """Expand [a:o]; turn all nonletters into a barrier marker."""
    surface = surface.lower()
    out = [""]
    i = 0
    while i < len(surface):
        if surface[i] == "[":
            j = surface.index("]", i)
            options = surface[i + 1 : j].split(":")
            out = [prefix + option for prefix in out for option in options]
            i = j + 1
        else:
            char = surface[i] if surface[i].isalpha() else "#"
            out = [prefix + char for prefix in out]
            i += 1
    return tuple(out)


def segments(surface: str) -> list[str]:
    return [part for part in surface.split("#") if part]


def candidate_names(values: list[tuple[tuple[str, ...], ...]]) -> set[str]:
    names: set[str] = set()
    for readings in values:
        for expansions in readings:
            for surface in expansions:
                parts = segments(surface)
                if not parts:
                    continue
                for n in (1, 2, 3):
                    if len(parts[0]) >= n:
                        names.add(f"START{n}:{parts[0][:n]}")
                    if len(parts[-1]) >= n:
                        names.add(f"END{n}:{parts[-1][-n:]}")
                    for part in parts:
                        for i in range(len(part) - n + 1):
                            names.add(f"HAS{n}:{part[i:i+n]}")
    return names


def evaluate(name: str, readings: tuple[tuple[str, ...], ...]) -> bool:
    kind = re.match(r"[A-Z]+", name).group(0)
    literal = name.split(":", 1)[1]

    def on_surface(surface: str) -> bool:
        parts = segments(surface)
        if kind == "START":
            return bool(parts) and parts[0].startswith(literal)
        if kind == "END":
            return bool(parts) and parts[-1].endswith(literal)
        return any(literal in part for part in parts)

    return all(on_surface(surface) for expansions in readings for surface in expansions)


def register_features(register: str, quality_rows: list[dict[str, str]]):
    rows = sorted([row for row in quality_rows if row["register"] == register], key=lambda row: POSITIONS.index(row["position"]))
    values = [tuple(variants(row[edition]) for edition in EDITIONS) for row in rows]
    features: dict[str, tuple[int, ...]] = {}
    for name in candidate_names(values):
        mask = tuple(int(evaluate(name, readings)) for readings in values)
        if 0 < sum(mask) < 4:
            features[name] = mask
    masks: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for name, mask in features.items():
        masks[mask].append(name)
    for aliases in masks.values():
        aliases.sort()
    decoder_pairs = []
    for a, b in itertools.combinations(sorted(masks), 2):
        if len({(a[i], b[i]) for i in range(4)}) == 4:
            decoder_pairs.append((a, b))
    return rows, features, masks, decoder_pairs


def mask_text(mask: tuple[int, ...]) -> str:
    return "".join(map(str, mask))


def main() -> None:
    quality = read_tsv(QUALITY)
    assert len(quality) == 8
    g179 = json.loads(G179.read_text())
    g180 = json.loads(G180.read_text())
    assert g179["counts"]["internal_decoder_matches"] == 8
    assert g180["counts"]["relation_matches"] == 5
    assert not g179["f84r_accessed"] and not g180["f84r_accessed"]

    analyses = {register: register_features(register, quality) for register in ("N1", "D1")}

    predicate_rows: list[dict[str, object]] = []
    for register, (_, features, masks, _) in analyses.items():
        for name in sorted(features):
            mask = features[name]
            predicate_rows.append({
                "register":register, "predicate":name, "position_mask_NE_SE_SW_NW":mask_text(mask),
                "support":sum(mask), "alias_count_for_mask":len(masks[mask]),
                "selected_in_gdt179":int((register == "N1" and name in {"START2:ot","END1:y"}) or (register == "D1" and name in {"HAS2:ok","END1:y"})),
            })
    write_tsv(PREDICATES, predicate_rows)

    pair_rows: list[dict[str, object]] = []
    selected_masks = {"N1":{(1,0,0,1),(0,1,0,1)}, "D1":{(0,1,1,0),(0,1,0,1)}}
    for register, (_, _, masks, pairs) in analyses.items():
        for index, (a, b) in enumerate(pairs, 1):
            pair_rows.append({
                "register":register, "decoder_pair_index":index,
                "mask_a":mask_text(a), "aliases_a":"|".join(masks[a]),
                "mask_b":mask_text(b), "aliases_b":"|".join(masks[b]),
                "selected_mask_pair_in_gdt179":int({a,b} == selected_masks[register]),
            })
    write_tsv(PAIRS, pair_rows)

    n_features = analyses["N1"][1]
    d_features = analyses["D1"][1]
    common = sorted(set(n_features) & set(d_features))
    shared_rows = []
    for name in common:
        nmask, dmask = n_features[name], d_features[name]
        shared_rows.append({
            "predicate":name, "N1_mask":mask_text(nmask), "D1_mask":mask_text(dmask),
            "same_mask":int(nmask == dmask), "selected_shared_axis":int(name == "END1:y"),
        })
    write_tsv(SHARED, shared_rows)

    null_rows: list[dict[str, object]] = []
    any_count = 0
    y_count = 0
    for world, permutation in enumerate(itertools.permutations(range(4))):
        equal = [name for name in common if n_features[name] == tuple(d_features[name][i] for i in permutation)]
        any_equal = bool(equal)
        y_equal = "END1:y" in equal
        any_count += int(any_equal)
        y_count += int(y_equal)
        null_rows.append({
            "world":world, "D1_position_permutation":"".join(map(str, permutation)),
            "any_common_literal_equal_mask":int(any_equal),
            "end1_y_equal_mask":int(y_equal), "equal_predicates":"|".join(equal),
            "observed_world":int(permutation == (0,1,2,3)),
        })
    write_tsv(NULL, null_rows)
    assert any_count == 10 and y_count == 4

    counter_rows = [
        {"id":"C1","finding":"N1 has three effective complete decoder-mask pairs; D1 has two.","impact":"A perfect 2x2 fit is not unique inside either exposed register."},
        {"id":"C2","finding":"The selected first coordinates are register-specific and were chosen after the W.73 phase was known.","impact":"Fire- and Water-incidence labels do not supply an independent test."},
        {"id":"C3","finding":"Any common literal shared-mask alignment occurs in 10/24 exact register permutations.","impact":"Search-adjusted p=0.4167; the shared axis is descriptive, not confirmatory."},
        {"id":"C4","finding":"END1:y specifically aligns in 4/24 worlds.","impact":"The narrower p=0.1667 is still weak and is not selection-adjusted."},
        {"id":"C5","finding":"The f77 process fit inherits the exposed N1 state assignment.","impact":"Its 5/5 topology fit remains a generative observation, not an independent semantic replication."},
        {"id":"C6","finding":"No f84r or new target was accessed.","impact":"The surprise target remains outside this audit."},
    ]
    write_tsv(COUNTER, counter_rows)

    outputs = [PREDICATES, PAIRS, SHARED, NULL, COUNTER]
    result = {
        "experiment":"GDT182_F57_DECODER_MULTIPLICITY_AUDIT",
        "status":"LOCAL_F57_DECODER_DESCRIPTIVE_NOT_ABOVE_FEATURE_MULTIPLICITY",
        "registers":{
            register:{"stable_predicates":len(data[1]),"unique_masks":len(data[2]),"complete_decoder_mask_pairs":len(data[3])}
            for register, data in analyses.items()
        },
        "shared_literal_predicates":len(common),
        "shared_equal_mask_predicates":[row["predicate"] for row in shared_rows if row["same_mask"]],
        "exact_null":{
            "worlds":24, "any_common_literal_equal_mask_worlds":any_count,
            "search_adjusted_p":any_count/24, "end1_y_equal_worlds":y_count,
            "end1_y_descriptive_p":y_count/24,
        },
        "semantic_effect":"GDT179 and GDT180 remain useful exposed local scaffolds but lose confirmation-like force; no local bit is promoted to a translated source unit.",
        "inputs":{str(path.relative_to(ROOT)):sha(path) for path in [QUALITY,G179,G180,METHOD]},
        "outputs":{path.name:sha(path) for path in outputs},
        "documents":{path.name:sha(path) for path in [METHOD,REPORT]},
        "implementation":sha(Path(__file__).resolve()),
        "f84r_accessed":False,
        "claim_ceiling":"A multiplicity correction for the exposed f57 two-register decoder. It does not invalidate the page-role analogy, but it prevents treating the 8/8 fit or shared terminal-y axis as confirmed semantics, words, or plaintext.",
    }
    RESULT.write_bytes(canonical(result))
    print(json.dumps({"status":result["status"], **result["exact_null"]}, sort_keys=True))


if __name__ == "__main__":
    main()
