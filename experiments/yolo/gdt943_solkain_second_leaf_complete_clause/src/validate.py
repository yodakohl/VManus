#!/usr/bin/env python3
"""Independent artifact census and source/contract audit, not a meaning test."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2]
def read(p):return json.loads(p.read_text())
def table(n):return list(csv.DictReader((EXP/'artifacts'/n).open(),delimiter='\t'))
def main():
    lock=read(EXP/'PREREG_LOCK.json')
    for path,h in lock['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    m=read(EXP/'src/MODEL.json');allow=set(read(ROOT/m['allow_source'])['allowed_selectors'])
    assert len(allow)==179 and not any(p.startswith('f84') or p=='f116v' for p in allow)
    lines={};allgroups={}
    for path in m['sources']:
        d=read(ROOT/path)
        for line in d['lines']:
            meta=line['metadata'];assert meta['page'] in allow
            rr=[meta|dict(zip(d['group_columns'],g)) for g in line['groups']]
            lines[meta['edition'],meta['locus']]=rr
            for r in rr:assert r['source_group_id'] not in allgroups;allgroups[r['source_group_id']]=r
    assert len(allgroups)==96184
    targets=set(m['shared_new'])|{'shl'}
    expected={i:r for i,r in allgroups.items() if r['ivtff_group_raw'] in targets}
    occ=table('NEW_OCCURRENCES.tsv');assert len(occ)==len(expected)==1705
    assert {r['source_group_id'] for r in occ}==set(expected)
    lx=read(EXP/'artifacts/LEXICONS.json');base=read(ROOT/m['base_lexicons']);assert len(lx)==8
    for cid,lex in lx.items():
        b=base[cid.rsplit('_',1)[0]]
        assert len(b)==33 and len(lex)==41
        assert all(lex[w]==g for w,g in b.items())
        assert {w:g for w,g in lex.items() if w not in b}==m['shared_new']|{'shl':m['shl_variants'][cid.rsplit('_',1)[1]]}
    for r in occ:
        original=expected[r['source_group_id']]
        for k in ['edition','page','locus','source_group_index','ivtff_group_raw','left_separator','right_separator']:assert r[k]==original[k]
        for variant in ['REL','TEMP']:
            assert r[variant+'_gloss']==lx['R_C_'+variant][r['ivtff_group_raw']][0]
            assert r[variant+'_role']==lx['R_C_'+variant][r['ivtff_group_raw']][1]
    targetkeys={(r['edition'],r['locus']) for r in expected.values()}
    def unpack(name):
        result={}
        for p in read(EXP/'artifacts'/name):
            k=p['edition'],p['locus'];assert k not in result
            rr=[dict(zip(p['columns'],g)) for g in p['groups']]
            assert rr==lines[k];result[k]=rr
        return result
    targetlines=unpack('SOURCE_TARGET_LINES.json');assert set(targetlines)==targetkeys
    pp=read(ROOT/m['paragraph_source']);expectedpp=[];contextkeys=set()
    for ed in ['ZL3b','IT2a']:
        for target in m['context_targets']:
            p=[p for p in pp[ed] if any(l['locus']==target for l in p['lines'])];assert len(p)==1
            expectedpp.append(dict(edition=ed,**p[0]))
            for l in p[0]['lines']:
                assert l['source_ids']==[r['source_group_id'] for r in lines[ed,l['locus']]]
                assert l['words']==[r['ivtff_group_raw'] for r in lines[ed,l['locus']]]
                contextkeys|={(ed,l['locus']),('RF1b',l['locus'])}
    assert expectedpp==read(EXP/'artifacts/CONTEXT_PARAGRAPHS.json')
    actual=unpack('CONTEXT_SOURCE_LINES.json');assert set(actual)==contextkeys
    covers=table('CONTEXT_COVERAGE.tsv');assert len(covers)==6
    by={(c['edition'],c['target']):c for c in covers}
    assert by['ZL3b','f80r.14']['end']=='f80r.27'
    assert by['IT2a','f80r.14']['end']=='f80r.17'
    assert [r['ivtff_group_raw'] for r in actual['ZL3b','f80v.32']][:2]==['s','olkain']
    local=table('LOCAL_ALIGNMENT.tsv');assert len(local)==288
    seen=set()
    for r in local:
        key=r['candidate'],r['source_id'];assert key not in seen;seen.add(key)
        s=allgroups[r['source_id']];assert s['locus']==m['seed_locus']
        assert r['raw']==s['ivtff_group_raw'] and (r['gloss'],r['role'])==tuple(lx[r['candidate']][r['raw']])
        assert r['left_separator']==s['left_separator'] and r['right_separator']==s['right_separator']
    cases=table('SHL_CASES.tsv');shls={i:r for i,r in allgroups.items() if r['ivtff_group_raw']=='shl'}
    assert len(shls)==9 and {r['locus'] for r in shls.values()}=={'f76v.20','f80r.14','f107r.35'}
    assert len(cases)==72 and {(r['candidate'],r['source_id']) for r in cases}=={(c,i) for c in lx for i in shls}
    for r in cases:
        src=shls[r['source_id']];rr=lines[src['edition'],src['locus']];i=rr.index(src)
        body=rr[i+1:i+4];prev=rr[i-1] if i else None;lex=lx[r['candidate']]
        assert r['body_ids']=='|'.join(x['source_group_id'] for x in body)
        roles=[lex.get(x['ivtff_group_raw'],['','UNREAD'])[1] for x in body]
        definite=len(body)==3 and all(x['left_separator']==rr[i+j]['right_separator']=='DEFINITE_SPACE' for j,x in enumerate(body))
        bodybound=roles==['EVENT_NOUN','RATE','COPULA'] and definite
        assert r['body_bound']==str(bodybound)
        assert bodybound==(src['locus']=='f80r.14')
        if bodybound:
            if r['candidate'].endswith('_REL'):
                assert r['status']=='LOCAL_OWNER_BOUND' and r['asserted_owner_id']==prev['source_group_id']
                assert prev['ivtff_group_raw']=='solkain'
            else:assert r['status']=='LOCAL_TIME_BOUND_OWNER_OPEN' and r['asserted_owner_id']==''
        else:assert r['status']=='NO_FIXED_CONSTRUCTION'
    decisions=table('CANDIDATE_DECISIONS.tsv');assert len(decisions)==8
    for r in decisions:
        assert r['shl_positions']=='9' and r['bound_subclauses']=='3' and r['other_locus_bound']=='0'
        assert r['independent_meaning_tests']==r['unexposed_confirmation_leaves']=='0'
    result=read(EXP/'artifacts/RESULT.json')
    for cid,eds in result['context_coverage'].items():
        for ed,c in eds.items():
            rr=[r for (e,l),rows in actual.items() if e==ed for r in rows]
            assert c=={'groups':len(rr),'hypothesis_groups':sum(r['ivtff_group_raw'] in lx[cid] for r in rr)}
    assert result['new_occurrences']==1705 and result['confirmed_words']==0 and result['meaning_selected'] is None
    assert result['new_admissions']==0 and result['significance_claim'] is False
    for path in (EXP/'artifacts').glob('*'):
        if path.is_file():assert path.stat().st_size<=5000000,path
    out={'status':'PASS','source_hashes':len(lock['files']),'source_groups':len(allgroups),'exact_new_occurrences':len(occ),'source_complete_target_lines':len(targetlines),'context_groups':sum(map(len,actual.values())),'local_alignment_rows':len(local),'shl_cases':len(cases),'old_words_unchanged':33,'new_words_per_model':8,'meaning_validated':False,'limitations':'Mechanical source, coverage, and local construction audit; no independent interpretation, visual test, or search-wide significance.'}
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
