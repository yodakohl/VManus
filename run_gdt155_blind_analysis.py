#!/usr/bin/env python3
"""Blind form-only HPR2-style analysis of GDT155 diplomatic controls."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt155_blinded_diplomatic.tsv"
FREEZE = ROOT / "gdt155_source_freeze.json"
METHOD = ROOT / "GDT155_MEDIEVAL_ABBREVIATION_POSITIVE_CONTROL_METHOD.md"
TRANS = ROOT / "gdt155_blind_transformations.tsv"
RECT = ROOT / "gdt155_blind_rectangles.tsv"
PARSES = ROOT / "gdt155_blind_group_parses.tsv"
ARCH = ROOT / "gdt155_blind_record_architecture.tsv"
PROFILES = ROOT / "gdt155_blind_record_profiles.tsv"
NEIGHBORS = ROOT / "gdt155_blind_retrieval_neighbors.tsv"
REPORT = ROOT / "GDT155_MEDIEVAL_ABBREVIATION_BLIND_REPORT.md"
RESULT = ROOT / "gdt155_blind_result.json"
BOOKS = ("Band2", "Band3", "Band4", "Band5")
REPRESENTATIONS = (
    "RAW_GROUP_IDENTITY", "RAW_CHAR3", "PAGE_HOST_IDENTITY",
    "PAGE_HOST_CHAR3", "COMPILER_SIGNATURE", "MARKER_AND_POSITION",
    "HOST_PLUS_COMPILER",
)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    assert rows, path
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


FOLD_MAP = str.maketrans({"ſ": "s", "ı": "i", "ȷ": "j", "ẜ": "s"})


def normalize_group(group: str) -> str:
    text = unicodedata.normalize("NFC", group).translate(FOLD_MAP).lower()
    return "".join(ch for ch in text if ch.isalnum() or ch == "¤")


def groups(text: str) -> list[str]:
    return [x for part in text.split() if (x := normalize_group(part))]


def char3(text: str) -> set[str]:
    value = "^" + text + "$"
    return {value[i:i+3] for i in range(max(1, len(value) - 2))}


def discover(token_counts: Counter[str], token_records: dict[str, set[str]]) -> tuple[list[str], list[str], list[dict[str, object]], dict[str, int]]:
    vocab = set(token_counts)
    stats: dict[tuple[str, str], dict[str, object]] = {}
    envelope = Counter()
    for word in sorted(vocab):
        if len(word) < 2:
            continue
        for length in range(1, min(3, len(word) - 1) + 1):
            base = word[length:]
            if base in vocab:
                key = ("LEFT", word[:length]); item = stats.setdefault(key, {"hosts": set(), "pairs": set(), "records": set(), "occurrences": 0})
                item["hosts"].add(base); item["pairs"].add((base, word)); item["records"].update(token_records[base] | token_records[word]); item["occurrences"] += token_counts[word]
                envelope[base] += 1
            base = word[:-length]
            if base in vocab:
                key = ("RIGHT", word[-length:]); item = stats.setdefault(key, {"hosts": set(), "pairs": set(), "records": set(), "occurrences": 0})
                item["hosts"].add(base); item["pairs"].add((base, word)); item["records"].update(token_records[base] | token_records[word]); item["occurrences"] += token_counts[word]
                envelope[base] += 1
    rows = []
    for (side, op), item in stats.items():
        rows.append({
            "side": side, "operation": op, "codepoint_length": len(op),
            "distinct_hosts": len(item["hosts"]), "exact_pair_types": len(item["pairs"]),
            "training_records": len(item["records"]), "transformed_occurrences": item["occurrences"],
            "eligible": int(len(item["hosts"]) >= 8 and len(item["records"]) >= 5),
        })
    rows.sort(key=lambda row: (row["side"], -int(row["distinct_hosts"]), -int(row["exact_pair_types"]), str(row["operation"])))
    left = [str(row["operation"]) for row in rows if row["side"] == "LEFT" and row["eligible"]][:12]
    right = [str(row["operation"]) for row in rows if row["side"] == "RIGHT" and row["eligible"]][:12]
    return left, right, rows, dict(envelope)


def parse_token(token: str, counts: Counter[str], left: list[str], right: list[str], envelope: dict[str, int]) -> dict[str, object]:
    base = token.replace("¤", "")
    marked = int("¤" in token)
    states = {(base, (), ())}
    frontier = {(base, (), ())}
    for _ in range(4):
        nxt = set()
        for host, ls, rs in frontier:
            if len(ls) < 2:
                for op in left:
                    if host.startswith(op) and len(host) > len(op):
                        residual = host[len(op):]
                        if counts[residual] or envelope.get(residual, 0) >= 2:
                            nxt.add((residual, ls + (op,), rs))
            if len(rs) < 2:
                for op in right:
                    if host.endswith(op) and len(host) > len(op):
                        residual = host[:-len(op)]
                        if counts[residual] or envelope.get(residual, 0) >= 2:
                            nxt.add((residual, ls, rs + (op,)))
        nxt -= states
        if not nxt:
            break
        states |= nxt; frontier = nxt
    def rank(state: tuple[str, tuple[str, ...], tuple[str, ...]]) -> tuple:
        host, ls, rs = state
        recurrence = counts[host] + 0.25 * envelope.get(host, 0)
        return (-recurrence, len(ls) + len(rs), -len(host), ls, rs, host)
    host, ls, rs = min(states, key=rank)
    return {
        "surface_group": token, "surface_without_marker": base,
        "outer_left": ls[0] if len(ls) > 0 else "NONE",
        "local_left": ls[1] if len(ls) > 1 else "NONE",
        "page_host": host or "EMPTY",
        "right_outer": rs[0] if len(rs) > 0 else "NONE",
        "right_inner": rs[1] if len(rs) > 1 else "NONE",
        "abbreviation_marker": marked,
        "operation_count": len(ls) + len(rs),
        "host_training_occurrences": counts[host],
        "host_envelope_types": envelope.get(host, 0),
    }


def feature_hash(features: set[str]) -> str:
    return hashlib.sha256("\n".join(sorted(features)).encode()).hexdigest()


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a or b else 0.0


lines = read(SOURCE)
assert len(lines) == 48347 and {row["corpus"] for row in lines} == {"STE1", "NUREMBERG"}
by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in lines:
    by_record[row["record_id"]].append(row)
for values in by_record.values():
    values.sort(key=lambda row: int(row["line_index"]))

record_tokens: dict[str, list[dict[str, object]]] = {}
for record, values in by_record.items():
    out = []
    total_lines = len(values)
    token_ordinal = 0
    all_groups = sum((groups(row["diplomatic_marked"]) for row in values), [])
    total_groups = len(all_groups)
    for row in values:
        row_groups = groups(row["diplomatic_marked"])
        for within, token in enumerate(row_groups, 1):
            token_ordinal += 1
            out.append({
                "token": token, "line_index": int(row["line_index"]),
                "line_count": total_lines, "within_line": within,
                "line_groups": len(row_groups), "token_index": token_ordinal,
                "record_groups": total_groups,
            })
    record_tokens[record] = out

models = {}
trans_rows = []
for held in BOOKS + ("ALL_NUREMBERG",):
    train_records = [record for record, values in by_record.items()
                     if values[0]["corpus"] == "NUREMBERG" and (held == "ALL_NUREMBERG" or values[0]["book_or_ms"] != held)]
    counts = Counter()
    token_records: dict[str, set[str]] = defaultdict(set)
    for record in train_records:
        for item in record_tokens[record]:
            token = str(item["token"]).replace("¤", "")
            if not token:
                continue
            counts[token] += 1; token_records[token].add(record)
    left, right, stats, envelope = discover(counts, token_records)
    models[held] = {"counts": counts, "left": left, "right": right, "envelope": envelope}
    selected = {("LEFT", op) for op in left} | {("RIGHT", op) for op in right}
    for row in stats:
        if (row["side"], row["operation"]) in selected:
            row = dict(row); row.update({
                "fold": held, "training_books": ";".join(book for book in BOOKS if held == "ALL_NUREMBERG" or book != held),
                "selected_rank": (left.index(row["operation"]) + 1) if row["side"] == "LEFT" else (right.index(row["operation"]) + 1),
            }); trans_rows.append(row)

parse_rows = []
parse_maps: dict[str, dict[str, dict[str, object]]] = {}
for held in BOOKS:
    tokens = sorted({str(item["token"]) for record, values in by_record.items() if values[0]["corpus"] == "NUREMBERG" and values[0]["book_or_ms"] == held for item in record_tokens[record]})
    model = models[held]; parse_maps[held] = {}
    for token in tokens:
        parsed = parse_token(token, model["counts"], model["left"], model["right"], model["envelope"])
        parse_maps[held][token] = parsed
        parse_rows.append({"fold": held, "training_books": ";".join(book for book in BOOKS if book != held), **parsed})
model = models["ALL_NUREMBERG"]; parse_maps["Ste1"] = {}
for token in sorted({str(item["token"]) for record, values in by_record.items() if values[0]["corpus"] == "STE1" for item in record_tokens[record]}):
    parsed = parse_token(token, model["counts"], model["left"], model["right"], model["envelope"])
    parse_maps["Ste1"][token] = parsed
    parse_rows.append({"fold": "STE1_TRANSFER", "training_books": ";".join(BOOKS), **parsed})

rect_rows = []
for fold, model in models.items():
    vocab = set(model["counts"])
    for left in model["left"]:
        for right in model["right"]:
            complete = three = two = one = zero = 0
            examples = []
            for host in vocab:
                mask = (host in vocab, left + host in vocab, host + right in vocab, left + host + right in vocab)
                present = sum(mask)
                if present == 4:
                    complete += 1
                    if len(examples) < 5: examples.append(host)
                elif present == 3: three += 1
                elif present == 2: two += 1
                elif present == 1: one += 1
                else: zero += 1
            rect_rows.append({
                "fold": fold, "left_operation": left, "right_operation": right,
                "complete_4_of_4_hosts": complete, "partial_3_of_4_hosts": three,
                "partial_2_of_4_hosts": two, "singleton_hosts": one,
                "example_complete_hosts": ";".join(examples) or "NONE",
            })

profiles: dict[str, dict[str, set[str]]] = {}
profile_rows = []
architecture_acc: dict[tuple, Counter[str]] = defaultdict(Counter)
for record, values in sorted(by_record.items()):
    corpus = values[0]["corpus"]; book = values[0]["book_or_ms"]
    key = book if corpus == "NUREMBERG" else "Ste1"
    parsed_instances = []
    features = {rep: set() for rep in REPRESENTATIONS}
    for item in record_tokens[record]:
        token = str(item["token"]); parsed = parse_maps[key][token]
        raw = token
        host = str(parsed["page_host"])
        sig = "|".join(str(parsed[field]) for field in ("outer_left", "local_left", "right_inner", "right_outer", "abbreviation_marker"))
        lq = min(3, 4 * (int(item["line_index"]) - 1) // max(1, int(item["line_count"])))
        tq = min(3, 4 * (int(item["token_index"]) - 1) // max(1, int(item["record_groups"])))
        features["RAW_GROUP_IDENTITY"].add("W=" + raw)
        features["RAW_CHAR3"].update("C=" + tri for tri in char3(raw))
        features["PAGE_HOST_IDENTITY"].add("H=" + host)
        features["PAGE_HOST_CHAR3"].update("HC=" + tri for tri in char3(host))
        features["COMPILER_SIGNATURE"].add("S=" + sig)
        features["MARKER_AND_POSITION"].add(f"M={parsed['abbreviation_marker']}|LQ={lq}|TQ={tq}")
        features["HOST_PLUS_COMPILER"].add("J=" + host + "@" + sig)
        parsed_instances.append((parsed, item, lq, tq))
        bucket = (corpus, book, lq)
        architecture_acc[bucket]["groups"] += 1
        architecture_acc[bucket]["markers"] += int(parsed["abbreviation_marker"])
        architecture_acc[bucket]["left_ops"] += int(parsed["outer_left"] != "NONE") + int(parsed["local_left"] != "NONE")
        architecture_acc[bucket]["right_ops"] += int(parsed["right_outer"] != "NONE") + int(parsed["right_inner"] != "NONE")
        architecture_acc[bucket]["host_chars"] += len(host)
    profiles[record] = features
    hosts = [str(parsed["page_host"]) for parsed, _, _, _ in parsed_instances]
    profile_rows.append({
        "corpus": corpus, "book_or_ms": book, "record_id": record,
        "pages": ";".join(sorted({row["page_id"] for row in values})),
        "lines": len(values), "groups": len(parsed_instances),
        "abbreviation_marked_groups": sum(int(parsed["abbreviation_marker"]) for parsed, _, _, _ in parsed_instances),
        "unique_raw_groups": len({str(item["token"]) for _, item, _, _ in parsed_instances}),
        "unique_page_hosts": len(set(hosts)), "reused_page_host_occurrences": len(hosts) - len(set(hosts)),
        **{rep.lower() + "_set_sha256": feature_hash(features[rep]) for rep in REPRESENTATIONS},
    })

architecture_rows = []
for (corpus, book, quartile), count in sorted(architecture_acc.items()):
    groups_n = count["groups"]
    architecture_rows.append({
        "corpus": corpus, "book_or_ms": book, "record_position_quartile": quartile,
        "groups": groups_n, "abbreviation_marked_groups": count["markers"],
        "marker_rate": f"{count['markers']/groups_n:.12g}",
        "left_operations_per_group": f"{count['left_ops']/groups_n:.12g}",
        "right_operations_per_group": f"{count['right_ops']/groups_n:.12g}",
        "mean_page_host_length": f"{count['host_chars']/groups_n:.12g}",
    })

neighbor_rows = []
for book in BOOKS:
    records = sorted(record for record, values in by_record.items() if values[0]["book_or_ms"] == book)
    page_sets = {record: {row["page_id"] for row in by_record[record]} for record in records}
    for rep in REPRESENTATIONS:
        for query in records:
            scored = []
            for candidate in records:
                if candidate == query or page_sets[query] & page_sets[candidate]:
                    continue
                scored.append((jaccard(profiles[query][rep], profiles[candidate][rep]), candidate))
            scored.sort(key=lambda item: (-item[0], item[1]))
            for rank, (similarity, candidate) in enumerate(scored[:10], 1):
                neighbor_rows.append({
                    "book": book, "query_record": query, "representation": rep,
                    "candidate_pool": len(scored), "blind_rank": rank,
                    "candidate_record": candidate, "set_jaccard": f"{similarity:.12g}",
                })

write(TRANS, trans_rows); write(RECT, rect_rows); write(PARSES, parse_rows)
write(ARCH, architecture_rows); write(PROFILES, profile_rows); write(NEIGHBORS, neighbor_rows)

top_ops = {}
for fold in BOOKS:
    rows = [row for row in trans_rows if row["fold"] == fold]
    top_ops[fold] = {
        "left": [row["operation"] for row in rows if row["side"] == "LEFT"][:5],
        "right": [row["operation"] for row in rows if row["side"] == "RIGHT"][:5],
    }
complete = sum(int(row["complete_4_of_4_hosts"]) for row in rect_rows if row["fold"] != "ALL_NUREMBERG")
ste_arch = [row for row in architecture_rows if row["corpus"] == "STE1"]
nb_arch = [row for row in architecture_rows if row["corpus"] == "NUREMBERG"]
result = {
    "schema": "GDT155_BLIND_ANALYSIS_RESULT_V1",
    "status": "BLIND_FORMAL_ANALYSIS_COMPLETE_TRUTH_UNEXPOSED",
    "records": len(by_record), "nuremberg_records": sum(values[0]["corpus"] == "NUREMBERG" for values in by_record.values()),
    "ste1_records": sum(values[0]["corpus"] == "STE1" for values in by_record.values()),
    "surface_group_occurrences": sum(len(values) for values in record_tokens.values()),
    "held_books": list(BOOKS), "representations": list(REPRESENTATIONS),
    "selected_operations_per_fold": 24, "complete_rectangle_host_instances_four_folds": complete,
    "top_operations": top_ops,
    "truth_content_sha256": json.loads(FREEZE.read_text(encoding="utf-8"))["truth_content_sha256"],
    "truth_exported_or_used": False,
    "interpretation": "Form-only operator, PAGE_HOST, record architecture, and retrieval objects frozen before expansion truth export.",
    "claim_ceiling": "Blind formal positive-control structure only; no Voynich word, morpheme, sound, language, plaintext, meaning, or translation.",
    "f84": {"voynich_inputs": 0, "accessed": False},
    "inputs": {SOURCE.name: sha(SOURCE), FREEZE.name: sha(FREEZE)},
    "implementation": {Path(__file__).name: sha(Path(__file__))},
    "outputs": {path.name: sha(path) for path in (TRANS, RECT, PARSES, ARCH, PROFILES, NEIGHBORS)},
    "documents": {METHOD.name: sha(METHOD)},
}
result["result_content_sha256"] = csha(result)
RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

all_ops = [row for row in trans_rows if row["fold"] == "ALL_NUREMBERG"]
best_left = next(row for row in all_ops if row["side"] == "LEFT")
best_right = next(row for row in all_ops if row["side"] == "RIGHT")
REPORT.write_text(f"""# GDT155 — blind medieval abbreviation analysis

## Outcome

**BLIND_FORMAL_ANALYSIS_COMPLETE_TRUTH_UNEXPOSED**

The expansion-free panel contains {result['surface_group_occurrences']:,}
surface-group occurrences in {result['nuremberg_records']:,} Nuremberg letter
records plus {result['ste1_records']} Ste1 technical-recipe records.  Each
Nuremberg book was parsed by operations learned only from the other three
books.  Exactly 12 left and 12 right operations were retained in every fold.

The all-Nuremberg source-only leader on the left is `{best_left['operation']}`
with {best_left['distinct_hosts']} exact base hosts; the right leader is
`{best_right['operation']}` with {best_right['distinct_hosts']} hosts.  Across
the four held-book training vocabularies, the 144 fixed left×right operation
pairs contain {complete:,} complete rectangle-host instances.  These are
ordinary form-only contrasts at this stage: inflection, derivation,
abbreviation, orthographic variation, and accidental nesting have not been
distinguished.

For all {result['nuremberg_records']:,} Nuremberg records, the seven frozen
representations now have top-ten same-book retrieval lists after excluding any
candidate sharing a page identifier.  PAGE_HOST, raw surface, compiler, and
marker/position bags are committed before a target is selected from expanded
or regularized text.  Ste1 is parsed only with the complete Nuremberg-trained
operator inventory and remains a two-record descriptive transfer.

No expansion characters, regularized words, addressee/content divisions, or
modern meanings were read or scored by this program.  The next program may
unblind exactly the committed truth and evaluate the frozen objects without
changing operations, representations, query pool, or tie-breaks.  No Voynich
corpus or image is an input, and f84 was not accessed.
""", encoding="utf-8")
print(json.dumps({"status": result["status"], "records": len(by_record), "groups": result["surface_group_occurrences"], "complete_rectangles": complete}, sort_keys=True))
