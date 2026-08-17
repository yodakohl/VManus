#!/usr/bin/env python3
"""Independently validate GDT207 corpora, scoring, local optima, and bindings."""
from __future__ import annotations

import csv
import ctypes
import hashlib
import json
import math
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from gdt001_core import LETTERS, TARGET_ALPHABET, universal_uint_bits
from run_gdt001_mtf_dynamic_rank import compile_library, static_score

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
BLIND = ROOT / "gdt155_blinded_diplomatic.tsv"
EXPANDED = ROOT / "gdt155_unblinded_lines.tsv"
RUNS = ROOT / "gdt207_mapping_runs.tsv"
PACKS = ROOT / "gdt207_abbreviation_pack_summary.tsv"
SENSITIVITY = ROOT / "gdt207_search_sensitivity.tsv"
RESULT = ROOT / "gdt207_result.json"
OUT = ROOT / "gdt207_validation.json"
UNKNOWN = "f102v2.33"
RIGHT = ("aiin", "air", "ain", "ar", "al")
FOLD = str.maketrans({"ſ": "s", "ı": "i", "ȷ": "j", "ẜ": "s", "ß": "ss"})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_line(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).translate(FOLD).lower()
    out = []
    last_space = True
    for char in value:
        if "a" <= char <= "z":
            out.append(char)
            last_space = False
        elif not last_space:
            out.append(" ")
            last_space = True
    return "".join(out).strip()


def train(lines: list[str]) -> tuple[np.ndarray, int, int]:
    size = len(TARGET_ALPHABET)
    counts = np.zeros((size + 1, size + 1, size), dtype=np.float64)
    letters = groups = 0
    for raw in lines:
        text = normalize_line(raw)
        if not text:
            continue
        groups += len(text.split())
        history = [size, size]
        for value in [TARGET_ALPHABET.index(char) for char in text]:
            counts[history[0], history[1], value] += 1.0
            history = [history[1], value]
            letters += value != 26
    costs = -np.log2((counts + 0.5) / (counts.sum(axis=-1, keepdims=True) + 0.5 * size))
    return np.ascontiguousarray(costs, dtype=np.float64), letters, groups


def source_sequences() -> list[list[int]]:
    rows = []
    with SOURCE.open(encoding="utf8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        for raw in handle:
            parts = raw.rstrip("\n").split("\t")
            locus, page = parts[0], parts[1]
            if locus.startswith("f84") or page.startswith("f84") or locus == UNKNOWN:
                continue
            rows.append(dict(zip(header, parts)))

    def preparse(row):
        host = row["residual_host"]
        if host.endswith("m") and len(host) > 1:
            host = host[:-1]
        for suffix in RIGHT:
            if host.endswith(suffix) and len(host) > len(suffix):
                host = host[:-len(suffix)]
                break
        if row["stripped_prefix"] in {"ch", "che", "sh"} and host.startswith("d") and len(host) > 1:
            host = host[1:]
        return host

    counts = Counter(preparse(row) for row in rows)
    licensed = {host for host in counts if counts[host] and counts["o" + host] and counts["ot" + host]} | {"ar", "al", "ol"}
    by = defaultdict(list)
    for row in rows:
        host = preparse(row)
        if host.startswith("ot") and host[2:] in licensed:
            host = host[2:]
        elif host.startswith("o") and host[1:] in licensed:
            host = host[1:]
        by[row["locus"]].append((int(row["group_index"]), host))
    sequences = []
    for locus, items in sorted(by.items()):
        line = []
        for index, (_, host) in enumerate(sorted(items)):
            if index:
                line.append(25)
            line.extend(LETTERS.index(char) for char in host)
        sequences.append(line)
    return sequences


def source_scope_census():
    f84r = f84_other = 0
    with SOURCE.open(encoding="utf8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        locus_i, page_i = header.index("locus"), header.index("page")
        for raw in handle:
            parts = raw.rstrip("\n").split("\t")
            locus, page = parts[locus_i], parts[page_i]
            if locus.startswith("f84r") or page.startswith("f84r"):
                f84r += 1
            elif locus.startswith("f84") or page.startswith("f84"):
                f84_other += 1
    return f84r, f84_other


def arrays(seqs):
    tokens = []
    offsets = [0]
    for seq in seqs:
        tokens.extend(seq)
        offsets.append(len(tokens))
    return np.asarray(tokens, dtype=np.int32), np.asarray(offsets, dtype=np.int64)


def kt_bits(seqs, active):
    remap = {value: index for index, value in enumerate(sorted(active))}
    space = len(remap)
    outcomes = space + 1
    counts = defaultdict(Counter)
    totals = Counter()
    bits = 0.0
    for seq in seqs:
        history = [-1, -1]
        for old in seq:
            value = space if old == 25 else remap[old]
            context = tuple(history)
            bits -= math.log2((counts[context][value] + 0.5) / (totals[context] + 0.5 * outcomes))
            counts[context][value] += 1
            totals[context] += 1
            history = [history[1], value]
    return bits


def main():
    result = json.loads(RESULT.read_text(encoding="utf8"))
    runs = read(RUNS)
    packs = read(PACKS)
    sensitivity = read(SENSITIVITY)
    diplomatic = {}
    for row in read(BLIND):
        if row["corpus"] == "NUREMBERG":
            diplomatic[row["line_id"]] = row["diplomatic_bare"]
    expanded = {}
    for row in read(EXPANDED):
        if row["corpus"] == "NUREMBERG":
            expanded[row["line_id"]] = row["expanded_diplomatic"]
    checks = []

    def check(name, condition):
        checks.append((name, bool(condition)))

    check("schema", result["schema"] == "GDT207_DIPLOMATIC_ABBREVIATION_LANGUAGE_SCREEN_RESULT_V1")
    check("status", result["status"] == "DIPLOMATIC_ABBREVIATION_RELATIVE_GAIN_DIRECT_DECODER_REJECTED")
    check("parallel_keys", diplomatic.keys() == expanded.keys() and len(diplomatic) == 48337)
    seqs = source_sequences()
    tokens, offsets = arrays(seqs)
    active = {value for seq in seqs for value in seq if value != 25}
    common = 3 + universal_uint_bits(2)
    key_bits = sum(math.log2(26 - index) for index in range(len(active)))
    null_total = kt_bits(seqs, active) + common
    check("source_counts", len(seqs) == 2430 and len(tokens) == 60023 and len(active) == 20)
    pack_data = {
        "REAL_DIPLOMATIC": [diplomatic[key] for key in sorted(diplomatic)],
        "EXPANDED_PARALLEL": [expanded[key] for key in sorted(expanded)],
    }
    api = compile_library()
    best = {}
    for pack, lines in pack_data.items():
        costs, letters, groups = train(lines)
        exported = next(row for row in packs if row["pack"] == pack)
        check("pack_lines:" + pack, int(exported["parallel_lines"]) == len(lines))
        check("pack_letters:" + pack, int(exported["normalized_letter_events"]) == letters)
        check("pack_groups:" + pack, int(exported["normalized_group_events"]) == groups)
        current = []
        for row in [item for item in runs if item["pack"] == pack]:
            mapping = np.asarray([ord(char) - 97 for char in row["full_mapping_order"]], dtype=np.int32)
            active_mapping = "".join(
                f"{chr(97 + index)}>{chr(97 + int(mapping[index]))}"
                for index in sorted(active)
            )
            check("active_mapping:" + pack + ":" + row["seed"], row["active_mapping"] == active_mapping)
            check("mapping_hash:" + pack + ":" + row["seed"], row["mapping_hash"] == hashlib.sha256(active_mapping.encode()).hexdigest())
            payload = static_score(api, tokens, offsets, mapping, costs)
            total = payload + common + 1.0 + key_bits
            check("payload:" + pack + ":" + row["seed"], abs(payload - float(row["payload_bits"])) < 1e-7)
            check("total:" + pack + ":" + row["seed"], abs(total - float(row["paid_total_bits"])) < 1e-7)
            check("gap:" + pack + ":" + row["seed"], abs(total - null_total - float(row["gap_vs_matched_kt_bits"])) < 1e-7)
            minimum = payload
            for left in range(26):
                for right in range(left + 1, 26):
                    changed = mapping.copy()
                    changed[[left, right]] = changed[[right, left]]
                    minimum = min(minimum, static_score(api, tokens, offsets, changed, costs))
            check("local:" + pack + ":" + row["seed"], minimum >= payload - 1e-7 and row["all_pair_swaps_locally_optimal"] == "1")
            current.append((total, row))
        check("three_runs:" + pack, len(current) == 3)
        best[pack] = min(current, key=lambda item: item[0])[1]
    saving = float(best["EXPANDED_PARALLEL"]["paid_total_bits"]) - float(best["REAL_DIPLOMATIC"]["paid_total_bits"])
    check("saving", abs(saving - float(result["comparison"]["diplomatic_saving_bits"])) < 1e-7 and saving > 0)
    check("diplomatic_still_loses", float(best["REAL_DIPLOMATIC"]["gap_vs_matched_kt_bits"]) > 0)
    check("unstable", len({row["mapping_hash"] for row in runs if row["pack"] == "REAL_DIPLOMATIC"}) > 1)
    sensitivity_savings = []
    for seed in (18901, 18902, 18903):
        totals = {}
        for pack in pack_data:
            row = next(item for item in sensitivity if item["pack"] == pack and int(item["seed"]) == seed)
            mapping = np.asarray([0] * 26, dtype=np.int32)
            active_map = {
                piece[0]: piece[2]
                for piece in [row["active_mapping"][index:index + 3] for index in range(0, len(row["active_mapping"]), 3)]
            }
            used_targets = {ord(value) - 97 for value in active_map.values()}
            unused_targets = iter(sorted(set(range(26)) - used_targets))
            for index in range(26):
                mapping[index] = ord(active_map[chr(97 + index)]) - 97 if index in active else next(unused_targets)
            costs, _, _ = train(pack_data[pack])
            payload = static_score(api, tokens, offsets, mapping, costs)
            total = payload + common + 1.0 + key_bits
            check("sensitivity_total:" + pack + ":" + str(seed), abs(total - float(row["paid_total_bits"])) < 1e-7)
            check("sensitivity_local_flag:" + pack + ":" + str(seed), row["all_pair_swaps_locally_optimal"] == "1")
            totals[pack] = total
        sensitivity_savings.append(totals["EXPANDED_PARALLEL"] - totals["REAL_DIPLOMATIC"])
    primary_savings = []
    for seed in (20701, 20702, 20703):
        erow = next(row for row in runs if row["pack"] == "EXPANDED_PARALLEL" and int(row["seed"]) == seed)
        drow = next(row for row in runs if row["pack"] == "REAL_DIPLOMATIC" and int(row["seed"]) == seed)
        primary_savings.append(float(erow["paid_total_bits"]) - float(drow["paid_total_bits"]))
    all_savings = sensitivity_savings + primary_savings
    check("six_shared_start_directions", all(value > 0 for value in all_savings))
    check("sensitivity_range", abs(min(all_savings) - float(result["comparison"]["paired_saving_min_bits"])) < 1e-7 and abs(max(all_savings) - float(result["comparison"]["paired_saving_max_bits"])) < 1e-7)
    check("gates", result["gates"] == {"real_diplomatic_beats_expanded_parallel": True, "real_diplomatic_beats_matched_kt": False, "real_diplomatic_mapping_stable": False, "inverse_transducer_screen_authorized": False})
    f84r_rows, f84_other_rows = source_scope_census()
    check("f84_source_scope", result["f84"]["f84r_rows_in_source"] == f84r_rows == 0 and result["f84"]["other_f84_rows_in_source"] == f84_other_rows == 228)
    check("no_f84_formal_use", result["f84"]["formal_fields_retained"] == result["f84"]["formal_rows_joined"] == result["f84"]["formal_rows_scored"] == 0 and result["f84"]["formal_payload_displayed"] is False)
    for section in ("inputs", "implementation", "outputs", "documents"):
        for filename, digest in result[section].items():
            check("hash:" + filename, sha(ROOT / filename) == digest)
    body = dict(result)
    stored = body.pop("result_content_sha256")
    check("content_hash", content_sha(body) == stored)
    failed = [name for name, passed in checks if not passed]
    validation = {
        "schema": "GDT207_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(passed for _, passed in checks),
        "checks_total": len(checks),
        "failed": failed,
        "result_sha256": sha(RESULT),
        "scope": "Independent corpus normalization, PAGE_HOST reconstruction, LM training, primary and post-hoc retained-map CPU scoring, primary 1,950 pair-swap probes, accounting, gates, seal, and hash validation.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps(validation, sort_keys=True))
    raise SystemExit(bool(failed))


if __name__ == "__main__":
    main()
