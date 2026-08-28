#!/usr/bin/env python3
from __future__ import annotations

import os

import argparse
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

WORK = Path(os.environ.get("GDT612_WORK", Path(__file__).resolve().parent)).resolve()
DECODER = WORK / "decoder"
PREP = WORK / "prepared"


def job_command(job):
    command = [
        str(DECODER), "--prepared", str(PREP), "--language", job["language"],
        "--kind", job["kind"], "--seed", str(job["seed"]),
        "--iterations", str(job["iterations"]), "--output", str(job["output"]),
    ]
    if job.get("train_chunks"):
        command.extend(["--train-chunks", str(job["train_chunks"])])
    return command


def run(job):
    job["output"].mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    result = subprocess.run(job_command(job), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elapsed = time.monotonic() - start
    (job["output"] / "stdout.log").write_text(result.stdout, encoding="utf-8")
    (job["output"] / "stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"job {job['name']} exited {result.returncode}: {result.stderr[-1000:]}")
    return {"name": job["name"], "wall_seconds": elapsed, "command": job_command(job)}


def build_jobs(mode):
    jobs = []
    if mode in ("synthetic", "all"):
        for seed in range(7001, 7007):
            jobs.append({
                "name": f"synthetic_latin_real_{seed}", "language": "latin", "kind": "real",
                "seed": seed, "iterations": 60000,
                "train_chunks": WORK / "synthetic/train_chunks.tsv",
                "output": WORK / f"synthetic/runs/seed_{seed}",
            })
    if mode in ("target", "all"):
        specifications = [
            ("latin", 1100), ("old_italian", 2100), ("middle_high_german", 3100),
        ]
        for language, base in specifications:
            for offset in range(1, 7):
                seed = base + offset
                jobs.append({
                    "name": f"target_{language}_real_{seed}", "language": language, "kind": "real",
                    "seed": seed, "iterations": 60000,
                    "output": WORK / f"target_runs/{language}/real/seed_{seed}",
                })
            for offset in range(91, 94):
                seed = base + offset
                jobs.append({
                    "name": f"target_{language}_destroyed_{seed}", "language": language, "kind": "destroyed",
                    "seed": seed, "iterations": 60000,
                    "output": WORK / f"target_runs/{language}/destroyed/seed_{seed}",
                })
    return jobs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("synthetic", "target", "all"))
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    jobs = build_jobs(args.mode)
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run, job): job for job in jobs}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda x: x["name"])
    (WORK / f"runtime_{args.mode}.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
