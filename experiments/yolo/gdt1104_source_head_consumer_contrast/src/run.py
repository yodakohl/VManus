#!/usr/bin/env python3
"""Frozen written-head obligation; no semantic decoder or noun classifier."""
import csv, hashlib, io, json, subprocess
from collections import Counter, defaultdict
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in BASE.parents if (p/'AGENTS.md').is_file())
SOURCE=ROOT/'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
ALLOW=ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
COLS='source_group_id,edition,page,locus,kind,code,grammar_scope,source_row_index,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw'
def dump(x):return json.dumps(x,indent=2,ensure_ascii=False)+'\n'
def tab(rs):
 out=io.StringIO();w=csv.DictWriter(out,list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs);return out.getvalue()
def build():
 lock=json.loads((BASE/'PREREG_LOCK.json').read_text())
 for path,h in lock['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 model=json.loads((BASE/'src/MODEL.json').read_text())
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0'
 allowed={r['page'] for r in csv.DictReader(ALLOW.open(),delimiter='\t')}
 assert set(model['pages'])<=allowed and not any(p.startswith('f84') or p=='f116v' for p in model['pages'])
 cmd=[str(ROOT/'vmanus-exp'),'query-tsv',str(SOURCE),'--selector','page','--columns',COLS]
 for p in model['pages']:cmd+=['--allow',p]
 raw=subprocess.check_output(cmd,text=True)
 rows=list(csv.DictReader(io.StringIO(raw),delimiter='\t'))
 lines=defaultdict(list)
 for r in rows:
  assert r['page'] in model['pages'];lines[(r['edition'],r['page'],r['locus'])].append(r)
 for rs in lines.values():
  rs.sort(key=lambda r:int(r['source_group_index']))
  assert [int(r['source_group_index']) for r in rs]==list(range(1,len(rs)+1))
  assert all(int(r['source_group_count'])==len(rs) for r in rs)
 pages=defaultdict(list)
 for key,rs in lines.items():
  if rs[0]['kind']=='P':pages[key[:2]].append(rs)
 units={};bindings={}
 for (ed,page),ls in sorted(pages.items()):
  active=[]
  for rs in sorted(ls,key=lambda x:int(x[0]['source_row_index'])):
   if rs[0]['paragraph_start']=='1':active=[]
   if rs[0]['paragraph_start']=='1' or active:active.append(rs)
   if rs[0]['paragraph_end']=='1' and active:
    ns=[int(x[0]['locus'].rsplit('.',1)[1]) for x in active]
    if all(b==a+1 for a,b in zip(ns,ns[1:])):
     uid=ed+'|'+page+'|'+active[0][0]['locus']+'-'+active[-1][0]['locus']
     flat=[r for line in active for r in line];units[uid]={'id':uid,'edition':ed,'page':page,'lines':active,'groups':flat}
     for i,r in enumerate(flat):bindings[r['source_group_id']]=(uid,i)
    active=[]
 cases=[];occ=[];excluded=[];retain=set()
 for key,rs in sorted(lines.items()):
  for r in rs:
   if r['ivtff_group_raw'] not in model['selectors']:continue
   if r['kind']!='P':excluded.append(r);continue
   b=bindings.get(r['source_group_id']);uid,pos=b if b else ('',None)
   flat=units[uid]['groups'] if b else []
   form=r['ivtff_group_raw'];derived=form!='s'
   if b:retain.add(uid)
   item={k:r[k] for k in ('source_group_id','edition','page','locus','source_group_index','ivtff_group_raw')}
   item.update(unit_id=uid,unit_position='' if pos is None else pos+1,available_right='' if pos is None else len(flat)-pos-1,whole_line=' '.join(x['ivtff_group_raw'] for x in rs))
   occ.append(item)
   for cid,c in model['candidates'].items():
    need=c['derived_right'] if derived else c['free_s_right']
    right=flat[pos+1:pos+1+need] if b else []
    outcome='NOT_TESTABLE' if not b else ('CAPACITY_COMPATIBLE' if len(right)==need else 'CONTRADICTION')
    cases.append(item|{'candidate':cid,'required_right':need,'right_ids':'|'.join(x['source_group_id'] for x in right),'right_raw':'|'.join(x['ivtff_group_raw'] for x in right),'outcome':outcome,'meaning_binding':'UNRESOLVED'})
 result={'experiment':'GDT1104','status':'FIXED_CAPACITY_NOT_MEANING','registered_utc':lock['registered_utc'],'queried_groups':len(rows),'native_units_by_reader':{e:sum(u['edition']==e for u in units.values()) for e in model['editions']},'occurrences_by_reader':{e:sum(o['edition']==e for o in occ) for e in model['editions']},'physical_loci':len({o['locus'] for o in occ}),'physical_leaves':len({o['page'] for o in occ}),'excluded_nonprose':len(excluded),'candidates':{},'confirmed_words':0,'independent_confirmation_leaves':0,'significance_claim':False}
 for cid in model['candidates']:
  cs=[c for c in cases if c['candidate']==cid];bad=[c for c in cs if c['outcome']=='CONTRADICTION']
  result['candidates'][cid]={'by_reader':{e:dict(Counter(c['outcome'] for c in cs if c['edition']==e)) for e in model['editions']},'contradictions':bad,'decision':'REJECT_FIXED_PACKAGE' if bad else 'NO_SURFACE_REFUTATION_MEANING_UNSELECTED'}
 retained={'projected_rows':rows,'matched_native_units':[units[u] for u in sorted(retain)],'nonprose_matches':excluded}
 md=['# All matching native lines','No assigned meaning; all cases retained.']
 for o in occ:md+=['',o['edition']+' '+o['locus']+' G'+o['source_group_index'],'`'+o['whole_line']+'`']
 for uid in sorted(retain):
  u=units[uid];md+=['','## Complete native unit '+uid]
  for line in u['lines']:md.append(line[0]['locus']+'  '+' '.join(r['ivtff_group_raw'] for r in line))
 return {'RESULT.json':dump(result),'OCCURRENCES.tsv':tab(occ),'CANDIDATE_CASES.tsv':tab(cases),'RETAINED_SOURCE.json':dump(retained),'COMPLETE_CONTEXTS.md':'\n'.join(md)+'\n'}
if __name__=='__main__':
 out=build()
 for n,s in out.items():(BASE/'artifacts'/n).write_text(s)
 print(out['RESULT.json'])
