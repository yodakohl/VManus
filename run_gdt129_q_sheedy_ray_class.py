#!/usr/bin/env python3
"""Enumerate and score the exact q*|sheedy Q20 visual lead."""
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ROOT / "gdt127_q20_field_inventory.tsv"
STAR = ROOT / "experiments/semantic_assumptions/star_morphology_entry/source_panel.tsv"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
GDT128 = ROOT / "gdt128_result.json"
METHOD = ROOT / "GDT129_Q_SHEEDY_RAY_CLASS_METHOD.md"
INVENTORY = ROOT / "gdt129_q_sheedy_inventory.tsv"
TESTS = ROOT / "gdt129_q_sheedy_tests.tsv"
COUNTER = ROOT / "gdt129_q_sheedy_counterexamples.tsv"
REPORT = ROOT / "GDT129_Q_SHEEDY_RAY_CLASS_REPORT.md"
RESULT = ROOT / "gdt129_result.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    fields = list(rows[0])
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def hypergeom_tail(population, successes, draws, observed):
    denominator = math.comb(population, draws)
    return sum(math.comb(successes, k) * math.comb(population - successes, draws - k)
               for k in range(observed, min(draws, successes) + 1)
               if 0 <= draws - k <= population - successes) / denominator


def main():
    star = {(row["page"], int(row["star_ordinal"])): row for row in read(STAR)}
    records = defaultdict(lambda: {"forms": [], "q_forms": [], "q_loci": [], "two_group": False})
    for row in read(FIELDS):
        if row["edition"] != "ZL3b":
            continue
        assert not row["page"].startswith("f84r")
        tokens = row["group_tokens"].split("|")
        if "sheedy" not in tokens:
            continue
        key = (row["page"], int(row["star_ordinal"]))
        records[key]["forms"].append(row["group_tokens"])
        records[key]["two_group"] |= len(tokens) == 2 and tokens[-1] == "sheedy"
        if any(tokens[i].startswith("q") and tokens[i + 1] == "sheedy" for i in range(len(tokens) - 1)):
            records[key]["q_forms"].append(row["group_tokens"])
            records[key]["q_loci"].append(row["locus"])

    source_tokens = defaultdict(list)
    for row in read(SOURCE):
        if row["locus"].startswith("f84r"):
            continue
        source_tokens[(row["edition"], row["locus"])].append((int(row["source_group_index"]), row["ivtff_group_raw"]))
    for key in source_tokens:
        source_tokens[key].sort()

    def edition_exact(info, edition):
        for locus in info["q_loci"]:
            tokens = [token for _, token in source_tokens[(edition, locus)]]
            if any(tokens[i].startswith("q") and tokens[i + 1] == "sheedy" for i in range(len(tokens) - 1)):
                return 1
        return 0

    rows = []
    for key in sorted(records):
        assert key in star
        visual = star[key]
        info = records[key]
        rows.append({
            "panel": "ARCHIVED_DISCOVERY", "page": key[0], "physical_folio": visual["physical_folio"],
            "star_ordinal": key[1], "sheedy_fields": ";".join(info["forms"]),
            "exact_adjacent_q_sheedy": int(bool(info["q_forms"])),
            "q_sheedy_fields": ";".join(info["q_forms"]), "has_exact_two_group_sheedy": int(info["two_group"]),
            "zl_exact_q_sheedy": edition_exact(info, "ZL3b"), "it_exact_q_sheedy": edition_exact(info, "IT2a"),
            "rf_exact_q_sheedy": edition_exact(info, "RF1b"),
            "all_readings_exact_q_sheedy": int(all(edition_exact(info, edition) for edition in ("ZL3b", "IT2a", "RF1b"))),
            "rays": visual["rays"], "tail": visual["tail"], "color": visual["color"],
            "visual_provenance": "EXISTING_HUMAN_ANNOTATION_STOLFI_STAR_PROPS",
            "review_support": "ARCHIVED_SINGLE_SOURCE_CATALOGUE",
        })

    transfer = json.loads(GDT128.read_text(encoding="utf-8"))
    assert transfer["status"] == "Q20_QOKAL_SHEEDY_RAY_TRANSFER_HIT_TAIL_TRANSFER_FAILED"
    rows.append({
        "panel": "PROSPECTIVE_GDT128", "page": "f103r", "physical_folio": "f103", "star_ordinal": 15,
        "sheedy_fields": "qokal|sheedy", "exact_adjacent_q_sheedy": 1,
        "q_sheedy_fields": "qokal|sheedy", "has_exact_two_group_sheedy": 1,
        "zl_exact_q_sheedy": 1, "it_exact_q_sheedy": 1, "rf_exact_q_sheedy": 0,
        "all_readings_exact_q_sheedy": 0,
        "rays": transfer["review"]["ray_consensus"], "tail": transfer["review"]["tail_consensus"],
        "color": "UNPREDICTED", "visual_provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "review_support": "RAYS_2_OF_3_TAIL_3_OF_3",
    })
    write(INVENTORY, rows)

    discovery = [row for row in rows if row["panel"] == "ARCHIVED_DISCOVERY" and row["rays"] in {"7", "8"}]
    q_discovery = [row for row in discovery if int(row["exact_adjacent_q_sheedy"])]
    two_group = [row for row in discovery if int(row["has_exact_two_group_sheedy"])]
    q_two = [row for row in two_group if int(row["exact_adjacent_q_sheedy"])]
    q_combined = [row for row in rows if int(row["exact_adjacent_q_sheedy"]) and str(row["rays"]) in {"7", "8"}]
    q_all_readings = [row for row in rows if int(row["all_readings_exact_q_sheedy"]) and str(row["rays"]) in {"7", "8"}]
    discovery_ray8 = sum(row["rays"] == "8" for row in discovery)
    q_discovery_hits = sum(row["rays"] == "8" for row in q_discovery)
    two_ray8 = sum(row["rays"] == "8" for row in two_group)
    q_two_hits = sum(row["rays"] == "8" for row in q_two)
    combined_all = [row for row in rows if str(row["rays"]) in {"7", "8"}]
    combined_ray8 = sum(str(row["rays"]) == "8" for row in combined_all)
    q_combined_hits = sum(str(row["rays"]) == "8" for row in q_combined)
    informative_pages = 0
    for page in sorted({row["page"] for row in discovery}):
        page_rows = [row for row in discovery if row["page"] == page]
        if any(int(row["exact_adjacent_q_sheedy"]) for row in page_rows) and any(not int(row["exact_adjacent_q_sheedy"]) for row in page_rows) and len({row["rays"] for row in page_rows}) > 1:
            informative_pages += 1

    tests = [
        {"test": "DISCOVERY_CONDITIONAL_ON_EXACT_SHEEDY", "population": len(discovery), "ray8_population": discovery_ray8,
         "q_sheedy_records": len(q_discovery), "q_sheedy_ray8": q_discovery_hits,
         "one_sided_exact_p": f"{hypergeom_tail(len(discovery), discovery_ray8, len(q_discovery), q_discovery_hits):.12f}",
         "inference": "LOCAL_POSTSELECTED_DIAGNOSTIC"},
        {"test": "DISCOVERY_EXACT_TWO_GROUP_SHEEDY_ONLY", "population": len(two_group), "ray8_population": two_ray8,
         "q_sheedy_records": len(q_two), "q_sheedy_ray8": q_two_hits,
         "one_sided_exact_p": f"{hypergeom_tail(len(two_group), two_ray8, len(q_two), q_two_hits):.12f}",
         "inference": "SHAPE_MATCHED_LOCAL_DIAGNOSTIC"},
        {"test": "COMBINED_WITH_ONE_FROZEN_PROSPECTIVE_TARGET", "population": len(combined_all), "ray8_population": combined_ray8,
         "q_sheedy_records": len(q_combined), "q_sheedy_ray8": q_combined_hits,
         "one_sided_exact_p": f"{hypergeom_tail(len(combined_all), combined_ray8, len(q_combined), q_combined_hits):.12f}",
         "inference": "DESCRIPTIVE_NOT_CONFIRMATORY"},
        {"test": "WITHIN_PAGE_CONTRAST_CAPACITY", "population": len(discovery), "ray8_population": discovery_ray8,
         "q_sheedy_records": len(q_discovery), "q_sheedy_ray8": q_discovery_hits,
         "one_sided_exact_p": "", "inference": f"NO_IDENTIFIABLE_WITHIN_PAGE_CONTRAST_{informative_pages}_INFORMATIVE_PAGES"},
    ]
    write(TESTS, tests)

    counters = []
    for row in rows:
        reasons = []
        if row["panel"] == "PROSPECTIVE_GDT128" and str(row["tail"]) != "1":
            reasons.append("FROZEN_1_TAIL_PREDICTION_FAILED")
        if int(row["exact_adjacent_q_sheedy"]) and not int(row["all_readings_exact_q_sheedy"]):
            reasons.append("PRIMARY_Q_SHEEDY_NOT_EXACT_IN_ALL_READINGS")
        if not int(row["exact_adjacent_q_sheedy"]) and str(row["rays"]) == "8":
            reasons.append("EIGHT_RAYS_WITHOUT_Q_SHEEDY")
        elif not int(row["exact_adjacent_q_sheedy"]) and str(row["rays"]) == "7" and "sheedy" in row["sheedy_fields"]:
            reasons.append("SHEEDY_WITH_SEVEN_RAYS")
        if reasons:
            counters.append({"page": row["page"], "star_ordinal": row["star_ordinal"], "sheedy_fields": row["sheedy_fields"], "rays": row["rays"], "tail": row["tail"], "counterexample": ";".join(reasons)})
    write(COUNTER, counters)

    status = "Q_SHEEDY_EIGHT_RAY_LEAD_PROVISIONAL_TAIL_STATE_FAILED"
    REPORT.write_text(f"""# GDT129 — exact `q… | sheedy` ray-class synthesis

Status: **{status}**

After the GDT128 reveal, the archived GDT127 panel was enumerated and found to
contain 15 ZL3b records with exact `sheedy`; seven have 8 rays. The primary-view
exact adjacent construction `q* | sheedy` occurs in three records on two
folios, and all three have 8 rays. Conditional on all archived `sheedy`
records, the local exact diagnostic is p={tests[0]['one_sided_exact_p']}; within
the narrower exact two-group `* | sheedy` records it is
p={tests[1]['one_sided_exact_p']}. Neither is a search-adjusted confirmation.

The publicly frozen f103r target adds a third folio and a fourth ZL3b/IT2a
`q* | sheedy` record. Its 2/3 reviewer ray consensus is 8, so the coarse
primary-view ray pattern is 4/4 descriptively across three folios. RF1b does
not retain the exact two-group form at f103r, and one archived ZL3b occurrence
also changes in RF1b. Agreement-only exact support is therefore **{len(q_all_readings)}
records**, all archived, rather than 4/4. The target's unanimous tail
count is 0, breaking the prior 3/3 one-tail pattern and falsifying the exact
visual-state transfer. The combined local p={tests[2]['one_sided_exact_p']} is
descriptive only because the formal rule and target were postselected.

There are **{informative_pages} informative within-page contrasts** after
conditioning on exact `sheedy`: pages containing the q construction do not
also provide both ray states among comparable `sheedy` records. The rule is
also not necessary: several non-q `sheedy` fields have 8 rays, while other
`sheedy` fields have 7. No further exact q-adjacent-`sheedy` target exists in
the current non-f84 Q20 source inventory, so another exact prospective transfer
requires new independently localized records rather than broadening the rule.

The useful outcome is a concrete primary-reading codeword candidate: exact `q* | sheedy` may
mark a coarse 8-ray record class. It remains small, postselected, visually
disputed at one target, and unidentifiable against page ecology. No number,
star property, role, word, morpheme, POS, sound, language, plaintext, meaning,
or translation follows. f84r remained sealed.
""", encoding="utf-8")

    result = {
        "schema": "GDT129_Q_SHEEDY_RAY_CLASS_RESULT_V1", "status": status,
        "counts": {"archived_sheedy_records": len(discovery), "archived_q_sheedy_records": len(q_discovery),
                   "archived_q_sheedy_ray8": q_discovery_hits, "combined_q_sheedy_records": len(q_combined),
                   "combined_q_sheedy_ray8": q_combined_hits, "physical_folios_combined": len({row["physical_folio"] for row in q_combined}),
                   "all_readings_exact_q_sheedy_records": len(q_all_readings),
                   "all_readings_exact_q_sheedy_ray8": sum(str(row["rays"]) == "8" for row in q_all_readings),
                   "prospective_all_readings_exact": int(next(row for row in rows if row["panel"] == "PROSPECTIVE_GDT128")["all_readings_exact_q_sheedy"]),
                   "informative_within_page_contrasts": informative_pages},
        "tests": tests,
        "chronology": "GDT128 was prospectively frozen; the GDT129 archive-wide census and combined summary are post-reveal synthesis.",
        "interpretation": "Primary-reading exact q-adjacent-sheedy is a provisional coarse 8-ray codeword lead; the prospective form is reading-unstable and the exact tail state failed.",
        "claim_ceiling": "Postselected formal/visual codeword lead only; no number, star meaning, role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "retained", "queried", "joined", "scored", "targeted", "assigned", "predicted")},
        "inputs": {FIELDS.name: sha(FIELDS), str(STAR.relative_to(ROOT)): sha(STAR), str(SOURCE.relative_to(ROOT)): sha(SOURCE), GDT128.name: sha(GDT128), "gdt128_validation.json": sha(ROOT / "gdt128_validation.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {INVENTORY.name: sha(INVENTORY), TESTS.name: sha(TESTS), COUNTER.name: sha(COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "counts": result["counts"], "tests": tests}, sort_keys=True))


if __name__ == "__main__":
    main()
