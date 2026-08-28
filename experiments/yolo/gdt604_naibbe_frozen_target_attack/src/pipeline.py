#!/usr/bin/env python3
"""Portable, end-to-end implementation of the frozen GDT604 target attack."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import random
import statistics
import subprocess
import unicodedata
import shutil
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

import portable_factorizer as factor
import portable_keylib as keylib
from common import find_repository_root, read_tsv, sha256_path, tsv_bytes


EXPECTED_GDT327_SAFE = "7eba46774be44992064cc114f67329723ac7bf589321b0d763fb7f7f748cc1e9"
EXPECTED_TARGET = "d9186790969641f5dce9fb75d697bd926310936248d7214ef804ba29d0a1e413"
EXPECTED_TRAIN = "28bbfbbae5a2c622263ac0b0a182d8e73be94abc74223644e2662ba0939461f2"
EXPECTED_HELD = "1fe1497ae6e63e1b37fe27ae72354c7e080b9cff798f3bd757e6965af2302825"
EXPECTED_SEGMENTS = {
    115: "be9ab5fbed6109ede96765a2e28c0bd81fd5b68e7221e4f17206af367b55a9d4",
    132: "e1a73509a0c3d70e75ad73ca2e87a5c40a81c1345693fc3e47bc1e53498a7880",
    138: "cc2df74c86553a2c1c9575f728cda8efdf6775736ed6a5251608a4383627d76f",
}
EXPECTED_TRAIN_ONLY_SEGMENT = "e742393ec666308f5d29c412814a10f9e38d35053626c1e619e0e77d5ebfa5fc"
PREREG_SHA256 = "47d54ab3b180d4cf1fdc57fd3bbd0f69af866ad39ff61879b72a19ec742c8d97"
REFERENCE_HASHES = {
    "caesar_la.txt": "84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c",
    "divina_commedia.txt": "aafa15bbc0644dac7680ce3d0e4494b99775fbc83394cb7ad88145a0f8d6b31e",
    "mhg/Erec-conll.txt": "367cc2e9d0b60aadee501c187864dea97c77af41303f216986cfa35575f43675",
    "mhg/Iwein-conll.txt": "5b43f962da24d5b438ff93f64f30036087fe37d1cd5863c0bd29e764957b6a6f",
    "mhg/Parzival-conll.txt": "9d7ef5fd1842f6197121b654eb3c57a307ff01a9698768e27be069732afdf5cf",
    "mhg/Rolandslied-conll.txt": "46b078128c6932759d56a6a4bf13f9c3bf84d88f7a8d0e35fca31670cc0191fa",
    "mhg/Willehalm-conll.txt": "abee7d5d1aee54fa944e0d311d4645455503d4fc0bbd9ef919c46a9cfd10e7fe",
}
MHG_FILES = (
    "Erec-conll.txt", "Iwein-conll.txt", "Parzival-conll.txt",
    "Rolandslied-conll.txt", "Willehalm-conll.txt",
)
SEEDS = (11, 29, 47)
RESTARTS = (0, 1)
ITERATIONS = 50_000
REFERENCE_CHARS = 120_000
CHUNK = 90
NULLS = 32
TOP_N = 20


def materialize_guarded(work: Path, artifacts: Path) -> tuple[Path, Path]:
    root = find_repository_root()
    safe = root / "gdt327_joint_tuple_interlinear.tsv"
    if sha256_path(safe) != EXPECTED_GDT327_SAFE:
        raise RuntimeError("GDT327 allow-list changed")
    page_to_folio: dict[str, str] = {}
    with safe.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page, folio = row["page"], row["physical_folio"]
            if page.lower().startswith("f84") or folio.lower().startswith("f84"):
                raise RuntimeError("sealed selector found in GDT327 allow-list")
            old = page_to_folio.setdefault(page, folio)
            if old != folio:
                raise RuntimeError((page, old, folio))
    pages = sorted(page_to_folio)
    folios = sorted(set(page_to_folio.values()))
    if len(pages) != 180 or len(folios) != 91:
        raise RuntimeError((len(pages), len(folios)))
    ranked = sorted(
        folios,
        key=lambda folio: hashlib.sha256(
            ("gdt604-held-v1|" + folio).encode()
        ).hexdigest(),
    )
    held, train = sorted(ranked[:23]), sorted(ranked[23:])
    split = {
        "schema": "gdt604-physical-folio-split-v1",
        "algorithm": "first 23 by sha256('gdt604-held-v1|' + physical_folio)",
        "gdt327_safe_sha256": EXPECTED_GDT327_SAFE,
        "pages": pages,
        "page_to_physical_folio": page_to_folio,
        "train_folios": train,
        "held_folios": held,
        "f84": "FORBIDDEN_AND_ABSENT",
    }
    split_path = artifacts / "gdt604_folio_split.json"
    split_path.write_text(json.dumps(split, indent=2, sort_keys=True) + "\n")

    command = [
        str(root / "vmanus-exp"), "query-tsv",
        "transcription/voynich_zl3b_lines.tsv", "--selector", "page",
    ]
    for page in pages:
        command.extend(("--allow", page))
    command.extend((
        "--forbid-prefix", "f84", "--columns",
        "page,locus,line_number,section,language,hand,eva_clean",
    ))
    emitted = subprocess.run(
        command, cwd=root, check=True, capture_output=True, text=True
    ).stdout
    source_rows = list(csv.DictReader(io.StringIO(emitted), delimiter="\t"))
    fields = [
        "page", "physical_folio", "split", "locus", "line_number",
        "section", "language", "hand", "eva_clean",
    ]
    rows = []
    for row in source_rows:
        page = row["page"]
        if page not in page_to_folio or page.lower().startswith("f84"):
            raise RuntimeError("guard emitted forbidden or unallowlisted selector")
        folio = page_to_folio[page]
        rows.append({
            **row,
            "physical_folio": folio,
            "split": "held" if folio in held else "train",
        })
    target_path = work / "gdt604_target_rows.tsv"
    target_path.write_bytes(tsv_bytes(fields, rows))
    if sha256_path(target_path) != EXPECTED_TARGET:
        raise RuntimeError("guarded target hash changed")
    return target_path, split_path


def split_guarded(target_path: Path, work: Path) -> tuple[Path, Path]:
    if sha256_path(target_path) != EXPECTED_TARGET:
        raise RuntimeError("guarded target changed")
    rows = read_tsv(target_path)
    fields = list(rows[0])
    result = {}
    expected = {"train": EXPECTED_TRAIN, "held": EXPECTED_HELD}
    for split in ("train", "held"):
        path = work / f"gdt604_{split}_rows.tsv"
        path.write_bytes(tsv_bytes(fields, [row for row in rows if row["split"] == split]))
        if sha256_path(path) != expected[split]:
            raise RuntimeError(f"{split} row hash changed")
        result[split] = path
    return result["train"], result["held"]


def segment_target(target_path: Path, artifacts: Path) -> dict[int, Path]:
    rows = read_tsv(target_path)
    if any(row["page"].lower().startswith("f84") for row in rows):
        raise RuntimeError("forbidden page in guarded target")
    train_tokens = [
        token for row in rows if row["split"] == "train"
        for token in row["eva_clean"].split()
    ]
    held_tokens = [
        token for row in rows if row["split"] == "held"
        for token in row["eva_clean"].split()
    ]
    train_freq, held_freq = Counter(train_tokens), Counter(held_tokens)
    outputs: dict[int, Path] = {}
    manifest_outputs = []
    for u_size in (115, 132, 138):
        train_map, _, _ = factor.fit_target_variant(u_size, train_freq)
        u_dict = {token for token, rec in train_map.items() if rec["state"] == "U"}
        p_count, s_count = Counter(), Counter()
        for token, rec in train_map.items():
            if rec["state"] == "B":
                cut = int(rec["cut"])
                p_count[token[:cut]] += train_freq[token]
                s_count[token[cut:]] += train_freq[token]
        p_dict, s_dict = set(p_count), set(s_count)
        held_map = {}
        held_cut_hist = Counter()
        for token in held_freq:
            if token in train_map:
                held_map[token] = {**train_map[token], "source": "TRAIN_TYPE"}
                continue
            viable = [
                cut for cut in range(1, len(token))
                if token[:cut] in p_dict and token[cut:] in s_dict
            ]
            held_cut_hist[len(viable)] += 1
            if viable:
                cut = max(
                    viable,
                    key=lambda index: (
                        (p_count[token[:index]] + 0.5)
                        * (s_count[token[index:]] + 0.5),
                        -index,
                    ),
                )
                held_map[token] = {"state": "B", "cut": cut, "source": "FROZEN_PS"}
            else:
                held_map[token] = {"state": "UNKNOWN", "source": "NO_FROZEN_PARSE"}
        known_occ = sum(
            count for token, count in held_freq.items()
            if held_map[token]["state"] != "UNKNOWN"
        )
        seen_occ = sum(count for token, count in held_freq.items() if token in train_map)
        result = {
            "schema": "gdt604-train-only-segmentation-v1",
            "u_size": u_size,
            "confirmatory": u_size == 138,
            "target_sha256": EXPECTED_TARGET,
            "train_token_occurrences": len(train_tokens),
            "train_token_types": len(train_freq),
            "held_token_occurrences": len(held_tokens),
            "held_token_types": len(held_freq),
            "train_dictionaries": {"U": len(u_dict), "P": len(p_dict), "S": len(s_dict)},
            "train_parsed_occurrence_fraction": sum(
                count for token, count in train_freq.items()
                if train_map[token]["state"] != "UNKNOWN"
            ) / len(train_tokens),
            "train_parsed_type_fraction": sum(
                rec["state"] != "UNKNOWN" for rec in train_map.values()
            ) / len(train_map),
            "held_seen_train_occurrence_fraction": seen_occ / len(held_tokens),
            "held_parsed_occurrence_fraction": known_occ / len(held_tokens),
            "held_parsed_type_fraction": sum(
                rec["state"] != "UNKNOWN" for rec in held_map.values()
            ) / len(held_map),
            "held_unseen_viable_cut_histogram": {
                str(key): value for key, value in sorted(held_cut_hist.items())
            },
            "train_frequency": train_freq,
            "held_frequency": held_freq,
            "prefix_frequency": p_count,
            "suffix_frequency": s_count,
            "train_token_map": train_map,
            "held_token_map": held_map,
        }
        path = artifacts / f"gdt604_target_segmentation_u{u_size}.json"
        path.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
        if sha256_path(path) != EXPECTED_SEGMENTS[u_size]:
            raise RuntimeError(f"U={u_size} segmentation changed")
        outputs[u_size] = path
        manifest_outputs.append({"path": path.name, "sha256": sha256_path(path)})
    manifest = {
        "schema": "gdt604-target-segmentation-freeze-v1",
        "primary": outputs[138].name,
        "navigation": [outputs[115].name, outputs[132].name],
        "outputs": manifest_outputs,
    }
    (artifacts / "gdt604_target_segmentation_freeze.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return outputs


def make_train_only_segmentation(segment: Path, artifacts: Path) -> Path:
    if sha256_path(segment) != EXPECTED_SEGMENTS[138]:
        raise RuntimeError("confirmatory segmentation changed")
    source = json.loads(segment.read_text())
    keep = [
        "schema", "u_size", "confirmatory", "target_sha256",
        "train_token_occurrences", "train_token_types", "train_dictionaries",
        "train_parsed_occurrence_fraction", "train_parsed_type_fraction",
        "train_frequency", "prefix_frequency", "suffix_frequency",
        "train_token_map",
    ]
    out = artifacts / "gdt604_target_segmentation_u138_trainonly.json"
    out.write_text(json.dumps(
        {key: source[key] for key in keep}, sort_keys=True, separators=(",", ":")
    ) + "\n")
    if sha256_path(out) != EXPECTED_TRAIN_ONLY_SEGMENT:
        raise RuntimeError("train-only segmentation changed")
    return out


def render_reference(text: str) -> str:
    text = text.lower().replace("æ", "ae").replace("œ", "oe").replace("ß", "ss")
    text = "".join(
        char for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )
    text = text.replace("j", "i").replace("k", "c").replace("w", "uu")
    return "".join(char for char in text if char in keylib.LATIN_LETTERS)


def load_references(reference_dir: Path) -> dict[str, str]:
    for relative, expected in REFERENCE_HASHES.items():
        path = reference_dir / relative
        if sha256_path(path) != expected:
            raise RuntimeError(f"reference changed or absent: {relative}")
    raw = (reference_dir / "caesar_la.txt").read_text()
    raw = raw[raw.find("GALLIA est omnis"):]
    footer = "*** END OF THE PROJECT GUTENBERG"
    if footer in raw:
        raw = raw[:raw.find(footer)]
    latin = render_reference(raw)[:REFERENCE_CHARS]
    italian = render_reference(
        (reference_dir / "divina_commedia.txt").read_text()
    )[:REFERENCE_CHARS]
    mhg_parts = []
    for name in MHG_FILES:
        tokens = [
            line.split("\t", 1)[0]
            for line in (reference_dir / "mhg" / name).read_text().splitlines()
            if line.strip()
        ]
        mhg_parts.append(
            render_reference(" ".join(tokens))[:REFERENCE_CHARS // len(MHG_FILES)]
        )
    result = {
        "latin": latin,
        "old_italian": italian,
        "middle_high_german": "".join(mhg_parts),
    }
    if any(len(text) != REFERENCE_CHARS for text in result.values()):
        raise RuntimeError({name: len(text) for name, text in result.items()})
    return result


def lm_text(text: str, language: str, destroyed: bool) -> str:
    chunks = [text[index:index + CHUNK] for index in range(0, len(text), CHUNK)]
    if destroyed:
        seed = int(hashlib.sha256(
            ("gdt604-reference-null|" + language).encode()
        ).hexdigest()[:16], 16)
        rng = random.Random(seed)
        shuffled = []
        for chunk in chunks:
            chars = list(chunk)
            rng.shuffle(chars)
            shuffled.append("".join(chars))
        chunks = shuffled
    return " ".join(chunks)


class CharModel:
    def __init__(self, order=4, alpha=0.25):
        self.order, self.alpha, self.logp = order, alpha, None

    def fit(self, text):
        alphabet = keylib.ALPHABET
        size = len(alphabet)
        ids = np.array(
            [alphabet.index(char) for char in text if char in alphabet], dtype=np.int64
        )
        unigram = np.bincount(ids, minlength=size).astype(np.float64)
        conditional = (unigram + 1.0) / (unigram.sum() + size)
        for context_order in range(1, self.order):
            context_size = size ** context_order
            packed = np.zeros(len(ids) - context_order, dtype=np.int64)
            for offset in range(context_order):
                packed = packed * size + ids[offset:len(ids) - context_order + offset]
            packed = packed * size + ids[context_order:]
            counts = np.bincount(
                packed, minlength=context_size * size
            ).astype(float).reshape(context_size, size)
            totals = counts.sum(axis=1, keepdims=True)
            lower = conditional.reshape(-1, size)
            backoff = np.tile(lower, (context_size // lower.shape[0], 1))
            strength = self.alpha * size
            conditional = (counts + strength * backoff) / (totals + strength)
        self.logp = np.log2(conditional.reshape(-1))
        return self


def train_runs(rows, token_map):
    runs = []
    for row in rows:
        current = []
        for token in row["eva_clean"].split():
            rec = token_map[token]
            if rec["state"] == "UNKNOWN":
                if current:
                    runs.append(current)
                    current = []
            elif rec["state"] == "U":
                current.append("U|" + token)
            else:
                cut = int(rec["cut"])
                current.extend(("P|" + token[:cut], "S|" + token[cut:]))
        if current:
            runs.append(current)
    return runs


FIT_REFS = None
FIT_OBS = None
FIT_VOCAB = None


def init_fit_worker(refs, obs, vocab):
    global FIT_REFS, FIT_OBS, FIT_VOCAB
    FIT_REFS, FIT_OBS, FIT_VOCAB = refs, obs, vocab


def fit_worker(job):
    language, destroyed, seed, restart = job
    model = CharModel().fit(lm_text(FIT_REFS[language], language, destroyed))
    solver_seed = seed * 100 + restart
    total, key = keylib.solve(FIT_OBS, FIT_VOCAB, model, ITERATIONS, 1, solver_seed)
    return {
        "language": language,
        "model": "destroyed" if destroyed else "real",
        "seed": seed,
        "restart": restart,
        "solver_seed": solver_seed,
        "train_bits_per_event": total / len(FIT_OBS),
        "key": {
            code: keylib.ALPHABET[int(key[index])]
            for index, code in enumerate(FIT_VOCAB)
        },
    }


def fit_keys(
    train_path: Path, segment: Path, reference_dir: Path, artifacts: Path, workers: int
) -> Path:
    if sha256_path(train_path) != EXPECTED_TRAIN:
        raise RuntimeError("train rows changed")
    if sha256_path(segment) != EXPECTED_TRAIN_ONLY_SEGMENT:
        raise RuntimeError("train-only segmentation changed")
    rows = read_tsv(train_path)
    if any(
        row["split"] != "train" or row["page"].lower().startswith("f84")
        for row in rows
    ):
        raise RuntimeError("held or forbidden row reached fitter")
    segmentation = json.loads(segment.read_text())
    runs = train_runs(rows, segmentation["train_token_map"])
    vocab, _, obs = keylib.build_stream(runs)
    groups = Counter(code[0] for code in vocab)
    refs = load_references(reference_dir)
    ref_meta = {
        language: {
            "rendered_chars": len(text),
            "rendered_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "real_lm_input_sha256": hashlib.sha256(
                lm_text(text, language, False).encode()
            ).hexdigest(),
            "destroyed_lm_input_sha256": hashlib.sha256(
                lm_text(text, language, True).encode()
            ).hexdigest(),
        }
        for language, text in refs.items()
    }
    jobs = [
        (language, destroyed, seed, restart)
        for language in sorted(refs)
        for destroyed in (False, True)
        for seed in SEEDS for restart in RESTARTS
    ]
    results = []
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=init_fit_worker,
        initargs=(refs, obs, vocab),
    ) as pool:
        futures = [pool.submit(fit_worker, job) for job in jobs]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda rec: (
        rec["language"], rec["model"], rec["seed"], rec["restart"]
    ))
    output = {
        "schema": "gdt604-train-only-key-freeze-v1",
        "prereg_sha256": PREREG_SHA256,
        "train_rows_sha256": EXPECTED_TRAIN,
        "segmentation_sha256": EXPECTED_TRAIN_ONLY_SEGMENT,
        "reference_sources": REFERENCE_HASHES,
        "mhg_commit": "3eddc3dc1620cf400c152d9ed8915416cb8d6d7a",
        "reference_models": ref_meta,
        "configuration": {
            "languages": sorted(refs), "seeds": list(SEEDS),
            "restarts": list(RESTARTS), "iterations": ITERATIONS,
            "order": 4, "alpha": 0.25, "reference_chars": REFERENCE_CHARS,
            "chunk": CHUNK, "state_letter_capacity": 6,
        },
        "train_runs": len(runs), "train_lm_events": len(obs),
        "code_types": len(vocab), "state_code_types": groups,
        "jobs": results, "held_material_opened": False,
    }
    out = artifacts / "gdt604_target_key_freeze.json"
    out.write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    return out


def units_for_row(row, token_map):
    tokens = row["eva_clean"].split()
    token_units = []
    runs, current = [], []
    for token in tokens:
        rec = token_map[token]
        if rec["state"] == "UNKNOWN":
            token_units.append(None)
            if current:
                runs.append(current)
                current = []
        elif rec["state"] == "U":
            codes = ["U|" + token]
            token_units.append(codes)
            current.extend(codes)
        else:
            cut = int(rec["cut"])
            codes = ["P|" + token[:cut], "S|" + token[cut:]]
            token_units.append(codes)
            current.extend(codes)
    if current:
        runs.append(current)
    return tokens, token_units, runs


def score_char_runs(char_runs, model):
    alphabet = keylib.ALPHABET
    size = len(alphabet)
    modulus = size ** (model.order - 1)
    total = 0.0
    for text in char_runs:
        context = 0
        for _ in range(model.order - 1):
            context = context * size + keylib.SPACE_ID
        for char in text:
            letter = alphabet.index(char)
            total += float(model.logp[context * size + letter])
            context = (context * size + letter) % modulus
    return total


def zscore(observed, null_scores):
    mean = statistics.mean(null_scores)
    sd = statistics.stdev(null_scores)
    return (observed - mean) / sd if sd else 0.0, mean, sd


EVAL_ROWS = None
EVAL_TOKEN_MAP = None
EVAL_REFS = None


def init_eval_worker(rows, token_map, refs):
    global EVAL_ROWS, EVAL_TOKEN_MAP, EVAL_REFS
    EVAL_ROWS, EVAL_TOKEN_MAP, EVAL_REFS = rows, token_map, refs


def evaluate_worker(job):
    language = job["language"]
    real_model = CharModel().fit(lm_text(EVAL_REFS[language], language, False))
    destroyed_model = CharModel().fit(lm_text(EVAL_REFS[language], language, True))
    key = job["key"]
    aggregate_real = aggregate_destroyed = 0.0
    aggregate_null_real = [0.0] * NULLS
    aggregate_null_destroyed = [0.0] * NULLS
    folio_real = Counter()
    folio_null = [Counter() for _ in range(NULLS)]
    decoded_chars = parsed_tokens = all_tokens = 0
    line_results = []
    for line_index, row in enumerate(EVAL_ROWS):
        tokens, token_units, code_runs = units_for_row(row, EVAL_TOKEN_MAP)
        char_runs = ["".join(key[code] for code in run) for run in code_runs]
        nchar = sum(map(len, char_runs))
        parsed = sum(value is not None for value in token_units)
        all_tokens += len(tokens)
        parsed_tokens += parsed
        decoded_chars += nchar
        real_score = score_char_runs(char_runs, real_model)
        destroyed_score = score_char_runs(char_runs, destroyed_model)
        aggregate_real += real_score
        aggregate_destroyed += destroyed_score
        folio_real[row["physical_folio"]] += real_score
        null_real_line, null_destroyed_line = [], []
        for null_index in range(NULLS):
            shuffled_runs = []
            for run_index, text in enumerate(char_runs):
                seed = int(hashlib.sha256(
                    f"gdt604-held-null|{row['locus']}|{null_index}|{run_index}".encode()
                ).hexdigest()[:16], 16)
                rng = random.Random(seed)
                chars = list(text)
                rng.shuffle(chars)
                shuffled_runs.append("".join(chars))
            real_null = score_char_runs(shuffled_runs, real_model)
            destroyed_null = score_char_runs(shuffled_runs, destroyed_model)
            null_real_line.append(real_null)
            null_destroyed_line.append(destroyed_null)
            aggregate_null_real[null_index] += real_null
            aggregate_null_destroyed[null_index] += destroyed_null
            folio_null[null_index][row["physical_folio"]] += real_null
        display = [
            "<?>" if codes is None else "".join(key[code] for code in codes)
            for codes in token_units
        ]
        line_results.append({
            "seed": job["seed"], "restart": job["restart"],
            "line_index": line_index, "page": row["page"],
            "physical_folio": row["physical_folio"], "locus": row["locus"],
            "section": row["section"], "eva_clean": row["eva_clean"],
            "decoded": "".join(display), "tokens": len(tokens),
            "parsed_tokens": parsed, "decoded_chars": nchar,
            "real_bits": real_score, "destroyed_bits": destroyed_score,
            "order_gain_per_char": (
                (real_score - statistics.mean(null_real_line)) / nchar if nchar else 0.0
            ),
            "lr_gain_per_char": (
                ((real_score - destroyed_score) - statistics.mean([
                    real - destroyed
                    for real, destroyed in zip(null_real_line, null_destroyed_line)
                ])) / nchar if nchar else 0.0
            ),
        })
    order_z, order_mean, order_sd = zscore(aggregate_real, aggregate_null_real)
    lr_observed = aggregate_real - aggregate_destroyed
    lr_null = [
        real - destroyed
        for real, destroyed in zip(aggregate_null_real, aggregate_null_destroyed)
    ]
    lr_z, lr_mean, lr_sd = zscore(lr_observed, lr_null)
    positive_folios = sum(
        folio_real[folio] > statistics.mean([
            folio_null[index][folio] for index in range(NULLS)
        ])
        for folio in sorted(folio_real)
    )
    return {
        "language": language, "model": job["model"],
        "seed": job["seed"], "restart": job["restart"],
        "train_bits_per_event": job["train_bits_per_event"],
        "held_decoded_chars": decoded_chars,
        "held_token_coverage": parsed_tokens / all_tokens,
        "held_real_bits_per_char": aggregate_real / decoded_chars,
        "held_destroyed_bits_per_char": aggregate_destroyed / decoded_chars,
        "held_lr_bits_per_char": lr_observed / decoded_chars,
        "held_order_z": order_z,
        "held_order_null_mean_bits_per_char": order_mean / decoded_chars,
        "held_order_null_sd_bits_per_char": order_sd / decoded_chars,
        "held_lr_z": lr_z,
        "held_lr_null_mean_bits_per_char": lr_mean / decoded_chars,
        "held_lr_null_sd_bits_per_char": lr_sd / decoded_chars,
        "positive_order_folios": positive_folios,
        "held_folios": len(folio_real),
        "line_results": line_results if job["model"] == "real" else [],
    }


def key_agreement(jobs, held_code_counts):
    pairs = []
    for index, left in enumerate(jobs):
        for right in jobs[index + 1:]:
            shared = sorted(set(left["key"]) & set(right["key"]))
            type_same = sum(left["key"][code] == right["key"][code] for code in shared)
            weight = sum(held_code_counts[code] for code in shared)
            weighted_same = sum(
                held_code_counts[code] for code in shared
                if left["key"][code] == right["key"][code]
            )
            pairs.append({
                "a": f"s{left['seed']}r{left['restart']}",
                "b": f"s{right['seed']}r{right['restart']}",
                "shared_types": len(shared),
                "type_agreement": type_same / len(shared),
                "held_weighted_agreement": weighted_same / weight,
            })
    return pairs


def evaluate_held(
    held_path: Path, segment: Path, key_path: Path, reference_dir: Path,
    artifacts: Path, workers: int,
) -> Path:
    if sha256_path(held_path) != EXPECTED_HELD:
        raise RuntimeError("held rows changed")
    if sha256_path(segment) != EXPECTED_SEGMENTS[138]:
        raise RuntimeError("held segmentation changed")
    rows = read_tsv(held_path)
    if any(
        row["split"] != "held" or row["page"].lower().startswith("f84")
        for row in rows
    ):
        raise RuntimeError("train or forbidden row reached held evaluator")
    segmentation = json.loads(segment.read_text())
    token_map = segmentation["held_token_map"]
    frozen = json.loads(key_path.read_text())
    refs = load_references(reference_dir)
    held_code_counts = Counter()
    line_code_units = []
    for row in rows:
        _, token_units, _ = units_for_row(row, token_map)
        held_code_counts.update(
            code for codes in token_units if codes is not None for code in codes
        )
        line_code_units.append(token_units)
    results = []
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=init_eval_worker,
        initargs=(rows, token_map, refs),
    ) as pool:
        futures = [pool.submit(evaluate_worker, job) for job in frozen["jobs"]]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda rec: (
        rec["language"], rec["model"], rec["seed"], rec["restart"]
    ))
    languages = {}
    top_artifacts = []
    for language in sorted(refs):
        frozen_real = [
            job for job in frozen["jobs"]
            if job["language"] == language and job["model"] == "real"
        ]
        eval_real = [
            rec for rec in results
            if rec["language"] == language and rec["model"] == "real"
        ]
        eval_null = [
            rec for rec in results
            if rec["language"] == language and rec["model"] == "destroyed"
        ]
        by_real = {(rec["seed"], rec["restart"]): rec for rec in eval_real}
        by_null = {(rec["seed"], rec["restart"]): rec for rec in eval_null}
        paired_lr = {
            f"s{seed}r{restart}": (
                by_real[(seed, restart)]["held_lr_bits_per_char"]
                - by_null[(seed, restart)]["held_lr_bits_per_char"]
            )
            for seed in SEEDS for restart in RESTARTS
        }
        pairs = key_agreement(frozen_real, held_code_counts)
        all_six_same = majority_same = total_units = 0
        line_consensus = {}
        for line_index, token_units in enumerate(line_code_units):
            same = majority = count = 0
            for codes in token_units:
                if codes is None:
                    continue
                for code in codes:
                    letters = [job["key"][code] for job in frozen_real]
                    count += 1
                    same += len(set(letters)) == 1
                    majority += Counter(letters).most_common(1)[0][1] / len(letters)
            line_consensus[line_index] = {
                "all_six": same / count if count else 0.0,
                "majority": majority / count if count else 0.0,
            }
            all_six_same += same
            majority_same += majority
            total_units += count
        line_by_job = {
            (rec["seed"], rec["restart"]): {
                line["line_index"]: line for line in rec["line_results"]
            }
            for rec in eval_real
        }
        candidates = []
        for line_index, row in enumerate(rows):
            records = [
                line_by_job[(seed, restart)][line_index]
                for seed in SEEDS for restart in RESTARTS
            ]
            coverage = records[0]["parsed_tokens"] / max(1, records[0]["tokens"])
            if coverage < 0.8 or records[0]["decoded_chars"] < 10:
                continue
            rank_score = statistics.median(
                record["lr_gain_per_char"] for record in records
            )
            candidates.append((rank_score, line_index, records))
        top_rows = []
        for rank, (rank_score, line_index, records) in enumerate(
            sorted(candidates, reverse=True)[:TOP_N], 1
        ):
            row = rows[line_index]
            item = {
                "rank": rank, "page": row["page"],
                "physical_folio": row["physical_folio"], "locus": row["locus"],
                "section": row["section"], "eva_clean": row["eva_clean"],
                "parsed_token_fraction": records[0]["parsed_tokens"] / records[0]["tokens"],
                "median_lr_order_gain_bits_per_char": rank_score,
                "all_six_consensus_fraction": line_consensus[line_index]["all_six"],
                "majority_consensus_fraction": line_consensus[line_index]["majority"],
                "all_restarts_identical": int(line_consensus[line_index]["all_six"] == 1.0),
            }
            for record in records:
                item[f"decoded_s{record['seed']}_r{record['restart']}"] = record["decoded"]
            top_rows.append(item)
        top_path = artifacts / f"gdt604_top_lines_{language}.tsv"
        top_path.write_bytes(tsv_bytes(list(top_rows[0]), top_rows))
        top_artifacts.append({"path": top_path.name, "sha256": sha256_path(top_path)})
        coverage = eval_real[0]["held_token_coverage"]
        gates = {
            "coverage_ge_0_80": coverage >= 0.80,
            "every_order_z_ge_5": min(rec["held_order_z"] for rec in eval_real) >= 5,
            "every_positive_folios_ge_16": min(
                rec["positive_order_folios"] for rec in eval_real
            ) >= 16,
            "every_paired_lr_advantage_ge_0_10": min(paired_lr.values()) >= 0.10,
            "min_type_agreement_ge_0_70": min(
                pair["type_agreement"] for pair in pairs
            ) >= 0.70,
            "min_weighted_agreement_ge_0_85": min(
                pair["held_weighted_agreement"] for pair in pairs
            ) >= 0.85,
            "all_six_occurrence_consensus_ge_0_90": all_six_same / total_units >= 0.90,
        }
        languages[language] = {
            "held_token_coverage": coverage,
            "real_restart_metrics": [
                {key: value for key, value in rec.items() if key != "line_results"}
                for rec in eval_real
            ],
            "destroyed_restart_metrics": [
                {key: value for key, value in rec.items() if key != "line_results"}
                for rec in eval_null
            ],
            "paired_real_minus_destroyed_key_lr_bits_per_char": paired_lr,
            "key_pair_agreement": pairs,
            "min_key_type_agreement": min(pair["type_agreement"] for pair in pairs),
            "min_key_held_weighted_agreement": min(
                pair["held_weighted_agreement"] for pair in pairs
            ),
            "all_six_occurrence_consensus": all_six_same / total_units,
            "majority_occurrence_consensus": majority_same / total_units,
            "gates": gates,
            "all_gates_pass": all(gates.values()),
            "top_lines_path": top_path.name,
        }
    passers = [
        language for language, record in languages.items() if record["all_gates_pass"]
    ]
    decision = (
        "LANGUAGE_LIKE_READING" if len(passers) == 1
        else "LM_DRIVEN_PSEUDOTEXT_NO_READING"
    )
    output = {
        "schema": "gdt604-held-target-evaluation-v1",
        "prereg_sha256": PREREG_SHA256,
        "held_rows_sha256": EXPECTED_HELD,
        "segmentation_sha256": EXPECTED_SEGMENTS[138],
        "key_freeze_sha256": sha256_path(key_path),
        "segmentation_capacity_and_coverage": {
            key: segmentation[key] for key in (
                "train_dictionaries", "train_parsed_occurrence_fraction",
                "train_parsed_type_fraction", "held_seen_train_occurrence_fraction",
                "held_parsed_occurrence_fraction", "held_parsed_type_fraction",
                "held_unseen_viable_cut_histogram",
            )
        },
        "languages": languages,
        "passing_languages": passers,
        "decision": decision,
        "claim_ceiling": (
            "No Voynich language, sound, lexeme, plaintext, translation, or meaning is assigned."
        ),
        "top_line_artifacts": top_artifacts,
    }
    out = artifacts / "gdt604_target_result.json"
    out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    return out


def reference_calibration(reference_dir: Path, artifacts: Path) -> Path:
    raw = (reference_dir / "caesar_la.txt").read_text()
    raw = raw[raw.find("GALLIA est omnis"):]
    footer = "*** END OF THE PROJECT GUTENBERG"
    if footer in raw:
        raw = raw[:raw.find(footer)]
    latin = render_reference(raw)
    italian = render_reference((reference_dir / "divina_commedia.txt").read_text())
    mhg_train, mhg_held = [], []
    for name in MHG_FILES:
        tokens = [
            line.split("\t", 1)[0]
            for line in (reference_dir / "mhg" / name).read_text().splitlines()
            if line.strip()
        ]
        text = render_reference(" ".join(tokens))
        mhg_train.append(text[:24_000])
        mhg_held.append(text[24_000:48_000])
    references = {
        "latin": (latin[:120_000], latin[120_000:]),
        "old_italian": (italian[:120_000], italian[120_000:240_000]),
        "middle_high_german": ("".join(mhg_train), "".join(mhg_held)),
    }
    result = {}
    for language, (train, held) in references.items():
        real = CharModel().fit(lm_text(train, language, False))
        null = CharModel().fit(lm_text(train, language, True))
        runs = [held[index:index + 90] for index in range(0, len(held), 90) if held[index:index + 90]]
        observed = score_char_runs(runs, real) - score_char_runs(runs, null)
        nulls = []
        for index in range(32):
            shuffled = []
            for run_index, run in enumerate(runs):
                seed = int(hashlib.sha256(
                    f"gdt604-ref-cal|{language}|{index}|{run_index}".encode()
                ).hexdigest()[:16], 16)
                rng = random.Random(seed)
                chars = list(run)
                rng.shuffle(chars)
                shuffled.append("".join(chars))
            nulls.append(score_char_runs(shuffled, real) - score_char_runs(shuffled, null))
        z_value, mean, sd = zscore(observed, nulls)
        result[language] = {
            "held_chars": len(held),
            "held_sha256": hashlib.sha256(held.encode()).hexdigest(),
            "real_minus_destroyed_bits_per_char": observed / len(held),
            "order_null_mean_bits_per_char": mean / len(held),
            "order_null_sd_bits_per_char": sd / len(held),
            "order_z": z_value,
        }
    out = artifacts / "gdt604_reference_calibration.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return out


def render_top_appendix(artifacts: Path) -> Path:
    languages = ("latin", "old_italian", "middle_high_german")
    labels = {
        "latin": "Latin", "old_italian": "Old Italian",
        "middle_high_german": "Middle High German",
    }
    lines = [
        "# Complete GDT604 held-folio top-line appendix", "",
        "These are character-LM hypotheses, not translations or meanings. Rankings use the median real-vs-destroyed order gain across all six frozen restarts.", "",
    ]
    for language in languages:
        rows = read_tsv(artifacts / f"gdt604_top_lines_{language}.tsv")
        lines.extend((f"## {labels[language]}", ""))
        for row in rows:
            lines.extend((
                f"### {row['rank']}. {row['locus']} — {row['page']} / {row['physical_folio']} / section {row['section']}",
                "",
                f"Coverage `{float(row['parsed_token_fraction']):.4f}`; median LR-order gain `{float(row['median_lr_order_gain_bits_per_char']):.6f}` bit/char; all-six consensus `{float(row['all_six_consensus_fraction']):.4f}`; majority consensus `{float(row['majority_consensus_fraction']):.4f}`; all restarts identical `{row['all_restarts_identical']}`.",
                "",
                f"- EVA: `{row['eva_clean']}`",
                f"- seed 11 / restart 0: `{row['decoded_s11_r0']}`",
                f"- seed 11 / restart 1: `{row['decoded_s11_r1']}`",
                f"- seed 29 / restart 0: `{row['decoded_s29_r0']}`",
                f"- seed 29 / restart 1: `{row['decoded_s29_r1']}`",
                f"- seed 47 / restart 0: `{row['decoded_s47_r0']}`",
                f"- seed 47 / restart 1: `{row['decoded_s47_r1']}`",
                "",
            ))
    out = artifacts / "GDT604_TOP_LINES_FULL.md"
    out.write_text("\n".join(lines) + "\n")
    return out


def run_all(work: Path, artifacts: Path, reference_dir: Path, workers: int):
    work.mkdir(parents=True, exist_ok=True)
    artifacts.mkdir(parents=True, exist_ok=True)
    target, _ = materialize_guarded(work, artifacts)
    train, held = split_guarded(target, work)
    segments = segment_target(target, artifacts)
    train_segment = make_train_only_segmentation(segments[138], artifacts)
    keys = fit_keys(train, train_segment, reference_dir, artifacts, workers)
    result = evaluate_held(held, segments[138], keys, reference_dir, artifacts, workers)
    calibration = reference_calibration(reference_dir, artifacts)
    appendix = render_top_appendix(artifacts)
    return {
        "key_freeze": keys,
        "result": result,
        "reference_calibration": calibration,
        "top_appendix": appendix,
    }


def run_from_frozen_segmentation(
    work: Path, artifacts: Path, reference_dir: Path, frozen_dir: Path, workers: int
):
    """Reproduce the full 36-key/held run from the published pre-key freeze.

    The legacy factorizer used insertion-sensitive set/Counter tie ordering.
    Consequently its already-frozen segmentation is a required input to exact
    result reproduction.  Target material is still queried afresh and its hash
    and split are revalidated before any key is fitted.
    """
    work.mkdir(parents=True, exist_ok=True)
    artifacts.mkdir(parents=True, exist_ok=True)
    target, split_path = materialize_guarded(work, artifacts)
    train, held = split_guarded(target, work)
    prereg_source = frozen_dir / "GDT604_TARGET_ATTACK_PREREG.md"
    if sha256_path(prereg_source) != PREREG_SHA256:
        raise RuntimeError("published preregistration changed")
    shutil.copyfile(prereg_source, artifacts / prereg_source.name)
    required = {
        "gdt604_target_segmentation_u115.json": EXPECTED_SEGMENTS[115],
        "gdt604_target_segmentation_u132.json": EXPECTED_SEGMENTS[132],
        "gdt604_target_segmentation_u138.json": EXPECTED_SEGMENTS[138],
        "gdt604_target_segmentation_u138_trainonly.json": EXPECTED_TRAIN_ONLY_SEGMENT,
    }
    copied = {}
    for name, expected in required.items():
        source = frozen_dir / name
        if sha256_path(source) != expected:
            raise RuntimeError(f"published pre-key freeze changed: {name}")
        target_path = artifacts / name
        shutil.copyfile(source, target_path)
        copied[name] = target_path
    manifest_source = frozen_dir / "gdt604_target_segmentation_freeze.json"
    if manifest_source.is_file():
        shutil.copyfile(
            manifest_source, artifacts / "gdt604_target_segmentation_freeze.json"
        )
    keys = fit_keys(
        train, copied["gdt604_target_segmentation_u138_trainonly.json"],
        reference_dir, artifacts, workers,
    )
    result = evaluate_held(
        held, copied["gdt604_target_segmentation_u138.json"], keys,
        reference_dir, artifacts, workers,
    )
    calibration = reference_calibration(reference_dir, artifacts)
    appendix = render_top_appendix(artifacts)
    return {
        "split": split_path,
        "key_freeze": keys,
        "result": result,
        "reference_calibration": calibration,
        "top_appendix": appendix,
    }
