#!/usr/bin/env python3
"""GDT269: exact-host/page conditional decomposition of q13 q record stage."""
import csv
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

R = Path(__file__).resolve().parent
SRC = "gdt227_q13_abstract_interlinear.tsv"
METHOD = "GDT269_Q13_WRAPPER_HOST_CONDITIONAL_METHOD.md"
CONTEXT = ["gdt010_result.json", "gdt064_result.json", "gdt267_result.json", "gdt268_result.json"]
VARIANTS = [
    ("PAGE_HOST_PAGE", ("page", "page_host")),
    ("PAGE_HOST_PAGE_ROLE", ("page", "page_host", "field_role")),
    ("PAGE_HOST_PAGE_RELATIVE_QUARTILE", ("page", "page_host", "relative_quartile")),
    ("PAGE_HOST_PAGE_WITHIN_FIELD_POSITION", ("page", "page_host", "within_field_position")),
    ("PAGE_HOST_PAGE_FIELD_END", ("page", "page_host", "field_end")),
    ("PAGE_HOST_PAGE_ROLE_WITHIN_FIELD_POSITION", ("page", "page_host", "field_role", "within_field_position")),
    ("PAGE_HOST_PAGE_RELATIVE_QUARTILE_WITHIN_FIELD_POSITION", ("page", "page_host", "relative_quartile", "within_field_position")),
]


def read(name):
    with (R / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    if not rows:
        raise ValueError(name)
    with (R / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def sha(name):
    return hashlib.sha256((R / name).read_bytes()).hexdigest()


def content_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def panel_and_occurrences():
    source = read(SRC)
    assert source and all(not row["page"].startswith("f84") for row in source)
    records = defaultdict(list)
    loci = defaultdict(set)
    for row in source:
        key = (row["page"], row["record_id"])
        records[key].append(row)
        loci[key].add(row["locus"])
    page_records = defaultdict(list)
    for (page, record_id), values in loci.items():
        if len(values) >= 4:
            page_records[page].append(record_id)
    panel = {page: sorted(ids) for page, ids in page_records.items() if len(ids) == 2}
    assert len(panel) == 9

    occurrences = []
    for page, ids in sorted(panel.items()):
        for ordinal, record_id in enumerate(ids):
            ordinal_class = "EARLIER" if ordinal == 0 else "LATER"
            for field in records[(page, record_id)]:
                hosts = field["page_hosts"].split("|")
                cells = field["compiler_cells"].split("|")
                tokens = field["source_tokens"].split("|")
                assert len(hosts) == len(cells) == len(tokens)
                for index, (host, cell, token) in enumerate(zip(hosts, cells, tokens)):
                    wrapper = cell.split(":")[0]
                    if wrapper not in {"q", "NONE"}:
                        continue
                    if len(hosts) == 1:
                        within = "SINGLE"
                    elif index == 0:
                        within = "FIRST"
                    elif index == len(hosts) - 1:
                        within = "LAST"
                    else:
                        within = "MIDDLE"
                    relative = float(field["relative_position"])
                    occurrences.append({
                        "page": page,
                        "physical_folio": field["physical_folio"],
                        "record_id": record_id,
                        "ordinal_class": ordinal_class,
                        "ordinal_binary": ordinal,
                        "locus": field["locus"],
                        "field_ordinal": field["field_ordinal"],
                        "field_role": field["abstract_role_like"],
                        "relative_quartile": min(3, int(relative * 4)),
                        "within_field_position": within,
                        "field_end": field["line_field_end"],
                        "page_host": host,
                        "wrapper": wrapper,
                        "source_token": token,
                        "claim_state": "OPAQUE_CONSTRUCTIONAL_OCCURRENCE_NO_GLOSS",
                    })
    assert len(occurrences) == 632
    return panel, occurrences


def evaluate(name, keys, occurrences):
    grouped = defaultdict(Counter)
    for row in occurrences:
        key = tuple(str(row[k]) for k in keys)
        grouped[key][(row["wrapper"], int(row["ordinal_binary"]))] += 1

    mobile = []
    strata_rows = []
    for key, counts in sorted(grouped.items()):
        q_early = counts[("q", 0)]
        q_late = counts[("q", 1)]
        none_early = counts[("NONE", 0)]
        none_late = counts[("NONE", 1)]
        n = q_early + q_late + none_early + none_late
        q_total = q_early + q_late
        early_total = q_early + none_early
        low = max(0, q_total - (n - early_total))
        high = min(q_total, early_total)
        movable = int(high > low)
        expected = q_total * early_total / n if n else 0.0
        row = {
            "variant": name,
            "stratum_key": json.dumps(dict(zip(keys, key)), sort_keys=True, separators=(",", ":")),
            "q_early": q_early,
            "q_late": q_late,
            "none_early": none_early,
            "none_late": none_late,
            "occurrences": n,
            "expected_q_early": f"{expected:.12f}",
            "conditional_score": f"{q_early - expected:.12f}",
            "null_min_q_early": low,
            "null_max_q_early": high,
            "movable": movable,
        }
        strata_rows.append(row)
        if movable:
            mobile.append((key, counts, n, q_total, early_total, low, high))

    distribution = {0: 1.0}
    numerator = denominator = score = variance = 0.0
    observed = 0
    page_scores = defaultdict(float)
    mobile_hosts = set()
    mobile_pages = set()
    for key, counts, n, q_total, early_total, low, high in mobile:
        a = counts[("q", 0)]
        b = counts[("q", 1)]
        c = counts[("NONE", 0)]
        d = counts[("NONE", 1)]
        numerator += a * d / n
        denominator += b * c / n
        expected = q_total * early_total / n
        delta = a - expected
        score += delta
        page_scores[key[0]] += delta
        observed += a
        mobile_pages.add(key[0])
        mobile_hosts.add(key[1])
        if n > 1:
            variance += q_total * (n - q_total) * early_total * (n - early_total) / (n * n * (n - 1))
        local = {
            value: comb(early_total, value) * comb(n - early_total, q_total - value) / comb(n, q_total)
            for value in range(low, high + 1)
        }
        new = defaultdict(float)
        for total, p0 in distribution.items():
            for value, p1 in local.items():
                new[total + value] += p0 * p1
        distribution = dict(new)

    mean = sum(value * probability for value, probability in distribution.items())
    upper = sum(probability for value, probability in distribution.items() if value >= observed)
    two = sum(probability for value, probability in distribution.items() if abs(value - mean) >= abs(observed - mean) - 1e-12)
    exact_rows = [{
        "variant": name,
        "q_early_total": value,
        "probability": f"{probability:.15f}",
        "upper_tail_probability": f"{sum(p for v, p in distribution.items() if v >= value):.15f}",
    } for value, probability in sorted(distribution.items())]

    ordered_pages = sorted({row["page"] for row in occurrences})
    page_rows = [{
        "variant": name,
        "page": page,
        "conditional_score": f"{page_scores[page]:.12f}",
        "direction": "Q_EARLIER" if page_scores[page] > 0 else "Q_LATER" if page_scores[page] < 0 else "TIE",
    } for page in ordered_pages]
    page_values = [page_scores[page] for page in ordered_pages]

    def sign_stat(values):
        den = math.sqrt(sum(value * value for value in values))
        return abs(sum(values)) / den if den else 0.0

    observed_sign = sign_stat(page_values)
    sign_rows = []
    sign_values = []
    for world, signs in enumerate(itertools.product((-1, 1), repeat=len(ordered_pages))):
        value = sign_stat([sign * score_value for sign, score_value in zip(signs, page_values)])
        sign_values.append(value)
        sign_rows.append({
            "variant": name,
            "world": world,
            "signs": "".join("+" if sign == 1 else "-" for sign in signs),
            "page_cluster_stat": f"{value:.12f}",
        })
    sign_p = (1 + sum(value >= observed_sign - 1e-15 for value in sign_values)) / (len(sign_values) + 1)

    summary = {
        "variant": name,
        "stratification": "+".join(keys),
        "all_strata": len(grouped),
        "movable_strata": len(mobile),
        "mobile_occurrences": sum(item[2] for item in mobile),
        "mobile_hosts": len(mobile_hosts),
        "mobile_pages": len(mobile_pages),
        "observed_q_early": observed,
        "expected_q_early": f"{mean:.12f}",
        "conditional_score_u": f"{score:.12f}",
        "conditional_z": f"{score / math.sqrt(variance):.12f}" if variance else "0.000000000000",
        "mantel_haenszel_odds_ratio": f"{numerator / denominator:.12f}" if denominator else "INF",
        "exact_upper_p": f"{upper:.12f}",
        "exact_two_sided_p": f"{two:.12f}",
        "positive_page_scores": sum(value > 0 for value in page_values),
        "negative_page_scores": sum(value < 0 for value in page_values),
        "tied_page_scores": sum(value == 0 for value in page_values),
        "page_cluster_stat": f"{observed_sign:.12f}",
        "page_sign_flip_p": f"{sign_p:.12f}",
        "semantic_value": "UNASSIGNED",
    }
    return summary, strata_rows, exact_rows, page_rows, sign_rows


def main():
    panel, occurrences = panel_and_occurrences()
    tests = []
    strata = []
    exact_null = []
    page_scores = []
    sign_null = []
    for name, keys in VARIANTS:
        summary, srows, erows, prows, nrows = evaluate(name, keys, occurrences)
        tests.append(summary)
        strata.extend(srows)
        exact_null.extend(erows)
        page_scores.extend(prows)
        sign_null.extend(nrows)

    write("gdt269_occurrences.tsv", occurrences)
    write("gdt269_tests.tsv", tests)
    write("gdt269_strata.tsv", strata)
    write("gdt269_exact_null.tsv", exact_null)
    write("gdt269_page_scores.tsv", page_scores)
    write("gdt269_page_sign_null.tsv", sign_null)

    primary = tests[0]
    position = next(row for row in tests if row["variant"] == "PAGE_HOST_PAGE_WITHIN_FIELD_POSITION")
    role_position = next(row for row in tests if row["variant"] == "PAGE_HOST_PAGE_ROLE_WITHIN_FIELD_POSITION")
    counterexamples = [
        {"counterexample": "WITHIN_FIELD_POSITION_SENSITIVITY", "value": f"OR {position['mantel_haenszel_odds_ratio']} exact two-sided p {position['exact_two_sided_p']}", "consequence": "the exact-host/page association weakens after within-field group-position matching"},
        {"counterexample": "ROLE_PLUS_POSITION_CAPACITY", "value": f"{role_position['movable_strata']} movable strata {role_position['mobile_occurrences']} occurrences", "consequence": "fine matching loses capacity and does not establish a position-independent q record-stage rule"},
        {"counterexample": "Q20_TRANSFER_GDT268", "value": "same aggregate direction but max-two p 0.172464 for q", "consequence": "the q13 rule is not confirmed manuscript-wide"},
        {"counterexample": "OCCURRENCE_DEPENDENCE", "value": "groups share fields records and pages", "consequence": "the hypergeometric p is an exchangeability diagnostic; page sign flips are also reported"},
        {"counterexample": "GDT010_LINE_POSITION", "value": "same-host q already shifts earlier within physical lines", "consequence": "record-stage and local construction-position mechanisms remain entangled"},
    ]
    write("gdt269_counterexamples.tsv", counterexamples)

    status = "Q13_Q_STAGE_SURVIVES_EXACT_HOST_PAGE_CONDITIONING_BUT_IS_POSITION_SENSITIVE"
    report = [
        "# GDT269 — q13 q-wrapper stage conditional on exact PAGE_HOST",
        "",
        f"Status: **{status}**.",
        "",
        "## Result",
        "",
        "The unchanged GDT267 panel contains 632 q-or-bare group occurrences. Exact",
        "`PAGE_HOST × page` conditioning leaves 30 movable strata, 211 occurrences,",
        "12 hosts, and all nine pages. The q/earlier association remains positive:",
        f"Mantel–Haenszel OR {float(primary['mantel_haenszel_odds_ratio']):.3f}, conditional U {float(primary['conditional_score_u']):+.3f}, exact occurrence-level two-sided diagnostic p {float(primary['exact_two_sided_p']):.4f}, and page-cluster sign-flip p {float(primary['page_sign_flip_p']):.4f}. Seven of nine page scores are positive.",
        "",
        "This removes the simplest alternative that GDT267 merely compared different",
        "host vocabularies on earlier and later records. The same opaque PAGE_HOST can",
        "occur with q and bare rendering, and q remains earlier-associated within exact",
        "page/host strata.",
        "",
        "## Position sensitivities",
        "",
        "| conditioning | movable strata | occurrences | hosts | OR | exact two-sided p | page sign p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in tests:
        report.append(f"| {row['variant']} | {row['movable_strata']} | {row['mobile_occurrences']} | {row['mobile_hosts']} | {float(row['mantel_haenszel_odds_ratio']):.3f} | {float(row['exact_two_sided_p']):.4f} | {float(row['page_sign_flip_p']):.4f} |")
    report += [
        "",
        "The result is not position-independent. Matching within-field group position",
        f"reduces the OR to {float(position['mantel_haenszel_odds_ratio']):.3f} and the exact two-sided diagnostic to p={float(position['exact_two_sided_p']):.4f}; adding the field-role-like stratum leaves only {role_position['mobile_occurrences']} mobile occurrences. This is evidence that q participates in a q13 record/template stage, but local field composition is a plausible part of that mechanism.",
        "",
        "## Interpretation",
        "",
        "The combined GDT010/GDT064/GDT267/GDT269 picture is now more precise: q is a",
        "reusable outer rendering on the same PAGE_HOST, it tends earlier inside lines,",
        "and in this q13 panel it tends toward the earlier eligible record even after",
        "exact host/page conditioning. It is not yet a universal record ordinal—GDT268",
        "gave only a weak same-direction Stars echo—and it has no assigned meaning.",
        "",
        "This exploratory post-hoc decomposition assigns no word, morpheme, sound,",
        "semantic operator, topic, language, plaintext, or translation. No f84r material",
        "was opened, retained, queried, joined, or scored.",
        "",
    ]
    (R / "GDT269_Q13_WRAPPER_HOST_CONDITIONAL_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    outputs = [
        "gdt269_occurrences.tsv", "gdt269_tests.tsv", "gdt269_strata.tsv",
        "gdt269_exact_null.tsv", "gdt269_page_scores.tsv", "gdt269_page_sign_null.tsv",
        "gdt269_counterexamples.tsv", "GDT269_Q13_WRAPPER_HOST_CONDITIONAL_REPORT.md",
    ]
    result = {
        "experiment": "GDT269_Q13_WRAPPER_HOST_CONDITIONAL",
        "status": status,
        "analysis_state": "EXPLORATORY_POSTHOC_CONDITIONAL_DECOMPOSITION",
        "pages": len(panel),
        "records": sum(len(value) for value in panel.values()),
        "q_or_bare_occurrences": len(occurrences),
        "variants_reported": len(VARIANTS),
        "primary": {
            "movable_strata": int(primary["movable_strata"]),
            "mobile_occurrences": int(primary["mobile_occurrences"]),
            "mobile_hosts": int(primary["mobile_hosts"]),
            "mh_odds_ratio": float(primary["mantel_haenszel_odds_ratio"]),
            "conditional_u": float(primary["conditional_score_u"]),
            "exact_two_sided_p": float(primary["exact_two_sided_p"]),
            "page_sign_flip_p": float(primary["page_sign_flip_p"]),
            "positive_pages": int(primary["positive_page_scores"]),
        },
        "position_sensitivity": {
            "mh_odds_ratio": float(position["mantel_haenszel_odds_ratio"]),
            "exact_two_sided_p": float(position["exact_two_sided_p"]),
            "mobile_occurrences": int(position["mobile_occurrences"]),
        },
        "interpretation": "q13 q remains earlier-record-associated within exact PAGE_HOST and page, but the association weakens under within-field position matching.",
        "claim_ceiling": "Opaque q13 wrapper placement conditional on exact host/page only; no semantic operator word morpheme meaning plaintext or translation.",
        "semantic_assignments": 0,
        "f84r": {"new_access": False, "used": False, "scored": False, "prior_process_breach_disclosed": True},
        "inputs": {SRC: sha(SRC), **{name: sha(name) for name in CONTEXT}},
        "documents": {METHOD: sha(METHOD)},
        "implementation": {Path(__file__).name: sha(Path(__file__).name)},
        "outputs": {name: sha(name) for name in outputs},
    }
    result["content_hash"] = content_hash(result)
    (R / "gdt269_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "primary": result["primary"], "position": result["position_sensitivity"]}, sort_keys=True))


if __name__ == "__main__":
    main()
