"""Independent source census and fixed-value/coverage checks; no semantic certification."""
from pathlib import Path
from collections import Counter
import csv, hashlib, json
import run
EXP=Path(__file__).resolve().parents[1]; ROOT=EXP.parents[2]; ART=EXP/'artifacts'
read=lambda p:json.loads(p.read_text())
m=read(EXP/'src/MODEL.json'); lock=read(EXP/'PREREG_LOCK.json')
for p,h in lock['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
spec=read(ROOT/m['inventory_spec']); allow=set(read(ROOT/spec['allow_source'])['allowed_selectors'])
assert len(allow)==179 and not any(x.startswith('f84') or x=='f116v' for x in allow)
source={}; rawlines={}; paths={}
for p in spec['sources']:
    d=read(ROOT/p)
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==spec['hashes'][p]
    for line in d['lines']:
        meta=line['metadata']; assert meta['page'] in allow and not meta['page'].startswith('f84')
        key=meta['edition'],meta['locus']; assert key not in rawlines
        rr=[dict(**meta,**dict(zip(d['group_columns'],g))) for g in line['groups']]
        rawlines[key]=rr; paths[key]=p
        for r in rr: assert r['source_group_id'] not in source; source[r['source_group_id']]=r
expected={sid:r for sid,r in source.items() if r['ivtff_group_raw'] in ['qoteey','sheey','dalchedy']}
assert len(source)==96184 and len(expected)==500
assert Counter((r['edition'],r['ivtff_group_raw']) for r in expected.values())==Counter({('ZL3b','qoteey'):40,('IT2a','qoteey'):40,('RF1b','qoteey'):41,('ZL3b','sheey'):126,('IT2a','sheey'):128,('RF1b','sheey'):111,('ZL3b','dalchedy'):5,('IT2a','dalchedy'):4,('RF1b','dalchedy'):5})
inv=read(ART/'INVENTORY.json'); assert {r['source_group_id']:r for r in inv['hits']}==expected
keys={(r['edition'],r['locus']) for r in expected.values()}; assert len(keys)==469
assert {(l['edition'],l['locus']) for l in inv['target_lines']}==keys
for l in inv['target_lines']:
    key=l['edition'],l['locus']; assert l['groups']==rawlines[key] and l['source_path']==paths[key]
paragraphs=[]
for ed,ps in read(ROOT/m['paragraph_source']).items():
    for p in ps:
        if any((ed,l['locus']) in keys for l in p['lines']): paragraphs.append(dict(edition=ed,**p))
assert inv['complete_paragraphs']==paragraphs and len(paragraphs)==258
assert sum(p['groups'] for p in paragraphs)==15982
for p in paragraphs:
    for line in p['lines']:
        rr=rawlines[p['edition'],line['locus']]
        assert [r['source_group_id'] for r in rr]==line['source_ids']
        assert [r['ivtff_group_raw'] for r in rr]==line['words']
lex=read(ART/'LEXICONS.json'); assert set(lex)=={'R_C','R_W','T_C','T_W'}
base=read(ROOT/m['base_model'])['models']['M']['lexicon']; prior={k:dict(base) for k in ['R','T']}
for p in m['extensions']:
    for k in prior: prior[k].update(read(ROOT/p)['models'][k]['lexicon'])
for cid,words in lex.items():
    old,added=cid.split('_'); assert words==dict(prior[old],**m['content_models'][added]['lexicon']) and len(words)==24
rows=list(csv.DictReader((ART/'TARGET_OCCURRENCES.tsv').open(),delimiter='\t'))
assert len(rows)==len({(r['candidate'],r['source_group_id']) for r in rows})==2000
for cid in lex: assert {r['source_group_id'] for r in rows if r['candidate']==cid}==set(expected)
for r in rows:
    s=expected[r['source_group_id']]; key=s['edition'],s['locus']; rr=rawlines[key]; i=rr.index(s)
    assert r['raw']==s['ivtff_group_raw'] and r['source_path']==paths[key]
    assert [r['gloss'],r['role']]==lex[r['candidate']][r['raw']]
    assert r['left_raw']==(rr[i-1]['ivtff_group_raw'] if i else '')
    assert r['right_raw']==(rr[i+1]['ivtff_group_raw'] if i+1<len(rr) else '')
    assert r['left_separator']==s['left_separator'] and r['right_separator']==s['right_separator']
    assert int(r['full_line_unread'])==sum(x['ivtff_group_raw'] not in lex[r['candidate']] for x in rr)
    assert int(r['full_line_unread'])>=2
small=read(ROOT/m['source'])['groups']; smap={r['source_group_id']:r for r in small}
oldrows=list(csv.DictReader((ROOT/m['prior_alignment']).open(),delimiter='\t'))
assert len(oldrows)==2816
for r in oldrows:
    s=smap[r['source_group_id']]; assert all(r[k]==str(v) for k,v in s.items())
    assert [r['gloss'],r['role']]==prior[r['model']].get(s['ivtff_group_raw'],['⟦'+s['ivtff_group_raw']+'⟧','UNREAD'])
work=list(csv.DictReader((ART/'WORKING_ALIGNMENT.tsv').open(),delimiter='\t'))
assert len(work)==len({(r['candidate'],r['source_group_id']) for r in work})==5632
for r in work:
    s=smap[r['source_group_id']]; assert all(r[k]==str(v) for k,v in s.items())
    assert [r['gloss'],r['role']]==lex[r['candidate']].get(s['ivtff_group_raw'],['⟦'+s['ivtff_group_raw']+'⟧','UNREAD'])
local=list(csv.DictReader((ART/'LOCAL_PREDICTIONS.tsv').open(),delimiter='\t')); assert len(local)==12
for row in local:
    c=row['candidate'].split('_')[1]
    assert row['known_groups']=='5' and row['prediction_group']==c
    assert row['optically_clear']==('True' if c=='C' else '')
    assert row['water_identity']==('True' if c=='W' else '')
    assert row['unmixed']=='True'
    assert row['factual_inference']==row['empirically_selected']=='False' and row['independent_meaning_tests']=='0'
# Independent full raw line rendering test; includes all paragraph lines, even without targets.
for ed in ['ZL3b','IT2a','RF1b']:
    doc=(ART/f'CONTEXTS_{ed}.md').read_text(); required={key for key in keys if key[0]==ed}
    required|={(ed,l['locus']) for p in paragraphs if p['edition']==ed for l in p['lines']}
    for key in required:
        rr=rawlines[key]; text=rr[0]['ivtff_group_raw']
        for r in rr[1:]: text+={'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // '}[r['left_separator']]+r['ivtff_group_raw']
        assert '### '+key[1]+'\n' in doc and '`'+text+'`' in doc
islands=read(ART/'TARGET_ISLANDS.json'); assessment=read(EXP/'src/ASSESSMENT.json')
assert len(islands)==89
assert {' '.join(r['words']) for r in islands}==set(assessment['notes'])
assert assessment['selection']=='NONE'
for r in islands:
    assert [source[sid]['ivtff_group_raw'] for sid in r['ids']]==r['words']
    for cid,words in lex.items(): assert r['readings'][cid]==[words[w][0] for w in r['words']]
for name,value in run.build().items(): assert (ART/name).read_text()==value,name
res=read(ART/'RESULT.json'); assert res['confirmed_words']==res['independent_meaning_tests']==res['new_admissions']==0
assert not res['semantics_validated'] and res['selected_translation'] is None
out={'status':'PASS','checks':['all locked inputs intact','independent96184-group admitted census','all500 exact targets and2000 candidate cases','all469 whole target lines and258 available paragraphs/15982groups','all old2816 alignments and new5632 working alignments','24word lexicons fixed; local prediction groups C/W distinct','raw boundaries retained and deterministic replay'],'semantics_validated':False}
(ART/'VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
