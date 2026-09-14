"""Independently scan whole-frame antecedents and every retained interval."""
from collections import Counter,defaultdict
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];ART=EXP/'artifacts'


def main():
    lock=json.loads((EXP/'PREREG_LOCK.json').read_text())
    for name,digest in lock['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    spec=json.loads((EXP/'src/MODEL.json').read_text())
    source=json.loads((ROOT/spec['source']).read_text())['groups'];assert len(source)==1408
    frames=json.loads((ROOT/spec['frames']).read_text())['paragraph_frames']
    models=json.loads((ROOT/spec['lexicons']).read_text())['models']
    baseline={(r['model'],r['source_group_id']):r for r in csv.DictReader((ROOT/spec['baseline_bindings']).open(),delimiter='\t')}
    blocks=defaultdict(list)
    for r in source:
        assert r['page'] in ('f77r','f17r','f21r','f32v','f29v') and not r['page'].startswith('f84')
        if r['kind']!='P':continue
        n=int(r['locus'].split('.')[1]);matches=[i for i,(lo,hi) in enumerate(frames[r['page']],1) if lo<=n<=hi]
        assert len(matches)==1
        blocks[r['edition'],r['page']+':P'+str(matches[0])].append(r)
    for rr in blocks.values():rr.sort(key=lambda r:(int(r['locus'].split('.')[1]),int(r['source_group_index'])))
    refs=list(csv.DictReader((ART/'REFERENCE_CASES.tsv').open(),delimiter='\t'))
    bykey={(r['policy'],r['model'],r['source_group_id']):r for r in refs}
    expected=set()
    intervals=json.loads((ART/'INTERVALS.json').read_text())
    for (ed,bid),rr in blocks.items():
        for mid,m in models.items():
            lex=m['lexicon'];roles=[lex.get(r['ivtff_group_raw'],('', 'UNREAD'))[1] for r in rr]
            ids=[r['source_group_id'] for r in rr];where={sid:i for i,sid in enumerate(ids)}
            def ismat(j):return roles[j]=='MATERIAL' or (roles[j]=='PART' and j+1<len(rr) and roles[j+1]=='GENITIVE')
            def expected_flow(policy,i):
                if policy=='LOCAL':head=where.get(baseline[mid,ids[i]]['head_id'])
                else:
                    candidates=[j for j in range(i-1,-1,-1) if (ismat(j) if policy=='TYPED_BACK' else roles[j] in ('MATERIAL','VESSEL','PLACE','PART'))]
                    head=candidates[0] if candidates else None
                status='NO_ANTECEDENT' if head is None else 'COMPATIBLE' if ismat(head) else 'TYPE_CONFLICT' if roles[head] in ('VESSEL','PLACE') else 'UNRESOLVED_NOMINAL_TYPE'
                return head,status
            for i,r in enumerate(rr):
                role=roles[i]
                if role not in ('FLOW','CONTINUATION'):continue
                for policy in spec['policies']:
                    key=(policy,mid,ids[i]);expected.add(key);x=bykey[key]
                    if role=='FLOW':head,status=expected_flow(policy,i);participant=head
                    else:
                        if policy=='LOCAL':head=where.get(baseline[mid,ids[i]]['head_id'])
                        else:
                            prior=[j for j in range(i-1,-1,-1) if roles[j]=='FLOW'];head=prior[0] if prior else None
                        if head is None:participant=None;status='NO_FLOW_ANTECEDENT'
                        else:
                            participant,status=expected_flow(policy,head)
                            if status!='COMPATIBLE':status='FLOW_'+status
                    assert (x['edition'],x['block'],x['locus'],x['role'],x['raw'])==(ed,bid,r['locus'],role,r['ivtff_group_raw'])
                    assert x['head_id']==(ids[head] if head is not None else '')
                    assert x['participant_id']==(ids[participant] if participant is not None else '')
                    assert x['status']==status and x['meaning_confirmed']=='False'
                    if policy!='LOCAL':
                        assert head is None or head<i
                        assert participant is None or participant<i
                    def between(pos):return list(range(min(pos,i)+1,max(pos,i))) if pos is not None else []
                    hg=between(head);pg=between(participant)
                    assert intervals[x['case_id']]=={'head_gap':[ids[j] for j in hg],'participant_gap':[ids[j] for j in pg]}
                    for name,pos,gap in [('head',head,hg),('participant',participant,pg)]:
                        assert x[name+'_gap_groups']==(str(len(gap)) if pos is not None else '')
                        assert x['unknown_'+name+'_gap_groups']==(str(sum(roles[j]=='UNREAD' for j in gap)) if pos is not None else '')
                    audit=pg if participant is not None else hg
                    assert json.loads(x['intervening_bare_nominals'])==[ids[j] for j in audit if roles[j] in ('MATERIAL','VESSEL','PLACE','PART')]
                    assert json.loads(x['intervening_copulas'])==[ids[j] for j in audit if roles[j]=='COPULA']
                    assert json.loads(x['material_mentions_after_flow'])==([ids[j] for j in hg if ismat(j)] if role=='CONTINUATION' else [])
                    path=i+1 if role=='FLOW' and i+1<len(rr) and roles[i+1] in ('SOURCE','GOAL') else None
                    assert x['immediate_path_id']==(ids[path] if path is not None else '')
    assert len(refs)==len(bykey)==len(expected)==450 and set(bykey)==expected
    assert len(intervals)==450
    for ed in ('ZL3b','IT2a','RF1b'):
        doc=(ART/('P2_P3_READING_'+ed+'.md')).read_text()
        assert doc.count('## f77r.')==24
        for n in range(25,49):
            rr=sorted([r for r in source if (r['edition'],r['locus'])==(ed,'f77r.'+str(n))],key=lambda r:int(r['source_group_index']))
            raw=''.join(('' if i==0 else ' / ' if 'UNCERTAIN' in r['left_separator'] else ' ')+r['ivtff_group_raw'] for i,r in enumerate(rr))
            assert '`'+raw+'`' in doc
    critical=bykey['TYPED_BACK','M','ZL3b|f77r.42|G001']
    assert critical['participant_id']=='ZL3b|f77r.38|G008' and critical['unknown_participant_gap_groups']=='24'
    assert bykey['NOMINAL_BACK','M','ZL3b|f77r.42|G001']['status']=='TYPE_CONFLICT'
    assert bykey['TYPED_BACK','V','ZL3b|f77r.42|G001']['participant_id']==''
    assert json.loads(bykey['TYPED_BACK','V','ZL3b|f77r.36|G006']['material_mentions_after_flow'])==['ZL3b|f77r.35|G002']
    result=json.loads((ART/'RESULT.json').read_text())
    assert not result['lexicons_changed'] and result['new_words']==result['confirmed_words']==0 and result['selected_translation'] is None
    for mid,eds in result['models'].items():
        for ed,policies in eds.items():
            for policy,counts in policies.items():
                aa=[r for r in refs if (r['model'],r['edition'],r['policy'])==(mid,ed,policy)]
                for role,label in [('FLOW','flow_status'),('CONTINUATION','continuation_status')]:assert counts[label]==dict(Counter(r['status'] for r in aa if r['role']==role))
                assert counts['compatible_with_unread_gap']==sum(r['status']=='COMPATIBLE' and int(r['unknown_participant_gap_groups'] or 0)>0 for r in aa)
    subprocess.run([sys.executable,str(EXP/'src/run.py'),'--check'],check=True,capture_output=True)
    out={'status':'PASS','source_groups':1408,'reference_cases':450,'complete_target_loci':72,'lexicons_changed':False,
         'coverage':'all three policies, source IDs, antecedents, raw intervals, unknown counts, competitors, no retroactive V repair, complete P2/P3 raw lines, byte replay',
         'meaning_validated':False,'independent_reviewer':False}
    (ART/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))


if __name__=='__main__':main()
