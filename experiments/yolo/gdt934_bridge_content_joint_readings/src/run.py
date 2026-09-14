"""Render three frozen content hypotheses, keeping all source groups and gaps."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,io,json,hashlib
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2]
EDS=['ZL3b','IT2a','RF1b'];PAGES=['f77r','f17r','f21r','f32v','f29v']

def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def tsv(rows):
    s=io.StringIO();w=csv.DictWriter(s,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue()
def join(rr,fn):
    out=[]
    for i,r in enumerate(rr):
        if i: out.append({'DEFINITE_SPACE':' ', 'UNCERTAIN_SMALL_SPACE':' / ', 'DRAWING_INTERRUPTION':' // '}[r['left_separator']])
        out.append(fn(r))
    return ''.join(out)

def build():
    for name in ['PREREG_LOCK.json','MODEL_LOCK.json']:
        for p,h in json.loads((EXP/name).read_text())['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    m=json.loads((EXP/'src/MODEL.json').read_text())
    src=json.loads((ROOT/m['source']).read_text())['groups']
    src=sorted(src,key=lambda r:(EDS.index(r['edition']),PAGES.index(r['page']),int(r['locus'].split('.')[1]),int(r['source_group_index'])))
    frames=json.loads((ROOT/m['frames']).read_text())['paragraph_frames']
    base=json.loads((ROOT/m['base_model']).read_text())['models']['M']['lexicon']
    lex={k:dict(base,**v['lexicon']) for k,v in m['models'].items()}
    lines=defaultdict(list)
    for r in src:lines[r['edition'],r['locus']].append(r)
    alignment=[];cases=[];counts={};documents={}
    for mid in m['models']:
        for r in src:
            gloss,role=lex[mid].get(r['ivtff_group_raw'],['⟦'+r['ivtff_group_raw']+'⟧','UNREAD'])
            item=dict(model=mid,**r,gloss=gloss,role=role)
            alignment.append(item)
            if r['ivtff_group_raw'] in m['targets']:
                rr=lines[r['edition'],r['locus']];i=rr.index(r)
                cases.append(dict(model=mid,edition=r['edition'],source_group_id=r['source_group_id'],locus=r['locus'],raw=r['ivtff_group_raw'],gloss=gloss,role=role,left_raw=rr[i-1]['ivtff_group_raw'] if i else '',right_raw=rr[i+1]['ivtff_group_raw'] if i+1<len(rr) else '',left_separator=r['left_separator'],right_separator=r['right_separator'],full_line=join(rr,lambda x:x['ivtff_group_raw']),full_model_line=join(rr,lambda x:lex[mid].get(x['ivtff_group_raw'],['⟦'+x['ivtff_group_raw']+'⟧'])[0]),assessment='EXPOSED_HYPOTHESIS_NOT_CONFIRMED'))
    for e in EDS:
        rr=[r for r in src if r['edition']==e];ct=Counter(r['ivtff_group_raw'] for r in rr)
        counts[e]={'source_groups':len(rr),'new_hypothesis_positions':sum(ct[t] for t in m['targets']),'target_counts':{t:ct[t] for t in m['targets']},'baseline_known':sum(r['ivtff_group_raw'] in base for r in rr),'with_extension_known':sum(r['ivtff_group_raw'] in lex['R'] for r in rr)}
        d=[f'# GDT934 — vollständige Quellausrichtung {e}', '', 'R=Sammlung/Verbleib, T=Sammlung/Abfluss, Q=trüb/klar. Alle deutschen Werte sind Hypothesen.', 'Rohgruppen bleiben erhalten: / = unsicherer kleiner Abstand; // = Zeichnungsunterbrechung. Kein deutscher Fließtext für unbekannte Gruppen.', 'Die drei Erweiterungen benutzen unverändert GDT932-M; V bleibt offene Gegenlesung.', '']
        lastblock=None
        for (ed,locus),lr in lines.items():
            if ed!=e:continue
            r=lr[0];n=int(locus.split('.')[1])
            bs=[i for i,(lo,hi) in enumerate(frames[r['page']],1) if lo<=n<=hi] if r['kind']=='P' else []
            block=r['page']+':P'+str(bs[0]) if bs else r['locus']+':LABEL'
            if block!=lastblock:d.extend([f'## {block}','']);lastblock=block
            d.extend([f'### {locus}', '', '`'+join(lr,lambda x:x['ivtff_group_raw'])+'`',''])
            for mid in m['models']:d.extend([mid+': '+join(lr,lambda x:lex[mid][x['ivtff_group_raw']][0]+'?' if x['ivtff_group_raw'] in lex[mid] else '⟦'+x['ivtff_group_raw']+'⟧'),''])
        documents[f'READING_{e}.md']='\n'.join(d).rstrip()+'\n'
    result={'experiment':'GDT934','status':'THREE_EXPOSED_BRIDGE_CONTENT_HYPOTHESES_UNSELECTED','source_groups':len(src),'all_alignment_rows':len(alignment),'target_occurrences':len(cases)//3,'candidate_occurrence_rows':len(cases),'counts':counts,'target_pages':sorted(set(r['locus'].split('.')[0] for r in cases)),'target_loci':sorted(set(r['locus'] for r in cases),key=lambda x:int(x.split('.')[1])),'selected_translation':None,'confirmed_words':0,'independent_meaning_tests':0,'unexposed_confirmation_folios':0,'new_admissions':0,'significance_claimed':False,'semantics_validated':False,'meaning_selection_by_counts':False,'base_V_changed':False}
    return {'ALIGNMENT.tsv':tsv(alignment),'CANDIDATE_OCCURRENCES.tsv':tsv(cases),'RESULT.json':dump(result),**documents}

if __name__=='__main__':
    for name,text in build().items():(EXP/'artifacts'/name).write_text(text)
    print((EXP/'artifacts/RESULT.json').read_text())
