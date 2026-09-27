"""Descriptive word evidence from an explicitly admitted, guarded corpus.

No normalization, inferred morphology, semantic ranking, or pooled readers.
The disposable SQLite file is a cache, not a second research registry.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import sqlite3
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("experiments/semantic_assumptions/results/source_separator_transcription.tsv")
ALLOWLIST = Path("experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv")
DEFAULT_CACHE = ROOT / "experiments/semantic_assumptions/cache/word_profiles.sqlite"
EXPECTED_ALLOWLIST_SHA256 = "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
SCHEMA_VERSION = 1
SOURCE_COLUMNS = (
    "source_group_id", "edition", "locus", "page", "section", "currier", "hand",
    "code", "kind", "grammar_scope", "source_row_index", "source_group_index",
    "source_group_count", "paragraph_start", "paragraph_end", "left_separator",
    "right_separator", "ivtff_group_raw", "clean_ascii_fragments",
    "clean_ascii_fragment_count", "legacy_surface_positions_1based",
    "legacy_interlinear_row_present", "legacy_mapping_status",
)
COLUMNS = (
    "source_group_id", "edition", "page", "locus", "section", "currier", "hand",
    "kind", "source_group_index", "source_group_count", "ivtff_group_raw",
    "left_separator", "right_separator",
)
STRATA = ("section", "currier", "hand", "kind")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inputs(root: Path) -> tuple[dict[str, Any], list[str]]:
    # This reads only the public header; all data rows go through query-tsv.
    with (root / SOURCE).open(encoding="utf-8", newline="") as stream:
        header = next(csv.reader([stream.readline()], delimiter="\t"))
    if tuple(header) != SOURCE_COLUMNS:
        raise ValueError("source header changed; review the exact raw-group schema")
    allow_hash = _sha256(root / ALLOWLIST)
    if allow_hash != EXPECTED_ALLOWLIST_SHA256:
        raise ValueError("admission allowlist changed; explicit scope review is required")
    with (root / ALLOWLIST).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames != ["page"]:
            raise ValueError("unexpected allowlist header")
        pages = [row["page"] for row in reader]
    if len(pages) != 179 or len(set(pages)) != 179:
        raise ValueError("expected the fixed 179-selector admission")
    if any(not page or page.startswith("f84") or page == "f116v" for page in pages):
        raise ValueError("excluded selector in admission allowlist")
    return {
        "schema_version": SCHEMA_VERSION,
        "source": SOURCE.as_posix(),
        "source_sha256": _sha256(root / SOURCE),
        "allowlist": ALLOWLIST.as_posix(),
        "allowlist_sha256": allow_hash,
        "code": "tools/word_profiles.py",
        "code_sha256": _sha256(Path(__file__)),
        "selector_count": len(pages),
        "selectors": sorted(pages),
        "columns": list(COLUMNS),
        "matching": "exact_raw_group",
        "reader_policy": "alternate readings, never pooled",
        "exposure": "previously exposed exploration; not independent confirmation",
    }, sorted(pages)


def _guarded_rows(root: Path, pages: list[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    command = [str(root / "vmanus-exp"), "query-tsv", SOURCE.as_posix(), "--selector", "page"]
    for page in pages:
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(COLUMNS), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    if result.returncode:
        # Do not echo rejected payloads, command paths, or unrelated stderr.
        raise ValueError("guarded query failed; no cache was published")
    reports = [line[12:] for line in result.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(reports) != 1:
        raise ValueError("guarded query did not return one statistics receipt")
    stats = json.loads(reports[0])
    if set(stats) != {"selected", "skipped_forbidden", "skipped_not_allowed"}:
        raise ValueError("unexpected guard statistics schema")
    if any(type(value) is not int or value < 0 for value in stats.values()):
        raise ValueError("invalid guard statistics")
    reader = csv.DictReader(io.StringIO(result.stdout), delimiter="\t")
    if reader.fieldnames != list(COLUMNS):
        raise ValueError("guarded projection header changed")
    allowed = set(pages)
    rows: list[dict[str, Any]] = []
    for row in reader:
        if set(row) != set(COLUMNS) or any(value is None for value in row.values()):
            raise ValueError("malformed admitted group")
        if row["page"] not in allowed or row["page"].startswith("f84"):
            raise ValueError("guard returned a selector outside the admission")
        if row["edition"] not in EDITIONS:
            raise ValueError("unexpected transcription edition")
        if not row["source_group_id"] or not row["locus"] or not row["ivtff_group_raw"]:
            raise ValueError("empty group identity or literal")
        for key in ("source_group_index", "source_group_count"):
            row[key] = int(row[key])
        if not 1 <= row["source_group_index"] <= row["source_group_count"]:
            raise ValueError("invalid source group position")
        rows.append(row)
    if len(rows) != stats["selected"]:
        raise ValueError("guard receipt and projected row count disagree")
    return rows, stats


def _connect_readonly(cache: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(cache.resolve().as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_cache(root: Path = ROOT, cache: Path | None = None, rebuild: bool = False) -> sqlite3.Connection:
    """Return a read-only connection, atomically rebuilding stale guarded data.

    Hashing the mixed source is opaque byte hashing; its rows are never decoded
    here. An allowlist change is refused, rather than silently widening scope.
    """
    root = Path(root).resolve()
    cache = Path(cache) if cache is not None else root / DEFAULT_CACHE.relative_to(ROOT)
    inputs, pages = _inputs(root)
    if cache.is_file() and not rebuild:
        conn = None
        try:
            conn = _connect_readonly(cache)
            saved = receipt(conn)
            if saved.get("inputs") == inputs:
                total = conn.execute("SELECT COUNT(*) FROM groups").fetchone()[0]
                if total == saved["guard_stats"]["selected"] and conn.execute("PRAGMA quick_check").fetchone()[0] == "ok":
                    return conn
        except (sqlite3.DatabaseError, ValueError, KeyError, TypeError):
            pass
        if conn is not None:
            conn.close()
    rows, stats = _guarded_rows(root, pages)
    # Refuse a build whose inputs changed between the receipt and query.
    if _inputs(root)[0] != inputs:
        raise ValueError("input changed during guarded cache build")
    cache.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="word_profiles_", suffix=".sqlite", dir=cache.parent)
    os.close(fd)
    temp = Path(temporary)
    conn = None
    try:
        conn = sqlite3.connect(temp)
        definitions = [f'"{name}" {"INTEGER" if name in ("source_group_index", "source_group_count") else "TEXT"} NOT NULL' for name in COLUMNS]
        conn.execute("CREATE TABLE groups (" + ",".join(definitions) + ", PRIMARY KEY (source_group_id), UNIQUE(edition,page,locus,source_group_index))")
        conn.executemany("INSERT INTO groups VALUES (" + ",".join("?" for _ in COLUMNS) + ")", [tuple(row[name] for name in COLUMNS) for row in rows])
        malformed = conn.execute("""SELECT 1 FROM groups GROUP BY edition,page,locus
            HAVING MIN(source_group_index) != 1 OR MAX(source_group_index) != COUNT(*)
            OR MIN(source_group_count) != COUNT(*) OR MAX(source_group_count) != COUNT(*) LIMIT 1""").fetchone()
        if malformed:
            raise ValueError("incomplete or inconsistent admitted source locus")
        conn.execute("CREATE INDEX group_form ON groups(ivtff_group_raw,edition)")
        conn.execute("CREATE TABLE vocabulary AS SELECT edition,ivtff_group_raw AS form,COUNT(*) AS n FROM groups GROUP BY edition,ivtff_group_raw")
        conn.execute("CREATE UNIQUE INDEX vocabulary_form ON vocabulary(edition,form)")
        conn.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        saved = {"inputs": inputs, "guard_stats": stats, "cache_role": "disposable descriptive cache; no semantic conclusions"}
        conn.execute("INSERT INTO metadata VALUES ('receipt',?)", (json.dumps(saved, sort_keys=True),))
        conn.commit()
        conn.close()
        conn = None
        os.replace(temp, cache)
    finally:
        if conn is not None:
            conn.close()
        temp.unlink(missing_ok=True)
    return _connect_readonly(cache)


def receipt(conn: sqlite3.Connection) -> dict[str, Any]:
    """Portable provenance without machine paths or clock-based freshness."""
    row = conn.execute("SELECT value FROM metadata WHERE key='receipt'").fetchone()
    if row is None:
        raise ValueError("missing cache receipt")
    return json.loads(row[0])


def occurrences(conn: sqlite3.Connection, form: str, edition: str | None = None) -> list[dict[str, Any]]:
    """All exact occurrences; literal neighbours never cross source loci."""
    if not isinstance(form, str) or not form or any(not 33 <= ord(char) <= 126 for char in form):
        raise ValueError("form must be a nonempty printable ASCII literal without whitespace")
    if edition is not None and edition not in EDITIONS:
        raise ValueError("unknown transcription edition")
    query = """SELECT g.*, p.ivtff_group_raw AS previous_literal,
        n.ivtff_group_raw AS next_literal FROM groups AS g
        LEFT JOIN groups AS p ON p.edition=g.edition AND p.page=g.page AND p.locus=g.locus AND p.source_group_index=g.source_group_index-1
        LEFT JOIN groups AS n ON n.edition=g.edition AND n.page=g.page AND n.locus=g.locus AND n.source_group_index=g.source_group_index+1
        WHERE g.ivtff_group_raw=?"""
    parameters = [form]
    if edition is not None:
        query += " AND g.edition=?"
        parameters.append(edition)
    query += " ORDER BY g.edition,g.page,g.locus,g.source_group_index,g.source_group_id"
    rows = [dict(row) for row in conn.execute(query, parameters)]
    counts = Counter((row["edition"], row["page"], row["locus"]) for row in rows)
    for row in rows:
        index, total = row["source_group_index"], row["source_group_count"]
        row["position"] = "single" if total == 1 else "start" if index == 1 else "end" if index == total else "middle"
        row["line_form_count"] = counts[(row["edition"], row["page"], row["locus"])]
        row["previous_same"] = row["previous_literal"] == form
        row["next_same"] = row["next_literal"] == form
    return rows


def _one_edit(left: str, right: str) -> bool:
    """Exactly one raw-character insertion, deletion or substitution."""
    if abs(len(left) - len(right)) > 1 or left == right:
        return False
    if len(left) == len(right):
        return sum(a != b for a, b in zip(left, right)) == 1
    if len(left) > len(right):
        left, right = right, left
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return left[index:] == right[index + 1:]
    return True


def _bounded_counts(counter: Counter, limit: int) -> list[dict[str, Any]]:
    return [{"form": key, "count": value} for key, value in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))[:limit]]


def profile(conn: sqlite3.Connection, form: str, limit: int = 8) -> dict[str, Any]:
    """Counts and contexts per reading; no semantic compatibility score."""
    if type(limit) is not int or limit < 1 or limit > 20:
        raise ValueError("limit must be an integer from 1 to 20")
    all_rows = occurrences(conn, form)
    by_edition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        by_edition[row["edition"]].append(row)
    output: dict[str, Any] = {"form": form, "matching": "exact_raw_group", "editions": {}, "notes": [
        "Readers are alternate readings of one manuscript, not independent confirmations.",
        "Positions are source locus edges, not grammatical sentence boundaries.",
        "Literal neighbours include uncertain spaces; inspect preserved separators.",
        "One-edit neighbours are raw spellings, not established morphemes or variants.",
        "Strata report source metadata without imputing unknown values.",
        "Page counts are admitted selectors, not independent physical leaves.",
        "Rank is one plus the number of strictly more frequent exact types; ties share a rank.",
        "Examples are deterministically bounded; occurrences() returns every case.",
    ]}
    for edition in EDITIONS:
        rows = by_edition[edition]
        count = len(rows)
        total, pages_total = conn.execute("SELECT COUNT(*),COUNT(DISTINCT page) FROM groups WHERE edition=?", (edition,)).fetchone()
        rank = None if not count else 1 + conn.execute("SELECT COUNT(*) FROM vocabulary WHERE edition=? AND n>?", (edition, count)).fetchone()[0]
        strata = {}
        for dimension in STRATA:
            strata[dimension] = [dict(row) for row in conn.execute(f'''SELECT "{dimension}" AS value,
                SUM(CASE WHEN ivtff_group_raw=? THEN 1 ELSE 0 END) AS count,COUNT(*) AS total_groups
                FROM groups WHERE edition=? GROUP BY "{dimension}" ORDER BY "{dimension}"''', (form, edition))]
        line_counts = Counter((row["page"], row["locus"]) for row in rows)
        position_counts = Counter(row["position"] for row in rows)
        neighbors = {}
        for direction in ("previous", "next"):
            neighbors[direction] = _bounded_counts(Counter(row[f"{direction}_literal"] for row in rows if row[f"{direction}_literal"] is not None), limit)
        vocabulary = conn.execute("SELECT form,n FROM vocabulary WHERE edition=? AND ABS(LENGTH(form)-?)<=1 ORDER BY n DESC,form", (edition, len(form)))
        spellings = [{"form": row["form"], "count": row["n"]} for row in vocabulary if _one_edit(form, row["form"])]
        output["editions"][edition] = {
            "count": count, "total_groups": total, "fraction": count / total if total else None,
            "rank": rank, "pages_with_form": len({row["page"] for row in rows}), "pages_total": pages_total,
            "strata": strata, "positions": {key: position_counts[key] for key in ("start", "middle", "end", "single")},
            "repetition": {"lines_with_form": len(line_counts), "repeated_lines": sum(n > 1 for n in line_counts.values()),
                "adjacent_pairs": sum(row["next_same"] for row in rows), "max_per_line": max(line_counts.values(), default=0)},
            "neighbors": neighbors, "spelling_neighbors": spellings[:limit], "spelling_neighbor_types_total": len(spellings),
            "examples": rows[:limit],
        }
    return output
