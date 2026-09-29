#!/usr/bin/env python3
"""GDT1086 text-blind invalid-owner preflight; never opens transcription TSV."""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt1086_f68v2_cardinal_side_reference"
INV = "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
E = ["f68v2.18", "f68v2.7", "f68v2.9", "f68v2.10", "f68v2.12", "f68v2.13", "f68v2.15", "f68v2.16"]
S = ["f68v2.17", "f68v2.8", "f68v2.11", "f68v2.14"]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    cmd = ["./vmanus-exp", "query-tsv", INV, "--selector", "page", "--allow", "f68v2", "--columns", "page,locus,unit,array_id,slot_index,unit_description"]
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(p.stdout), delimiter="\t"))
    assert len(rows) == 12
    assert [r["locus"] for r in rows if r["unit"] == "E1"] == E
    assert [r["locus"] for r in rows if r["unit"] == "S1"] == S
    assert all(r["page"] == "f68v2" for r in rows)
    result = {
        "experiment": "GDT1086",
        "status": "INVALID_OWNER_MAPPING__TEXT_ECHO_NOT_RUN",
        "registered_model": "four multi-star cardinal label fields, each referenced by two neighbouring radial titles",
        "observed_image_topology": "eight alternating sectors: four multi-star clusters without local labels (9,8,9,9 stars) and four single stars with paired radial labels (one star each); eight radial title lines lie on sector boundaries",
        "catalogue_source": "https://vib.tamagothi.de/index.php?id=f68v2&show=page",
        "native_image_source": "https://collections.library.yale.edu/iiif/2/1006197/3300,500,2400,2500/full/0/default.jpg",
        "native_image_sha256": "3bd53ba8b529913e2b357df2c22535351b1c1637f09436feee87818c59652e82",
        "text_blind_inventory_sha256": sha(ROOT / INV),
        "inventory_rows": rows,
        "query_command": cmd,
        "query_guard_stats": p.stderr.strip(),
        "transcription_tsv_queried": False,
        "transcription_content_scored": False,
        "confirmed_lexemes": 0,
        "sealed_f84_f84r": "CLOSED",
        "prior_exposure": "GDT353 historical; GDT1085 image; VIB public page displayed unadmitted f68v2 P/C text after registration, excluded from analysis",
        "decision": "Predeclared owner-check invalidates model before echo scoring; no posthoc sector reassignment."
    }
    out = EXP / "artifacts/RESULT.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(out)

if __name__ == "__main__":
    main()
