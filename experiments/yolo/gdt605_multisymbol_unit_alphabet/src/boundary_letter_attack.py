#!/usr/bin/env python3
"""Try the 98 learned units as ordinary one-letter homophones.

Certain spaces and drawing interruptions split plaintext chunks; ZL-uncertain
separators are joined before the train-only BPE fit.  This is a deliberately
narrow negative/positive diagnostic before admitting variable-length codebook
entries.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import random
import sys
from collections import Counter
from pathlib import Path

from separator_crossing import apply_bpe, clean_source_line, collapse, learn_bpe


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G602 = load_module(
    "gdt602_for_gdt605",
    ROOT / "experiments/yolo/gdt602_naibbe_blind_key_recovery/src/run.py",
)
G601 = G602.G601


def reference_models(language: str):
    paths = G601.fetch_sources()
    source, marker = {
        "latin": (paths["caesar_la.txt"], "GALLIA est omnis"),
        "old_italian": (paths["divina_commedia.txt"], "INFERNO"),
    }[language]
    text = G601.clean_reference(source, marker)[:120_000]
    chunks = [text[index:index + 90] for index in range(0, len(text), 90)]
    real = G601.CharModel(4, 0.25).fit(" ".join(chunks))
    rng = random.Random(
        int(hashlib.sha256(("gdt605-null|" + language).encode()).hexdigest()[:16], 16)
    )
    destroyed_chunks = []
    for chunk in chunks:
        characters = list(chunk)
        rng.shuffle(characters)
        destroyed_chunks.append("".join(characters))
    destroyed = G601.CharModel(4, 0.25).fit(" ".join(destroyed_chunks))
    return real, destroyed


def hard_chunks(row: dict[str, str]) -> list[str] | None:
    tokens, separators = clean_source_line(row["ivtff_raw"])
    clean = row["eva_clean"].split()
    if tokens != clean or len(separators) != max(0, len(clean) - 1):
        return None
    if not clean:
        return []
    chunks = []
    current = collapse(clean[0])
    for separator, token in zip(separators, clean[1:]):
        if separator == "uncertain":
            current += collapse(token)
        else:
            chunks.append(current)
            current = collapse(token)
    chunks.append(current)
    return chunks


def score(texts, model) -> float:
    total = 0.0
    for text in texts:
        _context, bits = G601.advance(G601.start_context(model.order), text, model)
        total += bits
    return total


def decode(lines, mapping):
    return ["".join(G601.ALPHABET[mapping[code]] for code in line) for line in lines]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--guarded-rows", type=Path, required=True)
    parser.add_argument("--language", choices=("latin", "old_italian"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=30_000)
    args = parser.parse_args()

    with args.guarded_rows.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if any(row["page"].lower().startswith("f84") for row in rows):
        raise SystemExit("forbidden selector present")
    chunks = {"train": [], "held": []}
    unresolved = []
    for row in rows:
        values = hard_chunks(row)
        if values is None:
            unresolved.append(row["locus"])
        else:
            chunks[row["split"]].extend(values)

    rules, train_segmentations = learn_bpe(chunks["train"], 64)
    train_lines = [
        ["X|" + unit for unit in train_segmentations[chunk]]
        for chunk in chunks["train"]
    ]
    held_lines = [
        ["X|" + unit for unit in apply_bpe(chunk, rules)]
        for chunk in chunks["held"]
    ]
    held_counts = Counter(code for line in held_lines for code in line)
    real, destroyed = reference_models(args.language)
    output = {
        "schema": "gdt605-boundary-aware-one-letter-attack-v1",
        "language": args.language,
        "train_chunks": len(train_lines),
        "held_chunks": len(held_lines),
        "unit_types": len({code for line in train_lines for code in line}),
        "held_unseen_unit_types": sorted(
            {code for line in held_lines for code in line}
            - {code for line in train_lines for code in line}
        ),
        "unresolved_loci": unresolved,
        "models": {},
    }
    keys = {}
    for model_name, model in (("real", real), ("destroyed", destroyed)):
        problem = G602.build_blind_problem(train_lines, model)
        records = []
        keymaps = []
        for seed in (11, 29, 47):
            total, key = G602.solve(
                problem,
                args.iterations,
                1,
                seed + (0 if model_name == "real" else 1000),
                True,
            )
            mapping = {code: int(key[index]) for index, code in enumerate(problem.vocab)}
            texts = decode(held_lines, mapping)
            real_bits = score(texts, real)
            destroyed_bits = score(texts, destroyed)
            characters = sum(map(len, texts))
            records.append({
                "seed": seed,
                "train_bits_per_unit": total / len(problem.obs),
                "held_characters": characters,
                "held_real_bits_per_character": real_bits / characters,
                "held_destroyed_bits_per_character": destroyed_bits / characters,
                "held_real_minus_destroyed_bits_per_character": (
                    real_bits - destroyed_bits
                ) / characters,
                "sample_chunks": texts[:50],
            })
            keymaps.append(mapping)
        agreements = []
        for left in range(len(keymaps)):
            for right in range(left + 1, len(keymaps)):
                shared = sorted(set(keymaps[left]) & set(keymaps[right]))
                same = {code for code in shared if keymaps[left][code] == keymaps[right][code]}
                agreements.append({
                    "left": left,
                    "right": right,
                    "type_agreement": len(same) / len(shared),
                    "held_weighted_agreement": (
                        sum(held_counts[code] for code in same)
                        / sum(held_counts[code] for code in shared)
                    ),
                })
        output["models"][model_name] = {"runs": records, "key_agreement": agreements}
        keys[model_name] = keymaps

    real_runs = output["models"]["real"]["runs"]
    output["decision"] = (
        "ONE_LETTER_READING_CANDIDATE"
        if min(run["held_real_minus_destroyed_bits_per_character"] for run in real_runs) >= 0.10
        and min(
            pair["held_weighted_agreement"]
            for pair in output["models"]["real"]["key_agreement"]
        ) >= 0.85
        else "BOUNDARY_AWARE_ONE_LETTER_SUBSTITUTION_REJECTED"
    )
    output["claim_ceiling"] = (
        "Narrow one-letter homophone attack only; no language, plaintext, lexeme, sound or meaning."
    )
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "language": args.language,
        "decision": output["decision"],
        "real_runs": real_runs,
        "real_key_agreement": output["models"]["real"]["key_agreement"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
