#!/usr/bin/env python3
"""Fixed accounting of frozen human/model reading judgments; no classification."""
import hashlib,json
from pathlib import Path
EXP=Path(__file__).resolve().parents[1]
C=['WATER','AIR','BASIN_ART','PIPE_ART','BASIN_NAT','PIPE_NAT']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def label(vals):return 'E' if 'E' in vals else 'U' if 'U' in vals else 'N'
def counts(aa,bb,fields):
 lower=[0,0,0];upper=[0,0,0]
 for a,b in zip(aa,bb):
  av=[label([a[k] for k in f]) for f in fields];bv=[label([b[k] for k in f]) for f in fields]
  for j in range(2):lower[j]+=av[j]==bv[j]=='E';upper[j]+=av[j]!='N' or bv[j]!='N'
  lower[2]+=all(v=='E' for v in av+bv)
  upper[2]+=all(av[j]!='N' or bv[j]!='N' for j in range(2))
 return {'lower':lower,'upper':upper}
def main():
 windows=json.loads((EXP/'artifacts/WINDOWS.json').read_text())['windows']; ids={r['id'] for r in windows}
 streams={'A':{},'B':{}};bindings={}
 for p in sorted((EXP/'artifacts').glob('ANNOTATIONS_*.json')):
  packet=json.loads(p.read_text());o=packet['observer'];assert o in streams
  assert packet['complete_reading'] is True
  for r in packet['rows']:
   assert r['id'] in ids and r['id'] not in streams[o]
   assert set(r['values'])==set(C) and set(r['values'].values())<={'E','U','N'}
   assert all(k in r['evidence'] for k in C if r['values'][k]!='N')
   streams[o][r['id']]=r['values']
  bindings[str(p.relative_to(EXP))]=digest(p)
 coverage={o:len(v) for o,v in streams.items()}
 if any(set(v)!=ids for v in streams.values()):
  result={'status':'INCOMPLETE_SOURCE_ANNOTATION_NO_PRIORITY','coverage':coverage,'required_per_stream':len(ids),'bindings':bindings}
 else:
  cells=[]
  for work in ['GALEN','QUINTE','SALERNO','BALNEIS']:
   native=sorted([r for r in windows if r['work']==work],key=lambda x:x['index'])
   for scale in [100,200,400]:
    n=scale//100; aggregated={o:[] for o in streams}
    for start in range(0,len(native),n):
     part=native[start:start+n]
     for o in streams:aggregated[o].append({k:label([streams[o][r['id']][k] for r in part]) for k in C})
    cell={'work':work,'scale':scale,'windows':len(aggregated['A'])}
    for pair,fields in {'T':[['WATER'],['AIR']],'F_ART':[['BASIN_ART'],['PIPE_ART']],'F_BROAD':[['BASIN_ART','BASIN_NAT'],['PIPE_ART','PIPE_NAT']]}.items():
     cell[pair]=counts(aggregated['A'],aggregated['B'],fields)
    cells.append(cell)
  def dominates(x,y):
   inequalities=all(c[x]['lower'][j]>=c[y]['upper'][j] for c in cells for j in range(3))
   strict=all(any(c[x]['lower'][j]>c[y]['upper'][j] for c in cells) for j in range(2))
   joint=all(sum(c[x]['lower'][2]>0 for c in cells if c['scale']==s)>=2 for s in [100,200,400])
   return inequalities and strict and joint
  comparisons={f'{x}>{y}':dominates(x,y) for x,y in [('T','F_ART'),('T','F_BROAD'),('F_ART','T'),('F_BROAD','T')]}
  status='CONDITIONAL_T_NOMINAL_PRIORITY' if comparisons['T>F_ART'] and comparisons['T>F_BROAD'] else 'CONDITIONAL_F_NOMINAL_PRIORITY' if comparisons['F_ART>T'] and comparisons['F_BROAD>T'] else 'NO_ROBUST_SOURCE_PRIORITY'
  result={'status':status,'coverage':coverage,'cells':cells,'comparisons':comparisons,'bindings':bindings}
 result.update(experiment='GDT1162',confirmed_words=0,new_target_access=0,claim_ceiling='Source-domain authorship priority only; no target likelihood, local-reading rejection or translation.')
 (EXP/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
if __name__=='__main__':main()
