#!/usr/bin/env python3
"""Independent byte and policy checks for the GDT378 source-only freeze."""
from __future__ import annotations
import csv, hashlib, json, os, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"
ART = BASE / "artifacts"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def bundle(paths: list[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda p: str(p.relative_to(root))):
        digest.update(str(path.relative_to(root)).encode()); digest.update(b"\0")
        digest.update(path.read_bytes()); digest.update(b"\0")
    return digest.hexdigest()

def main() -> None:
    cache_name = os.environ.get("GDT378_SOURCE_CACHE")
    if not cache_name:
        raise SystemExit("set GDT378_SOURCE_CACHE for source-byte validation")
    cache = Path(cache_name)
    freeze_path = ART / "gdt378_source_freeze.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    manifest = rows(ART / "gdt378_comparator_source_manifest.tsv")
    pages = rows(ART / "gdt378_curious_cures_page_manifest.tsv")
    exclusions = rows(ART / "gdt378_source_access_exclusions.tsv")
    pceec = cache / "pceec2"
    parsed = list((pceec / "data/parsed").glob("*.psd"))
    curious = sorted((cache / "curious_add9308").glob("*.html"))
    payload = dict(freeze); expected_content = payload.pop("content_hash")
    checks = {
      "status": freeze["status"] == "COMPARATOR_SOURCES_FROZEN_BEFORE_SCORING",
      "five_included": freeze["included_domains"] == ["COREMA","PCEEC2","CURIOUS_CURES","HARLEIAN_COOKERY","QUINTE_ESSENCE"],
      "two_excluded": freeze["excluded_domains"] == ["REGIOMONTANUS","MEMT"],
      "manifest_rows": len(manifest) == 7,
      "source_statuses": {r["domain"]:r["status"] for r in manifest} == {
        "COREMA":"INCLUDED_GOLD","PCEEC2":"INCLUDED_GOLD","CURIOUS_CURES":"INCLUDED_PROCEDURAL",
        "HARLEIAN_COOKERY":"INCLUDED_SENSITIVITY","QUINTE_ESSENCE":"INCLUDED_PROCEDURAL",
        "REGIOMONTANUS":"EXCLUDED_LICENSE","MEMT":"EXCLUDED_ACCESS"},
      "exclusions_not_replaced": len(exclusions) == 2 and all(r["replacement_used"] == "NO" for r in exclusions),
      "pceec_commit": subprocess.check_output(["git","-C",str(pceec),"rev-parse","HEAD"],text=True).strip() == freeze["inputs"]["pceec2_commit"],
      "pceec_files": len(parsed) == 84,
      "pceec_bundle": bundle(parsed,pceec) == freeze["inputs"]["pceec2_parsed_bundle"],
      "curious_pages": len(pages) == len(curious) == 183,
      "curious_unique": len({r["sequence"] for r in pages}) == 183 and len({r["diplomatic_url"] for r in pages}) == 183,
      "curious_page_hashes": all(sha(cache/"curious_add9308"/f'{int(r["sequence"]):03d}.html') == r["sha256"] for r in pages),
      "curious_bundle": bundle(curious,cache/"curious_add9308") == freeze["inputs"]["curious_ms_add_9308_pages_bundle"],
      "harleian_hash": sha(cache/"harleian_ia_ocr.txt") == freeze["inputs"]["harleian_ia_ocr"],
      "quinte_hash": sha(cache/"quinte_17179.txt") == freeze["inputs"]["quinte_gutenberg"],
      "output_hashes": all(sha(ROOT/path) == value for path,value in freeze["outputs"].items()),
      "implementation_hash": all(sha(ROOT/path) == value for path,value in freeze["implementation"].items()),
      "content_hash": hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest() == expected_content,
      "no_voynich": freeze["voynich_rows_read"] == 0 and not freeze["voynich_scored"],
      "f84_sealed": not any(freeze["f84"].values()),
    }
    out = {"schema":"GDT378_SOURCE_FREEZE_VALIDATION_V1","status":"PASS" if all(checks.values()) else "FAIL",
           "checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),
           "source_freeze_sha256":sha(freeze_path)}
    (ART/"gdt378_source_freeze_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out["status"],f'{out["checks_passed"]}/{out["checks_total"]}')
    if out["status"] != "PASS": raise SystemExit(1)

if __name__ == "__main__":
    main()
