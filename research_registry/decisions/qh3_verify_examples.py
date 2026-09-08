#!/usr/bin/env python3
"""Recount ten selected Luna examples through the selector-first source guard."""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
EXAMPLES = [('f8r.19','shol kaiin shol kaiin'),
            ('f30r.11','cheor chey cheor chey'),
            ('f16v.8','chol y daiin'),('f21v.4','chol daiin daiin'),
            ('f21v.6','chol todaiin daiin'),('f105r.15','ol r aiin'),
            ('f107r.46','ol cheor aiin'),('f55v.10','ol s aiin'),
            ('f104v.4','chey qol chedy'),('f111v.32','chey qol chedy')]

def main():
    cmd = ['./vmanus-exp','query-tsv',SOURCE,'--selector','page','--columns',
           'edition,locus,source_group_index,ivtff_group_raw,left_separator,right_separator',
           '--forbid-prefix','f84','--forbid-prefix','f84r']
    for page in sorted({loc.split('.')[0] for loc,_ in EXAMPLES}):
        cmd += ['--allow',page]
    query = subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
    rows = list(csv.DictReader(io.StringIO(query.stdout),delimiter='\t'))
    out = []
    for locus,pattern in EXAMPLES:
        terms = pattern.split()
        matches = {}
        for edition in ('ZL3b','IT2a','RF1b'):
            seq = sorted((r for r in rows if r['edition']==edition and r['locus']==locus),
                         key=lambda r:int(r['source_group_index']))
            hits = []
            for i in range(len(seq)-len(terms)+1):
                window = seq[i:i+len(terms)]
                if [r['ivtff_group_raw'] for r in window] != terms:
                    continue
                indices = [int(r['source_group_index']) for r in window]
                assert indices == list(range(indices[0],indices[0]+len(terms)))
                seams = [v for a,b in zip(window,window[1:])
                         for v in (a['right_separator'],b['left_separator'])]
                hits.append({'indices_1based':indices,'internal_separators':seams})
            matches[edition] = hits
        literal = all(len(hits)==1 for hits in matches.values())
        definite = literal and all(set(hits[0]['internal_separators'])=={'DEFINITE_SPACE'}
                                   for hits in matches.values())
        out.append({'locus':locus,'literal':pattern,'unique_match_each_reading':literal,
                    'all_internal_seams_definite':definite,'readings':matches})
    result = {'source':SOURCE,'source_sha256':hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),
              'guard_command':cmd,'guard_statistics':query.stderr.strip(),
              'projection_sha256':hashlib.sha256(query.stdout.encode()).hexdigest(),
              'examples':out,
              'limits':'Selected-example recount only; no statistical salience, novelty or semantic test. Alternate readings are not independent manuscript observations.'}
    destination = ROOT/'research_registry/decisions/qh3_verified_examples.json'
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'examples':len(out),'literal_all_readings':sum(r['unique_match_each_reading'] for r in out),
                      'definite_seams_all_readings':sum(r['all_internal_seams_definite'] for r in out),
                      'qualified':[r['locus'] for r in out if not r['all_internal_seams_definite']]}))

if __name__ == '__main__':
    main()
