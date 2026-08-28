#!/usr/bin/env python3
"""Independent result and live guarded-query validator for GDT605."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
SAFE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
EXPECTED_SAFE = "7eba46774be44992064cc114f67329723ac7bf589321b0d763fb7f7f748cc1e9"
EXPECTED_GUARDED = "d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9"
EXPECTED = {
    "gdt605_unit_result.json": "c2d293c121f1ee01fe0ddcbe4647c77f5f94796b4ecc4b1adc554cc2f740c3d9",
    "gdt605_unit_inventory.tsv": "ade74733200e941ddc66285988eb1498ac98e87ad374cad11ac412ce42893e82",
    "gdt605_bpe_merges.tsv": "4625c9389ead390907e4ac74e65bc158236f02b439c69cf3b09157f0cd6ca539",
    "gdt605_separator_crossing.json": "87574fb3e2a3d16274ffba5b5c773f1a4821ec73df416b57164b3b729c6eb145",
    "gdt605_boundary_latin.json": "b332a9ccca8f3dfdd5f26e675380caba0061501314b9b5feb5a26a732f1c41f2",
    "gdt605_boundary_old_italian.json": "6542d068376866a63b96c7985ba423dfaa9881c757d64e84c832e6c1eb034ff7",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(name: str):
    return json.loads((OUT / name).read_text())


def live_guarded_hash() -> tuple[str, int, int, int]:
    if sha256(SAFE) != EXPECTED_SAFE:
        raise AssertionError("GDT327 safe allow-list hash")
    page_to_folio = {}
    with SAFE.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page, folio = row["page"], row["physical_folio"]
            if page.lower().startswith("f84") or folio.lower().startswith("f84"):
                raise AssertionError("sealed selector in allow-list")
            page_to_folio[page] = folio
    pages = sorted(page_to_folio)
    folios = sorted(set(page_to_folio.values()))
    ranked = sorted(
        folios,
        key=lambda folio: hashlib.sha256(
            ("gdt604-held-v1|" + folio).encode()
        ).hexdigest(),
    )
    held = set(ranked[:23])
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv",
        "transcription/voynich_zl3b_lines.tsv", "--selector", "page",
    ]
    for page in pages:
        command.extend(("--allow", page))
    command.extend((
        "--forbid-prefix", "f84", "--columns",
        "page,locus,line_number,section,language,hand,eva_clean,ivtff_raw",
    ))
    emitted = subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout
    source_rows = list(csv.DictReader(io.StringIO(emitted), delimiter="\t"))
    fields = [
        "page", "physical_folio", "split", "locus", "line_number",
        "section", "language", "hand", "eva_clean", "ivtff_raw",
    ]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=fields, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    for row in source_rows:
        page = row["page"]
        if page not in page_to_folio or page.lower().startswith("f84"):
            raise AssertionError("guard emitted forbidden selector")
        folio = page_to_folio[page]
        writer.writerow({
            **row,
            "physical_folio": folio,
            "split": "held" if folio in held else "train",
        })
    digest = hashlib.sha256(buffer.getvalue().encode()).hexdigest()
    return digest, len(source_rows), len(pages), len(folios)


def main() -> int:
    checks = []

    def check(name: str, condition: bool) -> None:
        checks.append({"check": name, "passed": bool(condition)})

    for name, expected in EXPECTED.items():
        check(f"hash {name}", sha256(OUT / name) == expected)

    unit = load_json("gdt605_unit_result.json")
    check("unit schema", unit["schema"] == "gdt605-boundary-aware-unit-inventory-v1")
    check("unit decision", unit["decision"] == "STABLE_98_UNIT_BOUNDARY_AWARE_ALPHABET")
    check("unit guarded binding", unit["guarded_rows_sha256"] == EXPECTED_GUARDED)
    check("68/23 split labels", unit["configuration"]["training"] == "68 physical folios" and unit["configuration"]["held"] == "23 physical folios")
    check("98/97 unit types", unit["splits"]["train"]["unit_types"] == 98 and unit["splits"]["held"]["unit_types"] == 97)
    check("zero held OOV", unit["held_unseen_unit_types"] == [])
    check("fourteen unresolved rows", unit["unresolved_rows"] == 14)

    with (OUT / "gdt605_unit_inventory.tsv").open(newline="") as handle:
        inventory = list(csv.DictReader(handle, delimiter="\t"))
    check("98 inventory rows", len(inventory) == 98)
    check("all held units seen in train", all(row["seen_in_train"] == "1" for row in inventory if row["seen_in_held"] == "1"))
    check("inventory train occurrence total", sum(int(row["train_occurrences"]) for row in inventory) == 43_335)
    check("inventory held occurrence total", sum(int(row["held_occurrences"]) for row in inventory) == 21_679)
    with (OUT / "gdt605_bpe_merges.tsv").open(newline="") as handle:
        merges = list(csv.DictReader(handle, delimiter="\t"))
    check("64 ordered merges", len(merges) == 64 and [int(row["rank"]) for row in merges] == list(range(1, 65)))

    separator = load_json("gdt605_separator_crossing.json")
    held = separator["counts"]["held"]
    check("separator guarded binding", separator["guarded_rows_sha256"] == EXPECTED_GUARDED)
    check("separator alignment", separator["aligned_rows"] == 4_151 and separator["unresolved_rows"] == 14)
    check("held uncertain count", held["uncertain"]["crossed"] == 185 and held["uncertain"]["total"] == 749)
    check("held certain count", held["certain"]["crossed"] == 575 and held["certain"]["total"] == 8_570)
    check("held drawing count", held["drawing"]["crossed"] == 5 and held["drawing"]["total"] == 97)
    sign = separator["held_summary"]["folio_sign"]
    check("22/23 held-folio sign", sign == {"comparable": 23, "uncertain_above_certain": 22, "uncertain_equal_certain": 0, "uncertain_below_certain": 1})
    check("held crossing ratio above 3.6", separator["held_summary"]["uncertain_to_certain_crossing_ratio"] > 3.6)

    for name, language in (
        ("gdt605_boundary_latin.json", "latin"),
        ("gdt605_boundary_old_italian.json", "old_italian"),
    ):
        attack = load_json(name)
        check(f"{language} attack language", attack["language"] == language)
        check(f"{language} attack decision", attack["decision"] == "BOUNDARY_AWARE_ONE_LETTER_SUBSTITUTION_REJECTED")
        check(f"{language} attack inventory", attack["unit_types"] == 98 and attack["held_unseen_unit_types"] == [])
        check(f"{language} three real starts", len(attack["models"]["real"]["runs"]) == 3)
        check(f"{language} every real differential negative", all(run["held_real_minus_destroyed_bits_per_character"] < 0 for run in attack["models"]["real"]["runs"]))
        check(f"{language} unstable held-weighted keys", max(pair["held_weighted_agreement"] for pair in attack["models"]["real"]["key_agreement"]) < 0.30)

    live_digest, live_rows, live_pages, live_folios = live_guarded_hash()
    check("live guarded digest", live_digest == EXPECTED_GUARDED)
    check("live guarded capacity", (live_rows, live_pages, live_folios) == (4_165, 180, 91))

    forbidden_patterns = (
        re.compile("/(?:" + "home" + "|" + "Users" + "|" + "tmp" + ")/"),
        re.compile("file" + "://"),
        re.compile(r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY"),
        re.compile(r"(?:AKIA|ghp_|sk-)[A-Za-z0-9_-]{12,}"),
    )
    scanned = 0
    for area in (HERE / "src", HERE / "artifacts"):
        for path in area.rglob("*"):
            if not path.is_file() or path.name == "gdt605_validation.json":
                continue
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                check(f"no bytecode cache {path.relative_to(HERE)}", False)
                continue
            text = path.read_text(errors="ignore")
            check(f"privacy {path.relative_to(HERE)}", not any(pattern.search(text) for pattern in forbidden_patterns))
            scanned += 1
    check("privacy scan covered files", scanned >= 10)

    status = "PASS" if all(item["passed"] for item in checks) else "FAIL"
    result = {
        "experiment_id": "GDT605",
        "status": status,
        "checks": checks,
        "checks_passed": sum(item["passed"] for item in checks),
        "artifact_sha256": EXPECTED,
        "decision": "STABLE_98_UNIT_ALPHABET__ONE_LETTER_READING_REJECTED",
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
    }
    (OUT / "gdt605_validation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
