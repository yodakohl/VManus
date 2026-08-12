#!/usr/bin/env python3
"""Independent exact-DP validator for all RTA001 edge-program TSVs."""

from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent; R=HERE/'results'
REPS=('surface','family','member','root','construction')
COST={'KEEP':0,'DELETE':2,'INSERT':2,'SUBSTITUTE':3}

def rows(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dp(a,b):
    n=len(a);m=len(b);c=[[0]*(m+1) for _ in range(n+1)];t=[[0]*(m+1) for _ in range(n+1)];t[0][0]=1
    for i in range(1,n+1):c[i][0]=2*i;t[i][0]=1
    for j in range(1,m+1):c[0][j]=2*j;t[0][j]=1
    for i in range(1,n+1):
        for j in range(1,m+1):
            q=[(c[i-1][j-1]+(0 if a[i-1]==b[j-1] else 3),i-1,j-1),(c[i-1][j]+2,i-1,j),(c[i][j-1]+2,i,j-1)]
            z=min(x[0] for x in q);c[i][j]=z;t[i][j]=sum(t[x][y] for v,x,y in q if v==z)
    return c[n][m],t[n][m]
def main():
    meta=json.loads((R/'rta001_edge_programs.json').read_text()); checks=0
    for rep in REPS:
        p=R/f'rta001_edge_programs_{rep}.tsv'; data=rows(p)
        assert len(data)==1611;checks+=1
        assert meta['artifacts'][p.name]==sha(p);checks+=1
        assert Counter(x['status'] for x in data)=={'EXACT_PROGRAM':1596,'MISSING_SOURCE_READING':15};checks+=1
        for x in data:
            assert x['representation']==rep
            if x['status']!='EXACT_PROGRAM':
                assert x['edition']=='IT2a' and x['source_locus'].startswith('fRos') or x['target_locus'].startswith('fRos');continue
            a=json.loads(x['source_sequence_json']);b=json.loads(x['target_sequence_json']);cost,ties=dp(a,b)
            assert int(x['minimum_edit_cost'])==cost and int(x['optimal_alignment_count'])==ties
            program=json.loads(x['canonical_dsl_program_json']); assert program and all('op' in z for z in program)
            checks+=1
    print(json.dumps({'status':'PASS','checks':checks,'metadata_sha256':sha(R/'rta001_edge_programs.json')},sort_keys=True))
if __name__=='__main__':main()
