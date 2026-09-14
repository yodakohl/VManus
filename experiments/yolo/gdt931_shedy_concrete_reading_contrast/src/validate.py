"""Independently check coverage, constant values and all immediate attachments."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
ART = EXP/'artifacts'


def read_tsv(name):
    with (ART/name).open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def main():
    lock = json.loads((EXP/'PREREG_LOCK.json').read_text())
    for path, digest in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest
    model = json.loads((EXP/'src/MODEL.json').read_text())
    source = json.loads((ROOT/model['source']).read_text())['groups']
    prior = json.loads((ROOT/model['prior_model']).read_text())
    originals = {r['source_group_id']:r for r in source}
    alignment = read_tsv('ALIGNMENT.tsv')
    aligned = {r['source_group_id']:r for r in alignment}
    assert len(alignment)==len(source)==len(aligned)==1408
    assert set(aligned)==set(originals)
    nominal = {}
    marked = set()
    for p in prior['pairs']:
        nominal[p['base']] = nominal[p['marked']] = p['id']+'?'
        marked.add(p['marked'])
    for sid,a in aligned.items():
        r=originals[sid]
        for k in ('edition','page','locus','kind','source_group_index','ivtff_group_raw','left_separator','right_separator'):
            assert a[k]==str(r[k]),(sid,k)
        assert not a['page'].startswith('f84') and a['page']!='f116v'
        number=int(a['locus'].split('.')[1])
        if a['kind']=='P':
            frames=[i for i,(lo,hi) in enumerate(prior['paragraph_frames'][a['page']],1) if lo<=number<=hi]
            assert len(frames)==1 and a['block']==a['page']+':P'+str(frames[0])
        else:
            assert a['block']==a['locus']+':LABEL'
        for mid,gloss in model['readings'].items():
            raw=a['ivtff_group_raw']
            assert a[mid]==(gloss+'?' if raw=='shedy' else nominal.get(raw,'⟦'+raw+'⟧'))
    cases=read_tsv('SHEDY_CASES.tsv')
    expected={sid for sid,a in aligned.items() if a['ivtff_group_raw']=='shedy'}
    assert {c['source_group_id'] for c in cases}==expected and len(cases)==30
    assert Counter(c['edition'] for c in cases)=={'ZL3b':12,'IT2a':12,'RF1b':6}
    neighbors={}
    for a in alignment:
        rr=sorted([x for x in alignment if (x['edition'],x['block'])==(a['edition'],a['block'])],
                  key=lambda x:(int(x['locus'].split('.')[1]),int(x['source_group_index'])))
        i=next(i for i,x in enumerate(rr) if x['source_group_id']==a['source_group_id'])
        neighbors[a['source_group_id']]={'LEFT':rr[i-1] if i and a['kind']=='P' else None,
            'RIGHT':rr[i+1] if i+1<len(rr) and a['kind']=='P' else None}
    for c in cases:
        for side in ('LEFT','RIGHT'):
            n=neighbors[c['source_group_id']][side]
            assert c[side.lower()+'_id']==(n['source_group_id'] if n else '')
            assert c[side.lower()+'_raw']==(n['ivtff_group_raw'] if n else '')
        assert c['semantic_participant_confirmed']=='False'
    attachments=read_tsv('ATTACHMENTS.tsv')
    target_ids={sid for sid,a in aligned.items() if a['ivtff_group_raw'] in marked and a['kind']=='P'}
    assert len(attachments)==2*len(target_ids)==172
    assert {(a['source_group_id'],a['direction']) for a in attachments}=={(sid,d) for sid in target_ids for d in ('LEFT','RIGHT')}
    for a in attachments:
        n=neighbors[a['source_group_id']][a['direction']]
        raw=n['ivtff_group_raw'] if n else ''
        expected=('BOUNDARY' if n is None else 'MARKED_HEAD' if raw in marked else
                  'SHEDY_HYPOTHESIS' if raw=='shedy' else 'BASE_HYPOTHESIS' if raw in nominal else 'UNTRANSLATED_HEAD')
        assert a['status']==expected and a['head_raw']==raw
        assert a['head_id']==(n['source_group_id'] if n else '')
    result=json.loads((ART/'RESULT.json').read_text())
    assert result['selected_translation'] is None and result['confirmed_words']==0
    assert not result['reserved_pages_opened'] and not result['visual_relation_evidence_added']
    for ed,totals in result['editions'].items():
        aa=[a for a in alignment if a['edition']==ed]
        cc=[c for c in cases if c['edition']==ed]
        assert totals['source_groups']==len(aa) and totals['shedy_occurrences']==len(cc)
        assert totals['candidate_positions']==sum(a['ivtff_group_raw'] in nominal or a['ivtff_group_raw']=='shedy' for a in aa)
        assert totals['adjacent_nominated_nominal']==sum(bool(c['left_nominal'] or c['right_nominal']) for c in cc)
        for direction in ('LEFT','RIGHT'):
            assert totals['directed_head_statuses'][direction]==dict(Counter(a['status'] for a in attachments if a['edition']==ed and a['direction']==direction))
    subprocess.run([sys.executable,str(EXP/'src/run.py'),'--check'],check=True,capture_output=True)
    validation={'status':'PASS','source_groups':1408,'target_occurrences':30,'directed_attachment_cases':172,
                'coverage':'locked sources; all raw groups and exact target cases; both immediate neighbors; constant candidate values; counts; byte replay',
                'independent_reviewer':False,'meaning_validated':False}
    (ART/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(validation))


if __name__=='__main__':
    main()
