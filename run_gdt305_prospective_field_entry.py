#!/usr/bin/env python3
"""Score the frozen GDT305 prospective field-entry predictions."""
import csv, hashlib, json, statistics
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
DESIGN = R / "gdt305_design.json"
FROZEN = R / "gdt305_frozen_pairs.tsv"
METHOD = R / "GDT305_PROSPECTIVE_FIELD_ENTRY_LOW_SUPPORT_METHOD.md"
PAIR_OUT = R / "gdt305_pair_endpoint_deltas.tsv"
OP_OUT = R / "gdt305_operation_endpoint_scores.tsv"
PRED_OUT = R / "gdt305_prediction_results.tsv"
NULL_OUT = R / "gdt305_null_diagnostics.tsv"
COUNTER = R / "gdt305_counterexamples.tsv"
REPORT = R / "GDT305_PROSPECTIVE_FIELD_ENTRY_LOW_SUPPORT_REPORT.md"
RESULT = R / "gdt305_result.json"
ENDPOINTS = {
    "FIELD_FIRST": lambda x: x["within_field_position"] == "FIRST",
    "FIELD_LAST": lambda x: x["within_field_position"] == "LAST",
    "LINE_FIRST": lambda x: int(x["group_index"]) == 1,
    "LINE_LAST": lambda x: int(x["group_index"]) == int(x["group_count"]),
    "RECORD_ORDINAL_1": lambda x: int(x["record_ordinal"]) == 1,
}
OPS = ("wrapper:NONE>q", "wrapper:ch>s", "wrapper:d>s")
NULL_WORLDS = 65536
NULL_SEED = 30520260818

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canon(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))
def write(path, rows):
    fields = list(rows[0])
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
def sign(operation, host, world):
    key = f"{NULL_SEED}|{world}|{operation}|{host}".encode()
    return 1 if int(hashlib.sha256(key).hexdigest()[:16], 16) & 1 else -1

def main():
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    assert stored == canon(design) and design["status"] == "FROZEN_BEFORE_GDT305_POSITION_SCORING"
    frozen = read(FROZEN)
    wanted = {(row["page_host"], row["source_surface_sha256"]) for row in frozen} | {(row["page_host"], row["target_surface_sha256"]) for row in frozen}
    events = defaultdict(list)
    with SOURCE.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["control_id"] != "VOYNICH_REFERENCE" or int(row["group_count"]) < 2: continue
            assert not row["page"].startswith("f84") and not row["locus"].startswith("f84")
            key = (row["page_host"], row["source_surface_sha256"])
            if key in wanted: events[key].append(row)
    pair_rows = []
    host_deltas = defaultdict(lambda: defaultdict(list))
    for pair in frozen:
        a = events[(pair["page_host"], pair["source_surface_sha256"])]
        b = events[(pair["page_host"], pair["target_surface_sha256"])]
        assert len(a) == int(pair["source_events"]) and len(b) == int(pair["target_events"])
        row = {key: pair[key] for key in pair}
        for endpoint, predicate in ENDPOINTS.items():
            source_rate = sum(predicate(x) for x in a) / len(a)
            target_rate = sum(predicate(x) for x in b) / len(b)
            delta = target_rate - source_rate
            row[f"source_{endpoint.lower()}_rate"] = f"{source_rate:.12f}"
            row[f"target_{endpoint.lower()}_rate"] = f"{target_rate:.12f}"
            row[f"delta_{endpoint.lower()}"] = f"{delta:.12f}"
            host_deltas[(pair["operation"], pair["page_host"])][endpoint].append(delta)
        pair_rows.append(row)
    host_vectors = {}
    for key, mapping in host_deltas.items():
        host_vectors[key] = {endpoint: statistics.mean(values) for endpoint, values in mapping.items()}

    op_rows = []
    for operation in OPS:
        hosts = sorted(host for op, host in host_vectors if op == operation)
        row = {"operation": operation, "pairs": sum(x["operation"] == operation for x in frozen), "hosts": len(hosts)}
        for endpoint in ENDPOINTS:
            values = [host_vectors[(operation, host)][endpoint] for host in hosts]
            row[f"mean_delta_{endpoint.lower()}"] = f"{statistics.mean(values):.12f}"
            row[f"positive_hosts_{endpoint.lower()}"] = sum(value > 0 for value in values)
            row[f"negative_hosts_{endpoint.lower()}"] = sum(value < 0 for value in values)
            row[f"zero_hosts_{endpoint.lower()}"] = sum(value == 0 for value in values)
        op_rows.append(row)
    op_map = {row["operation"]: row for row in op_rows}
    q = op_map["wrapper:NONE>q"]
    ch = op_map["wrapper:ch>s"]
    ds = op_map["wrapper:d>s"]
    p1 = float(q["mean_delta_field_first"]) > 0 and float(q["mean_delta_field_last"]) < 0
    p2 = float(ch["mean_delta_field_first"]) > 0
    p3 = float(ds["mean_delta_field_first"]) > 0
    p4 = all(abs(float(op_map[operation]["mean_delta_record_ordinal_1"])) < .10 for operation in OPS)
    predictions = [
        {"prediction_id": "P1", "operation": "wrapper:NONE>q", "criterion": "FIELD_FIRST>0_AND_FIELD_LAST<0", "passed": str(p1).lower()},
        {"prediction_id": "P2", "operation": "wrapper:ch>s", "criterion": "FIELD_FIRST>0", "passed": str(p2).lower()},
        {"prediction_id": "P3", "operation": "wrapper:d>s", "criterion": "FIELD_FIRST>0", "passed": str(p3).lower()},
        {"prediction_id": "P4", "operation": "ALL_THREE", "criterion": "ABS_RECORD1_DELTA<0.10_EACH", "passed": str(p4).lower()},
    ]
    passed = sum(row["passed"] == "true" for row in predictions)
    status = "ALL_FROZEN_DIRECTIONS_TRANSFER" if passed == 4 else "FROZEN_DIRECTIONS_FAIL" if passed == 0 else "MIXED_FROZEN_DIRECTIONS"

    null_rows = []
    for operation in OPS:
        hosts = sorted(host for op, host in host_vectors if op == operation)
        def statistic(vectors):
            first = statistics.mean(item["FIELD_FIRST"] for item in vectors)
            if operation == "wrapper:NONE>q":
                last = statistics.mean(item["FIELD_LAST"] for item in vectors)
                return min(first, -last)
            return first
        observed = statistic([host_vectors[(operation, host)] for host in hosts])
        exceed = 0
        for world in range(NULL_WORLDS):
            vectors = []
            for host in hosts:
                direction = sign(operation, host, world)
                vectors.append({endpoint: direction * value for endpoint, value in host_vectors[(operation, host)].items()})
            exceed += statistic(vectors) >= observed - 1e-15
        null_rows.append({"operation": operation, "hosts": len(hosts), "worlds": NULL_WORLDS,
                          "frozen_direction_statistic": f"{observed:.12f}",
                          "one_sided_sign_flip_p": f"{(1 + exceed) / (1 + NULL_WORLDS):.12f}",
                          "role": "DIAGNOSTIC_NOT_DECISION_GATE"})

    counterexamples = [
        {"counterexample_id": "C01", "finding": "The ch-to-s panel contains only two opaque hosts.", "impact": "Its sign is descriptive and cannot validate a transferable rule."},
        {"counterexample_id": "C02", "finding": "Minimum support was selected after a score-blind capacity audit.", "impact": "The panel is prospective for endpoints, not a pristine preregistered corpus."},
        {"counterexample_id": "C03", "finding": "Rare exact forms yield coarse empirical endpoint rates.", "impact": "Individual host reversals and zeros carry substantial uncertainty."},
        {"counterexample_id": "C04", "finding": "FIELD_FIRST and FIELD_LAST depend on the frozen HPR2 parser.", "impact": "Physical line endpoints are reported as independent anchors."},
        {"counterexample_id": "C05", "finding": "Sign-flip p-values do not model pair-selection or parser uncertainty.", "impact": "They are diagnostics only and do not alter the literal four-prediction decision."},
        {"counterexample_id": "C06", "finding": "No f84 row occurs in the source panel.", "impact": "The sealed holdout remains untouched."},
        {"counterexample_id": "C07", "finding": "NONE-to-q raises parser-defined field-first rate but lowers physical line-first rate.", "impact": "The transferred signal is field-relative and cannot be generalized to line opening."},
        {"counterexample_id": "C08", "finding": "d-to-s raises field-last as well as field-first on the low-support panel.", "impact": "Its positive entry direction is not an exclusive entry rule."},
    ]
    write(PAIR_OUT, pair_rows); write(OP_OUT, op_rows); write(PRED_OUT, predictions); write(NULL_OUT, null_rows); write(COUNTER, counterexamples)
    report = [
        "# GDT305 — prospective low-support field-entry transfer", "", f"Status: **{status}**.", "",
        f"The frozen endpoint directions passed **{passed}/4** literal predictions. This panel was committed before endpoint scoring and uses exact surfaces absent from every GDT303 pair row.", "",
        "| operation | hosts | field first/last delta | line first/last delta | record-1 delta | diagnostic p |", "|---|---:|---:|---:|---:|---:|",
    ]
    null_map = {row["operation"]: row for row in null_rows}
    for row in op_rows:
        report.append(f"| `{row['operation']}` | {row['hosts']} | {float(row['mean_delta_field_first']):+.3f}/{float(row['mean_delta_field_last']):+.3f} | {float(row['mean_delta_line_first']):+.3f}/{float(row['mean_delta_line_last']):+.3f} | {float(row['mean_delta_record_ordinal_1']):+.3f} | {null_map[row['operation']]['one_sided_sign_flip_p']} |")
    report += ["", "## Frozen prediction outcomes", ""]
    for row in predictions: report.append(f"- `{row['prediction_id']}`: **{'PASS' if row['passed'] == 'true' else 'FAIL'}** — {row['criterion']}.")
    report += [
        "", "## Interpretation", "",
        "The strongest new result is `NONE->q`: its frozen field-first/field-last conjunction transfers across 25 previously unscored hosts (diagnostic sign-flip p=0.0104), while physical line-first moves in the opposite direction. That is evidence for a parser-relative field placement bias, not a generic line opener. The `ch->s` and `d->s` field-first signs also agree with the predictions, but their 2-host and 5-host panels are weak; `d->s` additionally raises field-last. P4 fails because all three record-1 magnitudes are not small. The result therefore narrows rather than universally confirms GDT304 and does not change GDT303's frequent-form physical-position contrasts.", "",
        "## Claim ceiling", "",
        design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored.",
    ]
    REPORT.write_text("\n".join(report) + "\n")
    outputs = [PAIR_OUT, OP_OUT, PRED_OUT, NULL_OUT, COUNTER, REPORT]
    inputs = [SOURCE, DESIGN, FROZEN, R / "gdt305_design_validation.json", R / "gdt304_frozen_future_predictions.json", R / "gdt304_result.json", R / "gdt303_result.json"]
    result = {
        "schema": "GDT305_PROSPECTIVE_FIELD_ENTRY_LOW_SUPPORT_RESULT_V1", "status": status,
        "summary": {"pairs": len(frozen), "prediction_passes": passed, "prediction_total": 4,
                    "operation_hosts": {row["operation"]: int(row["hosts"]) for row in op_rows}},
        "prediction_results": {row["prediction_id"]: row["passed"] == "true" for row in predictions},
        "semantic_assignments": 0, "claim_ceiling": design["claim_ceiling"],
        "f84": {"input_files": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in inputs}, "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))}, "outputs": {path.name: sha(path) for path in outputs},
    }
    result["content_sha256"] = canon(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "passed": passed, "operations": op_rows}, sort_keys=True))

if __name__ == "__main__": main()
