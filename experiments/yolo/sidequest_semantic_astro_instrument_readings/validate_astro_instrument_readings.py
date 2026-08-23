#!/usr/bin/env python3
"""Validate the three complete creative Astro instrument readings."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "sidequest_semantic_astro_nomenclator_closure"

SOURCE_LOCI = SOURCE / "ASTRO_142_NOMENCLATOR_CLOSED_LOCI.tsv"
SOURCE_GROUPS = SOURCE / "ASTRO_395_NOMENCLATOR_CLOSED.tsv"
SOURCE_UNIFIED = SOURCE / "TEN_PAGE_776_NOMENCLATOR_CLOSED.tsv"

OUTPUTS = {
    "instruments": HERE / "THREE_ASTRO_INSTRUMENTS.tsv",
    "modules": HERE / "FOURTEEN_INSTRUMENT_MODULES.tsv",
    "loci": HERE / "ASTRO_142_OPERATIONAL_LOCI.tsv",
    "unified": HERE / "TEN_PAGE_776_INSTRUMENT_CONTEXT.tsv",
    "readings": HERE / "THREE_COMPLETE_INSTRUMENT_READINGS.md",
    "manual": HERE / "INSTRUMENT_APPRENTICE_MANUAL.md",
    "summary": HERE / "BUILD_SUMMARY.json",
}
VALIDATION_OUT = HERE / "VALIDATION.json"


EXPECTED_MODULE_LOCI = {
    "M67_RIGHT_SECTORS": 12,
    "M67_RIGHT_RING_RULES": 3,
    "M67_RIGHT_PHASES": 8,
    "M67_LEFT_ASPECT_FIELDS": 37,
    "M67_LEFT_OUTER_STATIONS": 12,
    "M67_LEFT_RING_RULE": 1,
    "M67_SHARED_LEGEND": 1,
    "M68_PANEL_HEADERS": 7,
    "M68_STAR_STATIONS": 28,
    "M68_CENTER_KEY": 2,
    "M69_LEFT_RUBRIC": 1,
    "M69_LEFT_28_SLOTS": 28,
    "M69_MIDDLE_QUALITY": 1,
    "M69_RIGHT_LIGHT": 1,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    source_loci = read_tsv(SOURCE_LOCI)
    source_groups = read_tsv(SOURCE_GROUPS)
    source_unified = read_tsv(SOURCE_UNIFIED)
    instruments = read_tsv(OUTPUTS["instruments"])
    modules = read_tsv(OUTPUTS["modules"])
    loci = read_tsv(OUTPUTS["loci"])
    unified = read_tsv(OUTPUTS["unified"])
    readings = OUTPUTS["readings"].read_text(encoding="utf-8")
    manual = OUTPUTS["manual"].read_text(encoding="utf-8")

    check("source_inventory", (len(source_loci), len(source_groups), len(source_unified)) == (142, 395, 776),
          f"loci={len(source_loci)}, groups={len(source_groups)}, unified={len(source_unified)}")
    check("instrument_inventory", len(instruments) == 3 and {r["page"] for r in instruments} == {"f67r2", "f68r1", "f69v"},
          f"instruments={len(instruments)}, pages={','.join(sorted(r['page'] for r in instruments))}")
    instrument_loci = {r["instrument_id"]: int(r["locus_count"]) for r in instruments}
    instrument_groups = {r["instrument_id"]: int(r["group_count"]) for r in instruments}
    check("instrument_locus_counts", instrument_loci == {
        "I67_TWO_WHEEL_COMPARATOR": 74, "I68_STAR_CLASS_ATLAS": 37, "I69_THREE_WHEEL_REGISTER": 31,
    }, str(instrument_loci))
    check("instrument_group_counts", instrument_groups == {
        "I67_TWO_WHEEL_COMPARATOR": 190, "I68_STAR_CLASS_ATLAS": 65, "I69_THREE_WHEEL_REGISTER": 140,
    }, str(instrument_groups))
    check("instrument_rules", all(r["selection_rule"] == "CHOOSE_VISIBLE_OWNER__NO_START_OR_DIRECTION" and
                                  r["crosspage_rule"] == "NO_REQUIRED_CROSSPAGE_KEY" for r in instruments),
          "all three instruments use visible owners without a cross-page key")

    check("module_inventory", len(modules) == 14 and len({r["module_id"] for r in modules}) == 14,
          f"modules={len(modules)}")
    module_loci = {r["module_id"]: int(r["locus_count"]) for r in modules}
    check("module_locus_counts", module_loci == EXPECTED_MODULE_LOCI, str(module_loci))
    check("module_group_total", sum(int(r["group_count"]) for r in modules) == 395,
          f"groups={sum(int(r['group_count']) for r in modules)}")
    check("module_order_rules", all(r["order_rule"] == "OWNER_SELECTED__NOT_CYCLICALLY_ORDERED" for r in modules),
          "all fourteen modules are owner-selected rather than cyclically ordered")

    check("operational_locus_inventory", len(loci) == 142 and len({(r["page"], r["locus"]) for r in loci}) == 142,
          f"rows={len(loci)}")
    source_keys = [(r["page"], r["locus"], r["local_image_owner"], r["surface_sequence"], r["group_count"]) for r in source_loci]
    new_keys = [(r["page"], r["locus"], r["local_image_owner"], r["surface_sequence"], r["group_count"]) for r in loci]
    check("operational_locus_binding", source_keys == new_keys, "all 142 locus identities, owners, surfaces, and group counts unchanged")
    check("operational_group_total", sum(int(r["group_count"]) for r in loci) == 395,
          f"groups={sum(int(r['group_count']) for r in loci)}")
    check("complete_imperatives", all(r["imperative_reading_de"] and r["compact_default_sequence_de"] in r["imperative_reading_de"] for r in loci),
          "every locus has a concrete imperative containing its full compact sequence")
    check("complete_fluent_readings", all(r["fluent_workshop_reading_de"] for r in loci), "all loci have a fluent module reading")
    check("locus_selection_rule", all(r["selection_rule"] == "SELECT_VISIBLE_OWNER__NO_CYCLIC_ORDER" for r in loci),
          "no locus receives a cyclic order")
    check("locus_orientation_guard", all(r["orientation_status"] == "UNORDERED_LOCAL_ADDRESS__COPY_VISIBLE_POSITION" for r in loci),
          "all 142 source orientation guards retained")
    operator_counts = Counter(r["operator_class"] for r in loci)
    check("operator_inventory", set(operator_counts) == {"ASPECT", "READOUT", "CLASS", "CONDITION", "INDEX", "TRANSFER", "VALUE", "PROCESS", "LOCAL_ENTRY"},
          str(dict(sorted(operator_counts.items()))))

    check("reading_bullet_count", sum(line.startswith("- `f") for line in readings.splitlines()) == 142,
          f"locus_bullets={sum(line.startswith('- `f') for line in readings.splitlines())}")
    check("reading_page_sections", all(title in readings for title in [
        "f67r2 — Doppelrad", "f68r1 — Mehrpaneel-Atlas", "f69v — Dreirad-Register",
    ]), "all three full instrument sections present")
    check("manual_contract", all(term in manual for term in [
        "TO/TE", "AM", "K/KE/KA", "CHEO/CHEY", "CTH", "IIR", "keinen allgemeinen Startpunkt", "kein Schlüssel",
    ]), "manual teaches shared roots, local modules, and no-order rule")

    check("unified_inventory", len(unified) == 776 and Counter(r["register"] for r in unified) ==
          Counter({"PROSE_WORKSHOP": 381, "ASTRO_DIAGRAM": 395}), str(dict(Counter(r["register"] for r in unified))))
    old_prose = [r for r in source_unified if r["register"] == "PROSE_WORKSHOP"]
    new_prose = [{k: v for k, v in r.items() if k not in {"instrument_id", "module_id", "instrument_context_de"}}
                 for r in unified if r["register"] == "PROSE_WORKSHOP"]
    check("prose_unchanged", old_prose == new_prose, "all 381 prose rows unchanged apart from instrument context columns")
    astro_modules = Counter(r["module_id"] for r in unified if r["register"] == "ASTRO_DIAGRAM")
    expected_group_modules = {r["module_id"]: int(r["group_count"]) for r in modules}
    check("unified_module_counts", dict(astro_modules) == expected_group_modules, str(dict(astro_modules)))
    check("complete_unified_context", all(r["instrument_context_de"] for r in unified), "all 776 rows have instrument or prose context")
    fixed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    check("fixed_page_scope", {r["page"] for r in unified} == fixed_pages, ",".join(sorted({r["page"] for r in unified})))

    before = {name: digest(path) for name, path in OUTPUTS.items() if name != "summary"}
    run = subprocess.run([sys.executable, str(HERE / "build_astro_instrument_readings.py")], capture_output=True, text=True)
    after = {name: digest(path) for name, path in OUTPUTS.items() if name != "summary"}
    check("deterministic_rebuild", run.returncode == 0 and before == after, "all instrument artifacts rebuilt byte-identically")

    staged_text = "\n".join(path.read_text(encoding="utf-8") for path in OUTPUTS.values())
    check("sealed_page_scope", "f84\t" not in staged_text and "f84r\t" not in staged_text and "`f84`" not in staged_text,
          "no sealed page selector appears")

    failed = [row for row in checks if not row["passed"]]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "counts": {"instruments": len(instruments), "modules": len(modules), "astro_loci": len(loci),
                   "astro_groups": sum(int(r["group_count"]) for r in loci), "unified_rows": len(unified)},
        "checks": checks,
        "artifact_sha256": {name: digest(path) for name, path in OUTPUTS.items()},
    }
    VALIDATION_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    result = validate()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
