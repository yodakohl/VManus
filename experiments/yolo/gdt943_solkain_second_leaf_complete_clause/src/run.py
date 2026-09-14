#!/usr/bin/env python3
"""Fixed exploratory whole-clause drafts; no decoder or semantic scoring."""
import csv, hashlib, io, json, re
from collections import Counter, defaultdict
from pathlib import Path
EXP=Path(__file__).resolve().parents[1]; ROOT=EXP.parents[2]
EDS=['ZL3b','IT2a','RF1b']
SEP={'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // ','DRAWING_INTERRUPTION_UNALIGNED':' ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ '}

def read(p): return json.loads((ROOT/p).read_text())
def dump(x): return json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n'
def tsv(rows):
    s=io.StringIO(); w=csv.DictWriter(s,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue()
def leaf(p): return re.match(r'f(\d+)',p)[1]
def sortkey(l): return int(re.match(r'f(\d+)',l)[1]),l.split('.')[0],int(l.split('.')[1])
def join(rr,fn): return ''.join(('' if i==0 else SEP[r['left_separator']])+fn(r) for i,r in enumerate(rr))
def pack(lines,selected):
    out=[]
    for ed,locus in sorted(selected,key=lambda x:(EDS.index(x[0]),sortkey(x[1]))):
        rr=lines[ed,locus]; keys=list(rr[0]);out.append({'edition':ed,'locus':locus,'columns':keys,'groups':[[r[k] for k in keys] for r in rr]})
    return out

def load():
    lock=read(str(EXP.relative_to(ROOT)/'PREREG_LOCK.json'))
    for p,h in lock['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    m=read(str(EXP.relative_to(ROOT)/'src/MODEL.json'));allow=set(read(m['allow_source'])['allowed_selectors'])
    assert len(allow)==179 and not any(x.startswith('f84') or x=='f116v' for x in allow)
    lines={}
    for p in m['sources']:
        d=read(p)
        for line in d['lines']:
            meta=line['metadata'];assert meta['page'] in allow
            key=meta['edition'],meta['locus'];assert key not in lines
            lines[key]=[dict(**meta,**dict(zip(d['group_columns'],g))) for g in line['groups']]
    base=read(m['base_lexicons']);lex={}
    for bid,b in base.items():
        for sid,g in m['shl_variants'].items():
            assert not (set(b)&(set(m['shared_new'])|{'shl'}))
            lex[bid+'_'+sid]={**b,**m['shared_new'],'shl':g}
    return m,lines,base,lex,read(m['paragraph_source'])

def build():
    m,lines,base,lex,pp=load();targets=set(m['shared_new'])|{'shl'}
    occurrences=[r for rr in lines.values() for r in rr if r['ivtff_group_raw'] in targets]
    selected={(r['edition'],r['locus']) for r in occurrences}
    occrows=[]
    for r in occurrences:
        word=r['ivtff_group_raw']; rel=lex['R_C_REL'][word];tmp=lex['R_C_TEMP'][word]
        occrows.append({k:r[k] for k in ['edition','page','locus','source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']}|dict(physical_leaf=leaf(r['page']),REL_gloss=rel[0],TEMP_gloss=tmp[0],REL_role=rel[1],TEMP_role=tmp[1],scope='ALL_FOUR_BASE_MODELS;HYPOTHESIS_ONLY'))
    counts=[]
    for word in sorted(targets):
        hit=[r for r in occurrences if r['ivtff_group_raw']==word]
        counts.append(dict(word=word,**{e:sum(r['edition']==e for r in hit) for e in EDS},loci=len({r['locus'] for r in hit}),leaves=len({leaf(r['page']) for r in hit})))
    contexts={};coverage=[];context_keys=set()
    for ed in ['ZL3b','IT2a']:
        for target in m['context_targets']:
            matches=[p for p in pp[ed] if any(l['locus']==target for l in p['lines'])];assert len(matches)==1
            p=matches[0];contexts[ed,p['id']]=p
            coverage.append(dict(edition=ed,target=target,paragraph_id=p['id'],start=p['lines'][0]['locus'],end=p['lines'][-1]['locus'],line_count=len(p['lines']),group_count=sum(len(l['words']) for l in p['lines']),status='COMPLETE_EXISTING_READER_PARAGRAPH'))
            for line in p['lines']:
                rr=lines[ed,line['locus']]
                assert [r['source_group_id'] for r in rr]==line['source_ids']
                assert [r['ivtff_group_raw'] for r in rr]==line['words']
                context_keys.add((ed,line['locus']));context_keys.add(('RF1b',line['locus']))
    assert pp['RF1b']==[]
    cases=[]
    for ed,locus in sorted(selected,key=lambda x:(EDS.index(x[0]),sortkey(x[1]))):
        rr=lines[ed,locus]
        for i,r in enumerate(rr):
            if r['ivtff_group_raw']!='shl': continue
            prev=rr[i-1] if i else None;body=rr[i+1:i+4]
            for cid,lx in lex.items():
                roles=[lx.get(x['ivtff_group_raw'],['','UNREAD'])[1] for x in body]
                inner=len(body)==3 and all(x['left_separator']=='DEFINITE_SPACE' and rr[i+j]['right_separator']=='DEFINITE_SPACE' for j,x in enumerate(body))
                body_ok=roles==m['relative_body_roles'] and inner
                owner_ok=bool(prev and lx.get(prev['ivtff_group_raw'],['','UNREAD'])[1] in m['nominal_roles'] and r['left_separator']==prev['right_separator']=='DEFINITE_SPACE')
                relative=cid.endswith('_REL')
                status='LOCAL_OWNER_BOUND' if body_ok and relative and owner_ok else 'LOCAL_OWNER_MISSING' if body_ok and relative else 'LOCAL_TIME_BOUND_OWNER_OPEN' if body_ok else 'NO_FIXED_CONSTRUCTION'
                cases.append(dict(candidate=cid,edition=ed,page=r['page'],physical_leaf=leaf(r['page']),locus=locus,source_id=r['source_group_id'],previous_id=prev['source_group_id'] if prev else '',previous_raw=prev['ivtff_group_raw'] if prev else '',body_ids='|'.join(x['source_group_id'] for x in body),body_raw=' '.join(x['ivtff_group_raw'] for x in body),body_roles='|'.join(roles),inner_definite=inner,body_bound=body_ok,status=status,asserted_owner_id=prev['source_group_id'] if body_ok and relative and owner_ok else '',partition='DESIGN_LOCUS' if locus==m['seed_locus'] else 'OTHER_EXPOSED_DESIGN_LEAF' if leaf(r['page'])=='80' else 'OTHER_EXPOSED_LEAF'))
    local=[];readings=[]
    for cid,lx in lex.items():
        for ed in EDS:
            rr=lines[ed,m['seed_locus']];assert [r['ivtff_group_raw'] for r in rr]==m['local_raw']
            for r in rr:
                word=r['ivtff_group_raw'];local.append(dict(candidate=cid,edition=ed,locus=r['locus'],source_id=r['source_group_id'],index=r['source_group_index'],raw=word,gloss=lx[word][0],role=lx[word][1],origin='GDT939_UNCHANGED_HYPOTHESIS' if word in base[cid.rsplit('_',1)[0]] else 'NEW_GDT943_HYPOTHESIS',left_separator=r['left_separator'],right_separator=r['right_separator']))
        relative=cid.endswith('_REL')
        prose=('Der Inhalt, dessen Abfluss langsam ist, gelangt dabei langsam nach außen bis zur unteren Kammer.' if relative else 'Der Inhalt — während der Abfluss langsam ist — gelangt dabei langsam nach außen bis zur unteren Kammer.')
        readings.append(dict(candidate=cid,whole_seed_reading=prose,flow_owner='solkain / content' if relative else 'UNSPECIFIED',main_subject='solkain',old_whole_values=33,new_whole_values=8,confirmed_meanings=0))
    decisions=[]
    for c in readings:
        cs=[r for r in cases if r['candidate']==c['candidate']];bs=[r for r in cs if r['body_bound']]
        outside=[r for r in bs if r['locus']!=m['seed_locus']]
        decisions.append(dict(candidate=c['candidate'],local_groups=12,local_covered=12,new_values=8,shl_positions=len(cs),bound_subclauses=len(bs),bound_loci=len({r['locus'] for r in bs}),other_locus_bound=len(outside),other_leaf_bound=len({r['physical_leaf'] for r in outside if r['physical_leaf']!='80'}),owner_missing=sum(r['status']=='LOCAL_OWNER_MISSING' for r in cs),other_syntax_unresolved=sum(r['status']=='NO_FIXED_CONSTRUCTION' for r in cs),decision='FULL_LOCAL_DRAFT_MEANING_UNSELECTED',independent_meaning_tests=0,unexposed_confirmation_leaves=0))
    out={'LEXICONS.json':dump(lex),'SOURCE_TARGET_LINES.json':dump(pack(lines,selected)),'NEW_OCCURRENCES.tsv':tsv(occrows),'WORD_COUNTS.tsv':tsv(counts),'CONTEXT_PARAGRAPHS.json':dump([dict(edition=e,**p) for (e,i),p in contexts.items()]),'CONTEXT_COVERAGE.tsv':tsv(coverage),'CONTEXT_SOURCE_LINES.json':dump(pack(lines,context_keys)),'SHL_CASES.tsv':tsv(cases),'LOCAL_ALIGNMENT.tsv':tsv(local),'LOCAL_READINGS.tsv':tsv(readings),'CANDIDATE_DECISIONS.tsv':tsv(decisions)}
    context_coverage={}
    for typ,keys in [('TARGET_LINES',selected),('CONTEXT',context_keys)]:
        for ed in EDS:
            doc=[f'# GDT943 {typ} {ed}','','Every source group retained. ? = hypothesis; brackets = unread. Slash = inherited uncertain space; double slash = drawing interruption. Render-identical candidates grouped only for display. RF context is a line union, not an independently established paragraph.','']
            for e,locus in sorted(keys,key=lambda x:(EDS.index(x[0]),sortkey(x[1]))):
                if e!=ed:continue
                rr=lines[e,locus];doc+=['## '+locus,'','`'+join(rr,lambda r:r['ivtff_group_raw'])+'`','']
                equivalent=defaultdict(list)
                for cid,lx in lex.items():
                    rendered=join(rr,lambda r:lx[r['ivtff_group_raw']][0]+'?' if r['ivtff_group_raw'] in lx else '⟦'+r['ivtff_group_raw']+'⟧')
                    equivalent[rendered].append(cid)
                for rendered,cids in equivalent.items():doc+=[' / '.join(cids)+': '+rendered,'']
            out[f'{typ}_{ed}.md']='\n'.join(doc).rstrip()+'\n'
    for cid,lx in lex.items():
        context_coverage[cid]={ed:{'groups':sum(len(lines[e,l]) for e,l in context_keys if e==ed),'hypothesis_groups':sum(r['ivtff_group_raw'] in lx for e,l in context_keys if e==ed for r in lines[e,l])} for ed in EDS}
    out['RESULT.json']=dump(dict(experiment='GDT943',status='FULL_SECOND_LEAF_CLAUSE_HYPOTHESES_UNSELECTED',source_groups=sum(len(r) for r in lines.values()),source_selector_count=179,new_words=8,new_occurrences=len(occurrences),new_target_lines=len(selected),new_target_loci=len({l for e,l in selected}),shl_cases=len(cases),local_alignment_rows=len(local),local_equivalence_groups={'REL':['R_C_REL','R_W_REL','T_C_REL','T_W_REL'],'TEMP':['R_C_TEMP','R_W_TEMP','T_C_TEMP','T_W_TEMP']},context_coverage=context_coverage,candidates=decisions,confirmed_words=0,meaning_selected=None,independent_meaning_tests=0,unexposed_confirmation_leaves=0,significance_claim=False,new_admissions=0))
    return out

if __name__=='__main__':
    for name,value in build().items():(EXP/'artifacts'/name).write_text(value)
    result=read(str(EXP.relative_to(ROOT)/'artifacts/RESULT.json'))
    print(json.dumps({k:v for k,v in result.items() if k not in ['context_coverage','candidates']},indent=2))
    print((EXP/'artifacts/WORD_COUNTS.tsv').read_text())
    print((EXP/'artifacts/CANDIDATE_DECISIONS.tsv').read_text())
