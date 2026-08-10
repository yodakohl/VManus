#!/usr/bin/env python3
"""One-shot frozen F69M001 manuscript target."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path

from f69m001_core import ALPHABET, evaluate, null_prefix_codes, validate_sequences


BASE=Path(__file__).resolve().parent; ROOT=BASE.parent.parent; RESULTS=BASE/'results'
FREEZE=BASE/'F69M001_TARGET_FREEZE.json'; CAPACITY=RESULTS/'f69m001_capacity.json'
CONTROLS=RESULTS/'f69m001_controls.json'; CONTROL_VALIDATION=RESULTS/'f69m001_controls_validation.json'
CONSENSUS=RESULTS/'source_sta_family_consensus_loci.tsv'
OUT=RESULTS/'f69m001_target.json'; REPORT=RESULTS/'f69m001_target.md'
VOUT=RESULTS/'f69m001_target_validation.json'; VREPORT=RESULTS/'f69m001_target_validation.md'
FROZEN_FILES={
    'experiments/semantic_assumptions/F69M001_LUNAR_MANSION_PREFIX_METHOD.md',
    'experiments/semantic_assumptions/f69v_lunar_mansion_agrippa_roster.tsv',
    'experiments/semantic_assumptions/audit_f69m001_capacity.py',
    'experiments/semantic_assumptions/results/f69m001_capacity.json',
    'experiments/semantic_assumptions/results/f69m001_capacity.md',
    'experiments/semantic_assumptions/f69m001_core.py',
    'experiments/semantic_assumptions/run_f69m001_controls.py',
    'experiments/semantic_assumptions/results/f69m001_controls.json',
    'experiments/semantic_assumptions/results/f69m001_controls.md',
    'experiments/semantic_assumptions/validate_f69m001_controls.py',
    'experiments/semantic_assumptions/results/f69m001_controls_validation.json',
    'experiments/semantic_assumptions/results/f69m001_controls_validation.md',
    'experiments/semantic_assumptions/run_f69m001_target.py',
    'experiments/semantic_assumptions/validate_f69m001_target.py',
    'experiments/semantic_assumptions/freeze_f69m001_target.py',
    'experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv',
    'experiments/semantic_assumptions/results/source_sta_family_consensus_validation.json',
    'transcription/voynich_stolfi25e1_lines.tsv',
}


def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()


def install(path:Path,text:str)->None:
    if path.exists():raise SystemExit(f'refusing overwrite {path.name}')
    fd,temp=tempfile.mkstemp(prefix=f'.{path.name}.',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf8') as handle:
            handle.write(text);handle.flush();os.fsync(handle.fileno())
        if path.exists():raise SystemExit('concurrent output')
        os.link(temp,path)
    finally:
        try:os.unlink(temp)
        except FileNotFoundError:pass


def main()->None:
    outputs=(OUT,REPORT,VOUT,VREPORT)
    if any(path.exists() for path in outputs):raise SystemExit('target/validation output exists')
    freeze=json.loads(FREEZE.read_text())
    if freeze['status']!='FROZEN_TARGET_AND_VALIDATION_ABSENT':raise SystemExit('freeze')
    if set(freeze['frozen_files'])!=FROZEN_FILES:raise SystemExit('frozen allowlist')
    for relative,digest in freeze['frozen_files'].items():
        if sha(ROOT/relative)!=digest:raise SystemExit(f'frozen mismatch {relative}')
    if freeze['target_outputs']!=[str(path.relative_to(ROOT)) for path in outputs]:raise SystemExit('outputs')
    capacity=json.loads(CAPACITY.read_text());controls=json.loads(CONTROLS.read_text());validation=json.loads(CONTROL_VALIDATION.read_text())
    if capacity['status']!='PASS_UNSCORED_28_ORDERED_LABELS_AND_FIXED_ROSTER':raise SystemExit('capacity')
    if controls['status']!='PASS_40_WORLD_PREFIX_TOPOLOGY_CONTROLS' or not all(controls['gates'].values()):raise SystemExit('controls')
    if validation['status']!='PASS_INDEPENDENT_40_WORLD_RECONSTRUCTION':raise SystemExit('validation')
    expected=capacity['panel'];expected_map={row['locus']:row for row in expected}
    if len(expected)!=28 or len(expected_map)!=28 or sorted(int(row['ordinal']) for row in expected)!=list(range(1,29)):
        raise SystemExit('capacity panel')
    target={};all_families=set()
    with CONSENSUS.open(encoding='utf8',newline='') as handle:
        for row in csv.DictReader(handle,delimiter='\t'):
            all_families.update(row['family_sequence'])
            if row['locus'] in expected_map:
                if row['locus'] in target:raise SystemExit('duplicate target locus')
                target[row['locus']]=row
    if tuple(sorted(all_families))!=ALPHABET or set(target)!=set(expected_map):raise SystemExit('target coverage/alphabet')
    sequences=[]
    for meta in sorted(expected,key=lambda row:int(row['ordinal'])):
        row=target[meta['locus']]
        if row['page']!='f69v' or row['code']!='@Ri' or int(row['symbol_count'])!=meta['consensus_symbol_count'] or len(row['family_sequence'])<3:
            raise SystemExit('target metadata')
        sequences.append(row['family_sequence'])
    validate_sequences(sequences)
    roster=[row['name'] for row in capacity['historical_roster']]
    nulls={domain:null_prefix_codes(roster,domain) for domain in ('GLOBAL','INITIAL_CONDITIONED')}
    result_eval=evaluate(sequences,roster,nulls)
    external={"capacity_pass":True,"controls_pass":True,"independent_controls_pass":True,"frozen_hashes_pass":True,
              "exact_28_ordered_sequences":len(sequences)==28,"global_21_family_alphabet":True,
              "target_and_validation_absent_before_run":True,"zero_English_glosses":True}
    decision='CONFIRM_FIXED_LATIN_MANSION_ROSTER_PREFIX_TOPOLOGY' if result_eval['passes'] and all(external.values()) else 'NONCONFIRM_FIXED_LATIN_MANSION_PREFIX_TOPOLOGY'
    result={"experiment":"F69M001_TARGET","status":"PROVISIONAL_AWAITING_INDEPENDENT_VALIDATION","freeze_sha256":sha(FREEZE),
            "inputs":{path.name:sha(path) for path in (FREEZE,CAPACITY,CONTROLS,CONTROL_VALIDATION,CONSENSUS,BASE/'f69m001_core.py',Path(__file__))},
            "ordered_loci":[row['locus'] for row in sorted(expected,key=lambda row:int(row['ordinal']))],"target_sequences":sequences,
            "evaluation":result_eval,"external_gates":external,"decision":decision,
            "claim_ceiling":"A pass supports only an anonymous three-depth prefix-topology alignment with this fixed Latin mansion roster; it does not identify a mansion, name, letter, sound, word, language, cipher, plaintext, or translation."}
    e=result_eval
    report=("# F69M001 f69v mansion-prefix target\n\n"+f"Status: **{result['status']}**\n\nDecision: **{decision}**\n\n"
            f"The best of 56 cyclic/reflected alignments is **{e['best_direction']} rotation {e['best_rotation']}**, with mean phi **{e['S']:.6f}** and depth values **{e['best_depth_phi'][0]:.6f}, {e['best_depth_phi'][1]:.6f}, {e['best_depth_phi'][2]:.6f}**. "
            f"The full-permutation p is **{e['p_global']:.6f}** and the dominant-initial-conditioned p is **{e['p_initial_conditioned']:.6f}**. Alignment margin is **{e['alignment_margin']:.6f}** and minimum one-item deletion score is **{e['min_deletion']:.6f}**.\n\n"
            "Independent reconstruction is mandatory. Neither outcome identifies a mansion, name, number, letter, sound, word, meaning, plaintext, or translation.\n")
    if any(path.exists() for path in outputs):raise SystemExit('output appeared')
    install(REPORT,report)
    try:install(OUT,json.dumps(result,indent=2,sort_keys=True)+'\n')
    except BaseException:
        try:REPORT.unlink()
        except FileNotFoundError:pass
        raise
    print(json.dumps({"decision":decision,"S":e['S'],"p_global":e['p_global'],"p_conditioned":e['p_initial_conditioned']},sort_keys=True))


if __name__=='__main__':main()
