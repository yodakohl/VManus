"""Independent raw-prefix reconstruction; no import from build.py."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent
R=H.parents[4]
def read(name): return list(csv.DictReader((H/name).open(),delimiter='\t'))
model=json.loads((H/'MODEL.json').read_text());manifest=json.loads((H/'SOURCE.json').read_text())
for item in manifest['files']: assert hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256']
source=list(csv.DictReader((R/manifest['files'][0]['path']).open(),delimiter='\t'))
raw=[]
for line in source:
    assert line['page']=='f83r'
    raw.extend((line['record_id'],line['locus'],str(i),line['locus']+':'+str(i),w) for i,w in enumerate(line['zl3b_line'].split(),1))
assert len(raw)==341 and len(source)==51
inp=read('INPUT.tsv');keys=['record','locus','position','source','word']
assert [tuple(g[k] for k in keys) for g in inp]==raw
names={'shedy':'Flüssigkeit','lchedy':'Zusatzstoff','qokaiin':'Gefäß','sol':'Ansatz'}
descriptions={'solkeedy':'zuvor erwärmter Ansatz','solchedy':'zuvor filtrierter Ansatz'}
assert model['names']==names and model['descriptions']==descriptions
materials={'shedy','lchedy','sol',*descriptions};verbs={'chedy','qokeedy'}
def prior_at(i): return [g for g in raw[:i] if g[0]==raw[i][0]]
def describe(i,v):
    g=raw[i];word=g[4]
    if word in descriptions: return word,descriptions[word]
    if word=='sol':
        types=set(x[4] for x in prior_at(i) if x[4] in descriptions)
        q=next(iter(types)) if v=='K' and len(types)==1 else 'AMBIGUOUS' if v=='K' and len(types)>1 else 'UNKNOWN'
        return q,descriptions[q] if q in descriptions else 'Ansatz [Qualifikation '+('mehrdeutig' if q=='AMBIGUOUS' else 'offen')+']'
    return 'UNKNOWN',names[word]
indices={g[3]:i for i,g in enumerate(raw)}
for v in ['K','W']:
    align=read('ALIGNMENT_'+v+'.tsv');actions=read('ACTIONS_'+v+'.tsv');refs=read('REFERENCES_'+v+'.tsv')
    assert [tuple(g[k] for k in keys) for g in align]==raw
    assert [a['source'] for a in actions]==[g[3] for g in raw if g[4] in verbs]
    assert [a['source'] for a in refs]==[g[3] for g in raw if g[4]=='sol']
    for row in refs:
        i=indices[row['source']];prior=[x for x in prior_at(i) if x[4] in descriptions]
        types=list(dict.fromkeys(x[4] for x in prior));expected='INDEPENDENT_WORD' if v=='W' else 'MISSING_INTRODUCTION' if not types else 'LICENSED' if len(types)==1 else 'AMBIGUOUS'
        assert row['license']==expected
        assert row['introduction_types']==(','.join(types) or 'NONE')
        assert row['introduction_sources']==(','.join(x[3] for t in types for x in prior if x[4]==t) or 'NONE')
        assert (row['qualification'],row['render'])==describe(i,v)
    for a in actions:
        i=indices[a['source']];before=prior_at(i);patients=[g for g in before if g[4] in materials];vessels=[g for g in before if g[4]=='qokaiin'];need=a['word']=='qokeedy'
        patient=patients[-1] if patients else None;dest=vessels[-1][3] if need and vessels else 'NONE'
        assert a['patient_source']==(patient[3] if patient else 'NONE') and a['destination_source']==dest
        q,desc=describe(indices[patient[3]],v) if patient else ('NA','NONE')
        assert a['qualification']==q and a['patient_description']==desc
        missing=[]
        if not patient: missing.append('MATERIAL')
        if need and dest=='NONE': missing.append('DESTINATION')
        assert a['status']==('MISSING_'+'_AND_'.join(missing) if missing else 'COMPLETE')
    for g,a in zip(raw,align):
        w=g[4];role='MATERIAL' if w in materials else 'DESTINATION' if w=='qokaiin' else 'ACTION' if w in verbs else 'OPEN'
        assert a['role']==role
        if role=='MATERIAL': assert (a['qualification'],a['render'])==describe(indices[g[3]],v)
        if role=='OPEN': assert a['render']=='['+w+' — offen]'
        assert (w+' → '+a['render']) in (H/('READING_'+v+'.md')).read_text()
fams=read('SOL_FORMS.tsv');assert {f['word'] for f in fams}=={g[4] for g in raw if g[4].startswith('sol')}
for f in fams:
    obs=[g[3] for g in raw if g[4]==f['word']];assert int(f['count'])==len(obs) and f['sources']==','.join(obs)
k=read('ACTIONS_K.tsv');w=read('ACTIONS_W.tsv');changed=read('CHANGED_ACTIONS.tsv')
assert [a['action_source'] for a in changed]==[a['source'] for a,b in zip(k,w) if a['qualification']!=b['qualification']]
for row,a,b in zip(read('HISTORY_AUDIT.tsv'),k,w):
    i=indices[a['source']];p=a['patient_source'];priorheat=[g[3] for g in raw[:i] if g[0]==raw[i][0] and g[4]=='chedy' and p!='NONE' and next((x[3] for x in reversed(prior_at(indices[g[3]])) if x[4] in materials),'NONE')==p]
    def facts(action):
        out={'HEATED'} if priorheat else set()
        if action['qualification']=='solkeedy': out.add('HEATED')
        if action['qualification']=='solchedy': out.add('FILTERED')
        return out
    assert row['earlier_explicit_heat']==(','.join(priorheat) or 'NONE')
    assert row['K_history']==(','.join(sorted(facts(a))) or 'UNKNOWN')
    assert row['W_history']==(','.join(sorted(facts(b))) or 'UNKNOWN')
    assert row['additional_K_history']==(','.join(sorted(facts(a)-facts(b))) or 'NONE')
res=json.loads((H/'RESULT.json').read_text());assert res['K_licenses']==dict(Counter(x['license'] for x in read('REFERENCES_K.tsv')))
assert res['actions_with_changed_qualification']==len(changed)==5
assert res['actions_with_additional_history']==sum(x['additional_K_history']!='NONE' for x in read('HISTORY_AUDIT.tsv'))==3
assert res['hypothetical_positions']==sum(a['role']!='OPEN' for a in read('ALIGNMENT_K.tsv'))==60
assert res['open_positions']==281 and res['action_statuses']==dict(Counter(x['status'] for x in k))
report={'status':'PASS','source_hashes':3,'raw_groups_per_reading':341,'readings':2,'actions_checked':40,'short_reference_rows':14,'whole_sol_forms':8,'changed_qualifications':5,'nonredundant_history_differences':3,'limits':'Independent code reconstruction only; no meaning, identity, unobserved ambiguity or held-page validation'}
(H/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
