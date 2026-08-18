#!/usr/bin/env python3
"""Independent integrity checks for the score-blind GDT305 freeze."""
import csv, hashlib, itertools, json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
EXPOSED = R / "gdt303_pair_deltas.tsv"
PAIRS = R / "gdt305_frozen_pairs.tsv"
CAPACITY = R / "gdt305_capacity.tsv"
DESIGN = R / "gdt305_design.json"
OUT = R / "gdt305_design_validation.json"
FIELDS = ("wrapper", "local_frame", "inner_d", "right_family", "dy_closure", "b3")
OPS = {("wrapper", "NONE", "q"), ("wrapper", "ch", "s"), ("wrapper", "d", "s")}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canon(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

checks = []
def check(name, condition):
    if not condition: raise AssertionError(name)
    checks.append(name)

def main():
    design = json.loads(DESIGN.read_text())
    content = design.pop("content_sha256")
    check("design_content_hash", content == canon(design))
    check("design_status", design["status"] == "FROZEN_BEFORE_GDT305_POSITION_SCORING")
    check("f84_forbidden", design["f84"] == {"authorized": False, "joined": False, "opened": False, "parsed": False, "retained": False, "scored": False})
    exposed = {value for row in read(EXPOSED) for value in (row["source_surface_sha256"], row["target_surface_sha256"])}
    forms = defaultdict(lambda: defaultdict(lambda: {"n": 0, "folios": set(), "r": None}))
    source_rows_f84_free = True
    renderer_constant = True
    with SOURCE.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["control_id"] != "VOYNICH_REFERENCE" or int(row["group_count"]) < 2: continue
            source_rows_f84_free &= not row["page"].startswith("f84") and not row["locus"].startswith("f84")
            item = forms[row["page_host"]][row["source_surface_sha256"]]
            item["n"] += 1; item["folios"].add(row["physical_folio"])
            renderer = tuple(row[key] for key in FIELDS)
            if item["r"] is None: item["r"] = renderer
            renderer_constant &= item["r"] == renderer
    check("source_rows_f84_free", source_rows_f84_free)
    check("surface_renderer_constant", renderer_constant)
    expected = []
    for host, mapping in forms.items():
        for (sa, a), (sb, b) in itertools.combinations(sorted(mapping.items()), 2):
            diff = [i for i, values in enumerate(zip(a["r"], b["r"])) if values[0] != values[1]]
            if len(diff) != 1: continue
            i = diff[0]
            for source_sha, source, target_sha, target in ((sa, a, sb, b), (sb, b, sa, a)):
                operation = (FIELDS[i], source["r"][i], target["r"][i])
                if operation not in OPS: continue
                if min(source["n"], target["n"]) < 2 or min(len(source["folios"]), len(target["folios"])) < 2: continue
                if source_sha in exposed or target_sha in exposed: continue
                op = f"{operation[0]}:{operation[1]}>{operation[2]}"
                pair_id = "G305P" + hashlib.sha256(f"{op}|{host}|{source_sha}|{target_sha}".encode()).hexdigest()[:12].upper()
                expected.append((pair_id, op, host, source_sha, target_sha, source["n"], target["n"], len(source["folios"]), len(target["folios"])))
                break
    actual = [(
        row["pair_id"], row["operation"], row["page_host"], row["source_surface_sha256"], row["target_surface_sha256"],
        int(row["source_events"]), int(row["target_events"]), int(row["source_folios"]), int(row["target_folios"]),
    ) for row in read(PAIRS)]
    check("exact_pair_inventory", sorted(actual) == sorted(expected))
    check("expected_pair_count_32", len(actual) == 32)
    counts = defaultdict(lambda: [0, set()])
    for row in read(PAIRS): counts[row["operation"]][0] += 1; counts[row["operation"]][1].add(row["page_host"])
    check("operation_capacity", {key: (value[0], len(value[1])) for key, value in counts.items()} == {"wrapper:NONE>q": (25, 25), "wrapper:ch>s": (2, 2), "wrapper:d>s": (5, 5)})
    cap = {row["operation"]: row for row in read(CAPACITY)}
    check("capacity_rows", set(cap) == set(counts))
    check("input_hashes", all(design["inputs"][name] == sha(R / name) for name in design["inputs"]))
    check("output_hashes", all(design["outputs"][name] == sha(R / name) for name in design["outputs"]))
    result = {"schema": "GDT305_DESIGN_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks,
              "design_sha256": sha(DESIGN), "f84_rows": 0}
    result["content_sha256"] = canon(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "pairs": len(actual)}, sort_keys=True))

if __name__ == "__main__": main()
