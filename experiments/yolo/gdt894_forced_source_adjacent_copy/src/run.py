#!/usr/bin/env python3
"""Fixed source adjacency, frozen partial key, no new values or target realignment."""
import csv,hashlib,io,json,re,subprocess
from collections import defaultdict
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
ROOT=BASE.parents[2]
RAW='experiments/semantic_assumptions/results/source_separator_transcription.tsv'
COLS='source_group_id,edition,locus,page,kind,source_group_index,source_group_count,left_separator,right_separator,ivtff_group_raw'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def number(r):
 m=re.fullmatch(r'f103v\.([0-9]+)',r['locus'])
 assert m,'INVALID_TARGET_SCHEMA'
 return int(m[1])
def acquire():
 cmd=['./vmanus-exp','query-tsv',RAW,'--selector','page','--allow','f103v','--columns',COLS,'--forbid-prefix','f84','--forbid-prefix','f84r']
 raw=subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True).stdout
 rows=[r for r in csv.DictReader(io.StringIO(raw),delimiter='\t') if r['edition']=='RF1b']
 assert rows and all(r['page']=='f103v' for r in rows)
 rows.sort(key=lambda r:(number(r),int(r['source_group_index'])))
 return {'guard':{'argv':cmd,'source_sha256':sha(ROOT/RAW),'projection_sha256':hashlib.sha256(raw.encode()).hexdigest()},'rows':rows}

def evaluate(rows,p):
 assert all(r['page']=='f103v' and r['edition']=='RF1b' for r in rows)
 assert len({r['source_group_id'] for r in rows})==len(rows),'INVALID_TARGET_SCHEMA'
 assert rows==sorted(rows,key=lambda r:(number(r),int(r['source_group_index']))),'INVALID_TARGET_SCHEMA'
 assert len({(number(r),int(r['source_group_index'])) for r in rows})==len(rows),'INVALID_TARGET_SCHEMA'
 lines=defaultdict(list)
 for r in rows:lines[r['locus']].append(r)
 badlines=set()
 for locus,items in lines.items():
  n=len(items)
  if [int(r['source_group_index']) for r in items]!=list(range(1,n+1)) or any(int(r['source_group_count'])!=n for r in items):badlines.add(locus)
 positions={r['source_group_id']:i for i,r in enumerate(rows)}
 anchor=p['anchor'];ids=anchor['source_group_ids'];where=[positions[x] for x in ids]
 assert where==list(range(where[0],where[0]+len(ids))),'ANCHOR_CHANGED'
 assert [rows[i]['ivtff_group_raw'] for i in where]==anchor['cipher_words'],'ANCHOR_CHANGED'
 key=p['conditional_map'];values=set(key.values());assert len(values)==len(key)
 assert all(key[c]==s for c,s in zip(anchor['cipher_words'],anchor['source_words']))
 def edge(a,b):
  if a['locus']==b['locus']:
   if a['right_separator']!='DEFINITE_SPACE' or b['left_separator']!='DEFINITE_SPACE':return 'NONDEFINITE_SEPARATOR'
  elif number(b)!=number(a)+1:return 'MISSING_NUMERIC_LINE'
  elif a['right_separator']!='LINE_END' or b['left_separator']!='LINE_START':return 'NONDEFINITE_SEPARATOR'
  return None
 def row_problem(r):
  if r['locus'] in badlines:return 'INVALID_LINE_COUNTS'
  if r['kind']!='P':return 'NON_P_KIND'
  if not re.fullmatch('[a-z]+',r['ivtff_group_raw']):return 'NONLITERAL_GROUP'
  return None
 for i in where:
  assert row_problem(rows[i]) is None,'ANCHOR_MEASUREMENT_INVALID'
 for a,b in zip(where,where[1:]):assert edge(rows[a],rows[b]) is None,'ANCHOR_MEASUREMENT_INVALID'
 result={}
 for direction,step,start in (('preceding',-1,where[0]),('following',1,where[-1])):
  horizon=p['horizons'][direction];pairs=list(zip(horizon['offsets'],horizon['source_words']))
  if step<0:pairs.reverse()
  comparisons=[];barrier=None;cursor=start
  for offset,source in pairs:
   nxt=cursor+step
   if not 0<=nxt<len(rows):barrier={'offset':offset,'reason':'FOLIO_EDGE'};break
   left,right=(rows[nxt],rows[cursor]) if step<0 else (rows[cursor],rows[nxt])
   problem=edge(left,right) or row_problem(rows[nxt])
   if problem:barrier={'offset':offset,'reason':problem};break
   r=rows[nxt];code=r['ivtff_group_raw']
   if source in values:
    condition='KNOWN_MATCH' if key.get(code)==source else 'KNOWN_MISMATCH'
   else:condition='FORBIDDEN_KNOWN_CODE' if code in key else 'UNMAPPED_COMPATIBLE'
   comparisons.append({'offset':offset,'source_word':source,'source_group_id':r['source_group_id'],'cipher_word':code,'condition':condition,'compatible':condition in ('KNOWN_MATCH','UNMAPPED_COMPATIBLE')})
   cursor=nxt
  contradictions=[r for r in comparisons if not r['compatible']]
  status='CONTRADICTED' if contradictions else 'UNKNOWN_MEASUREMENT' if barrier else 'COMPATIBLE_NECESSARY_CONDITIONS'
  result[direction]={'requested_positions':len(pairs),'checked_positions':len(comparisons),'barrier':barrier,'comparisons':comparisons,'contradictions':contradictions,'status':status}
 statuses={r['status'] for r in result.values()}
 status='CONTRADICTED' if 'CONTRADICTED' in statuses else 'UNKNOWN_MEASUREMENT' if 'UNKNOWN_MEASUREMENT' in statuses else 'COMPATIBLE_NECESSARY_CONDITIONS'
 return {'schema':'GDT894_FIXED_SOURCE_ADJACENCY_RESULT_V1','status':status,'directions':result}

def main():
 destination=BASE/'artifacts/RESULT.json';assert not destination.exists(),'refusing overwrite'
 p=json.loads((BASE/'artifacts/PREDICTION.json').read_text());target=acquire();write(BASE/'artifacts/TARGET.json',target)
 result=evaluate(target['rows'],p)
 result.update(prediction_sha256=sha(BASE/'artifacts/PREDICTION.json'),target_sha256=sha(BASE/'artifacts/TARGET.json'),claim_ceiling='Literal RF transcription and exact continuous-copy law only. No confirmed meaning, independent held prediction, native certainty or refutation of paragraph-switching montage.')
 write(destination,result)
 print(json.dumps({'status':result['status'],'directions':{k:{q:r[q] for q in ('status','checked_positions','requested_positions','barrier')} for k,r in result['directions'].items()}}))
if __name__=='__main__':main()
