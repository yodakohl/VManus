#!/usr/bin/env python3
"""Reproduce the frozen complete candidate pools for accelerated optimization."""
import argparse,subprocess,time
from pathlib import Path
from run import BASE,EDITIONS,prepare,candidate_rows,write_json

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-units',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--budget-seconds',type=float,default=600);a=p.parse_args()
 out=a.output_dir;out.mkdir(parents=True,exist_ok=True)
 assert not any(out.glob('*_CANDIDATES.json.gz')),'refusing to overwrite prepared candidates'
 deadline=time.monotonic()+a.budget_seconds;packet=prepare(a.source_units,out);binary=out/'match'
 subprocess.run(['g++','-O3','-std=c++17','-fopenmp',str(BASE/'src/match.cpp'),'-o',str(binary)],check=True)
 import json
 for e in EDITIONS:
  matches=out/(e+'_MATCHES.csv');remaining=deadline-time.monotonic()
  assert remaining>0,'preparation budget exhausted'
  r=subprocess.run([str(binary),str(out/(e+'_TARGET.txt')),str(out/'SOURCE_RECORDS.txt'),str(matches)],check=True,capture_output=True,text=True,timeout=remaining)
  enumeration=json.loads(r.stdout);candidates,n,complete=candidate_rows(packet,e,matches,deadline)
  assert complete and n==enumeration['matches'],'candidate preparation incomplete'
  write_json(out/(e+'_CANDIDATES.json.gz'),{'edition':e,'candidates':candidates,'enumeration':enumeration,'raw_matches':n,'candidate_materialization_complete':complete})
  paragraphs={p:i for i,p in enumerate(sorted({c['paragraph'] for c in candidates}))}
  with (out/(e+'_OPT_INPUT.txt')).open('w') as f:
   f.write(str(len(candidates))+'\n')
   for c in candidates:
    pairs=sorted(c['mapping'].items());f.write(str(paragraphs[c['paragraph']])+' '+str(c['weight'])+' '+str(len(pairs))+' '+' '.join(str(x) for pair in pairs for x in pair)+'\n')
  print(e,len(candidates),flush=True)
if __name__=='__main__':main()
