"""Check source conservation and stipulated consequences, not meaning truth."""
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
ART=EXP/'artifacts'


def read(name):
    return list(csv.DictReader((ART/name).open(),delimiter='\t'))


def main():
    checks=[]
    lock=json.loads((EXP/'MODEL_LOCK.json').read_text())
    for name,digest in lock['files'].items():
        assert hashlib.sha256((EXP/name).read_bytes()).hexdigest()==digest
    prereg=json.loads((EXP/'PREREG_LOCK.json').read_text())
    assert hashlib.sha256((EXP/'PREREGISTRATION.md').read_bytes()).hexdigest()==prereg['preregistration_sha256']
    checks.append('preregistration and post-exposure model/source locks unchanged')
    source=json.loads((ART/'SOURCE.json').read_text())['groups']
    manifest=json.loads((EXP/'src/SOURCE.json').read_text())
    assert hashlib.sha256((ART/'f77r.jpg').read_bytes()).hexdigest()==manifest['image_sha256']
    assert manifest['sealed_data']=={'f84':'FORBIDDEN','f84r':'FORBIDDEN'} and manifest['new_image_admissions']==0
    checks.append('exact already admitted image bytes and explicit seals')
    command=manifest['command']
    assert command[:3]==['./vmanus-exp','query-tsv','experiments/semantic_assumptions/results/source_separator_transcription.tsv']
    allowed=[command[i+1] for i,x in enumerate(command) if x=='--allow']
    assert set(allowed)=={'f77r','f17r','f21r','f32v','f29v'} and command.count('--forbid-prefix')==2
    queried=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=True)
    guarded=list(csv.DictReader(io.StringIO(queried.stdout),delimiter='\t'))
    assert {x['page'] for x in guarded}==set(allowed)
    limits={'f17r':range(4,7),'f21r':range(8,13),'f32v':range(7,12),'f29v':range(1,5)}
    expected=[x for x in guarded if x['page']=='f77r' or int(x['locus'].split('.')[1]) in limits[x['page']]]
    assert expected==source and len({x['source_group_id'] for x in source})==len(source)
    checks.append('fresh selector-first projection equals complete frozen development source')
    by_id={x['source_group_id']:x for x in source}
    by_line=defaultdict(list)
    for x in source:
        assert not x['page'].startswith('f84')
        by_line[x['edition'],x['locus']].append(x)
    for rr in by_line.values():
        rr.sort(key=lambda x:int(x['source_group_index']))
        assert [int(x['source_group_index']) for x in rr]==list(range(1,len(rr)+1))
        assert {int(x['source_group_count']) for x in rr}=={len(rr)}
        assert all(a['right_separator']==b['left_separator'] for a,b in zip(rr,rr[1:]))
    checks.append('whole loci, source group indices, entities and separator continuity')
    model=json.loads((EXP/'src/MODEL.json').read_text())
    base={p['base']:p['id'] for p in model['pairs']}; marked={p['marked']:p['id'] for p in model['pairs']}
    assert set(base)=={'otedy','otol','otaiin','okaiin'} and set(marked)=={'qotedy','qotol','qotaiin','qokaiin'}
    displays={'N':'{}?','L':'zu {} gehörig?','S':'aus/von {}?','T':'zu/in {}?'}
    alignment=read('ALIGNMENT.tsv'); amap={x['source_group_id']:x for x in alignment}
    assert set(amap)==set(by_id) and len(alignment)==len(source)
    blocks=defaultdict(list)
    for sid,a in amap.items():
        r=by_id[sid]; raw=r['ivtff_group_raw']
        for key in ['edition','locus','kind','left_separator','right_separator']:assert a[key]==r[key]
        assert a['raw']==raw and a['group_index']==r['source_group_index']
        for mid,pattern in displays.items():
            expected_display=base[raw]+'?' if raw in base else pattern.format(marked[raw]) if raw in marked else '⟦'+raw+'⟧'
            assert a[mid]==expected_display
        if r['kind']=='P':
            frames=model['paragraph_frames'][r['page']]
            bi=next(i for i,(lo,hi) in enumerate(frames,1) if lo<=int(r['locus'].split('.')[1])<=hi)
            assert a['block']==f"{r['page']}:P{bi}"
            blocks[(r['edition'],a['block'])].append(r)
    checks.append('all four complete alignments preserve every source group with exactly eight proposed forms')
    expected_cases={}
    for rr in blocks.values():
        rr.sort(key=lambda x:(int(x['locus'].split('.')[1]),int(x['source_group_index'])))
        for i,r in enumerate(rr):
            if r['ivtff_group_raw'] not in marked:continue
            left=rr[i-1] if i else None
            status='NO_LEFT_GROUP' if left is None else 'LEFT_IS_MARKED_FORM' if left['ivtff_group_raw'] in marked else 'ASSUMED_BASE_HEAD' if left['ivtff_group_raw'] in base else 'HEAD_UNTRANSLATED'
            expected_cases[r['source_group_id']]=(left,status)
    consequences=read('CONSEQUENCES.tsv')
    assert Counter(x['model'] for x in consequences)==dict.fromkeys(['L','S','T'],len(expected_cases))
    for mid in ['L','S','T']:
        cc=[x for x in consequences if x['model']==mid]
        assert {x['source_group_id'] for x in cc}==set(expected_cases)
        for x in cc:
            left,status=expected_cases[x['source_group_id']]
            assert x['head_source_group_id']==(left['source_group_id'] if left else '')
            assert x['head_raw']==(left['ivtff_group_raw'] if left else '')
            assert x['attachment_status']==status and x['semantic_credit'].startswith('0;')
            pair=marked[by_id[x['source_group_id']]['ivtff_group_raw']]
            endpoint=pair+' (concept, not identified individual)'; head=x['head_source_group_id']
            assert x['proposed_direction']==(endpoint+' -> '+head if mid=='S' else head+' -> '+endpoint)
            assert x['relation']=={'L':'BELONGS_TO','S':'FROM','T':'TO'}[mid]
    checks.append('all proposed relations retain the actual immediate head, including unknowns and blocked marked heads')
    labels=read('LABEL_REUSE.tsv')
    assert {x['source_group_id'] for x in labels}=={r['source_group_id'] for r in source if r['page']=='f77r' and r['kind']!='P'}
    for x in labels:
        rr=[r for r in source if r['edition']==x['edition'] and r['kind']=='P']
        assert set(json.loads(x['exact_prose']))=={r['source_group_id'] for r in rr if r['ivtff_group_raw']==x['raw']}
        assert set(json.loads(x['literal_q_plus_prose']))=={r['source_group_id'] for r in rr if r['ivtff_group_raw']=='q'+x['raw']}
    checks.append('all label groups retained, with literal matches including unselected uncertain single-character cases')
    result=json.loads((ART/'RESULT.json').read_text())
    for ed,counts in result['editions'].items():
        rr=[r for r in source if r['edition']==ed]
        known=sum(r['ivtff_group_raw'] in base or r['ivtff_group_raw'] in marked for r in rr)
        assert counts['source_groups']==len(rr) and counts['hypothesis_groups']==known and counts['untranslated_groups']==len(rr)-known
        cc=[x for x in consequences if x['edition']==ed and x['model']=='S']
        assert counts['marked_occurrences']==len(cc) and counts['attachment_statuses']==dict(Counter(x['attachment_status'] for x in cc))
    assert result['confirmed_translated_words']==0 and not result['scientific_meanings_validated']
    assert result['model_selected_as_translation'] is None and not result['reserved_pages_opened']
    checks.append('reported coverage, unresolved obligations and semantic ceiling match the complete rows')
    packet=read('RELATION_PACKET.tsv'); members=json.loads((ART/'PACKET_MEMBERS.json').read_text())
    assert len(packet)==10 and sum(map(len,members.values()))==11
    assert all(r['eligibility_status'].startswith('INELIGIBLE_') for r in packet)
    gate=subprocess.run(['./vmanus-exp','check-edge-packet',str((ART/'RELATION_PACKET.tsv').relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True)
    gd=json.loads(gate.stdout)
    assert gd==json.loads((ART/'EDGE_GATE.json').read_text()) and not gd['score_ready'] and gd['eligible_edges']==0
    assert all('formal access is not sealed' in x for x in gd['errors'])
    assert not any(gd[k] for k in ['capacity_gate_50_edges_5_folios','holdout_gate','mobile_null_gate'])
    checks.append('GDT388 intake remains ineligible with failed capacity/holdout/null gates; no semantic score')
    replay=subprocess.run(['python',str(EXP/'src/run.py'),'--check'],capture_output=True,text=True)
    assert replay.returncode==0,replay.stderr
    checks.append('all generated artifacts replay byte-identically')
    out={'status':'PASS','checks':checks,'meaning_validated':False,'independent_reviewer':False,
         'coverage':'Source, contract and mechanical consequences only; root authored builder and validator.'}
    (ART/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':'PASS','check_groups':len(checks),'meaning_validated':False}))


if __name__=='__main__':main()
