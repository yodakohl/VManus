#!/usr/bin/env python3
"""Production-free target reconstruction for F69M001."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path

# This is the already validated clean-room implementation, not production core.
import validate_f69m001_controls as clean


BASE=Path(__file__).resolve().parent;ROOT=BASE.parent.parent;RESULTS=BASE/'results'
FREEZE=BASE/'F69M001_TARGET_FREEZE.json';CAPACITY=RESULTS/'f69m001_capacity.json';CONSENSUS=RESULTS/'source_sta_family_consensus_loci.tsv'
TARGET=RESULTS/'f69m001_target.json';TARGET_REPORT=RESULTS/'f69m001_target.md';OUT=RESULTS/'f69m001_target_validation.json';REPORT=RESULTS/'f69m001_target_validation.md'


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


def render(target:dict[str,object])->str:
    e=target['evaluation']
    return ("# F69M001 f69v mansion-prefix target\n\n"+f"Status: **{target['status']}**\n\nDecision: **{target['decision']}**\n\n"
            f"The best of 56 cyclic/reflected alignments is **{e['best_direction']} rotation {e['best_rotation']}**, with mean phi **{e['S']:.6f}** and depth values **{e['best_depth_phi'][0]:.6f}, {e['best_depth_phi'][1]:.6f}, {e['best_depth_phi'][2]:.6f}**. "
            f"The full-permutation p is **{e['p_global']:.6f}** and the dominant-initial-conditioned p is **{e['p_initial_conditioned']:.6f}**. Alignment margin is **{e['alignment_margin']:.6f}** and minimum one-item deletion score is **{e['min_deletion']:.6f}**.\n\n"
            "Independent reconstruction is mandatory. Neither outcome identifies a mansion, name, number, letter, sound, word, meaning, plaintext, or translation.\n")


def main()->None:
    if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
    freeze=json.loads(FREEZE.read_text())
    if freeze['status']!='FROZEN_TARGET_AND_VALIDATION_ABSENT':raise AssertionError('freeze status')
    if freeze['target_outputs']!=[str(path.relative_to(ROOT)) for path in (TARGET,TARGET_REPORT,OUT,REPORT)]:raise AssertionError('outputs')
    for relative,digest in freeze['frozen_files'].items():
        if sha(ROOT/relative)!=digest:raise AssertionError(relative)
    capacity=json.loads(CAPACITY.read_text());target=json.loads(TARGET.read_text());expected=capacity['panel'];emap={row['locus']:row for row in expected}
    if len(expected)!=28 or len(emap)!=28 or sorted(int(row['ordinal']) for row in expected)!=list(range(1,29)):raise AssertionError('capacity')
    if target['status']!='PROVISIONAL_AWAITING_INDEPENDENT_VALIDATION':raise AssertionError('target status')
    rows={};alphabet=set()
    with CONSENSUS.open(encoding='utf8',newline='') as handle:
        for row in csv.DictReader(handle,delimiter='\t'):
            alphabet.update(row['family_sequence'])
            if row['locus'] in emap:
                if row['locus'] in rows:raise AssertionError('duplicate target locus')
                rows[row['locus']]=row
    if tuple(sorted(alphabet))!=clean.ALPHABET or set(rows)!=set(emap):raise AssertionError('source')
    ordered=sorted(expected,key=lambda row:int(row['ordinal']));sequences=[rows[row['locus']]['family_sequence'] for row in ordered]
    clean.validate_sequences(sequences);roster=[row['name'] for row in capacity['historical_roster']]
    nulls={domain:clean.prepare(roster,domain) for domain in ('GLOBAL','INITIAL_CONDITIONED')}
    evaluation=clean.evaluate(sequences,roster,nulls)
    if target['ordered_loci']!=[row['locus'] for row in ordered] or target['target_sequences']!=sequences or target['evaluation']!=evaluation:raise AssertionError('target')
    external={"capacity_pass":True,"controls_pass":True,"independent_controls_pass":True,"frozen_hashes_pass":True,"exact_28_ordered_sequences":True,
              "global_21_family_alphabet":True,"target_and_validation_absent_before_run":True,"zero_English_glosses":True}
    decision='CONFIRM_FIXED_LATIN_MANSION_ROSTER_PREFIX_TOPOLOGY' if evaluation['passes'] else 'NONCONFIRM_FIXED_LATIN_MANSION_PREFIX_TOPOLOGY'
    if target['external_gates']!=external or target['decision']!=decision or target['freeze_sha256']!=sha(FREEZE):raise AssertionError('decision')
    if TARGET_REPORT.read_text()!=render(target):raise AssertionError('report')
    checks=16+len(freeze['frozen_files'])+28+56+2*8192
    result={"experiment":"F69M001_TARGET_VALIDATION","status":"PASS_PRODUCTION_FREE_TARGET_RECONSTRUCTION","checks":checks,
            "inputs":{path.name:sha(path) for path in (FREEZE,CAPACITY,CONSENSUS,TARGET,TARGET_REPORT,Path(__file__),BASE/'validate_f69m001_controls.py')},
            "S":evaluation['S'],"p_global":evaluation['p_global'],"p_initial_conditioned":evaluation['p_initial_conditioned'],
            "scientific_gates":evaluation['gates'],"final_decision":decision,"claim_ceiling":target['claim_ceiling']}
    report=f"# F69M001 target validation\n\nStatus: **{result['status']}**\n\nThe frozen clean-room implementation passes **{checks} checks** and reconstructs all 28 ordered prefix sequences, 56 alignments, both 8,192-assignment nulls, deletions, gates, report, and final decision **{decision}**. No mansion, name, number, letter, sound, word, meaning, plaintext, or translation follows.\n"
    install(REPORT,report)
    try:install(OUT,json.dumps(result,indent=2,sort_keys=True)+'\n')
    except BaseException:
        try:REPORT.unlink()
        except FileNotFoundError:pass
        raise
    print(json.dumps({"status":result['status'],"decision":decision,"S":evaluation['S'],"p_global":evaluation['p_global'],"p_conditioned":evaluation['p_initial_conditioned']},sort_keys=True))


if __name__=='__main__':main()
