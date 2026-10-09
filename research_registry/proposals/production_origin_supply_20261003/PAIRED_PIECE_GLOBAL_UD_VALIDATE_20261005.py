#!/usr/bin/env python3
"""Bind a conditional code lemma to two fixed, exposed transcription loci.

Not an independent mathematical proof or image authentication. All raw-source
access goes through the selector-first guard; readers remain separate.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PREFIX = "PAIRED_PIECE_GLOBAL_UD_"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    packet = HERE / "HAND_WORD_EXTREMES_PACKET_20261005.json"
    profiles = HERE / (PREFIX + "PROFILES_20261005.json")
    contract = HERE / (PREFIX + "CONTRACT_NOTE_20261005.json")
    old = json.loads(packet.read_text())
    prof = json.loads(profiles.read_text())
    columns = "source_group_id,edition,page,locus,source_group_index,source_group_count,ivtff_group_raw,left_separator,right_separator"
    command = ["./vmanus-exp", "query-tsv", "experiments/semantic_assumptions/results/source_separator_transcription.tsv", "--selector", "locus", "--allow", "f14r.3", "--columns", columns]
    run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(run.stdout), delimiter="\t"))
    assert len(rows) == 15
    witnesses = []
    summaries = {}
    for edition in ("ZL3b", "IT2a", "RF1b"):
        lines = [line for line in old["lines"] if line["edition"] == edition and line["locus"] == "f23r.5"]
        assert len(lines) == 1
        groups = lines[0]["groups"]
        base = [g for g in groups if g["source_group_id"] == f"{edition}|f23r.5|G008"][0]
        assert base["ivtff_group_raw"] == "ol"
        assert base["left_separator"] == base["right_separator"] == "DEFINITE_SPACE"
        assert int(base["source_group_index"]) < int(base["source_group_count"])
        doubled = [g for g in rows if g["source_group_id"] == f"{edition}|f14r.3|G005"][0]
        assert doubled["ivtff_group_raw"] == base["ivtff_group_raw"] * 2
        assert doubled["left_separator"] == "DEFINITE_SPACE"
        assert doubled["right_separator"] == "LINE_END"
        assert int(doubled["source_group_index"]) == int(doubled["source_group_count"]) == 5
        for form in ("ol", "olol"):
            entry = next(p for p in prof["profiles"] if p["form"] == form)["editions"][edition]
            summaries.setdefault(form, {})[edition] = {k: entry[k] for k in ("count", "pages_with_form", "positions", "repetition")}
            if form == "olol":
                assert any(e["source_group_id"] == doubled["source_group_id"] and e["ivtff_group_raw"] == "olol" for e in entry["examples"])
        witnesses.append({"edition": edition, "base": base, "double": doubled})
    result = {
        "status": "FIXED_TWO_PIECE_GLOBAL_UD_CARRIER_CONTRADICTED",
        "binding_validation": "PASS",
        "witnesses": witnesses,
        "existing_profile_summaries": summaries,
        "source_command": command,
        "guard_receipt": run.stderr.strip(),
        "guarded_full_double_lines": rows,
        "hashes": {str(p.relative_to(ROOT)): sha(p) for p in (packet, profiles, contract, Path(__file__))},
        "proof": "Global injectivity of the non-erasing homomorphic piece code forces parse(WW)=parse(W)parse(W). Nonfinal W has two tokens; WW must then have four, exceeding either normal two or final singleton.",
        "limits": ["Conditional literal transcription and common-carrier contract, not identified native atoms", "Three alternate readings of one manuscript, not independent confirmations", "No original image inspection for these two loci", "No refutation of variable piece counts, group/context-dependent decoding, or1201confluent content decoding", "No complete writer, source-frequency test, or word meaning"]
    }
    out = HERE / (PREFIX + "RESULT_20261005.json")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "binding_validation": "PASS", "reader_bindings": len(witnesses), "result": str(out.relative_to(ROOT))}))

if __name__ == "__main__":
    main()
