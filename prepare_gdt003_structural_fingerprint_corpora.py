#!/usr/bin/env python3
"""Freeze matched surface-form corpora for the GDT003 fingerprint comparator.

This is an acquisition/preparation program, not a language-identification
model.  It records only document routing and normalized surface forms.  It
never reads lemmas, tags, translations, glosses, or phonological fields.
"""

from __future__ import annotations

import bz2
import csv
import gzip
import hashlib
import io
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import urllib.error
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "experiments/semantic_assumptions/results"
OUT_CORPORA = ROOT / "gdt003_structural_fingerprint_corpora.json.gz"
OUT_MANIFEST = ROOT / "gdt003_structural_fingerprint_corpus_manifest.tsv"
OUT_PROVENANCE = ROOT / "gdt003_structural_fingerprint_source_provenance.json"

UD_TAG = "r2.18"
TOKENS_PER_FOLD = 1000
FOLDS = 12
MATCHED_TOKENS = TOKENS_PER_FOLD * FOLDS
MIN_LENGTH = 2
MAX_LENGTH = 30
WIKI_TARGET_RAW_TOKENS = 18000
WIKI_MAX_BATCHES = 80
USER_AGENT = "VManus-GDT003-structural-fingerprint/1.0 (github.com/yodakohl/VManus)"


@dataclass(frozen=True)
class WikiSpec:
    corpus_id: str
    language: str
    family: str
    wiki: str
    script: str
    requested_scope: str
    historical_status: str


@dataclass(frozen=True)
class UDSpec:
    corpus_id: str
    language: str
    family: str
    repo: str
    prefix: str
    requested_scope: str
    historical_status: str


WIKI_SPECS = (
    WikiSpec("KAZAKH_KIPCHAK_SENSITIVITY", "Kazakh", "Turkic_Kipchak", "kk", "CYRILLIC", "Cuman_Kipchak", "MODERN_PROXY_NOT_CUMAN"),
    WikiSpec("ADYGHE_MODERN_SENSITIVITY", "Adyghe", "Northwest_Caucasian", "ady", "CYRILLIC", "Adyghe_Circassian", "MODERN_ONLY"),
    WikiSpec("ABKHAZ_MODERN_SENSITIVITY", "Abkhaz", "Northwest_Caucasian", "ab", "CYRILLIC", "Abkhaz", "MODERN_ONLY"),
    WikiSpec("AVAR_MODERN_SENSITIVITY", "Avar", "Northeast_Caucasian", "av", "CYRILLIC", "Avar_Lezgian", "MODERN_ONLY"),
    WikiSpec("LEZGIAN_MODERN_SENSITIVITY", "Lezgian", "Northeast_Caucasian", "lez", "CYRILLIC", "Avar_Lezgian", "MODERN_ONLY"),
    WikiSpec("ARMENIAN_MODERN_SENSITIVITY", "Armenian", "Armenian", "hy", "ARMENIAN", "Middle_Armenian", "MODERN_SENSITIVITY"),
    WikiSpec("GEORGIAN_MODERN_SENSITIVITY", "Georgian", "Kartvelian", "ka", "GEORGIAN", "historical_Georgian", "MODERN_SENSITIVITY"),
    WikiSpec("MALTESE_MODERN_SENSITIVITY", "Maltese", "Semitic", "mt", "LATIN", "Early_Maltese_Siculo_Arabic", "MODERN_PROXY_NOT_EARLY_MALTESE"),
    WikiSpec("HUNGARIAN_MODERN", "Hungarian", "Uralic", "hu", "LATIN", "Hungarian", "MODERN_ONLY"),
    WikiSpec("BASQUE_MODERN", "Basque", "Basque", "eu", "LATIN", "Basque", "MODERN_ONLY"),
    WikiSpec("LATIN_WIKI_CONTROL", "Latin", "Italic", "la", "LATIN", "Latin_control", "MODERN_COMPOSITION_IN_HISTORICAL_LANGUAGE"),
    WikiSpec("ITALIAN_WIKI_CONTROL", "Italian", "Romance", "it", "LATIN", "Italian_control", "MODERN_CONTROL"),
    WikiSpec("GERMAN_WIKI_CONTROL", "German", "Germanic", "de", "LATIN", "German_control", "MODERN_CONTROL"),
    WikiSpec("GREEK_WIKI_CONTROL", "Greek", "Greek", "el", "GREEK", "Greek_control", "MODERN_CONTROL"),
    WikiSpec("ARABIC_WIKI_CONTROL", "Arabic", "Semitic", "ar", "ARABIC", "Arabic_control", "MODERN_STANDARD_CONTROL"),
)

UD_SPECS = (
    UDSpec("MIDDLE_ARMENIAN_UD", "Middle Armenian", "Armenian", "UD_Middle_Armenian-ArmTDP", "axm_armtdp", "Middle_Armenian", "HISTORICAL_EXACT_LOW_CAPACITY"),
    UDSpec("OLD_GEORGIAN_UD", "Old Georgian", "Kartvelian", "UD_Old_Georgian-GLC", "oge_glc", "historical_Georgian", "HISTORICAL_EXACT"),
    UDSpec("OLD_CHURCH_SLAVONIC_UD", "Old Church Slavonic", "Slavic", "UD_Old_Church_Slavonic-PROIEL", "cu_proiel", "Old_Church_Slavonic", "HISTORICAL_EXACT"),
    UDSpec("LATIN_PROIEL_CONTROL", "Latin", "Italic", "UD_Latin-PROIEL", "la_proiel", "Latin_control", "HISTORICAL_CONTROL"),
    UDSpec("OLD_ITALIAN_UD_CONTROL", "Old Italian", "Romance", "UD_Italian-Old", "it_old", "Italian_control", "HISTORICAL_CONTROL"),
    UDSpec("ANCIENT_GREEK_PROIEL_CONTROL", "Ancient Greek", "Greek", "UD_Ancient_Greek-PROIEL", "grc_proiel", "Greek_control", "HISTORICAL_CONTROL"),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(data)


def fetch(url: str, params: dict[str, object] | None = None, tries: int = 8) -> tuple[bytes, str]:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    error: Exception | None = None
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read(), response.geturl()
        except urllib.error.HTTPError as exc:  # pragma: no cover - network retry path
            error = exc
            retry_after = int(exc.headers.get("Retry-After", "0") or 0)
            time.sleep(max(retry_after, min(30, 2 ** attempt)))
        except Exception as exc:  # pragma: no cover - network retry path
            error = exc
            time.sleep(min(30, 2 ** attempt))
    raise RuntimeError(f"failed to fetch {url}: {error}")


def script_ok(token: str, script: str) -> bool:
    saw_letter = False
    for char in token:
        category = unicodedata.category(char)
        if category.startswith("L"):
            saw_letter = True
            name = unicodedata.name(char, "")
            if script not in name:
                return False
        elif category.startswith("M"):
            continue
        else:
            return False
    return saw_letter


def letter_tokens(text: str, script: str) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    for char in unicodedata.normalize("NFC", text).casefold():
        category = unicodedata.category(char)
        if category.startswith("L") or (category.startswith("M") and current):
            current.append(char)
        else:
            if current:
                chunks.append("".join(current))
                current = []
    if current:
        chunks.append("".join(current))
    return [value for value in chunks if MIN_LENGTH <= len(value) <= MAX_LENGTH and script_ok(value, script)]


def balance_units(unit_tokens: dict[str, list[str]], corpus_id: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Assign whole units greedily, then hash-sample 1,000 tokens per fold."""
    usable = {unit: values for unit, values in unit_tokens.items() if values}
    if len(usable) < FOLDS:
        return [], {"capacity_state": "INSUFFICIENT_UNITS", "units": len(usable), "eligible_tokens": sum(map(len, usable.values()))}
    fold_units: list[list[str]] = [[] for _ in range(FOLDS)]
    fold_sizes = [0] * FOLDS
    for unit, values in sorted(usable.items(), key=lambda item: (-len(item[1]), hashlib.sha256(f"{corpus_id}|{item[0]}".encode()).hexdigest())):
        fold = min(range(FOLDS), key=lambda index: (fold_sizes[index], index))
        fold_units[fold].append(unit)
        fold_sizes[fold] += len(values)
    if min(fold_sizes) < TOKENS_PER_FOLD:
        return [], {
            "capacity_state": "INSUFFICIENT_TOKENS_PER_FOLD",
            "units": len(usable),
            "eligible_tokens": sum(map(len, usable.values())),
            "fold_sizes_before_sampling": fold_sizes,
        }
    rows: list[dict[str, object]] = []
    for fold, units in enumerate(fold_units, 1):
        occurrences: list[tuple[str, int, str]] = []
        for unit in units:
            occurrences.extend((unit, index, value) for index, value in enumerate(unit_tokens[unit]))
        occurrences.sort(key=lambda row: hashlib.sha256(f"{corpus_id}|{row[0]}|{row[1]}|{row[2]}".encode()).digest())
        for rank, (unit, index, form) in enumerate(occurrences[:TOKENS_PER_FOLD], 1):
            rows.append({"corpus_id": corpus_id, "fold_id": f"F{fold:02d}", "unit_id": unit, "occurrence_index": index, "form": form, "sample_rank": rank})
    return rows, {
        "capacity_state": "MATCHED_12000",
        "units": len(usable),
        "eligible_tokens": sum(map(len, usable.values())),
        "fold_sizes_before_sampling": fold_sizes,
    }


def retain_low_capacity(unit_tokens: dict[str, list[str]], corpus_id: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Retain an exact small corpus without pretending it is 12k matched."""
    usable = {unit: values for unit, values in unit_tokens.items() if values}
    low_folds = min(6, len(usable))
    if low_folds < 3:
        return [], {"capacity_state": "INSUFFICIENT_UNITS", "units": len(usable), "eligible_tokens": sum(map(len, usable.values()))}
    fold_units: list[list[str]] = [[] for _ in range(low_folds)]
    fold_sizes = [0] * low_folds
    for unit, values in sorted(usable.items(), key=lambda item: (-len(item[1]), hashlib.sha256(f"{corpus_id}|{item[0]}".encode()).hexdigest())):
        fold = min(range(low_folds), key=lambda index: (fold_sizes[index], index))
        fold_units[fold].append(unit)
        fold_sizes[fold] += len(values)
    rows: list[dict[str, object]] = []
    for fold, units in enumerate(fold_units, 1):
        rank = 0
        for unit in sorted(units):
            for index, form in enumerate(unit_tokens[unit]):
                rank += 1
                rows.append({"corpus_id": corpus_id, "fold_id": f"F{fold:02d}", "unit_id": unit, "occurrence_index": index, "form": form, "sample_rank": rank})
    return rows, {
        "capacity_state": "LOW_CAPACITY_UNMATCHED_ALL",
        "units": len(usable), "eligible_tokens": sum(map(len, usable.values())),
        "fold_sizes_before_sampling": fold_sizes, "actual_folds": low_folds,
    }


def acquire_wikipedia(spec: WikiSpec) -> tuple[list[dict[str, object]], dict[str, object]]:
    endpoint = f"https://{spec.wiki}.wikipedia.org/w/api.php"
    pages: dict[str, dict[str, object]] = {}
    response_hashes: list[str] = []
    for batch in range(WIKI_MAX_BATCHES):
        payload, resolved = fetch(
            endpoint,
            {
                "action": "query", "format": "json", "formatversion": 2,
                "generator": "random", "grnnamespace": 0, "grnlimit": 20,
                "prop": "extracts|revisions", "explaintext": 1, "exintro": 1, "exsectionformat": "plain",
                "rvprop": "ids|timestamp", "redirects": 1,
            },
        )
        response_hashes.append(sha256_bytes(payload))
        time.sleep(0.6)
        data = json.loads(payload)
        for page in data.get("query", {}).get("pages", []):
            if "missing" in page:
                continue
            tokens = letter_tokens(page.get("extract", ""), spec.script)
            if not tokens:
                continue
            pageid = str(page["pageid"])
            revision = (page.get("revisions") or [{}])[0]
            pages[pageid] = {
                "title": page.get("title", ""), "tokens": tokens,
                "revision_id": revision.get("revid"), "revision_timestamp": revision.get("timestamp"),
            }
        if sum(len(page["tokens"]) for page in pages.values()) >= WIKI_TARGET_RAW_TOKENS and len(pages) >= FOLDS * 2:
            break
    units = {pageid: page["tokens"] for pageid, page in pages.items()}
    rows, capacity = balance_units(units, spec.corpus_id)
    provenance = {
        "corpus_id": spec.corpus_id,
        "source_type": "WIKIMEDIA_RANDOM_MAIN_NAMESPACE_PLAINTEXT_EXTRACTS",
        "endpoint": endpoint,
        "access_date": "2026-08-14",
        "request_batches": len(response_hashes),
        "response_sha256": response_hashes,
        "page_count": len(pages),
        "page_manifest": [
            {"pageid": pageid, "title": page["title"], "revision_id": page["revision_id"], "revision_timestamp": page["revision_timestamp"], "eligible_tokens": len(page["tokens"])}
            for pageid, page in sorted(pages.items(), key=lambda item: int(item[0]))
        ],
        **capacity,
    }
    return rows, provenance


def ud_file_urls(spec: UDSpec) -> list[str]:
    base = f"https://raw.githubusercontent.com/UniversalDependencies/{spec.repo}/{UD_TAG}"
    urls = []
    for split in ("train", "dev", "test"):
        url = f"{base}/{spec.prefix}-ud-{split}.conllu"
        try:
            payload, resolved = fetch(url, tries=1)
        except RuntimeError:
            continue
        if payload:
            urls.append(resolved)
    if not urls:
        url = f"{base}/{spec.prefix}-ud-test.conllu"
        payload, resolved = fetch(url)
        if payload:
            urls.append(resolved)
    return urls


def infer_script(spec: UDSpec) -> str:
    if "Armenian" in spec.language:
        return "ARMENIAN"
    if "Georgian" in spec.language:
        return "GEORGIAN"
    if "Slavonic" in spec.language:
        return "CYRILLIC"
    if "Greek" in spec.language:
        return "GREEK"
    return "LATIN"


def acquire_ud(spec: UDSpec) -> tuple[list[dict[str, object]], dict[str, object]]:
    script = infer_script(spec)
    units: dict[str, list[str]] = defaultdict(list)
    file_records = []
    sentence_serial = 0
    for url in ud_file_urls(spec):
        payload, resolved = fetch(url)
        file_name = resolved.rsplit("/", 1)[-1]
        current_doc = ""
        current_sent = ""
        sentence_tokens: list[str] = []

        def flush_sentence() -> None:
            nonlocal sentence_serial, sentence_tokens
            if not sentence_tokens:
                return
            sentence_serial += 1
            # Preserve real documents when present; otherwise use contiguous
            # 10-sentence source blocks so that held folds are not token splits.
            unit = f"{file_name}|DOC|{current_doc}" if current_doc else f"{file_name}|BLOCK|{(sentence_serial - 1) // 10:05d}"
            units[unit].extend(sentence_tokens)
            sentence_tokens = []

        for raw in payload.decode("utf-8").splitlines():
            if not raw:
                flush_sentence()
                current_sent = ""
                continue
            if raw.startswith("# newdoc id ="):
                current_doc = raw.split("=", 1)[1].strip()
            elif raw.startswith("# sent_id ="):
                current_sent = raw.split("=", 1)[1].strip()
            elif not raw.startswith("#"):
                cols = raw.split("\t")
                if len(cols) != 10 or not re.fullmatch(r"\d+", cols[0]):
                    continue
                normalized = letter_tokens(cols[1], script)
                if len(normalized) == 1:
                    sentence_tokens.append(normalized[0])
        flush_sentence()
        file_records.append({"url": resolved, "sha256": sha256_bytes(payload), "bytes": len(payload)})
    # Real newdoc units remain indivisible. A historical source with fewer
    # than three documents is capacity-insufficient rather than token-split.
    rows, capacity = balance_units(dict(units), spec.corpus_id)
    if not rows:
        rows, capacity = retain_low_capacity(dict(units), spec.corpus_id)
    provenance = {
        "corpus_id": spec.corpus_id,
        "source_type": "UNIVERSAL_DEPENDENCIES_CONLLU_FORM_COLUMN_ONLY",
        "release_tag": UD_TAG,
        "repository": f"https://github.com/UniversalDependencies/{spec.repo}",
        "files": file_records,
        "access_date": "2026-08-14",
        **capacity,
    }
    return rows, provenance


def load_voynich() -> tuple[list[dict[str, object]], dict[str, object]]:
    separator_path = RESULTS / "source_separator_transcription.tsv"
    alignment_path = RESULTS / "source_sta_group_alignment.tsv"
    metadata: dict[str, dict[str, str]] = {}
    with separator_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"].startswith("f84r"):
                continue
            metadata[row["source_group_id"]] = row
    grouped: dict[str, dict[str, str]] = defaultdict(dict)
    with alignment_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"].startswith("f84r") or row["source_group_id"] not in metadata:
                continue
            key = f"{row['locus']}|G{int(row['source_group_index']):03d}"
            grouped[key][row["edition"]] = row["nearest_basic_eva_primary"].lower()
    units: dict[str, list[str]] = defaultdict(list)
    rejected = 0
    for key, readings in grouped.items():
        if set(readings) == {"ZL3b", "IT2a", "RF1b"} and len(set(readings.values())) == 1 and re.fullmatch(r"[a-z?]+", next(iter(readings.values()))):
            locus = key.split("|", 1)[0]
            match = re.match(r"(f\d+)", locus)
            folio = match.group(1) if match else locus.split(".", 1)[0]
            units[folio].append(next(iter(readings.values())))
        else:
            rejected += 1
    rows, capacity = balance_units(dict(units), "VOYNICH_MATCHED")
    return rows, {
        "corpus_id": "VOYNICH_MATCHED",
        "source_type": "GDT003_STRICT_THREE_READING_SOURCE_GROUPS",
        "files": [
            {"path": str(separator_path.relative_to(ROOT)), "sha256": sha256_bytes(separator_path.read_bytes())},
            {"path": str(alignment_path.relative_to(ROOT)), "sha256": sha256_bytes(alignment_path.read_bytes())},
        ],
        "alternate_readings_not_replications": True,
        "f84r_retained_or_sampled": False,
        "rejected_ambiguous_keys": rejected,
        **capacity,
    }


def write_gzip_json(path: Path, value: object) -> None:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as handle:
            handle.write(payload)


def main() -> None:
    all_rows: list[dict[str, object]] = []
    provenance: list[dict[str, object]] = []
    metadata: dict[str, dict[str, str]] = {
        "VOYNICH_MATCHED": {"language": "Voynich", "family": "UNKNOWN", "tier": "TARGET", "requested_scope": "Voynich", "historical_status": "MANUSCRIPT_SOURCE"}
    }
    rows, prov = load_voynich()
    all_rows.extend(rows)
    provenance.append(prov)
    reuse_wiki = "--reuse-wiki-freeze" in sys.argv and OUT_CORPORA.exists() and OUT_PROVENANCE.exists()
    old_records: dict[str, list[dict[str, object]]] = defaultdict(list)
    old_prov: dict[str, dict[str, object]] = {}
    if reuse_wiki:
        with gzip.open(OUT_CORPORA, "rt", encoding="utf-8") as handle:
            for row in json.load(handle)["records"]:
                old_records[str(row["corpus_id"])].append(row)
        old_prov = {str(row["corpus_id"]): row for row in json.loads(OUT_PROVENANCE.read_text(encoding="utf-8"))["sources"]}
    for spec in WIKI_SPECS:
        if reuse_wiki and spec.corpus_id in old_records:
            print(f"reusing frozen {spec.corpus_id}", file=sys.stderr, flush=True)
            rows, prov = old_records[spec.corpus_id], old_prov[spec.corpus_id]
        else:
            print(f"acquiring {spec.corpus_id}", file=sys.stderr, flush=True)
            rows, prov = acquire_wikipedia(spec)
        all_rows.extend(rows)
        provenance.append(prov)
        metadata[spec.corpus_id] = {"language": spec.language, "family": spec.family, "tier": "MODERN_MATCHED_SENSITIVITY", "requested_scope": spec.requested_scope, "historical_status": spec.historical_status}
    for spec in UD_SPECS:
        print(f"acquiring {spec.corpus_id}", file=sys.stderr, flush=True)
        rows, prov = acquire_ud(spec)
        all_rows.extend(rows)
        provenance.append(prov)
        metadata[spec.corpus_id] = {"language": spec.language, "family": spec.family, "tier": "HISTORICAL_UD", "requested_scope": spec.requested_scope, "historical_status": spec.historical_status}

    corpus_payload = {
        "schema": "GDT003_STRUCTURAL_FINGERPRINT_CORPORA_V1",
        "freeze_date": "2026-08-14",
        "normalization": "NFC_CASEFOLD_CONTIGUOUS_SINGLE_SCRIPT_LETTER_MARK_RUNS_LENGTH_2_TO_30",
        "matched_design": {"folds": FOLDS, "tokens_per_fold": TOKENS_PER_FOLD, "tokens_per_admitted_corpus": MATCHED_TOKENS},
        "records": sorted(all_rows, key=lambda row: (str(row["corpus_id"]), str(row["fold_id"]), int(row["sample_rank"]), str(row["unit_id"]))),
    }
    write_gzip_json(OUT_CORPORA, corpus_payload)
    counts = Counter(str(row["corpus_id"]) for row in all_rows)
    prov_by_id = {str(row["corpus_id"]): row for row in provenance}
    manifest_rows = []
    for corpus_id, meta in sorted(metadata.items()):
        prov = prov_by_id[corpus_id]
        manifest_rows.append({
            "corpus_id": corpus_id,
            **meta,
            "capacity_state": prov["capacity_state"],
            "sampled_tokens": counts[corpus_id],
            "source_units": prov["units"],
            "eligible_source_tokens": prov["eligible_tokens"],
            "folds": len({str(row["fold_id"]) for row in all_rows if str(row["corpus_id"]) == corpus_id}),
            "surface_only": 1,
            "phoneme_mapping": 0,
            "translation_or_lemma_used": 0,
        })
    with OUT_MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest_rows)
    prov_payload = {
        "schema": "GDT003_STRUCTURAL_FINGERPRINT_SOURCE_PROVENANCE_V1",
        "freeze_date": "2026-08-14",
        "sources": provenance,
        "corpora_sha256": sha256_bytes(OUT_CORPORA.read_bytes()),
        "manifest_sha256": sha256_bytes(OUT_MANIFEST.read_bytes()),
        "selection_note": "Wikipedia pages were a frozen random main-namespace draw made before any transformation scoring. Historical UD data use release r2.18. Exact normalized records are frozen in the committed corpus artifact.",
        "unsupported_exact_varieties": {
            "Cuman": "NO_ADMISSIBLE_MATCHED_HISTORICAL_CORPUS; KAZAKH IS MODERN KIPCHAK SENSITIVITY ONLY",
            "Early_Maltese_or_Siculo_Arabic": "NO_ADMISSIBLE_MATCHED_HISTORICAL_CORPUS; MODERN MALTESE IS SENSITIVITY ONLY",
            "Adyghe_Abkhaz_Avar_Lezgian": "MODERN WIKIPEDIA SURFACE CORPORA ONLY",
        },
    }
    OUT_PROVENANCE.write_text(json.dumps(prov_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(all_rows), "counts": counts, "corpora_sha256": sha256_bytes(OUT_CORPORA.read_bytes())}, default=dict, sort_keys=True))


if __name__ == "__main__":
    main()
