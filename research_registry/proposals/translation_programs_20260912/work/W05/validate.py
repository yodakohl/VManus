"""Validate frozen bytes, exhaustive cases and declared consequences, not meanings."""
import collections,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
E=Path(__file__).resolve().parent;P=E.parent/'W02';W4=E.parent/'W04'
ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(name):return list(csv.DictReader((E/name).open(),delimiter='\t'))
spec=json.loads((E/'SPEC.json').read_text())
for f in spec['inputs']:
    assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
source=json.loads((P/'SOURCE.json').read_text())
expected=[(p['id'],l['locus'],str(i),w) for t in source['targets'] for p in t['hosts']['ZL3b']
          for l in p['lines'] for i,w in enumerate(l['words'],1)]
alignment=read('ALIGNMENT.tsv')
assert [(r['paragraph'],r['locus'],r['index'],r['raw']) for r in alignment]==expected
oldalign=list(csv.DictReader((W4/'ALIGNMENT.tsv').open(),delimiter='\t'))
assert [r['unchanged_W04_C'] for r in alignment]==[r['C'] for r in oldalign]
assert len(alignment)==900 and sum(r['status']=='UNREAD' for r in alignment)==370
assert not any(r[1].startswith('f84') for r in expected)
text=(E/'READING.md').read_text()
for t in source['targets']:
    for l in t['hosts']['ZL3b'][0]['lines']:
        assert text.count(l['locus']+': `'+' '.join(l['words'])+'`')==1
D={r['form']:r for r in csv.DictReader((P/'LEXICON.tsv').open(),delimiter='\t')}
for word,override in spec['word_overrides'].items():D[word]={**D[word],**override}
act=set(spec['action_roles']);mat=set(spec['material_roles']);mod=set(spec['transparent_roles'])
alt=json.loads((P/'ALTERNATE_LINES.json').read_text())['readings']
expected_runs={};expected_ops=set();payload={}
# An independent split-at-every-non-action construction proves census completeness.
for ed,lines in alt.items():
    for l in lines:
        locus=l['metadata']['locus'];words=[g['ivtff_group_raw'] for g in l['groups']];payload[(ed,locus)]=words
        roles=[D.get(w,{}).get('role','OPEN') for w in words]
        bounds=[-1]+[i for i,r in enumerate(roles) if r not in act]+[len(words)]
        for lo,hi in zip(bounds,bounds[1:]):
            if hi-lo-1>=2:
                expected_runs[(ed,locus+':'+str(lo+2)+'-'+str(hi))]=(words,roles,lo+1,hi)
        for i,r in enumerate(roles,1):
            if r in act:
                for v in spec['variants']:expected_ops.add((ed,v,locus+':'+str(i)))
cases=read('ALL_VERB_RUNS.tsv');args=read('ARGUMENTS.tsv')
assert {(r['edition'],r['run']) for r in cases}==set(expected_runs)
assert len(cases)==44
assert {(r['edition'],r['variant'],r['operation']) for r in args}==expected_ops
assert len(args)==903
byarg={(r['edition'],r['variant'],r['operation']):r for r in args}
for c in cases:
    words,roles,start,end=expected_runs[(c['edition'],c['run'])]
    assert c['verbs']==' '.join(words[start:end]) and c['raw_line']==' '.join(words)
    for v in ['J','M']:
        tail_positions=[i for i in range(end,len(words)) if roles[i] not in mod] if v=='M' else list(range(end,len(words)))
        first=tail_positions[0] if tail_positions else len(words)
        eligible=first<len(words) and roles[first] in mat
        assert (c[v+'_status']=='SHARED_EXPLICIT_RIGHT')==eligible
        if eligible:
            assert c[v+'_primary']==c['locus']+':'+str(first+1)
            for op in c['operations'].split(';'):
                assert byarg[(c['edition'],v,op)]['patient']==c[v+'_primary']
        else:
            for op in c['operations'].split(';'):
                for key in ['patient','coingredient','debts']:
                    assert byarg[(c['edition'],v,op)][key]==byarg[(c['edition'],'B',op)][key]
oldargs={r['operation']:r for r in csv.DictReader((W4/'ARGUMENTS.tsv').open(),delimiter='\t') if r['model']=='C'}
for op,old in oldargs.items():
    b=byarg[('ZL3b','B',op)]
    assert all(b[k]==old[k] for k in ['patient','patient_form','rule','coingredient','debts'])
for v in ['J','M']:
    assert byarg[('ZL3b',v,'f6v.14:1')]['patient']=='f6v.14:3'
    assert byarg[('ZL3b',v,'f9v.7:1')]['patient']=='f9v.6:4'
    assert byarg[('ZL3b',v,'f17v.5:1')]['patient']=='f17v.4:1'
    assert byarg[('ZL3b',v,'f24r.12:1')]['coingredient']=='f24r.12:4'
    assert byarg[('ZL3b',v,'f102v2.35:5')]['patient']=='f102v2.35:7'
assert byarg[('ZL3b','J','f6v.7:1')]['patient']=='f6v.6:2'
assert byarg[('ZL3b','M','f6v.7:1')]['patient']=='f6v.7:4'
changed=read('CHANGED_ARGUMENTS.tsv')
for ed in alt:
    for v in ['J','M']:
        actual={(r['operation'],r['patient'],r['coingredient'],r['debts']) for r in args if r['edition']==ed and r['variant']==v
            and any(r[k]!=byarg[(ed,'B',r['operation'])][k] for k in ['patient','coingredient','debts'])}
        assert actual=={(r['operation'],r['new_patient'],r['new_second'],r['new_debts']) for r in changed if r['edition']==ed and r['variant']==v}
qualities=read('QUALITY_ASSERTIONS.tsv')
oldq=[r for r in csv.DictReader((W4/'QUALITY_ASSERTIONS.tsv').open(),delimiter='\t') if r['model']=='C' and r['attachment']=='R']
for v in spec['variants']:
    rows=[r for r in qualities if r['variant']==v]
    assert collections.Counter((r['mention'],r['kind'],r['axis'],r['value'],r['scope']) for r in rows)==collections.Counter((r['mention'],r['kind'],r['axis'],r['value'],r['scope']) for r in oldq)
    assert len(rows)==136 and sum(not r['patient'] for r in rows)==8
    # New phases count actual bound command patients, not merely written action positions.
    for r in rows:
        if r['kind'] in {'BARE_NOMINAL','PROCESSED_NOMINAL'}:assert r['phase']=='0'
        if v=='B':
            old=next(x for x in oldq if x['mention']==r['mention'] and x['axis']==r['axis'])
            assert all(r[k]==old[k] for k in ['patient','patient_form','phase','scope','rule'])
assert next(r for r in qualities if r['variant']=='M' and r['mention']=='f102v2.35:8')['phase']=='2'
assert next(r for r in qualities if r['variant']=='B' and r['mention']=='f102v2.35:8')['phase']=='0'
prior=json.loads((E.parent/'W03/SPEC.json').read_text())
for i,a in enumerate(qualities):
    for b in qualities[i+1:]:
        if not a['patient'] or any(a[k]!=b[k] for k in ['variant','locus','patient','phase','axis','scope']):continue
        assert sorted([a['value'],b['value']]) not in [sorted(p) for p in prior['opposed'][a['axis']]]
assert not read('CONTRADICTIONS.tsv')
# f99r's entire command inventory is unchanged, preserving the earlier SAME-liquid issue.
for v in ['J','M']:
    for op in oldargs:
        if op.startswith('f99r.'):
            assert all(byarg[('ZL3b',v,op)][k]==byarg[('ZL3b','B',op)][k] for k in ['patient','coingredient','debts'])
assert len(read('PARAGRAPH_COVERAGE.tsv'))==13
assert len(read('COMPLETE_ALTERNATE_CASE_LINES.tsv'))==45
assessment=json.loads((E/'ASSESSMENT.json').read_text())
assert assessment['new_global_winner'] is None and assessment['meaning_identifications']==0
validation=dict(status='PASS',executed_utc=datetime.now(timezone.utc).isoformat(),
    checks=['FROZEN_INPUT_BYTES','UNCHANGED_900_WORD_VALUES','EXHAUSTIVE_44_MAXIMAL_RUNS','ALL_903_ARGUMENT_ROWS',
            'REGISTERED_DIRECT_AND_MODIFIER_BARRIERS','COMPLETE_CHANGED_ARGUMENT_REPORT','408_QUALITY_ASSERTIONS',
            'F102_COOL_STATE_PHASE_CHANGE','F99_COMMAND_BINDINGS_UNCHANGED'],
    meaning_confirmation=False,scope='Document fidelity and finite consequences, not semantic truth')
(E/'VALIDATION.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(validation))
