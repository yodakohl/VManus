#!/usr/bin/env python3
"""Independent enumeration of literal frames from guarded sources, plus replay."""
import csv, hashlib, importlib.util, json, re
from collections import Counter, defaultdict
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def main():
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 m=json.loads((R/'experiments/yolo/gdt1100_sy_genitive_closure/src/MODEL.json').read_text())
 allow=set(json.loads((R/m['allow_source']).read_text())['allowed_selectors']);assert len(allow)==179
 pagelines=defaultdict(list);allsy=set()
 for p in m['sources']:
  d=json.loads((R/p).read_text())
  for l in d['lines']:
   meta=l['metadata'];assert meta['page'] in allow and not meta['page'].startswith('f84') and meta['page']!='f116v'
   gs=[meta|dict(zip(d['group_columns'],x)) for x in l['groups']]
   allsy.update(g['source_group_id'] for g in gs if g['ivtff_group_raw']=='sy')
   if meta['kind']=='P':pagelines[meta['edition'],meta['page']].append((meta,gs))
 units={}
 for (ed,page),ls in pagelines.items():
  active=None
  for meta,gs in sorted(ls,key=lambda x:int(x[0]['source_row_index'])):
   if meta['paragraph_start']=='1':active=[]
   if active is not None:active.append((meta,gs))
   if meta['paragraph_end']=='1' and active is not None:
    nums=[int(x[0]['locus'].split('.')[-1]) for x in active]
    if all(nums[j]==nums[0]+j for j in range(len(nums))):
     uid=page+'|'+active[0][0]['locus']+'-'+active[-1][0]['locus'];units[ed,uid]=[g for _,xs in active for g in xs]
    active=None
 clear=set(m['clear_separators']);present=set();absent=set();pc=Counter();ac=Counter();pi=defaultdict(list);ai=defaultdict(list)
 for (ed,uid),gs in sorted(units.items()):
  for i in range(len(gs)):
   n=5 if gs[i]['ivtff_group_raw']=='sy' else 4
   if n==5:
    if i<2 or i+2>=len(gs):continue
    seq=gs[i-2:i+3];flank=seq[:2]+seq[3:]
   else:
    if i+4>len(gs):continue
    seq=gs[i:i+4];flank=seq
   if any(re.fullmatch('[a-z]+',g['ivtff_group_raw']) is None or g['ivtff_group_raw']=='sy' for g in flank):continue
   if any(seq[j]['right_separator'] not in clear or seq[j+1]['left_separator'] not in clear for j in range(len(seq)-1)):continue
   ids=','.join(g['source_group_id'] for g in seq);frame=' '.join(g['ivtff_group_raw'] for g in flank)
   if n==5:present.add((ed,uid,ids,frame));pc[ed]+=1;pi[ed,frame].append(ids)
   else:absent.add((ed,uid,ids,frame));ac[ed]+=1;ai[ed,frame].append(ids)
 def read(n):return list(csv.DictReader((E/'artifacts'/n).open(),delimiter='\t'))
 inv=read('SY_INVENTORY.tsv');assert {r['source_group_id'] for r in inv}==allsy and len(inv)==len(allsy)==88
 emitted=read('PRESENT_FRAMES.tsv');assert {(x['edition'],x['unit_id'],x['group_ids'],x['frame']) for x in emitted}==present
 pair_expected={(ed,frame,p,a) for (ed,frame),ps in pi.items() for p in ps for a in ai.get((ed,frame),[])}
 pairs=read('PAIRS.tsv');assert {(x['edition'],x['frame'],x['present_ids'],x['absent_ids']) for x in pairs}==pair_expected
 matches=read('MATCHING_ABSENT_FRAMES.tsv');assert {(x['edition'],x['unit_id'],x['group_ids'],x['frame']) for x in matches}=={x for x in absent if (x[0],x[3]) in pi}
 result=json.loads((E/'artifacts/RESULT.json').read_text())
 for ed in ['ZL3b','IT2a','RF1b']:
  rr=result['by_reader'][ed];assert rr['eligible_present']==pc[ed] and rr['eligible_absent']==ac[ed]
  assert rr['exact_sy']==sum(x.startswith(ed+'|') for x in allsy)
  assert rr['present_frames']==sum(k[0]==ed for k in pi)
  assert rr['present_recurrent_frames']==sum(k[0]==ed and len(v)>1 for k,v in pi.items())
  assert rr['absent_recurrent_frames']==sum(k[0]==ed and len(v)>1 for k,v in ai.items())
 spec=importlib.util.spec_from_file_location('replay',E/'src/run.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 for n,t in mod.build().items():assert (E/'artifacts'/n).read_text()==t,n
 v={'status':'PASS_INDEPENDENT_LITERAL_ENUMERATION_AND_BYTE_REPLAY','scope':'Bookkeeping and literal comparison capacity only; no semantic confirmation','exact_sy':len(allsy),'complete_units':dict(Counter(ed for ed,_ in units)),'eligible_present':dict(pc),'eligible_absent':dict(ac),'pairs':len(pairs)}
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
