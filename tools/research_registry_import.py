"""Deterministic, metadata-only import of the existing research registry.

No report pointers are dereferenced. Imported statuses are provenance, never
scientific review decisions. TSV source_row values are physical starting lines.
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
from pathlib import Path


SOURCES = {
    "ideas": "docs/IDEA_BACKLOG.md",
    "families": "experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv",
    "ledger": "experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv",
    "index": "experiments/EXPERIMENT_INDEX.tsv",
    "anchors": "experiments/semantic_assumptions/results/translation_anchor_acquisition_registry_v1.tsv",
}
IP = re.compile(r"(?<![A-Za-z0-9_])IP\d{3,}(?![A-Za-z0-9_])")
GDT = re.compile(r"GDT\d{3,}\Z")
STATED_GDT = re.compile(r"\A(GDT\d{3,})[_-]", re.IGNORECASE)
HISTORICAL_IDEA_MAX = 82
SIGNALS_POLICY = "NAVIGATION_HINTS_NOT_ADJUDICATION"
# Deliberately lexical: mentions of failures in questions, negated statements,
# or historical limitations are still mentions, not adjudicated outcomes.
SIGNAL_PATTERNS = {
    "capacity": r"\b(?:capacity|kapazität|power gate|power calibration)\b",
    "nonconfirmation": r"\b(?:nonconfirmation|non confirmation|nonconfirm|non confirm|not confirmed|unconfirmed|nicht bestätigt|nichtbestätigung)\b",
    "counterexample": r"\b(?:counterexamples?|counter examples?|gegenbeispiel\w*|gegenbeleg\w*)\b",
    "missing_binding": r"\b(?:missing (?:binding|ownership|antecedent)|no (?:independent |author visible |explicit )?(?:binding|ownership|antecedent)|binding (?:missing|unresolved)|fehlende? (?:bindung|zuordnung)|keine (?:bindung|zuordnung))\b",
    "source_unavailable": r"\b(?:source unavailable|source missing|missing source|no source available|no available source|unavailable source|quelle fehlt|quelle nicht verfügbar|fehlende quelle)\b",
    "control_failure": r"\b(?:control failure|control fail(?:ed|s)?|controls fail(?:ed)?|failed control|kontrollversagen|kontrolle gescheitert)\b",
    "correction": r"\b(?:correction\w*|corrected|korrektur\w*|korrigiert\w*)\b",
}


def _signals(record: dict) -> list[str]:
    parts = [record["source_status"], record["summary"]]
    for event in record["events"]:
        parts.extend(event[field] for field in ("status", "summary", "limitations"))
    # Paths, aliases, titles and arbitrary artifact columns are not signal input.
    text = "\n".join(parts).casefold().replace("_", " ").replace("-", " ")
    return sorted(code for code, pattern in SIGNAL_PATTERNS.items() if re.search(pattern, text))


def _load(root: Path) -> dict:
    result = {}
    for name, relative in SOURCES.items():
        raw = (root / relative).read_bytes()
        result[name] = {
            "path": relative,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "text": raw.decode("utf-8-sig"),
        }
    return result


def _rows(source: dict) -> list[tuple[int, dict]]:
    reader = csv.DictReader(io.StringIO(source["text"], newline=""), delimiter="\t")
    # Accessing fieldnames consumes the header, including multiline headers.
    if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
        raise ValueError(f"Missing or duplicate columns in {source['path']}")
    result = []
    previous = reader.line_num
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"Malformed TSV at {source['path']}:{previous + 1}")
        result.append((previous + 1, row))
        previous = reader.line_num
    return result


def _source(source: dict, line: int) -> dict:
    return {"path": source["path"], "locator": f"line:{line}", "sha256": source["sha256"]}


def _record(identifier: str, kind: str, title: str, summary: str, status: str) -> dict:
    return {
        "id": identifier, "kind": kind, "aliases": [], "title": title,
        "summary": summary, "source_status": status, "scope": "unknown",
        "review_status": "imported_unreviewed", "verdict": "unreviewed",
        "blockers": [],
        "reopen": {"policy": "unreviewed", "all_of": [], "not_sufficient": []},
        "relations": [], "sources": [], "events": [],
    }


def _definition(line: str, identifier: str) -> bool:
    # An ID as first table cell or first heading/bold-paragraph token.
    if not line.lstrip().startswith(('|', '#', '**')):
        return False
    stripped = re.sub(r"^[#\s|*]+", "", line)
    if not re.match(re.escape(identifier) + r"(?![A-Za-z0-9_])", stripped):
        return False
    remainder = stripped[len(identifier):].lstrip("* ")
    # A batch heading is a mention, not the first definition of its first ID.
    return not bool(re.match(r"(?:[–—/-]\s*IP\d|/\d|bis\s+IP\d)", remainder))


def _ideas(source: dict) -> list[dict]:
    lines = source["text"].splitlines()
    mentions: dict[str, list[int]] = {}
    for number, line in enumerate(lines, 1):
        for identifier in sorted(set(IP.findall(line))):
            mentions.setdefault(identifier, []).append(number)
    result = []
    for identifier, numbers in sorted(mentions.items()):
        definitions = [n for n in numbers if _definition(lines[n - 1], identifier)]
        if not definitions:
            # Keep unlocated definitions visible rather than inventing one.
            definitions = []
        chosen = (definitions or numbers)[0]
        heading = lines[chosen - 1].strip()
        title = re.sub(r"^[#\s|*]+", "", heading)
        title = re.sub(r"^" + identifier + r"\b[\s*|—:–-]*", "", title)
        title = title.split("|", 1)[0].strip() or identifier
        excerpts = []
        # Bounded excerpts, all mention locators retained separately below.
        for number in (definitions + [n for n in numbers if n not in definitions])[:8]:
            end = number
            if not lines[number - 1].lstrip().startswith("|"):
                for next_number in range(number + 1, min(number + 14, len(lines)) + 1):
                    candidate = lines[next_number - 1]
                    if candidate.startswith("#") or (IP.search(candidate) and _definition(candidate, IP.search(candidate).group())):
                        break
                    end = next_number
            excerpts.append({"locator": f"line:{number}", "end_line": end,
                             "text": "\n".join(lines[number - 1:end])[:1800]})
        first_excerpt = excerpts[0]["text"] if excerpts else heading
        status_match = re.search(r"Status:\s*`?([^`\n]+)", first_excerpt)
        status = status_match.group(1).strip() if status_match else "UNSPECIFIED_IN_DEFINITION"
        record = _record(identifier, "idea", title[:300], first_excerpt[:1400], status)
        record["aliases"] = [f"IDEA:{identifier}"]
        record["sources"] = [_source(source, n) for n in numbers]
        record["imported_fields"] = {
            "definition_lines": definitions,
            "mention_lines": numbers,
            "excerpts": excerpts,
            "excerpt_limit": 8,
            "definition_missing": not bool(definitions),
            "status_note": "Later mentions may supersede the extracted definition; not reconciled.",
        }
        result.append(record)
    return result


def _build(data: dict) -> list[dict]:
    records = {r["id"]: r for r in _ideas(data["ideas"])}
    for number, row in _rows(data["index"]):
        identifier = row["experiment_id"]
        if not GDT.fullmatch(identifier):
            raise ValueError(f"Non-exact GDT index key: {identifier!r}")
        if identifier in records:
            raise ValueError(f"Duplicate index ID: {identifier}")
        question = row.get("question", "")
        record = _record(identifier, "attempt", question or row.get("experiment_name", identifier),
                         question, row.get("status", ""))
        record["aliases"] = [f"EXPERIMENT:{identifier}"]
        record["sources"] = [_source(data["index"], number)]
        record["imported_fields"] = {key: row.get(key, "") for key in (
            "experiment_name", "latest_date", "primary_report", "manifest", "claim_ceiling")}
        records[identifier] = record
    for number, row in _rows(data["families"]):
        name = row["family"]
        identifier = "FAMILY:" + name
        if identifier in records:
            raise ValueError(f"Duplicate family ID: {identifier}")
        record = _record(identifier, "family", name, row.get("what_the_archive_establishes", ""), row.get("status", ""))
        record["aliases"] = [name]
        record["legacy_reopen_text"] = row.get("reopen_only_if", "")
        record["imported_fields"] = {"archive_pointer": row.get("archive_pointer", "")}
        record["sources"] = [_source(data["families"], number)]
        records[identifier] = record
    for number, row in _rows(data["anchors"]):
        name = row["candidate_id"]
        identifier = "ANCHOR:" + name
        if identifier in records:
            raise ValueError(f"Duplicate anchor ID: {identifier}")
        record = _record(identifier, "anchor", name, row.get("requested_observation", ""), row.get("ledger_status", ""))
        record["aliases"] = [name]
        record["imported_fields"] = dict(row)
        record["sources"] = [_source(data["anchors"], number)]
        records[identifier] = record
    for number, row in _rows(data["ledger"]):
        key = row["experiment"]
        if GDT.fullmatch(key) and key in records and records[key]["kind"] == "attempt":
            identifier = key
        else:
            identifier = "HIST:" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        if identifier not in records:
            records[identifier] = _record(identifier, "history", key, row.get("live_scope", ""), row.get("status", ""))
            records[identifier]["aliases"] = [key, "LEDGER:" + key]
            records[identifier]["imported_fields"] = {"exact_ledger_key": key}
        record = records[identifier]
        if record["kind"] == "history" and record["imported_fields"]["exact_ledger_key"] != key:
            raise ValueError("Truncated history hash collision")
        record["events"].append({
            "date": row.get("date", ""), "status": row.get("status", ""),
            "summary": row.get("live_scope", ""), "limitations": row.get("forbidden_inference", ""),
            "evidence": row.get("primary_report", ""), "source_row": number,
        })
        record["sources"].append(_source(data["ledger"], number))
        if record["kind"] == "attempt":
            record["aliases"].append("LEDGER:" + key)
    for record in records.values():
        if record["kind"] == "history":
            key = record["imported_fields"]["exact_ledger_key"]
            match = STATED_GDT.match(key)
            if match:
                target = match.group(1).upper()
                if target in records and records[target]["kind"] == "attempt":
                    # A stated experiment reference only: no idea identity claim
                    # and no transfer or merging of any event or verdict.
                    record["relations"].append({"type": "same_experiment_reference", "target": target})
        record["signals"] = _signals(record)
        record["signals_policy"] = SIGNALS_POLICY
        record["aliases"] = sorted(set(record["aliases"]))
        record["sources"].sort(key=lambda s: (s["path"], int(s["locator"].split(":")[1])))
        # Events retain original append-only source order, including duplicates.
    return [records[key] for key in sorted(records)]


def import_records(root: Path) -> list[dict]:
    """Read only the five declared metadata sources; return unreviewed records."""
    return _build(_load(Path(root)))


def import_manifest(root: Path) -> dict:
    """Return deterministic source hashes, preservation counts and ID gaps."""
    data = _load(Path(root))
    records = _build(data)
    ideas = {r["id"] for r in records if r["kind"] == "idea"}
    index_ids = {row["experiment_id"] for _, row in _rows(data["index"])}
    maximum = max((int(key[3:]) for key in index_ids), default=0)
    expected_gdt = {f"GDT{n:03d}" for n in range(1, maximum + 1)}
    idea_maximum = max((int(key[2:]) for key in ideas), default=0)
    expected_ideas = {f"IP{n:03d}" for n in range(1, max(HISTORICAL_IDEA_MAX, idea_maximum) + 1)}
    return {
        "version": 1,
        "build_version": 2,
        "signals_policy": SIGNALS_POLICY,
        "sources": [{"name": name, "path": source["path"], "sha256": source["sha256"],
                     "bytes": source["bytes"], "physical_lines": len(source["text"].splitlines()),
                     "data_rows": len(_rows(source)) if name != "ideas" else None}
                    for name, source in sorted(data.items())],
        "counts": {**{kind: sum(r["kind"] == kind for r in records) for kind in ("idea", "family", "attempt", "history", "anchor")},
                   "records": len(records), "ledger_events": sum(len(r["events"]) for r in records),
                   "stated_experiment_references": sum(len(r["relations"]) for r in records)},
        "missing_ids": {"ideas": sorted(expected_ideas - ideas), "index_gdt_sequence": sorted(expected_gdt - index_ids)},
        "historical_idea_baseline_max": HISTORICAL_IDEA_MAX,
        "observed_idea_max": idea_maximum,
        "unexpected_idea_ids": [],
        "ideas_without_definition": [r["id"] for r in records if r["kind"] == "idea" and r["imported_fields"]["definition_missing"]],
        "limitations": ["No scientific status adjudication or semantic merging.",
                        "Only exact GDT ledger keys attach to indexed attempts.",
                        "Anchored GDT prefix navigation links state experiment references, not same-idea identity; events stay separate.",
                        "Lexical signals are NAVIGATION_HINTS_NOT_ADJUDICATION, including negated or historical mentions.",
                        "All ledger rows preserved as events, including duplicate rows.",
                        "Report pointers retained without opening reports.",
                        "Idea excerpts bounded; all explicit ID mention line locators preserved.",
                        "Unexpanded prose ID ranges are not individual definition evidence."],
    }
