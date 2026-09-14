"""Fixed whole-line hypotheses and exhaustive conditional complement test; no training."""
from pathlib import Path
from collections import Counter
import csv,io,json,hashlib,re
EXP=Path(__file__).resolve().parents[1]; ROOT=EXP.parents[2]
EDS=['ZL3b','IT2a','RF1b']
SEP={'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // ','DRAWING_INTERRUPTION_UNALIGNED':' ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ '}
def read(p):return json.loads((ROOT/p).read_text())
def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def tsv(rows):
    f=io.StringIO();w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return f.getvalue()
def join(rr,fn):return ''.join(('' if i==0 else SEP[r['left_separator']])+fn(r) for i,r in enumerate(rr))
def leaf(page):return re.match(r'f(\d+)',page)[1]
def load():
    m=read(str(EXP.relative_to(ROOT)/'src/MODEL.json'));lock=read(str(EXP.relative_to(ROOT)/'PREREG_LOCK.json'))
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    spec=read(m['inventory_spec']);allow=set(read(spec['allow_source'])['allowed_selectors'])
    assert len(allow)==179 and not any(x.startswith('f84') or x=='f116v' for x in allow)
    lines={};paths={}
    for p in spec['sources']:
        d=read(p)
        for line in d['lines']:
            meta=line['metadata'];assert meta['page'] in allow and not meta['page'].startswith('f84')
            key=meta['edition'],meta['locus'];assert key not in lines
            lines[key]=[dict(**meta,**dict(zip(d['group_columns'],g))) for g in line['groups']];paths[key]=p
    old=read(m['prior_lexicons']);lex={cid:dict(words,**m['new_lexicon']) for cid,words in old.items()}
    assert all(len(w)==33 and not w.keys() & m['new_lexicon'].keys() for w in old.values())
    return m,lines,paths,lex

def obligation(rr,i,cid,words,m):
    r=rr[i];rule=m['transfer_rules'][r['ivtff_group_raw']];j=i+1;used=False;span=[r];head=None
    while True:
        if j==len(rr):status='OPEN';reason='LINE_END';break
        n=rr[j]
        if rr[j-1]['right_separator']!='DEFINITE_SPACE' or n['left_separator']!='DEFINITE_SPACE':status='OPEN';reason='UNCERTAIN_BOUNDARY';break
        span.append(n)
        if not used and rule['optional'] and n['ivtff_group_raw']==rule['optional']:
            used=True;j+=1;continue
        head=n
        if n['ivtff_group_raw'] not in words:status='OPEN';reason='UNREAD_HEAD'
        elif words[n['ivtff_group_raw']][1] in m['nominal_roles']:status='COMPATIBLE';reason='KNOWN_NOMINAL'
        else:status='CONFLICT';reason='KNOWN_NONNOMINAL'
        break
    hgloss,hrole=words.get(head['ivtff_group_raw'],['','UNREAD']) if head else ['','']
    return dict(candidate=cid,edition=r['edition'],page=r['page'],physical_leaf=leaf(r['page']),locus=r['locus'],trigger_id=r['source_group_id'],trigger=r['ivtff_group_raw'],rule=rule['id'],status=status,reason=reason,span_ids='|'.join(x['source_group_id'] for x in span),raw_span=join(span,lambda x:x['ivtff_group_raw']),head_id=head['source_group_id'] if head else '',head_raw=head['ivtff_group_raw'] if head else '',head_gloss=hgloss,head_role=hrole,partition='DESIGN_LEAF_111' if leaf(r['page'])=='111' else 'OTHER_EXPOSED_LEAF',meaning_status='CONDITIONAL_ON_FIXED_WORDS_AND_SYNTAX')

def build():
    m,lines,paths,lex=load();targets=set(m['new_lexicon'])
    hits=[r for rr in lines.values() for r in rr if r['ivtff_group_raw'] in targets];keys={(r['edition'],r['locus']) for r in hits}
    occ=[]
    for r in hits:
        key=r['edition'],r['locus'];rr=lines[key];i=rr.index(r);gloss,role=m['new_lexicon'][r['ivtff_group_raw']]
        occ.append(dict(edition=r['edition'],page=r['page'],physical_leaf=leaf(r['page']),locus=r['locus'],source_group_id=r['source_group_id'],raw=r['ivtff_group_raw'],gloss=gloss,role=role,left_raw=rr[i-1]['ivtff_group_raw'] if i else '',right_raw=rr[i+1]['ivtff_group_raw'] if i+1<len(rr) else '',left_separator=r['left_separator'],right_separator=r['right_separator'],source_path=paths[key],applies_to=','.join(lex),meaning_status='HYPOTHESIS_ONLY'))
    docs={};framealignment=[];local=[];pred=[]
    for ed in EDS:
        for kind,selected in [('TARGET_LINES',sorted(l for e,l in keys if e==ed)),('FRAME',[f'f111v.{n}' for n in range(1,26)])]:
            doc=[f'# GDT940 — {kind} {ed}','','Alle Wortwerte hypothetisch. ? = angenommener Wert; ⟦…⟧ = ungelesene Rohgruppe. / unsicherer Abstand; // Zeichnungsunterbrechung; ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ nicht ausgerichtete Unterbrechung. FRAME: ZL/IT ganzer bestehender Absatz, RF nur entsprechendes Vergleichsfenster. TARGET_LINES sind ganze Zeilen, keine behaupteten ganzen Absätze.','']
            for locus in selected:
                rr=lines[ed,locus];doc+=['## '+locus,'','`'+join(rr,lambda r:r['ivtff_group_raw'])+'`','']
                for cid,words in lex.items():
                    doc+=[cid+': '+join(rr,lambda r:words[r['ivtff_group_raw']][0]+'?' if r['ivtff_group_raw'] in words else '⟦'+r['ivtff_group_raw']+'⟧'),'']
                    if kind=='FRAME':
                        for r in rr:
                            gloss,role=words.get(r['ivtff_group_raw'],['⟦'+r['ivtff_group_raw']+'⟧','UNREAD'])
                            framealignment.append(dict(candidate=cid,**r,gloss=gloss,role=role))
            docs[kind+'_'+ed+'.md']='\n'.join(doc).rstrip()+'\n'
        rr=lines[ed,m['locus']];assert [r['ivtff_group_raw'] for r in rr]==m['expected_words'][ed]
        for cid,words in lex.items():
            for r,slot in zip(rr,m['local_roles']):
                gloss,role=words.get(r['ivtff_group_raw'],['⟦'+r['ivtff_group_raw']+'⟧','UNREAD'])
                local.append(dict(candidate=cid,edition=ed,source_group_id=r['source_group_id'],raw=r['ivtff_group_raw'],left_separator=r['left_separator'],gloss=gloss,lexical_role=role,proposed_slot=slot,binding_status='LOCAL_HYPOTHESIS' if role!='UNREAD' else 'UNBOUND_VARIANT'))
            gaps=[r['ivtff_group_raw'] for r in rr if r['ivtff_group_raw'] not in words]
            pred.append(dict(candidate=cid,edition=ed,prediction_group=cid.split('_')[1],source_groups=len(rr),assigned=len(rr)-len(gaps),unread='|'.join(gaps),complete_local_sentence=m['sentences'][cid.split('_')[1]] if not gaps else '',status='COMPLETE_LOCAL_HYPOTHESIS' if not gaps else 'INCOMPLETE_READER_VARIANT',subject_id=rr[1]['source_group_id'],same_material_as_line17='UNBOUND',aperture_identity='UNBOUND',other_vessel_reference='UNBOUND',empirically_selected=False))
    tests=[obligation(rr,i,cid,words,m) for key,rr in sorted(lines.items()) for i,r in enumerate(rr) if r['ivtff_group_raw'] in m['transfer_rules'] for cid,words in lex.items()]
    summaries=[];candidates=[]
    for cid in lex:
        ct=[t for t in tests if t['candidate']==cid];conflicts=sum(t['status']=='CONFLICT' for t in ct)
        for raw,rule in m['transfer_rules'].items():
            tt=[t for t in ct if t['trigger']==raw];external=[t for t in tt if t['partition']=='OTHER_EXPOSED_LEAF' and t['status']!='OPEN']
            summaries.append(dict(candidate=cid,trigger=raw,rule=rule['id'],occurrences=len(tt),compatible=sum(t['status']=='COMPATIBLE' for t in tt),conflicts=sum(t['status']=='CONFLICT' for t in tt),open=sum(t['status']=='OPEN' for t in tt),testable_other_physical_leaves=len({t['physical_leaf'] for t in external}),conflict_loci=len({t['locus'] for t in tt if t['status']=='CONFLICT'}),unexposed_confirmation_leaves=0,independent_meaning_tests=0))
        cap=all(x['testable_other_physical_leaves']>=2 for x in summaries if x['candidate']==cid)
        status='REJECT_FIXED_NOMINAL_EXTENSION' if conflicts else 'EXPLORATORY_COMPATIBILITY_ONLY' if cap else 'INSUFFICIENT_TRANSFER_CAPACITY'
        candidates.append(dict(candidate=cid,local_IT2a=m['sentences'][cid.split('_')[1]],local_ZL3b_assigned=next(p['assigned'] for p in pred if p['candidate']==cid and p['edition']=='ZL3b'),local_IT2a_assigned=next(p['assigned'] for p in pred if p['candidate']==cid and p['edition']=='IT2a'),local_RF1b_assigned=next(p['assigned'] for p in pred if p['candidate']==cid and p['edition']=='RF1b'),transfer_conflicts=conflicts,transfer_compatible=sum(t['status']=='COMPATIBLE' for t in ct),transfer_open=sum(t['status']=='OPEN' for t in ct),decision=status,remaining_ambiguity='words vs immediate nominal syntax; R/T and C/W not independently selected',unexposed_confirmation_leaves=0,independent_meaning_tests=0))
    counts=[]
    for w,(gloss,role) in m['new_lexicon'].items():
        hh=[r for r in hits if r['ivtff_group_raw']==w]
        counts.append(dict(raw=w,gloss=gloss,role=role,**{ed:sum(r['edition']==ed for r in hh) for ed in EDS},loci=len({r['locus'] for r in hh}),physical_leaves=len({leaf(r['page']) for r in hh}),independent_meaning_tests=0))
    grouped={}
    for t in tests:
        if t['status']=='OPEN':continue
        k=(t['candidate'],t['trigger'],t['raw_span'],t['head_role'],t['status'])
        grouped.setdefault(k,[]).append(t)
    patterns=[dict(candidate=k[0],trigger=k[1],raw_span=k[2],head_role=k[3],status=k[4],reader_occurrences=len(tt),loci='|'.join(sorted({t['locus'] for t in tt})),source_ids='|'.join(t['trigger_id'] for t in tt),interpretation='CONTRACT_ONLY_NOT_WORD_REFUTATION') for k,tt in sorted(grouped.items())]
    recurrence_loci=sorted({t['locus'] for t in tests if t['raw_span']=='o l r' and t['trigger']=='o'})
    variants=[dict(edition=ed,locus=locus,groups=lines[ed,locus],status='POSTHOC_RECURRENCE_CONTEXT_NOT_SEMANTIC_CONFIRMATION') for locus in recurrence_loci for ed in EDS]
    result=dict(experiment='GDT940',status='REJECT_FIXED_NOMINAL_EXTENSION' if all(c['transfer_conflicts'] for c in candidates) else 'SEE_CANDIDATES',source_groups=sum(len(rr) for rr in lines.values()),target_occurrences=len(hits),target_reader_lines=len(keys),target_loci=len({l for e,l in keys}),new_word_values=10,lexicon_size=43,local_alignment_rows=len(local),frame_alignment_rows=len(framealignment),obligation_rows=len(tests),obligation_trigger_positions=len(tests)//4,candidates=candidates,local_prediction_groups={'C':['R_C','T_C'],'W':['R_W','T_W']},confirmed_words=0,independent_meaning_tests=0,unexposed_confirmation_folios=0,new_admissions=0,semantics_validated=False,significance_claimed=False,selected_translation=None,whole_paragraph_translation_achieved=False)
    return {'CONTRACT_PATTERNS.tsv':tsv(patterns),'OLR_VARIANTS.json':dump(variants),'NEW_OCCURRENCES.tsv':tsv(occ),'WORD_COUNTS.tsv':tsv(counts),'LEXICONS.json':dump(lex),'FRAME_ALIGNMENT.tsv':tsv(framealignment),'LOCAL_ALIGNMENT.tsv':tsv(local),'LOCAL_PREDICTIONS.tsv':tsv(pred),'TRANSFER_OBLIGATIONS.tsv':tsv(tests),'TRANSFER_SUMMARY.tsv':tsv(summaries),'CANDIDATE_DECISIONS.tsv':tsv(candidates),'RESULT.json':dump(result),**docs}
if __name__=='__main__':
    for name,value in build().items():(EXP/'artifacts'/name).write_text(value)
    print((EXP/'artifacts/RESULT.json').read_text())
