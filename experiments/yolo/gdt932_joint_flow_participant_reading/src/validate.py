"""Independent source/role/interval checks, not semantic confirmation."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];ART=EXP/'artifacts'


def read(name):
    with (ART/name).open() as f:return list(csv.DictReader(f,delimiter='\t'))


def main():
    for name,digest in json.loads((EXP/'PREREG_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    model=json.loads((EXP/'src/MODEL.json').read_text())
    source=json.loads((ROOT/model['source']).read_text())['groups']
    originals={r['source_group_id']:r for r in source}
    alignment=read('ALIGNMENT.tsv')
    assert len(originals)==1408 and len(alignment)==2816
    assert Counter((r['model'],r['source_group_id']) for r in alignment)==Counter((mid,sid) for mid in ('M','V') for sid in originals)
    frames=json.loads((ROOT/model['frames']).read_text())['paragraph_frames']
    for a in alignment:
        src=originals[a['source_group_id']]
        for key in ('edition','page','locus','kind','source_group_index','ivtff_group_raw','left_separator','right_separator'):
            assert a[key]==str(src[key])
        assert not a['page'].startswith('f84') and a['page']!='f116v'
        if a['kind']=='P':
            n=int(a['locus'].split('.')[1]);indices=[i for i,(lo,hi) in enumerate(frames[a['page']],1) if lo<=n<=hi]
            assert len(indices)==1 and a['block']==a['page']+':P'+str(indices[0])
        else:assert a['block']==a['locus']+':LABEL'
        definition=model['models'][a['model']]['lexicon'].get(a['ivtff_group_raw'])
        assert a['reading']==(definition[0]+'?' if definition else '⟦'+a['ivtff_group_raw']+'⟧')
        assert a['role']==(definition[1] if definition else 'UNREAD')
    bindings=read('BINDINGS.tsv');index={(a['model'],a['source_group_id']):a for a in alignment}
    expected={(a['model'],a['source_group_id']) for a in alignment if a['kind']=='P' and a['role'] in ('FLOW','CONTINUATION')}
    assert {(b['model'],b['source_group_id']) for b in bindings}==expected and len(bindings)==len(expected)==150
    for b in bindings:
        a=index[b['model'],b['source_group_id']]
        block=sorted([x for x in alignment if (x['model'],x['edition'],x['block'])==(a['model'],a['edition'],a['block'])],
                     key=lambda x:(int(x['locus'].split('.')[1]),int(x['source_group_index'])))
        pos=next(i for i,x in enumerate(block) if x['source_group_id']==a['source_group_id'])
        lo=pos;hi=pos
        while lo>0 and block[lo-1]['role']!='UNREAD':lo-=1
        while hi+1<len(block) and block[hi+1]['role']!='UNREAD':hi+=1
        candidates=[]
        for j in list(range(pos-1,lo-1,-1))+list(range(pos+1,hi+1)):
            r=block[j]
            if a['role']=='CONTINUATION':eligible=r['role']=='FLOW'
            else:eligible=r['role']=='MATERIAL' or (a['model']=='V' and r['role']=='PART' and j<hi and block[j+1]['role']=='GENITIVE')
            if eligible:candidates.append(r)
        head=candidates[0] if candidates else None
        assert b['head_id']==(head['source_group_id'] if head else '')
        assert b['head_raw']==(head['ivtff_group_raw'] if head else '')
        assert b['head_cross_line']==str(bool(head and head['locus']!=a['locus']))
        assert b['status']==('HYPOTHETICAL_HEAD_BOUND' if head else 'UNRESOLVED_IN_KNOWN_RUN')
        assert b['meaning_confirmed']=='False'
    targets=read('QOKEEDY_CASES.tsv')
    target_expected={(mid,sid) for mid in ('M','V') for sid,r in originals.items() if r['ivtff_group_raw']=='qokeedy' and r['kind']=='P'}
    assert {(q['model'],q['source_group_id']) for q in targets}==target_expected and len(targets)==120
    for q in targets:
        row=next(b for b in bindings if (b['model'],b['source_group_id'])==(q['model'],q['source_group_id']))
        assert all(q[k]==v for k,v in row.items())
        rawline=sorted([r for r in source if (r['edition'],r['locus'])==(q['edition'],q['locus'])],key=lambda r:int(r['source_group_index']))
        assert q['full_raw_line']==' '.join(r['ivtff_group_raw'] for r in rawline)
    doublets=read('QOKEEDY_DOUBLETS.tsv')
    assert len(doublets)==18
    for d in doublets:
        first=originals[d['first_id']];second=originals[d['second_id']]
        assert first['edition']==second['edition']==d['edition']
        assert first['ivtff_group_raw']==second['ivtff_group_raw']=='qokeedy'
        assert first['locus']==second['locus'] and int(second['source_group_index'])==int(first['source_group_index'])+1
    scenarios=json.loads((EXP/'src/CLAUSE_HYPOTHESES.json').read_text())
    prereg=(EXP/'PREREGISTRATION.md').read_text()
    for s in scenarios:
        for mid in ('M','V'):assert s[mid] in prereg
    clauses=read('CLAUSES.tsv');assert len(clauses)==12
    for c in clauses:
        s=next(s for s in scenarios if s['locus']==c['locus'])
        rr=sorted([r for r in source if (r['edition'],r['locus'])==(c['edition'],c['locus'])],key=lambda r:int(r['source_group_index']))
        if s['selection']=='last5':rr=rr[-5:]
        assert json.loads(c['source_ids'])==[r['source_group_id'] for r in rr]
        assert c['raw']==' '.join(r['ivtff_group_raw'] for r in rr)
        assert c['hypothetical_german']==s[c['model']]
        assert int(c['groups'])==len(rr)
        assert int(c['mapped_groups'])==sum(r['ivtff_group_raw'] in model['models'][c['model']]['lexicon'] for r in rr)
        assert c['exact_candidate_sequence']==str([r['ivtff_group_raw'] for r in rr]==s['expected'])
    result=json.loads((ART/'RESULT.json').read_text())
    assert result['selected_translation'] is None and result['confirmed_words']==0 and not result['reserved_pages_opened']
    assert result['development_seed']=='M' and result['development_choice_stage']=='AFTER_RESULTS_OPERATIONAL_CHOICE'
    for mid,editions in result['models'].items():
        for ed,counts in editions.items():
            bb=[b for b in bindings if (b['model'],b['edition'])==(mid,ed)]
            flows={b['source_group_id']:b for b in bb if b['role']=='FLOW'}
            cont=[b for b in bb if b['role']=='CONTINUATION']
            assert counts['flow_positions']==len(flows)
            assert counts['flows_with_material']==sum(bool(b['head_id']) for b in flows.values())
            assert counts['continuation_positions']==len(cont)
            assert counts['continuations_with_flow']==sum(bool(b['head_id']) for b in cont)
            assert counts['continuations_with_flow_and_material']==sum(bool(b['head_id'] and flows[b['head_id']]['head_id']) for b in cont)
    subprocess.run([sys.executable,str(EXP/'src/run.py'),'--check'],check=True,capture_output=True)
    out={'status':'PASS','source_groups':1408,'aligned_group_readings':2816,'all_qokeedy_readings':120,'argument_obligations':150,
         'candidate_clause_displays':12,'checks':'source/locks/constants; every eligible obligation and nearest censored head; clause source completeness and preregistered text; exact replay',
         'meaning_validated':False,'independent_reviewer':False}
    (ART/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))


if __name__=='__main__':main()
