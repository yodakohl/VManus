#!/usr/bin/env python3
"""Reproduce GDT605 from a guarded query through both letter attacks."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
SRC = HERE / "src"
OUT = HERE / "artifacts"
SAFE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
EXPECTED_SAFE = "7eba46774be44992064cc114f67329723ac7bf589321b0d763fb7f7f748cc1e9"
EXPECTED_GUARDED = "d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def materialize_guarded(path: Path) -> None:
    if sha256(SAFE) != EXPECTED_SAFE:
        raise RuntimeError("GDT327 allow-list changed")
    page_to_folio = {}
    with SAFE.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page, folio = row["page"], row["physical_folio"]
            if page.lower().startswith("f84") or folio.lower().startswith("f84"):
                raise RuntimeError("sealed selector in safe allow-list")
            previous = page_to_folio.setdefault(page, folio)
            if previous != folio:
                raise RuntimeError("page-to-folio mapping drift")
    pages = sorted(page_to_folio)
    folios = sorted(set(page_to_folio.values()))
    if len(pages) != 180 or len(folios) != 91:
        raise RuntimeError("unexpected allow-list capacity")
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
        "--forbid-prefix", "f84",
        "--columns",
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
            raise RuntimeError("guard emitted forbidden or unallowlisted selector")
        folio = page_to_folio[page]
        writer.writerow({
            **row,
            "physical_folio": folio,
            "split": "held" if folio in held else "train",
        })
    path.write_bytes(buffer.getvalue().encode())
    if sha256(path) != EXPECTED_GUARDED:
        raise RuntimeError("guarded GDT605 export changed")


def run_command(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gdt605-guarded-") as temporary:
        guarded = Path(temporary) / "gdt605_guarded_rows.tsv"
        materialize_guarded(guarded)
        run_command([
            sys.executable, str(SRC / "unit_inventory.py"),
            "--guarded-rows", str(guarded), "--output-dir", str(OUT),
        ])
        run_command([
            sys.executable, str(SRC / "separator_crossing.py"),
            "--guarded-rows", str(guarded),
            "--output", str(OUT / "gdt605_separator_crossing.json"),
        ])
        letter_jobs = [
            [
                sys.executable, str(SRC / "boundary_letter_attack.py"),
                "--guarded-rows", str(guarded), "--language", language,
                "--output", str(OUT / output),
            ]
            for language, output in (
                ("latin", "gdt605_boundary_latin.json"),
                ("old_italian", "gdt605_boundary_old_italian.json"),
            )
        ]
        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(run_command, letter_jobs))
    names = (
        "gdt605_unit_result.json", "gdt605_unit_inventory.tsv",
        "gdt605_bpe_merges.tsv", "gdt605_separator_crossing.json",
        "gdt605_boundary_latin.json", "gdt605_boundary_old_italian.json",
    )
    print(json.dumps({name: sha256(OUT / name) for name in names}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
