#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sp=BASE/'artifacts/SOURCE_LINES.json';parent=BASE.parent/'gdt882_additive_line_lattice/artifacts/SELECTED_LINES.json'
    assert sha(sp)==sha(parent)=='bd8b58523e4e49754f4e49e3901f00ecef748679d90ac46184e453294c8753c2'
    rows=json.loads(sp.read_text());assert len(rows)==413 and len({r['locus'] for r in rows})==413 and any(r['locus']=='f19r.8' for r in rows)
    assert sorted(set(''.join(r['literal'] for r in rows)))==list('acdefghiklmnopqrstxy')
    folios={int(re.match(r'f(\d+)',r['page']).group(1)) for r in rows};assert len(folios)==43 and all(f%2 and f!=84 for f in folios)
    phase='REGISTERED_SOURCE_ONLY';p=BASE/'artifacts/FOLD_RESULT.json'
    if p.exists():
        result=json.loads(p.read_text());assert result['source_sha256']==sha(sp) and result['code_sha256']==sha(BASE/'src/fold.py') and result['runner_sha256']==sha(BASE/'src/run.py')
        independent=json.loads((BASE/'artifacts/INDEPENDENT_SUBGROUP.json').read_text())
        assert independent['source_sha256']==sha(sp) and independent['code_sha256']==sha(BASE/'src/independent_subgroup.py')
        a=result['core'];b=independent['core'];assert a['vertices']==b['vertex_count'] and a['edges']==b['positive_edges']
        assert result['full_group']==b['equals_full_free_group']
        assert result['core_rank']==b['rank'] and result['core_complete_cover']==(b['index']!='INFINITE') and result['subgroup_index']==b['index']
        cv=json.loads((BASE/'artifacts/CERTIFICATE_VALIDATION.json').read_text());assert cv['status']=='PASS' and cv['result_sha256']==sha(p) and cv['validator_sha256']==sha(BASE/'src/validate_certificate.py')
        receipt=json.loads((BASE/'artifacts/INDEPENDENT_RUN_RECEIPT.json').read_text());assert receipt['exit_code']==0 and receipt['stderr_empty']
        phase='COMPLETE_UNIVERSAL_RESULT_INDEPENDENT_CORE_AND_CERTIFICATE'
    out={'status':'PASS','phase':phase,'source_sha256':sha(sp),'exact_parent_copy':True,'lines':413,'odd_physical_leaves':43,'alphabet_size':20,'claim_ceiling':'Source and mathematical proof only; no historical atomicity, writing rule, meaning or held result.'}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
