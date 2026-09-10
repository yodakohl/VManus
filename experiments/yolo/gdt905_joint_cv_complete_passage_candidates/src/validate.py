#!/usr/bin/env python3
"""Source conservation and claim rollup; independent scientific checks are bound."""
import argparse,collections,gzip,hashlib,json,subprocess,sys
from pathlib import Path
import run
E=run.E;ROOT=run.ROOT
def main():
    p=argparse.ArgumentParser();p.add_argument('--cache-dir',type=Path,required=True);p.add_argument('--check',action='store_true');a=p.parse_args()
    run.check_lock();run.reference(a.cache_dir)
    source=run.module(ROOT/'experiments/yolo/gdt904_vinidarius_complete_relational_register/src/run.py','intake_validation')
    target=run.read('TARGET.json');assert source.intake()==target
    selected={(ed,r['paragraph_id']):r for ed,r in run.selected(target)}
    scope=run.read('SCOPE.json')
    for ed,rs in target['panels'].items():
        assert scope[ed]['total']==len(rs)
        assert scope[ed]['selected']==sum(12<=len(r['words'])<=24 for r in rs)
        expected=[dict(paragraph_id=r['paragraph_id'],word_count=len(r['words']),reason='OUTSIDE_REGISTERED_12_24_GROUP_SCOPE') for r in rs if not 12<=len(r['words'])<=24]
        assert scope[ed]['excluded']==expected
    scans=run.read('SCANS.json');assert len(scans)==len(selected)
    assert {(x['edition'],x['paragraph_id']) for x in scans}==set(selected)
    raw=E/'artifacts/CANDIDATES.json'
    data=raw.read_bytes() if raw.exists() else gzip.decompress(raw.with_suffix('.json.gz').read_bytes())
    candidates=json.loads(data);assert len(candidates)==len(selected)
    assert {(x['edition'],x['paragraph_id']) for x in candidates}==set(selected)
    for r in candidates:
        assert r['status'] in {'COMPLETE_CANDIDATES','UNSAT_SHARED_KEY_OR_GRAMMAR','UNSAT_LEXICAL_PATTERN','OUTSIDE_CHANNEL_ALPHABET','UNKNOWN_BUDGET','UNKNOWN_WITNESS_LIMIT','UNKNOWN_TOTAL_BUDGET','UNKNOWN_SCANNER_BUDGET'}
        assert len({(c['mask'],c['inherent']) for c in r['cases']})==len(r['cases'])
        if r['status'].startswith('UNSAT'):assert not r['witnesses']
        if r['status']=='COMPLETE_CANDIDATES':assert r['witnesses'] and all(c['status']=='COMPLETE' for c in r['cases'])
        if r['status']=='UNKNOWN_WITNESS_LIMIT':assert len(r['witnesses'])==64
    result=run.read('RESULT.json')
    assert result['paragraphs']==len(candidates)
    assert result['statuses']==dict(collections.Counter(x['status'] for x in candidates))
    assert result['candidate_keys']==sum(len(x['witnesses']) for x in candidates)
    assert result['candidate_paragraphs']==sum(bool(x['witnesses']) for x in candidates)
    assert result['confirmed_meanings']==0
    ind=run.read('INDEPENDENT_VALIDATION.json');assert ind['status']=='PASS'
    for k,n in [('target_sha256','TARGET.json'),('scans_sha256','SCANS.json'),('result_sha256','RESULT.json')]:assert ind[k]==run.sha(E/'artifacts'/n)
    assert ind['candidates_sha256']==hashlib.sha256(data).hexdigest()
    assert ind['validator_sha256']==run.sha(E/'src/validate_independent.py')
    assert ind['candidate_count']==result['candidate_keys']
    assert len(ind['mask_checks'])==len(selected)
    explanation=run.read('LEXICAL_KEY_EXPLANATION.json')
    assert ind['lexical_key_explanation_sha256']==run.sha(E/'artifacts/LEXICAL_KEY_EXPLANATION.json')
    assert len(ind['rejected_lexical_key_checks'])==sum(not k['grammar_accepted'] for r in explanation['records'] for k in r['keys'])
    assert all(not c['independent_CFG_accepted'] for c in ind['rejected_lexical_key_checks'])
    if (E/'artifacts/PACKING.json').exists():subprocess.run([sys.executable,str(E/'src/pack_artifacts.py'),'--check'],check=True,capture_output=True)
    out=dict(status='PASS',guarded_source_exact=True,paragraphs=len(selected),complete_mask_sets_independently_verified=len(ind['mask_checks']),candidate_witnesses_independently_verified=result['candidate_keys'],rejected_lexical_keys_independently_verified=len(ind['rejected_lexical_key_checks']),candidate_statuses=result['statuses'],logical_candidate_sha256=hashlib.sha256(data).hexdigest(),independent_receipt_sha256=run.sha(E/'artifacts/INDEPENDENT_VALIDATION.json'),claim_ceiling='Source and complete local-mask validation; explicit witnesses checked if present. Unfinished global-key searches remain unknown. No word meaning or control recovery established.')
    if a.check:assert run.read('VALIDATION.json')==out
    else:run.write('VALIDATION.json',out)
    print(run.enc(out))
if __name__=='__main__':main()
