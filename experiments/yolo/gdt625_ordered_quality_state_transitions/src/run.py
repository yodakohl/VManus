#!/usr/bin/env python3
"""Build GDT625: ordered quality paths and the cth- Herbal-part reader."""

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
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions")
ART = ROOT / BASE_REL / "artifacts"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
ALLOWLIST_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/PAGE_ALLOWLIST.tsv")
GDT624_RESULT_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/RESULT.json")
GDT624_READER_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/PRODUCTIVE_READER.tsv")
HISTORICAL_REL = BASE_REL / "artifacts/HISTORICAL_PROCESS_COMPARATORS.tsv"
VISUAL_REL = BASE_REL / "artifacts/MANUAL_VISUAL_JUDGMENTS.tsv"
OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "occurrences": BASE_REL / "artifacts/TERMINAL_QUALITY_OCCURRENCES.tsv",
    "pairs": BASE_REL / "artifacts/SUCCESSIVE_QUALITY_PAIRS.tsv",
    "matrix": BASE_REL / "artifacts/SUCCESSIVE_TRANSITION_MATRIX.tsv",
    "directions": BASE_REL / "artifacts/MOISTURE_DIRECTION_SUMMARY.tsv",
    "cycles": BASE_REL / "artifacts/THREE_STATE_CYCLES.tsv",
    "bridges": BASE_REL / "artifacts/INTERVENING_TOKEN_CANDIDATES.tsv",
    "term_roles": BASE_REL / "artifacts/CANDIDATE_TERM_ROLE_SUMMARY.tsv",
    "cth_family": BASE_REL / "artifacts/CTH_ROOT_FAMILY.tsv",
    "cthy_contacts": BASE_REL / "artifacts/CTHY_PART_CONTACTS.tsv",
    "quality_contacts": BASE_REL / "artifacts/ANCHOR_QUALITY_CONTACTS.tsv",
    "quality_contact_summary": BASE_REL / "artifacts/ANCHOR_QUALITY_SUMMARY.tsv",
    "cases": BASE_REL / "artifacts/CONCRETE_LOCAL_READINGS.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

TERMINAL_RE = re.compile(
    r"^(?P<prefix>.*?)(?P<thermal>k|t)(?P<moisture>ch|sh)(?P<e>e?)(?P<d>d?)y$"
)
REGISTERED_PREFIXES = {"", "o", "qo"}
OPENED_IMAGE_PAGES = {"f2v", "f3v", "f6v", "f15v", "f18r", "f23v", "f29v", "f31v", "f39v", "f43v", "f45v"}
ROLE_TERMS = ("cthy", "shor", "chor", "dair", "sair", "okaiin", "otar")
PART_TERMS = {"shor", "chor", "dair"}
KNOWN_ANCHORS = {
    "cthy", "shor", "chor", "dshor", "dair", "sair", "okaiin",
    "kooiin", "koaiin", "korary", "koary",
}
STATE_DE = {
    ("k", "ch"): "heiß-trocken", ("k", "sh"): "heiß-feucht",
    ("t", "ch"): "kalt-trocken", ("t", "sh"): "kalt-feucht",
}
STATE_ID = {
    ("k", "ch"): "KCH", ("k", "sh"): "KSH",
    ("t", "ch"): "TCH", ("t", "sh"): "TSH",
}


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


def safe_pages() -> set[str]:
    pages = {row["page"] for row in read_tsv(ROOT / ALLOWLIST_REL)}
    if len(pages) != 179 or "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("unsafe page allow-list")
    return pages


def guarded_query(relative_path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(relative_path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded query failed")
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guard statistics missing")
    stats = {key: int(value) for key, value in json.loads(stats_lines[0][12:]).items()}
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(row["page"] == "f1r" or row["page"].startswith("f84") for row in rows):
        raise RuntimeError("forbidden page materialized")
    return rows, stats


def line_number(locus: str) -> int:
    match = re.search(r"\.([0-9]+)$", locus)
    if not match:
        raise ValueError(locus)
    return int(match.group(1))


def token_sort_key(row: dict[str, str]) -> tuple[str, int, int]:
    return row["page"], line_number(row["locus"]), int(row["token_index"])


def parse_terminal(surface: str) -> dict[str, object] | None:
    match = TERMINAL_RE.fullmatch(surface)
    if not match:
        return None
    thermal, moisture = match.group("thermal"), match.group("moisture")
    prefix = match.group("prefix")
    return {
        "prefix": prefix,
        "thermal": thermal,
        "moisture": moisture,
        "e_bit": int(bool(match.group("e"))),
        "d_bit": int(bool(match.group("d"))),
        "state_id": STATE_ID[thermal, moisture],
        "state_de": STATE_DE[thermal, moisture],
        "registered": int(prefix in REGISTERED_PREFIXES),
    }


def stable_capacities(cross_rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    stable: dict[str, Counter[str]] = {}
    for row in cross_rows:
        editions = [Counter(row[field].split()) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        universe = set().union(*(counter.keys() for counter in editions))
        stable[row["locus"]] = Counter({
            word: min(counter[word] for counter in editions)
            for word in universe if min(counter[word] for counter in editions) > 0
        })
    return stable


def make_line_maps(tokens: list[dict[str, str]]) -> tuple[dict[str, list[str]], dict[str, list[dict[str, str]]], dict[str, dict[tuple[str, int], int]]]:
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sorted(tokens, key=token_sort_key):
        by_line[row["locus"]].append(row)
        by_page[row["page"]].append(row)
    line_words = {locus: [row["eva"] for row in rows] for locus, rows in by_line.items()}
    positions: dict[str, dict[tuple[str, int], int]] = {}
    for page, rows in by_page.items():
        positions[page] = {(row["locus"], int(row["token_index"])): index for index, row in enumerate(rows)}
    return line_words, by_page, positions


def make_occurrences(tokens: list[dict[str, str]], stable: dict[str, Counter[str]]) -> tuple[list[dict[str, object]], dict[str, list[dict[str, object]]]]:
    ordinals: Counter[tuple[str, str]] = Counter()
    rows: list[dict[str, object]] = []
    by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for token in sorted(tokens, key=token_sort_key):
        parsed = parse_terminal(token["eva"])
        if parsed is None:
            continue
        key = token["locus"], token["eva"]
        ordinals[key] += 1
        row: dict[str, object] = {
            "occurrence_id": f"G625-Q{len(rows) + 1:04d}",
            "page": token["page"], "locus": token["locus"], "line_number": line_number(token["locus"]),
            "token_index": int(token["token_index"]), "surface": token["eva"], "section": token["section"],
            "language": token["language"], "hand": token["hand"], "prefix": parsed["prefix"] or "BARE",
            "registered_grid": parsed["registered"], "thermal": parsed["thermal"], "moisture": parsed["moisture"],
            "e_bit": parsed["e_bit"], "d_bit": parsed["d_bit"], "state_id": parsed["state_id"],
            "working_state_de": parsed["state_de"],
            "triple_reading_token_stable": int(ordinals[key] <= stable.get(token["locus"], Counter())[token["eva"]]),
        }
        rows.append(row)
        by_page[token["page"]].append(row)
    for page_rows in by_page.values():
        page_rows.sort(key=lambda item: (int(item["line_number"]), int(item["token_index"])))
    return rows, by_page


def relation(first: dict[str, object], second: dict[str, object]) -> tuple[str, str, str]:
    ft, fm, st, sm = str(first["thermal"]), str(first["moisture"]), str(second["thermal"]), str(second["moisture"])
    if ft == st and fm == sm:
        return "SAME_QUADRANT", f"{first['state_id']}->{second['state_id']}", "gleicher Qualitätszustand"
    if ft == st:
        if fm == "ch":
            return "MOISTURE_FLIP", "DRY_TO_MOIST", "befeuchten/einweichen, falls derselbe Träger"
        return "MOISTURE_FLIP", "MOIST_TO_DRY", "trocknen, falls derselbe Träger"
    if fm == sm:
        return "THERMAL_FLIP", "HOT_TO_COLD" if ft == "k" else "COLD_TO_HOT", "kühlen/erwärmen, falls derselbe Träger"
    return "BOTH_AXES_FLIP", f"{first['state_id']}->{second['state_id']}", "kombinierter Zustands- oder Trägerwechsel"


def frame_relation(first: dict[str, object], second: dict[str, object]) -> str:
    same_ed = (first["e_bit"], first["d_bit"]) == (second["e_bit"], second["d_bit"])
    if same_ed and first["prefix"] == second["prefix"]:
        return "EXACT_PREFIX_E_D"
    if same_ed and int(first["registered_grid"]) and int(second["registered_grid"]):
        return "REGISTERED_PREFIX_CHANGE__SAME_E_D"
    if same_ed:
        return "SAME_E_D__EXTENDED_PREFIX_CHANGE"
    return "E_OR_D_FRAME_CHANGE"


def between_context(first: dict[str, object], second: dict[str, object], line_words: dict[str, list[str]]) -> tuple[list[str], str]:
    first_words = line_words[str(first["locus"])]
    first_index, second_index = int(first["token_index"]) - 1, int(second["token_index"]) - 1
    if first["locus"] == second["locus"]:
        return first_words[first_index + 1:second_index], " ".join(first_words)
    second_words = line_words[str(second["locus"])]
    return first_words[first_index + 1:] + second_words[:second_index], " ".join(first_words) + " / " + " ".join(second_words)


def following(occurrence: dict[str, object], page_rows: dict[str, list[dict[str, str]]], positions: dict[str, dict[tuple[str, int], int]]) -> list[str]:
    page = str(occurrence["page"])
    index = positions[page][str(occurrence["locus"]), int(occurrence["token_index"])]
    return [row["eva"] for row in page_rows[page][index + 1:index + 7] if len(row["eva"]) >= 3 and parse_terminal(row["eva"]) is None]


def make_pairs(by_page: dict[str, list[dict[str, object]]], line_words: dict[str, list[str]], page_rows: dict[str, list[dict[str, str]]], positions: dict[str, dict[tuple[str, int], int]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    internal: list[dict[str, object]] = []
    for page in sorted(by_page):
        for first, second in zip(by_page[page], by_page[page][1:]):
            line_delta = int(second["line_number"]) - int(first["line_number"])
            if line_delta > 1:
                continue
            between, context = between_context(first, second, line_words)
            axis, direction, reading = relation(first, second)
            first_follow, second_follow = following(first, page_rows, positions), following(second, page_rows, positions)
            repeated = []
            for word in first_follow:
                if word in second_follow and word not in repeated:
                    repeated.append(word)
            context_terms = set(context.replace(" / ", " ").split())
            row: dict[str, object] = {
                "pair_id": f"G625-P{len(rows) + 1:04d}", "page": page,
                "first_locus": first["locus"], "second_locus": second["locus"], "line_delta": line_delta,
                "first_surface": first["surface"], "second_surface": second["surface"],
                "first_state": first["state_id"], "second_state": second["state_id"],
                "axis_relation": axis, "direction": direction, "frame_relation": frame_relation(first, second),
                "intervening_token_count": len(between), "intervening_tokens": "|".join(between) or "DIRECT",
                "repeated_following_terms": "|".join(repeated) or "NONE",
                "known_local_anchors": "|".join(sorted(KNOWN_ANCHORS & context_terms)) or "NONE",
                "both_triple_token_stable": int(int(first["triple_reading_token_stable"]) and int(second["triple_reading_token_stable"])),
                "section": first["section"], "opened_image_page": int(page in OPENED_IMAGE_PAGES),
                "working_relation_de": reading, "surface_context": context,
            }
            rows.append(row)
            internal.append({"first": first, "second": second, "between": between, "row": row})
    return rows, internal


def make_matrix(pairs: list[dict[str, object]]) -> list[dict[str, object]]:
    states = ("KCH", "KSH", "TCH", "TSH")
    rows: list[dict[str, object]] = []
    for locality, delta in (("SAME_LINE", 0), ("NEXT_LINE", 1), ("LOCAL_TOTAL", None)):
        local = [row for row in pairs if delta is None or int(row["line_delta"]) == delta]
        for scope in ("ALL_TERMINAL", "SAME_E_D", "EXACT_FRAME"):
            selected = local
            if scope == "SAME_E_D":
                selected = [row for row in local if row["frame_relation"] != "E_OR_D_FRAME_CHANGE"]
            elif scope == "EXACT_FRAME":
                selected = [row for row in local if row["frame_relation"] == "EXACT_PREFIX_E_D"]
            counts = Counter((str(row["first_state"]), str(row["second_state"])) for row in selected)
            for first in states:
                for second in states:
                    rows.append({"locality": locality, "frame_scope": scope, "first_state": first, "second_state": second, "successive_pairs": counts[first, second]})
    return rows


def make_directions(pairs: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for locality, delta in (("SAME_LINE", 0), ("NEXT_LINE", 1), ("LOCAL_TOTAL", None)):
        for scope in ("ALL_TERMINAL", "SAME_E_D", "EXACT_FRAME"):
            for direction in ("DRY_TO_MOIST", "MOIST_TO_DRY"):
                selected = []
                for row in pairs:
                    if row["direction"] != direction or (delta is not None and int(row["line_delta"]) != delta):
                        continue
                    if scope == "SAME_E_D" and row["frame_relation"] == "E_OR_D_FRAME_CHANGE":
                        continue
                    if scope == "EXACT_FRAME" and row["frame_relation"] != "EXACT_PREFIX_E_D":
                        continue
                    selected.append(row)
                rows.append({
                    "locality": locality, "frame_scope": scope, "direction": direction,
                    "working_operation_de": "einweichen/befeuchten" if direction == "DRY_TO_MOIST" else "trocknen/abtrocknen lassen",
                    "pairs": len(selected), "stable_pairs": sum(int(row["both_triple_token_stable"]) for row in selected),
                    "opened_image_pairs": sum(int(row["opened_image_page"]) for row in selected),
                    "direct_pairs": sum(row["intervening_tokens"] == "DIRECT" for row in selected),
                    "example_pair_ids": "|".join(str(row["pair_id"]) for row in selected[:8]) or "NONE",
                })
    return rows


def make_cycles(by_page: dict[str, list[dict[str, object]]], line_words: dict[str, list[str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for page in sorted(by_page):
        for first, middle, last in zip(by_page[page], by_page[page][1:], by_page[page][2:]):
            if int(middle["line_number"]) - int(first["line_number"]) > 1 or int(last["line_number"]) - int(middle["line_number"]) > 1:
                continue
            if not (first["thermal"] == middle["thermal"] == last["thermal"] and first["moisture"] == last["moisture"] != middle["moisture"]):
                continue
            loci: list[str] = []
            for item in (first, middle, last):
                if str(item["locus"]) not in loci:
                    loci.append(str(item["locus"]))
            context = " / ".join(" ".join(line_words[locus]) for locus in loci)
            ordinary = [word for word in context.replace(" / ", " ").split() if len(word) >= 3 and parse_terminal(word) is None]
            repeated = sorted(word for word, count in Counter(ordinary).items() if count > 1)
            dry_first = first["moisture"] == "ch"
            rows.append({
                "cycle_id": f"G625-C{len(rows) + 1:03d}", "page": page, "loci": "|".join(loci),
                "first_surface": first["surface"], "middle_surface": middle["surface"], "last_surface": last["surface"],
                "state_path": f"{first['state_id']}->{middle['state_id']}->{last['state_id']}",
                "relation_default_de": "trocken-feucht-trocken; Einweichen-Trocknen nur bei gleichem Träger" if dry_first else "feucht-trocken-feucht; Trocknen-Befeuchten nur bei gleichem Träger",
                "all_three_triple_token_stable": int(all(int(item["triple_reading_token_stable"]) for item in (first, middle, last))),
                "repeated_context_terms": "|".join(repeated) or "NONE", "opened_image_page": int(page in OPENED_IMAGE_PAGES),
                "surface_context": context,
            })
    return rows


def make_bridges(pair_internal: list[dict[str, object]], tokens: list[dict[str, str]], stable: dict[str, Counter[str]]) -> list[dict[str, object]]:
    bridge_counts: dict[str, Counter[str]] = {key: Counter() for key in ("MOIST_TO_DRY", "DRY_TO_MOIST", "OTHER")}
    examples: dict[tuple[str, str], list[str]] = defaultdict(list)
    for item in pair_internal:
        row = item["row"]
        if int(row["line_delta"]) != 0:
            continue
        direction = str(row["direction"])
        bucket = direction if direction in ("MOIST_TO_DRY", "DRY_TO_MOIST") else "OTHER"
        for word in item["between"]:
            bridge_counts[bucket][word] += 1
            if len(examples[bucket, word]) < 5:
                examples[bucket, word].append(str(row["pair_id"]))
    corpus = Counter(row["eva"] for row in tokens)
    herbal = Counter(row["eva"] for row in tokens if row["section"] == "H")
    stable_total = Counter()
    for count in stable.values():
        stable_total.update(count)
    candidates = set(bridge_counts["MOIST_TO_DRY"]) | set(bridge_counts["DRY_TO_MOIST"])
    rows: list[dict[str, object]] = []
    for word in sorted(candidates, key=lambda item: (-bridge_counts["MOIST_TO_DRY"][item], -bridge_counts["DRY_TO_MOIST"][item], item)):
        role = "OPEN_BRIDGE"
        if word == "cthy":
            role = "BLATTGUT_OBJECT__NOT_DRYING_VERB"
        elif word == "otar":
            role = "THEN_UNTIL_OR_EXPLICIT_PROCESS_TOKEN_CANDIDATE"
        rows.append({
            "surface": word, "moist_to_dry_bridges": bridge_counts["MOIST_TO_DRY"][word],
            "dry_to_moist_bridges": bridge_counts["DRY_TO_MOIST"][word], "other_pair_bridges": bridge_counts["OTHER"][word],
            "direction_balance": bridge_counts["MOIST_TO_DRY"][word] - bridge_counts["DRY_TO_MOIST"][word],
            "corpus_occurrences": corpus[word], "herbal_occurrences": herbal[word],
            "herbal_share": f"{herbal[word] / corpus[word]:.6f}" if corpus[word] else "0.000000",
            "triple_stable_occurrences": stable_total[word],
            "drying_pair_ids": "|".join(examples["MOIST_TO_DRY", word]) or "NONE",
            "moistening_pair_ids": "|".join(examples["DRY_TO_MOIST", word]) or "NONE", "working_role": role,
        })
    return rows


def make_term_roles(tokens: list[dict[str, str]], line_words: dict[str, list[str]], cross_rows: list[dict[str, str]], stable: dict[str, Counter[str]]) -> list[dict[str, object]]:
    corpus = Counter(row["eva"] for row in tokens)
    herbal = Counter(row["eva"] for row in tokens if row["section"] == "H")
    edition = {field: Counter(word for row in cross_rows for word in row[field].split()) for field in ("it2a_clean", "rf1b_clean")}
    stable_total = Counter()
    for count in stable.values(): stable_total.update(count)
    pages: dict[str, set[str]] = defaultdict(set)
    loci: dict[str, set[str]] = defaultdict(set)
    positions: dict[str, Counter[str]] = defaultdict(Counter)
    for row in tokens:
        word = row["eva"]
        if word not in ROLE_TERMS: continue
        pages[word].add(row["page"]); loci[word].add(row["locus"])
        index, length = int(row["token_index"]), len(line_words[row["locus"]])
        if index == 1: positions[word]["FIRST"] += 1
        if index == length: positions[word]["LAST"] += 1
        if index not in (1, length): positions[word]["MIDDLE"] += 1
    defaults = {
        "cthy": ("Blattgut/Blattdroge (folium)", "MEDIUM_NEW_WORKING_DEFAULT"),
        "shor": ("Blüten-/Fruchtstand", "WEAK_TO_MEDIUM_INHERITED"),
        "chor": ("Blüten-/Pflanzenteil-Familie", "WEAK_CONTACT_SUPPORT"),
        "dair": ("Wurzelteil/Radix", "MEDIUM_INHERITED"), "sair": ("Wurzelteil; air-Familie", "WEAK_INHERITED"),
        "okaiin": ("Zubereitung/Materialcharge", "LOW_CARRIER_CANDIDATE"),
        "otar": ("danach/bis zum nächsten Zustand oder Prozesswort", "LOW_PROCESS_CANDIDATE"),
    }
    rows: list[dict[str, object]] = []
    for word in ROLE_TERMS:
        default, status = defaults[word]
        rows.append({
            "surface": word, "zl3b_occurrences": corpus[word], "it2a_occurrences": edition["it2a_clean"][word],
            "rf1b_occurrences": edition["rf1b_clean"][word], "triple_stable_occurrences": stable_total[word],
            "pages": len(pages[word]), "loci": len(loci[word]), "herbal_occurrences": herbal[word],
            "herbal_share": f"{herbal[word] / corpus[word]:.6f}", "line_first": positions[word]["FIRST"],
            "line_middle": positions[word]["MIDDLE"], "line_last": positions[word]["LAST"],
            "working_default_de": default, "status": status,
        })
    return rows


def make_cth_family(tokens: list[dict[str, str]], stable: dict[str, Counter[str]]) -> list[dict[str, object]]:
    counts = Counter(row["eva"] for row in tokens if row["eva"].startswith("cth"))
    herbal = Counter(row["eva"] for row in tokens if row["section"] == "H" and row["eva"].startswith("cth"))
    pages: dict[str, set[str]] = defaultdict(set)
    for row in tokens:
        if row["eva"].startswith("cth"): pages[row["eva"]].add(row["page"])
    stable_total = Counter()
    for count in stable.values(): stable_total.update(count)
    return [{
        "surface": surface, "cth_root": "cth", "remainder": surface[3:] or "BARE", "occurrences": count,
        "pages": len(pages[surface]), "herbal_occurrences": herbal[surface], "herbal_share": f"{herbal[surface] / count:.6f}",
        "triple_stable_occurrences": stable_total[surface], "root_default_de": "Blatt-/Krautteil-Familie",
        "surface_default_de": "Blattgut/Blattdroge" if surface == "cthy" else "cth-Pflanzenteilform; Endung offen",
        "status": "PRIMARY_CTHY_FORM" if surface == "cthy" else "ROOT_FAMILY_VARIANT",
    } for surface, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def make_cthy_contacts(tokens: list[dict[str, str]], line_words: dict[str, list[str]], stable: dict[str, Counter[str]]) -> list[dict[str, object]]:
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens: by_locus[row["locus"]].append(row)
    rows: list[dict[str, object]] = []
    for locus in sorted(by_locus, key=lambda item: (by_locus[item][0]["page"], line_number(item))):
        line = sorted(by_locus[locus], key=lambda item: int(item["token_index"]))
        for cthy in [row for row in line if row["eva"] == "cthy"]:
            for part in [row for row in line if row["eva"] in PART_TERMS]:
                distance = int(cthy["token_index"]) - int(part["token_index"])
                if abs(distance) > 7: continue
                rows.append({
                    "contact_id": f"G625-H{len(rows) + 1:03d}", "page": cthy["page"], "locus": locus,
                    "part_surface": part["eva"], "cthy_surface": "cthy", "signed_distance_part_to_cthy": distance,
                    "order": "PART_THEN_CTHY" if distance > 0 else "CTHY_THEN_PART", "adjacent": int(abs(distance) == 1),
                    "both_triple_token_stable": int(stable.get(locus, Counter())[part["eva"]] > 0 and stable.get(locus, Counter())["cthy"] > 0),
                    "working_part_pair_de": "Blüte/Fruchtstand und Blattgut" if part["eva"] in {"shor", "chor"} else "Wurzelteil und Blattgut",
                    "surface_line": " ".join(line_words[locus]),
                })
    return rows


def make_anchor_quality_contacts(tokens: list[dict[str, str]], line_words: dict[str, list[str]], stable: dict[str, Counter[str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Enumerate strict immediate contacts to a terminal quality form."""
    anchors = ("cthy", "shor", "chor", "dair", "sair", "air", "kooiin", "koaiin", "korary", "koary")
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_locus[row["locus"]].append(row)
    contacts: list[dict[str, object]] = []
    for locus in sorted(by_locus, key=lambda item: (by_locus[item][0]["page"], line_number(item))):
        line = sorted(by_locus[locus], key=lambda item: int(item["token_index"]))
        for anchor_index, anchor in enumerate(line):
            if anchor["eva"] not in anchors:
                continue
            for quality_index in (anchor_index - 1, anchor_index + 1):
                if not 0 <= quality_index < len(line):
                    continue
                quality = line[quality_index]
                parsed = parse_terminal(quality["eva"])
                if parsed is None:
                    continue
                contacts.append({
                    "contact_id": f"G625-A{len(contacts) + 1:03d}", "page": anchor["page"], "locus": locus,
                    "anchor_surface": anchor["eva"], "quality_surface": quality["eva"],
                    "order": "QUALITY_THEN_ANCHOR" if quality_index < anchor_index else "ANCHOR_THEN_QUALITY",
                    "state_id": parsed["state_id"], "working_state_de": parsed["state_de"],
                    "moisture": parsed["moisture"],
                    "both_triple_token_stable": int(stable.get(locus, Counter())[anchor["eva"]] > 0 and stable.get(locus, Counter())[quality["eva"]] > 0),
                    "surface_line": " ".join(line_words[locus]),
                })
    corpus = Counter(row["eva"] for row in tokens)
    pages: dict[str, set[str]] = defaultdict(set)
    for row in tokens:
        if row["eva"] in anchors:
            pages[row["eva"]].add(row["page"])
    summary: list[dict[str, object]] = []
    for anchor in anchors:
        selected = [row for row in contacts if row["anchor_surface"] == anchor]
        summary.append({
            "anchor_surface": anchor, "occurrences": corpus[anchor], "pages": len(pages[anchor]),
            "immediate_quality_contacts": len(selected),
            "stable_immediate_quality_contacts": sum(int(row["both_triple_token_stable"]) for row in selected),
            "dry_ch_contacts": sum(row["moisture"] == "ch" for row in selected),
            "moist_sh_contacts": sum(row["moisture"] == "sh" for row in selected),
            "working_role": "BLATTGUT_QUALITY_CARRIER" if anchor == "cthy" else "INHERITED_OR_OPEN_CARRIER",
        })
    return contacts, summary


def make_cases(pairs: list[dict[str, object]], cycles: list[dict[str, object]], cross_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    cross = {row["locus"]: row for row in cross_rows}
    pair_f29 = next(row for row in pairs if row["first_locus"] == "f29v.4" and row["first_surface"] == "otshy" and row["second_surface"] == "oltchy")
    pair_f45 = next(row for row in pairs if row["first_locus"] == "f45v.10" and row["second_locus"] == "f45v.11" and row["direction"] == "MOIST_TO_DRY")
    pair_f39 = next(row for row in pairs if row["first_locus"] == "f39v.8" and row["second_locus"] == "f39v.9" and row["direction"] == "DRY_TO_MOIST")
    cycle_f29 = next(row for row in cycles if row["page"] == "f29v" and row["state_path"] == "TCH->TSH->TCH")
    return [
        {
            "case_id": "F29_TWO_PART_BINDINGS", "page": "f29v", "loci": "f29v.4", "surface": cross["f29v.4"]["zl3b_clean"],
            "working_reading_de": "kalt-feuchte Zubereitung/Charge; Blattgut kalt-trocken",
            "local_parse": "[otshy okaiin] [cthy oltchy]", "operation_status": "PART_CONTRAST_PRIMARY__DRYING_SECONDARY",
            "visual_judgment": "ein Schriftblock und eine Pflanze, aber mehrere sichtbare Drogenteile; spiegelnde lokale Bindung schlägt reine Zeitfolge",
            "strength": "MEDIUM_CONCRETE_PART_READING", "source_ids": f"{pair_f29['pair_id']}|{cycle_f29['cycle_id']}",
        },
        {
            "case_id": "F45_REPRO_MOIST_DRY", "page": "f45v", "loci": "f45v.10|f45v.11", "surface": pair_f45["surface_context"],
            "working_reading_de": "Blüten-/Fruchtstand kalt-feucht; in der Folgezeile kalt-trocken",
            "local_parse": "[dshor otshy] / [or chor ytchy]", "operation_status": "TROCKNEN_POSSIBLE__SAME_PART_NOT_SECURE",
            "visual_judgment": "letzte benachbarte Zeilen desselben Blocks am selben Spross; keine gezeichnete Zeitachse",
            "strength": "LOW_TO_MEDIUM_TRANSITION", "source_ids": pair_f45["pair_id"],
        },
        {
            "case_id": "F39_DRY_MOIST_CONTROL", "page": "f39v", "loci": "f39v.8|f39v.9", "surface": pair_f39["surface_context"],
            "working_reading_de": "heiß-trocken; in der Folgezeile heiß-feucht",
            "local_parse": "qokchy / kshy", "operation_status": "BEFEUCHTEN_POSSIBLE__PART_CONTRAST_EQUALLY_LIVE",
            "visual_judgment": "dieselbe Pflanze, aber kein wiederholter lokaler Träger", "strength": "LOW_CONTROL", "source_ids": pair_f39["pair_id"],
        },
        {
            "case_id": "F45_CTHY_BINDINGS", "page": "f45v", "loci": "f45v.2|f45v.9",
            "surface": cross["f45v.2"]["zl3b_clean"] + " / " + cross["f45v.9"]["zl3b_clean"],
            "working_reading_de": "Blüten-/Pflanzenteil ... Blattgut / Blüten-/Pflanzenteil Blattgut",
            "local_parse": "chor ... cthy / ychor cthy", "operation_status": "NONE__PART_VOCABULARY",
            "visual_judgment": "blattreiche Pflanze; wiederholte chor-cthy-Nachbarschaft", "strength": "MEDIUM_CTHY_ROLE", "source_ids": "G625_CTHY_CONTACTS",
        },
        {
            "case_id": "F29_MULTI_PART", "page": "f29v", "loci": "f29v.1", "surface": cross["f29v.1"]["zl3b_clean"],
            "working_reading_de": "Wurzeldroge; Blüten-/Fruchtstand kalt-trocken ... Blattgut",
            "local_parse": "kooiin shor chetchy ... cthy", "operation_status": "NONE__MULTI_PART_ENTRY",
            "visual_judgment": "Wurzelstock, Blätter und reproduktive Organe sichtbar", "strength": "MEDIUM_MULTI_PART_READING",
            "source_ids": "G624_REPRO_F29|G625_CTHY_CONTACTS",
        },
    ]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = safe_pages()
    tokens, token_guard = guarded_query(TOKENS_REL, pages, "page,locus,code,kind,section,language,hand,token_index,eva")
    cross_rows, cross_guard = guarded_query(CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    tokens.sort(key=token_sort_key)
    stable = stable_capacities(cross_rows)
    line_words, page_rows, positions = make_line_maps(tokens)
    occurrences, by_page = make_occurrences(tokens, stable)
    pairs, pair_internal = make_pairs(by_page, line_words, page_rows, positions)
    matrix = make_matrix(pairs)
    directions = make_directions(pairs)
    cycles = make_cycles(by_page, line_words)
    bridges = make_bridges(pair_internal, tokens, stable)
    term_roles = make_term_roles(tokens, line_words, cross_rows, stable)
    cth_family = make_cth_family(tokens, stable)
    cthy_contacts = make_cthy_contacts(tokens, line_words, stable)
    quality_contacts, quality_contact_summary = make_anchor_quality_contacts(tokens, line_words, stable)
    cases = make_cases(pairs, cycles, cross_rows)

    write_tsv(ROOT / OUTPUTS["allowlist"], [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(ROOT / OUTPUTS["occurrences"], occurrences, ("occurrence_id", "page", "locus", "line_number", "token_index", "surface", "section", "language", "hand", "prefix", "registered_grid", "thermal", "moisture", "e_bit", "d_bit", "state_id", "working_state_de", "triple_reading_token_stable"))
    write_tsv(ROOT / OUTPUTS["pairs"], pairs, ("pair_id", "page", "first_locus", "second_locus", "line_delta", "first_surface", "second_surface", "first_state", "second_state", "axis_relation", "direction", "frame_relation", "intervening_token_count", "intervening_tokens", "repeated_following_terms", "known_local_anchors", "both_triple_token_stable", "section", "opened_image_page", "working_relation_de", "surface_context"))
    write_tsv(ROOT / OUTPUTS["matrix"], matrix, ("locality", "frame_scope", "first_state", "second_state", "successive_pairs"))
    write_tsv(ROOT / OUTPUTS["directions"], directions, ("locality", "frame_scope", "direction", "working_operation_de", "pairs", "stable_pairs", "opened_image_pairs", "direct_pairs", "example_pair_ids"))
    write_tsv(ROOT / OUTPUTS["cycles"], cycles, ("cycle_id", "page", "loci", "first_surface", "middle_surface", "last_surface", "state_path", "relation_default_de", "all_three_triple_token_stable", "repeated_context_terms", "opened_image_page", "surface_context"))
    write_tsv(ROOT / OUTPUTS["bridges"], bridges, ("surface", "moist_to_dry_bridges", "dry_to_moist_bridges", "other_pair_bridges", "direction_balance", "corpus_occurrences", "herbal_occurrences", "herbal_share", "triple_stable_occurrences", "drying_pair_ids", "moistening_pair_ids", "working_role"))
    write_tsv(ROOT / OUTPUTS["term_roles"], term_roles, ("surface", "zl3b_occurrences", "it2a_occurrences", "rf1b_occurrences", "triple_stable_occurrences", "pages", "loci", "herbal_occurrences", "herbal_share", "line_first", "line_middle", "line_last", "working_default_de", "status"))
    write_tsv(ROOT / OUTPUTS["cth_family"], cth_family, ("surface", "cth_root", "remainder", "occurrences", "pages", "herbal_occurrences", "herbal_share", "triple_stable_occurrences", "root_default_de", "surface_default_de", "status"))
    write_tsv(ROOT / OUTPUTS["cthy_contacts"], cthy_contacts, ("contact_id", "page", "locus", "part_surface", "cthy_surface", "signed_distance_part_to_cthy", "order", "adjacent", "both_triple_token_stable", "working_part_pair_de", "surface_line"))
    write_tsv(ROOT / OUTPUTS["quality_contacts"], quality_contacts, ("contact_id", "page", "locus", "anchor_surface", "quality_surface", "order", "state_id", "working_state_de", "moisture", "both_triple_token_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["quality_contact_summary"], quality_contact_summary, ("anchor_surface", "occurrences", "pages", "immediate_quality_contacts", "stable_immediate_quality_contacts", "dry_ch_contacts", "moist_sh_contacts", "working_role"))
    write_tsv(ROOT / OUTPUTS["cases"], cases, ("case_id", "page", "loci", "surface", "working_reading_de", "local_parse", "operation_status", "visual_judgment", "strength", "source_ids"))

    direction_lookup = {(row["locality"], row["frame_scope"], row["direction"]): int(row["pairs"]) for row in directions}
    role_lookup = {str(row["surface"]): row for row in term_roles}
    quality_contact_lookup = {str(row["anchor_surface"]): row for row in quality_contact_summary}
    cycle_paths = Counter(str(row["state_path"]) for row in cycles)
    historical, visual = read_tsv(ROOT / HISTORICAL_REL), read_tsv(ROOT / VISUAL_REL)
    result = {
        "schema": "GDT625_ORDERED_QUALITY_STATE_TRANSITIONS_RESULT_V1", "experiment_id": "GDT625",
        "status": "CTHY_BLATTGUT_PROMOTED__STATE_PATHS_SPLIT_PART_CONTRAST_FROM_PROCESS",
        "claim_boundary": "Ordered dry/moist forms provide an operation reading only after the same carrier is established. The strongest opened Herbal sequence on f29v instead resolves as two local part bindings: cold-moist okaiin and cold-dry cthy. cthy is 90/92 Herbal, belongs to a 408-token cth family, and repeatedly contacts shor/chor, so cth is promoted to a vegetative-part family and cthy to Blattgut or Blattdroge. Six dry-moist-dry paths remain process candidates, while otar is the first separate process/then/until token candidate. No isolated quality form is translated as an operation.",
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN_BEFORE_PAYLOAD", "f84r": "FORBIDDEN_BEFORE_PAYLOAD", "safe_pages": len(pages), "safe_tokens": len(tokens), "token_query": token_guard, "cross_query": cross_guard, "new_image_pages": 0, "opened_image_pages": sorted(OPENED_IMAGE_PAGES)},
        "quality_terminal_family": {"occurrences": len(occurrences), "types": len({str(row["surface"]) for row in occurrences}), "pages": len({str(row["page"]) for row in occurrences}), "loci": len({str(row["locus"]) for row in occurrences}), "registered_grid_occurrences": sum(int(row["registered_grid"]) for row in occurrences), "extended_prefix_occurrences": sum(not int(row["registered_grid"]) for row in occurrences), "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in occurrences)},
        "successive_local_pairs": {"pairs": len(pairs), "same_line": sum(int(row["line_delta"]) == 0 for row in pairs), "next_line": sum(int(row["line_delta"]) == 1 for row in pairs), "moisture_flips": sum(row["axis_relation"] == "MOISTURE_FLIP" for row in pairs), "same_line_dry_to_moist": direction_lookup["SAME_LINE", "ALL_TERMINAL", "DRY_TO_MOIST"], "same_line_moist_to_dry": direction_lookup["SAME_LINE", "ALL_TERMINAL", "MOIST_TO_DRY"], "local_exact_frame_dry_to_moist": direction_lookup["LOCAL_TOTAL", "EXACT_FRAME", "DRY_TO_MOIST"], "local_exact_frame_moist_to_dry": direction_lookup["LOCAL_TOTAL", "EXACT_FRAME", "MOIST_TO_DRY"]},
        "three_state_cycles": {"cycles": len(cycles), "path_counts": dict(sorted(cycle_paths.items())), "opened_image_cycles": sum(int(row["opened_image_page"]) for row in cycles), "f29v_cycle": next(str(row["cycle_id"]) for row in cycles if row["page"] == "f29v")},
        "cth_role": {"family_occurrences": sum(int(row["occurrences"]) for row in cth_family), "family_types": len(cth_family), "cthy_occurrences": int(role_lookup["cthy"]["zl3b_occurrences"]), "cthy_herbal_occurrences": int(role_lookup["cthy"]["herbal_occurrences"]), "cthy_stable_occurrences": int(role_lookup["cthy"]["triple_stable_occurrences"]), "cthy_part_contacts": len(cthy_contacts), "cthy_adjacent_part_contacts": sum(int(row["adjacent"]) for row in cthy_contacts), "cthy_immediate_quality_contacts": int(quality_contact_lookup["cthy"]["immediate_quality_contacts"]), "cthy_stable_quality_contacts": int(quality_contact_lookup["cthy"]["stable_immediate_quality_contacts"]), "cthy_dry_contacts": int(quality_contact_lookup["cthy"]["dry_ch_contacts"]), "cthy_moist_contacts": int(quality_contact_lookup["cthy"]["moist_sh_contacts"]), "working_default": "cth=vegetativer Pflanzenteil; cthy=Blattgut/Blattdroge"},
        "working_lexicon_updates": {"cth": "Blatt-/Krautteil-Familie", "cthy": "Blattgut/Blattdroge", "okaiin": "Zubereitung/Materialcharge (low)", "otar": "danach/bis oder separates Prozesswort (low)", "DRY_TO_MOIST": "befeuchten/einweichen, nur bei gleichem Träger", "MOIST_TO_DRY": "trocknen, nur bei gleichem Träger"},
        "manual_sources": {"historical_process_comparators": len(historical), "visual_judgments": len(visual), "concrete_readings": len(cases)},
        "inputs": {str(path): sha256(ROOT / path) for path in (TOKENS_REL, CROSS_REL, ALLOWLIST_REL, GDT624_RESULT_REL, GDT624_READER_REL, HISTORICAL_REL, VISUAL_REL)},
        "outputs": {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"},
    }
    result["content_sha256"] = canonical_hash(result)
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"GDT625 built: terminal={len(occurrences)} pairs={len(pairs)} moisture_flips={result['successive_local_pairs']['moisture_flips']} cycles={len(cycles)} cthy={role_lookup['cthy']['zl3b_occurrences']}/{role_lookup['cthy']['herbal_occurrences']}H contacts={len(cthy_contacts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
