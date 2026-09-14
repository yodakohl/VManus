#!/usr/bin/env python3
"""Separate census/coverage/phrase audit; no semantic-truth validation."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2]
def read(p):return json.loads(p.read_text())
def table(n):return list(csv.DictReader((EXP/'artifacts'/n).open(),delimiter='\t'))
def main():
 lock=read(EXP/'PREREG_LOCK.json')
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 m=read(EXP/'src/MODEL.json');allow=set(read(ROOT/m['allow_source'])['allowed_selectors'])
 assert len(allow)==179 and not any(x.startswith('f84') or x=='f116v' for x in allow)
 lines={};source={}
 for p in m['sources']:
  d=read(ROOT/p)
  for line in d['lines']:
   meta=line['metadata'];assert meta['page'] in allow
   rr=[meta|dict(zip(d['group_columns'],g)) for g in line['groups']];key=meta['edition'],meta['locus'];assert key not in lines;lines[key]=rr
   for r in rr:assert r['source_group_id'] not in source;source[r['source_group_id']]=r
 assert len(source)==96184
 base=read(ROOT/m['base_lexicons']);lex=read(EXP/'artifacts/LEXICONS.json');assert len(lex)==16
 for cid,lx in lex.items():
  b=base[cid.rsplit('_',1)[0]];assert len(b)==41 and len(lx)==50
  assert all(lx[w]==g for w,g in b.items())
  assert {w:g for w,g in lx.items() if w not in b}==m['shared_new']|m['event_variants'][cid[-1]]
  assert 's' not in lx and 'she@152;y' not in lx
 new=set(m['shared_new'])|set(m['event_variants']['F']);assert len(new)==9
 expected={i:r for i,r in source.items() if r['ivtff_group_raw'] in new}
 occ=table('NEW_OCCURRENCES.tsv');assert len(occ)==len(expected)==1751 and {r['source_group_id'] for r in occ}==set(expected)
 for r in occ:
  src=expected[r['source_group_id']]
  for k in ['edition','page','locus','source_group_index','ivtff_group_raw','left_separator','right_separator']:assert r[k]==src[k]
  for ev in ['F','S']:assert (r[ev+'_gloss'],r[ev+'_role'])==tuple(lex['R_C_REL_'+ev][r['ivtff_group_raw']])
 allbridges=[];markers=set()
 for (ed,locus),rr in lines.items():
  for i,r in enumerate(rr):
   for b in m['phrase_bridges']:
    spans=[]
    if r['ivtff_group_raw']==b['whole']:spans.append(('WHOLE',i+1,True))
    if i+1<len(rr) and [x['ivtff_group_raw'] for x in rr[i:i+2]]==b['parts']:
     valid=rr[i]['right_separator']==rr[i+1]['left_separator'] and rr[i]['right_separator'] in m['bridge_boundaries'];spans.append(('SPLIT',i+2,valid))
    for form,end,valid in spans:
     ids='|'.join(x['source_group_id'] for x in rr[i:end]);allbridges.append((b['name'],form,ed,locus,ids,str(i),str(end),str(valid)))
     if b['name']=='CONTENT' and form=='SPLIT' and valid:markers.add(r['source_group_id'])
 bridges=table('BRIDGE_CASES.tsv');cols=['bridge','form','edition','locus','source_ids','start','end','eligible']
 assert sorted(tuple(r[c] for c in cols) for r in bridges)==sorted(allbridges)
 assert len(bridges)==12 and markers=={'ZL3b|f80v.32|G001'}
 def unpack(kind):
  out={}
  for ed in ['ZL3b','IT2a','RF1b']:
   for p in read(EXP/f'artifacts/{kind}_SOURCE_{ed}.json'):
    key=p['edition'],p['locus'];assert key not in out
    rr=[dict(zip(p['columns'],g)) for g in p['groups']];assert rr==lines[key];out[key]=rr
  return out
 target=unpack('TARGET');assert set(target)=={(r['edition'],r['locus']) for r in expected.values()}|{(r['edition'],r['locus']) for r in bridges}
 pp=read(ROOT/m['paragraph_source']);contexts=read(EXP/'artifacts/CONTEXT_PARAGRAPHS.json')
 assert len(contexts)==6
 contextkeys=set()
 for p in contexts:
  original=[z for z in pp[p['edition']] if z['id']==p['id']];assert len(original)==1 and {k:v for k,v in p.items() if k!='edition'}==original[0]
  for l in p['lines']:
   assert l['source_ids']==[r['source_group_id'] for r in lines[p['edition'],l['locus']]]
   contextkeys|={(p['edition'],l['locus']),('RF1b',l['locus'])}
 context=unpack('CONTEXT');assert set(context)==contextkeys and sum(map(len,context.values()))==1553
 assert context['ZL3b','f80v.32'][0]['ivtff_group_raw']=='s'
 assert context['RF1b','f80v.32'][-1]['ivtff_group_raw']=='she@152;y'
 local=table('LOCAL_ALIGNMENT.tsv');assert len(local)==16*(9+9+8)
 seen=set()
 for r in local:
  pair=r['candidate'],r['source_id'];assert pair not in seen;seen.add(pair)
  src=source[r['source_id']];assert src['locus']=='f80v.32'
  assert r['raw']==src['ivtff_group_raw']
  lx=lex[r['candidate']];g,role=lx.get(r['raw'],['⟦'+r['raw']+'⟧','UNREAD'])
  assert r['literal_gloss']==g and r['lexical_role']==role
  assert bool(r['bridge_role'])==(r['source_id'] in markers)
  assert r['left_separator']==src['left_separator'] and r['right_separator']==src['right_separator']
 lc=table('LOCAL_CASES.tsv');assert len(lc)==48
 for r in lc:
  ed=r['edition'];expected_counts={'ZL3b':(9,8,1,1,0),'IT2a':(9,9,0,0,0),'RF1b':(8,7,0,1,1)}[ed]
  assert tuple(int(r[k]) for k in ['groups','lexical_hypothesis_groups','structural_phrase_groups','unread_without_bridge','unread_with_bridge'])==expected_counts
  assert r['unread_raw']==('she@152;y' if ed=='RF1b' else '')
 cases=table('PASSIVE_CASES.tsv');assert len(cases)==48
 kernel={b['source_ids']:b for b in bridges if b['bridge']=='PASSIVE' and b['eligible']=='True'};assert len(kernel)==3
 assert {(r['candidate'],r['event_ids']) for r in cases}=={(cid,k) for cid in lex for k in kernel}
 expected_mentions=[]
 for c in cases:
  b=kernel[c['event_ids']];rr=lines[b['edition'],b['locus']];end=int(b['end']);tail=rr[end:end+3];lx=lex[c['candidate']]
  assert c['tail_ids']=='|'.join(r['source_group_id'] for r in tail)
  assert [r['ivtff_group_raw'] for r in tail[:2]]==['olky','qolkain']
  assert all(r['left_separator']==rr[end+j-1]['right_separator']=='DEFINITE_SPACE' for j,r in enumerate(tail))
  if b['edition']=='RF1b':
   assert c['status']=='PRODUCT_UNREAD_OR_WRONG_ROLE' and c['product_id']==''
  else:
   assert c['status']=='SOURCE_PRODUCT_BOUND_HYPOTHETICALLY' and c['product_raw']=='shedy'
   ed=b['edition'];par=[p for p in contexts if p['edition']==ed and any(l['locus']==b['locus'] for l in p['lines'])][0]
   seq=[r for l in par['lines'] for r in lines[ed,l['locus']]];idx=next(i for i,r in enumerate(seq) if r['source_group_id']==c['product_id'])
   before=[r['source_group_id'] for r in seq[:idx] if r['ivtff_group_raw']=='shedy'];after=[r['source_group_id'] for r in seq[idx+1:] if r['ivtff_group_raw']=='shedy']
   assert before==[] and after==[f'{ed}|f80v.36|G009']
   assert c['earlier_same_word']=='' and c['later_same_word']==after[0]
   expected_mentions.append((c['candidate'],c['event_ids'],c['product_id'],after[0]))
  assert c['product_identity_status']=='UNRESOLVED' and c['meaning_selected']=='False'
 actual_mentions=table('PRODUCT_MENTIONS.tsv');assert len(actual_mentions)==32
 assert sorted((r['candidate'],r['event_ids'],r['product_id'],r['mention_id']) for r in actual_mentions)==sorted(expected_mentions)
 for r in actual_mentions:assert r['direction']=='AFTER' and r['identity_status']=='SAME_SPELLING_NOT_IDENTIFIED_AS_SAME_PORTION'
 decisions=table('CANDIDATE_DECISIONS.tsv');assert len(decisions)==16
 for r in decisions:
  assert r['passive_candidates']=='3' and r['source_product_bound']=='2' and r['bound_loci']=='1' and r['other_bound_loci']=='0'
  assert r['identified_prior_product']==r['identified_later_product']==r['independent_meaning_tests']==r['unexposed_confirmation_leaves']=='0'
 result=read(EXP/'artifacts/RESULT.json')
 for cid,eds in result['context_coverage'].items():
  for ed,v in eds.items():
   rr=[r for (e,l),ss in context.items() if e==ed for r in ss];lx=lex[cid]
   assert v==dict(groups=len(rr),lexical_hypothesis=sum(r['ivtff_group_raw'] in lx for r in rr),structural_only=sum(r['source_group_id'] in markers for r in rr),unread=sum(r['ivtff_group_raw'] not in lx and r['source_group_id'] not in markers for r in rr))
 assert result['confirmed_words']==0 and not result['significance_claim'] and result['new_admissions']==0
 assert result['semantic_equivalence_is_stipulated']
 for p in (EXP/'artifacts').iterdir():
  if p.is_file():assert p.stat().st_size<=5000000,p
 out=dict(status='PASS',frozen_hashes=len(lock['files']),source_groups=len(source),new_occurrences=len(occ),bridge_cases=len(bridges),complete_target_lines=len(target),context_groups=1553,local_alignment_rows=len(local),passive_cases=len(cases),product_mention_rows=len(actual_mentions),old_values_unchanged=41,new_whole_values=9,structural_marker_not_translated=True,meaning_validated=False,coverage='Independent source census, all fixed phrases/slots/mentions, complete inherited paragraphs and unchanged lexical values; not independent meaning or a whole-search control.')
 (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
