#!/usr/bin/env python3
from __future__ import annotations

import os

import csv
import hashlib
import itertools
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path(os.environ.get("GDT612_WORK", Path(__file__).resolve().parent)).resolve()
PREP = WORK / "prepared"
OUT = WORK / "evaluation"
ROLE_CORE = {"literal_carrier", "syllabic_carrier"}
ROLE_BOUNDARY = {"connector", "wholeform_logogram"}


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, fields, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class BackoffModel:
    def __init__(self, words, alpha=.25):
        self.alpha = alpha
        self.counts = [Counter() for _ in range(4)]
        self.totals = [Counter() for _ in range(4)]
        stream = " ".join(words)
        for i, char in enumerate(stream):
            self.counts[0][char] += 1
            for order in range(1, 4):
                if i >= order:
                    context = stream[i - order:i]
                    self.counts[order][(context, char)] += 1
                    self.totals[order][context] += 1
        self.total = sum(self.counts[0].values())

    def probability(self, context, char):
        lower = (self.counts[0][char] + 1) / (self.total + 27)
        for order in range(1, min(3, len(context)) + 1):
            ctx = context[-order:]
            strength = self.alpha * 27
            lower = (self.counts[order][(ctx, char)] + strength * lower) / (self.totals[order][ctx] + strength)
        return lower

    def score(self, words):
        if not words:
            return -25.0, 0
        context = "   "
        score = 0.0
        letters = 0
        for wi, word in enumerate(words):
            if wi:
                score += math.log2(self.probability(context, " "))
                context = (context + " ")[-3:]
            for char in word:
                score += math.log2(self.probability(context, char))
                context = (context + char)[-3:]
                letters += 1
        score += math.log2(self.probability(context, " "))
        return score, letters


class Architecture:
    def __init__(self):
        self.units = {int(r["unit_id"]): r for r in read_tsv(PREP / "units.tsv")}
        self.unit_name = {uid: row["unit"] for uid, row in self.units.items()}

    def load_key(self, directory):
        mapping = {}
        for row in read_tsv(Path(directory) / "primitive_mapping.tsv"):
            mapping[int(row["primitive_id"])] = (row["role"], "" if row["output"] == "<EMPTY>" else row["output"])
        overrides = {}
        for row in read_tsv(Path(directory) / "merge_overrides.tsv"):
            overrides[int(row["unit_id"])] = (row["type"], row["output"])
        return mapping, overrides

    def pieces(self, uid, mapping, overrides, memo):
        if uid in memo:
            return memo[uid]
        unit = self.units[uid]
        if uid in overrides:
            kind, output = overrides[uid]
            result = [("wholeform_logogram" if kind == "wholeform" else "syllabic_carrier", output)]
        elif unit["is_primitive"] == "1":
            result = [mapping[int(unit["primitive_id"])]]
        else:
            result = self.pieces(int(unit["left_unit_id"]), mapping, overrides, memo) + self.pieces(int(unit["right_unit_id"]), mapping, overrides, memo)
        memo[uid] = result
        return result

    @staticmethod
    def grammar_violation(roles):
        if not roles:
            return 0
        cores = [i for i, role in enumerate(roles) if role in ROLE_CORE]
        if not cores:
            return len(roles)
        first, last = cores[0], cores[-1]
        violations = 0
        for i, role in enumerate(roles):
            if role == "prefix_operator" and i > first:
                violations += 1
            if role == "suffix_operator" and i < last:
                violations += 1
            if role == "context_abbreviation_mark":
                if not ((i > 0 and roles[i - 1] in ROLE_CORE) or (i + 1 < len(roles) and roles[i + 1] in ROLE_CORE)):
                    violations += 1
            if role in ROLE_CORE | {"context_abbreviation_mark", "prefix_operator"} and i > last:
                if "suffix_operator" in roles[last + 1:i]:
                    violations += 1
        return violations

    def decode(self, sequence, mapping, overrides, with_spans=False):
        memo = {}
        words, spans = [], []
        current, roles, start, end = "", [], None, None

        def flush():
            nonlocal current, roles, start, end
            if current:
                words.append(current)
                spans.append((start, end, len(words) - 1, current))
            current, roles, start, end = "", [], None, None

        for position, uid in enumerate(sequence):
            for role, output in self.pieces(uid, mapping, overrides, memo):
                if role == "null_layout" or not output:
                    continue
                if role in ROLE_BOUNDARY:
                    flush()
                    words.append(output)
                    spans.append((position, position, len(words) - 1, output))
                else:
                    if start is None:
                        start = position
                    end = position
                    current += output
                    roles.append(role)
        flush()
        return (words, spans) if with_spans else words


def levenshtein(a, b):
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def run_directories():
    rows = []
    for language, base in (("latin", 1100), ("old_italian", 2100), ("middle_high_german", 3100)):
        for kind, offsets in (("real", range(1, 7)), ("destroyed", range(91, 94))):
            for offset in offsets:
                seed = base + offset
                directory = WORK / f"target_runs/{language}/{kind}/seed_{seed}"
                if not (directory / "summary.tsv").exists():
                    raise RuntimeError(f"missing job {directory}")
                rows.append((language, kind, seed, directory))
    return rows


def synthetic_evaluation(architecture):
    truth_mapping = {
        int(r["primitive_id"]): (r["role"], "" if r["output"] == "<EMPTY>" else r["output"])
        for r in read_tsv(WORK / "synthetic/truth_primitives.tsv")
    }
    truth_overrides = {
        int(r["unit_id"]): (r["type"], r["output"])
        for r in read_tsv(WORK / "synthetic/truth_overrides.tsv")
    }
    held = read_tsv(WORK / "synthetic/held.tsv")
    for row in held:
        seq = [int(x) for x in row["units"].split(",")]
        decoded = " ".join(architecture.decode(seq, truth_mapping, truth_overrides))
        if decoded != row["plaintext"]:
            raise RuntimeError(f"synthetic truth mismatch at {row['record_id']}: {decoded} != {row['plaintext']}")
    rows = []
    mappings = []
    for seed in range(7001, 7007):
        directory = WORK / f"synthetic/runs/seed_{seed}"
        estimated, overrides = architecture.load_key(directory)
        mappings.append(estimated)
        role_exact = sum(estimated[pid][0] == truth_mapping[pid][0] for pid in truth_mapping)
        output_exact = sum(estimated[pid] == truth_mapping[pid] for pid in truth_mapping)
        truth_override_exact = sum(overrides.get(uid) == value for uid, value in truth_overrides.items())
        predicted_override_precision = sum(truth_overrides.get(uid) == value for uid, value in overrides.items()) / max(1, len(overrides))
        exact, edit_distance, total_chars = 0, 0, 0
        for row in held:
            seq = [int(x) for x in row["units"].split(",")]
            decoded = " ".join(architecture.decode(seq, estimated, overrides))
            truth = row["plaintext"]
            exact += decoded == truth
            edit_distance += levenshtein(decoded, truth)
            total_chars += max(len(decoded), len(truth))
        summary = read_tsv(directory / "summary.tsv")[0]
        rows.append({
            "seed": seed,
            "primitive_role_exact": role_exact,
            "primitive_role_output_exact": output_exact,
            "truth_override_exact": truth_override_exact,
            "predicted_override_precision": f"{predicted_override_precision:.9f}",
            "held_word_exact": exact,
            "held_word_total": len(held),
            "held_exact_rate": f"{exact / len(held):.9f}",
            "held_normalized_char_similarity": f"{1 - edit_distance / max(1, total_chars):.9f}",
            "train_objective": summary["train_objective_per_sqrt_weight"],
        })
    pair_agreement = []
    for left, right in itertools.combinations(mappings, 2):
        pair_agreement.append(sum(left[pid] == right[pid] for pid in range(34)) / 34)
    write_tsv(OUT / "synthetic_recovery.tsv", list(rows[0]), rows)
    return {
        "truth_decode_rate": 1.0,
        "runs": len(rows),
        "primitive_role_exact_range": [min(int(r["primitive_role_exact"]) for r in rows), max(int(r["primitive_role_exact"]) for r in rows)],
        "primitive_role_output_exact_range": [min(int(r["primitive_role_output_exact"]) for r in rows), max(int(r["primitive_role_output_exact"]) for r in rows)],
        "override_exact_range": [min(int(r["truth_override_exact"]) for r in rows), max(int(r["truth_override_exact"]) for r in rows)],
        "held_exact_rate_range": [min(float(r["held_exact_rate"]) for r in rows), max(float(r["held_exact_rate"]) for r in rows)],
        "held_char_similarity_range": [min(float(r["held_normalized_char_similarity"]) for r in rows), max(float(r["held_normalized_char_similarity"]) for r in rows)],
        "restart_primitive_pair_agreement_mean": statistics.mean(pair_agreement),
    }


def target_evaluation(architecture):
    held = read_tsv(PREP / "held_chunks.tsv")
    held_lines = read_tsv(PREP / "held_lines.tsv")
    words_by_language = {}
    models = {}
    reference_baselines = []
    for language in ("latin", "old_italian", "middle_high_german"):
        real = (PREP / f"packs/{language}_real_words.txt").read_text(encoding="ascii").splitlines()
        destroyed = (PREP / f"packs/{language}_destroyed_words.txt").read_text(encoding="ascii").splitlines()
        words_by_language[language] = set(real)
        models[language] = (BackoffModel(real), BackoffModel(destroyed))
        counts = Counter(real)
        total = len(real)
        entropy = -sum((count / total) * math.log2(count / total) for count in counts.values())
        reference_baselines.append({
            "language": language, "words": total, "word_types": len(counts),
            "top_token": counts.most_common(1)[0][0],
            "top_token_fraction": f"{counts.most_common(1)[0][1] / total:.12f}",
            "top10_token_fraction": f"{sum(count for _word, count in counts.most_common(10)) / total:.12f}",
            "token_entropy_bits": f"{entropy:.12f}",
        })
    write_tsv(OUT / "reference_baselines.tsv", list(reference_baselines[0]), reference_baselines)
    locus_to_paragraph = {row["locus"]: row["paragraph_id"] for row in held_lines}
    line_order = {row["locus"]: (row["paragraph_id"], int(row["paragraph_line_index"])) for row in held_lines}
    jobs = []
    token_frequency_rows = []
    job_decodes = {}
    job_spans = {}
    paragraph_rows = []
    keys = {}
    for language, kind, seed, directory in run_directories():
        mapping, overrides = architecture.load_key(directory)
        keys[(language, kind, seed)] = (mapping, overrides)
        real_model, destroyed_model = models[language]
        lexicon = words_by_language[language]
        decode_rows, span_map = [], {}
        all_words = []
        known_chars = total_letters = empty = 0
        paragraph_chunks = defaultdict(lambda: defaultdict(list))
        for row in held:
            sequence = [int(x) for x in row["units"].split(",")]
            words, spans = architecture.decode(sequence, mapping, overrides, with_spans=True)
            all_words.extend(words)
            letters = sum(map(len, words))
            total_letters += letters
            known_chars += sum(len(word) for word in words if len(word) >= 2 and word in lexicon)
            empty += not words
            record_id = int(row["record_id"])
            for start, end, ordinal, word in spans:
                span_map[(record_id, start, end, ordinal)] = word
            text = " ".join(words)
            decode_rows.append({**row, "decoded_words": "|".join(words), "decoded_text": text, "decoded_letters": letters})
            pid = locus_to_paragraph[row["locus"]]
            paragraph_chunks[pid][row["locus"]].append((int(row["chunk_index"]), text))
        token_counts = Counter(all_words)
        token_total = sum(token_counts.values())
        token_entropy = -sum((count / token_total) * math.log2(count / token_total) for count in token_counts.values()) if token_total else 0.0
        for rank, (token, count) in enumerate(sorted(token_counts.items(), key=lambda item: (-item[1], item[0])), 1):
            token_frequency_rows.append({
                "language": language, "kind": kind, "seed": seed, "rank": rank,
                "token": token, "count": count, "fraction": f"{count / max(1, token_total):.12f}",
                "in_reference_lexicon": int(token in lexicon),
            })
        real_score, _ = real_model.score(all_words)
        destroyed_score, _ = destroyed_model.score(all_words)
        order_margin = (real_score - destroyed_score) / max(1, total_letters)
        summary = read_tsv(directory / "summary.tsv")[0]
        jobs.append({
            "language": language, "kind": kind, "seed": seed,
            "train_objective_per_sqrt_weight": summary["train_objective_per_sqrt_weight"],
            "active_overrides": summary["active_overrides"], "wholeform_overrides": summary["wholeform_overrides"],
            "null_primitive": summary["null_primitive"], "null_leaf_mass": summary["null_leaf_mass"],
            "held_chunks": len(held), "held_letters": total_letters, "empty_chunks": empty,
            "held_words": token_total, "held_word_types": len(token_counts),
            "top_token": token_counts.most_common(1)[0][0] if token_counts else "<EMPTY>",
            "top_token_fraction": f"{token_counts.most_common(1)[0][1] / max(1, token_total):.12f}" if token_counts else "0",
            "top10_token_fraction": f"{sum(count for _token, count in token_counts.most_common(10)) / max(1, token_total):.12f}",
            "token_entropy_bits": f"{token_entropy:.12f}",
            "held_order_signal_bits_per_letter": f"{order_margin:.12f}",
            "held_lexicon_char_coverage": f"{known_chars / max(1, total_letters):.12f}",
        })
        key = (language, kind, seed)
        job_decodes[key] = decode_rows
        job_spans[key] = span_map
        write_tsv(OUT / f"decodes/{language}_{kind}_{seed}.tsv", list(decode_rows[0]), decode_rows)

        if kind == "real":
            for paragraph_id, loci in paragraph_chunks.items():
                ordered = []
                for locus in sorted(loci, key=lambda x: line_order[x][1]):
                    line = " / ".join(text for _idx, text in sorted(loci[locus]))
                    ordered.append(line)
                text = " || ".join(ordered)
                para_words = [word for line in ordered for word in line.replace(" / ", " ").split()]
                rscore, plen = real_model.score(para_words)
                dscore, _ = destroyed_model.score(para_words)
                known = sum(len(word) for word in para_words if len(word) >= 2 and word in lexicon)
                first_line = next(row for row in held_lines if row["paragraph_id"] == paragraph_id)
                paragraph_rows.append({
                    "language": language, "seed": seed, "paragraph_id": paragraph_id,
                    "page": first_line["page"], "physical_folio": first_line["physical_folio"],
                    "line_count": len(loci), "letters": plen,
                    "order_signal_bits_per_letter": f"{(rscore - dscore) / max(1, plen):.12f}",
                    "lexicon_char_coverage": f"{known / max(1, plen):.12f}",
                    "decoded_paragraph": text,
                })
    write_tsv(OUT / "held_run_metrics.tsv", list(jobs[0]), jobs)
    write_tsv(OUT / "held_token_frequencies.tsv", list(token_frequency_rows[0]), token_frequency_rows)
    write_tsv(OUT / "held_paragraphs.tsv", list(paragraph_rows[0]), paragraph_rows)

    # Stability is computed solely among the six preregistered real starts.
    consensus_rows, stability_rows, stable_unit_rows, stable_span_rows, override_rows, anchor_rows = [], [], [], [], [], []
    for language in ("latin", "old_italian", "middle_high_german"):
        run_keys = [(language, "real", base) for base in ({"latin": range(1101, 1107), "old_italian": range(2101, 2107), "middle_high_german": range(3101, 3107)}[language])]
        primitive_runs = [keys[key][0] for key in run_keys]
        override_runs = [keys[key][1] for key in run_keys]
        pair_role, pair_exact, pair_unit = [], [], []
        unit_tables = [
            {int(row["unit_id"]): row["decoded_text"] for row in read_tsv(WORK / f"target_runs/{language}/real/seed_{key[2]}/unit_mapping.tsv")}
            for key in run_keys
        ]
        for left, right in itertools.combinations(range(6), 2):
            pair_role.append(sum(primitive_runs[left][pid][0] == primitive_runs[right][pid][0] for pid in range(34)) / 34)
            pair_exact.append(sum(primitive_runs[left][pid] == primitive_runs[right][pid] for pid in range(34)) / 34)
            pair_unit.append(sum(unit_tables[left][uid] == unit_tables[right][uid] for uid in range(98)) / 98)
        unanimous_primitive = unanimous_unit = 0
        for pid in range(34):
            values = [run[pid] for run in primitive_runs]
            role_counts = Counter(value[0] for value in values)
            output_counts = Counter(value[1] for value in values)
            pair_counts = Counter(values)
            role_mode, role_support = role_counts.most_common(1)[0]
            output_mode, output_support = output_counts.most_common(1)[0]
            pair_mode, pair_support = pair_counts.most_common(1)[0]
            unanimous_primitive += pair_support == 6
            primitive_name = next(r["primitive"] for r in read_tsv(PREP / "primitives.tsv") if int(r["primitive_id"]) == pid)
            consensus_rows.append({
                "language": language, "carrier_level": "primitive", "carrier_id": pid, "carrier": primitive_name,
                "modal_role": role_mode, "role_support_of_6": role_support,
                "modal_output": output_mode or "<EMPTY>", "output_support_of_6": output_support,
                "modal_exact_pair": f"{pair_mode[0]}:{pair_mode[1] or '<EMPTY>'}", "exact_pair_support_of_6": pair_support,
            })
            if primitive_name in {"C", "d", "y", "o"}:
                for index, key in enumerate(run_keys):
                    anchor_rows.append({
                        "language": language, "seed": key[2], "carrier": primitive_name,
                        "role": values[index][0], "output": values[index][1] or "<EMPTY>", "level": "primitive",
                    })
        for uid in range(98):
            values = [table[uid] for table in unit_tables]
            mode, support = Counter(values).most_common(1)[0]
            unanimous_unit += support == 6
            consensus_rows.append({
                "language": language, "carrier_level": "unit", "carrier_id": uid, "carrier": architecture.unit_name[uid],
                "modal_role": "", "role_support_of_6": "", "modal_output": mode or "<EMPTY>",
                "output_support_of_6": support, "modal_exact_pair": "", "exact_pair_support_of_6": support,
            })
            if support == 6 and len(mode) >= 2 and mode in words_by_language[language]:
                stable_unit_rows.append({
                    "language": language, "unit_id": uid, "unit": architecture.unit_name[uid],
                    "exact_output": mode, "support_of_6": 6,
                })
            if architecture.unit_name[uid] in {"ol", "qok"}:
                for index, key in enumerate(run_keys):
                    anchor_rows.append({
                        "language": language, "seed": key[2], "carrier": architecture.unit_name[uid],
                        "role": "composed_unit", "output": values[index] or "<EMPTY>", "level": "unit",
                    })
        all_override_ids = sorted(set().union(*(set(x) for x in override_runs)))
        for uid in all_override_ids:
            values = [run.get(uid) for run in override_runs]
            mode, support = Counter(values).most_common(1)[0]
            override_rows.append({
                "language": language, "unit_id": uid, "unit": architecture.unit_name[uid],
                "modal_override": "NONE" if mode is None else f"{mode[0]}:{mode[1]}",
                "support_of_6": support,
            })
        span_maps = [job_spans[key] for key in run_keys]
        common_spans = set.intersection(*(set(mapping) for mapping in span_maps))
        stable = 0
        stable_positions = set()
        for span in sorted(common_spans):
            values = [mapping[span] for mapping in span_maps]
            if len(set(values)) != 1:
                continue
            stable += 1
            record_id, start, end, ordinal = span
            source = held[record_id]
            source_units = source["unit_names"].split()[start:end + 1]
            output = values[0]
            stable_positions.update((record_id, pos) for pos in range(start, end + 1))
            stable_span_rows.append({
                "language": language, "record_id": record_id, "page": source["page"], "locus": source["locus"],
                "start_unit": start, "end_unit": end, "word_ordinal": ordinal,
                "source_units": " ".join(source_units), "exact_output": output,
                "support_of_6": 6, "in_reference_lexicon": int(output in words_by_language[language]),
            })
        total_positions = sum(len(row["units"].split(",")) for row in held)
        stability_rows.append({
            "language": language,
            "primitive_role_pairwise_agreement": f"{statistics.mean(pair_role):.12f}",
            "primitive_role_output_pairwise_agreement": f"{statistics.mean(pair_exact):.12f}",
            "unit_output_pairwise_agreement": f"{statistics.mean(pair_unit):.12f}",
            "unanimous_primitive_role_output_of_34": unanimous_primitive,
            "unanimous_unit_output_of_98": unanimous_unit,
            "unanimous_held_word_spans": stable,
            "stable_held_source_position_coverage": f"{len(stable_positions) / total_positions:.12f}",
            "stable_unit_reference_words": sum(row["language"] == language for row in stable_unit_rows),
            "stable_span_reference_words": sum(row["language"] == language and row["in_reference_lexicon"] for row in stable_span_rows),
        })
    write_tsv(OUT / "carrier_consensus.tsv", list(consensus_rows[0]), consensus_rows)
    write_tsv(OUT / "carrier_stability.tsv", list(stability_rows[0]), stability_rows)
    write_tsv(OUT / "stable_unit_reference_outputs.tsv", ["language", "unit_id", "unit", "exact_output", "support_of_6"], stable_unit_rows)
    write_tsv(OUT / "stable_held_spans.tsv", [
        "language", "record_id", "page", "locus", "start_unit", "end_unit", "word_ordinal", "source_units", "exact_output", "support_of_6", "in_reference_lexicon",
    ], stable_span_rows)
    write_tsv(OUT / "override_consensus.tsv", ["language", "unit_id", "unit", "modal_override", "support_of_6"], override_rows)
    write_tsv(OUT / "anchor_audit.tsv", ["language", "seed", "carrier", "role", "output", "level"], anchor_rows)

    eligible_paragraphs = [row for row in paragraph_rows if int(row["letters"]) >= 50]
    best = max(eligible_paragraphs, key=lambda row: (float(row["order_signal_bits_per_letter"]), float(row["lexicon_char_coverage"]), int(row["letters"])))
    (OUT / "best_held_paragraph.json").write_text(json.dumps(best, indent=2, sort_keys=True) + "\n")
    return {
        "jobs": len(jobs),
        "real_jobs": sum(row["kind"] == "real" for row in jobs),
        "destroyed_jobs": sum(row["kind"] == "destroyed" for row in jobs),
        "held_chunks_per_job": len(held),
        "held_folios": len({row["physical_folio"] for row in held}),
        "held_paragraphs": len({row["paragraph_id"] for row in held_lines}),
        "best_held_paragraph": best,
        "stability": stability_rows,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    architecture = Architecture()
    synthetic = synthetic_evaluation(architecture)
    target = target_evaluation(architecture)
    runtime = {
        "synthetic": json.loads((WORK / "runtime_synthetic.json").read_text()),
        "target": json.loads((WORK / "runtime_target.json").read_text()),
    }
    result = {
        "schema": "historical34-e2e-evaluation-v1",
        "synthetic": synthetic,
        "target": target,
        "runtime": {
            kind: {
                "jobs": len(rows), "sum_cpu_proxy_wall_seconds": sum(row["wall_seconds"] for row in rows),
                "min_job_wall_seconds": min(row["wall_seconds"] for row in rows),
                "max_job_wall_seconds": max(row["wall_seconds"] for row in rows),
            }
            for kind, rows in runtime.items()
        },
        "source_hashes": {
            "prepare.py": sha(WORK / "prepare.py"), "decoder.cpp": sha(WORK / "decoder.cpp"),
            "make_synthetic.py": sha(WORK / "make_synthetic.py"), "run_all.py": sha(WORK / "run_all.py"),
            "evaluate.py": sha(WORK / "evaluate.py"), "prepared_manifest": sha(PREP / "MANIFEST.json"),
        },
    }
    (OUT / "RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"synthetic": synthetic, "target_jobs": target["jobs"], "best": target["best_held_paragraph"]}, sort_keys=True))


if __name__ == "__main__":
    main()
