#!/usr/bin/env python3
"""Compete the three perfect f57 N1 decoders on held-folio line ordering."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
DECODERS = ROOT / "gdt182_decoder_pairs.tsv"
METHOD = ROOT / "GDT197_F77_DECODER_GLOBAL_COMPETITION_METHOD.md"
REPORT = ROOT / "GDT197_F77_DECODER_GLOBAL_COMPETITION_REPORT.md"
SCORES = ROOT / "gdt197_decoder_scores.tsv"
FOLDS = ROOT / "gdt197_folio_contributions.tsv"
NULL = ROOT / "gdt197_order_null.tsv"
COUNTER = ROOT / "gdt197_counterexamples.tsv"
RESULT = ROOT / "gdt197_result.json"
WORLDS = 4096
SEED = 197197
CANDIDATES = (
    ("AL_Y", "HAS2:al", "END1:y", 0),
    ("AL_OT", "HAS2:al", "START2:ot", 0),
    ("Y_OT", "END1:y", "START2:ot", 1),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def predicate(token: str, name: str) -> int:
    if name == "HAS2:al": return int("al" in token)
    if name == "END1:y": return int(token.endswith("y"))
    if name == "START2:ot": return int(token.startswith("ot"))
    raise KeyError(name)


def state(token: str, left: str, right: str) -> int:
    return 2 * predicate(token, left) + predicate(token, right)


def train(sequences: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    unigram = np.full(4, .5)
    transition = np.full((5, 4), .5)
    for seq in sequences:
        for value in seq: unigram[int(value)] += 1
        previous = 4
        for value in seq:
            transition[previous, int(value)] += 1
            previous = int(value)
    return -np.log2(unigram / unigram.sum()), -np.log2(transition / transition.sum(axis=1, keepdims=True))


def costs(seq: np.ndarray, model: tuple[np.ndarray, np.ndarray]) -> tuple[float, float]:
    uni, trans = model
    u = float(uni[seq].sum())
    previous = np.r_[4, seq[:-1]]
    m = float(trans[previous, seq].sum())
    return u, m


def main() -> None:
    rows = [r for r in read(SOURCE) if not r["page"].startswith("f84")]
    assert not any(r["locus"].startswith("f84") for r in rows)
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows: by_line[row["locus"]].append(row)
    lines = []
    for locus, group in by_line.items():
        group.sort(key=lambda r: int(r["group_index"]))
        if len(group) != int(group[0]["group_count"]): continue
        lines.append({"locus": locus, "folio": group[0]["physical_folio"], "section": group[0]["section"], "rows": group})
    lines.sort(key=lambda x: x["locus"])
    folios = sorted({x["folio"] for x in lines})
    events = sum(len(x["rows"]) for x in lines)
    assert len(lines) == 1169 and events == 8641 and len(folios) == 91

    frozen = [r for r in read(DECODERS) if r["register"] == "N1"]
    assert len(frozen) == 3 and sum(int(r["selected_mask_pair_in_gdt179"]) for r in frozen) == 1
    sequences: dict[str, list[np.ndarray]] = {}
    models: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    observed: dict[str, dict[str, float]] = {}
    fold_rows: list[dict[str, object]] = []
    section_gain: dict[str, Counter[str]] = defaultdict(Counter)

    for name, left, right, selected in CANDIDATES:
        seqs = [np.asarray([state(r["token"], left, right) for r in line["rows"]], dtype=np.int8) for line in lines]
        sequences[name] = seqs
        total_u = total_m = 0.0
        per_folio: dict[str, tuple[float, float]] = {}
        for folio in folios:
            train_sequences = [seq for seq, line in zip(seqs, lines) if line["folio"] != folio]
            model = train(train_sequences); models[name, folio] = model
            fu = fm = 0.0
            for seq, line in zip(seqs, lines):
                if line["folio"] != folio: continue
                u, m = costs(seq, model); fu += u; fm += m
                section_gain[name][line["section"]] += u - m
            per_folio[folio] = (fu, fm); total_u += fu; total_m += fm
            fold_rows.append({"candidate": name, "selected_gdt179": selected, "held_folio": folio,
                              "held_lines": sum(line["folio"] == folio for line in lines),
                              "held_groups": sum(len(line["rows"]) for line in lines if line["folio"] == folio),
                              "unigram_bits": fu, "markov_bits": fm, "order_gain_bits": fu - fm})
        observed[name] = {"unigram_bits": total_u, "markov_bits": total_m,
                          "gain_bits": total_u - total_m,
                          "positive_folios": sum(u - m > 0 for u, m in per_folio.values()),
                          "minimum_leave_one_folio_gain": min(total_u - total_m - (u - m) for u, m in per_folio.values())}

    rng = np.random.default_rng(SEED)
    world_mark = {name: np.zeros(WORLDS) for name, *_ in CANDIDATES}
    for index, line in enumerate(lines):
        n = len(line["rows"])
        permutations = np.argsort(rng.random((WORLDS, n)), axis=1)
        folio = line["folio"]
        for name, *_ in CANDIDATES:
            seq = sequences[name][index]
            permuted = seq[permutations]
            _, trans = models[name, folio]
            world_mark[name] += trans[4, permuted[:, 0]]
            if n > 1:
                world_mark[name] += trans[permuted[:, :-1], permuted[:, 1:]].sum(axis=1)

    world_gain = {name: observed[name]["unigram_bits"] - world_mark[name] for name, *_ in CANDIDATES}
    means = {name: float(world_gain[name].mean()) for name, *_ in CANDIDATES}
    sds = {name: float(world_gain[name].std(ddof=1)) for name, *_ in CANDIDATES}
    zs = {name: (observed[name]["gain_bits"] - means[name]) / sds[name] for name, *_ in CANDIDATES}
    world_z = {name: (world_gain[name] - means[name]) / sds[name] for name, *_ in CANDIDATES}
    max_world = np.maximum.reduce([world_z[name] for name, *_ in CANDIDATES])
    max_p = {name: (1 + int((max_world >= zs[name] - 1e-12).sum())) / (WORLDS + 1) for name, *_ in CANDIDATES}
    local_p = {name: (1 + int((world_gain[name] >= observed[name]["gain_bits"] - 1e-12).sum())) / (WORLDS + 1) for name, *_ in CANDIDATES}
    ranking = sorted((zs[name], name) for name, *_ in CANDIDATES)[::-1]
    paired_z_gap = zs["AL_Y"] - zs["Y_OT"]
    paired_world_gap = world_z["AL_Y"] - world_z["Y_OT"]
    paired_gap_p = (1 + int((np.abs(paired_world_gap) >= abs(paired_z_gap) - 1e-12).sum())) / (WORLDS + 1)

    score_rows = []
    for name, left, right, selected in CANDIDATES:
        counts = Counter(int(x) for seq in sequences[name] for x in seq)
        score_rows.append({"candidate": name, "predicate_a": left, "predicate_b": right,
                           "selected_gdt179": selected, "lines": len(lines), "groups": events,
                           "state_00": counts[0], "state_01": counts[1], "state_10": counts[2], "state_11": counts[3],
                           **observed[name], "gain_per_group": observed[name]["gain_bits"] / events,
                           "null_mean_gain": means[name], "null_sd_gain": sds[name], "observed_z": zs[name],
                           "local_p": local_p[name], "max_three_p": max_p[name],
                           "rank_by_z": next(i + 1 for i, (_, candidate) in enumerate(ranking) if candidate == name),
                           "section_gains": json.dumps(dict(sorted(section_gain[name].items())), sort_keys=True)})
    write(SCORES, score_rows, list(score_rows[0]))
    write(FOLDS, fold_rows, list(fold_rows[0]))
    null_rows = [{"candidate": name, "worlds": WORLDS, "seed": SEED, "null_mean_gain": means[name],
                  "null_sd_gain": sds[name], "observed_gain": observed[name]["gain_bits"],
                  "observed_z": zs[name], "local_p": local_p[name], "max_three_p": max_p[name],
                  "preserves": "exact line state multiset;line length;folio;section;candidate support"}
                 for name, *_ in CANDIDATES]
    write(NULL, null_rows, list(null_rows[0]))

    selected = next(r for r in score_rows if r["candidate"] == "Y_OT")
    winner = min(score_rows, key=lambda r: int(r["rank_by_z"]))
    wins = int(selected["rank_by_z"]) == 1 and float(selected["max_three_p"]) <= .05 and float(selected["minimum_leave_one_folio_gain"]) > 0
    status = "EXPOSED_OT_Y_DECODER_WINS_GLOBAL_SEQUENCE_COMPETITION" if wins else "TERMINAL_Y_SEQUENCE_SIGNAL_NOT_UNIQUE_OT_AXIS_NOT_SELECTED"
    counters = [
        {"counterexample_id": "C01", "finding": f"Selected Y_OT ranks {selected['rank_by_z']}/3; {winner['candidate']} has the largest global order z.", "impact": "Global record order does not uniquely select the exposed ot axis."},
        {"counterexample_id": "C02", "finding": "All three candidates were perfect only on four exposed f57 labels.", "impact": "Local 2x2 completeness remains high-multiplicity."},
        {"counterexample_id": "C03", "finding": "State frequencies differ strongly among candidates.", "impact": "Compare standardized order tails, not raw gain alone."},
        {"counterexample_id": "C04", "finding": "The test uses formal line order, not external content or readable semantics.", "impact": "Even a winning decoder would remain anonymous."},
        {"counterexample_id": "C05", "finding": "GDT196 found only one exact f77 diagram-label echo in page prose.", "impact": "No label dictionary is available to name the global states."},
    ]
    write(COUNTER, counters, list(counters[0]))

    report = f"""# GDT197 — the exposed `ot` + terminal-`y` decoder does not win globally

## Outcome

**{status}**

The complete non-`f84*` strict corpus supplies **{len(lines):,} complete
physical lines**, **{events:,} groups**, and **{len(folios)} physical folios**.
Each of the three decoder pairs that perfectly fit the exposed f57 N1 labels
was evaluated under identical whole-folio holdout and 4,096 within-line order
worlds.

| decoder | predicates | held gain | bits/group | z | local p | max-three p | z rank | positive folios |
|---|---|---:|---:|---:|---:|---:|---:|---:|
""" + "".join(
        f"| `{r['candidate']}` | `{r['predicate_a']}` + `{r['predicate_b']}` | {float(r['gain_bits']):+.3f} | {float(r['gain_per_group']):+.5f} | {float(r['observed_z']):+.3f} | {float(r['local_p']):.5f} | {float(r['max_three_p']):.5f} | {r['rank_by_z']} | {r['positive_folios']}/91 |\n"
        for r in score_rows
    ) + f"""

The selected `Y_OT` pair is rank **{selected['rank_by_z']}/3**.  The winner is
`{winner['candidate']}`, which replaces the chosen `ot` axis with the equally
perfect local `al` predicate.  The exact numerical order signal is real only
as anonymous surface-state regularity; it does not choose the f77 quality
decoder.  The standardized lead of `AL_Y` over `Y_OT` is only
{paired_z_gap:+.3f}; its paired two-sided shuffle tail is **p={paired_gap_p:.4f}**.
Thus the ranking itself is not a stable preference for `al`; the decisive fact
is that the globally strong order signal fails to distinguish the two.

## Consequence

Terminal `y` remains an unusually useful formal axis because both strongest
global pairs contain it.  What fails is the stronger claim that initial `ot`
is selected as the complementary state coordinate.  The GDT179/GDT180
COLD/DRY/HOT/MOIST display remains an economical local narrative, but global
record ordering does not disambiguate it from the alternative shallow
decoder already exposed by GDT182.

No state is assigned a quality, word, sound, language, plaintext value, or
meaning.  `f84r` and all other `f84*` rows were rejected before retention and
scoring.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT197_F77_DECODER_GLOBAL_COMPETITION_RESULT_V1", "status": status,
        "complete_lines": len(lines), "groups": events, "folios": len(folios), "worlds": WORLDS,
        "selected_candidate": "Y_OT", "winning_candidate": winner["candidate"],
        "selected_rank": selected["rank_by_z"], "selected_max_three_p": selected["max_three_p"],
        "al_y_minus_y_ot_observed_z_gap": paired_z_gap, "paired_gap_two_sided_p": paired_gap_p,
        "interpretation": "Global line-order regularity does not uniquely select initial ot as the complement to terminal y.",
        "claim_ceiling": "Anonymous shallow-predicate line-order competition only; no quality, word, morpheme, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False},
        "inputs": {SOURCE.name: sha(SOURCE), DECODERS.name: sha(DECODERS),
                   "gdt182_result.json": sha(ROOT / "gdt182_result.json"),
                   "gdt196_result.json": sha(ROOT / "gdt196_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {SCORES.name: sha(SCORES), FOLDS.name: sha(FOLDS), NULL.name: sha(NULL), COUNTER.name: sha(COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "winner": winner["candidate"], "selected_rank": selected["rank_by_z"],
                      "selected_max_p": selected["max_three_p"]}, sort_keys=True))


if __name__ == "__main__": main()
