#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
SAFE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
OUT = Path(__file__).resolve().parent.parent / "artifacts" / "guarded_rows.tsv"
EXPECTED_SAFE = "7eba46774be44992064cc114f67329723ac7bf589321b0d763fb7f7f748cc1e9"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sha(SAFE) != EXPECTED_SAFE:
        raise RuntimeError("GDT327 allow-list changed")
    page_to_folio = {}
    with SAFE.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page, folio = row["page"], row["physical_folio"]
            if page.lower().startswith("f84") or folio.lower().startswith("f84"):
                raise RuntimeError("forbidden selector in allow-list")
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
        "transcription/voynich_zl3b_lines.tsv",
        "--selector", "page",
    ]
    for page in pages:
        command.extend(("--allow", page))
    command.extend((
        "--forbid-prefix", "f84",
        "--columns", "page,locus,line_number,section,language,hand,eva_clean,ivtff_raw",
    ))
    raw = subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout
    rows = list(csv.DictReader(io.StringIO(raw), delimiter="\t"))
    fields = [
        "page", "physical_folio", "split", "locus", "line_number",
        "section", "language", "hand", "eva_clean", "ivtff_raw",
    ]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        page = row["page"]
        if page not in page_to_folio or page.lower().startswith("f84"):
            raise RuntimeError("unsafe emitted row")
        folio = page_to_folio[page]
        writer.writerow({
            **row,
            "physical_folio": folio,
            "split": "held" if folio in held else "train",
        })
    OUT.write_text(buffer.getvalue())
    if sha(OUT) != "d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9":
        raise RuntimeError("guarded GDT605 export changed")
    print(json.dumps({
        "rows": len(rows), "pages": len(pages), "folios": len(folios),
        "train_folios": len(folios) - len(held), "held_folios": len(held),
        "sha256": sha(OUT),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
