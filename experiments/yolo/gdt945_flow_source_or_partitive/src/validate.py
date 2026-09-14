#!/usr/bin/env python3
"""Independent source census and conditional-consequence validation, not meaning proof."""
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
   meta=l['metadata'];assert meta['page'] in allow;k=meta['edition'],meta['locus'];assert k not in lines
   rr=[meta|dict(zip(d['group_columns'],g)) for g in l['groups']];lines[k]=rr
   for r in rr:assert r['source_group_id'] not in source;source[r['source_group_id']]=r
 assert len(source)==96184
 base=read(R/m['base_lexicons']);lex=read(E/'artifacts/LEXICONS.json');assert len(base)==16 and len(lex)==32
 for cid,lx in lex.items():
  bid,v=cid.rsplit('_',1);b=base[bid];assert len(b)==50 and len(lx)==56
  assert {w:lx[w] for w in b}==b
  assert {w:g for w,g in lx.items() if w not in b}==m['shared_new']|m['variants'][v]
  assert 's' not in lx
 new=set(m['shared_new'])|{'qoker'};expected={k:r for k,r in source.items() if r['ivtff_group_raw'] in new};occ=tab('NEW_OCCURRENCES.tsv')
 assert len(occ)==len(expected)==1176 and {r['source_group_id'] for r in occ}==set(expected)
 for r in occ:
  for k,v in r.items():assert v==str(expected[r['source_group_id']][k])
 def unpack(kind):
  result={}
  for ed in ['ZL3b','IT2a','RF1b']:
   for p in read(E/f'artifacts/{kind}_SOURCE_{ed}.json'):
    k=ed,p['locus'];assert p['edition']==ed and k not in result
    rr=[dict(zip(p['columns'],g)) for g in p['groups']];assert rr==lines[k];result[k]=rr
  return result
 target=unpack('TARGET');assert set(target)=={(r['edition'],r['locus']) for r in expected.values()} and len(target)==1017
 contexts=read(E/'artifacts/CONTEXT_PARAGRAPHS.json');assert contexts==read(R/m['old_context_paragraphs'])
 pp=read(R/m['paragraph_source']);ck=set()
 for p in contexts:
  assert {k:v for k,v in p.items() if k!='edition'} in pp[p['edition']]
  for l in p['lines']:
   assert l['source_ids']==[r['source_group_id'] for r in lines[p['edition'],l['locus']]]
   ck|={(p['edition'],l['locus']),('RF1b',l['locus'])}
 context=unpack('CONTEXT');assert set(context)==ck and sum(map(len,context.values()))==1553
 for ed in ['ZL3b','IT2a','RF1b']:assert all((ed,'f80v.'+str(n)) in ck for n in range(30,38))
 cases=tab('RELATION_CASES.tsv');bykey={(r['candidate'],r['relation_id']):r for r in cases};relations=[r for r in source.values() if r['ivtff_group_raw'] in ['qoker','qokey']];assert len(cases)==len(bykey)==len(lex)*len(relations)==9024
 expected_states={}
 for cid,lx in lex.items():
  states=[]
  for rel in relations:
   rr=lines[rel['edition'],rel['locus']];i=next(i for i,r in enumerate(rr) if r['source_group_id']==rel['source_group_id']);nxt=rr[i+1] if i+1<len(rr) else None
   case=bykey[cid,rel['source_group_id']];assert case['relation']==rel['ivtff_group_raw']
   assert case['next_id']==(nxt['source_group_id'] if nxt else '')
   valid=nxt is not None and nxt['left_separator']=='DEFINITE_SPACE' and rel['right_separator']=='DEFINITE_SPACE'
   role=lx.get(nxt['ivtff_group_raw'],['','UNREAD'])[1] if nxt else 'NO_FOLLOWING_GROUP'
   assert case['next_role']==role
   permitted=set(m['goal_roles'] if rel['ivtff_group_raw']=='qokey' else m['nominal_roles'])
   status='NOT_TESTABLE' if not valid else 'UNBOUND' if role=='UNREAD' else 'COMPATIBLE' if role in permitted else 'CONTRADICTION'
   assert case['status']==status and case['eligible']==str(valid);states.append(status)
  expected_states[cid]=Counter(states)
 assert all(c==Counter(COMPATIBLE=21,CONTRADICTION=43,UNBOUND=197,NOT_TESTABLE=21) for c in expected_states.values())
 decisions=tab('CANDIDATE_DECISIONS.tsv');assert len(decisions)==32
 for d in decisions:
  for s,n in expected_states[d['candidate']].items():assert int(d[s])==n
  assert d['decision']=='STRICT_PACKAGE_REJECTED' and d['contradiction_loci']=='16' and d['independent_meaning_tests']==d['unexposed_confirmation_leaves']=='0'
 groups=read(E/'artifacts/OBSERVATIONAL_GROUPS.json');assert len(groups)==1 and set(groups[0]['candidates'])==set(lex)
 allframes=[]
 for (ed,locus),rr in lines.items():
  for i in range(len(rr)-1):
   if [r['ivtff_group_raw'] for r in rr[i:i+2]]==['qokeedy','qoker']:allframes.append((ed,locus,rr[i:i+4]))
 assert len(allframes)==3 and all(l=='f80v.33' for ed,l,rr in allframes)
 frames=tab('FLOW_FRAME_CASES.tsv');assert len(frames)==96 and all(r['status']=='COMPATIBLE' for r in frames)
 for r in frames:
  rr=next(rr for ed,l,rr in allframes if ed==r['edition'] and l==r['locus']);assert r['source_ids']=='|'.join(x['source_group_id'] for x in rr)
 local=tab('LOCAL_ALIGNMENT.tsv');assert len(local)==32*3*8
 for c in local:
  src=source[c['source_id']];assert c['raw']==src['ivtff_group_raw'] and [c['gloss'],c['role']]==lex[c['candidate']][c['raw']]
 result=read(E/'artifacts/RESULT.json');assert result['confirmed_words']==result['independent_meaning_tests']==result['new_admissions']==0 and result['significance_claim'] is False
 from run import build
 regenerated=build()
 for name,content in regenerated.items():assert (E/'artifacts'/name).read_text()==content,name
 out={'experiment':'GDT945','status':'PASS','checks':['frozen input and protocol hashes','179-selector boundary','independent 96184-group and 1176-hit census','unchanged 50-word base and exactly six additions per candidate','all 9024 immediate-complement candidate cases independently assessed','whole target lines and six retained paragraphs, all f80v30–37','all 32 strict packages rejected by 16 loci','one observational outcome group, no semantic equivalence inferred','raw seed alignment and all flow-frame occurrences','deterministic artifact replay'],'meaning_validation':False,'new_data_access':False}
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
