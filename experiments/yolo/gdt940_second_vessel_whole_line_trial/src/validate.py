"""Independent source census and contract evaluation, then replay. Not semantic validation."""
from pathlib import Path
from collections import Counter
import csv,json,hashlib
import run
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];ART=EXP/'artifacts'
def j(p):return json.loads(p.read_text())
def rows(name):return list(csv.DictReader((ART/name).open(),delimiter='\t'))
m=j(EXP/'src/MODEL.json');lock=j(EXP/'PREREG_LOCK.json')
for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
spec=j(ROOT/m['inventory_spec']);allow=set(j(ROOT/spec['allow_source'])['allowed_selectors'])
assert len(allow)==179 and not any(p.startswith('f84') or p=='f116v' for p in allow)
source={};lines={}
for p in spec['sources']:
    d=j(ROOT/p);assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==spec['hashes'][p]
    for line in d['lines']:
        meta=line['metadata'];assert meta['page'] in allow and not meta['page'].startswith('f84')
        rr=[dict(**meta,**dict(zip(d['group_columns'],g))) for g in line['groups']]
        key=meta['edition'],meta['locus'];assert key not in lines;lines[key]=rr
        for r in rr:assert r['source_group_id'] not in source;source[r['source_group_id']]=r
assert len(source)==96184
lex=j(ART/'LEXICONS.json');old=j(ROOT/m['prior_lexicons'])
assert set(lex)==set(old)=={'R_C','R_W','T_C','T_W'}
for cid in lex:assert len(old[cid])==33 and len(lex[cid])==43 and lex[cid]==dict(old[cid],**m['new_lexicon'])
expected={sid:r for sid,r in source.items() if r['ivtff_group_raw'] in m['new_lexicon']}
occ=rows('NEW_OCCURRENCES.tsv');assert len(occ)==len(expected)==len({r['source_group_id'] for r in occ})==3421
assert {r['source_group_id'] for r in occ}==set(expected)
for r in occ:
    src=source[r['source_group_id']]
    assert r['raw']==src['ivtff_group_raw'] and [r['gloss'],r['role']]==m['new_lexicon'][r['raw']]
    for k in ['edition','page','locus','left_separator','right_separator']:assert r[k]==str(src[k])
    assert r['applies_to']==','.join(lex)
# Check exact frame and paragraph bounds against an independently produced predecessor artifact.
pp=j(ROOT/m['paragraph_source'])
for ed in ['ZL3b','IT2a']:
    para=next(p for p in pp[ed] if any(l['locus']==m['locus'] for l in p['lines']))
    assert [l['locus'] for l in para['lines']]==[f'f111v.{i}' for i in range(1,26)]
    for line in para['lines']:
        rr=lines[ed,line['locus']]
        assert line['words']==[r['ivtff_group_raw'] for r in rr] and line['source_ids']==[r['source_group_id'] for r in rr]
assert pp['RF1b']==[]
frame=rows('FRAME_ALIGNMENT.tsv');fid={sid for sid,r in source.items() if r['page']=='f111v' and 1<=int(r['locus'].split('.')[1])<=25}
assert len(fid)==880 and len(frame)==3520
for cid in lex:assert {r['source_group_id'] for r in frame if r['candidate']==cid}==fid
for r in frame:
    src=source[r['source_group_id']];assert all(r[k]==str(v) for k,v in src.items())
    assert [r['gloss'],r['role']]==lex[r['candidate']].get(src['ivtff_group_raw'],['⟦'+src['ivtff_group_raw']+'⟧','UNREAD'])
loc=rows('LOCAL_ALIGNMENT.tsv');pred=rows('LOCAL_PREDICTIONS.tsv');assert len(loc)==168 and len(pred)==12
for ed in run.EDS:
    rr=lines[ed,m['locus']];assert [r['ivtff_group_raw'] for r in rr]==m['expected_words'][ed]
    for cid in lex:
        ll=[r for r in loc if r['edition']==ed and r['candidate']==cid]
        assert [r['source_group_id'] for r in ll]==[r['source_group_id'] for r in rr]
        assert [r['proposed_slot'] for r in ll]==m['local_roles']
        p=next(r for r in pred if r['edition']==ed and r['candidate']==cid)
        assert int(p['assigned'])==(14 if ed=='IT2a' else 11)
        assert bool(p['complete_local_sentence'])==(ed=='IT2a')
        for k in ['same_material_as_line17','aperture_identity','other_vessel_reference']:assert p[k]=='UNBOUND'
        for r in ll:assert [r['gloss'],r['lexical_role']]==lex[cid].get(r['raw'],['⟦'+r['raw']+'⟧','UNREAD'])
assert lines['ZL3b',m['locus']][5]['left_separator']=='UNCERTAIN_SMALL_SPACE'
# Evaluate each contract independently, without run.obligation.
obs=rows('TRANSFER_OBLIGATIONS.tsv');triggers={sid:r for sid,r in source.items() if r['ivtff_group_raw'] in m['transfer_rules']}
assert len(triggers)==741 and len(obs)==2964
assert {(r['candidate'],r['trigger_id']) for r in obs}=={(cid,sid) for cid in lex for sid in triggers}
expected_out={}
for cid,words in lex.items():
    for (ed,locus),rr in lines.items():
        for i,r in enumerate(rr):
            if r['source_group_id'] not in triggers:continue
            rule=m['transfer_rules'][r['ivtff_group_raw']];used=False;ids=[r['source_group_id']];head=None;status='OPEN';reason='LINE_END'
            for k in range(i+1,len(rr)):
                n=rr[k]
                if rr[k-1]['right_separator']!='DEFINITE_SPACE' or n['left_separator']!='DEFINITE_SPACE':reason='UNCERTAIN_BOUNDARY';break
                ids.append(n['source_group_id'])
                if rule['optional'] and not used and n['ivtff_group_raw']==rule['optional']:used=True;continue
                head=n
                if n['ivtff_group_raw'] not in words:reason='UNREAD_HEAD'
                elif words[n['ivtff_group_raw']][1] in m['nominal_roles']:status='COMPATIBLE';reason='KNOWN_NOMINAL'
                else:status='CONFLICT';reason='KNOWN_NONNOMINAL'
                break
            expected_out[cid,r['source_group_id']]=(status,reason,'|'.join(ids),head['source_group_id'] if head else '')
for r in obs:assert (r['status'],r['reason'],r['span_ids'],r['head_id'])==expected_out[r['candidate'],r['trigger_id']]
for cid in lex:
    cc=Counter(r['status'] for r in obs if r['candidate']==cid)
    assert cc==Counter({'COMPATIBLE':28,'CONFLICT':84,'OPEN':629} if cid.endswith('_C') else {'COMPATIBLE':34,'CONFLICT':78,'OPEN':629})
    assert all(next(r for r in obs if r['candidate']==cid and r['trigger_id']==ed+'|f50r.9|G004')['status']=='CONFLICT' for ed in run.EDS)
# Grouping difference is retained: olr is not assigned from its separated counterpart.
for ed in run.EDS:
    raw=[r['ivtff_group_raw'] for r in lines[ed,'f115v.38']]
    if ed=='IT2a':assert 'olr' in raw and 'olr' not in lex['R_C']
    else:assert any(raw[i:i+3]==['o','l','r'] for i in range(len(raw)-2))
# Full-line outputs include every target line and preserve every separator.
keys={(r['edition'],r['locus']) for r in expected.values()};assert len(keys)==2774
sep={'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // ','DRAWING_INTERRUPTION_UNALIGNED':' ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ '}
for ed,locus in keys:
    rr=lines[ed,locus];raw=rr[0]['ivtff_group_raw']+''.join(sep[r['left_separator']]+r['ivtff_group_raw'] for r in rr[1:])
    assert '`'+raw+'`' in (ART/f'TARGET_LINES_{ed}.md').read_text()
for name,content in run.build().items():assert (ART/name).read_text()==content,name
res=j(ART/'RESULT.json');assert res['confirmed_words']==res['independent_meaning_tests']==res['new_admissions']==0 and not res['semantics_validated']
out={'status':'PASS','checks':['19 preregistration/input hashes intact','independent complete3421 occurrence census over96184 admitted groups','all2774 target lines preserve raw separators','all33 prior values fixed in four43-word lexicons','168 local positions and3520 frame alignments; ZL/IT paragraphs independently matched','all741 triggers x4 candidates independently evaluated','C:84/28/629; W:78/34/629 conflict/compatible/open','f50r9 contradiction in all readers; f115v38 IT olr remains unassigned','deterministic output replay'],'semantics_validated':False}
(ART/'VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
