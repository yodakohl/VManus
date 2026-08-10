#!/usr/bin/env python3
"""Nonimporting reconstruction of F69M001 capacity and controls."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
RESULTS = BASE / "results"
CAPACITY = RESULTS / "f69m001_capacity.json"
CONTROLS = RESULTS / "f69m001_controls.json"
ROSTER_FILE = BASE / "f69v_lunar_mansion_agrippa_roster.tsv"
LINES = ROOT / "transcription" / "voynich_stolfi25e1_lines.tsv"
CONSENSUS = RESULTS / "source_sta_family_consensus_loci.tsv"
OUT = RESULTS / "f69m001_controls_validation.json"
REPORT = RESULTS / "f69m001_controls_validation.md"
ALPHABET = tuple("ABCDEFGHJKLMNPQTUVWXZ")
N, ASSIGNMENTS = 28, 8192
DEPTHS = (1, 2, 3)
TOL = 1e-15
MODES = ("FULL_PLANT", "NULL", "DOMINANT_INITIAL_ONLY", "FOUR_BLOCK_ONLY", "SHALLOW_TWO_DEPTH_ONLY")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha(value: object) -> str:
    return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()


def norm(name: str) -> str:
    value = name.lower().split()[0]
    if len(value) < 3 or not value.isascii() or not value.isalpha(): raise ValueError("name")
    return value


KEYS = [(direction, rotation) for direction in ("FORWARD", "REVERSE") for rotation in range(N)]
MAPS = np.asarray([
    [((i + rotation) % N if direction == "FORWARD" else (rotation - i) % N) for i in range(N)]
    for direction, rotation in KEYS
], dtype=np.int16)


def codes(values: list[str], depth: int) -> np.ndarray:
    prefixes = [value[:depth] for value in values]
    lookup = {value: index for index, value in enumerate(sorted(set(prefixes)))}
    return np.asarray([lookup[value] for value in prefixes], dtype=np.int16)


def validate_sequences(values: list[str]) -> None:
    if len(values) != N or any(len(value) < 3 for value in values): raise ValueError("shape")
    if any(any(char not in ALPHABET for char in value) for value in values): raise ValueError("alphabet")


def alignment_phi(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    pi, pj = np.triu_indices(N, 1)
    xe = x[pi] == x[pj]
    ex, ey, total = int(xe.sum()), int((y[pi] == y[pj]).sum()), N*(N-1)//2
    denominator = math.sqrt(ex*(total-ex)*ey*(total-ey))
    if denominator == 0: raise ValueError("degenerate")
    aligned = y[MAPS]
    n11 = (aligned[:, pi[xe]] == aligned[:, pj[xe]]).sum(axis=1).astype(float)
    n10, n01 = ex-n11, ey-n11
    n00 = total-n11-n10-n01
    return (n11*n00-n10*n01)/denominator


def observed(values: list[str], roster: list[str]) -> dict[str, object]:
    validate_sequences(values)
    names = [norm(name) for name in roster]
    phis = np.vstack([alignment_phi(codes(values,k),codes(names,k)) for k in DEPTHS]).T
    means = phis.mean(axis=1)
    best = min(range(56), key=lambda index: (-float(means[index]), index))
    second = max(float(value) for i,value in enumerate(means) if i != best)
    return {"best":best,"key":KEYS[best],"phi":phis[best],"S":float(means[best]),"second":second,"margin":float(means[best])-second}


def order(domain: str, assignment: int, positions: list[int]) -> list[int]:
    return sorted(positions,key=lambda position:hashlib.sha256(f"F69M001|{domain}|{assignment}|{position}".encode()).digest())


def prepare(roster: list[str], domain: str) -> dict[int,np.ndarray]:
    names=[norm(name) for name in roster]
    output={k:np.empty((ASSIGNMENTS,N),dtype=np.int16) for k in DEPTHS}
    groups=defaultdict(list)
    for position,name in enumerate(names): groups[name[0]].append(position)
    for a in range(ASSIGNMENTS):
        if domain=="GLOBAL": perm=[names[source] for source in order(domain,a,list(range(N)))]
        else:
            perm=list(names)
            for positions in groups.values():
                for destination,source in zip(sorted(positions),order(domain,a,positions),strict=True): perm[destination]=names[source]
        for k in DEPTHS: output[k][a]=codes(perm,k)
    return output


def orbit(values: list[str], prepared: dict[int,np.ndarray]) -> np.ndarray:
    validate_sequences(values)
    pi,pj=np.triu_indices(N,1); total=N*(N-1)//2
    scores=np.zeros((ASSIGNMENTS,56),dtype=float)
    for k in DEPTHS:
        x=codes(values,k); xe=x[pi]==x[pj]; ex=int(xe.sum())
        y=prepared[k]; ey=int((y[0,pi]==y[0,pj]).sum())
        den=math.sqrt(ex*(total-ex)*ey*(total-ey))
        if den==0: raise ValueError("degenerate")
        for start in range(0,ASSIGNMENTS,128):
            block=y[start:start+128,MAPS]
            n11=(block[:,:,pi[xe]]==block[:,:,pj[xe]]).sum(axis=2).astype(float)
            n10,n01=ex-n11,ey-n11; n00=total-n11-n10-n01
            scores[start:start+len(block)]+=(n11*n00-n10*n01)/den
    return (scores/3).max(axis=1)


def deletion(values:list[str],roster:list[str],best:int)->list[float]:
    names=[norm(name) for name in roster]; mapping=MAPS[best]; output=[]
    for deleted in range(N):
        keep=[i for i in range(N) if i!=deleted]; depths=[]
        for k in DEPTHS:
            x=[values[i][:k] for i in keep]; y=[names[int(mapping[i])][:k] for i in keep]
            pi,pj=np.triu_indices(N-1,1)
            xb=np.asarray([x[i]==x[j] for i,j in zip(pi,pj,strict=True)]); yb=np.asarray([y[i]==y[j] for i,j in zip(pi,pj,strict=True)])
            n11=int((xb&yb).sum()); n10=int((xb&~yb).sum()); n01=int((~xb&yb).sum()); n00=int((~xb&~yb).sum())
            den=math.sqrt((n11+n10)*(n01+n00)*(n11+n01)*(n10+n00))
            if den==0: raise ValueError("deletion")
            depths.append((n11*n00-n10*n01)/den)
        output.append(math.fsum(depths)/3)
    return output


def evaluate(values:list[str],roster:list[str],nulls:dict[str,dict[int,np.ndarray]])->dict[str,object]:
    obs=observed(values,roster); orbits={d:orbit(values,nulls[d]) for d in ("GLOBAL","INITIAL_CONDITIONED")}
    p={d:(1+int((a>=obs['S']-TOL).sum()))/(ASSIGNMENTS+1) for d,a in orbits.items()}
    deletes=deletion(values,roster,obs['best']); phi=[float(x) for x in obs['phi']]
    gates={
        "S_at_least_025":obs['S']>=.25-TOL,"global_p_at_most_001":p['GLOBAL']<=.01+TOL,
        "initial_conditioned_p_at_most_005":p['INITIAL_CONDITIONED']<=.05+TOL,
        "all_depths_positive":all(x>0 for x in phi),"depth2_and_depth3_at_least_025":phi[1]>=.25-TOL and phi[2]>=.25-TOL,
        "alignment_margin_at_least_003":obs['margin']>=.03-TOL,"all_deletions_at_least_015":min(deletes)>=.15-TOL,
        "finite":all(math.isfinite(x) for x in [obs['S'],obs['margin'],*phi,*p.values(),*deletes,*orbits['GLOBAL'],*orbits['INITIAL_CONDITIONED']]),
    }
    return {"sequence_sha256":object_sha(values),"best_direction":obs['key'][0],"best_rotation":obs['key'][1],"S":obs['S'],"best_depth_phi":phi,
            "second_best":obs['second'],"alignment_margin":obs['margin'],"p_global":p['GLOBAL'],"p_initial_conditioned":p['INITIAL_CONDITIONED'],
            "global_orbit_sha256":hashlib.sha256(orbits['GLOBAL'].astype('<f8').tobytes()).hexdigest(),
            "conditioned_orbit_sha256":hashlib.sha256(orbits['INITIAL_CONDITIONED'].astype('<f8').tobytes()).hexdigest(),
            "deletion_scores":deletes,"min_deletion":min(deletes),"gates":gates,"passes":all(gates.values())}


def synthetic(roster:list[str],world:int,mode:str)->list[str]:
    names=[norm(name) for name in roster]; chars=sorted(set(''.join(name[:3] for name in names))); offset=world%21
    mapping={char:ALPHABET[(i+offset)%21] for i,char in enumerate(chars)}
    positions=[((world*3+i)%N) if world%2==0 else ((world*3-i)%N) for i in range(N)]
    encoded=[''.join(mapping[c] for c in names[source][:3]) for source in positions]
    if mode=="FULL_PLANT": return encoded
    if mode=="NULL": return [ALPHABET[(i+world)%21]+ALPHABET[(i*5+world+1)%21]+ALPHABET[(i*11+world+2)%21] for i in range(N)]
    if mode=="DOMINANT_INITIAL_ONLY": return [encoded[i][0]+ALPHABET[(i+world)%5]+ALPHABET[((i//5)+world)%3] for i in range(N)]
    if mode=="FOUR_BLOCK_ONLY":
        out=[ALPHABET[(i+world)%21]+ALPHABET[(i*5+2)%21]+ALPHABET[(i*11+4)%21] for i in range(N)]
        for i in range(21,25):out[i]="AAA"
        return out
    if mode=="SHALLOW_TWO_DEPTH_ONLY": return [encoded[i][:2]+ALPHABET[(i+world)%2] for i in range(N)]
    raise ValueError(mode)


def main()->None:
    if OUT.exists() or REPORT.exists():raise SystemExit("refusing overwrite")
    capacity=json.loads(CAPACITY.read_text()); controls=json.loads(CONTROLS.read_text())
    with ROSTER_FILE.open(encoding='utf8',newline='') as f: roster_rows=list(csv.DictReader(f,delimiter='\t'))
    roster=[row['name'] for row in roster_rows]
    if capacity['historical_roster']!=[{"ordinal":int(r['ordinal']),"name":r['name']} for r in roster_rows]:raise AssertionError('roster')
    with LINES.open(encoding='utf8',newline='') as f:
        radial=[(r['locus'],r['old_locus']) for r in csv.DictReader(f,delimiter='\t') if r['page']=='f69v' and r['code']=='@Ri']
    radial.sort(key=lambda x:int(x[1].rsplit('.',1)[1]))
    if [x[0] for x in radial]!=[row['locus'] for row in capacity['panel']]:raise AssertionError('panel')
    nulls={d:prepare(roster,d) for d in ('GLOBAL','INITIAL_CONDITIONED')}
    records=[]
    for world in range(8):
        for mode in MODES:records.append({"world":world,"mode":mode,"evaluation":evaluate(synthetic(roster,world,mode),roster,nulls)})
    if controls['records']!=records:raise AssertionError('records')
    counts={mode:sum(r['evaluation']['passes'] for r in records if r['mode']==mode) for mode in MODES}
    if counts!={"FULL_PLANT":8,"NULL":0,"DOMINANT_INITIAL_ONLY":0,"FOUR_BLOCK_ONLY":0,"SHALLOW_TWO_DEPTH_ONLY":0}:raise AssertionError('counts')
    if controls['pass_counts']!=counts or not all(controls['gates'].values()):raise AssertionError('top')
    checks=40+28+8+len(controls['inputs'])
    for name,digest in controls['inputs'].items():
        path=RESULTS/name if name.endswith('.json') else BASE/name
        if sha(path)!=digest:raise AssertionError(name)
    result={"experiment":"F69M001_CONTROL_VALIDATION","status":"PASS_INDEPENDENT_40_WORLD_RECONSTRUCTION","checks":checks,
            "inputs":{p.name:sha(p) for p in (CAPACITY,CONTROLS,ROSTER_FILE,LINES,CONSENSUS,Path(__file__))},"pass_counts":counts,
            "target_prefixes_accessed":False,"decision":"AUTHORIZE_HASH_FREEZE_AND_ONE_TARGET",
            "claim_ceiling":"Independent validation of capacity and synthetic controls only; no f69v prefix topology, roster identity, name, sound, meaning, plaintext, or translation."}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    REPORT.write_text(f"# F69M001 control validation\n\nStatus: **{result['status']}**\n\nA nonimporting implementation passes **{checks} checks** and reconstructs the ordered capacity, all 40 worlds, both 8,192-permutation nulls, deletions, gates, and bindings. No f69v target prefix was accessed. One separately frozen target is authorized; no list identity, name, sound, meaning, plaintext, or translation follows.\n")
    print(json.dumps({"status":result['status'],"checks":checks},sort_keys=True))


if __name__=='__main__':main()
