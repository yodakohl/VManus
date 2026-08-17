#!/usr/bin/env python3
"""Rank exact q13 PAGE_HOST identities by wrapper-invariant placement and held-folio increment."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt229_q13_semantic_role_lattice.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, data: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(data)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nuisance_key(o: dict[str, object]) -> tuple[str, str, int]:
    n = int(o["field_group_count"])
    size = "1" if n == 1 else "2" if n == 2 else "3" if n == 3 else "4+"
    quartile = min(3, int(float(o["relative_position"]) * 4))
    return size, str(o["line_field_end"]), quartile


def modal(rows: list[dict[str, object]]) -> str:
    counts = Counter(str(r["abstract_role_like"]) for r in rows)
    return sorted(counts, key=lambda x: (-counts[x], x))[0]


def main() -> None:
    fields = read(SOURCE)
    assert len(fields) == 701
    assert all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in fields)
    occ: list[dict[str, object]] = []
    for r in fields:
        tokens = r["source_tokens"].split("|")
        hosts = r["page_hosts"].split("|")
        cells = r["compiler_cells"].split("|")
        assert len(tokens) == len(hosts) == len(cells)
        for token, host, cell in zip(tokens, hosts, cells):
            parts = cell.split(":")
            assert len(parts) == 6
            occ.append({**r, "source_token": token, "page_host": host, "wrapper": parts[0], "right_family": parts[3]})
    assert len(occ) == 1896
    by_host: dict[str, list[dict[str, object]]] = defaultdict(list)
    for o in occ: by_host[str(o["page_host"])].append(o)

    atlas: list[dict[str, object]] = []
    for host, rr in sorted(by_host.items()):
        folios = sorted({str(r["physical_folio"]) for r in rr})
        if len(rr) < 5 or len(folios) < 3: continue
        role_counts = Counter(str(r["abstract_role_like"]) for r in rr)
        dominant = sorted(role_counts, key=lambda x: (-role_counts[x], x))[0]
        purity = role_counts[dominant] / len(rr)
        host_correct = base_correct = total = 0
        for held in folios:
            train = [o for o in occ if o["physical_folio"] != held]
            test = [o for o in rr if o["physical_folio"] == held]
            host_train = [o for o in train if o["page_host"] == host]
            if not host_train: continue
            host_pred = modal(host_train)
            for o in test:
                key = nuisance_key(o)
                matched = [x for x in train if nuisance_key(x) == key]
                if not matched:
                    matched = [x for x in train if nuisance_key(x)[:2] == key[:2]]
                if not matched: matched = train
                base_pred = modal(matched)
                truth = str(o["abstract_role_like"])
                host_correct += int(host_pred == truth)
                base_correct += int(base_pred == truth)
                total += 1
        wrappers = sorted({str(r["wrapper"]) for r in rr})
        rights = sorted({str(r["right_family"]) for r in rr})
        surfaces = sorted({str(r["source_token"]) for r in rr})
        delta = (host_correct - base_correct) / total
        stable = len(rr) >= 8 and len(folios) >= 4 and purity >= .90
        if stable and len(wrappers) >= 2:
            status = "EXTERNAL_CONTENT_TEST_PRIORITY" if delta > 0 else "PLACEMENT_STABLE_NUISANCE_EXPLAINED"
        elif purity >= .90:
            status = "WRAPPER_LIMITED_STABLE"
        elif purity >= .80:
            status = "PROVISIONAL"
        else:
            status = "WEAK"
        atlas.append({
            "page_host": host, "occurrences": len(rr), "folios": len(folios), "pages": len({str(r["page"]) for r in rr}),
            "raw_surface_types": len(surfaces), "wrapper_types": len(wrappers), "right_family_types": len(rights),
            "dominant_abstract_role": dominant, "dominant_purity": f"{purity:.12f}",
            "held_folio_predictions": total, "host_lookup_correct": host_correct,
            "placement_baseline_correct": base_correct, "host_accuracy": f"{host_correct / total:.12f}",
            "placement_accuracy": f"{base_correct / total:.12f}", "host_increment": f"{delta:.12f}",
            "wrappers": "|".join(wrappers), "right_families": "|".join(rights),
            "example_surfaces": "|".join(surfaces[:12]), "priority_status": status,
            "claim_state": "OPAQUE_ADDRESS_CANDIDATE_NO_GLOSS",
        })
    atlas.sort(key=lambda r: ({"EXTERNAL_CONTENT_TEST_PRIORITY": 0, "PLACEMENT_STABLE_NUISANCE_EXPLAINED": 1, "WRAPPER_LIMITED_STABLE": 2, "PROVISIONAL": 3, "WEAK": 4}[str(r["priority_status"])], -float(r["dominant_purity"]), -int(r["occurrences"]), str(r["page_host"])))
    write(ROOT / "gdt230_content_host_atlas.tsv", atlas)

    top = [r for r in atlas if r["priority_status"] in {"EXTERNAL_CONTENT_TEST_PRIORITY", "PLACEMENT_STABLE_NUISANCE_EXPLAINED"}]
    counters = [
        {"counterexample": "PLACEMENT_BASELINE_MEETS_OR_BEATS_ALL_TOP_STABLE_HOSTS", "count": sum(float(r["host_increment"]) <= 0 for r in top), "denominator": len(top), "consequence": "wrapper-invariant placement alone cannot localize content"},
        {"counterexample": "NO_POSITIVE_TOP_PRIORITY_HOST", "count": sum(r["priority_status"] == "EXTERNAL_CONTENT_TEST_PRIORITY" for r in atlas), "denominator": len(atlas), "consequence": "no exact q13 host is promoted to a content address by this endpoint"},
    ]
    write(ROOT / "gdt230_counterexamples.tsv", counters)
    status_counts = Counter(str(r["priority_status"]) for r in atlas)
    result: dict[str, object] = {
        "experiment": "GDT230_Q13_CONTENT_HOST_ATLAS", "status": "WRAPPER_INVARIANT_HOST_PLACEMENT_NUISANCE_EXPLAINED_NO_LEXICAL_CANDIDATE",
        "group_occurrences": len(occ), "eligible_hosts": len(atlas), "status_counts": dict(sorted(status_counts.items())),
        "top_stable_hosts": [r["page_host"] for r in top],
        "top_stable_host_increments": {r["page_host"]: float(r["host_increment"]) for r in top},
        "interpretation": "Several exact hosts preserve broad field placement across wrappers and folios, but none improves on size/closure/position; prioritize external referent acquisition rather than assigning meanings.",
        "claim_ceiling": "Opaque host candidate ranking only; no content address, word, role, meaning, language, plaintext, or translation.",
        "f84": {"retained": False, "joined": False, "scored": False, "new_access": False},
        "inputs": {SOURCE.name: sha(SOURCE)}, "outputs": {}, "documents": {}, "implementation": {},
    }
    for name in ("gdt230_content_host_atlas.tsv", "gdt230_counterexamples.tsv"):
        result["outputs"][name] = sha(ROOT / name)
    for name in ("GDT230_Q13_CONTENT_HOST_ATLAS_METHOD.md", "GDT230_Q13_CONTENT_HOST_ATLAS_REPORT.md"):
        p = ROOT / name
        if p.exists(): result["documents"][name] = sha(p)
    result["implementation"][Path(__file__).name] = sha(Path(__file__))
    clean = dict(result)
    result["content_hash"] = hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (ROOT / "gdt230_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "eligible_hosts": len(atlas), "status_counts": result["status_counts"], "top": result["top_stable_hosts"]}, sort_keys=True))


if __name__ == "__main__": main()
