#!/usr/bin/env python3
"""Independent integrity/science validator for GDT220 (does not import runner)."""
import csv, hashlib, itertools, json
from pathlib import Path

R = Path(__file__).resolve().parent
RES = R / "gdt220_result.json"


def read(name):
    with (R / name).open(encoding="utf8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def sha(name):
    return hashlib.sha256((R / name).read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def main():
    checks = []
    def ck(name, value):
        checks.append((name, bool(value))); assert value, name

    result = json.loads(RES.read_text())
    manifest = read("gdt220_local_assembly_manifest.tsv")
    atlas = read("gdt220_local_reference_atlas.tsv")
    content = read("gdt220_f83_content_diagnostic.tsv")
    counter = read("gdt220_counterexamples.tsv")
    overlaps = read("gdt217_exact_overlaps.tsv")
    ck("seven_manifest", len(manifest) == 7)
    ck("seven_overlaps", len(overlaps) == 7)
    fields = ("representation", "page", "physical_folio", "shared_key", "label_loci", "paragraph_initial_loci")
    ck("exact_overlap_join", {tuple(r[k] for k in fields) for r in manifest} == {tuple(r[k] for k in fields) for r in overlaps})
    ck("no_f84_rows", not any(r["page"].startswith("f84") for r in manifest + atlas))
    same = [r for r in atlas if r["same_parent_reference_candidate"] == "1"]
    diff = [r for r in atlas if r["explicit_counterexample"] == "1"]
    ck("one_same_parent", len(same) == 1 and same[0]["page"] == "f83r")
    ck("two_different", len(diff) == 2 and {r["page"] for r in diff} == {"f75v", "f99v"})
    ck("four_unresolved", sum(r["interpretation"] == "OWNERSHIP_UNRESOLVED" for r in atlas) == 4)
    ck("four_content_lines", len(content) == 4 and {r["paragraph_locus"] for r in content} == {"f83r.52", "f83r.53", "f83r.54", "f83r.55"})
    ar = sum(int(r["exact_arolsy_hosts"]) for r in content)
    ol = sum(int(r["exact_ol_hosts"]) for r in content)
    complete = sum(int(r["complete_hpr2_coverage"]) for r in content)
    ck("no_arolsy", ar == 0 == result["f83"]["exact_arolsy_host_hits"])
    ck("ol_recount", ol == result["f83"]["exact_ol_host_hits"])
    ck("coverage_recount", complete == result["f83"]["complete_hpr2_lines"])
    worlds = list(itertools.permutations(("AB", "AG", "CA")))
    p = sum(w[2] == "CA" for w in worlds) / len(worlds)
    ck("local_exact_tail", len(worlds) == 6 and abs(p - result["f83"]["inclusive_p"]) < 1e-15)
    ck("counterexamples_present", len(counter) == 6)
    ck("status", result["status"] == "FIXED_EDGE_LOCAL_REFERENCE_NOT_ESTABLISHED_F83_CANDIDATE_ONLY")
    ck("content_hash", result["result_content_sha256"] == csha({k: v for k, v in result.items() if k != "result_content_sha256"}))
    for group in ("inputs", "outputs", "documents", "implementation"):
        for name, digest in result[group].items(): ck(f"hash_{name}", sha(name) == digest)
    ck("f84_flags", not any(result["f84"].values()))
    out = {"schema": "GDT220_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks),
           "checks_failed": 0, "result_sha256": hashlib.sha256(RES.read_bytes()).hexdigest(),
           "checks": [name for name, _ in checks]}
    (R / "gdt220_validation.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
