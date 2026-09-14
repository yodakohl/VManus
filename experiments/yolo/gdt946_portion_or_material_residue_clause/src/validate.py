#!/usr/bin/env python3
"""Separate raw-source and registered/post-census consequence audit."""
import csv,hashlib,json
from pathlib import Path
from collections import Counter
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(p):return json.loads(p.read_text())
def tab(n):return list(csv.DictReader((E/'artifacts'/n).open(),delimiter='\t'))
def main():
 lock=read(E/'PREREG_LOCK.json')
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 m=read(E/'src/MODEL.json');allow=set(read(R/m['allow_source'])['allowed_selectors']);assert len(allow)==179 and not any(x.startswith('f84') or x=='f116v' for x in allow)
 lines={};source={}
 for p in m['sources']:
  d=read(R/p)
  for l in d['lines']:
   meta=l['metadata'];assert meta['page'] in allow;k=meta['edition'],meta['locus'];assert k not in lines;rr=[meta|dict(zip(d['group_columns'],g)) for g in l['groups']];lines[k]=rr
   for r in rr:assert r['source_group_id'] not in source;source[r['source_group_id']]=r
 assert len(source)==96184
 base=read(R/m['base_lexicons']);lex=read(E/'artifacts/LEXICONS.json');assert len(base)==16 and len(lex)==32
 for cid,lx in lex.items():
  bid,v=cid.rsplit('_',1);b=base[bid];assert len(b)==50 and len(lx)==58 and {w:lx[w] for w in b}==b
  assert {w:g for w,g in lx.items() if w not in b}==m['shared_new']|m['variants'][v]
  assert not {'qoker','qokey','qokeey','tchcthy','lom','s'}&set(lx)
 new=set(m['shared_new'])|{'olshedy','olal'};expected={k:r for k,r in source.items() if r['ivtff_group_raw'] in new};occ=tab('NEW_OCCURRENCES.tsv');assert len(occ)==len(expected)==2048 and {r['source_group_id'] for r in occ}==set(expected)
 for r in occ:
  for k,v in r.items():assert v==str(expected[r['source_group_id']][k])
 def unpack(kind):
  out={}
  for ed in ['ZL3b','IT2a','RF1b']:
   for p in read(E/f'artifacts/{kind}_SOURCE_{ed}.json'):
    k=p['edition'],p['locus'];assert k[0]==ed and k not in out;rr=[dict(zip(p['columns'],g)) for g in p['groups']];assert rr==lines[k];out[k]=rr
  return out
 target=unpack('TARGET');loci={r['locus'] for r in expected.values()};assert len(loci)==680 and set(target)=={k for k in lines if k[1] in loci} and len(target)==2039
 tc=tab('TARGET_READER_COVERAGE.tsv');assert len(tc)==680*3
 assert [(r['edition'],r['locus']) for r in tc if r['status']=='SOURCE_LINE_ABSENT']==[('IT2a','f106r.29')]
 pp=read(R/m['paragraph_source']);contexts=read(E/'artifacts/CONTEXT_PARAGRAPHS.json');pc=tab('PARAGRAPH_COVERAGE.tsv');cloci={r['locus'] for r in expected.values() if r['ivtff_group_raw'] in ['olshedy','olal']}|set(m['focus_loci']);wanted={(p['edition'],p['id']) for p in read(R/m['old_context_paragraphs'])}
 for ed in ['ZL3b','IT2a']:
  for p in pp[ed]:
   if any(l['locus'] in cloci for l in p['lines']):wanted.add((ed,p['id']))
 assert len(contexts)==46 and {(p['edition'],p['id']) for p in contexts}==wanted
 ck=set()
 for p in contexts:
  assert {k:v for k,v in p.items() if k!='edition'} in pp[p['edition']]
  for l in p['lines']:
   assert l['words']==[r['ivtff_group_raw'] for r in lines[p['edition'],l['locus']]];ck|={(p['edition'],l['locus']),('RF1b',l['locus'])}
 assert set(unpack('CONTEXT'))==ck and sum(len(lines[k]) for k in ck)==6235
 assert all(r['status']=='COMPLETE_PARAGRAPH' for r in pc)
 relations=[r for r in source.values() if r['ivtff_group_raw']=='olal'];assert len(relations)==16
 cases=tab('RELATION_CASES.tsv');audit=tab('KNOWN_SIDE_AUDIT.tsv');cases_by={(c['candidate'],c['relation_id']):c for c in cases};audit_by={(c['candidate'],c['relation_id']):c for c in audit};assert len(cases)==len(cases_by)==len(audit)==len(audit_by)==512
 for cid,lx in lex.items():
  states=[];astates=[]
  for rel in relations:
   rr=lines[rel['edition'],rel['locus']];i=next(i for i,r in enumerate(rr) if r['source_group_id']==rel['source_group_id']);a=rr[i-1] if i else None;b=rr[i+1] if i+1<len(rr) else None
   eligible=bool(a and b) and a['right_separator']==rel['left_separator']==rel['right_separator']==b['left_separator']=='DEFINITE_SPACE'
   roles=[lx.get(t['ivtff_group_raw'],['','UNREAD'])[1] if t else 'MISSING' for t in [a,b]];allowed=[{'QUANTITY_PART'} if cid.endswith('_P') else set(m['material_roles']),set(m['material_roles'])]
   wrong=[side for side,role,ok in zip(['LEFT','RIGHT'],roles,allowed) if role not in ['UNREAD','MISSING'] and role not in ok]
   registered='NOT_TESTABLE' if not eligible else 'UNBOUND' if 'UNREAD' in roles else 'CONTRADICTION' if wrong else 'COMPATIBLE'
   audited='NOT_TESTABLE' if not eligible else 'KNOWN_SIDE_CONTRADICTION' if wrong else 'UNBOUND' if 'UNREAD' in roles else 'COMPATIBLE'
   c=cases_by[cid,rel['source_group_id']];d=audit_by[cid,rel['source_group_id']]
   assert [c['left_role'],c['right_role']]==roles and c['eligible']==str(eligible) and c['status']==registered and d['registered_status']==registered and d['audit_status']==audited
   assert c['left_id']==(a['source_group_id'] if a else '') and c['right_id']==(b['source_group_id'] if b else '')
   states.append(registered);astates.append(audited)
  assert Counter(states)==Counter(COMPATIBLE=2,UNBOUND=9,NOT_TESTABLE=5)
  assert Counter(astates)==Counter(COMPATIBLE=2,KNOWN_SIDE_CONTRADICTION=7,UNBOUND=2,NOT_TESTABLE=5)
 decisions=tab('CANDIDATE_DECISIONS.tsv');assert len(decisions)==32
 for d in decisions:assert d['registered_decision']=='PORTION_MATERIAL_UNSELECTED' and d['final_decision']=='FIXED_TYPED_PACKAGE_REJECTED_POST_CENSUS_AUDIT' and d['known_side_contradictions']=='7' and d['known_side_contradiction_loci']=='f107r.21|f108r.43|f113v.22'
 fp=[];ap=[]
 for k,rr in lines.items():
  for i in range(len(rr)):
   if [r['ivtff_group_raw'] for r in rr[i:i+2]]==['olshedy','qokeedy']:fp.append((k,rr[i]['source_group_id'],rr[i+1]['source_group_id']))
   if [r['ivtff_group_raw'] for r in rr[i:i+3]]==['ol','shey','daly']:ap.append((k,'|'.join(x['source_group_id'] for x in rr[i:i+3])))
 assert len(fp)==4 and len(ap)==2 and len(tab('FLOW_CASES.tsv'))==128 and len(tab('AFTER_EVENT_CASES.tsv'))==2
 for r in tab('FLOW_CASES.tsv'):assert ((r['edition'],r['locus']),r['participant_id'],r['flow_id']) in fp
 for r in tab('AFTER_EVENT_CASES.tsv'):assert ((r['edition'],r['locus']),r['source_ids']) in ap
 for c in tab('LOCAL_ALIGNMENT.tsv'):
  src=source[c['source_id']];assert c['raw']==src['ivtff_group_raw'];assert [c['gloss'],c['role']]==lex[c['candidate']].get(c['raw'],['UNREAD','UNREAD'])
 groups=read(E/'artifacts/OBSERVATIONAL_GROUPS.json');assert len(groups)==1 and set(groups[0]['candidates'])==set(lex)
 d=read(E/'artifacts/RESULT.json');assert d['confirmed_words']==d['new_admissions']==d['unexposed_confirmation_leaves']==d['independent_meaning_tests']==0 and d['significance_claim'] is False
 from run import build
 for n,v in build().items():assert (E/'artifacts'/n).read_text()==v,n
 result={'experiment':'GDT946','status':'PASS','checks':['frozen protocol/input hashes and179selector bounds','96184source groups,2048exact hits and all680locus reader variants','sole absent target source variant IT2a f106r29 disclosed','50old values unchanged,exactly8new values for32candidates','all512registered relation cases independently checked','all512post-census known-side audits checked separately','all flow/after-event cases retained','46complete paragraphs and6235context groups','source alignment preserves RF unread entities and ZL uncertain boundary','deterministic replay'],'meaning_validation':False,'post_census_correction_disclosed':True}
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
