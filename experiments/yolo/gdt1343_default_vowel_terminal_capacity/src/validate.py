from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):return json.loads((B/p).read_text())
def main():
    for p,h in read('src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    rows=json.loads(gzip.decompress((R/'experiments/yolo/gdt1342_qoky_written_predecessor/artifacts/SOURCE.json.gz').read_bytes()))
    allowed={x['page'] for x in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};assert len(allowed)==179
    assert all(x['page'] in allowed and not x['page'].startswith('f84') and x['page'] not in {'f1r','f116v'} for x in rows)
    pattern=re.compile('ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
    signs=['a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh']
    results=read('artifacts/RESULT.json')['readers'];class_rows=json.loads(gzip.decompress((B/'artifacts/CLASSIFICATION.json.gz').read_bytes()))
    assert len(rows)==len(class_rows)==94855
    actual={x[0]:x[1:] for x in class_rows};assert len(actual)==len(rows)
    witnesses=read('artifacts/WITNESSES.json');expected_witnesses=[];checks=0
    for ed in ['ZL3b','IT2a','RF1b']:
        selected=[x for x in rows if x['edition']==ed];byunit=Counter({s:0 for s in signs});reasons=Counter()
        for x in selected:
            tokens=pattern.findall(x['raw']);valid=bool(tokens) and ''.join(tokens)==x['raw']
            seams=all(x[side] in ['DEFINITE_SPACE','LINE_START','LINE_END'] for side in ['left','right'])
            if valid and seams:reason='STRICT'
            elif not valid and not seams:reason='PARSE_AND_SEAM_UNCERTAIN'
            elif not valid:reason='PARSE_UNCERTAIN'
            else:reason='SEAM_UNCERTAIN'
            double=reason=='STRICT' and len(tokens)>1 and tokens[-2:]==[tokens[-1]]*2
            assert actual[x['id']]==[reason,tokens[-1] if reason=='STRICT' else None,double]
            reasons[reason]+=1
            if double:byunit[tokens[-1]]+=1;expected_witnesses.append({'source':x,'units':tokens})
            checks+=1
        s=results[ed];N=reasons['STRICT'];U=len(selected)-N;D=sum(byunit.values())
        # Complement formulation: five vowel bodies can exclude the five smallest counts.
        M=D-sum(sorted(byunit.values())[:5])
        assert s['total_P_groups']==len(selected) and s['strict_N']==N and s['excluded_U']==U
        assert s['exclusion_account']==dict(reasons) and s['final_double_counts']==dict(byunit)
        assert (s['final_doubles_D'],s['seventeen_body_max_M'])==(D,M)
        assert s['strict_upper_fraction']==M/N and s['all_raw_upper_fraction_if_one_word_per_raw_group']==(M+U)/len(selected)
    key=lambda x:x['source']['id']
    assert sorted(witnesses,key=key)==sorted(expected_witnesses,key=key)
    # Distinct semantic endings can share cc; only the implication is licensed.
    assert read('artifacts/PROOF_CHECK.json')['converse_counterexample']=={'source':['C0','V0','C0','V0'],'output':['C0','C0']}
    out={'status':'PASS','source_groups':len(rows),'checked_classifications':checks,'terminal_witnesses':len(witnesses),'scope':'Independent regex source census and complement-bound arithmetic; no independent source language, glyph identity or meaning.'}
    (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
