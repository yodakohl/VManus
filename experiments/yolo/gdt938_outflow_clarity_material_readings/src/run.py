"""Four fixed content drafts; exact admitted occurrences and complete cached paragraphs."""
from pathlib import Path
from collections import Counter, defaultdict
import csv, hashlib, io, json, re
EXP=Path(__file__).resolve().parents[1]; ROOT=EXP.parents[2]
EDS=['ZL3b','IT2a','RF1b']
def dump(x): return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def tsv(rows):
    s=io.StringIO(); w=csv.DictWriter(s,list(rows[0]),delimiter='\t',lineterminator='\n'); w.writeheader(); w.writerows(rows); return s.getvalue()
def join(rr,fn):
    return ''.join(('' if i==0 else {'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // '}[r['left_separator']])+fn(r) for i,r in enumerate(rr))
def read(p): return json.loads((ROOT/p).read_text())
def load():
    for p,h in json.loads((EXP/'PREREG_LOCK.json').read_text())['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    m=json.loads((EXP/'src/MODEL.json').read_text()); spec=read(m['inventory_spec']); allowed=set(read(spec['allow_source'])['allowed_selectors'])
    assert len(allowed)==179 and not any(p.startswith('f84') for p in allowed)
    lines={}; sourcefiles={}
    for path in spec['sources']:
        d=read(path)
        for line in d['lines']:
            meta=line['metadata']; assert meta['page'] in allowed and not meta['page'].startswith('f84')
            key=meta['edition'],meta['locus']; assert key not in lines
            lines[key]=[dict(**meta,**dict(zip(d['group_columns'],g))) for g in line['groups']]; sourcefiles[key]=path
    base=read(m['base_model'])['models']['M']['lexicon']; inherited={mid:dict(base) for mid in m['base_models']}
    for path in m['extensions']:
        ext=read(path)['models']
        for mid in inherited:
            assert not inherited[mid].keys() & ext[mid]['lexicon'].keys()
            inherited[mid].update(ext[mid]['lexicon'])
    lex={mid+'_'+cid:dict(words,**content['lexicon']) for mid,words in inherited.items() for cid,content in m['content_models'].items()}
    assert all(len(x)==24 for x in lex.values())
    return m,lines,sourcefiles,lex,inherited

def build():
    m,lines,sourcefiles,lex,inherited=load(); targets=set(m['targets'])
    hits=[r for rr in lines.values() for r in rr if r['ivtff_group_raw'] in targets]
    hitkeys={(r['edition'],r['locus']) for r in hits}
    paragraphs=[]; memberships=defaultdict(list)
    for ed,pp in read(m['paragraph_source']).items():
        for p in pp:
            if not any((ed,l['locus']) in hitkeys for l in p['lines']): continue
            for l in p['lines']:
                rr=lines[ed,l['locus']]
                assert [r['source_group_id'] for r in rr]==l['source_ids']
                assert [r['ivtff_group_raw'] for r in rr]==l['words']
                memberships[ed,l['locus']].append(p['id'])
            paragraphs.append(dict(edition=ed,**p))
    documents={}; targetrows=[]; summary=[]
    for ed in EDS:
        doc=[f'# GDT938 — alle Zielkontexte {ed}', '', 'Alle deutschen Werte sind Hypothesen; ? markiert Wortannahmen, ⟦…⟧ offene Rohgruppen. / unsicherer Abstand; // Zeichnungsunterbrechung.', 'Vollständige verfügbare Zielabsätze, anschließend sämtliche noch nicht abgedeckten Trefferzeilen. Keine Zeile ist ein unabhängiger Bedeutungsbeleg.', '']
        shown=set()
        def render(locus):
            rr=lines[ed,locus]; raw=join(rr,lambda r:r['ivtff_group_raw'])
            doc.extend([f'### {locus}','','`'+raw+'`',''])
            for cid,words in lex.items(): doc.extend([cid+': '+join(rr,lambda r:words[r['ivtff_group_raw']][0]+'?' if r['ivtff_group_raw'] in words else '⟦'+r['ivtff_group_raw']+'⟧'),''])
            shown.add((ed,locus))
        for p in paragraphs:
            if p['edition']!=ed: continue
            doc.extend(['## Ganzer Absatz '+p['id'],''])
            for l in p['lines']: render(l['locus'])
        for e,locus in sorted(hitkeys):
            if e==ed and (e,locus) not in shown:
                doc.extend(['## Vollständige Trefferzeile; kein vollständiger Absatz im verwendeten Absatzpaket','']);render(locus)
        documents['CONTEXTS_'+ed+'.md']='\n'.join(doc).rstrip()+'\n'
    for cid,words in lex.items():
        for r in hits:
            key=r['edition'],r['locus']; rr=lines[key]; i=rr.index(r); gloss,role=words[r['ivtff_group_raw']]
            targetrows.append(dict(candidate=cid,edition=r['edition'],page=r['page'],locus=r['locus'],source_group_id=r['source_group_id'],raw=r['ivtff_group_raw'],gloss=gloss,role=role,left_raw=rr[i-1]['ivtff_group_raw'] if i else '',right_raw=rr[i+1]['ivtff_group_raw'] if i+1<len(rr) else '',left_separator=r['left_separator'],right_separator=r['right_separator'],paragraph_ids='|'.join(memberships[key]),source_path=sourcefiles[key],full_raw_line=join(rr,lambda x:x['ivtff_group_raw']),full_model_line=join(rr,lambda x:words[x['ivtff_group_raw']][0]+'?' if x['ivtff_group_raw'] in words else '⟦'+x['ivtff_group_raw']+'⟧'),full_line_unread=sum(x['ivtff_group_raw'] not in words for x in rr),assessment='FIXED_WORD_APPLIED; CONTENT_AND_REFERENTS_NOT_INDEPENDENTLY_BOUND'))
        content=m['content_models'][cid.split('_')[1]]
        for ed in EDS:
            b=[r for r in lines[ed,m['local_locus']] if int(r['source_group_index']) in m['local_group_indices']]
            assert [r['ivtff_group_raw'] for r in b]==m['local_block']
            summary.append(dict(candidate=cid,edition=ed,prediction_group=cid.split('_')[1],raw=join(b,lambda r:r['ivtff_group_raw']),word_alignment=join(b,lambda r:words[r['ivtff_group_raw']][0]),hypothetical_sentence=content['sentence'],optically_clear=content['consequences']['optically_clear'],water_identity=content['consequences']['water_identity'],unmixed=True,known_groups=len(b),f_scope='CONDITIONAL_ON_UNREAD_A',p_scope='OUTSIDE_THIS_SPECIFIED_CONDITION',factual_inference=False,empirically_selected=False,independent_meaning_tests=0))
    small=read(m['source'])['groups']; smalllines=defaultdict(list)
    alignment=[]
    for r in small:smalllines[r['edition'],r['locus']].append(r)
    for cid,words in lex.items():
        for r in small:
            gloss,role=words.get(r['ivtff_group_raw'],['⟦'+r['ivtff_group_raw']+'⟧','UNREAD'])
            alignment.append(dict(candidate=cid,**r,gloss=gloss,role=role))
    for ed in EDS:
        doc=[f'# GDT938 — ganzer GDT930-Arbeitsrahmen {ed}','','Alle Wortwerte hypothetisch. / unsicherer Abstand; // Zeichnungsunterbrechung. Keine Quellgruppe weggelassen.','']
        for (e,locus),rr in smalllines.items():
            if e!=ed:continue
            rr=sorted(rr,key=lambda r:int(r['source_group_index']))
            doc.extend(['## '+locus,'','`'+join(rr,lambda r:r['ivtff_group_raw'])+'`',''])
            for cid,words in lex.items():doc.extend([cid+': '+join(rr,lambda r:words[r['ivtff_group_raw']][0]+'?' if r['ivtff_group_raw'] in words else '⟦'+r['ivtff_group_raw']+'⟧'),''])
        documents['WORKING_READING_'+ed+'.md']='\n'.join(doc).rstrip()+'\n'
    # All target-containing runs with >=2 consecutive hypothesized groups, as navigation only.
    islands=[]
    for ed,locus in sorted(hitkeys):
        rr=lines[ed,locus]; start=0
        while start<len(rr):
            if rr[start]['ivtff_group_raw'] not in lex['R_C']:start+=1;continue
            end=start+1
            while end<len(rr) and rr[end]['ivtff_group_raw'] in lex['R_C'] and rr[end-1]['right_separator']==rr[end]['left_separator']=='DEFINITE_SPACE':end+=1
            block=rr[start:end]
            if len(block)>=2 and any(r['ivtff_group_raw'] in targets for r in block):
                islands.append(dict(edition=ed,locus=locus,ids=[r['source_group_id'] for r in block],words=[r['ivtff_group_raw'] for r in block],readings={cid:[words[r['ivtff_group_raw']][0] for r in block] for cid,words in lex.items()},status='NAVIGATION_ONLY_NOT_INFERRED_SYNTAX'))
            start=end
    counts={ed:{w:sum(r['edition']==ed and r['ivtff_group_raw']==w for r in hits) for w in m['targets']} for ed in EDS}
    result=dict(experiment='GDT938',status='TWO_FULL_B_CONTENT_DRAFTS_UNSELECTED',counts=counts,target_occurrences=len(hits),candidate_occurrence_rows=len(targetrows),target_reader_lines=len(hitkeys),target_loci=len({r['locus'] for r in hits}),target_leaves={w:len({re.match(r'f(\d+)',r['page'])[1] for r in hits if r['ivtff_group_raw']==w}) for w in m['targets']},target_loci_by_word={w:len({r['locus'] for r in hits if r['ivtff_group_raw']==w}) for w in m['targets']},complete_paragraph_readings=len(paragraphs),paragraph_counts=dict(Counter(p['edition'] for p in paragraphs)),complete_paragraph_groups=sum(p['groups'] for p in paragraphs),target_reader_lines_without_complete_paragraph=sum(not memberships[k] for k in hitkeys),working_source_groups=len(small),working_alignment_rows=len(alignment),local_summary_rows=len(summary),fixed_lexicon_size=24,base_lexicon_size=21,prediction_groups={'C':['R_C','T_C'],'W':['R_W','T_W']},target_islands=len(islands),selected_translation=None,confirmed_words=0,independent_meaning_tests=0,unexposed_confirmation_folios=0,new_admissions=0,significance_claimed=False,semantics_validated=False,factual_inference=False,scope_selection=False,whole_paragraph_translation_achieved=False)
    assessment=json.loads((EXP/'src/ASSESSMENT.json').read_text())
    grouped=defaultdict(list)
    for item in islands: grouped[item['locus'],' '.join(item['words'])].append(item['edition'])
    assert {words for locus,words in grouped}==set(assessment['notes'])
    audit=['# GDT938 — Inhaltsaudit aller mehrgliedrigen gelesenen Zielabschnitte','',f"Alle{len(islands)} Abschnitte ({len(grouped)} Locus/Rohfolgen;{len(assessment['notes'])} verschiedene Rohfolgen) sind aufgeführt. Diese Abschnitte sind keine erkannten Sätze. Ganze Kontexte stehen in CONTEXTS_*.md. Einzelzielstellen bleiben vollständig in TARGET_OCCURRENCES.tsv und haben keine ausreichende gelesene Umgebung.",'','| Locus | Lesungen | Ganze Rohfolge des Abschnitts | Bedingte Folgerung und offene Schuld |','|---|---|---|---|']
    for (locus,words),eds in grouped.items(): audit.append('| '+locus+' | '+','.join(eds)+' | `'+words+'` | '+assessment['notes'][words]+' |')
    documents['SEMANTIC_AUDIT.md']='\n'.join(audit)+'\n'
    inventory={'hits':hits,'target_lines':[{'edition':ed,'locus':loc,'source_path':sourcefiles[ed,loc],'groups':lines[ed,loc]} for ed,loc in sorted(hitkeys)],'complete_paragraphs':paragraphs}
    return {'INVENTORY.json':dump(inventory),'LEXICONS.json':dump(lex),'TARGET_OCCURRENCES.tsv':tsv(targetrows),'LOCAL_PREDICTIONS.tsv':tsv(summary),'WORKING_ALIGNMENT.tsv':tsv(alignment),'TARGET_ISLANDS.json':dump(islands),'RESULT.json':dump(result),**documents}
if __name__=='__main__':
    for name,value in build().items():(EXP/'artifacts'/name).write_text(value)
    print((EXP/'artifacts/RESULT.json').read_text())
