"""Exposed whole-context comparison trial; exact fixed operands, no decoder."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import json,hashlib,csv,io,re
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];EDS=['ZL3b','IT2a','RF1b']
SEP={'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // ','DRAWING_INTERRUPTION_UNALIGNED':' ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ '}
def read(p):return json.loads((ROOT/p).read_text())
def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def tsv(rows):
    s=io.StringIO();w=csv.DictWriter(s,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue()
def join(rr,fn):return ''.join(('' if i==0 else SEP[r['left_separator']])+fn(r) for i,r in enumerate(rr))
def leaf(page):return re.match(r'f(\d+)',page)[1]
def load():
    rel=EXP.relative_to(ROOT);m=read(str(rel/'src/MODEL.json'));lock=read(str(rel/'PREREG_LOCK.json'))
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    spec=read(m['inventory_spec']);allow=set(read(spec['allow_source'])['allowed_selectors'])
    assert len(allow)==179 and not any(p.startswith('f84') or p=='f116v' for p in allow)
    lines={};paths={}
    for p in spec['sources']:
        d=read(p)
        for line in d['lines']:
            meta=line['metadata'];assert meta['page'] in allow and not meta['page'].startswith('f84')
            key=meta['edition'],meta['locus'];assert key not in lines
            lines[key]=[dict(**meta,**dict(zip(d['group_columns'],g))) for g in line['groups']];paths[key]=p
    return m,lines,paths,read(m['base_lexicons']),read(m['paragraph_source'])
def evaluate(rr,i,cid,c,m):
    r=rr[i];l=rr[i-1] if i else None;n=rr[i+1] if i+1<len(rr) else None
    left=re.fullmatch(m['operand_regex'],l['ivtff_group_raw']) if l else None;right=re.fullmatch(m['operand_regex'],n['ivtff_group_raw']) if n else None
    lv=rv='';consequence='';status='UNBOUND_OPERANDS'
    if not l or not n:status='LINE_EDGE'
    elif not (l['right_separator']==r['left_separator']==r['right_separator']==n['left_separator']=='DEFINITE_SPACE'):status='UNCERTAIN_BOUNDARY'
    elif left and right:
        lv=len(left[1])+c['i_offset'];rv=len(right[1])+c['i_offset']
        if c['operation']=='RATIO':consequence=f'{lv}:{rv} = {Fraction(lv,rv)}';status='CONDITIONAL_LOCAL_COMPATIBILITY'
        else:consequence=f'{lv}>{rv} is {lv>rv}';status='CONDITIONAL_LOCAL_COMPATIBILITY' if lv>rv else 'CONTRADICTION'
    return dict(candidate=cid,edition=r['edition'],page=r['page'],physical_leaf=leaf(r['page']),locus=r['locus'],marker_id=r['source_group_id'],marker_raw=r['ivtff_group_raw'],predicted_marker=c['marker_gloss'],required_left=m['operand_regex'],required_right=m['operand_regex'],left_id=l['source_group_id'] if l else '',left_raw=l['ivtff_group_raw'] if l else '',right_id=n['source_group_id'] if n else '',right_raw=n['ivtff_group_raw'] if n else '',left_separator=r['left_separator'],right_separator=r['right_separator'],left_value=lv,right_value=rv,consequence=consequence,status=status,partition='DESIGN_LOCUS' if r['locus']==m['seed_locus'] else 'OTHER_DESIGN_LEAF' if leaf(r['page'])=='115' else 'OTHER_EXPOSED_LEAF',meaning_status='HYPOTHESIS_ONLY')
def build():
    m,lines,paths,base,pp=load();hits=[r for rr in lines.values() for r in rr if r['ivtff_group_raw']==m['marker']];loci=sorted({r['locus'] for r in hits})
    for ed in EDS:assert sorted(r['locus'] for r in hits if r['edition']==ed)==sorted(m['preexposed_exact_marker_loci'][ed])
    variants=[];cases=[]
    for locus in loci:
        for ed in EDS:
            rr=lines[ed,locus];variants.append(dict(edition=ed,locus=locus,exact_marker_count=sum(r['ivtff_group_raw']==m['marker'] for r in rr),raw_line=join(rr,lambda r:r['ivtff_group_raw']),source_ids='|'.join(r['source_group_id'] for r in rr),source_path=paths[ed,locus]))
            for i,r in enumerate(rr):
                if r['ivtff_group_raw']==m['marker']:
                    for cid,c in m['candidates'].items():cases.append(evaluate(rr,i,cid,c,m))
    contexts={};coverage=[];selected={ed:set(loci) for ed in EDS}
    for ed in ['ZL3b','IT2a']:
        for locus in loci:
            matches=[p for p in pp[ed] if any(l['locus']==locus for l in p['lines'])]
            assert len(matches)<=1
            coverage.append(dict(edition=ed,target=locus,paragraph_id=matches[0]['id'] if matches else '',status='COMPLETE_EXISTING_PARAGRAPH' if matches else 'MISSING_COMPLETE_PARAGRAPH'))
            for p in matches:contexts[ed,p['id']]=p
        for page,(lo,hi) in m['working_frames'].items():
            matches=[p for p in pp[ed] if p['page']==page and [l['locus'] for l in p['lines']]==[f'{page}.{n}' for n in range(lo,hi+1)]];assert len(matches)==1
            contexts[ed,matches[0]['id']]=matches[0]
    for (ed,pid),p in contexts.items():
        for line in p['lines']:
            rr=lines[ed,line['locus']];assert [r['source_group_id'] for r in rr]==line['source_ids'] and [r['ivtff_group_raw'] for r in rr]==line['words']
            selected[ed].add(line['locus']);selected['RF1b'].add(line['locus'])
    assert pp['RF1b']==[]
    docs={};align=[];workalign=[]
    for ed in EDS:
        doc=[f'# GDT941 — sämtliche Kontextzeilen {ed}','','? = alter hypothetischer Wortwert; ⟦…⟧ = ungelesen. / unsicherer Abstand, // Zeichnungsunterbrechung, ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ unaligned. ZL/IT-Absatzmitgliedschaft separat in CONTEXT_PARAGRAPHS.json/COVERAGE.tsv; RF nur Vereinigungsfenster ohne Absatzbehauptung. Keine GDT940-Glossen.','']
        for locus in sorted(selected[ed],key=lambda x:(int(re.match(r'f(\d+)',x)[1]),x.split('.')[0],int(x.split('.')[1]))):
            rr=lines[ed,locus];doc+=['## '+locus,'','`'+join(rr,lambda r:r['ivtff_group_raw'])+'`','']
            page=rr[0]['page'];n=int(locus.split('.')[1]);inwork=page in m['working_frames'] and m['working_frames'][page][0]<=n<=m['working_frames'][page][1]
            for cid,lex in base.items():
                doc+=[cid+': '+join(rr,lambda r:lex[r['ivtff_group_raw']][0]+'?' if r['ivtff_group_raw'] in lex else '⟦'+r['ivtff_group_raw']+'⟧'),'']
                for r in rr:
                    gloss,role=lex.get(r['ivtff_group_raw'],['⟦'+r['ivtff_group_raw']+'⟧','UNREAD']);a=dict(candidate=cid,**r,gloss=gloss,role=role);align.append(a)
                    if inwork:workalign.append(a)
            for c in cases:
                if c['edition']==ed and c['locus']==locus:doc+=[f"{c['candidate']} / {c['marker_id']}: {c['status']} — {c['left_raw']} [{c['predicted_marker']}?] {c['right_raw']} — {c['consequence']}".rstrip(),'']
        docs['CONTEXT_'+ed+'.md']='\n'.join(doc).rstrip()+'\n'
    sums=[]
    for cid,c in m['candidates'].items():
        cc=[x for x in cases if x['candidate']==cid];bound=[x for x in cc if x['status'] in ['CONTRADICTION','CONDITIONAL_LOCAL_COMPATIBILITY']];extra=[x for x in bound if x['partition']=='OTHER_EXPOSED_LEAF' and (x['left_raw'],x['right_raw'])!=('lkaiin','lkain')]
        conflicts=sum(x['status']=='CONTRADICTION' for x in bound)
        sums.append(dict(candidate=cid,marker_gloss=c['marker_gloss'],i_offset=c['i_offset'],design_prediction='2:1' if cid=='R0' else '3:2' if cid=='R1' else '2>1' if cid=='G0' else '3>2',marker_positions=len(cc),bound_positions=len(bound),bound_loci=len({x['locus'] for x in bound}),contradictions=conflicts,unbound=len(cc)-len(bound),other_leaf_new_pair_positions=len(extra),other_leaf_new_pair_leaves=len({x['physical_leaf'] for x in extra}),decision='REJECT_FIXED_NUMERIC_COMPARISON' if conflicts else 'EXPLORATORY_TRANSFER_UNSELECTED' if extra else 'NO_TRANSFER_CAPACITY',independent_meaning_tests=0,unexposed_confirmation_leaves=0))
    result=dict(experiment='GDT941',status='NO_TRANSFER_CAPACITY' if all(c['decision']=='NO_TRANSFER_CAPACITY' for c in sums) else 'SEE_CANDIDATES',source_groups=sum(len(rr) for rr in lines.values()),marker_occurrences=len(hits),marker_loci=len(loci),variant_lines=len(variants),candidate_cases=len(cases),whole_context_paragraphs_by_edition=dict(Counter(ed for ed,pid in contexts)),context_line_counts={ed:len(v) for ed,v in selected.items()},context_groups_by_edition={ed:sum(len(lines[ed,l]) for l in ls) for ed,ls in selected.items()},working_frame_groups_by_edition={ed:sum(len(rr) for (e,l),rr in lines.items() if e==ed and rr[0]['page'] in m['working_frames'] and m['working_frames'][rr[0]['page']][0]<=int(l.split('.')[1])<=m['working_frames'][rr[0]['page']][1]) for ed in EDS},context_alignment_rows=len(align),working_alignment_rows=len(workalign),candidates=sums,confirmed_words=0,selected_translation=None,independent_meaning_tests=0,unexposed_confirmation_folios=0,semantics_validated=False,new_admissions=0,significance_claimed=False,olr_meaning_selected=False,whole_paragraph_translation_achieved=False)
    paraout=[dict(edition=ed,**p) for (ed,pid),p in sorted(contexts.items())]
    return {'MARKER_CASES.tsv':tsv(cases),'MARKER_VARIANTS.tsv':tsv(variants),'CANDIDATE_DECISIONS.tsv':tsv(sums),'CONTEXT_PARAGRAPHS.json':dump(paraout),'CONTEXT_COVERAGE.tsv':tsv(coverage),'CONTEXT_ALIGNMENT.tsv':tsv(align),'WORKING_ALIGNMENT.tsv':tsv(workalign),'RESULT.json':dump(result),**docs}
if __name__=='__main__':
    for name,value in build().items():(EXP/'artifacts'/name).write_text(value)
    print((EXP/'artifacts/RESULT.json').read_text())
