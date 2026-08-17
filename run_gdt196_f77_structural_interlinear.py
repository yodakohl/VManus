#!/usr/bin/env python3
"""Build a complete strict f77r structural interlinear and label/prose bridge."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
STEPS = ROOT / "gdt180_f77_process_steps.tsv"
METHOD = ROOT / "GDT196_F77_STRUCTURAL_INTERLINEAR_METHOD.md"
REPORT = ROOT / "GDT196_F77_STRUCTURAL_INTERLINEAR_REPORT.md"
INTERLINEAR = ROOT / "gdt196_f77_structural_interlinear.tsv"
ECHOES = ROOT / "gdt196_label_prose_echoes.tsv"
COUNTER = ROOT / "gdt196_counterexamples.tsv"
RESULT = ROOT / "gdt196_result.json"
RIGHT = ("aiin", "air", "ain", "ar", "al")
PREFIXES = ("che", "ch", "sh", "t", "s", "d", "q")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def strip_layers(token: str) -> tuple[str, str, int]:
    prefix, host = "NONE", token
    for candidate in PREFIXES:
        if host.startswith(candidate) and len(host) > len(candidate):
            prefix, host = candidate, host[len(candidate):]
            break
    dy = int(host.endswith("dy") and len(host) > 2)
    if dy:
        host = host[:-2]
    return prefix, host, dy


def preparse(wrapper: str, residual: str) -> tuple[str, int, str, int]:
    host = residual
    b3 = int(host.endswith("m") and len(host) > 1)
    if b3:
        host = host[:-1]
    right = "NONE"
    for suffix in RIGHT:
        if host.endswith(suffix) and len(host) > len(suffix):
            host, right = host[: -len(suffix)], suffix
            break
    inner_d = int(wrapper in {"ch", "che", "sh"} and host.startswith("d") and len(host) > 1)
    if inner_d:
        host = host[1:]
    return host, b3, right, inner_d


def label_parser(source: list[dict[str, str]]):
    base = [preparse(r["wrapper"], _residual_from_frozen(r))[0] for r in source]
    counts = Counter(base)
    licensed = {h for h in counts if counts[h] and counts["o" + h] and counts["ot" + h]} | {"ar", "al", "ol"}

    def parse(token: str) -> dict[str, object]:
        wrapper, residual, dy = strip_layers(token)
        host, b3, right, inner_d = preparse(wrapper, residual)
        frame = "NONE"
        if host.startswith("ot") and host[2:] in licensed:
            host, frame = host[2:], "OT"
        elif host.startswith("o") and host[1:] in licensed:
            host, frame = host[1:], "O"
        return {"wrapper": wrapper, "inner_d": inner_d, "local_frame": frame,
                "page_host": host or "EMPTY", "right_family": right,
                "dy_closure": dy, "b3": b3}

    return parse


def _residual_from_frozen(row: dict[str, str]) -> str:
    """Reconstruct the pre-HPR2 residual used by the frozen GDT062 parser."""
    host = str(row["page_host"])
    if row["local_frame"] != "NONE":
        host = row["local_frame"].lower() + host
    if row["inner_d"] == "1":
        host = "d" + host
    if row["right_family"] != "NONE":
        host += row["right_family"]
    if row["b3"] == "1":
        host += "m"
    return host


def tuple_key(row: dict[str, object]) -> str:
    return "|".join(str(row[k]) for k in
                    ("wrapper", "inner_d", "local_frame", "page_host", "right_family", "dy_closure", "b3"))


def atom(row: dict[str, str]) -> str:
    bits = [f"H={row['page_host']}"]
    if row["wrapper"] != "NONE": bits.insert(0, f"W={row['wrapper']}")
    if row["inner_d"] == "1": bits.append("D=1")
    if row["local_frame"] != "NONE": bits.append(f"F={row['local_frame']}")
    if row["right_family"] != "NONE": bits.append(f"R={row['right_family']}")
    if row["dy_closure"] == "1": bits.append("DY=1")
    if row["b3"] == "1": bits.append("B3=1")
    return "FIELD[" + ",".join(bits) + "]"


def hypergeom_tail(N: int, K: int, n: int, observed: int) -> float:
    hi = min(K, n)
    den = math.comb(N, n)
    return sum(math.comb(K, x) * math.comb(N - K, n - x) for x in range(observed, hi + 1)) / den


def main() -> None:
    # Guard every f84 page before retention. The scientific source below is
    # the already parsed, f84r-free GDT062 view; we additionally reject f84v.
    source = [r for r in read(SOURCE) if not r["page"].startswith("f84")]
    assert not any(r["locus"].startswith("f84") for r in source)
    page = [r for r in source if r["page"] == "f77r"]
    assert len(page) == 193 and len({r["locus"] for r in page}) == 31
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in page:
        by_line[row["locus"]].append(row)

    steps = read(STEPS)
    assert len(steps) == 6 and [r["locus"] for r in steps] == [f"f77r.{x}" for x in range(2, 8)]
    labels = [r["ZL3b_surface"] for r in steps]
    states = {r["ZL3b_surface"]: r["provisional_quality_state"] for r in steps}
    parse_label = label_parser(source)
    parsed_labels = {token: parse_label(token) for token in labels}

    interlinear: list[dict[str, object]] = []
    for locus, rows in sorted(by_line.items(), key=lambda item: int(item[0].split(".")[1])):
        rows.sort(key=lambda r: int(r["group_index"]))
        complete = len(rows) == int(rows[0]["group_count"])
        exact = [r["token"] for r in rows if r["token"] in states]
        interlinear.append({
            "locus": locus,
            "groups": len(rows),
            "expected_groups": int(rows[0]["group_count"]),
            "coverage": "COMPLETE" if complete else "PARTIAL_STRICT_CONSENSUS",
            "missing_or_unstable_groups": int(rows[0]["group_count"]) - len(rows),
            "surface_sequence": " | ".join(r["token"] for r in rows),
            "record_state_sequence": " > ".join(r.get("record_state", "UNAVAILABLE") for r in rows),
            "structural_translation": " ; ".join(atom(r) for r in rows),
            "dy_checkpoints": sum(int(r["dy_closure"]) for r in rows),
            "b3_closers": sum(int(r["b3"]) for r in rows),
            "exact_label_echoes": ";".join(exact),
            "provisional_semantic_annotation": ";".join(f"{x}={states[x]}_LABEL_ECHO" for x in exact) if exact else "NONE",
            "semantic_status": "POSTHOC_CANDIDATE_ECHO_NOT_TRANSLATION" if exact else "UNASSIGNED",
            "reading_basis": "STRICT_ZERO_ALTERNATIVE_ALL_THREE_READINGS",
        })
    write(INTERLINEAR, interlinear, list(interlinear[0]))

    def full_key(r: dict[str, str]) -> str:
        return tuple_key(r)

    echoes: list[dict[str, object]] = []
    for step in steps:
        token = step["ZL3b_surface"]
        parsed = parsed_labels[token]
        key = tuple_key(parsed)
        exact_all = [r for r in source if r["token"] == token]
        exact_page = [r for r in page if r["token"] == token]
        tuple_all = [r for r in source if full_key(r) == key]
        tuple_page = [r for r in page if full_key(r) == key]
        host_all = [r for r in source if r["page_host"] == parsed["page_host"]]
        host_page = [r for r in page if r["page_host"] == parsed["page_host"]]
        echoes.append({
            "step": step["step"], "label_locus": step["locus"], "label_surface": token,
            "provisional_state": step["provisional_quality_state"],
            "wrapper": parsed["wrapper"], "inner_d": parsed["inner_d"],
            "local_frame": parsed["local_frame"], "page_host": parsed["page_host"],
            "right_family": parsed["right_family"], "dy_closure": parsed["dy_closure"], "b3": parsed["b3"],
            "exact_surface_f77_prose": len(exact_page), "exact_surface_nonf84_prose": len(exact_all),
            "exact_surface_nonf84_folios": len({r["physical_folio"] for r in exact_all}),
            "full_tuple_f77_prose": len(tuple_page), "full_tuple_nonf84_prose": len(tuple_all),
            "page_host_f77_prose": len(host_page), "page_host_nonf84_prose": len(host_all),
            "page_host_nonf84_folios": len({r["physical_folio"] for r in host_all}),
            "f77_exact_loci": ";".join(sorted({r["locus"] for r in exact_page})),
            "f77_host_loci": ";".join(sorted({r["locus"] for r in host_page})),
            "bridge_status": "EXACT_WHOLE_FORM_ECHO_POSTHOC" if exact_page else "NO_EXACT_PAGE_ECHO",
        })
    write(ECHOES, echoes, list(echoes[0]))

    scope = [r for r in source if r["section"] == "B" and r["currier"] == "B" and r["hand"] == "2"]
    K = sum(r["token"] in set(labels) for r in scope)
    observed = sum(r["token"] in set(labels) for r in page)
    p = hypergeom_tail(len(scope), K, len(page), observed)
    exact_labels_on_page = sum(int(r["exact_surface_f77_prose"]) > 0 for r in echoes)
    distinct_nongeneric = sum(int(r["full_tuple_f77_prose"]) > 0 and int(r["page_host_nonf84_folios"]) <= 3 for r in echoes)
    status = ("LABEL_KEY_BRIDGES_F77_PROSE" if exact_labels_on_page >= 3 and p <= .05 and distinct_nongeneric >= 2
              else "STRICT_STRUCTURAL_INTERLINEAR_PARTIAL_LABEL_KEY_NOT_BRIDGED")
    counters = [
        {"counterexample_id": "C01", "finding": f"Only {exact_labels_on_page}/6 diagram surfaces recur in strict f77r prose ({observed} group occurrence).", "impact": "The six labels do not provide a page dictionary."},
        {"counterexample_id": "C02", "finding": f"Same-register exact-surface enrichment is p={p:.6f} (one-sided descriptive hypergeometric).", "impact": "The sole echo is not page-enriched."},
        {"counterexample_id": "C03", "finding": f"{sum(int(r['exact_surface_nonf84_prose']) == 0 for r in echoes)}/6 label surfaces never occur in strict non-f84 prose.", "impact": "Some labels remain diagram-local or outside the strict prose inventory."},
        {"counterexample_id": "C04", "finding": "Stripped hosts e/ol/or recur, but stripping collapses visibly different label forms into common compiler-supported material.", "impact": "PAGE_HOST recurrence alone cannot import the exposed quality gloss."},
        {"counterexample_id": "C05", "finding": "GDT182 found multiple perfect shallow decoders and GDT195 found no exact readable homolog.", "impact": "The local state names remain post-hoc scaffolding."},
    ]
    write(COUNTER, counters, list(counters[0]))

    report = f"""# GDT196 — strict f77 structural skeleton

## Outcome

**{status}**

All stable groups on **31** consensus-covered confirmed-prose lines on `f77r`
are now rendered as an HPR2 structural interlinear: **193 groups**,
**{sum(int(r['dy_checkpoints']) for r in interlinear)} DY checkpoints**, and
**{sum(int(r['b3_closers']) for r in interlinear)} B3 closers**.  Eighteen
lines are complete ({sum(int(r['groups']) for r in interlinear if r['coverage']=='COMPLETE')}
groups); thirteen are partial consensus views ({sum(int(r['groups']) for r in interlinear if r['coverage']!='COMPLETE')}
retained groups).  Every retained group has a compiler decomposition.  This is
an exhaustive strict-consensus skeleton, not plaintext; missing or unstable
groups are explicit and never reconstructed.

## Does the diagram key enter the prose?

Only **{exact_labels_on_page}/6** state-label surfaces recur anywhere in the
strict page prose.  The sole echo is `otedy` at `f77r.25`; the other five are
absent as exact visible forms.  Across all retained non-`f84*` strict prose,
the six-surface set occurs {sum(int(r['exact_surface_nonf84_prose']) for r in echoes)}
times, mostly because `otedy` and `otol` are ordinary recurrent forms.

Within the matched Section B / Currier B / hand 2 stratum, `f77r` contains
{observed}/{len(page)} hits versus {K}/{len(scope)} in the complete stratum.
The descriptive one-sided hypergeometric tail is **p={p:.6f}**.  The page is
not enriched for its own six diagram surfaces.

| label | exposed state | HPR2 tuple | exact f77 prose | exact non-f84 prose | same host f77 prose | bridge |
|---|---|---|---:|---:|---:|---|
""" + "".join(
        f"| `{r['label_surface']}` | {r['provisional_state']} | `{r['wrapper']}:{r['local_frame']}:{r['page_host']}:{r['right_family']}:DY{r['dy_closure']}` | {r['exact_surface_f77_prose']} | {r['exact_surface_nonf84_prose']} | {r['page_host_f77_prose']} | {r['bridge_status']} |\n"
        for r in echoes
    ) + f"""

The stripped hosts `e`, `ol`, and `or` do recur on the page, but this is not a
semantic bridge: they are broad compiler-supported host material, and their
surface wrappers/right edges differ.  Importing `DRY`, `HOT`, or `COLD` from a
label into every such host occurrence would be exactly the kind of
many-to-one post-hoc glossing that the full interlinear was designed to catch.

## Translation consequence

The useful translation now available for this page is structural:

```text
physical line = ordered field sequence
field = wrapper + optional inner-D/frame + opaque PAGE_HOST + optional right renderer
DY = internal checkpoint
B3 = probabilistic record close
```

One prose group is an exact visible echo of an exposed diagram label, but the
six-label key does not propagate through the page.  Therefore the f77 process
scaffold cannot currently unlock its prose.  GDT181's hybrid compiler remains
the leading architecture, while the GDT180 quality labels remain local,
post-hoc annotations rather than translated words.

No word, sound, language, plaintext, or confirmed meaning is recovered.
`f84r` and all other `f84*` rows were excluded before retention and scoring.
"""
    REPORT.write_text(report, encoding="utf-8")

    result = {
        "schema": "GDT196_F77_STRUCTURAL_INTERLINEAR_RESULT_V1",
        "status": status,
        "consensus_covered_lines": len(interlinear), "complete_lines": sum(r["coverage"] == "COMPLETE" for r in interlinear),
        "partial_lines": sum(r["coverage"] != "COMPLETE" for r in interlinear), "strict_groups": len(page),
        "dy_checkpoints": sum(int(r["dy_checkpoints"]) for r in interlinear),
        "b3_closers": sum(int(r["b3_closers"]) for r in interlinear),
        "diagram_labels": len(echoes), "exact_labels_echoed_on_page": exact_labels_on_page,
        "exact_label_group_occurrences_on_page": observed,
        "same_register_population_groups": len(scope), "same_register_label_occurrences": K,
        "same_register_hypergeometric_p": p,
        "interpretation": "Exhaustive retained-consensus f77r structural skeleton with explicit partial lines; exposed diagram labels do not provide a prose dictionary.",
        "claim_ceiling": "Formal page interlinear and label/prose bridge only; no word, sound, language, plaintext, meaning, or confirmed translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False},
        "inputs": {SOURCE.name: sha(SOURCE), STEPS.name: sha(STEPS),
                   "gdt180_result.json": sha(ROOT / "gdt180_result.json"),
                   "gdt182_result.json": sha(ROOT / "gdt182_result.json"),
                   "gdt195_result.json": sha(ROOT / "gdt195_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {INTERLINEAR.name: sha(INTERLINEAR), ECHOES.name: sha(ECHOES), COUNTER.name: sha(COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "lines": len(interlinear), "groups": len(page),
                      "exact_labels_echoed": exact_labels_on_page, "p": p}, sort_keys=True))


if __name__ == "__main__":
    main()
