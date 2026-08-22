#!/usr/bin/env python3
"""Validate the V69 R2 final dual edition and all bound canonical layers."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
QUERY = ROOT / "vmanus-exp"
UNITS = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"]
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
CARDS = {"MASS?", "ANWENDEN?", "BEREIT?", "ANSATZ?", "ZIEL?", "KLAR?", "VORIGES?", "ANTEIL?", "TEMPERIEREN?", "SPÜLEN?", "ABLASSEN?"}
FORMALS = {"STANDARDSLOT_SETZEN", "LOKALEN_RELATIONSSLOT_SETZEN", "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN", "VORGABEPARAMETER?"}
TAG_RE = re.compile(r"\[(CARD|FORMAL|REGISTER|IMAGE|IMAGE_RIVAL|GENRE|EXEMPLAR|LOCAL_EXEMPLAR|UNKNOWN):([^\[\]]+)\]")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise AssertionError(f"malformed TSV row in {path.name}")
    return rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def guarded(path: Path, allows: list[str], columns: list[str]) -> list[dict[str, str]]:
    command = [str(QUERY), "query-tsv", str(path), "--selector", "page"]
    for value in allows:
        command.extend(["--allow", value])
    command.extend(["--columns", ",".join(columns), "--forbid-prefix", "f84"])
    result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    material = "\n".join(line for line in result.stdout.splitlines() if not line.startswith("GUARD_STATS "))
    return list(csv.DictReader(io.StringIO(material), delimiter="\t"))


def require(test: bool, message: str) -> None:
    if not test:
        raise AssertionError(message)


def audit_tagged_text(text: str, unit: str, side: str) -> None:
    matches = list(TAG_RE.finditer(text))
    require(matches, f"no semantic tags in {unit} {side}")
    residue = TAG_RE.sub("", text)
    require(not residue.strip(), f"untagged content remains in {unit} {side}: {residue!r}")
    for match in matches:
        tag, value = match.groups()
        normalized = value.rstrip(".")
        if tag == "CARD":
            require(normalized in CARDS, f"unlicensed card tag {value!r} in {unit} {side}")
        if tag == "FORMAL":
            require(normalized in FORMALS, f"unlicensed formal tag {value!r} in {unit} {side}")


def main() -> int:
    fixed = read_tsv(HERE / "V69_R2_FIXED_DICTIONARY_BINDING.tsv")
    manual = read_tsv(HERE / "V69_R2_FINAL_DICTIONARY_SOURCE_ORDER_MANUAL.tsv")
    binding = read_tsv(HERE / "V69_R2_776_BINDING.tsv")
    edition = read_tsv(HERE / "V69_R2_DUAL_FOURTEEN_UNIT_EDITION.tsv")
    contradictions = read_tsv(HERE / "V69_R2_CONTRADICTION_CONFIDENCE.tsv")
    sources = read_tsv(HERE / "V69_R2_HISTORICAL_SOURCES.tsv")
    report = (HERE / "V69_R2_FINAL_HISTORICAL_DUAL_EDITION_REPORT.md").read_text(encoding="utf-8")

    require(len(fixed) == 6, "six canonical artifacts must be byte-bound")
    for row in fixed:
        path = ROOT / row["canonical_selected_path"]
        require(path.is_file(), f"missing canonical artifact {path}")
        require(sha256(path) == row["sha256"], f"SHA-256 mismatch for {path.name}")
        require(row["binding_status"] == "BYTE_BOUND", "canonical binding status mismatch")

    decisions_path = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_EXACT_CARD_DECISIONS.tsv"
    dictionary_path = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_173_CARD_DICTIONARY.tsv"
    event_path = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_381_EVENT_LEDGER.tsv"
    decisions = read_tsv(decisions_path)
    dictionary = read_tsv(dictionary_path)
    require(len(decisions) == 11 and len(dictionary) == 173, "fixed dictionary row counts mismatch")
    manual_cards = {row["entry_id"]: row for row in manual if row["entry_type"] == "EXACT_CARD"}
    require(set(manual_cards) == {row["card"] for row in decisions}, "manual exact-card set mismatch")
    for row in decisions:
        manual_row = manual_cards[row["card"]]
        require(manual_row["exact_identity_or_scope"] == row["joint_tuple_id"], f"identity mismatch {row['card']}")
        require(manual_row["fixed_value_or_order"] == row["selected_short_mnemonic"], f"mnemonic mismatch {row['card']}")
        require(int(manual_row["occurrences"]) == int(row["occurrences"]), f"occurrence mismatch {row['card']}")
    require({row["fixed_value_or_order"] for row in manual if row["entry_type"] == "FORMAL_PROMPT"} == FORMALS, "formal prompt set mismatch")
    require({row["entry_id"] for row in manual if row["entry_type"] == "REGISTER"} == {"OWNER", "ACTIVE", "TARGET", "PREVIOUS"}, "register set mismatch")
    require({row["entry_id"] for row in manual if row["entry_type"] == "TEMPLATE"} == {"HERBAL_SOURCE_ORDER", "BIO_SOURCE_ORDER", "ASTRO_SOURCE_ORDER"}, "source template set mismatch")

    event_rows = guarded(event_path, ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"], ["page", "event_serial", "record_unit_id", "joint_tuple_id"])
    herbal_path = ROOT / "experiments/yolo/sidequest_theory_candidates_v64/V64_R2_100_EVENT_HERBAL_INTERLINEAR.tsv"
    bio_path = ROOT / "experiments/yolo/sidequest_theory_candidates_v65/V65_R2_281_EVENT_BIO_INTERLINEAR.tsv"
    astro_path = ROOT / "experiments/yolo/sidequest_theory_candidates_v66/V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv"
    herbal = guarded(herbal_path, ["f10r", "f11r", "f55v", "f56r"], ["page", "record_unit_id", "event_serial", "field_id", "statement_id"])
    bio = guarded(bio_path, ["f81v", "f82r", "f83r"], ["page", "record_unit_id", "event_serial", "field_id", "statement_id"])
    astro = guarded(astro_path, ["f67r2", "f68r1", "f69v"], ["page", "group_serial", "locus"])
    require((len(event_rows), len(herbal), len(bio), len(astro)) == (381, 100, 281, 395), "canonical coverage counts mismatch")
    require({int(row["event_serial"]) for row in event_rows} == set(range(1, 382)), "V60 event serial coverage mismatch")
    require(len({row["joint_tuple_id"] for row in event_rows}) == 173, "V60 event ledger must bind 173 exact cards")

    require([row["unit_id"] for row in binding] == UNITS, "binding must contain ordered 14 units")
    require([row["unit_id"] for row in edition] == UNITS, "edition must contain ordered 14 units")
    require([row["unit_id"] for row in contradictions] == UNITS, "contradiction table must contain ordered 14 units")
    require({row["page"] for row in binding} == PAGES, "fixed page scope mismatch")
    require(all(row["content_parity"].startswith("PRIMARY_AND_RIVAL_SAME_VISIBLE_") for row in binding), "binding parity flag missing")
    require(all("PARITY" in row["content_parity_status"] for row in edition), "edition parity flag missing")

    expected = {
        "H1": (1, 14, 14), "H2": (15, 38, 24), "H3": (39, 55, 17), "H4": (56, 73, 18), "H5": (74, 100, 27),
        "B1": (101, 166, 66), "B2": (167, 228, 62), "B3": (229, 314, 86), "B4": (315, 361, 47), "B5": (362, 372, 11), "B6": (373, 381, 9),
        "A1": (1, 190, 190), "A2": (191, 255, 65), "A3": (256, 395, 140),
    }
    observed: dict[str, tuple[int, int, int]] = {}
    for unit in UNITS[:11]:
        rows = [row for row in herbal + bio if row["record_unit_id"] == unit]
        serials = [int(row["event_serial"]) for row in rows]
        observed[unit] = (min(serials), max(serials), len(serials))
    for unit, page in (("A1", "f67r2"), ("A2", "f68r1"), ("A3", "f69v")):
        rows = [row for row in astro if row["page"] == page]
        serials = [int(row["group_serial"]) for row in rows]
        observed[unit] = (min(serials), max(serials), len(serials))
    require(observed == expected, "canonical unit intervals mismatch")
    for row in binding:
        actual = (int(row["serial_start"]), int(row["serial_end"]), int(row["visible_group_count"]))
        require(actual == expected[row["unit_id"]], f"binding interval mismatch {row['unit_id']}")
        require(sha256(ROOT / row["canonical_ledger"]) == row["canonical_sha256"], f"ledger SHA mismatch {row['unit_id']}")
    require(sum(int(row["visible_group_count"]) for row in binding) == 776, "binding total must be 776")
    require(sum(int(row["field_or_locus_count"]) for row in binding) == 277, "20 Herbal fields + 115 Bio fields + 142 Astro loci required")
    require(sum(int(row["statement_count"]) for row in binding if row["statement_count"] != "NA") == 116, "source statements must total 116")
    require(len({(row["page"], row["locus"]) for row in astro}) == 142, "Astro loci must total 142")

    for row in edition:
        require(int(row["visible_group_count"]) == expected[row["unit_id"]][2], f"edition count mismatch {row['unit_id']}")
        audit_tagged_text(row["primary_iatromedical_text_tagged"], row["unit_id"], "medical")
        audit_tagged_text(row["equally_visible_practical_text_tagged"], row["unit_id"], "practical")
        confidence = float(row["content_confidence"])
        require(0.0 <= confidence <= 0.40, f"content confidence ceiling exceeded {row['unit_id']}")
    require(all(float(row["formal_binding_confidence"]) == 1.0 for row in contradictions), "formal binding confidence must be 1.00")
    require(all(0.0 <= float(row["medical_content_confidence"]) <= 0.40 and 0.0 <= float(row["practical_content_confidence"]) <= 0.40 for row in contradictions), "content confidence range failure")

    require(len(sources) >= 10 and all(row["reference_url"].startswith("https://") for row in sources), "historical source gate failed")
    normalized = " ".join(report.split()).lower()
    for phrase in ("inhaltsparität", "bestätigte lexeme", "776/776", "0/776", "sichtbaren schlüssel", "keine entzifferung", "folgt kein v70"):
        require(phrase in normalized, f"report missing required statement: {phrase}")

    result = {
        "status": "PASS",
        "decision": "CONTENT_PARITY_DUAL_EDITION",
        "units": 14,
        "fixed_dictionary": {"exact_cards": len(dictionary), "selected_mnemonics": len(decisions), "event_ledger": len(event_rows), "byte_bound_artifacts": len(fixed)},
        "coverage": {"Herbal_records": 5, "Herbal_events": len(herbal), "Herbal_fields": len({row['field_id'] for row in herbal}), "Bio_records": 6, "Bio_events": len(bio), "Bio_fields": len({row['field_id'] for row in bio}), "Prose_statements": 116, "Astro_diagrams": 3, "Astro_groups": len(astro), "Astro_loci": len({(row['page'], row['locus']) for row in astro}), "total_visible_groups": len(herbal) + len(bio) + len(astro)},
        "semantic_ceiling": {"confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "identified_language": False, "phonetic_mapping": False, "new_card_meanings": False, "content_without_master_exemplar": "0/776", "f68_f69_visible_key": False, "sealed_f84_used": False},
        "historical_sources": len(sources),
        "next_pass": None,
    }
    (HERE / "V69_R2_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ValueError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
