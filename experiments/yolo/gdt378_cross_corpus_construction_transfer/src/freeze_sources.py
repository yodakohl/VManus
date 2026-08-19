#!/usr/bin/env python3
"""Freeze GDT378 public comparator sources without scoring outcomes."""
from __future__ import annotations
import csv, hashlib, json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"
ART = BASE / "artifacts"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def bundle_sha(paths: list[Path], root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(paths, key=lambda p: str(p.relative_to(root))):
        h.update(str(path.relative_to(root)).encode())
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()

def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)

def main() -> None:
    cache_env = os.environ.get("GDT378_SOURCE_CACHE")
    if not cache_env:
        raise SystemExit("set GDT378_SOURCE_CACHE to the downloaded comparator cache")
    cache = Path(cache_env)
    ART.mkdir(parents=True, exist_ok=True)

    pceec = cache / "pceec2"
    parsed = list((pceec / "data/parsed").glob("*.psd"))
    commit = os.popen(f"git -C {pceec!s} rev-parse HEAD").read().strip()
    if not commit or len(commit) != 40:
        raise SystemExit("PCEEC2 commit unavailable")

    collection = cache / "curious_collection.json"
    metadata = cache / "MS-ADD-09308_metadata.json"
    pages_dir = cache / "curious_add9308"
    page_paths = sorted(pages_dir.glob("*.html"))
    page_urls: dict[int, tuple[str, str]] = {}
    with (cache / "curious_add9308_urls.tsv").open(encoding="utf-8") as handle:
        for line in handle:
            seq, label, url = line.rstrip("\n").split("\t")
            page_urls[int(seq)] = (label, url)
    if len(page_paths) != 183 or len(page_urls) != 183:
        raise SystemExit("Curious Cures transcript census mismatch")
    page_rows = []
    for path in page_paths:
        seq = int(path.stem)
        label, url = page_urls[seq]
        page_rows.append({"manuscript_id":"MS-ADD-09308","sequence":seq,"folio_label":label,
                          "diplomatic_url":url,"sha256":sha(path),"bytes":path.stat().st_size})
    page_manifest = ART / "gdt378_curious_cures_page_manifest.tsv"
    write_tsv(page_manifest, page_rows)

    sources = [
      {"domain":"COREMA","source_id":"COREMA_SIX_COLLECTIONS","status":"INCLUDED_GOLD",
       "date":"medieval recipe collections","language":"multiple","format":"TEI plus frozen hidden oracle",
       "url":"repository-bound GDT176/GDT376 sources","version":"GDT376 bound inputs",
       "content_sha256":sha(ROOT/"gdt176_corema_role_oracle.tsv"),"items":"6 collections",
       "oracle":"EDITOR_ROLE_ANNOTATION_PARENT_LINK","publishability":"DERIVED_FEATURES_ALREADY_PUBLIC"},
      {"domain":"PCEEC2","source_id":"PCEEC2_PARSED","status":"INCLUDED_GOLD",
       "date":"1410-1695","language":"English","format":"Penn-style parsed corpus",
       "url":"https://github.com/beatrice57/pceec2","version":commit,
       "content_sha256":bundle_sha(parsed,pceec),"items":f"{len(parsed)} parsed files",
       "oracle":"CONSTITUENT_PARSE_AND_POS","publishability":"DERIVED_FEATURES_ONLY"},
      {"domain":"CURIOUS_CURES","source_id":"CUL_MS_ADD_9308","status":"INCLUDED_PROCEDURAL",
       "date":"1390-1410","language":"Middle English; Latin","format":"HTR-assisted diplomatic TEI/HTML with line coordinates",
       "url":"https://cudl.lib.cam.ac.uk/iiif/MS-ADD-09308","version":"public service snapshot",
       "content_sha256":bundle_sha(page_paths,pages_dir),"items":"183 transcript-bearing pages",
       "oracle":"FROZEN_HIGH_PRECISION_LEXICAL_PROCEDURAL","publishability":"DERIVED_FEATURES_ONLY"},
      {"domain":"HARLEIAN_COOKERY","source_id":"AUSTIN_HARL_279_4016","status":"INCLUDED_SENSITIVITY",
       "date":"c.1430; c.1450","language":"Middle English","format":"OCR derivative of public-domain diplomatic print edition",
       "url":"https://archive.org/download/twofifteenthcent00aust/twofifteenthcent00aust_djvu.txt","version":"Internet Archive derivative",
       "content_sha256":sha(cache/"harleian_ia_ocr.txt"),"items":"2 manuscript books in one edition",
       "oracle":"FROZEN_HIGH_PRECISION_LEXICAL_PROCEDURAL","publishability":"DERIVED_FEATURES_ONLY"},
      {"domain":"QUINTE_ESSENCE","source_id":"GUTENBERG_17179","status":"INCLUDED_PROCEDURAL",
       "date":"MS c.1460-1470; edition 1889","language":"Middle English","format":"public-domain edited plain text",
       "url":"https://www.gutenberg.org/files/17179/17179.txt","version":"Project Gutenberg 17179",
       "content_sha256":sha(cache/"quinte_17179.txt"),"items":"1 work; editorial process sections",
       "oracle":"FROZEN_HIGH_PRECISION_LEXICAL_PROCESS","publishability":"DERIVED_FEATURES_ONLY"},
      {"domain":"REGIOMONTANUS","source_id":"DEFENSIO_THEONIS_DARTMOUTH","status":"EXCLUDED_LICENSE",
       "date":"fifteenth century","language":"Latin","format":"diplomatic and normalized web edition",
       "url":"https://regio.dartmouth.edu/about/about-project.html","version":"not downloaded",
       "content_sha256":"","items":"0","oracle":"POTENTIAL_SCIENTIFIC_FUNCTIONS",
       "publishability":"PROPRIETARY_PERMISSION_REQUIRED"},
      {"domain":"MEMT","source_id":"MIDDLE_ENGLISH_MEDICAL_TEXTS","status":"EXCLUDED_ACCESS",
       "date":"1375-1500","language":"Middle English","format":"commercial corpus",
       "url":"https://varieng.helsinki.fi/CoRD/corpora/CEEM/MEMTindex.html","version":"not downloaded",
       "content_sha256":"","items":"0","oracle":"POTENTIAL_MEDICAL_FUNCTIONS",
       "publishability":"COMMERCIAL_NOT_STRAIGHTFORWARD"},
    ]
    manifest = ART / "gdt378_comparator_source_manifest.tsv"
    write_tsv(manifest, sources)
    exclusions = ART / "gdt378_source_access_exclusions.tsv"
    write_tsv(exclusions, [
      {"domain":"REGIOMONTANUS","reason":"AVAILABLE_EDITION_STATES_PROPRIETARY_AND_PERMISSION_REQUIRED","replacement_used":"NO","blocks_experiment":"NO"},
      {"domain":"MEMT","reason":"MACHINE_READABLE_ACCESS_COMMERCIAL_NOT_STRAIGHTFORWARD","replacement_used":"NO","blocks_experiment":"NO"},
    ])
    inputs = {
      "gdt176_corema_role_oracle.tsv": sha(ROOT/"gdt176_corema_role_oracle.tsv"),
      "pceec2_commit": commit,
      "pceec2_parsed_bundle": bundle_sha(parsed,pceec),
      "curious_collection_manifest": sha(collection),
      "curious_ms_add_9308_metadata": sha(metadata),
      "curious_ms_add_9308_pages_bundle": bundle_sha(page_paths,pages_dir),
      "harleian_ia_ocr": sha(cache/"harleian_ia_ocr.txt"),
      "quinte_gutenberg": sha(cache/"quinte_17179.txt"),
    }
    outputs = {str(p.relative_to(ROOT)):sha(p) for p in [manifest,page_manifest,exclusions]}
    freeze = {"schema":"GDT378_SOURCE_FREEZE_V1","status":"COMPARATOR_SOURCES_FROZEN_BEFORE_SCORING",
              "included_domains":["COREMA","PCEEC2","CURIOUS_CURES","HARLEIAN_COOKERY","QUINTE_ESSENCE"],
              "excluded_domains":["REGIOMONTANUS","MEMT"],"inputs":inputs,"outputs":outputs,
              "voynich_scored":False,"voynich_rows_read":0,
              "f84":{"opened":False,"parsed":False,"retained":False,"scored":False},
              "implementation":{str((BASE/"src/freeze_sources.py").relative_to(ROOT)):sha(BASE/"src/freeze_sources.py")},
              "claim_ceiling":"COMPARATOR_SOURCE_AND_ACCESS_FREEZE_ONLY"}
    payload=dict(freeze)
    freeze["content_hash"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    (ART/"gdt378_source_freeze.json").write_text(json.dumps(freeze,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":freeze["status"],"included":len(freeze["included_domains"]),"curious_pages":len(page_rows)}))

if __name__ == "__main__":
    main()
