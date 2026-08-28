#!/usr/bin/env python3
"""Run GDT601: literal published-Naibbe-key attack on an f84-free corpus."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import numpy as np


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
CACHE = Path(tempfile.gettempdir()) / "gdt601_naibbe_literal_key_attack"

ALPHABET = "abcdefghijklmnopqrstuvwxyz "
A = len(ALPHABET)
SPACE = ALPHABET.index(" ")
NULLS = 32
ORDER = 4
ALPHA = 0.25
BEAM = 3000

GRESHKO_COMMIT = "f2675ec5dd275268bc64dd48ea64fc0e0e9827a2"
ROZANOVA_COMMIT = "956a7c4fc39981f4d116fa3f4edfccce6d065571"
SOURCES = {
    "naibbe_tables.csv": {
        "url": f"https://raw.githubusercontent.com/greshko/naibbe-cipher/{GRESHKO_COMMIT}/references/naibbe_tables.csv",
        "sha256": "4e7cfd54b7ec66515d39a51e11ec97e8e19b643b0b189124eebc3982e707dcec",
    },
    "nathist_output_ciphertext.txt": {
        "url": f"https://raw.githubusercontent.com/greshko/naibbe-cipher/{GRESHKO_COMMIT}/encrypted/nathist_output_ciphertext.txt",
        "sha256": "9cdf2de12f371ac7efdb2e78713f229ada508286c1717758184238a59cd64326",
    },
    "divina_commedia.txt": {
        "url": f"https://raw.githubusercontent.com/greshko/naibbe-cipher/{GRESHKO_COMMIT}/input/examples/divina_commedia.txt",
        "sha256": "aafa15bbc0644dac7680ce3d0e4494b99775fbc83394cb7ad88145a0f8d6b31e",
    },
    "caesar_la.txt": {
        "url": f"https://raw.githubusercontent.com/lrozanova/voynich-units/{ROZANOVA_COMMIT}/voynich_decipherment_repro_bundle/decipherment_attack_v6/lm_corpora/caesar_la.txt",
        "sha256": "84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c",
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_sources() -> dict[str, Path]:
    CACHE.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, spec in SOURCES.items():
        path = CACHE / name
        data = path.read_bytes() if path.is_file() else b""
        if sha256_bytes(data) != spec["sha256"]:
            with urllib.request.urlopen(spec["url"], timeout=60) as response:
                data = response.read()
            if sha256_bytes(data) != spec["sha256"]:
                raise RuntimeError(f"source hash mismatch for {name}")
            temp = path.with_suffix(path.suffix + ".tmp")
            temp.write_bytes(data)
            temp.replace(path)
        paths[name] = path
    return paths


def f84_free_pages() -> list[str]:
    pages = set()
    with (ROOT / "gdt327_joint_tuple_interlinear.tsv").open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            pages.add(row["page"])
    if not pages or any(page.lower().startswith("f84") for page in pages):
        raise RuntimeError("GDT327 allow-list is empty or contains forbidden f84")
    return sorted(pages)


def f84_free_physical_folios() -> set[str]:
    folios = set()
    with (ROOT / "gdt327_joint_tuple_interlinear.tsv").open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            folios.add(row["physical_folio"])
    if not folios or any(folio.lower().startswith("f84") for folio in folios):
        raise RuntimeError("GDT327 physical-folio set is empty or contains forbidden f84")
    return folios


def guarded_voynich_lines() -> list[tuple[str, list[str], dict[str, str]]]:
    pages = f84_free_pages()
    command = [
        str(ROOT / "vmanus-exp"),
        "query-tsv",
        "transcription/voynich_zl3b_lines.tsv",
        "--selector",
        "page",
    ]
    for page in pages:
        command.extend(["--allow", page])
    command.extend(
        ["--columns", "page,locus,line_number,section,language,hand,eva_clean"]
    )
    result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    rows = []
    for row in csv.DictReader(io.StringIO(result.stdout), delimiter="\t"):
        if row["page"] not in pages or row["page"].lower().startswith("f84"):
            raise RuntimeError("guarded query emitted forbidden or unallowed page")
        rows.append((row["locus"], row["eva_clean"].split(), row))
    if not rows:
        raise RuntimeError("guarded query emitted no rows")
    return rows


def control_lines(path: Path):
    return [
        (f"control.{index + 1}", line.split(), {"page": "CONTROL", "section": "LATIN"})
        for index, line in enumerate(path.read_text().splitlines())
        if line.strip()
    ]


def reverse_tables(path: Path):
    reverse = {state: {} for state in ("unigram", "prefix", "suffix")}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            state, _table, letter = row["code"].split("_", 2)
            reverse[state].setdefault(row["glyphs"], set()).add(letter)
    return reverse


def parse_options(token: str, reverse) -> tuple[str, ...]:
    options = set(reverse["unigram"].get(token, ()))
    for cut in range(1, len(token)):
        for left in reverse["prefix"].get(token[:cut], ()):
            for right in reverse["suffix"].get(token[cut:], ()):
                options.add(left + right)
    return tuple(sorted(options))


def clean_reference(path: Path, start_marker: str | None = None) -> str:
    raw = path.read_text()
    if start_marker and start_marker in raw:
        raw = raw[raw.find(start_marker) :]
    footer = "*** END OF THE PROJECT GUTENBERG"
    if footer in raw:
        raw = raw[: raw.find(footer)]
    return "".join(
        char
        for char in raw.lower().replace("j", "i").replace("k", "c").replace("w", "uu")
        if "a" <= char <= "z"
    )


class CharModel:
    def __init__(self, order: int, alpha: float):
        self.order = order
        self.alpha = alpha
        self.logp = None

    @staticmethod
    def encode(text: str) -> np.ndarray:
        return np.array([ALPHABET.index(char) for char in text if char in ALPHABET], dtype=np.int64)

    def fit(self, text: str):
        ids = self.encode(text)
        unigram = np.bincount(ids, minlength=A).astype(np.float64)
        conditional = (unigram + 1.0) / (unigram.sum() + A)
        for context_order in range(1, self.order):
            context_size = A**context_order
            packed = np.zeros(len(ids) - context_order, dtype=np.int64)
            for offset in range(context_order):
                packed = packed * A + ids[offset : len(ids) - context_order + offset]
            packed = packed * A + ids[context_order:]
            counts = np.bincount(packed, minlength=context_size * A).astype(np.float64)
            counts = counts.reshape(context_size, A)
            totals = counts.sum(axis=1, keepdims=True)
            lower = conditional.reshape(-1, A)
            backoff = np.tile(lower, (context_size // lower.shape[0], 1))
            strength = self.alpha * A
            conditional = (counts + strength * backoff) / (totals + strength)
        self.logp = np.log2(conditional.reshape(-1))
        return self


def language_models(paths: dict[str, Path]):
    references = {
        "latin": clean_reference(paths["caesar_la.txt"], "GALLIA est omnis"),
        "italian": clean_reference(paths["divina_commedia.txt"], "INFERNO"),
    }
    models = {}
    for language, text in references.items():
        chunks = " ".join(text[index : index + 90] for index in range(0, len(text), 90))
        models[language] = CharModel(ORDER, ALPHA).fit(chunks)
    return models


def start_context(order: int) -> int:
    context = 0
    for _ in range(order - 1):
        context = context * A + SPACE
    return context


def advance(context: int, text: str, model: CharModel):
    score = 0.0
    modulus = A ** (model.order - 1)
    for char in text:
        letter = ALPHABET.index(char)
        score += float(model.logp[context * A + letter])
        context = (context * A + letter) % modulus
    return context, score


def decode_line(tokens: list[str], options: dict[str, tuple[str, ...]], model: CharModel):
    rendered = []
    total_score = 0.0
    total_chars = 0
    states = {start_context(model.order): (0.0, "")}

    def flush():
        nonlocal states, total_score, total_chars
        _context, (score, text) = max(states.items(), key=lambda item: item[1][0])
        rendered.append(text)
        total_score += score
        total_chars += len(text)
        states = {start_context(model.order): (0.0, "")}

    for token in tokens:
        candidates = options[token]
        if not candidates:
            flush()
            rendered.append(f"[{token}]")
            continue
        next_states = {}
        for context, (score, text) in states.items():
            for candidate_text in candidates:
                next_context, added = advance(context, candidate_text, model)
                candidate = (score + added, text + candidate_text)
                if next_context not in next_states or candidate[0] > next_states[next_context][0]:
                    next_states[next_context] = candidate
        if len(next_states) > BEAM:
            next_states = dict(
                sorted(next_states.items(), key=lambda item: item[1][0], reverse=True)[:BEAM]
            )
        states = next_states
    flush()
    return " ".join(rendered), total_score, total_chars


def shuffle_parsed_runs(tokens, options, rng):
    shuffled = tokens.copy()
    start = 0
    while start < len(shuffled):
        if not options[shuffled[start]]:
            start += 1
            continue
        end = start + 1
        while end < len(shuffled) and options[shuffled[end]]:
            end += 1
        run = shuffled[start:end]
        rng.shuffle(run)
        shuffled[start:end] = run
        start = end
    return shuffled


def score_corpus(lines, options, model, shuffle_seed: int | None = None):
    rng = random.Random(shuffle_seed)
    total_score = 0.0
    total_chars = 0
    rendered_rows = []
    for locus, tokens, metadata in lines:
        use = shuffle_parsed_runs(tokens, options, rng) if shuffle_seed is not None else tokens
        rendered, score, chars = decode_line(use, options, model)
        total_score += score
        total_chars += chars
        rendered_rows.append(
            {
                "locus": locus,
                "page": metadata.get("page", ""),
                "section": metadata.get("section", ""),
                "token_count": len(tokens),
                "decoded_chars": chars,
                "score_bits_per_char": score / chars if chars else None,
                "rendered": rendered,
            }
        )
    return total_score / total_chars, total_chars, rendered_rows


def coverage(lines, options):
    tokens = [token for _locus, line, _metadata in lines for token in line]
    parsed = sum(bool(options[token]) for token in tokens)
    ambiguous = sum(len(options[token]) > 1 for token in tokens)
    types = set(tokens)
    return {
        "events": len(tokens),
        "types": len(types),
        "parsed_events": parsed,
        "parsed_event_fraction": parsed / len(tokens),
        "parsed_types": sum(bool(options[token]) for token in types),
        "parsed_type_fraction": sum(bool(options[token]) for token in types) / len(types),
        "ambiguous_events": ambiguous,
        "ambiguous_event_fraction": ambiguous / len(tokens),
    }


def tsv_bytes(fields, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(
        {
            key: value.rstrip() if isinstance(value, str) else value
            for key, value in row.items()
        }
        for row in rows
    )
    return stream.getvalue().encode()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = fetch_sources()
    reverse = reverse_tables(paths["naibbe_tables.csv"])
    corpora = {
        "naibbe_latin_positive_control": control_lines(paths["nathist_output_ciphertext.txt"]),
        "voynich_f84_free_91_folios": guarded_voynich_lines(),
    }
    token_types = {
        token
        for lines in corpora.values()
        for _locus, line, _metadata in lines
        for token in line
    }
    options = {token: parse_options(token, reverse) for token in token_types}
    models = language_models(paths)

    results = []
    examples = []
    coverage_rows = {name: coverage(lines, options) for name, lines in corpora.items()}
    for language, model in models.items():
        for corpus_name, lines in corpora.items():
            observed, chars, rendered = score_corpus(lines, options, model)
            null_scores = np.array(
                [
                    score_corpus(lines, options, model, shuffle_seed=601000 + index)[0]
                    for index in range(NULLS)
                ],
                dtype=np.float64,
            )
            null_mean = float(null_scores.mean())
            null_sd = float(null_scores.std(ddof=1))
            z = (observed - null_mean) / null_sd
            rank_high = 1 + int(np.sum(null_scores >= observed))
            results.append(
                {
                    "language": language,
                    "corpus": corpus_name,
                    "observed_bits_per_char": observed,
                    "decoded_chars": chars,
                    "null_count": NULLS,
                    "null_mean_bits_per_char": null_mean,
                    "null_sd": null_sd,
                    "order_z": z,
                    "upper_rank": rank_high,
                    "upper_randomization_p": rank_high / (NULLS + 1),
                    "null_scores": [float(value) for value in null_scores],
                }
            )
            if corpus_name.startswith("voynich"):
                eligible = [
                    item
                    for item in rendered
                    if item["decoded_chars"] >= 8 and item["score_bits_per_char"] is not None
                ]
                for rank, item in enumerate(
                    sorted(eligible, key=lambda x: x["score_bits_per_char"], reverse=True)[:12],
                    start=1,
                ):
                    examples.append({"language": language, "rank": rank, **item})

    control_latin = next(
        row
        for row in results
        if row["language"] == "latin" and row["corpus"] == "naibbe_latin_positive_control"
    )
    target_rows = [row for row in results if row["corpus"].startswith("voynich")]
    decision = (
        "LITERAL_NAIBBE_KEY_REJECTED_ON_F84_FREE_91_FOLIO_CORPUS"
        if control_latin["order_z"] >= 8.0 and all(row["order_z"] <= 0.0 for row in target_rows)
        else "INCONCLUSIVE"
    )
    result = {
        "experiment_id": "GDT601",
        "status": decision,
        "question": "Does the published Naibbe table act as a literal Latin or Italian key on an f84-free Voynich corpus?",
        "configuration": {
            "ngram_order": ORDER,
            "interpolation_alpha": ALPHA,
            "beam": BEAM,
            "within_parsed_run_nulls": NULLS,
            "orientation": "normal token and glyph order",
            "visible_gap_treatment": "parsed options concatenate; unknown tokens reset",
        },
        "sources": SOURCES,
        "voynich_source": {
            "guarded_path": "transcription/voynich_zl3b_lines.tsv",
            "allow_list_source": "gdt327_joint_tuple_interlinear.tsv",
            "physical_folios": len(f84_free_physical_folios()),
            "pages": len({row[2]["page"] for row in corpora["voynich_f84_free_91_folios"]}),
            "lines": len(corpora["voynich_f84_free_91_folios"]),
            "f84": "FORBIDDEN_AND_NOT_MATERIALIZED",
        },
        "coverage": coverage_rows,
        "model_results": results,
        "decision_rule": "positive-control Latin z >= 8 and every Voynich target-language z <= 0",
        "claim_ceiling": "Rejects the exact published Naibbe table under the tested orientation and gap treatment; does not reject every verbose or homophonic cipher and assigns no Voynich plaintext or meaning.",
    }
    (OUT / "gdt601_result.json").write_bytes(json_bytes(result))
    (OUT / "gdt601_top_chance_readings.tsv").write_bytes(
        tsv_bytes(
            [
                "language",
                "rank",
                "locus",
                "page",
                "section",
                "token_count",
                "decoded_chars",
                "score_bits_per_char",
                "rendered",
            ],
            examples,
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
