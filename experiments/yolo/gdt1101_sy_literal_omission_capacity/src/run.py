#!/usr/bin/env python3
"""Literal whole-group insertion capacity; no decoder or meaning score."""
import csv, hashlib, importlib.util, io, json, re
from collections import Counter, defaultdict
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
P='experiments/yolo/gdt1100_sy_genitive_closure'
CLEAR={'DEFINITE_SPACE','LINE_START','LINE_END','DRAWING_INTERRUPTION'}
def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def table(rows,cols):
 s=io.StringIO();w=csv.DictWriter(s,cols,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue()
def good(gs):
 return all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) and g['ivtff_group_raw']!='sy' for g in gs)
def boundary(gs):return all(a['right_separator'] in CLEAR and b['left_separator'] in CLEAR for a,b in zip(gs,gs[1:]))
def event(ed,u,gs,has_sy):
 f=gs[:2]+gs[3:] if has_sy else gs
 return {'edition':ed,'unit_id':u['id'],'page':u['page'],'leaf':re.match(r'f(\d+)',u['page'])[1],
         'group_ids':','.join(g['source_group_id'] for g in gs),'loci':','.join(dict.fromkeys(g['locus'] for g in gs)),
         'frame':' '.join(g['ivtff_group_raw'] for g in f),'hand':gs[0]['hand'] if len({g['hand'] for g in gs})==1 else 'MIXED',
         'gap_right':gs[2 if has_sy else 1]['right_separator'],'boundaries':'|'.join(a['right_separator']+'/'+b['left_separator'] for a,b in zip(gs,gs[1:]))}
def build():
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 spec=importlib.util.spec_from_file_location('frozen1100',R/P/'src/run.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 old,units=mod.build();occ=list(csv.DictReader(io.StringIO(old['OCCURRENCES.tsv']),delimiter='\t'));byid={r['source_group_id']:r for r in occ}
 present=[];absent=[];inventory=[];reason=Counter();ready=set()
 for (ed,uid),u in sorted(units.items()):
  gs=[g for l in u['lines'] for g in l['groups']]
  for i,g in enumerate(gs):
   if g['ivtff_group_raw']!='sy':continue
   why=[]
   if i<2 or i+2>=len(gs):why.append('INSUFFICIENT_TWO_SIDED_FLANK')
   else:
    seq=gs[i-2:i+3];flanks=seq[:2]+seq[3:]
    if not good(flanks):why.append('NON_LITERAL_OR_SY_FLANK')
    if not boundary(seq):why.append('UNCERTAIN_INTERVENING_BOUNDARY')
    if not why:present.append(event(ed,u,seq,True));ready.add(g['source_group_id'])
   reason[g['source_group_id']]='|'.join(why) if why else 'READY'
  for i in range(len(gs)-3):
   seq=gs[i:i+4]
   if good(seq) and boundary(seq):absent.append(event(ed,u,seq,False))
 for r in occ:
  inventory.append({k:r[k] for k in ['source_group_id','edition','page','locus','unit_id','whole_line']}|{'status':reason.get(r['source_group_id'],'NO_COMPLETE_UNIT')})
 pi=defaultdict(list);ai=defaultdict(list)
 for e in present:pi[e['edition'],e['frame']].append(e)
 for e in absent:ai[e['edition'],e['frame']].append(e)
 pairs=[];matches=[];retained=set()
 for k,ps in sorted(pi.items()):
  for a in ai.get(k,[]):
   matches.append(a);retained.add((a['edition'],a['unit_id']))
   for p in ps:
    changed=(p['gap_right'] in {'LINE_END','DRAWING_INTERRUPTION'} and a['gap_right']=='DEFINITE_SPACE') or (a['gap_right'] in {'LINE_END','DRAWING_INTERRUPTION'} and p['gap_right']=='DEFINITE_SPACE')
    samehand=p['hand']==a['hand'] and p['hand'] not in {'','?','UNKNOWN','MIXED','-1'}
    pairs.append({'edition':k[0],'frame':k[1],'present_ids':p['group_ids'],'absent_ids':a['group_ids'],'present_unit':p['unit_id'],'absent_unit':a['unit_id'],'present_gap':p['gap_right'],'absent_gap':a['gap_right'],'different_leaf':p['leaf']!=a['leaf'],'changed_wrap':changed,'same_known_hand':samehand})
    retained.add((p['edition'],p['unit_id']))
 result={'experiment':'GDT1101','registered_utc':lock['registered_utc'],'by_reader':{ed:{'exact_sy':sum(r['edition']==ed for r in occ),'eligible_present':sum(p['edition']==ed for p in present),'eligible_absent':sum(a['edition']==ed for a in absent),'present_frames':sum(k[0]==ed for k in pi),'present_recurrent_frames':sum(k[0]==ed and len(v)>1 for k,v in pi.items()),'absent_recurrent_frames':sum(k[0]==ed and len(v)>1 for k,v in ai.items()),'contrast_pairs':sum(p['edition']==ed for p in pairs),'changed_wrap_different_leaf_same_hand_pairs':sum(p['edition']==ed and p['changed_wrap'] and p['different_leaf'] and p['same_known_hand'] for p in pairs),'statuses':dict(Counter(r['status'] for r in inventory if r['edition']==ed))} for ed in ['ZL3b','IT2a','RF1b']},'absent_ordered_sha256':hashlib.sha256(dump(absent).encode()).hexdigest(),'decision':'LITERAL_CONTRAST_AVAILABLE_UNSELECTED' if pairs else 'NO_LITERAL_SY_PRESENCE_ABSENCE_COMPARISON','confirmed_words':0,'independent_meaning_confirmation':0,'new_admissions':0,'significance_claim':False,'earlier_decisions_changed':False}
 ec=list(present[0]) if present else ['edition','unit_id','page','leaf','group_ids','loci','frame','hand','gap_right','boundaries']
 pc=['edition','frame','present_ids','absent_ids','present_unit','absent_unit','present_gap','absent_gap','different_leaf','changed_wrap','same_known_hand']
 return {'RESULT.json':dump(result),'SY_INVENTORY.tsv':table(inventory,list(inventory[0])),'PRESENT_FRAMES.tsv':table(present,ec),'MATCHING_ABSENT_FRAMES.tsv':table(matches,ec),'PAIRS.tsv':table(pairs,pc),'PAIRED_COMPLETE_UNITS.json':dump([units[k] for k in sorted(retained)])}
if __name__=='__main__':
 out=build()
 for n,t in out.items():(E/'artifacts'/n).write_text(t)
 print(out['RESULT.json'])
