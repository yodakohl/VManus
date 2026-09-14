#!/usr/bin/env python3
"""Fixed portion/material hypotheses with full source context and finite cases."""
import csv,hashlib,io,json,re
from pathlib import Path
from collections import Counter,defaultdict
E=Path(__file__).resolve().parents[1];R=E.parents[2];EDS=['ZL3b','IT2a','RF1b']
def read(p):return json.loads((R/p).read_text())
def dump(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n'
def table(rows,fields=None):
 s=io.StringIO();w=csv.DictWriter(s,fields or list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue()
def leaf(p):return re.match(r'f(\d+)',p)[1]
def order(k):return EDS.index(k[0]),int(leaf(k[1])),k[1].split('.')[0],int(k[1].split('.')[1])
def definite(rr):return all(a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(rr,rr[1:]))
def join(rr,fn):
 sep={'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // '}
 return ''.join(('' if i==0 else sep.get(r['left_separator'],' ⟪'+r['left_separator']+'⟫ '))+fn(r) for i,r in enumerate(rr))
def build():
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 m=json.loads((E/'src/MODEL.json').read_text());allow=set(read(m['allow_source'])['allowed_selectors']);assert len(allow)==179 and not any(p.startswith('f84') or p=='f116v' for p in allow)
 lines={}
 for p in m['sources']:
  d=read(p)
  for l in d['lines']:
   meta=l['metadata'];assert meta['page'] in allow;k=meta['edition'],meta['locus'];assert k not in lines;lines[k]=[meta|dict(zip(d['group_columns'],g)) for g in l['groups']]
 base=read(m['base_lexicons']);lex={cid+'_'+v:b|m['shared_new']|n for cid,b in base.items() for v,n in m['variants'].items()};new=set(m['shared_new'])|{'olshedy','olal'}
 hits=[r for rr in lines.values() for r in rr if r['ivtff_group_raw'] in new];targetloci={r['locus'] for r in hits};targetkeys={k for k in lines if k[1] in targetloci};occ=[{k:r[k] for k in ['edition','page','locus','source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']} for r in hits]
 counts=[]
 for w in sorted(new):
  hh=[r for r in hits if r['ivtff_group_raw']==w];counts.append(dict(word=w,**{ed:sum(r['edition']==ed for r in hh) for ed in EDS},loci=len({r['locus'] for r in hh}),physical_leaves=len({leaf(r['page']) for r in hh})))
 relation=[];flow=[];after=[]
 for k in sorted(targetkeys,key=order):
  rr=lines[k]
  for i,r in enumerate(rr):
   w=r['ivtff_group_raw']
   if w=='olal':
    ss=rr[max(i-1,0):i+2];left=rr[i-1] if i else None;right=rr[i+1] if i+1<len(rr) else None;eligible=bool(left and right) and definite(ss)
    for cid,lx in lex.items():
     roles=[lx.get(t['ivtff_group_raw'],['','UNREAD'])[1] if t else 'MISSING' for t in [left,right]]
     compatible=roles[0]=='QUANTITY_PART' and roles[1] in m['material_roles'] if cid.endswith('_P') else all(t in m['material_roles'] for t in roles)
     status='NOT_TESTABLE' if not eligible else 'UNBOUND' if 'UNREAD' in roles else 'COMPATIBLE' if compatible else 'CONTRADICTION'
     relation.append(dict(candidate=cid,edition=k[0],page=r['page'],physical_leaf=leaf(r['page']),locus=k[1],relation_id=r['source_group_id'],left_id=left['source_group_id'] if left else '',right_id=right['source_group_id'] if right else '',raw=join(ss,lambda x:x['ivtff_group_raw']),left_role=roles[0],right_role=roles[1],left_boundary=r['left_separator'],right_boundary=r['right_separator'],eligible=eligible,status=status,interpretation='PART_OF_MATERIAL' if cid.endswith('_P') else 'MATERIAL_BESIDE_MATERIAL',exposure='DESIGN_LEAF' if leaf(r['page']) in ['77','80','85'] else 'OTHER_EXPOSED_LEAF'))
   if w=='olshedy' and i+1<len(rr) and rr[i+1]['ivtff_group_raw']=='qokeedy':
    for cid,lx in lex.items():flow.append(dict(candidate=cid,edition=k[0],locus=k[1],physical_leaf=leaf(r['page']),participant_id=r['source_group_id'],flow_id=rr[i+1]['source_group_id'],participant_gloss=lx[w][0],status='COMPATIBLE_HYPOTHETICAL_PARTICIPANT' if definite(rr[i:i+2]) and lx[w][1] in m['flow_roles'] and lx['qokeedy'][1]=='FLOW' else 'NOT_TESTABLE',meaning_selected=False))
   if [x['ivtff_group_raw'] for x in rr[i:i+3]]==['ol','shey','daly']:
    after.append(dict(edition=k[0],locus=k[1],source_ids='|'.join(x['source_group_id'] for x in rr[i:i+3]),status='BOUND_HYPOTHETICAL_AFTER_EVENT' if definite(rr[i:i+3]) else 'NOT_TESTABLE'))
 pp=read(m['paragraph_source']);contexts={(p['edition'],p['id']):p for p in read(m['old_context_paragraphs'])};locs={r['locus'] for r in hits if r['ivtff_group_raw'] in ['olshedy','olal']}|set(m['focus_loci']);coverage=[]
 for ed in ['ZL3b','IT2a']:
  for locus in sorted(locs):
   ps=[p for p in pp[ed] if any(l['locus']==locus for l in p['lines'])];assert len(ps)<=1
   coverage.append(dict(edition=ed,locus=locus,status='COMPLETE_PARAGRAPH' if ps else 'MISSING_PARAGRAPH',paragraph_id=ps[0]['id'] if ps else ''))
   for p in ps:contexts[ed,p['id']]=dict(edition=ed,**p)
 contextkeys={(ed,l['locus']) for (ed,pid),p in contexts.items() for l in p['lines']};contextkeys|={('RF1b',l) for e,l in contextkeys if ('RF1b',l) in lines}
 for (ed,pid),p in contexts.items():
  for l in p['lines']:
   rr=lines[ed,l['locus']];assert l['words']==[r['ivtff_group_raw'] for r in rr] and l['source_ids']==[r['source_group_id'] for r in rr]
 known_sides=[]
 for c in relation:
  expected_left=['QUANTITY_PART'] if c['candidate'].endswith('_P') else m['material_roles'];expected_right=m['material_roles']
  wrong=[name for name,role,allowed in [('LEFT',c['left_role'],expected_left),('RIGHT',c['right_role'],expected_right)] if role not in ['UNREAD','MISSING'] and role not in allowed]
  status='NOT_TESTABLE' if not c['eligible'] else 'KNOWN_SIDE_CONTRADICTION' if wrong else 'UNBOUND' if 'UNREAD' in [c['left_role'],c['right_role']] else 'COMPATIBLE'
  known_sides.append(dict(candidate=c['candidate'],edition=c['edition'],locus=c['locus'],relation_id=c['relation_id'],registered_status=c['status'],audit_status=status,known_wrong_sides='|'.join(wrong) if c['eligible'] else '',left_role=c['left_role'],right_role=c['right_role'],stage='POST_CENSUS_NECESSARY_CONDITION_AUDIT'))
 oldmodel=read(m['old_model']);markers=set()
 for rr in lines.values():
  for a,b in zip(rr,rr[1:]):
   if [a['ivtff_group_raw'],b['ivtff_group_raw']]==['s','olkain'] and a['right_separator']==b['left_separator'] and a['right_separator'] in oldmodel['bridge_boundaries']:markers.add(a['source_group_id'])
 local=[];localcases=[];decisions=[]
 for cid,lx in lex.items():
  for ed in EDS:
   for locus in m['focus_loci']:
    rr=lines[ed,locus];unread=[r['ivtff_group_raw'] for r in rr if r['ivtff_group_raw'] not in lx];rawrender=join(rr,lambda r:lx.get(r['ivtff_group_raw'],['⟦'+r['ivtff_group_raw']+'⟧'])[0])
    for r in rr:local.append(dict(candidate=cid,edition=ed,locus=locus,source_id=r['source_group_id'],raw=r['ivtff_group_raw'],gloss=lx.get(r['ivtff_group_raw'],['UNREAD','UNREAD'])[0],role=lx.get(r['ivtff_group_raw'],['UNREAD','UNREAD'])[1],origin='OLD50_HYPOTHESIS' if r['ivtff_group_raw'] in base[cid.rsplit('_',1)[0]] else 'NEW_WHOLE_HYPOTHESIS' if r['ivtff_group_raw'] in new else 'UNREAD',left_separator=r['left_separator'],right_separator=r['right_separator']))
    prose=('Im Rückstand bleibt auch nach diesem Abfluss '+('ein Anteil der Flüssigkeit' if cid.endswith('_P') else 'Öl neben Flüssigkeit')+' zurück.') if locus==m['seed_locus'] and not unread else rawrender
    localcases.append(dict(candidate=cid,edition=ed,locus=locus,groups=len(rr),hypothesis_covered=len(rr)-len(unread),unread='|'.join(unread),reading=prose,complete_hypothetical_reading=locus==m['seed_locus'] and not unread,identity_of_previous_event_or_product='NOT_BOUND'))
  cc=[r for r in relation if r['candidate']==cid];ct=Counter(r['status'] for r in cc);compatible=[r for r in cc if r['status']=='COMPATIBLE'];bad=[r for r in cc if r['status']=='CONTRADICTION'];fc=[r for r in flow if r['candidate']==cid]
  decisions.append(dict(candidate=cid,old_values=50,new_values=8,**{s:ct[s] for s in ['COMPATIBLE','CONTRADICTION','UNBOUND','NOT_TESTABLE']},compatible_loci='|'.join(sorted({r['locus'] for r in compatible})),other_compatible_leaves='|'.join(sorted({r['physical_leaf'] for r in compatible if r['physical_leaf']!='80'},key=int)),contradiction_loci='|'.join(sorted({r['locus'] for r in bad})),flow_pair_cases=len(fc),flow_pair_loci='|'.join(sorted({r['locus'] for r in fc})),decision='FIXED_RELATION_PACKAGE_REJECTED' if bad else 'PORTION_MATERIAL_UNSELECTED',independent_meaning_tests=0,unexposed_confirmation_leaves=0))
 for d in decisions:
  aa=[x for x in known_sides if x['candidate']==d['candidate']];d['registered_decision']=d.pop('decision');d['known_side_contradictions']=sum(x['audit_status']=='KNOWN_SIDE_CONTRADICTION' for x in aa);d['known_side_contradiction_loci']='|'.join(sorted({x['locus'] for x in aa if x['audit_status']=='KNOWN_SIDE_CONTRADICTION'}));d['final_decision']='FIXED_TYPED_PACKAGE_REJECTED_POST_CENSUS_AUDIT' if d['known_side_contradictions'] else d['registered_decision']
 eq=defaultdict(list)
 for cid in lex:eq[tuple((r['relation_id'],r['status']) for r in relation if r['candidate']==cid)].append(cid)
 out={'KNOWN_SIDE_AUDIT.tsv':table(known_sides),'TARGET_READER_COVERAGE.tsv':table([dict(edition=ed,locus=l,status='SOURCE_LINE_PRESENT' if (ed,l) in lines else 'SOURCE_LINE_ABSENT') for l in sorted(targetloci) for ed in EDS]),'LEXICONS.json':dump(lex),'NEW_OCCURRENCES.tsv':table(occ),'WORD_COUNTS.tsv':table(counts),'RELATION_CASES.tsv':table(relation),'FLOW_CASES.tsv':table(flow),'AFTER_EVENT_CASES.tsv':table(after),'LOCAL_ALIGNMENT.tsv':table(local),'LOCAL_CASES.tsv':table(localcases),'CANDIDATE_DECISIONS.tsv':table(decisions),'PARAGRAPH_COVERAGE.tsv':table(coverage),'CONTEXT_PARAGRAPHS.json':dump(list(contexts.values())),'OBSERVATIONAL_GROUPS.json':dump([dict(candidates=cids,scope='Same fixed-triple outcomes, not same meanings.') for cids in eq.values()])}
 for kind,kk in [('TARGET',targetkeys),('CONTEXT',contextkeys)]:
  for ed in EDS:
   packed=[];doc=[f'# GDT946 {kind} {ed}','','All ? are hypotheses. ⟦raw⟧ unread; / uncertain space; // drawing interruption. No discarded reader variant; NOM? is only the retained GDT944 structural assumption. These mechanical renderings do not constitute manual meaning verification.','']
   for k in sorted((k for k in kk if k[0]==ed),key=order):
    rr=lines[k];cols=list(rr[0]);packed.append(dict(edition=ed,locus=k[1],columns=cols,groups=[[r[c] for c in cols] for r in rr]));doc+=['## '+k[1],'','`'+join(rr,lambda r:r['ivtff_group_raw'])+'`',''];rendered=defaultdict(list)
    for cid,lx in lex.items():
     s=join(rr,lambda r:lx[r['ivtff_group_raw']][0]+'?' if r['ivtff_group_raw'] in lx else '⟨NOM?⟩' if r['source_group_id'] in markers else '⟦'+r['ivtff_group_raw']+'⟧');rendered[s].append(cid)
    doc.extend(' / '.join(cids)+': '+s+'\n' for s,cids in rendered.items())
   out[f'{kind}_SOURCE_{ed}.json']=dump(packed);out[f'{kind}_{ed}.md']='\n'.join(doc).rstrip()+'\n'
 out['RESULT.json']=dump(dict(experiment='GDT946',status='PORTION_OR_MATERIAL_WHOLE_CLAUSE_AUDITED',source_groups=sum(map(len,lines.values())),new_values_per_candidate=8,new_occurrences=len(hits),target_lines=len(targetkeys),target_loci=len(targetloci),context_paragraphs=len(contexts),context_groups=sum(len(lines[k]) for k in contextkeys),missing_paragraphs=sum(r['status']=='MISSING_PARAGRAPH' for r in coverage),relation_positions=len(relation)//32,flow_positions=len(flow)//32,after_event_positions=len(after),observational_groups=len(eq),candidates=decisions,confirmed_words=0,independent_meaning_tests=0,unexposed_confirmation_leaves=0,significance_claim=False,new_admissions=0))
 return out
if __name__=='__main__':
 for n,v in build().items():(E/'artifacts'/n).write_text(v)
 print((E/'artifacts/WORD_COUNTS.tsv').read_text());d=json.loads((E/'artifacts/RESULT.json').read_text());print(json.dumps({k:v for k,v in d.items() if k!='candidates'},indent=2));print(json.dumps(d['candidates'][:2],indent=2))
