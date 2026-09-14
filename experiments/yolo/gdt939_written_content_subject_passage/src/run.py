"""Frozen whole-line content draft and census of all newly assigned exact words."""
from pathlib import Path
from collections import Counter, defaultdict
import csv,hashlib,io,json,re
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];EDS=['ZL3b','IT2a','RF1b']
def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def read(p):return json.loads((ROOT/p).read_text())
def tsv(rows):
    s=io.StringIO();w=csv.DictWriter(s,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue()
def join(rr,fn):return ''.join(('' if i==0 else {'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // ','DRAWING_INTERRUPTION_UNALIGNED':' ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ '}[r['left_separator']])+fn(r) for i,r in enumerate(rr))
def load():
    for p,h in read(str(EXP.relative_to(ROOT)/'PREREG_LOCK.json'))['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    m=json.loads((EXP/'src/MODEL.json').read_text());spec=read(m['inventory_spec']);allow=set(read(spec['allow_source'])['allowed_selectors']);assert len(allow)==179 and not any(x.startswith('f84') or x=='f116v' for x in allow)
    lines={};source_paths={}
    for p in spec['sources']:
        d=read(p)
        for line in d['lines']:
            meta=line['metadata'];assert meta['page'] in allow
            key=meta['edition'],meta['locus'];assert key not in lines
            lines[key]=[dict(**meta,**dict(zip(d['group_columns'],g))) for g in line['groups']];source_paths[key]=p
    old=read(m['prior_lexicons']);lex={cid:dict(words,**m['new_lexicon']) for cid,words in old.items()}
    assert all(len(v)==24 and not v.keys() & m['new_lexicon'].keys() for v in old.values())
    assert all(len(v)==33 for v in lex.values())
    return m,lines,source_paths,old,lex

def build():
    m,lines,source_paths,old,lex=load();targets=set(m['new_lexicon']);hits=[r for rr in lines.values() for r in rr if r['ivtff_group_raw'] in targets]
    hitkeys={(r['edition'],r['locus']) for r in hits};occ=[]
    for r in hits:
        key=r['edition'],r['locus'];rr=lines[key];i=rr.index(r);gloss,role=m['new_lexicon'][r['ivtff_group_raw']]
        occ.append(dict(edition=r['edition'],page=r['page'],locus=r['locus'],source_group_id=r['source_group_id'],raw=r['ivtff_group_raw'],gloss=gloss,role=role,left_raw=rr[i-1]['ivtff_group_raw'] if i else '',right_raw=rr[i+1]['ivtff_group_raw'] if i+1<len(rr) else '',left_separator=r['left_separator'],right_separator=r['right_separator'],source_path=source_paths[key],applies_to='R_C,R_W,T_C,T_W',meaning_status='HYPOTHESIS_ONLY'))
    docs={}
    for ed in EDS:
        doc=[f'# GDT939 — alle vollständigen neuen Trefferzeilen {ed}','','Alle Wortwerte hypothetisch. ? markiert Annahmen; ⟦…⟧ ungelesene Rohgruppen; / unsicherer Abstand; // Zeichnungsunterbrechung; ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ nicht ausgerichtete Zeichnungsunterbrechung. Keine zusätzlichen vollständigen Absätze behauptet.','']
        for e,locus in sorted(hitkeys):
            if e!=ed:continue
            rr=lines[e,locus];doc.extend(['## '+locus,'','`'+join(rr,lambda r:r['ivtff_group_raw'])+'`',''])
            for cid,words in lex.items():doc.extend([cid+': '+join(rr,lambda r:words[r['ivtff_group_raw']][0]+'?' if r['ivtff_group_raw'] in words else '⟦'+r['ivtff_group_raw']+'⟧'),''])
        docs['TARGET_LINES_'+ed+'.md']='\n'.join(doc).rstrip()+'\n'
    frame=[];alignment=[];local=[];predictions=[]
    page,lo,hi=m['frame']
    for ed in EDS:
        doc=[f'# GDT939 — ganzer Arbeitsrahmen {ed}','','ZL/IT: vollständiger bestehender Absatz. RF: entsprechendes25-Zeilen-Vergleichsfenster ohne behauptete Absatzvollständigkeit. Alle Bedeutungen hypothetisch; Grenzen unverändert.','']
        for n in range(lo,hi+1):
            rr=lines[ed,f'{page}.{n}'];frame.extend(rr);doc.extend(['## '+f'{page}.{n}','','`'+join(rr,lambda r:r['ivtff_group_raw'])+'`',''])
            for cid,words in lex.items():
                doc.extend([cid+': '+join(rr,lambda r:words[r['ivtff_group_raw']][0]+'?' if r['ivtff_group_raw'] in words else '⟦'+r['ivtff_group_raw']+'⟧'),''])
                for r in rr:
                    gloss,role=words.get(r['ivtff_group_raw'],['⟦'+r['ivtff_group_raw']+'⟧','UNREAD'])
                    alignment.append(dict(candidate=cid,**r,gloss=gloss,role=role))
            if n==17:
                assert [r['ivtff_group_raw'] for r in rr]==m['expected_words']
                for cid,words in lex.items():
                    for r,slot in zip(rr,m['local_roles']):local.append(dict(candidate=cid,edition=ed,source_group_id=r['source_group_id'],raw=r['ivtff_group_raw'],gloss=words[r['ivtff_group_raw']][0],lexical_role=words[r['ivtff_group_raw']][1],local_role=slot,subject_id=rr[0]['source_group_id'],status='LOCAL_BINDING_HYPOTHESIS'))
                    c=cid.split('_')[1]
                    predictions.append(dict(candidate=cid,edition=ed,prediction_group=c,full_sentence=m['sentences'][c],subject_id=rr[0]['source_group_id'],subject='Inhalt',container_id=rr[2]['source_group_id'],container='Rohr',demonstrative_id=rr[1]['source_group_id'],predicate_id=rr[3]['source_group_id'],copula_id=rr[4]['source_group_id'],motion_ids=rr[5]['source_group_id']+'|'+rr[9]['source_group_id'],motion_subject_id=rr[0]['source_group_id'],aperture_id=rr[11]['source_group_id'],optical_clarity=True if c=='C' else None,water_identity=True if c=='W' else None,asserts_pipe_water_identity=False,chronology_inferred=False,factual_inference=False,empirically_selected=False))
        docs['FRAME_'+ed+'.md']='\n'.join(doc).rstrip()+'\n'
    # Every known multiword run containing a newly assigned value, for bounded manual navigation.
    islands=[]
    for ed,locus in sorted(hitkeys):
        rr=lines[ed,locus];i=0
        while i<len(rr):
            if rr[i]['ivtff_group_raw'] not in lex['R_C']:i+=1;continue
            j=i+1
            while j<len(rr) and rr[j]['ivtff_group_raw'] in lex['R_C'] and rr[j-1]['right_separator']==rr[j]['left_separator']=='DEFINITE_SPACE':j+=1
            block=rr[i:j]
            if len(block)>=2 and any(r['ivtff_group_raw'] in targets for r in block):islands.append(dict(edition=ed,locus=locus,ids=[r['source_group_id'] for r in block],words=[r['ivtff_group_raw'] for r in block],status='NOT_INFERRED_CLAUSE'))
            i=j
    stats=[]
    for w in m['new_lexicon']:
        rr=[r for r in hits if r['ivtff_group_raw']==w]
        stats.append(dict(raw=w,gloss=m['new_lexicon'][w][0],role=m['new_lexicon'][w][1],ZL3b=sum(r['edition']=='ZL3b' for r in rr),IT2a=sum(r['edition']=='IT2a' for r in rr),RF1b=sum(r['edition']=='RF1b' for r in rr),loci=len({r['locus'] for r in rr}),physical_leaves=len({re.match(r'f(\d+)',r['page'])[1] for r in rr}),independent_meaning_tests=0))
    sol_loci=sorted({r['locus'] for r in hits if r['ivtff_group_raw']=='solkain'})
    variants=[dict(edition=ed,locus=locus,exact_solkain=any(r['ivtff_group_raw']=='solkain' for r in lines[ed,locus]),groups=lines[ed,locus]) for locus in sol_loci for ed in EDS]
    covered=[dict(edition=ed,locus=locus,groups=len(lines[ed,locus]),words=[r['ivtff_group_raw'] for r in lines[ed,locus]],status='LEXICALLY_COVERED_NOT_SEMANTICALLY_CONFIRMED') for ed,locus in sorted(hitkeys) if all(r['ivtff_group_raw'] in lex['R_C'] for r in lines[ed,locus])]
    result=dict(experiment='GDT939',status='FULL_LINE_CONTENT_SUBJECT_DRAFTS_UNSELECTED',source_groups=sum(len(rr) for rr in lines.values()),target_occurrences=len(hits),target_reader_lines=len(hitkeys),target_loci=len({loc for ed,loc in hitkeys}),frame_groups=len(frame),frame_counts=dict(Counter(r['edition'] for r in frame)),frame_alignment_rows=len(alignment),local_alignment_rows=len(local),local_prediction_rows=len(predictions),new_word_values=9,lexicon_size=33,known_target_runs=len(islands),complete_hypothetical_line_readings=12,lexically_covered_reader_lines=len(covered),prediction_groups={'C':['R_C','T_C'],'W':['R_W','T_W']},selected_translation=None,confirmed_words=0,independent_meaning_tests=0,unexposed_confirmation_folios=0,new_admissions=0,semantics_validated=False,significance_claimed=False,factual_inference=False,whole_paragraph_translation_achieved=False,decision='Written content subject makes local W identity about content rather than pipe, conditional on nine new words and local nominal/subject syntax; no independent rescue or semantic winner.')
    return {'NEW_OCCURRENCES.tsv':tsv(occ),'WORD_COUNTS.tsv':tsv(stats),'LEXICONS.json':dump(lex),'FRAME_ALIGNMENT.tsv':tsv(alignment),'LOCAL_ALIGNMENT.tsv':tsv(local),'LOCAL_PREDICTIONS.tsv':tsv(predictions),'TARGET_RUNS.json':dump(islands),'SOLKAIN_VARIANTS.json':dump(variants),'LEXICALLY_COVERED_LINES.json':dump(covered),'RESULT.json':dump(result),**docs}
if __name__=='__main__':
    for name,value in build().items():(EXP/'artifacts'/name).write_text(value)
    print((EXP/'artifacts/RESULT.json').read_text())
