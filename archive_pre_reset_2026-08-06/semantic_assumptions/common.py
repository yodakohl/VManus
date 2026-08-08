#!/usr/bin/env python3
"""Shared parsing and feature code for the semantic-assumption tournament."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ARTIFACTS = BASE / "voynich-manuscript-decoding-artifacts"
TRANSCRIPT = BASE / "transcription" / "sources" / "ZL3b-n.txt"
CACHE = HERE / "cache"
RESULTS = HERE / "results"

sys.path.insert(0, str(ARTIFACTS))
import voynich_fast_state_graph as core  # noqa: E402
import voynich_paradigm_decoder as paradigm  # noqa: E402


PAGE_RE = re.compile(r"^<([^>.]+)>\s+<!(.*)>")
LOCUS_RE = re.compile(r"^<([^,]+),([^>]*)>\s*(?:<!([^>]*)>)?\s*(.*)$")
META_RE = re.compile(r"\$([A-Z])=([^\s>]+)")
LINE_RE = re.compile(r"\.(\d+)$")
FOLIO_RE = re.compile(r"^f(\d+)([rv]?)(.*)$", re.I)


@dataclass
class Row:
    page: str
    section: str
    language: str
    hand: str
    locus: str
    code: str
    words: list[str]
    paragraph_start: bool
    paragraph_end: bool

    @property
    def kind(self) -> str:
        return self.code[1] if len(self.code) > 1 else ""

    @property
    def subtype(self) -> str:
        return self.code[2:] if len(self.code) > 2 else ""

    @property
    def relation(self) -> str:
        return self.code[0] if self.code else ""

    @property
    def line_number(self) -> int:
        match = LINE_RE.search(self.locus)
        return int(match.group(1)) if match else 0


def page_key(page: str) -> tuple[int, int, str]:
    match = FOLIO_RE.match(page)
    if not match:
        return -1, -1, page
    return int(match.group(1)), 0 if match.group(2).lower() == "r" else 1, match.group(3)


def folio_number(page: str) -> int:
    match = FOLIO_RE.match(page)
    return int(match.group(1)) if match else -1


def parse_rows(path: Path = TRANSCRIPT) -> list[Row]:
    rows: list[Row] = []
    page = ""
    meta: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        header = PAGE_RE.match(raw)
        if header:
            page = header.group(1).lower()
            meta = dict(META_RE.findall(header.group(2)))
            continue
        match = LOCUS_RE.match(raw)
        if not match:
            continue
        locus, code, comment, text = match.groups()
        words = core.clean_text(text)
        if not words:
            continue
        rows.append(Row(
            page=page,
            section=meta.get("I", ""),
            language=meta.get("L", ""),
            hand=meta.get("H", ""),
            locus=locus,
            code=code,
            words=words,
            paragraph_start="<%>" in text,
            paragraph_end="<$>" in text,
        ))
    return rows


def _sig_features(unit: str) -> set[str]:
    root, q, initial, stage1, stage2, final = paradigm.strict_parse(unit)
    output = {
        f"ROOT={root}",
        f"ROOT_FINAL={root}|{final}",
        f"ROOT_STAGE2={root}|{stage2}",
        f"SIGNATURE={root}|q{int(q)}|{initial}|{stage1}|{stage2}|{final}",
    }
    if q:
        output.add("FORM_Q=1")
    if initial != "NONE":
        output.add(f"FORM_INITIAL={initial}")
    if stage1 != "NONE":
        output.add(f"FORM_STAGE1={stage1}")
    if stage2 != "NONE":
        output.add(f"FORM_STAGE2={stage2}")
    if final != "NONE":
        output.add(f"FORM_FINAL={final}")
    return output


def _clear_form_slots(
    word: str, *, initials: set[str] | None = None,
    finals: set[str] | None = None,
) -> str | None:
    """Remove only boundary operations licensed by the paired-base audit."""
    signatures = [list(paradigm.strict_parse(unit)) for unit in core.segment(word)]
    changed = False
    for signature in signatures:
        if initials and signature[2] in initials:
            signature[2] = "NONE"
            changed = True
        if finals and signature[5] in finals:
            signature[5] = "NONE"
            changed = True
    if not changed:
        return None
    return "".join(
        paradigm.render_sig(tuple(signature)) for signature in signatures
    )


def _boundary_canonicalizations(word: str) -> dict[str, str]:
    """Fixed experimental views that unite a boundary variant with its base."""
    pf = _clear_form_slots(word, initials={"P", "F"}) or word
    kt = word[1:] if len(word) > 1 and word[0] in "kt" else word
    dyt = word[1:] if len(word) > 1 and word[0] in "dyt" else word
    mg = _clear_form_slots(word, finals={"M", "G"}) or word
    combined = pf
    if len(combined) > 1 and combined[0] in "dkty":
        combined = combined[1:]
    combined = _clear_form_slots(combined, finals={"M", "G"}) or combined
    return {
        "CANON_PF": pf,
        "CANON_KT": kt,
        "CANON_DYT": dyt,
        "CANON_MG": mg,
        "CANON_BOUNDARY": combined,
    }


def features_for_word(word: str) -> set[str]:
    """Generate literal, atom, root, and form hypotheses for one token.

    The output is a set: a feature counts at most once per surface token.  This
    makes page counts interpretable as numbers of tokens carrying a candidate.
    """
    output: set[str] = {f"WORD={word}"}
    for length in (2, 3, 4):
        if len(word) >= length:
            output.add(f"PREFIX{length}={word[:length]}")
            output.add(f"SUFFIX{length}={word[-length:]}")
    for length in (2, 3, 4, 5):
        for index in range(len(word) - length + 1):
            output.add(f"CHAR{length}={word[index:index + length]}")
    atoms = core.atomize(word)
    if word:
        output.add(f"FORM_SURFACE_INITIAL={word[0]}")
        output.add(f"FORM_SURFACE_FINAL={word[-1]}")
    if atoms:
        output.add(f"FORM_SURFACE_INITIAL_ATOM={atoms[0]}")
        output.add(f"FORM_SURFACE_FINAL_ATOM={atoms[-1]}")
    for length in (2, 3, 4):
        for index in range(len(atoms) - length + 1):
            output.add(f"ATOM{length}={'~'.join(atoms[index:index + length])}")
    units = core.segment(word)
    output.add(f"FORM_UNIT_COUNT={min(len(units), 4)}")
    output.add(f"FORM_LENGTH_BIN={min(len(atoms), 12)}")
    for unit in units:
        output.update(_sig_features(unit))
    if word.startswith("q"):
        output.add("FORM_SURFACE_Q_INITIAL=1")
    canonical = _boundary_canonicalizations(word)
    for family, normalized in canonical.items():
        output.add(f"{family}_WORD={normalized}")
    normalized = canonical["CANON_BOUNDARY"]
    for length in (2, 3, 4):
        if len(normalized) >= length:
            output.add(f"CANON_BOUNDARY_PREFIX{length}={normalized[:length]}")
            output.add(f"CANON_BOUNDARY_SUFFIX{length}={normalized[-length:]}")
        for index in range(len(normalized) - length + 1):
            output.add(
                f"CANON_BOUNDARY_CHAR{length}={normalized[index:index + length]}"
            )
    return output


def feature_track(feature: str) -> str:
    if feature.startswith("FORM_") or feature.startswith("SIGNATURE="):
        return "FORM"
    return "LEXICAL"


def save_csr(prefix: Path, rows: Iterable[Iterable[int]]) -> tuple[int, int]:
    indptr = [0]
    indices: list[int] = []
    row_count = 0
    for row in rows:
        indices.extend(sorted(row))
        indptr.append(len(indices))
        row_count += 1
    np.save(prefix.with_name(prefix.name + "_indptr.npy"), np.asarray(indptr, dtype=np.int64))
    np.save(prefix.with_name(prefix.name + "_indices.npy"), np.asarray(indices, dtype=np.int32))
    return row_count, len(indices)


def load_csr(prefix: Path, mmap: bool = True) -> tuple[np.ndarray, np.ndarray]:
    mode = "r" if mmap else None
    return (
        np.load(prefix.with_name(prefix.name + "_indptr.npy"), mmap_mode=mode),
        np.load(prefix.with_name(prefix.name + "_indices.npy"), mmap_mode=mode),
    )


def csr_feature_counts(
    indptr: np.ndarray,
    indices: np.ndarray,
    selected_rows: np.ndarray | list[int],
    feature_count: int,
) -> np.ndarray:
    selected = np.asarray(selected_rows, dtype=np.int64)
    if not len(selected):
        return np.zeros(feature_count, dtype=np.int64)
    parts = [indices[indptr[row]:indptr[row + 1]] for row in selected]
    if not parts:
        return np.zeros(feature_count, dtype=np.int64)
    return np.bincount(np.concatenate(parts), minlength=feature_count)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
