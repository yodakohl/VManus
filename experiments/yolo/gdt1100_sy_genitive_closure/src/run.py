#!/usr/bin/env python3
"""Fixed written-operand capacity. No lexical decoding."""
import csv, hashlib, io, json, re
from collections import Counter, defaultdict
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(p):return json.loads((R/p).read_text())
def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def table(rows):
 s=io.StringIO();w=csv.DictWriter(s,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue()
def build():
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 m=json.loads((E/'src/MODEL.json').read_text());allow=set(read(m['allow_source'])['allowed_selectors'])
 assert len(allow)==179 and not any(p.startswith('f84') or p=='f116v' for p in allow)
 lines={}
 for p in m['sources']:
  d=read(p)
  for l in d['lines']:
   meta=l['metadata'];assert meta['page'] in allow and not meta['page'].startswith('f84')
   k=meta['edition'],meta['locus'];assert k not in lines
   gs=[meta|dict(zip(d['group_columns'],g)) for g in l['groups']]
   assert all(int(g['source_group_index'])==i+1 for i,g in enumerate(gs))
   lines[k]={'metadata':meta,'groups':gs}
 pages=defaultdict(list)
 for (ed,loc),l in lines.items():
  if l['metadata']['kind']=='P':pages[ed,l['metadata']['page']].append(l)
 units={};gu={}
 for (ed,page),ls in sorted(pages.items()):
  active=[]
  for l in sorted(ls,key=lambda x:int(x['metadata']['source_row_index'])):
   meta=l['metadata']
   if meta['paragraph_start']=='1':active=[]
   if meta['paragraph_start']=='1' or active:active.append(l)
   if meta['paragraph_end']=='1' and active:
    ns=[int(x['metadata']['locus'].rsplit('.',1)[1]) for x in active]
    if all(b==a+1 for a,b in zip(ns,ns[1:])):
     uid=page+'|'+active[0]['metadata']['locus']+'-'+active[-1]['metadata']['locus']
     units[ed,uid]={'edition':ed,'id':uid,'page':page,'lines':list(active)}
     flat=[g for x in active for g in x['groups']]
     for pos,g in enumerate(flat):gu[g['source_group_id']]=uid,pos,len(flat)
    active=[]
 occ=[];cases=[];retained={};matched=set()
 for (ed,loc),l in sorted(lines.items()):
  for g in l['groups']:
   if g['ivtff_group_raw']!='sy':continue
   binding=gu.get(g['source_group_id']);uid,pos,size=binding if binding else ('',None,None)
   clear=g['left_separator'] in m['clear_separators'] and g['right_separator'] in m['clear_separators']
   status='READY' if binding and clear else ('UNCERTAIN_WORD_BOUNDARY' if not clear else 'NO_COMPLETE_UNIT')
   row={k:g[k] for k in ['source_group_id','edition','page','locus','kind','source_group_index','source_group_count','left_separator','right_separator','paragraph_start','paragraph_end']}
   row.update(physical_leaf=re.match(r'f(\d+)',g['page'])[1],unit_id=uid,unit_position='' if pos is None else pos+1,unit_size='' if size is None else size,available_left='' if pos is None else pos,available_right='' if pos is None else size-pos-1,eligibility=status,exposure='SEED_EXPOSED' if g['page']=='f22r' else 'OTHER_EXPOSED',whole_line=' '.join(x['ivtff_group_raw'] for x in l['groups']))
   occ.append(row);retained[ed,loc]=l
   if binding:matched.add((ed,uid))
   for cid,c in m['candidates'].items():
    faults=[]
    if status=='READY':
     if c['left'] and pos==0:faults.append('NO_WRITTEN_LEFT_OPERAND')
     if c['right'] and pos==size-1:faults.append('NO_WRITTEN_RIGHT_OPERAND')
    outcome='NOT_TESTABLE' if status!='READY' else ('CONTRADICTION' if faults else 'CAPACITY_COMPATIBLE')
    cases.append(row|{'candidate':cid,'construction':c['construction'],'outcome':outcome,'contradiction':'|'.join(faults),'meaning_binding':'UNRESOLVED'})
 decisions={}
 for cid in m['candidates']:
  cc=[c for c in cases if c['candidate']==cid];bad=[c for c in cc if c['outcome']=='CONTRADICTION']
  decisions[cid]={'prediction':m['candidates'][cid],'by_reader':{ed:dict(Counter(c['outcome'] for c in cc if c['edition']==ed)) for ed in m['editions']},'contradiction_loci':sorted({c['locus'] for c in bad}),'contradiction_physical_leaves':sorted({c['physical_leaf'] for c in bad},key=int),'decision':'REJECT_FIXED_PACKAGE' if bad else 'NO_SURFACE_REFUTATION_NOT_SELECTED','independent_meaning_confirmation':0}
 result={'experiment':'GDT1100','registered_utc':lock['registered_utc'],'counts':{ed:sum(r['edition']==ed for r in occ) for ed in m['editions']},'source_groups':sum(len(l['groups']) for l in lines.values()),'loci':len({r['locus'] for r in occ}),'physical_leaves':len({r['physical_leaf'] for r in occ}),'eligibility_by_reader':{ed:dict(Counter(r['eligibility'] for r in occ if r['edition']==ed)) for ed in m['editions']},'complete_units_by_reader':{ed:sum(k[0]==ed for k in units) for ed in m['editions']},'candidates':decisions,'confirmed_words':0,'independent_meaning_tests':0,'independent_confirmation_leaves':0,'new_admissions':0,'significance_claim':False,'old_AS_changed':False}
 records={'lines':list(retained.values()),'complete_units':[units[k] for k in sorted(matched)]}
 return {'RESULT.json':dump(result),'OCCURRENCES.tsv':table(occ),'CANDIDATE_CASES.tsv':table(cases),'RETAINED_SOURCE.json':dump(records)},units
if __name__=='__main__':
 out,_=build()
 for name,text in out.items():(E/'artifacts'/name).write_text(text)
 result=json.loads(out['RESULT.json']);print(json.dumps({k:result[k] for k in ['experiment','counts','loci','physical_leaves','candidates']},ensure_ascii=False))
