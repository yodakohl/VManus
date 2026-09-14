"""Two fixed joint readings and censored local argument audit; no fitted decoder."""
import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path

EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
ART=EXP/'artifacts'
EDS=['ZL3b','IT2a','RF1b']
PAGES=['f77r','f17r','f21r','f32v','f29v']


def table(rows):
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows);return out.getvalue()


def build():
    lock=json.loads((EXP/'PREREG_LOCK.json').read_text())
    for path,digest in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    model=json.loads((EXP/'src/MODEL.json').read_text())
    prior=json.loads((ROOT/model['frames']).read_text())
    source=json.loads((ROOT/model['source']).read_text())['groups']
    source=sorted(source,key=lambda r:(EDS.index(r['edition']),PAGES.index(r['page']),int(r['locus'].split('.')[1]),int(r['source_group_index'])))
    blocks=defaultdict(list);lines=defaultdict(list)
    for r in source:
        n=int(r['locus'].split('.')[1])
        frames=[i for i,(lo,hi) in enumerate(prior['paragraph_frames'][r['page']],1) if lo<=n<=hi] if r['kind']=='P' else []
        assert r['kind']!='P' or len(frames)==1
        r=dict(r,block=r['page']+':P'+str(frames[0]) if frames else r['locus']+':LABEL')
        blocks[r['edition'],r['block']].append(r);lines[r['edition'],r['locus']].append(r)
    alignment=[];bindings=[];targets=[];runs=[];duplicates=[]
    for mid,m in model['models'].items():
        lex=m['lexicon']
        for (ed,bid),rr in blocks.items():
            run_for={};current=[]
            for i,r in enumerate(rr):
                if r['kind']=='P' and r['ivtff_group_raw'] in lex:current.append(i)
                else:
                    if current:
                        for j in current:run_for[j]=current
                        current=[]
            if current:
                for j in current:run_for[j]=current
            seen=set()
            for i,r in enumerate(rr):
                raw=r['ivtff_group_raw'];value,role=lex.get(raw,('⟦'+raw+'⟧','UNREAD'))
                a={k:r[k] for k in ('source_group_id','edition','page','locus','kind','block','source_group_index','ivtff_group_raw','left_separator','right_separator')}
                a.update(model=mid,reading=value+'?' if role!='UNREAD' else value,role=role)
                alignment.append(a)
                run=run_for.get(i,[])
                run_id=rr[run[0]]['source_group_id'] if run else ''
                if run_id and run_id not in seen:
                    seen.add(run_id);runs.append({'model':mid,'edition':ed,'block':bid,'run_id':run_id,
                        'source_ids':json.dumps([rr[j]['source_group_id'] for j in run]),
                        'raw':' '.join(rr[j]['ivtff_group_raw'] for j in run),
                        'boundary_meaning':'lexical-censoring, not sentence boundary'})
                if raw=='qokeedy' and i+1<len(rr) and rr[i+1]['ivtff_group_raw']==raw:
                    duplicates.append({'model':mid,'edition':ed,'first_id':r['source_group_id'],
                        'second_id':rr[i+1]['source_group_id'],'role':role,'run_id':run_id,
                        'interpretation':'two written positions; construction and event identity unresolved'})
                if r['kind']=='P' and role in ('FLOW','CONTINUATION'):
                    eligible=[]
                    for j in run:
                        candidate_role=lex[rr[j]['ivtff_group_raw']][1]
                        material=(candidate_role=='MATERIAL' or (mid=='V' and candidate_role=='PART' and
                            j+1 in run and lex[rr[j+1]['ivtff_group_raw']][1]=='GENITIVE'))
                        if (role=='FLOW' and material) or (role=='CONTINUATION' and candidate_role=='FLOW'):
                            eligible.append(j)
                    left=[j for j in eligible if j<i];right=[j for j in eligible if j>i]
                    chosen=max(left) if left else min(right) if right else None
                    head=rr[chosen] if chosen is not None else None
                    binding={'model':mid,'edition':ed,'source_group_id':r['source_group_id'],'locus':r['locus'],
                        'group_index':r['source_group_index'],'raw':raw,'role':role,'run_id':run_id,
                        'head_id':head['source_group_id'] if head else '',
                        'head_raw':head['ivtff_group_raw'] if head else '',
                        'status':'HYPOTHETICAL_HEAD_BOUND' if head else 'UNRESOLVED_IN_KNOWN_RUN',
                        'head_cross_line':bool(head and head['locus']!=r['locus']),
                        'meaning_confirmed':False}
                    bindings.append(binding)
                    if raw=='qokeedy':
                        target=dict(binding)
                        target['left_raw']=rr[i-1]['ivtff_group_raw'] if i else ''
                        target['right_raw']=rr[i+1]['ivtff_group_raw'] if i+1<len(rr) else ''
                        target['run_raw']=' '.join(rr[j]['ivtff_group_raw'] for j in run)
                        target['full_raw_line']=' '.join(x['ivtff_group_raw'] for x in lines[ed,r['locus']])
                        targets.append(target)
    result={'experiment':'GDT932','status':'JOINT_CLAUSE_CANDIDATES_EXPLORATORY_UNDERDETERMINED',
        'source_groups':len(source),'models':{},'selected_translation':None,'confirmed_words':0,
        'independent_meaning_tests':0,'statistical_significance_claimed':False,'new_admissions':0,
        'reserved_pages_opened':False,'visual_relation_evidence_added':False,
        'binding_ceiling':'constant hypothesis roles and source IDs; unknowns censor local probe, not sentence boundaries or refutation'}
    for mid in model['models']:
        result['models'][mid]={}
        for ed in EDS:
            bb=[b for b in bindings if b['model']==mid and b['edition']==ed]
            flows=[b for b in bb if b['role']=='FLOW'];cont=[b for b in bb if b['role']=='CONTINUATION']
            flowmap={b['source_group_id']:b for b in flows}
            result['models'][mid][ed]={'hypothesis_groups':sum(a['model']==mid and a['edition']==ed and a['role']!='UNREAD' for a in alignment),
                'flow_positions':len(flows),'flows_with_material':sum(bool(b['head_id']) for b in flows),
                'continuation_positions':len(cont),'continuations_with_flow':sum(bool(b['head_id']) for b in cont),
                'continuations_with_flow_and_material':sum(bool(b['head_id'] and flowmap[b['head_id']]['head_id']) for b in cont),
                'qokeedy_doublets':sum(d['model']==mid and d['edition']==ed for d in duplicates)}
    decision=json.loads((EXP/'src/DEVELOPMENT_DECISION.json').read_text())
    result['development_seed']=decision['development_seed']
    result['development_choice_stage']=decision['stage']
    clauses=[]
    for candidate in json.loads((EXP/'src/CLAUSE_HYPOTHESES.json').read_text()):
        for ed in EDS:
            rr=lines[ed,candidate['locus']]
            if candidate['selection']=='last5':rr=rr[-5:]
            raw=[r['ivtff_group_raw'] for r in rr]
            for mid,m in model['models'].items():
                clauses.append({'edition':ed,'model':mid,'locus':candidate['locus'],
                    'selection':candidate['selection'],'source_ids':json.dumps([r['source_group_id'] for r in rr]),
                    'raw':' '.join(raw),'groups':len(rr),'mapped_groups':sum(x in m['lexicon'] for x in raw),
                    'exact_candidate_sequence':raw==candidate['expected'],
                    'hypothetical_german':candidate[mid],
                    'status':'ALL_CANDIDATE_WORDS_PRESENT_NOT_CONFIRMED' if raw==candidate['expected'] else 'SOURCE_VARIANTS_LEAVE_DRAFT_PARTIAL',
                    'added_syntax':candidate['added_syntax']})
    out={'CLAUSES.tsv':table(clauses),'ALIGNMENT.tsv':table(alignment),'BINDINGS.tsv':table(bindings),'QOKEEDY_CASES.tsv':table(targets),
         'KNOWN_RUNS.tsv':table(runs),'QOKEEDY_DOUBLETS.tsv':table(duplicates),
         'RESULT.json':json.dumps(result,indent=2,ensure_ascii=False)+'\n'}
    for ed in EDS:
        doc=[f'# GDT932 — vollständige Quellausrichtung {ed}','',
             'M: Stoff und Fließvorgang; V: Anteil und Fortsetzung. Alle neun Wortwerte hypothetisch.',
             '⟦…⟧ bleibt ungelesen; ? kennzeichnet eine Setzung. Keine vollständig gelesenen Absätze.','']
        for (reader,locus),rr in lines.items():
            if reader!=ed:continue
            raw=''.join(('' if i==0 else ' / ' if 'UNCERTAIN' in r['left_separator'] else ' ')+r['ivtff_group_raw'] for i,r in enumerate(rr))
            doc+=['## '+locus+' — '+rr[0]['block'],'',f'`{raw}`','']
            for mid in model['models']:
                aa=[a for a in alignment if (a['edition'],a['locus'],a['model'])==(ed,locus,mid)]
                doc+=[mid+': '+' '.join(a['reading'] for a in aa),'']
        out['READING_'+ed+'.md']='\n'.join(doc).rstrip()+'\n'
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for name,content in build().items():
        if args.check:assert (ART/name).read_text()==content,name
        else:(ART/name).write_text(content)
    print((ART/'RESULT.json').read_text())


if __name__=='__main__':main()
