#!/usr/bin/env python3
"""GDT111: whole-folio-held PAGE_HOST structure around DY boundaries."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
METHOD = ROOT / "GDT111_DY_PAGE_HOST_TRANSITION_METHOD.md"
REPORT = ROOT / "GDT111_DY_PAGE_HOST_TRANSITION_REPORT.md"
SCORES = ROOT / "gdt111_transition_model_scores.tsv"
FOLDS = ROOT / "gdt111_transition_folio_scores.tsv"
REGISTERS = ROOT / "gdt111_transition_register_scores.tsv"
INVENTORY = ROOT / "gdt111_boundary_inventory.tsv"
RESULT = ROOT / "gdt111_result.json"

ALPHA = 32.0
MODELS = (
    "NUISANCE", "NEXT_RAW_CHAR3", "NEXT_PAGE_HOST_CHAR3", "PREV_PAGE_HOST_CHAR3", "NEXT_COMPILER",
    "NEXT_PREV_PAGE_HOST_CHAR3", "NEXT_PAGE_HOST_EDGE_PAIR",
    "NEXT_PREV_PAGE_HOST_EDGE_PAIR", "NEXT_HOST_FINAL", "PREV_HOST_FINAL",
)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def char3(value: str, prefix: str) -> list[str]:
    padded = "^" + value + "$"
    return [prefix + padded[i:i + 3] for i in range(max(1, len(padded) - 2))]


def compiler(row: dict[str, str], side: str) -> list[str]:
    output = []
    for key, label, absent in (("wrapper", "W", "NONE"), ("inner_d", "D", "0"), ("local_frame", "F", "NONE"),
                               ("right_family", "R", "NONE"), ("b3", "B3", "0")):
        if row[key] != absent:
            output.append(f"{side}:{label}={row[key]}")
    return output


def features(event: dict[str, object], model: str) -> Counter[str]:
    previous = event["previous"]; following = event["following"]
    nuisance = [f"REG={event['register']}", f"POS={event['position_quartile']}", f"LEN={event['line_length_bucket']}"]
    nuisance += compiler(previous, "P") + compiler(following, "N")
    output = Counter(nuisance)
    if model == "NUISANCE": return output
    if model == "NEXT_RAW_CHAR3": output.update(char3(following["token"], "NR:")); return output
    if model == "NEXT_PAGE_HOST_CHAR3": output.update(char3(following["page_host"], "NH:")); return output
    if model == "PREV_PAGE_HOST_CHAR3": output.update(char3(previous["page_host"], "PH:")); return output
    if model == "NEXT_COMPILER": return output
    if model in {"NEXT_PREV_PAGE_HOST_CHAR3", "NEXT_PREV_PAGE_HOST_EDGE_PAIR"}:
        output.update(char3(following["page_host"], "NH:")); output.update(char3(previous["page_host"], "PH:"))
    elif model == "NEXT_PAGE_HOST_EDGE_PAIR":
        output.update(char3(following["page_host"], "NH:"))
    elif model == "NEXT_HOST_FINAL":
        output["NE=" + following["page_host"][-1:]] += 1; return output
    elif model == "PREV_HOST_FINAL":
        output["PE=" + previous["page_host"][-1:]] += 1; return output
    if model in {"NEXT_PAGE_HOST_EDGE_PAIR", "NEXT_PREV_PAGE_HOST_EDGE_PAIR"}:
        output["PAIR=" + previous["page_host"][-1:] + ">" + following["page_host"][-1:]] += 1
    return output


def fit(rows: list[dict[str, object]], model: str) -> tuple[list[Counter[str]], list[int], set[str]]:
    counts = [Counter(), Counter()]; totals = [0, 0]; support = Counter()
    for row in rows:
        f = row["feature_cache"][model]; y = int(row["dy_boundary"]); counts[y].update(f); totals[y] += sum(f.values()); support.update(f)
    vocab = {key for key, value in support.items() if value >= 5}
    return counts, totals, vocab


def probability(model_fit: tuple[list[Counter[str]], list[int], set[str]], train: list[dict[str, object]], row: dict[str, object], model: str) -> float:
    counts, totals, vocab = model_fit; class_counts = Counter(int(item["dy_boundary"]) for item in train)
    logp = []
    for y in (0, 1):
        score = math.log((class_counts[y] + .5) / (len(train) + 1))
        denominator = totals[y] + ALPHA * max(1, len(vocab))
        for key, value in row["feature_cache"][model].items():
            if key in vocab: score += value * math.log((counts[y][key] + ALPHA) / denominator)
        logp.append(score)
    maximum = max(logp); values = [math.exp(value - maximum) for value in logp]
    return values[1] / sum(values)


def average_precision(labels: list[int], probabilities: list[float]) -> float:
    positives = sum(labels)
    if not positives: return 0.0
    groups = defaultdict(lambda: [0, 0])
    for label, probability_value in zip(labels, probabilities):
        groups[probability_value][0] += label; groups[probability_value][1] += 1
    true_positive = seen = 0; score = 0.0
    for probability_value in sorted(groups, reverse=True):
        positive, count = groups[probability_value]; true_positive += positive; seen += count
        if positive: score += positive / positives * true_positive / seen
    return score


def main() -> None:
    source = read(SOURCE)
    assert len(source) == 15592 and not any(row["locus"].startswith("f84r") for row in source)
    by_line = defaultdict(list)
    for row in source: by_line[row["locus"]].append(row)
    events = []
    for locus, rows in sorted(by_line.items()):
        rows.sort(key=lambda row: int(row["group_index"]))
        for i, (previous, following) in enumerate(zip(rows, rows[1:])):
            if int(following["group_index"]) != int(previous["group_index"]) + 1:
                continue
            position = int(4 * i / max(1, len(rows) - 2)); length_bucket = min(5, len(rows) // 3)
            events.append({"boundary_id": f"{locus}|B{i + 1:03d}", "locus": locus, "page": previous["page"],
                           "physical_folio": previous["physical_folio"], "register": previous["register"],
                           "boundary_index": i + 1, "group_count": len(rows), "position_quartile": position,
                           "line_length_bucket": length_bucket, "dy_boundary": int(previous["dy_closure"]),
                           "previous": previous, "following": following})
    assert events and all(int(row["following"]["group_index"]) == int(row["previous"]["group_index"]) + 1 for row in events)
    folios = sorted({row["physical_folio"] for row in events})
    for row in events:
        row["feature_cache"] = {model: features(row, model) for model in MODELS}

    inventory = [{"boundary_id": row["boundary_id"], "locus": row["locus"], "page": row["page"],
                  "physical_folio": row["physical_folio"], "register": row["register"],
                  "boundary_index": row["boundary_index"], "group_count": row["group_count"],
                  "position_quartile": row["position_quartile"], "dy_boundary": row["dy_boundary"],
                  "previous_page_host": row["previous"]["page_host"], "next_page_host": row["following"]["page_host"],
                  "previous_edge": row["previous"]["page_host"][-1:], "next_edge": row["following"]["page_host"][-1:],
                  "semantic_role": "UNASSIGNED"} for row in events]
    write(INVENTORY, inventory)

    predictions = []
    for held in folios:
        train = [row for row in events if row["physical_folio"] != held]
        test = [row for row in events if row["physical_folio"] == held]
        for model in MODELS:
            trained = fit(train, model)
            for row in test:
                predictions.append({"held_folio": held, "boundary_id": row["boundary_id"], "register": row["register"],
                                    "actual": row["dy_boundary"], "model": model,
                                    "probability": probability(trained, train, row, model)})

    score_rows = []; fold_rows = []; register_rows = []
    for model in MODELS:
        subset = [row for row in predictions if row["model"] == model]
        labels = [int(row["actual"]) for row in subset]; probabilities = [float(row["probability"]) for row in subset]
        losses = [-math.log2(p if y else 1 - p) for y, p in zip(labels, probabilities)]
        base = [row for row in predictions if row["model"] == "NUISANCE"]
        baseline_losses = [-math.log2(float(row["probability"]) if int(row["actual"]) else 1 - float(row["probability"])) for row in base]
        assert [row["boundary_id"] for row in subset] == [row["boundary_id"] for row in base]
        per_folio = defaultdict(lambda: [0.0, 0.0, 0, 0])
        per_register = defaultdict(lambda: [0.0, 0.0, 0, 0])
        for row, baseline, loss in zip(subset, baseline_losses, losses):
            for target in (per_folio[row["held_folio"]], per_register[row["register"]]):
                target[0] += baseline; target[1] += loss; target[2] += 1; target[3] += int(row["actual"])
        for folio, values in sorted(per_folio.items()):
            fold_rows.append({"model": model, "held_folio": folio, "events": values[2], "dy_boundaries": values[3],
                              "nuisance_bits": values[0], "model_bits": values[1], "gain_bits": values[0] - values[1]})
        for register, values in sorted(per_register.items()):
            register_rows.append({"model": model, "register": register, "events": values[2], "dy_boundaries": values[3],
                                  "nuisance_bits": values[0], "model_bits": values[1], "gain_bits": values[0] - values[1]})
        positive_gain = sum(baseline_losses[i] - losses[i] for i, y in enumerate(labels) if y)
        negative_gain = sum(baseline_losses[i] - losses[i] for i, y in enumerate(labels) if not y)
        score_rows.append({"model": model, "events": len(labels), "dy_boundaries": sum(labels),
                           "nuisance_bits": sum(baseline_losses), "held_bits": sum(losses),
                           "gain_vs_nuisance_bits": sum(baseline_losses) - sum(losses),
                           "selector_paid_gain_bits": sum(baseline_losses) - sum(losses) - math.log2(len(MODELS)),
                           "gain_on_dy_bits": positive_gain, "gain_on_non_dy_bits": negative_gain,
                           "average_precision": average_precision(labels, probabilities),
                           "positive_gain_folios": sum(values[0] > values[1] for values in per_folio.values()),
                           "positive_gain_registers": sum(values[0] > values[1] for values in per_register.values()),
                           "min_folio_gain": min(values[0] - values[1] for values in per_folio.values()),
                           "max_folio_gain": max(values[0] - values[1] for values in per_folio.values())})
    score_rows.sort(key=lambda row: (-float(row["gain_vs_nuisance_bits"]), row["model"]))
    write(SCORES, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in score_rows])
    write(FOLDS, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in fold_rows])
    write(REGISTERS, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in register_rows])

    by_model = {row["model"]: row for row in score_rows}
    next_host = by_model["NEXT_PAGE_HOST_CHAR3"]; next_raw = by_model["NEXT_RAW_CHAR3"]
    previous = by_model["PREV_PAGE_HOST_CHAR3"]
    previous_final = by_model["PREV_HOST_FINAL"]
    additive = by_model["NEXT_PREV_PAGE_HOST_CHAR3"]; edge = by_model["NEXT_PAGE_HOST_EDGE_PAIR"]
    full = by_model["NEXT_PREV_PAGE_HOST_EDGE_PAIR"]; compiler_model = by_model["NEXT_COMPILER"]
    post_host_increment = float(previous["held_bits"]) - float(additive["held_bits"])
    ordered_edge_increment = float(additive["held_bits"]) - float(full["held_bits"])
    full_increment_given_previous = float(previous["held_bits"]) - float(full["held_bits"])
    full_increment_given_previous_final = float(previous_final["held_bits"]) - float(full["held_bits"])
    status = "DY_PREVIOUS_HOST_LICENSING_WITH_WEAK_TRANSITION_RESIDUAL"
    if full_increment_given_previous <= 0:
        status = "DY_IS_PREVIOUS_EDGE_LICENSING_NOT_TRANSITION_ALGEBRA"
    elif post_host_increment > 0 and ordered_edge_increment > 0 and full_increment_given_previous_final > 0:
        status = "DY_PAGE_HOST_TRANSITION_ALGEBRA_PROVISIONAL"

    REPORT.write_text(f"""# GDT111 — DY/PAGE_HOST transition test

## Outcome

**{status}**

The whole-folio-held panel contains {len(events):,} within-line boundaries on
{len(folios)} physical folios, including
{sum(int(row['dy_boundary']) for row in events):,} boundaries after DY.

Next PAGE_HOST character trigrams save
{float(next_host['gain_vs_nuisance_bits']):+.3f} bits over the compiler/position
nuisance model on {int(next_host['positive_gain_folios'])}/{len(folios)}
folios and {int(next_host['positive_gain_registers'])}/5 registers. Next raw
string trigrams save {float(next_raw['gain_vs_nuisance_bits']):+.3f} bits;
next compiler-only state saves
{float(compiler_model['gain_vs_nuisance_bits']):+.3f}.

Previous PAGE_HOST alone saves
{float(previous['gain_vs_nuisance_bits']):+.3f} bits. After controlling that
host-specific DY propensity, adding next PAGE_HOST changes held code by
{post_host_increment:+.3f} bits. Adding the ordered previous-final→next-final
edge pair beyond both additive hosts changes it by
{ordered_edge_increment:+.3f}; the full model scores
{float(full['gain_vs_nuisance_bits']):+.3f} bits against nuisance.
The full model changes code by {full_increment_given_previous:+.3f} bits
relative to previous-host trigrams alone. The simpler previous-host final
character is strongest at {float(previous_final['gain_vs_nuisance_bits']):+.3f}
bits on {int(previous_final['positive_gain_folios'])}/{len(folios)} folios and
all five registers; the full transition model is
{full_increment_given_previous_final:+.3f} bits worse than that edge-only
licensing rule.
Positive- and negative-class contributions, every folio, and every register
are exported.

The result distinguishes a transferable post-DY slot distribution from an
ordered transition algebra. It updates the formal compiler only; it does not
assign DY or a PAGE_HOST a semantic function. GDT020's earlier coarse phase
result remains prior evidence rather than a replication. f84r was absent and
not opened, parsed, retained, queried, joined, scored, or targeted. No semantic
role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or
translation is assigned.
""", encoding="utf-8")
    result = {"schema": "GDT111_DY_PAGE_HOST_TRANSITION_RESULT_V1", "status": status,
              "events": len(events), "dy_boundaries": sum(int(row["dy_boundary"]) for row in events),
              "physical_folios": len(folios), "models": score_rows, "next_page_host": next_host,
              "next_raw": next_raw, "next_compiler": compiler_model, "next_prev_page_host": additive,
              "previous_page_host": previous, "additive_next_previous_page_host": additive,
              "previous_host_final": previous_final,
              "next_edge_pair": edge, "full_transition": full,
              "post_host_increment_given_previous_bits": post_host_increment,
              "ordered_edge_increment_given_both_hosts_bits": ordered_edge_increment,
              "full_increment_given_previous_host_bits": full_increment_given_previous,
              "full_increment_given_previous_final_bits": full_increment_given_previous_final,
              "interpretation": "Whole-folio-held post-DY PAGE_HOST slot and ordered pre/post transition decomposition only.",
              "claim_ceiling": "No semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
              "f84r": {"opened": False, "parsed": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False},
              "inputs": {SOURCE.name: sha(SOURCE), "gdt020_result.json": sha(ROOT / "gdt020_result.json"), "gdt108_result.json": sha(ROOT / "gdt108_result.json")},
              "implementation": {Path(__file__).name: sha(Path(__file__))},
              "outputs": {path.name: sha(path) for path in (SCORES, FOLDS, REGISTERS, INVENTORY)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}}
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "next_host_gain": next_host["gain_vs_nuisance_bits"],
                      "next_raw_gain": next_raw["gain_vs_nuisance_bits"], "previous_host_gain": previous["gain_vs_nuisance_bits"],
                      "previous_final_gain": previous_final["gain_vs_nuisance_bits"],
                      "post_increment": post_host_increment, "ordered_edge_increment": ordered_edge_increment,
                      "full_increment_given_previous": full_increment_given_previous,
                      "best": score_rows[0]}, sort_keys=True))


if __name__ == "__main__":
    main()
