"""Independent census, inherited-value and full-output checks; no meaning validation."""
from pathlib import Path
from collections import Counter
import csv,hashlib,json
import run
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];ART=EXP/'artifacts'
def read(p):return json.loads(p.read_text())
m=read(EXP/'src/MODEL.json');lock=read(EXP/'PREREG_LOCK.json')
for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
spec=read(ROOT/m['inventory_spec']);allow=set(read(ROOT/spec['allow_source'])['allowed_selectors']);assert len(allow)==179 and not any(p.startswith('f84') or p=='f116v' for p in allow)
source={};lines={};paths={}
for p in spec['sources']:
    d=read(ROOT/p);assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==spec['hashes'][p]
    for line in d['lines']:
        meta=line['metadata'];assert meta['page'] in allow and not meta['page'].startswith('f84')
        key=meta['edition'],meta['locus'];assert key not in lines
        rr=[dict(**meta,**dict(zip(d['group_columns'],g))) for g in line['groups']];lines[key]=rr;paths[key]=p
        for r in rr:assert r['source_group_id'] not in source;source[r['source_group_id']]=r
assert len(source)==96184
expected={sid:r for sid,r in source.items() if r['ivtff_group_raw'] in m['new_lexicon']};assert len(expected)==2684
rows=list(csv.DictReader((ART/'NEW_OCCURRENCES.tsv').open(),delimiter='\t'))
assert len(rows)==len({r['source_group_id'] for r in rows})==2684
assert {r['source_group_id'] for r in rows}==set(expected)
for r in rows:
    s=expected[r['source_group_id']];key=s['edition'],s['locus'];rr=lines[key];i=rr.index(s)
    assert r['raw']==s['ivtff_group_raw'] and [r['gloss'],r['role']]==m['new_lexicon'][r['raw']]
    for k in ['edition','page','locus','left_separator','right_separator']:assert r[k]==s[k]
    assert r['source_path']==paths[key] and r['applies_to']=='R_C,R_W,T_C,T_W'
    assert r['left_raw']==(rr[i-1]['ivtff_group_raw'] if i else '') and r['right_raw']==(rr[i+1]['ivtff_group_raw'] if i+1<len(rr) else '')
lex=read(ART/'LEXICONS.json');old=read(ROOT/m['prior_lexicons'])
for cid in ['R_C','R_W','T_C','T_W']:assert len(lex[cid])==33 and lex[cid]==dict(old[cid],**m['new_lexicon'])
prior_targets=list(csv.DictReader((ROOT/m['prior_target_table']).open(),delimiter='\t'));assert len(prior_targets)==2000
for r in prior_targets:assert lex[r['candidate']][r['raw']]==[r['gloss'],r['role']]
prior_work=list(csv.DictReader((ROOT/m['prior_working_alignment']).open(),delimiter='\t'));assert len(prior_work)==5632
for r in prior_work:
    if r['role']!='UNREAD':assert lex[r['candidate']][r['ivtff_group_raw']]==[r['gloss'],r['role']]
# ZL/IT whole paragraph coverage is separately grounded in the old paragraph cache.
pp=read(ROOT/m['paragraph_source'])
for ed in ['ZL3b','IT2a']:
    para=next(p for p in pp[ed] if any(l['locus']=='f111v.17' for l in p['lines']))
    assert [l['locus'] for l in para['lines']]==[f'f111v.{n}' for n in range(1,26)]
    for line in para['lines']:
        rr=lines[ed,line['locus']];assert [r['source_group_id'] for r in rr]==line['source_ids'];assert [r['ivtff_group_raw'] for r in rr]==line['words']
assert pp['RF1b']==[]
frame=list(csv.DictReader((ART/'FRAME_ALIGNMENT.tsv').open(),delimiter='\t'))
assert len(frame)==len({(r['candidate'],r['source_group_id']) for r in frame})==3520
frameids={sid for sid,r in source.items() if r['page']=='f111v' and 1<=int(r['locus'].split('.')[1])<=25};assert len(frameids)==880
for cid in lex:assert {r['source_group_id'] for r in frame if r['candidate']==cid}==frameids
for r in frame:
    s=source[r['source_group_id']];assert all(r[k]==str(v) for k,v in s.items())
    assert [r['gloss'],r['role']]==lex[r['candidate']].get(s['ivtff_group_raw'],['⟦'+s['ivtff_group_raw']+'⟧','UNREAD'])
local=list(csv.DictReader((ART/'LOCAL_ALIGNMENT.tsv').open(),delimiter='\t'));pred=list(csv.DictReader((ART/'LOCAL_PREDICTIONS.tsv').open(),delimiter='\t'))
assert len(local)==144 and len(pred)==12
for cid in lex:
    for ed in ['ZL3b','IT2a','RF1b']:
        rr=lines[ed,'f111v.17'];assert [r['ivtff_group_raw'] for r in rr]==m['expected_words']
        lr=[r for r in local if r['candidate']==cid and r['edition']==ed]
        assert [r['source_group_id'] for r in lr]==[r['source_group_id'] for r in rr]
        assert [r['local_role'] for r in lr]==m['local_roles']
        p=next(r for r in pred if r['candidate']==cid and r['edition']==ed)
        assert p['subject_id']==p['motion_subject_id']==rr[0]['source_group_id']
        assert p['container_id']==rr[2]['source_group_id'] and p['subject_id']!=p['container_id']
        assert p['motion_ids']=='|'.join(rr[i]['source_group_id'] for i in [5,9])
        assert p['aperture_id']==rr[11]['source_group_id']
        assert p['optical_clarity']==('True' if cid.endswith('_C') else '') and p['water_identity']==('True' if cid.endswith('_W') else '')
        assert p['asserts_pipe_water_identity']==p['chronology_inferred']==p['factual_inference']==p['empirically_selected']=='False'
variants=read(ART/'SOLKAIN_VARIANTS.json');assert len(variants)==9 and sum(x['exact_solkain'] for x in variants)==8
for v in variants:assert v['groups']==lines[v['edition'],v['locus']]
assert not next(v for v in variants if v['edition']=='ZL3b' and v['locus']=='f80v.32')['exact_solkain']
# No source separator can silently become a definite space, including unaligned drawing breaks.
sep={'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // ','DRAWING_INTERRUPTION_UNALIGNED':' ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ '}
keys={(r['edition'],r['locus']) for r in expected.values()};assert len(keys)==2251
for ed in ['ZL3b','IT2a','RF1b']:
    doc=(ART/f'TARGET_LINES_{ed}.md').read_text();fdoc=(ART/f'FRAME_{ed}.md').read_text()
    for e,loc in keys|{(ed,f'f111v.{n}') for n in range(1,26)}:
        if e!=ed:continue
        rr=lines[e,loc];raw=rr[0]['ivtff_group_raw']
        for r in rr[1:]:raw+=sep[r['left_separator']]+r['ivtff_group_raw']
        if (e,loc) in keys:assert '`'+raw+'`' in doc
        if loc.startswith('f111v.') and 1<=int(loc.split('.')[1])<=25:assert '`'+raw+'`' in fdoc
covered=read(ART/'LEXICALLY_COVERED_LINES.json')
assert {(x['edition'],x['locus']) for x in covered}=={(e,l) for e,l in keys if all(r['ivtff_group_raw'] in lex['R_C'] for r in lines[e,l])}
assert len(covered)==5 and sum(x['groups']==1 for x in covered)==2
for name,value in run.build().items():assert (ART/name).read_text()==value,name
res=read(ART/'RESULT.json');assert res['confirmed_words']==res['independent_meaning_tests']==res['new_admissions']==0 and not res['semantics_validated'] and res['selected_translation'] is None
out={'status':'PASS','checks':['all input/model hashes intact','independent2684 target census from96184 admitted groups','all2251 full target lines and raw separator kinds','all24 old values retained in old2000cases/5632alignments','whole ZL/IT paragraph and separately labeled RF window','all144 local and3520 frame assignments','subject distinct from container under fixed local hypothesis','all9 solkain variants including missing ZL exact form','five lexically covered lines include two single-word cases','deterministic replay'],'semantics_validated':False}
(ART/'VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
