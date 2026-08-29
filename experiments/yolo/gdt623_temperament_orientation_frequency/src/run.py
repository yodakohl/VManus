#!/usr/bin/env python3
"""Build GDT623 frequency, attachment, root-slot, and reader artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

BASE_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency")
ART = ROOT / BASE_REL / "artifacts"
SAFE_REL = Path("gdt327_joint_tuple_interlinear.tsv")
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
SOURCE_ROWS_REL = Path("experiments/yolo/gdt622_clm667_temperament_codebook/artifacts/SOURCE_OBSERVATIONS.tsv")
GDT622_REPORT_REL = Path("experiments/yolo/gdt622_clm667_temperament_codebook/REPORT.md")
GDT622_PAIRS_REL = Path("experiments/yolo/gdt622_clm667_temperament_codebook/artifacts/MINIMAL_PAIR_EVIDENCE.tsv")

MANUAL_INPUTS = {
    "provenance": BASE_REL / "artifacts/SOURCE_PROVENANCE.tsv",
    "layout": BASE_REL / "artifacts/HISTORICAL_LAYOUT_OBSERVATIONS.tsv",
    "visual": BASE_REL / "artifacts/VISUAL_OBSERVATIONS.tsv",
    "visual_roles": BASE_REL / "artifacts/VISUAL_ROLE_AUDIT.tsv",
    "anchors": BASE_REL / "artifacts/ANCHOR_EVIDENCE.tsv",
    "carrier_specs": BASE_REL / "artifacts/CARRIER_SPECS.tsv",
    "alternate_readings": BASE_REL / "artifacts/ALTERNATE_READING_AUDIT.tsv",
}
OUTPUTS = {
    "family_counts": BASE_REL / "artifacts/FAMILY_COUNTS.tsv",
    "section_counts": BASE_REL / "artifacts/SECTION_FAMILY_COUNTS.tsv",
    "source_quadrants": BASE_REL / "artifacts/SOURCE_QUADRANT_COUNTS.tsv",
    "orientations": BASE_REL / "artifacts/ORIENTATION_FREQUENCY_COMPARISON.tsv",
    "marginals": BASE_REL / "artifacts/MARGINAL_AXIS_COMPARISON.tsv",
    "headers": BASE_REL / "artifacts/HEADER_REPEAT_AUDIT.tsv",
    "initials": BASE_REL / "artifacts/INITIAL_SHELL_AUDIT.tsv",
    "carrier_evidence": BASE_REL / "artifacts/CARRIER_EVIDENCE.tsv",
    "carrier_summary": BASE_REL / "artifacts/CARRIER_FAMILY_SUMMARY.tsv",
    "suffixes": BASE_REL / "artifacts/SUFFIX_AUDIT.tsv",
    "states": BASE_REL / "artifacts/STATE_WORD_AUDIT.tsv",
    "binding": BASE_REL / "artifacts/BINDING_RULES.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V2.tsv",
    "readings": BASE_REL / "artifacts/CONCRETE_READINGS_V2.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

FAMILIES = ("KCH", "KSH", "TCH", "TSH")
MANUAL_EXTRA_PAGES = {"f31v"}
FAMILY_PARTS = {"KCH": ("k", "ch"), "KSH": ("k", "sh"), "TCH": ("t", "ch"), "TSH": ("t", "sh")}
V1 = {"k": "HOT", "t": "COLD", "ch": "MOIST", "sh": "DRY"}
V2 = {"k": "HOT", "t": "COLD", "ch": "DRY", "sh": "MOIST"}
QUADRANTS = (("HOT", "DRY"), ("HOT", "MOIST"), ("COLD", "DRY"), ("COLD", "MOIST"))
DE = {("HOT", "DRY"): "heiß und trocken", ("HOT", "MOIST"): "heiß und feucht", ("COLD", "DRY"): "kalt und trocken", ("COLD", "MOIST"): "kalt und feucht"}
EXACT_RE = re.compile(r"^qo(?P<a>[kt])(?P<b>ch|sh)(?:y|ey)$")
PREFIX_RE = re.compile(r"^qo(?P<a>[kt])(?P<b>ch|sh)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    fieldnames = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "NONE") if row.get(field, "") != "" else "NONE" for field in fieldnames})


def line_no(locus: str) -> int:
    match = re.search(r"\.([0-9]+)$", locus)
    if not match:
        raise ValueError(f"bad locus: {locus}")
    return int(match.group(1))


def sort_key(row: dict[str, str]) -> tuple[str, int, int]:
    return row["page"], line_no(row["locus"]), int(row["token_index"])


def safe_pages() -> set[str]:
    source = GuardedTSV(ROOT / SAFE_REL, selector_column="page", allowed_values=None, forbidden_prefixes=("f84",), forbidden_action="error")
    pages = {row["page"] for row in source}
    pages.discard("f1r")
    if not pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("unsafe page inventory")
    return pages


def guarded_tokens(pages: set[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(TOKENS_REL), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", "page,locus,code,kind,section,language,hand,token_index,eva", "--forbid-prefix", "f84"))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if done.returncode:
        raise RuntimeError(done.stderr or "query-tsv failed")
    match = re.search(r"GUARD_STATS\s+(\{.*\})", done.stderr)
    if not match:
        raise RuntimeError("query-tsv omitted guard statistics")
    stats = {key: int(value) for key, value in json.loads(match.group(1)).items()}
    rows = list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))
    rows.sort(key=sort_key)
    if any(row["page"].startswith("f84") or row["page"] == "f1r" for row in rows):
        raise RuntimeError("forbidden row materialized")
    return rows, stats


def family(a: str, b: str) -> str:
    return a.upper() + b.upper()


def surface_families(surface: str, mode: str) -> tuple[str, ...]:
    if mode == "EXACT_Y_EY":
        match = EXACT_RE.fullmatch(surface)
        return (family(match.group("a"), match.group("b")),) if match else ()
    if mode == "Q_PREFIX":
        match = PREFIX_RE.match(surface)
        return (family(match.group("a"), match.group("b")),) if match else ()
    if mode == "SUBSTRING":
        return tuple(name for name in FAMILIES if name.lower() in surface)
    raise ValueError(mode)


def v2_reading(name: str) -> tuple[str, str, str]:
    left, right = FAMILY_PARTS[name]
    thermal, moisture = V2[left], V2[right]
    return thermal, moisture, DE[(thermal, moisture)]


def all_orientations() -> list[tuple[str, dict[str, str]]]:
    answer: list[tuple[str, dict[str, str]]] = []
    for k in ("HOT", "COLD"):
        for ch in ("DRY", "MOIST"):
            answer.append((f"KT_THERMAL__K_{k}__CH_{ch}", {"k": k, "t": "COLD" if k == "HOT" else "HOT", "ch": ch, "sh": "MOIST" if ch == "DRY" else "DRY"}))
    for k in ("DRY", "MOIST"):
        for ch in ("HOT", "COLD"):
            answer.append((f"KT_MOISTURE__K_{k}__CH_{ch}", {"k": k, "t": "MOIST" if k == "DRY" else "DRY", "ch": ch, "sh": "COLD" if ch == "HOT" else "HOT"}))
    return answer


def mapped_quad(mapping: dict[str, str], name: str) -> tuple[str, str]:
    values = {mapping[part] for part in FAMILY_PARTS[name]}
    return next(value for value in values if value in {"HOT", "COLD"}), next(value for value in values if value in {"DRY", "MOIST"})


def smoothed(counts: Counter[tuple[str, str]]) -> dict[tuple[str, str], float]:
    total = sum(counts.values()) + 0.5 * len(QUADRANTS)
    return {quad: (counts[quad] + 0.5) / total for quad in QUADRANTS}


def first_quality(row: dict[str, str], page_rows: dict[str, list[dict[str, str]]], horizon: int) -> tuple[dict[str, str] | None, str]:
    origin_line, origin_index = line_no(row["locus"]), int(row["token_index"])
    choices: list[tuple[int, int, dict[str, str], str]] = []
    for candidate in page_rows[row["page"]]:
        delta = line_no(candidate["locus"]) - origin_line
        if delta < 0 or delta > horizon or (delta == 0 and int(candidate["token_index"]) <= origin_index):
            continue
        match = PREFIX_RE.match(candidate["eva"])
        if match:
            choices.append((delta, int(candidate["token_index"]), candidate, family(match.group("a"), match.group("b"))))
    if not choices:
        return None, "NONE"
    _, _, candidate, name = min(choices, key=lambda value: (value[0], value[1]))
    return candidate, name


def make_family_counts(tokens: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict[tuple[str, str, str], int]]:
    scopes: dict[str, Callable[[dict[str, str]], bool]] = {
        "ALL_SAFE_NO_F1R": lambda row: True,
        "HERBAL_ALL": lambda row: row["section"] == "H",
        "HERBAL_A": lambda row: row["section"] == "H" and row["language"] == "A",
    }
    lookup: dict[tuple[str, str, str], int] = {}
    output: list[dict[str, object]] = []
    for scope, predicate in scopes.items():
        selected = [row for row in tokens if predicate(row)]
        for mode in ("EXACT_Y_EY", "Q_PREFIX", "SUBSTRING"):
            events = {name: [] for name in FAMILIES}
            for row in selected:
                for name in surface_families(row["eva"], mode):
                    events[name].append(row)
            total = sum(map(len, events.values()))
            for name in FAMILIES:
                count = len(events[name])
                lookup[(scope, mode, name)] = count
                output.append({"scope": scope, "mode": mode, "family": name, "occurrences": count, "pages": len({row["page"] for row in events[name]}), "family_share": f"{count / total:.6f}" if total else "0.000000", "total_four_family_events": total})
    return output, lookup


def make_orientation_rows(lookup: dict[tuple[str, str, str], int], source_counts: Counter[tuple[str, str]]) -> list[dict[str, object]]:
    source_dist = smoothed(source_counts)
    output: list[dict[str, object]] = []
    for scope in ("ALL_SAFE_NO_F1R", "HERBAL_ALL", "HERBAL_A"):
        for mode in ("EXACT_Y_EY", "Q_PREFIX", "SUBSTRING"):
            group: list[dict[str, object]] = []
            for assignment, mapping in all_orientations():
                mapped: Counter[tuple[str, str]] = Counter()
                for name in FAMILIES:
                    mapped[mapped_quad(mapping, name)] += lookup[(scope, mode, name)]
                target = smoothed(mapped)
                tv = 0.5 * sum(abs(target[quad] - source_dist[quad]) for quad in QUADRANTS)
                group.append({"scope": scope, "mode": mode, "assignment_id": assignment, "k": mapping["k"], "t": mapping["t"], "ch": mapping["ch"], "sh": mapping["sh"], "hot_dry": mapped[("HOT", "DRY")], "hot_moist": mapped[("HOT", "MOIST")], "cold_dry": mapped[("COLD", "DRY")], "cold_moist": mapped[("COLD", "MOIST")], "total_variation_smoothed": f"{tv:.6f}", "is_v1": int(mapping == V1), "is_v2": int(mapping == V2)})
            group.sort(key=lambda row: (float(row["total_variation_smoothed"]), row["assignment_id"]))
            for rank, row in enumerate(group, 1):
                row["rank_within_scope_mode"] = rank
                output.append(row)
    return output


def make_state_word_audit(tokens: list[dict[str, str]]) -> list[dict[str, object]]:
    """Measure concrete chody/shody/shedy defaults against the nearest strict q-code.

    The distance calculation is deliberately visible: closest physical line,
    then closest token on that line, then source order.  Missing q-code pages
    remain missing rather than receiving an imputed value.
    """
    sequence = {id(row): index for index, row in enumerate(tokens)}
    quality_by_page: dict[str, list[tuple[int, int, int, str, str]]] = defaultdict(list)
    baseline = Counter()
    for row in tokens:
        match = PREFIX_RE.match(row["eva"])
        if not match:
            continue
        name = family(match.group("a"), match.group("b"))
        moisture = "DRY" if name in {"KCH", "TCH"} else "MOIST"
        baseline[moisture] += 1
        quality_by_page[row["page"]].append((line_no(row["locus"]), int(row["token_index"]), sequence[id(row)], moisture, name))

    specs: list[tuple[str, set[str], str, str]] = [
        ("CHODY", {"chody"}, "trocken oder Trockenklasse", "DRY_CLASS_DEFAULT_MEDIUM"),
        ("SHODY", {"shody"}, "gelernte Form im Trocken-Kontext; Inhalt offen", "MOIST_DEFAULT_REJECTED__WHOLE_FORM_OPEN"),
        ("SHEDY", {"shedy"}, "feucht oder Feuchtklasse", "REGISTER_LOCAL_MOIST_CLASS_DEFAULT_WEAK"),
        ("SHODY_OR_SHEDY", {"shody", "shedy"}, "keine gemeinsame Bedeutung; nur formale Nachbarschaft", "MERGE_REJECTED"),
    ]
    output: list[dict[str, object]] = []
    for state_id, surfaces, meaning, status in specs:
        selected = [row for row in tokens if row["eva"] in surfaces]
        contexts: list[tuple[str, list[dict[str, str]]]] = [("ALL_SAFE_NO_F1R", selected)]
        contexts.extend(
            (f"SECTION_{section}__LANG_{language}", [row for row in selected if row["section"] == section and row["language"] == language])
            for section, language in sorted({(row["section"], row["language"]) for row in selected})
        )
        for context, rows in contexts:
            nearest = Counter()
            within_one = Counter()
            no_q = 0
            for row in rows:
                candidates = quality_by_page[row["page"]]
                if not candidates:
                    no_q += 1
                    continue
                origin_line = line_no(row["locus"])
                origin_token = int(row["token_index"])
                origin_sequence = sequence[id(row)]
                candidate = min(
                    candidates,
                    key=lambda value: (
                        abs(value[0] - origin_line),
                        abs(value[1] - origin_token) if value[0] == origin_line else 999999,
                        abs(value[2] - origin_sequence),
                        value[2],
                    ),
                )
                nearest[candidate[3]] += 1
                if abs(candidate[0] - origin_line) <= 1:
                    within_one[candidate[3]] += 1
            assigned = nearest["DRY"] + nearest["MOIST"]
            local_assigned = within_one["DRY"] + within_one["MOIST"]
            output.append({
                "state_id": state_id,
                "surfaces": "|".join(sorted(surfaces)),
                "context": context,
                "occurrences": len(rows),
                "pages": len({row["page"] for row in rows}),
                "no_strict_q_on_page": no_q,
                "nearest_dry": nearest["DRY"],
                "nearest_moist": nearest["MOIST"],
                "nearest_moist_rate": f"{nearest['MOIST'] / assigned:.6f}" if assigned else "0.000000",
                "within_one_line_dry": within_one["DRY"],
                "within_one_line_moist": within_one["MOIST"],
                "within_one_line_moist_rate": f"{within_one['MOIST'] / local_assigned:.6f}" if local_assigned else "0.000000",
                "corpus_q_dry": baseline["DRY"],
                "corpus_q_moist": baseline["MOIST"],
                "corpus_q_moist_rate": f"{baseline['MOIST'] / sum(baseline.values()):.6f}",
                "working_default_de": meaning,
                "status": status,
                "claim_limit": "chody is the strongest dry-class candidate. shody's moist reading is rejected by its own context. shedy retains only a weak register-local moist-class reading; fresh and moistened are separate hypotheses and are not merged here.",
            })
    return output


def main() -> int:
    pages = safe_pages()
    inspection_tokens, guard = guarded_tokens(pages | MANUAL_EXTRA_PAGES)
    tokens = [row for row in inspection_tokens if row["page"] in pages]
    page_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inspection_tokens:
        page_rows[row["page"]].append(row)
    source_rows = read_tsv(ROOT / SOURCE_ROWS_REL)
    specs = read_tsv(ROOT / MANUAL_INPUTS["carrier_specs"])
    anchors = read_tsv(ROOT / MANUAL_INPUTS["anchors"])

    family_rows, lookup = make_family_counts(tokens)
    write_tsv(ROOT / OUTPUTS["family_counts"], family_rows, ("scope", "mode", "family", "occurrences", "pages", "family_share", "total_four_family_events"))

    section_counter: Counter[tuple[str, str, str]] = Counter()
    section_pages: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in tokens:
        for name in surface_families(row["eva"], "Q_PREFIX"):
            key = row["section"], row["language"], name
            section_counter[key] += 1
            section_pages[key].add(row["page"])
    section_rows = [{"section": section, "language": language, "family": name, "occurrences": section_counter[(section, language, name)], "pages": len(section_pages[(section, language, name)])} for section, language, name in sorted(section_counter)]
    write_tsv(ROOT / OUTPUTS["section_counts"], section_rows, ("section", "language", "family", "occurrences", "pages"))

    source_counts = Counter((row["thermal"], row["moisture"]) for row in source_rows if row["thermal"] in {"HOT", "COLD"} and row["moisture"] in {"DRY", "MOIST"})
    source_total = sum(source_counts.values())
    source_quad_rows = [{"thermal": thermal, "moisture": moisture, "observations": source_counts[(thermal, moisture)], "share_complete_rows": f"{source_counts[(thermal, moisture)] / source_total:.6f}"} for thermal, moisture in QUADRANTS]
    write_tsv(ROOT / OUTPUTS["source_quadrants"], source_quad_rows, ("thermal", "moisture", "observations", "share_complete_rows"))

    orientation_rows = make_orientation_rows(lookup, source_counts)
    write_tsv(ROOT / OUTPUTS["orientations"], orientation_rows, ("scope", "mode", "rank_within_scope_mode", "assignment_id", "k", "t", "ch", "sh", "hot_dry", "hot_moist", "cold_dry", "cold_moist", "total_variation_smoothed", "is_v1", "is_v2"))

    source_hot = sum(count for (thermal, _), count in source_counts.items() if thermal == "HOT") / source_total
    source_dry = sum(count for (_, moisture), count in source_counts.items() if moisture == "DRY") / source_total
    marginal_rows: list[dict[str, object]] = []
    for scope in ("ALL_SAFE_NO_F1R", "HERBAL_ALL", "HERBAL_A"):
        for mode in ("EXACT_Y_EY", "Q_PREFIX", "SUBSTRING"):
            counts = {name: lookup[(scope, mode, name)] for name in FAMILIES}
            total = sum(counts.values())
            fractions = {"K": (counts["KCH"] + counts["KSH"]) / total, "T": (counts["TCH"] + counts["TSH"]) / total, "CH": (counts["KCH"] + counts["TCH"]) / total, "SH": (counts["KSH"] + counts["TSH"]) / total}
            for axis, left, right in (("KT", "K", "T"), ("CH_SH", "CH", "SH")):
                for semantic, value, source_fraction in (("THERMAL", "HOT", source_hot), ("MOISTURE", "DRY", source_dry)):
                    for symbol in (left, right):
                        marginal_rows.append({"scope": scope, "mode": mode, "symbol_axis": axis, "semantic_axis": semantic, "mapping": f"{symbol}={value}", "target_fraction": f"{fractions[symbol]:.6f}", "source_fraction": f"{source_fraction:.6f}", "absolute_error": f"{abs(fractions[symbol] - source_fraction):.6f}"})
    write_tsv(ROOT / OUTPUTS["marginals"], marginal_rows, ("scope", "mode", "symbol_axis", "semantic_axis", "mapping", "target_fraction", "source_fraction", "absolute_error"))

    state_rows = make_state_word_audit(tokens)
    write_tsv(ROOT / OUTPUTS["states"], state_rows, ("state_id", "surfaces", "context", "occurrences", "pages", "no_strict_q_on_page", "nearest_dry", "nearest_moist", "nearest_moist_rate", "within_one_line_dry", "within_one_line_moist", "within_one_line_moist_rate", "corpus_q_dry", "corpus_q_moist", "corpus_q_moist_rate", "working_default_de", "status", "claim_limit"))

    heads: dict[str, dict[str, str]] = {}
    for row in tokens:
        if row["section"] == "H" and row["token_index"] == "1" and row["code"].startswith("@"):
            heads.setdefault(row["page"], row)
    head_counts = Counter(row["eva"] for row in heads.values())
    header_rows: list[dict[str, object]] = []
    for surface, count in sorted(head_counts.items(), key=lambda item: (-item[1], item[0])):
        if count < 2:
            continue
        evidence = [row for row in heads.values() if row["eva"] == surface]
        contacts, families = [], []
        for row in evidence:
            code, name = first_quality(row, page_rows, 3)
            contacts.append(f"{row['locus']}->{code['locus']}:{code['eva']}" if code else f"{row['locus']}->NONE")
            families.append(name)
        header_rows.append({"surface": surface, "header_occurrences": count, "global_occurrences": sum(row["eva"] == surface for row in tokens), "pages": "|".join(row["page"] for row in evidence), "nearest_quality_families_plus3": "|".join(families), "consistent_nonempty_family": int(len(set(families)) == 1 and families[0] != "NONE"), "contacts": "|".join(contacts)})
    write_tsv(ROOT / OUTPUTS["headers"], header_rows, ("surface", "header_occurrences", "global_occurrences", "pages", "nearest_quality_families_plus3", "consistent_nonempty_family", "contacts"))

    initials: list[dict[str, object]] = []
    for inventory, rows in (("ALL_TOKENS", tokens), ("HERBAL_PAGE_HEADS", list(heads.values()))):
        total = len(rows)
        union = sum(bool(row["eva"]) and row["eva"][0] in "ptkf" for row in rows)
        initials.append({"inventory": inventory, "initial": "P_OR_T_OR_K_OR_F", "occurrences": union, "total": total, "rate": f"{union / total:.6f}"})
        for char in "fkpt":
            count = sum(row["eva"].startswith(char) for row in rows)
            initials.append({"inventory": inventory, "initial": char, "occurrences": count, "total": total, "rate": f"{count / total:.6f}"})
    write_tsv(ROOT / OUTPUTS["initials"], initials, ("inventory", "initial", "occurrences", "total", "rate"))

    global_counts = Counter(row["eva"] for row in inspection_tokens)
    carrier_rows: list[dict[str, object]] = []
    for spec in specs:
        for row in (candidate for candidate in inspection_tokens if candidate["eva"] == spec["member_surface"]):
            if spec["match_scope"] == "HERBAL" and row["section"] != "H":
                continue
            position_ok = row["token_index"] == "1" and (spec["position_rule"] != "PAGE_HEAD" or row["code"].startswith("@"))
            if not position_ok:
                continue
            code, name = first_quality(row, page_rows, int(spec["max_forward_lines"]))
            thermal, moisture, reading = v2_reading(name) if name != "NONE" else ("NONE", "NONE", "NONE")
            carrier_rows.append({"carrier_id": spec["carrier_id"], "member_surface": spec["member_surface"], "global_surface_occurrences": global_counts[spec["member_surface"]], "page": row["page"], "locus": row["locus"], "section": row["section"], "language": row["language"], "position_rule": spec["position_rule"], "quality_locus": code["locus"] if code else "NONE", "quality_surface": code["eva"] if code else "NONE", "distance_lines": line_no(code["locus"]) - line_no(row["locus"]) if code else "NONE", "observed_family": name, "expected_family": spec["expected_family"], "family_match": int(name == spec["expected_family"]), "v2_thermal": thermal, "v2_moisture": moisture, "v2_reading_de": reading, "working_role": spec["working_role"], "claim_limit": spec["claim_limit"]})
    carrier_rows.sort(key=lambda row: (row["carrier_id"], row["page"], row["locus"]))
    write_tsv(ROOT / OUTPUTS["carrier_evidence"], carrier_rows, ("carrier_id", "member_surface", "global_surface_occurrences", "page", "locus", "section", "language", "position_rule", "quality_locus", "quality_surface", "distance_lines", "observed_family", "expected_family", "family_match", "v2_thermal", "v2_moisture", "v2_reading_de", "working_role", "claim_limit"))

    specs_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    evidence_by_id: dict[str, list[dict[str, object]]] = defaultdict(list)
    for spec in specs:
        specs_by_id[spec["carrier_id"]].append(spec)
    for row in carrier_rows:
        evidence_by_id[str(row["carrier_id"])].append(row)
    summaries: list[dict[str, object]] = []
    for carrier_id, members in sorted(specs_by_id.items()):
        evidence = evidence_by_id.get(carrier_id, [])
        exact_twice = carrier_id.startswith("EXACT_") and len(members) == 1 and global_counts[members[0]["member_surface"]] == 2
        accepted = (
            len(evidence) >= 2
            and all(int(row["family_match"]) for row in evidence)
            and all(row["distance_lines"] != "NONE" and int(row["distance_lines"]) <= 3 for row in evidence)
        )
        summaries.append({"carrier_id": carrier_id, "members": "|".join(spec["member_surface"] for spec in members), "qualified_occurrences": len(evidence), "pages": "|".join(sorted({str(row["page"]) for row in evidence})) or "NONE", "observed_families": "|".join(sorted({str(row["observed_family"]) for row in evidence})) or "NONE", "expected_families": "|".join(sorted({spec["expected_family"] for spec in members})), "matching_occurrences": sum(int(row["family_match"]) for row in evidence), "exact_surface_occurs_twice_globally": int(exact_twice), "accepted_local_attachment": int(accepted), "working_role": members[0]["working_role"], "selection_scope": "EXPLORATORY_POST_HOC_CARRIER_SEARCH"})
    write_tsv(ROOT / OUTPUTS["carrier_summary"], summaries, ("carrier_id", "members", "qualified_occurrences", "pages", "observed_families", "expected_families", "matching_occurrences", "exact_surface_occurs_twice_globally", "accepted_local_attachment", "working_role", "selection_scope"))

    surfaces, types = [row["eva"] for row in tokens], {row["eva"] for row in tokens}
    suffix_rows: list[dict[str, object]] = []
    for suffix in ("or", "os", "dal"):
        selected = [row for row in tokens if row["eva"].endswith(suffix)]
        suffix_rows.append({"audit_kind": "SUFFIX", "surface_or_pair": suffix, "occurrences": len(selected), "types_or_left_bases": len({row["eva"] for row in selected}), "standalone_occurrences_or_shared_bases": sum(row["eva"] == suffix for row in selected), "line_head_occurrences": sum(row["token_index"] == "1" for row in selected), "interpretation": "PRODUCTIVE_ENDING_SLOT_NOT_PLANT_OR_NAME_MEANING"})
    bases = {ending: {surface[: -len(ending)] for surface in types if surface.endswith(ending) and surface != ending} for ending in ("or", "os", "dal", "dar", "dy")}
    for left, right in (("or", "os"), ("dal", "dar"), ("dal", "dy")):
        suffix_rows.append({"audit_kind": "BASE_PAIR", "surface_or_pair": f"{left}<->{right}", "occurrences": "NOT_APPLICABLE", "types_or_left_bases": len(bases[left]), "standalone_occurrences_or_shared_bases": len(bases[left] & bases[right]), "line_head_occurrences": "NOT_APPLICABLE", "interpretation": "SHARED_BASES_SUPPORT_ENDING_ALTERNATION"})
    write_tsv(ROOT / OUTPUTS["suffixes"], suffix_rows, ("audit_kind", "surface_or_pair", "occurrences", "types_or_left_bases", "standalone_occurrences_or_shared_bases", "line_head_occurrences", "interpretation"))

    binding_rows = [
        {"priority": 1, "rule_id": "SAME_LINE", "working_rule": "Bind a quality code first to a carrier or clause on the same physical line.", "historical_basis": "Clm667 inline rows and Mainz opening clauses", "voynich_consequence": "dsheody and tchdor contacts outrank distant page-head matches."},
        {"priority": 2, "rule_id": "LOCAL_OPENING", "working_rule": "Allow the next one or two lines when a carrier visibly opens a record.", "historical_basis": "Mainz rubric plus opening sentence", "voynich_consequence": "kooiin plus next-line TCH and f45v plus line-three KCH are admissible."},
        {"priority": 3, "rule_id": "FORWARD_BLOCK", "working_rule": "A line-first quality header can govern a bounded following list until a peer header.", "historical_basis": "Pal.lat.1234 quality-degree columns", "voynich_consequence": "Search forward from headers rather than backward from any first page token."},
        {"priority": 4, "rule_id": "EXPLICIT_REANCHOR", "working_rule": "Long binding needs a repeated name stem class word or uninterrupted visible block.", "historical_basis": "Mainz re-anchoring and Pal.lat.1234 nested part rubrics", "voynich_consequence": "Root leaf seed flower fruit wood and gum slots require repeated local carriers."},
        {"priority": 5, "rule_id": "NO_SILENT_BACKWARD_PAGE_BINDING", "working_rule": "Do not silently bind a later code eleven or twelve lines back to the first token.", "historical_basis": "No inspected comparator supports arbitrary backward page scope", "voynich_consequence": "Old f3r Diptam and f24r Cucurbita matches no longer orient the axes."},
    ]
    write_tsv(ROOT / OUTPUTS["binding"], binding_rows, ("priority", "rule_id", "working_rule", "historical_basis", "voynich_consequence"))

    dictionary: list[dict[str, object]] = [
        {"layer": "QUALITY_CONTEXT", "surface": "qo-", "composition_slot": "QUALITY_FIELD_WRAPPER", "default_meaning_de": "Temperament- oder Qualitätsfeld beginnt", "status": "STRUCTURAL_DEFAULT", "evidence": "Four corners and thirteen exact GDT622 minimal pairs.", "caveat": "q and o are not separately translated."},
        {"layer": "QUALITY_CONTEXT", "surface": "k", "composition_slot": "THERMAL", "default_meaning_de": "heiß", "status": "WORKING_DEFAULT_V2", "evidence": "f45v Chamaedrys local hot-dry anchor plus the retained GDT622 thermal lead.", "caveat": "Only inside qo plus k or t plus ch or sh; frequency leaves t-hot as a serious rival."},
        {"layer": "QUALITY_CONTEXT", "surface": "t", "composition_slot": "THERMAL", "default_meaning_de": "kalt", "status": "WORKING_DEFAULT_V2", "evidence": "Conditional f15v Herb Paris reads qotch as cold-dry.", "caveat": "Thermal sign is weaker than moisture sign."},
        {"layer": "QUALITY_CONTEXT", "surface": "ch", "composition_slot": "MOISTURE", "default_meaning_de": "trocken", "status": "WORKING_DEFAULT_V2_FLIPPED", "evidence": "CH occupies 87.5 to 94 percent in the principal cuts against 88.9 percent dry historical rows.", "caveat": "The historical rows are a readable sample not a complete unbiased list."},
        {"layer": "QUALITY_CONTEXT", "surface": "sh", "composition_slot": "MOISTURE", "default_meaning_de": "feucht", "status": "WORKING_DEFAULT_V2_FLIPPED", "evidence": "Binary complement of the ch-dry default.", "caveat": "Rare SH forms make named counterexamples important."},
    ]
    for name, surface in (("KCH", "qokch-"), ("KSH", "qoksh-"), ("TCH", "qotch-"), ("TSH", "qotsh-")):
        dictionary.append({"layer": "QUALITY_BUNDLE", "surface": surface, "composition_slot": "COMPOSITE_QUALITY", "default_meaning_de": v2_reading(name)[2], "status": "CONCRETE_WORKING_DEFAULT_V2", "evidence": "Formal 2x2 family plus orientation synthesis.", "caveat": "Strongest as a Herbal working reading; other registers may reuse the form abstractly."})
    dictionary.extend([
        {"layer": "QUALITY_CONTEXT", "surface": "-(y|ey)", "composition_slot": "QUALITY_ENDING", "default_meaning_de": "Qualitätscode endet oder bindet weiter", "status": "STRUCTURAL_DEFAULT", "evidence": "Both endings occur in all four corners.", "caveat": "No degree value is fixed."},
        {"layer": "HERBAL_HEAD", "surface": "p|t|k|f- at page head", "composition_slot": "ENTRY_INITIAL_SHELL", "default_meaning_de": "Eintragsanfang oder Initialhülle", "status": "NEW_STRUCTURAL_DEFAULT", "evidence": "Strong enrichment at Herbal page heads.", "caveat": "Contextual shell does not replace quality-context k or t."},
        {"layer": "HERBAL_HEAD", "surface": "kooiin", "composition_slot": "THICK_OR_CREEPING_ROOT_DRUG_SUBCLASS", "default_meaning_de": "kalt-trockene dicke oder kriechende Wurzeldroge; Wurzelstock-Unterklasse", "status": "CONCRETE_VISUAL_DEFAULT_MEDIUM", "evidence": "Two exact page heads both next-line TCH; f2v and f29v show different plants but compact underground stocks; koaiin f3v shows a segmented stock.", "caveat": "Wurzelstock is a modern visual gloss, not a claimed medieval rhizoma word; other rootstock-rich pages lack the form."},
        {"layer": "HERBAL_HEAD", "surface": "pdrairdy|podairol|podair|pdair|pdsairy", "composition_slot": "ROOT_PART_OR_RADIX", "default_meaning_de": "Wurzelteil oder Wurzeldrogen-Eintrag (Radix)", "status": "CONCRETE_VISUAL_DEFAULT_MEDIUM", "evidence": "All five p...air Herbal page heads accompany conspicuous underground structures on manually inspected official images.", "caveat": "Not specific enough for Faserwurzel or one species; f43v has two units and mixed q-onsets prove that temperament is separate."},
        {"layer": "HERBAL_HEAD", "surface": "air|dair inside p...air head", "composition_slot": "ROOT_PART_CORE_CANDIDATE", "default_meaning_de": "Wurzelteil oder Radix", "status": "COMPOSITIONAL_CORE_DEFAULT_MEDIUM", "evidence": "The five p...air heads share air or dair, while RF1b explicitly splits f39v pdair as p air.", "caveat": "Outside this page-head construction air remains unassigned."},
        {"layer": "HERBAL_HEAD", "surface": "poror(y)", "composition_slot": "RECORD_OPENER", "default_meaning_de": "Herbal-Eintrag eröffnet", "status": "RECLASSIFIED_FROM_PLANT_NAME", "evidence": "f15v and f24r open visibly different plant pages.", "caveat": "Exact grammatical wording remains open."},
        {"layer": "HERBAL_PART", "surface": "shor", "composition_slot": "REPRODUCTIVE_HEAD", "default_meaning_de": "Blüten- oder Fruchtstand; reproduktiver Kopf", "status": "CONCRETE_VISUAL_DEFAULT_WEAK", "evidence": "Eight exact occurrences on six of eleven inspected Herbal images, all with conspicuous reproductive structures; 67 of 91 panel occurrences are Herbal.", "caveat": "Several conspicuous reproductive images lack shor, and the form also occurs outside Herbal."},
        {"layer": "HERBAL_HEAD", "surface": "koary|korary", "composition_slot": "REPRODUCTIVE_DRUG_SUBCLASS", "default_meaning_de": "Frucht-, Samen- oder Reproduktivdroge", "status": "CONCRETE_VISUAL_DEFAULT_WEAK", "evidence": "The only two heads accompany many terminal bodies and early shor on f6v and f45v.", "caveat": "Both word boundaries are unstable, f45v also has a huge rootstock, and koair is explicitly excluded from this family."},
        {"layer": "QUALITY_FORM", "surface": "-ody|-edy", "composition_slot": "QUALITY_BEARING_ENDING_SHELL", "default_meaning_de": "Hülle einer Qualitäts- oder Zustandsform", "status": "STRUCTURAL_DEFAULT", "evidence": "chody shody and shedy are overwhelmingly line-internal and support productive ch/sh-bearing shells.", "caveat": "The ending has no independent English translation yet."},
        {"layer": "MATERIAL_STATE", "surface": "chody", "composition_slot": "DRY_CLASS", "default_meaning_de": "trocken oder Trockenklasse", "status": "CONCRETE_WORKING_DEFAULT_MEDIUM", "evidence": "65 of 66 assignable occurrences have a dry nearest strict q-code; 33 of 34 within one line are dry, with f1r excluded.", "caveat": "Getrocknet or exsiccata is a separate weaker preparation hypothesis, not silently merged with dry or sicca."},
        {"layer": "LEARNED_WHOLE_FORM", "surface": "shody", "composition_slot": "OPEN_CONTENT_IN_DRY_CONTEXT", "default_meaning_de": "gelernte Form im Trocken-Kontext; konkrete Bedeutung offen", "status": "MOIST_DEFAULT_REJECTED", "evidence": "Its nearest strict q-code is dry 37 times and moist once; within one line it is dry 14 and moist zero.", "caveat": "The ch/sh symmetry outside a licensed quality slot is insufficient to read it as moist."},
        {"layer": "MATERIAL_STATE", "surface": "shedy", "composition_slot": "MOIST_CLASS", "default_meaning_de": "feucht oder Feuchtklasse", "status": "REGISTER_LOCAL_DEFAULT_WEAK", "evidence": "79 of 326 assignable occurrences have a moist nearest q-code versus 57 of 512 strict q-codes globally.", "caveat": "The enrichment is section-variable and moist remains the minority; fresh and moistened are separate competing meanings."},
        {"layer": "FORM_ENDING", "surface": "-or|-os|-dal", "composition_slot": "PRODUCTIVE_ENDING", "default_meaning_de": "produktiver End- oder Grammatikslot", "status": "STRUCTURAL_DEFAULT", "evidence": "Large counts and many shared bases.", "caveat": "None means plant or name by itself."},
    ])
    for summary in summaries:
        if not int(summary["accepted_local_attachment"]):
            continue
        name = str(summary["expected_families"]).split("|")[0]
        dictionary.append({"layer": "RECURRENT_CARRIER", "surface": summary["members"], "composition_slot": summary["working_role"], "default_meaning_de": f"wiederkehrender Träger; lokaler Wert {v2_reading(name)[2]}", "status": "ATTACHMENT_DEFAULT_NOT_NOUN_TRANSLATION", "evidence": f"{summary['matching_occurrences']}/{summary['qualified_occurrences']} contacts carry {name}.", "caveat": "Different owner images or registers prevent one substance-name assignment."})
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, ("layer", "surface", "composition_slot", "default_meaning_de", "status", "evidence", "caveat"))

    by_line: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in inspection_tokens:
        by_line[(row["page"], line_no(row["locus"]))].append(row)
    line_text = {key: " ".join(row["eva"] for row in sorted(value, key=lambda item: int(item["token_index"]))) for key, value in by_line.items()}
    carrier_gloss = {"kooiin": "kalte-trockene dicke/kriechende Wurzeldroge", "koaiin": "dicke/kriechende Wurzeldrogen-Unterklasse", "pdrairdy": "Wurzelteil/Radix-Eintrag", "podairol": "Wurzelteil/Radix-Eintrag", "podair": "Wurzelteil/Radix-Eintrag", "pdsairy": "Wurzelteil/Radix-Eintrag", "pdair": "Wurzelteil/Radix-Eintrag", "koary": "Frucht-/Samen-/Reproduktivdroge?", "korary": "Frucht-/Samen-/Reproduktivdroge?", "shor": "Blüten-/Fruchtstand?", "chody": "trocken/Trockenklasse", "shody": "gelernte Form; Inhalt offen", "shedy": "feucht/Feuchtklasse?", "dsheody": "wiederkehrender Träger", "tchdor": "wiederkehrender Träger", "poraiin": "wiederkehrender Träger", "tshod": "wiederkehrender Träger", "yshol": "wiederkehrender Träger"}

    def render(text: str) -> tuple[str, list[str]]:
        output, names = [], []
        for surface in text.split():
            found = surface_families(surface, "Q_PREFIX")
            if found:
                names.extend(found)
                output.append(f"[{v2_reading(found[0])[2]}]")
            elif surface in carrier_gloss:
                output.append(f"[{carrier_gloss[surface]}]")
            else:
                output.append(f"<{surface}>")
        return " ".join(output), names

    reading_specs = [
        ("F15_A", "f15v", 4, 4, "conditional Herb Paris contact"), ("F15_B", "f15v", 6, 6, "conditional Herb Paris contact"),
        ("F24_PAIR", "f24r", 12, 12, "thermal minimal pair"), ("F25_PAIR", "f25r", 3, 3, "moisture minimal pair"), ("F28_PAIR", "f28v", 5, 5, "moisture minimal pair"),
        ("KOOIIN_F2", "f2v", 1, 2, "repeated page-head and rootstock candidate"), ("KOOIIN_F29", "f29v", 1, 2, "repeated page-head and rootstock candidate"), ("KOOAIIN_F3", "f3v", 1, 1, "one-edit rootstock candidate"),
        ("PDROOT_F18", "f18r", 1, 2, "underground-part candidate"), ("PDROOT_F43", "f43v", 1, 5, "underground-part candidate"),
        ("PDROOT_F23", "f23v", 1, 2, "underground-part candidate"), ("PDROOT_F31", "f31v", 1, 2, "underground-part candidate"),
        ("STATE_CHODY_F56", "f56r", 16, 16, "same-line dry-class candidate"),
        ("DSHEODY_F86", "f86v3", 17, 17, "exact repeated same-line carrier"), ("DSHEODY_F102", "f102r1", 4, 4, "exact repeated same-line carrier"),
        ("TCHDOR_F95", "f95r1", 6, 6, "exact repeated same-line carrier"), ("TCHDOR_F115", "f115v", 11, 11, "exact repeated same-line carrier"),
        ("PORAIIN_F107", "f107v", 37, 38, "exact repeated local carrier"), ("PORAIIN_F113", "f113v", 13, 13, "exact repeated same-line carrier"),
        ("CHAMAEDRYS_F45V", "f45v", 1, 3, "conditional local Chamaedrys hot-dry anchor"),
    ]
    readings: list[dict[str, object]] = []
    for reading_id, page, start, stop, basis in reading_specs:
        values = [line_text[(page, number)] for number in range(start, stop + 1) if (page, number) in line_text]
        if not values:
            continue
        rendered, names = [], []
        for value in values:
            translated, found = render(value)
            rendered.append(translated)
            names.extend(found)
        readings.append({"reading_id": reading_id, "page": page, "locus_span": f"{page}.{start}-{stop}", "surface_span": " / ".join(values), "working_reading_de": " / ".join(rendered), "quality_families": "|".join(names) or "NONE", "basis": basis, "unmapped_policy": "ANGLE_BRACKETS_PRESERVE_UNTRANSLATED_SURFACES"})
    write_tsv(ROOT / OUTPUTS["readings"], readings, ("reading_id", "page", "locus_span", "surface_span", "working_reading_de", "quality_families", "basis", "unmapped_policy"))

    v2_row = next(row for row in orientation_rows if row["scope"] == "HERBAL_A" and row["mode"] == "EXACT_Y_EY" and int(row["is_v2"]))
    v1_row = next(row for row in orientation_rows if row["scope"] == "HERBAL_A" and row["mode"] == "EXACT_Y_EY" and int(row["is_v1"]))
    accepted = [row for row in summaries if int(row["accepted_local_attachment"])]
    exact_twice = [row for row in accepted if int(row["exact_surface_occurs_twice_globally"])]
    result = {
        "schema": "GDT623_TEMPERAMENT_ORIENTATION_AND_ATTACHMENT_RESULT_V1",
        "experiment_id": "GDT623",
        "status": "WORKING_TRANSLATION_V2__MOISTURE_AXIS_FLIPPED__LOCAL_ATTACHMENT_REPAIRED",
        "claim_boundary": "Adopt k=hot t=cold ch=dry sh=moist inside the quality construction as the current Herbal throughput default. The ch-dry sign is substantially stronger than the k-hot sign. Conditional f15v and f45v anchors support v2; same-line f38r and local f45r from GDT622 remain counterevidence. Repeated local carrier-to-code attachments are real, but most carrier nouns remain open. kooiin and the five-member p-air family receive explicit visual root-slot defaults. chody is the first medium dry-class word candidate. shody's moist reading is rejected; shedy keeps only a weak register-local moist-class reading. shor and koary or korary receive weak reproductive-part defaults.",
        "guard": {"f84": "FORBIDDEN_AND_REJECTED_BEFORE_PAYLOAD", "f84r": "FORBIDDEN_AND_REJECTED_BEFORE_PAYLOAD", "f1r": "EXCLUDED_BEFORE_QUERY_ALLOW_LIST", "frequency_panel_pages": len(pages), "manual_extra_pages": sorted(MANUAL_EXTRA_PAGES), **guard},
        "source_frequency": {"complete_clm_rows": source_total, "hot": sum(count for (thermal, _), count in source_counts.items() if thermal == "HOT"), "dry": sum(count for (_, moisture), count in source_counts.items() if moisture == "DRY"), "quadrants": {f"{thermal}_{moisture}": source_counts[(thermal, moisture)] for thermal, moisture in QUADRANTS}, "sampling_limit": "readable 28-row sample not unbiased full census"},
        "working_v2": {"grammar": "qo+(k|t)+(ch|sh)+closure_or_continuation", "values": V2, "bundles_de": {name: v2_reading(name)[2] for name in FAMILIES}, "herbal_a_exact_frequency_rank": int(v2_row["rank_within_scope_mode"]), "herbal_a_exact_frequency_tv": float(v2_row["total_variation_smoothed"]), "old_v1_rank": int(v1_row["rank_within_scope_mode"]), "old_v1_tv": float(v1_row["total_variation_smoothed"]), "semantic_scope": "HERBAL_WORKING_DEFAULT"},
        "attachment": {"accepted_carrier_families": len(accepted), "accepted_exact_twice_carriers": len(exact_twice), "exact_twice_ids": [row["carrier_id"] for row in exact_twice], "kooiin": "COLD_DRY_THICK_OR_CREEPING_ROOT_DRUG_SUBCLASS_MEDIUM", "pd_air": "ROOT_PART_OR_RADIX_MEDIUM__TEMPERAMENT_SEPARATE", "shor": "REPRODUCTIVE_HEAD_WEAK", "koary_korary": "REPRODUCTIVE_DRUG_SUBCLASS_WEAK", "porory": "RECORD_OPENER_NOT_CUCURBITA_NAME", "scope_rule": "SAME_LINE_THEN_LOCAL_OPENING_THEN_FORWARD_BLOCK_WITH_REANCHOR"},
        "state_words": {"chody": "DRY_OR_DRY_CLASS_MEDIUM", "shody": "MOIST_READING_REJECTED__WHOLE_FORM_OPEN", "shedy": "MOIST_CLASS_REGISTER_LOCAL_WEAK", "ody_edy": "QUALITY_BEARING_ENDING_SHELL"},
        "anchors": {"rows": len(anchors), "v2_support": [row["anchor_id"] for row in anchors if row["result"].startswith("SUPPORTS_V2")], "v1_counterevidence": [row["anchor_id"] for row in anchors if row["result"].startswith("SUPPORTS_V1")], "rejected_distant": [row["anchor_id"] for row in anchors if row["result"] == "V1_MATCH_NOT_BINDABLE"]},
        "summary": {"safe_pages_no_f1r": len(pages), "safe_tokens_no_f1r": len(tokens), "herbal_page_heads": len(heads), "herbal_page_head_types": len(head_counts), "repeated_header_types": len(header_rows), "concrete_reading_spans": len(readings), "historical_layout_rows": len(read_tsv(ROOT / MANUAL_INPUTS["layout"])), "visual_rows": len(read_tsv(ROOT / MANUAL_INPUTS["visual"])), "visual_role_rows": len(read_tsv(ROOT / MANUAL_INPUTS["visual_roles"]))},
        "inputs": {str(path): sha256(ROOT / path) for path in (SAFE_REL, TOKENS_REL, SOURCE_ROWS_REL, GDT622_REPORT_REL, GDT622_PAIRS_REL, *MANUAL_INPUTS.values())},
        "outputs": {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"},
    }
    result["content_sha256"] = canonical_hash(result)
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"GDT623 built: safe_tokens={len(tokens)} sealed_rows_rejected={guard.get('skipped_forbidden', 0)} exact_twice_carriers={len(exact_twice)} v2_rank={v2_row['rank_within_scope_mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
