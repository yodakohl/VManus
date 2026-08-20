"""Rank likely closed-route and experiment duplicates for a proposed idea."""

from __future__ import annotations

import csv
import math
import re
from collections import Counter
from pathlib import Path

from tools.vmanus_experiment import ROOT


TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "by",
    "do",
    "does",
    "for",
    "from",
    "in",
    "is",
    "it",
    "new",
    "not",
    "of",
    "on",
    "or",
    "the",
    "to",
    "use",
    "with",
}


def tokens(value: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(value.lower()) if token not in STOPWORDS]


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _documents(closed_path: Path, index_path: Path) -> list[dict[str, object]]:
    documents: list[dict[str, object]] = []
    for row in _read_tsv(closed_path):
        weighted = (
            tokens(row["family"]) * 4
            + tokens(row["what_the_archive_establishes"]) * 2
            + tokens(row["reopen_only_if"])
            + tokens(row["status"])
        )
        documents.append(
            {
                "kind": "CLOSED_ROUTE",
                "identifier": row["family"],
                "status": row["status"],
                "summary": row["what_the_archive_establishes"],
                "reopen_only_if": row["reopen_only_if"],
                "report": row["archive_pointer"],
                "terms": Counter(weighted),
            }
        )
    for row in _read_tsv(index_path):
        weighted = (
            tokens(row["experiment_name"]) * 3
            + tokens(row["question"]) * 2
            + tokens(row["status"]) * 2
            + tokens(row["claim_ceiling"])
            + tokens(row["dependencies"])
        )
        documents.append(
            {
                "kind": "EXPERIMENT",
                "identifier": row["experiment_id"],
                "status": row["status"],
                "summary": row["question"] or row["experiment_name"],
                "reopen_only_if": "",
                "report": row["primary_report"],
                "terms": Counter(weighted),
            }
        )
    return documents


def query_routes(
    query: str,
    *,
    closed_path: Path | None = None,
    index_path: Path | None = None,
    limit: int = 10,
) -> list[dict[str, object]]:
    query_terms = Counter(tokens(query))
    if not query_terms:
        raise ValueError("route query must contain a non-stopword term")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    documents = _documents(
        closed_path or ROOT / "experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv",
        index_path or ROOT / "experiments/EXPERIMENT_INDEX.tsv",
    )
    document_frequency = Counter()
    for document in documents:
        document_frequency.update(document["terms"].keys())
    total = len(documents)
    ranked: list[dict[str, object]] = []
    for document in documents:
        score = 0.0
        matched: list[str] = []
        terms: Counter[str] = document["terms"]  # type: ignore[assignment]
        for term, query_count in query_terms.items():
            if term not in terms:
                continue
            inverse_frequency = math.log((total + 1) / (document_frequency[term] + 1)) + 1
            score += query_count * (1 + math.log(terms[term])) * inverse_frequency
            matched.append(term)
        if not matched:
            continue
        ranked.append(
            {
                "kind": document["kind"],
                "identifier": document["identifier"],
                "status": document["status"],
                "score": round(score, 6),
                "matched_terms": ",".join(sorted(matched)),
                "summary": document["summary"],
                "reopen_only_if": document["reopen_only_if"],
                "report": document["report"],
            }
        )
    ranked.sort(key=lambda row: (-float(row["score"]), str(row["kind"]), str(row["identifier"])))
    return ranked[:limit]


def render_tsv(rows: list[dict[str, object]]) -> str:
    columns = (
        "kind",
        "identifier",
        "status",
        "score",
        "matched_terms",
        "summary",
        "reopen_only_if",
        "report",
    )
    output = ["\t".join(columns)]
    for row in rows:
        output.append("\t".join(str(row[column]).replace("\t", " ") for column in columns))
    return "\n".join(output) + "\n"
