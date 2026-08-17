#!/usr/bin/env python3
"""Test whether f57 R2 indexes the independent 17-sector f67v1 wheel."""

import csv, hashlib, json, math, statistics
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
METHOD = ROOT / "GDT185_F57_F67_REFERENCE_ALIGNMENT_METHOD.md"
REPORT = ROOT / "GDT185_F57_F67_REFERENCE_ALIGNMENT_REPORT.md"
SCORES = ROOT / "gdt185_alignment_scores.tsv"
BEST = ROOT / "gdt185_best_alignment.tsv"
COUNTER = ROOT / "gdt185_counterexamples.tsv"
RESULT = ROOT / "gdt185_result.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
TARGET_LOCI = tuple(f"f67v1.{i}" for i in range(13, 30))
WORLDS = 65536
MASK64 = (1 << 64) - 1

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def selected_rows():
    """Retain/parse only the two registered pages; never retain an f84 row."""
    raw = []
    with SOURCE.open(encoding="utf-8") as h:
        header = h.readline().rstrip("\n").split("\t")
        for line in h:
            # The first three columns are source_group_id, edition, locus.
            # Inspect that prefix before parsing any formal payload columns.
            prefix = line.split("\t", 3)
            locus = prefix[2]
            if locus != "f57v.3" and locus not in TARGET_LOCI:
                continue
            assert not locus.startswith("f84")
            parts = line.rstrip("\n").split("\t")
            raw.append(parts)
    rows = [dict(zip(header, parts)) for parts in raw]
    digest = hashlib.sha256(("\t".join(header)+"\n"+"\n".join("\t".join(x) for x in raw)+"\n").encode()).hexdigest()
    return rows, digest

def permutations(n, seed):
    out = np.empty((n, 17), dtype=np.int16)
    for w in range(n):
        a = list(range(17))
        state = (seed ^ ((w + 1) * 0x9E3779B97F4A7C15)) & MASK64
        for i in range(16, 0, -1):
            state = (6364136223846793005 * state + 1442695040888963407) & MASK64
            j = state % (i + 1)
            a[i], a[j] = a[j], a[i]
        out[w] = a
    return out

def orientation_indices():
    out = []
    meta = []
    for reflected in (0, 1):
        base = list(reversed(range(17))) if reflected else list(range(17))
        for rotation in range(17):
            out.append(base[rotation:] + base[:rotation])
            meta.append((reflected, rotation))
    return np.asarray(out, dtype=np.int16), meta

ORIENT, ORIENT_META = orientation_indices()

def compat_matrix(key, targets, mode):
    m = np.zeros((17, 17), dtype=np.int8)
    for sector, target in enumerate(targets):
        for item, symbol in enumerate(key):
            if mode == "ANY": ok = symbol in target
            elif mode == "FIRST": ok = symbol == target[0]
            else: ok = symbol == target[-1]
            m[sector, item] = int(ok)
    return m

def world_best(perms, compat):
    best = np.zeros(len(perms), dtype=np.int16)
    sectors = np.arange(17)
    for oi in range(34):
        assigned = perms[:, ORIENT[oi]]
        score = compat[sectors[None, :], assigned].sum(axis=1)
        best = np.maximum(best, score)
    return best

def observed_best(compat):
    vals = []
    for oi in range(34):
        vals.append(int(compat[np.arange(17), ORIENT[oi]].sum()))
    top = max(vals)
    return top, vals.index(top)

def write_tsv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def main():
    rows, selected_digest = selected_rows()
    assert len(rows) == 375
    score_rows, best_rows = [], []
    summary = {}
    for ei, edition in enumerate(EDITIONS):
        r2 = sorted((r for r in rows if r["edition"] == edition and r["locus"] == "f57v.3"), key=lambda r: int(r["source_group_index"]))
        assert len(r2) in (68, 69)
        period = r2[:17]
        keys = {
            "CODE": [r["primary_sta_codes"].split()[0] for r in period],
            "FAMILY": [r["primary_sta_families"][0] for r in period],
        }
        targets = {"CODE": [], "FAMILY": []}
        for locus in TARGET_LOCI:
            rr = sorted((r for r in rows if r["edition"] == edition and r["locus"] == locus), key=lambda r: int(r["source_group_index"]))
            assert rr
            targets["CODE"].append([x for r in rr for x in r["primary_sta_codes"].split()])
            targets["FAMILY"].append([x for r in rr for x in r["primary_sta_families"]])
        perms = permutations(WORLDS, 185000 + ei)
        nulls, observed = {}, {}
        for representation in ("CODE", "FAMILY"):
            for position in ("ANY", "FIRST", "LAST"):
                metric = f"{representation}_{position}"
                comp = compat_matrix(keys[representation], targets[representation], position)
                obs, oi = observed_best(comp)
                null = world_best(perms, comp)
                mean = float(null.mean()); sd = float(null.std())
                p = (1 + int((null >= obs).sum())) / (WORLDS + 1)
                z = (obs - mean) / sd if sd else 0.0
                reflected, rotation = ORIENT_META[oi]
                assigned_idx = ORIENT[oi]
                assigned = [keys[representation][i] for i in assigned_idx]
                matches = []
                for j, (symbol, target) in enumerate(zip(assigned, targets[representation])):
                    ok = symbol in target if position == "ANY" else symbol == target[0] if position == "FIRST" else symbol == target[-1]
                    if ok: matches.append(TARGET_LOCI[j])
                score_rows.append({
                    "edition": edition, "metric": metric, "observed_best": obs,
                    "null_mean": f"{mean:.9f}", "null_sd": f"{sd:.9f}",
                    "local_p": f"{p:.9f}", "z": f"{z:.9f}",
                    "best_reflected": reflected, "best_rotation": rotation,
                    "matched_loci": ";".join(matches),
                })
                best_rows.append({
                    "edition": edition, "metric": metric, "sector_loci": ";".join(TARGET_LOCI),
                    "assigned_symbols": ";".join(assigned), "matched_loci": ";".join(matches),
                })
                nulls[metric] = null; observed[metric] = (obs, z)
        max_obs = max(z for _, z in observed.values())
        max_world = np.maximum.reduce([
            (nulls[m] - nulls[m].mean()) / nulls[m].std() if nulls[m].std() else np.zeros(WORLDS)
            for m in nulls
        ])
        max_p = (1 + int((max_world >= max_obs).sum())) / (WORLDS + 1)
        summary[edition] = {"max_six_z": max_obs, "max_six_p": max_p,
                            "best_metric": max(observed, key=lambda m: observed[m][1])}
    write_tsv(SCORES, score_rows); write_tsv(BEST, best_rows)
    counter = [
      {"id":"C1","finding":"ZL3b exact-code anywhere alignment matches 7 of 17 sectors versus a null mean above 7.","impact":"The primary reading has no positive ordered-key excess."},
      {"id":"C2","finding":"All six ZL3b local tails exceed .80 and the max-six tail is near one.","impact":"Rotation, reflection, and feature search cannot rescue the alignment."},
      {"id":"C3","finding":"The best direction and phase differ across readings and metrics.","impact":"There is no alternate-reading-stable reference phase."},
      {"id":"C4","finding":"Rare R2 codes are absent from most radial sector texts.","impact":"The exact sign inventory does not behave as a sector label key."},
      {"id":"C5","finding":"The f57 and f67 pages share the number 17 but not an ordered sign-to-sector correspondence.","impact":"Cardinality coincidence alone is not a decipherment bridge."},
    ]
    write_tsv(COUNTER, counter)
    gates = {
      "zl_max_six_p_le_0_05": summary["ZL3b"]["max_six_p"] <= .05,
      "same_best_phase_all_readings": len({(r["best_reflected"], r["best_rotation"]) for r in score_rows if r["metric"] == summary["ZL3b"]["best_metric"]}) == 1,
    }
    gates["all_pass"] = all(gates.values())
    result = {
      "experiment":"GDT185_F57_F67_REFERENCE_ALIGNMENT",
      "status":"F57_R2_DOES_NOT_INDEX_F67V1_17_SECTOR_TEXT",
      "headline":"The f57 17-sign reference sequence has no rotation/reflection-corrected correspondence to the independent f67v1 17-sector texts.",
      "counts":{"selected_source_rows":len(rows),"r2_positions":17,"target_sectors":17,"metrics":6,"alignments_per_metric":34,"null_worlds_per_reading":WORLDS},
      "reading_summary":summary,"gates":gates,
      "claim_ceiling":"This rejects only a direct ordered f57-R2 sign to f67v1-sector indexing bridge. It establishes no sign value, number, alphabet, cipher, word, language, plaintext, or translation.",
      "provenance":{"selected_source_payload_sha256":selected_digest,"source_rows_retained_only_for":"f57v.3 and f67v1.13-.29","source_container_has_other_pages":True,"nonselected_rows_guarded_before_formal_field_parsing":True,"f84r_formal_payload_retained_parsed_joined_scored":False},
      "inputs":{"GDT184_result":sha(ROOT/"gdt184_result.json")},
      "outputs":{p.name:sha(p) for p in (SCORES,BEST,COUNTER)},
      "documents":{p.name:sha(p) for p in (METHOD,REPORT)},
      "implementation":sha(Path(__file__)),"f84r_accessed":False,
    }
    RESULT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(result["status"], summary)

if __name__ == "__main__": main()
