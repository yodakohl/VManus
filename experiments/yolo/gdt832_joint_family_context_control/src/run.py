#!/usr/bin/env python3
"""Train-only orchestration; never opens source truth or held ciphertext."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys

EXP = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def save(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def code_number(code: str) -> int:
    if len(code) != 3 or code[0] not in "LSW" or not code[1:].isdigit():
        raise ValueError("invalid control atom")
    k = int(code[1:])
    count = {"L": 26, "S": 4, "W": 8}[code[0]]
    if not 0 <= k < count:
        raise ValueError("control atom outside fixed inventory")
    return {"L": 0, "S": 26, "W": 30}[code[0]] + k


def source_families(types):
    """Raw atom equality only; no key or role-derived stem."""
    groups = defaultdict(list)
    for i, word in enumerate(types):
        if len(word) >= 4:
            groups[word[:-1]].append(i)
    pairs = []
    for prefix in sorted(groups):
        pairs.extend(combinations(groups[prefix], 2))
    degree = Counter(x for pair in pairs for x in pair)
    return [(a, b, 1.0 / max(degree[a], degree[b])) for a, b in sorted(pairs)]


def projection(discovery: Path, candidates: dict, output: Path) -> dict:
    if "discovery" not in discovery.name or "held" in discovery.name:
        raise ValueError("fitter accepts discovery-only named input")
    data = json.loads(discovery.read_text())
    if data.get("split") != "discovery":
        raise ValueError("non-discovery payload refused")
    paras = []
    for para in data["paragraphs"]:
        words = [tuple(code_number(c) for c in word) for word in para["words"]]
        if not words or any(not w for w in words):
            raise ValueError("empty control paragraph or word")
        paras.append(words)
    counts = Counter(w for para in paras for w in para)
    types = sorted(counts)
    ids = {word: i for i, word in enumerate(types)}
    transitions = Counter((ids[a], ids[b]) for para in paras for a, b in zip(para, para[1:]))
    families = source_families(types)
    suffixes, wholes = candidates["suffix_pool"], candidates["wholeword_pool"]
    lines = [f"SUFFIX {len(suffixes)}", *suffixes, f"WHOLE {len(wholes)}", *wholes, f"WORDS {len(types)}"]
    lines += [f"{counts[w]} {len(w)} " + " ".join(map(str, w)) for w in types]
    lines += [f"TRANSITIONS {len(transitions)}"]
    lines += [f"{a} {b} {n}" for (a, b), n in sorted(transitions.items())]
    lines += [f"FAMILIES {len(families)}"]
    lines += [f"{a} {b} {weight:.17g}" for a, b, weight in families]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n")
    return {"paragraphs": len(paras), "word_occurrences": sum(counts.values()),
            "word_types": len(types), "source_family_edges": len(families),
            "projection_sha256": digest(output), "discovery_input_sha256": digest(discovery)}


def parse_cpp(path: Path):
    key, score, proposals = {}, None, None
    for line in path.read_text().splitlines():
        parts = line.split("\t")
        if parts[0] == "SCORE":
            score = dict(zip(["total_nats", "language_nats", "family_nats"], map(float, parts[1:])))
        elif parts[0] == "PROPOSALS":
            proposals = int(parts[1])
        else:
            code_number(parts[0])
            if parts[0] in key:
                raise ValueError("duplicate result key entry")
            key[parts[0]] = parts[1]
    if len(key) != 38 or score is None or proposals is None:
        raise ValueError("incomplete C++ result")
    return key, score, proposals


def fit_job(job: dict) -> str:
    raw = Path(job["raw_output"])
    args = [job["binary"], job["model"], job["projection"], job["arm"], str(job["seed"]),
            str(job["start"]), str(job["steps"]), str(job["sweeps"]), str(raw)]
    subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    key, objective, proposals = parse_cpp(raw)
    result = {name: job[name] for name in ["world_id", "condition", "arm", "seed", "start"]}
    result.update({"schema": "GDT832_FIT_V1", "key": key, "discovery_objective": objective,
                   "proposals": proposals, "input_hashes": job["input_hashes"]})
    save(Path(job["output"]), result)
    return job["output"]


def lock_fits(spec: dict) -> dict:
    restart_paths, selected_paths = [], []
    for world in spec["world_ids"]:
        for condition, arms in [("real", spec["real_arms"]), ("pseudo", spec["pseudo_arms"])]:
            for arm in arms:
                paths = [EXP / "artifacts" / "fits" / f"world_{world}_{condition}_{arm}_start{start}.json"
                         for start in spec["starts"]]
                runs = [(json.loads(path.read_text()), path) for path in paths]
                best, _ = min(runs, key=lambda item: (-item[0]["discovery_objective"]["total_nats"], item[0]["start"]))
                selected = EXP / "artifacts" / "fits" / f"world_{world}_{condition}_{arm}_selected.json"
                save(selected, best)
                restart_paths.extend(path.relative_to(EXP).as_posix() for path in paths)
                selected_paths.append(selected.relative_to(EXP).as_posix())
    all_paths = sorted(restart_paths + selected_paths)
    lock = {"schema": "GDT832_FIT_LOCK_V1", "restarts": sorted(restart_paths), "selected": sorted(selected_paths),
            "sha256": {path: digest(EXP / path) for path in all_paths},
            "spec_sha256": digest(EXP / "src" / "SPEC.json"),
            "claim": "Complete discovery-only fit set fixed before key/plaintext evaluation"}
    save(EXP / "artifacts" / "FIT_LOCK.json", lock)
    return lock


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fit", action="store_true")
    parser.add_argument("--check", action="store_true", help="check fitted bytes without truth access")
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--runtime", type=Path, default=EXP / "runtime")
    args = parser.parse_args()
    spec = json.loads((EXP / "src" / "SPEC.json").read_text())
    lock_path = EXP / "artifacts" / "FIT_LOCK.json"
    if args.check:
        lock = json.loads(lock_path.read_text())
        assert lock["spec_sha256"] == digest(EXP / "src" / "SPEC.json")
        assert len(lock["restarts"]) == 120 and len(lock["selected"]) == 15
        for path, expected in lock["sha256"].items():
            assert digest(EXP / path) == expected, path
        print("FIT_LOCK_PASS; no plaintext, held data or key truth opened")
        return 0
    if not args.fit:
        parser.error("choose --fit or --check")
    if lock_path.exists():
        raise RuntimeError("fit set already locked; refuse overwrite/reselection")
    registration = json.loads((EXP / "src" / "PREREG_LOCK.json").read_text())
    for path, expected in registration["sha256"].items():
        if digest(EXP / path) != expected:
            raise RuntimeError(f"registration hash mismatch: {path}")
    capacity = json.loads((EXP / "prepared" / "ACTIVE_RULE_CAPACITY.json").read_text())
    if capacity.get("status") != "ACTIVE_RULE_SOURCE_CAPACITY_PASS":
        raise RuntimeError("source capacity gate has not passed")
    runtime = args.runtime.resolve()
    runtime.mkdir(parents=True, exist_ok=True)
    model = runtime / "reference_model"
    subprocess.run([sys.executable, str(EXP / "src" / "reference_model.py"), "--reference",
                    str(EXP / "prepared" / "reference.jsonl"), "--families", str(EXP / "prepared" / "families.json"),
                    "--out", str(model)], check=True)
    binary = runtime / "decoder"
    subprocess.run(["g++", "-std=c++17", "-O3", "-DNDEBUG", str(EXP / "src" / "decoder.cpp"), "-o", str(binary)], check=True)
    candidates = json.loads((EXP / "prepared" / "candidates.json").read_text())
    jobs, projections = [], {}
    for world in spec["world_ids"]:
        for condition, arms in [("real", spec["real_arms"]), ("pseudo", spec["pseudo_arms"])]:
            label = "" if condition == "real" else "pseudo_"
            source = EXP / "prepared" / f"world_{world}_{label}discovery.json"
            table = runtime / f"world_{world}_{condition}.txt"
            meta = projection(source, candidates, table)
            projections[f"{world}_{condition}"] = meta
            for arm in arms:
                for start in spec["starts"]:
                    name = f"world_{world}_{condition}_{arm}_start{start}"
                    jobs.append({"world_id": world, "condition": condition, "arm": arm, "start": start,
                                 "seed": 83200000 + 100 * world + start,
                                 "steps": spec["optimizer"]["annealing_steps"], "sweeps": spec["optimizer"]["polish_sweeps"],
                                 "binary": str(binary), "model": str(model), "projection": str(table),
                                 "raw_output": str(runtime / (name + ".tsv")),
                                 "output": str(EXP / "artifacts" / "fits" / (name + ".json")),
                                 "input_hashes": {**meta, "model_meta_sha256": digest(model / "model_meta.json"),
                                                  "decoder_source_sha256": digest(EXP / "src" / "decoder.cpp"),
                                                  "spec_sha256": digest(EXP / "src" / "SPEC.json")}})
    save(EXP / "artifacts" / "FIT_INPUTS.json", projections)
    with ProcessPoolExecutor(max_workers=min(24, max(1, args.workers))) as pool:
        futures = [pool.submit(fit_job, job) for job in jobs]
        for n, future in enumerate(as_completed(futures), 1):
            future.result()
            print(f"completed discovery fits {n}/{len(jobs)}", flush=True)
    lock = lock_fits(spec)
    print(json.dumps({"status": "FITS_LOCKED_UNEVALUATED", "restarts": len(lock["restarts"]), "selected": len(lock["selected"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
