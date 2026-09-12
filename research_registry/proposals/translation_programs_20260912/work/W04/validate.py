"""Check source fidelity and all published consequence claims; not semantic truth."""
import collections,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
E=Path(__file__).resolve().parent;P=E.parent/'W02'
ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(name):return list(csv.DictReader((E/name).open(),delimiter='\t'))
spec=json.loads((E/'SPEC.json').read_text())
for f in spec['input_files']:
    assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'], f['path']
src=json.loads((P/'SOURCE.json').read_text())
paragraphs=[t['hosts']['ZL3b'][0] for t in src['targets']]
expected=[(p['id'],l['locus'],str(i),w) for p in paragraphs for l in p['lines'] for i,w in enumerate(l['words'],1)]
align=read('ALIGNMENT.tsv')
assert [(r['paragraph'],r['locus'],r['index'],r['raw']) for r in align]==expected
assert len(expected)==900 and len(paragraphs)==13 and len({r[1] for r in expected})==152
assert not any(r[1].startswith('f84') for r in expected)
assert sum(r['status']=='UNREAD' for r in align)==370
for r in align:
    for model,changes in spec['variants'].items():
        assert r[model] == (changes[r['raw']] if r['raw'] in changes else r['N'])
        if r['status']=='UNREAD':assert r[model]=='[ungelesen: '+r['raw']+']'
for model in spec['variants']:
    text=(E/('READING_'+model+'.md')).read_text()
    for p in paragraphs:
        for l in p['lines']:
            assert text.count(l['locus']+': `'+' '.join(l['words'])+'`')==1

lex={r['form']:r for r in csv.DictReader((P/'LEXICON.tsv').open(),delimiter='\t')}
args=read('ARGUMENTS.tsv')
action_roles={'ACTION','MIX','REPEAT_ACTION','REPEAT_COOL','ACTION_TYPED'}
for model,changes in spec['variants'].items():
    positions={l+':'+i for _,l,i,w in expected if w in changes or lex.get(w,{}).get('role') in action_roles}
    assert {r['operation'] for r in args if r['model']==model}==positions
old={r['operation']:r for r in csv.DictReader((P/'ARGUMENTS.tsv').open(),delimiter='\t') if r['model']=='A'}
for r in args:
    if r['model']=='N':assert r['patient']==old[r['operation']]['patient']
changes=read('CHANGED_OLD_ARGUMENTS.tsv')
for model in ['C','CT']:
    actual={(r['operation'],r['old_patient'],r['new_patient']) for r in changes if r['model']==model and r['old_patient']!=r['new_patient']}
    assert actual=={('f6v.14:1','f6v.14:3','f6v.13:4'),('f9v.7:1','f9v.7:6','f9v.6:4'),('f17v.5:1','f17v.5:4','f17v.4:1')}
assert not any(r['model']=='T' for r in changes)

alt=json.loads((P/'ALTERNATE_LINES.json').read_text())['readings']
expected_candidates=collections.Counter((ed,m,l['metadata']['locus']+':'+str(i),g['ivtff_group_raw'])
    for ed,lines in alt.items() for m in spec['variants'] for l in lines
    for i,g in enumerate(l['groups'],1) if g['ivtff_group_raw'] in {'chol','oty'})
candidates=read('CANDIDATE_TABLE.tsv')
assert collections.Counter((r['edition'],r['model'],r['position'],r['form']) for r in candidates)==expected_candidates
assert len(candidates)==360
q=read('QUALITY_ASSERTIONS.tsv')
prior=json.loads((E.parent/'W03/SPEC.json').read_text())
expected_features=collections.Counter((model,attachment,locus+':'+i,f['axis'],f['value'])
    for model in spec['variants'] for attachment in ['L','R'] for _,locus,i,w in expected
    for f in prior['features'] if f['form']==w)
assert collections.Counter((r['model'],r['attachment'],r['mention'],r['axis'],r['value']) for r in q)==expected_features
assert len(q)==1088
def one(model,attachment,mention):
    rows=[r for r in q if r['model']==model and r['attachment']==attachment and r['mention']==mention]
    assert len(rows)==1
    return rows[0]
assert one('C','L','f9v.10:4')['patient']==''
assert one('C','L','f19v.9:6')['patient']==''
assert one('C','R','f9v.10:4')['patient']=='f9v.10:2'
assert one('C','R','f9v.10:4')['phase']=='1'
assert one('C','R','f9v.10:1')['phase']=='0'
assert one('C','R','f22v.9:2')['phase']=='0'
assert one('C','R','f22v.9:3')['phase']=='1'
assert one('T','R','f9v.10:1')['phase']==one('T','R','f9v.10:4')['phase']=='1'
opposed={axis:{frozenset(v) for v in vals} for axis,vals in prior['opposed'].items()}
expected_conflicts=[]
for i,a in enumerate(q):
    for b in q[i+1:]:
        if not a['patient'] or any(a[k]!=b[k] for k in ['model','attachment','locus','patient','phase','axis','scope']):continue
        if frozenset([a['value'],b['value']]) in opposed[a['axis']]:
            expected_conflicts.append((a['model'],a['attachment'],a['mention'],b['mention']))
assert collections.Counter(expected_conflicts)==collections.Counter((r['model'],r['attachment'],r['first'],r['second']) for r in read('CONTRADICTIONS.tsv'))
assert len(expected_conflicts)==8
summary=read('MODEL_COMPARISON.tsv')
for r in summary:
    sub=[x for x in q if x['model']==r['model'] and x['attachment']==r['attachment']]
    assert int(r['unbound_quality_assertions'])==sum(not x['patient'] for x in sub)
    assert int(r['conditional_contradictions'])==sum(x[:2]==(r['model'],r['attachment']) for x in expected_conflicts)

dry=read('ALL_DRYING_CONTEXTS.tsv');later=read('LATER_EXACT_MATERIAL_MENTIONS.tsv')
assert len(dry)==24
assert {r['operation'] for r in dry}=={r['operation'] for r in args if r['model']=='C' and r['form']=='chol'}
assert {r['operation'] for r in dry if r['assumed_type']=='EXPLICIT_LIQUID'}=={'f17v.16:2','f99r.48:4'}
assert {r['operation'] for r in dry if r['same_instance_issue']}=={'f99r.48:4'}
for r in dry:
    p=next(p for p in paragraphs if any(l['locus']==r['operation'].rsplit(':',1)[0] for l in p['lines']))
    flat=[(l['locus']+':'+str(i),w) for l in p['lines'] for i,w in enumerate(l['words'],1)]
    offset=next(i for i,x in enumerate(flat) if x[0]==r['operation'])
    actual={x[0] for x in flat[offset+1:] if x[1]==r['form'] and x[0]!=r['patient']}
    assert actual=={x['later_mention'] for x in later if x['operation']==r['operation']}
assessment=json.loads((E/'ASSESSMENT.json').read_text())
assert assessment['working_variant']=='C/R' and assessment['meaning_identifications']==0
assert not assessment['held_access'] and not assessment['significance_claim']
validation=dict(status='PASS',executed_utc=datetime.now(timezone.utc).isoformat(),
    checks=['FROZEN_W02_W03_INPUTS','EXACT_900_GROUP_FOUR_VARIANT_COVERAGE','COMPLETE_360_ALTERNATE_CANDIDATE_ROWS',
            'ALL_COMMAND_POSITIONS_AND_THREE_CHANGED_OLD_PATIENTS','COMPLETE_1088_QUALITY_ASSERTIONS',
            'ALL_SAME_PHASE_OPPOSITIONS','CRITICAL_PHASE_AND_LOST_MODIFIER_CASES','ALL_24_DRYING_CONTINUATIONS'],
    scope='Document fidelity and stated consequences, not independent meaning validation',meaning_confirmation=False)
(E/'VALIDATION.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(validation))
