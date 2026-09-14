#!/usr/bin/env python3
"""Execute fixed whole-word hypotheses and strict immediate-complement audit."""
import csv,io,json,hashlib,re
from pathlib import Path
from collections import Counter,defaultdict
E=Path(__file__).resolve().parents[1];R=E.parents[2];EDS=['ZL3b','IT2a','RF1b']
def read(p):return json.loads((R/p).read_text())
def dump(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n'
def table(rows,fields=None):
 f=io.StringIO();w=csv.DictWriter(f,fields or list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return f.getvalue()
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
   meta=l['metadata'];assert meta['page'] in allow;k=meta['edition'],meta['locus'];assert k not in lines
   lines[k]=[meta|dict(zip(d['group_columns'],g)) for g in l['groups']]
 base=read(m['base_lexicons']);lex={cid+'_'+v:b|m['shared_new']|new for cid,b in base.items() for v,new in m['variants'].items()};new=set(m['shared_new'])|{'qoker'}
 hits=[r for rr in lines.values() for r in rr if r['ivtff_group_raw'] in new];keys={(r['edition'],r['locus']) for r in hits};occ=[]
 fields=['edition','page','locus','source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']
 for r in hits:occ.append({k:r[k] for k in fields})
 counts=[]
 for w in sorted(new):
  hh=[r for r in hits if r['ivtff_group_raw']==w];counts.append(dict(word=w,**{ed:sum(r['edition']==ed for r in hh) for ed in EDS},loci=len({r['locus'] for r in hh}),physical_leaves=len({leaf(r['page']) for r in hh})))
 relations=[];frames=[]
 for k in sorted(keys,key=order):
  rr=lines[k]
  for i,r in enumerate(rr):
   w=r['ivtff_group_raw']
   if w not in ['qoker','qokey']:continue
   tail=rr[i+1:i+2];t=tail[0] if tail else None;eligible=bool(t) and definite([r,t]);allowed=m['nominal_roles'] if w=='qoker' else m['goal_roles']
   for cid,lx in lex.items():
    role=lx.get(t['ivtff_group_raw'],['','UNREAD'])[1] if t else 'NO_FOLLOWING_GROUP'
    status='NOT_TESTABLE' if not eligible else 'UNBOUND' if role=='UNREAD' else 'COMPATIBLE' if role in allowed else 'CONTRADICTION'
    relations.append(dict(candidate=cid,edition=k[0],page=r['page'],physical_leaf=leaf(r['page']),locus=k[1],relation_id=r['source_group_id'],relation=w,relation_gloss=lx[w][0],next_id=t['source_group_id'] if t else '',next_raw=t['ivtff_group_raw'] if t else '',next_gloss=lx.get(t['ivtff_group_raw'],['',''])[0] if t else '',next_role=role,boundary=r['right_separator'],eligible=eligible,status=status,exposure='SEED_LEAF_EXPOSED' if leaf(r['page'])=='80' else 'OTHER_EXPOSED_LEAF'))
   if i>0 and rr[i-1]['ivtff_group_raw']=='qokeedy' and w=='qoker':
    ss=rr[i-1:i+3];ok=len(ss)==4 and definite(ss)
    for cid,lx in lex.items():
     roles=[lx.get(x['ivtff_group_raw'],['','UNREAD'])[1] for x in ss[2:]]
     status='NOT_TESTABLE' if not ok else 'UNBOUND' if 'UNREAD' in roles else 'COMPATIBLE' if roles[0] in m['nominal_roles'] and roles[1] in m['product_roles'] else 'CONTRADICTION'
     frames.append(dict(candidate=cid,edition=k[0],locus=k[1],physical_leaf=leaf(r['page']),source_ids='|'.join(x['source_group_id'] for x in ss),raw=join(ss,lambda x:x['ivtff_group_raw']),roles='|'.join(roles),status=status,binding='N1_SOURCE_N2_FLOWING_PART' if cid.endswith('_SRC') else 'N1_PARENT_N2_FLOWING_PART'))
 contexts=read(m['old_context_paragraphs']);contextkeys=set()
 for p in contexts:
  for l in p['lines']:
   rr=lines[p['edition'],l['locus']];assert l['source_ids']==[r['source_group_id'] for r in rr] and l['words']==[r['ivtff_group_raw'] for r in rr]
   contextkeys|={(p['edition'],l['locus']),('RF1b',l['locus'])}
 oldmodel=read(m['old_model']);markers=set()
 for rr in lines.values():
  for a,b in zip(rr,rr[1:]):
   if [a['ivtff_group_raw'],b['ivtff_group_raw']]==['s','olkain'] and a['right_separator']==b['left_separator'] and a['right_separator'] in oldmodel['bridge_boundaries']:markers.add(a['source_group_id'])
 local=[];localcases=[];decisions=[]
 for cid,lx in lex.items():
  for ed in EDS:
   rr=lines[ed,m['seed_locus']]
   for r in rr:local.append(dict(candidate=cid,edition=ed,source_id=r['source_group_id'],raw=r['ivtff_group_raw'],gloss=lx.get(r['ivtff_group_raw'],['UNREAD','UNREAD'])[0],role=lx.get(r['ivtff_group_raw'],['UNREAD','UNREAD'])[1],origin='OLD50_HYPOTHESIS' if r['ivtff_group_raw'] in base[cid.rsplit('_',1)[0]] else 'NEW_WHOLE_HYPOTHESIS',left_separator=r['left_separator'],right_separator=r['right_separator']))
   draft='Aus dem Inhalt fließt ein Flüssigkeitsanteil langsam zum Ausgang hin.' if cid.endswith('_SRC') else 'Der Flüssigkeitsanteil des Inhalts fließt langsam zum Ausgang hin.'
   localcases.append(dict(candidate=cid,edition=ed,groups=len(rr),hypothesis_covered=sum(r['ivtff_group_raw'] in lx for r in rr),draft=draft,previous_product_identity='UNPROVEN'))
  cc=[c for c in relations if c['candidate']==cid];fc=[c for c in frames if c['candidate']==cid];counts_c=Counter(c['status'] for c in cc)
  nonseed=[c for c in cc if c['status']=='COMPATIBLE' and c['physical_leaf']!='80'];bad=[c for c in cc if c['status']=='CONTRADICTION']
  decisions.append(dict(candidate=cid,old_values=50,new_values=6,**{s:counts_c[s] for s in ['COMPATIBLE','CONTRADICTION','UNBOUND','NOT_TESTABLE']},contradiction_loci=len({c['locus'] for c in bad}),other_compatible_loci=len({c['locus'] for c in nonseed}),other_compatible_exposed_leaves='|'.join(sorted({c['physical_leaf'] for c in nonseed},key=int)),bound_flow_frame_loci='|'.join(sorted({c['locus'] for c in fc if c['status']=='COMPATIBLE'})),decision='STRICT_PACKAGE_REJECTED' if bad else 'PROVISIONAL_UNSELECTED',independent_meaning_tests=0,unexposed_confirmation_leaves=0))
 out={'LEXICONS.json':dump(lex),'NEW_OCCURRENCES.tsv':table(occ),'WORD_COUNTS.tsv':table(counts),'RELATION_CASES.tsv':table(relations),'FLOW_FRAME_CASES.tsv':table(frames),'LOCAL_ALIGNMENT.tsv':table(local),'LOCAL_CASES.tsv':table(localcases),'CANDIDATE_DECISIONS.tsv':table(decisions),'CONTEXT_PARAGRAPHS.json':dump(contexts)}
 signatures=defaultdict(list)
 for cid in lex:
  sig=tuple((c['relation_id'],c['status']) for c in relations if c['candidate']==cid);signatures[sig].append(cid)
 out['OBSERVATIONAL_GROUPS.json']=dump([dict(candidates=cids,scope='Identical eligibility and compatible/contradiction/unbound predictions; lexical roles may differ. Source/genitive bindings and full lexicons remain semantically different.') for cids in signatures.values()])
 for kind,kk in [('TARGET',keys),('CONTEXT',contextkeys)]:
  for ed in EDS:
   packed=[];doc=[f'# GDT945 {kind} {ed}','','Every ? is a hypothesis. ⟦raw⟧ unread; / uncertain space, // drawing interruption. NOM? is the unchanged GDT944 structural assumption. All candidates are grouped only when this line renders identically. RF is a line union, not a paragraph edition.','']
   for k in sorted((k for k in kk if k[0]==ed),key=order):
    rr=lines[k];cols=list(rr[0]);packed.append(dict(edition=ed,locus=k[1],columns=cols,groups=[[r[c] for c in cols] for r in rr]));doc+=['## '+k[1],'','`'+join(rr,lambda r:r['ivtff_group_raw'])+'`',''];eq=defaultdict(list)
    for cid,lx in lex.items():
     s=join(rr,lambda r:lx[r['ivtff_group_raw']][0]+'?' if r['ivtff_group_raw'] in lx else '⟨NOM?⟩' if r['source_group_id'] in markers else '⟦'+r['ivtff_group_raw']+'⟧');eq[s].append(cid)
    doc.extend(' / '.join(cids)+': '+s+'\n' for s,cids in eq.items())
   out[f'{kind}_SOURCE_{ed}.json']=dump(packed);out[f'{kind}_{ed}.md']='\n'.join(doc).rstrip()+'\n'
 # Complete paragraph coverage; unknown groups are never discarded.
 coverage={}
 for cid,lx in lex.items():
  coverage[cid]={}
  for ed in EDS:
   rr=[r for k in contextkeys if k[0]==ed for r in lines[k]];coverage[cid][ed]=dict(groups=len(rr),lexical=sum(r['ivtff_group_raw'] in lx for r in rr),structural_only=sum(r['source_group_id'] in markers for r in rr),unread=sum(r['ivtff_group_raw'] not in lx and r['source_group_id'] not in markers for r in rr))
 out['RESULT.json']=dump(dict(experiment='GDT945',status='STRICT_SOURCE_PARTITIVE_PACKAGES_AUDITED',source_groups=sum(map(len,lines.values())),new_words=6,new_occurrences=len(hits),target_lines=len(keys),target_loci=len({k[1] for k in keys}),physical_target_leaves=len({leaf(k[1]) for k in keys}),candidates=decisions,observational_groups=len(signatures),context_groups=sum(len(lines[k]) for k in contextkeys),context_coverage=coverage,confirmed_words=0,independent_meaning_tests=0,unexposed_confirmation_leaves=0,new_admissions=0,significance_claim=False))
 return out
if __name__=='__main__':
 for n,v in build().items():(E/'artifacts'/n).write_text(v)
 print((E/'artifacts/WORD_COUNTS.tsv').read_text());d=json.loads((E/'artifacts/RESULT.json').read_text());print(json.dumps({k:v for k,v in d.items() if k not in ['candidates','context_coverage']},indent=2));print(json.dumps(d['candidates'][0],indent=2))
