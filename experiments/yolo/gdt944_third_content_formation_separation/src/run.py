#!/usr/bin/env python3
"""Fixed whole-word hypotheses and two explicit phrase comparisons."""
import csv,hashlib,io,json,re
from collections import Counter,defaultdict
from pathlib import Path
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];EDS=['ZL3b','IT2a','RF1b']
SEP={'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // ','DRAWING_INTERRUPTION_UNALIGNED':' ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ '}
def read(p):return json.loads((ROOT/p).read_text())
def dump(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n'
def tsv(rows,fields=None):
 s=io.StringIO();w=csv.DictWriter(s,fieldnames=fields or list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue()
def order(l):return int(re.match(r'f(\d+)',l)[1]),l.split('.')[0],int(l.split('.')[1])
def leaf(p):return re.match(r'f(\d+)',p)[1]
def join(rr,fn):return ''.join(('' if i==0 else SEP[r['left_separator']])+fn(r) for i,r in enumerate(rr))
def pack(lines,keys):
 out=[]
 for ed,locus in sorted(keys,key=lambda x:(EDS.index(x[0]),order(x[1]))):
  rr=lines[ed,locus];cols=list(rr[0]);out.append(dict(edition=ed,locus=locus,columns=cols,groups=[[r[c] for c in cols] for r in rr]))
 return out

def load():
 lock=read(str(EXP.relative_to(ROOT)/'PREREG_LOCK.json'))
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 m=read(str(EXP.relative_to(ROOT)/'src/MODEL.json'));allow=set(read(m['allow_source'])['allowed_selectors'])
 assert len(allow)==179 and not any(x.startswith('f84') or x=='f116v' for x in allow)
 lines={}
 for path in m['sources']:
  d=read(path)
  for line in d['lines']:
   meta=line['metadata'];assert meta['page'] in allow
   key=meta['edition'],meta['locus'];assert key not in lines
   lines[key]=[dict(**meta,**dict(zip(d['group_columns'],g))) for g in line['groups']]
 base=read(m['base_lexicons']);lex={}
 for bid,b in base.items():
  for ev,new in m['event_variants'].items():
   assert not set(b)&(set(m['shared_new'])|set(new))
   lex[bid+'_'+ev]={**b,**m['shared_new'],**new}
 return m,lines,base,lex,read(m['paragraph_source'])

def bridges_for(rr,m):
 out=[]
 for i,r in enumerate(rr):
  for b in m['phrase_bridges']:
   if r['ivtff_group_raw']==b['whole']:out.append((b['name'],'WHOLE',i,i+1,True))
   if i+1<len(rr) and [x['ivtff_group_raw'] for x in rr[i:i+2]]==b['parts']:
    allowed=r['right_separator']==rr[i+1]['left_separator'] and r['right_separator'] in m['bridge_boundaries']
    out.append((b['name'],'SPLIT',i,i+2,allowed))
 return out

def build():
 m,lines,base,lex,pp=load();newwords=set(m['shared_new'])|set(m['event_variants']['F']);assert len(newwords)==9
 hits=[r for rr in lines.values() for r in rr if r['ivtff_group_raw'] in newwords]
 targetkeys={(r['edition'],r['locus']) for r in hits};bridges=[];kernels=[];marker_ids=set()
 for (ed,locus),rr in lines.items():
  for name,form,start,end,allowed in bridges_for(rr,m):
   ss=rr[start:end];r=ss[0];row=dict(bridge=name,form=form,edition=ed,page=r['page'],physical_leaf=leaf(r['page']),locus=locus,source_ids='|'.join(x['source_group_id'] for x in ss),raw_groups=' '.join(x['ivtff_group_raw'] for x in ss),start=start,end=end,eligible=allowed,internal_boundary=ss[0]['right_separator'] if form=='SPLIT' else 'INTERNAL_TO_WHOLE',meaning_status='PROPOSED_CORRESPONDENCE_NOT_CONFIRMED')
   bridges.append(row);targetkeys.add((ed,locus))
   if name=='CONTENT' and form=='SPLIT' and allowed:marker_ids.add(r['source_group_id'])
   if name=='PASSIVE' and allowed:kernels.append(row)
 contexts={(p['edition'],p['id']):{k:v for k,v in p.items() if k!='edition'} for p in read(m['old_context_paragraphs'])}
 coverage=[]
 for ed in ['ZL3b','IT2a']:
  for locus in sorted({k['locus'] for k in kernels},key=order):
   ps=[p for p in pp[ed] if any(l['locus']==locus for l in p['lines'])];assert len(ps)<=1
   coverage.append(dict(edition=ed,target=locus,paragraph_id=ps[0]['id'] if ps else '',status='COMPLETE_EXISTING_PARAGRAPH' if ps else 'MISSING_PARAGRAPH'))
   for p in ps:contexts[ed,p['id']]=p
 contextkeys=set()
 for (ed,pid),p in contexts.items():
  for line in p['lines']:
   rr=lines[ed,line['locus']];assert [r['source_group_id'] for r in rr]==line['source_ids'] and [r['ivtff_group_raw'] for r in rr]==line['words']
   contextkeys|={(ed,line['locus']),('RF1b',line['locus'])}
 assert pp['RF1b']==[]
 cases=[];mentions=[]
 for k in kernels:
  rr=lines[k['edition'],k['locus']];start,end=k['start'],k['end'];tail=rr[end:end+3]
  for cid,lx in lex.items():
   roles=[lx.get(r['ivtff_group_raw'],['','UNREAD'])[1] for r in tail]
   definite=len(tail)==3 and all(r['left_separator']==rr[end+j-1]['right_separator']=='DEFINITE_SPACE' for j,r in enumerate(tail))
   frame=len(tail)==3 and [r['ivtff_group_raw'] for r in tail[:2]]==m['fixed_tail'] and definite
   bound=frame and roles[2] in m['product_roles']
   status='SOURCE_PRODUCT_BOUND_HYPOTHETICALLY' if bound else 'PRODUCT_UNREAD_OR_WRONG_ROLE' if frame else 'NO_FIXED_SOURCE_PRODUCT_FRAME'
   product=tail[2] if bound else None
   related=[p for (ed,pid),p in contexts.items() if ed==k['edition'] and any(l['locus']==k['locus'] for l in p['lines'])]
   assert len(related)<=1
   before=[];after=[]
   if bound and related:
    sequence=[r for l in related[0]['lines'] for r in lines[k['edition'],l['locus']]];idx=next(i for i,r in enumerate(sequence) if r['source_group_id']==product['source_group_id'])
    for pos,r in enumerate(sequence):
     if r['ivtff_group_raw']==product['ivtff_group_raw'] and pos!=idx:
      direction='BEFORE' if pos<idx else 'AFTER';(before if pos<idx else after).append(r['source_group_id'])
      mentions.append(dict(candidate=cid,event_ids=k['source_ids'],edition=k['edition'],paragraph_id=related[0]['id'],product_id=product['source_group_id'],product_raw=product['ivtff_group_raw'],mention_id=r['source_group_id'],mention_locus=r['locus'],direction=direction,identity_status='SAME_SPELLING_NOT_IDENTIFIED_AS_SAME_PORTION'))
   cases.append(dict(candidate=cid,edition=k['edition'],page=k['page'],physical_leaf=k['physical_leaf'],locus=k['locus'],form=k['form'],event_ids=k['source_ids'],event_raw=k['raw_groups'],event_reading=m['event_variants'][cid[-1]]['arolkeedy'][0],tail_ids='|'.join(r['source_group_id'] for r in tail),tail_raw=' '.join(r['ivtff_group_raw'] for r in tail),tail_roles='|'.join(roles),status=status,source_id=tail[1]['source_group_id'] if frame else '',product_id=product['source_group_id'] if product else '',product_raw=product['ivtff_group_raw'] if product else '',earlier_same_word='|'.join(before),later_same_word='|'.join(after),paragraph_scope=related[0]['id'] if related else 'NO_READER_PARAGRAPH',product_identity_status='UNRESOLVED',semantic_contradiction='NOT_ESTABLISHED',meaning_selected=False))
 occurrence_rows=[]
 for r in hits:
  word=r['ivtff_group_raw'];f=lex['R_C_REL_F'][word];s=lex['R_C_REL_S'][word]
  occurrence_rows.append({k:r[k] for k in ['edition','page','locus','source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']}|dict(F_gloss=f[0],S_gloss=s[0],F_role=f[1],S_role=s[1],meaning_status='ALL_EIGHT_BASE_MODELS;HYPOTHESIS'))
 local=[];local_cases=[]
 for cid,lx in lex.items():
  for ed in EDS:
   rr=lines[ed,m['seed_locus']];unknown=[];nstruct=0
   for r in rr:
    word=r['ivtff_group_raw'];g,role=lx.get(word,['⟦'+word+'⟧','UNREAD']);struct=r['source_group_id'] in marker_ids
    if word not in lx and not struct:unknown.append(word)
    nstruct+=struct
    local.append(dict(candidate=cid,edition=ed,locus=r['locus'],source_id=r['source_group_id'],raw=word,left_separator=r['left_separator'],right_separator=r['right_separator'],literal_gloss=g,lexical_role=role,bridge_role='NOMINAL_MARKER_HYPOTHESIS_NOT_WORD_TRANSLATION' if struct else '',origin='OLD41_HYPOTHESIS' if word in base[cid.rsplit('_',1)[0]] else 'NEW_WHOLE_HYPOTHESIS' if word in newwords else 'STRUCTURAL_PHRASE_HYPOTHESIS' if struct else 'UNREAD'))
   product='Flüssigkeit' if not unknown else '⟦'+','.join(unknown)+'⟧'
   prose='Der Inhalt zerfällt allmählich, und dabei wird aus dem Inhalt '+product+' '+('gebildet.' if cid.endswith('_F') else 'abgesondert.')
   local_cases.append(dict(candidate=cid,edition=ed,groups=len(rr),lexical_hypothesis_groups=sum(r['ivtff_group_raw'] in lx for r in rr),structural_phrase_groups=nstruct,unread_without_bridge=sum(r['ivtff_group_raw'] not in lx for r in rr),unread_with_bridge=len(unknown),unread_raw='|'.join(unknown),whole_draft=prose,content_source_identity='ASSUMED_LOCAL_COREFERENCE_NOT_PROVEN',status='COMPLETE_HYPOTHETICAL_CLAUSE' if not unknown else 'INCOMPLETE_READER_CLAUSE'))
 counts=[]
 for word in sorted(newwords):
  hh=[r for r in hits if r['ivtff_group_raw']==word];counts.append(dict(word=word,**{ed:sum(r['edition']==ed for r in hh) for ed in EDS},loci=len({r['locus'] for r in hh}),leaves=len({leaf(r['page']) for r in hh})))
 decisions=[]
 for cid in lex:
  cc=[c for c in cases if c['candidate']==cid];bound=[c for c in cc if c['status']=='SOURCE_PRODUCT_BOUND_HYPOTHETICALLY']
  decisions.append(dict(candidate=cid,old_words=41,new_wholes=9,full_local_readers='|'.join(c['edition'] for c in local_cases if c['candidate']==cid and c['unread_with_bridge']==0),passive_candidates=len(cc),source_product_bound=len(bound),bound_loci=len({c['locus'] for c in bound}),other_bound_loci=len({c['locus'] for c in bound if c['locus']!=m['seed_locus']}),identified_prior_product=0,identified_later_product=0,semantic_contradictions='NOT_ESTABLISHED',decision='FORMATION_SEPARATION_UNSELECTED',independent_meaning_tests=0,unexposed_confirmation_leaves=0))
 out={'LEXICONS.json':dump(lex),'BRIDGE_CASES.tsv':tsv(bridges),'NEW_OCCURRENCES.tsv':tsv(occurrence_rows),'WORD_COUNTS.tsv':tsv(counts),'LOCAL_ALIGNMENT.tsv':tsv(local),'LOCAL_CASES.tsv':tsv(local_cases),'PASSIVE_CASES.tsv':tsv(cases),'PRODUCT_MENTIONS.tsv':tsv(mentions,['candidate','event_ids','edition','paragraph_id','product_id','product_raw','mention_id','mention_locus','direction','identity_status']),'CANDIDATE_DECISIONS.tsv':tsv(decisions),'CONTEXT_PARAGRAPHS.json':dump([dict(edition=ed,**p) for (ed,pid),p in contexts.items()]),'PASSIVE_PARAGRAPH_COVERAGE.tsv':tsv(coverage)}
 for kind,keys in [('TARGET',targetkeys),('CONTEXT',contextkeys)]:
  for ed in EDS:
   out[f'{kind}_SOURCE_{ed}.json']=dump(pack(lines,{k for k in keys if k[0]==ed}))
   doc=[f'# GDT944 {kind} {ed}','','? = hypothetical whole-word value. ⟦raw⟧ = unread; ⟨NOM?⟩ = separate structural phrase assumption, not an English/German word. Source spaces/entities preserved. / uncertain space; // drawing interruption. Identical rendered candidates grouped only for display. RF context is a line union, not independent paragraph evidence.','']
   for e,locus in sorted(keys,key=lambda x:(EDS.index(x[0]),order(x[1]))):
    if e!=ed:continue
    rr=lines[e,locus];doc+=['## '+locus,'','`'+join(rr,lambda r:r['ivtff_group_raw'])+'`',''];eq=defaultdict(list)
    for cid,lx in lex.items():
     rendered=join(rr,lambda r:'⟨NOM?⟩' if r['source_group_id'] in marker_ids else lx[r['ivtff_group_raw']][0]+'?' if r['ivtff_group_raw'] in lx else '⟦'+r['ivtff_group_raw']+'⟧');eq[rendered].append(cid)
    for rendered,cids in eq.items():doc+=[' / '.join(cids)+': '+rendered,'']
   out[f'{kind}_{ed}.md']='\n'.join(doc).rstrip()+'\n'
 coverage={}
 for cid,lx in lex.items():
  coverage[cid]={}
  for ed in EDS:
   rr=[r for e,l in contextkeys if e==ed for r in lines[e,l]]
   coverage[cid][ed]=dict(groups=len(rr),lexical_hypothesis=sum(r['ivtff_group_raw'] in lx for r in rr),structural_only=sum(r['source_group_id'] in marker_ids for r in rr),unread=sum(r['ivtff_group_raw'] not in lx and r['source_group_id'] not in marker_ids for r in rr))
 out['RESULT.json']=dump(dict(experiment='GDT944',status='THIRD_CONTENT_CLAUSE_FORMATION_SEPARATION_UNSELECTED',source_groups=sum(map(len,lines.values())),new_wholes=9,new_occurrences=len(hits),target_lines=len(targetkeys),target_loci=len({l for e,l in targetkeys}),bridge_summary=dict(Counter(b['bridge']+'_'+b['form']+'_'+str(b['eligible']) for b in bridges)),passive_kernels=len(kernels),passive_candidate_cases=len(cases),context_groups=sum(len(lines[k]) for k in contextkeys),context_paragraphs=len(contexts),context_coverage=coverage,local_cases=local_cases,candidates=decisions,confirmed_words=0,independent_meaning_tests=0,unexposed_confirmation_leaves=0,significance_claim=False,new_admissions=0,semantic_equivalence_is_stipulated=True))
 return out
if __name__=='__main__':
 for n,v in build().items():(EXP/'artifacts'/n).write_text(v)
 r=read(str(EXP.relative_to(ROOT)/'artifacts/RESULT.json'))
 print(json.dumps({k:v for k,v in r.items() if k not in ['context_coverage','local_cases','candidates']},indent=2))
 print((EXP/'artifacts/WORD_COUNTS.tsv').read_text())
 print((EXP/'artifacts/BRIDGE_CASES.tsv').read_text())
