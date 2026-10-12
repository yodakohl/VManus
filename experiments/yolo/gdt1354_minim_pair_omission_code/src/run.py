from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
PLAN={'IT2a':{'i','n'},'RF1b':{'i'},'ZL3b':{'i'}}
SAMPLES=['daldy','daiin','aiin','in','iiin','iir','qokaiii']
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(p,x):
    raw=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();p.write_bytes(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else raw)
def backward(w,H):
    out=[];j=len(w)
    while j:
        width=2 if w[j-1] in H else 1
        if j<width:return None
        out.append(w[j-width:j]);j-=width
    return out[::-1]
def main():
    for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');prior=read(R/'experiments/yolo/gdt1353_general_ud_forced_units/artifacts/RESULT.json')['panels'];allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};results={}
    for reader,rows in sorted(data.items()):
        H=PLAN[reader];alpha=sorted({u for r in rows for u in r['units']});assert len(alpha)==22;offered={(a,) for a in alpha if a not in H}|{(a,b) for a in alpha for b in H};uses=Counter();hist=Counter();entry_lengths=Counter();active=0;events=[];failures=[]
        for row in rows:
            assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';w=tuple(row['units']);assert ''.join(w)==row['ivtff_group_raw'];initial=0
            for u in w:
                if u not in H:break
                initial+=1
            parts=backward(w,H);assert (parts is not None)==(initial%2==0);hist[initial]+=1
            if parts is None:failures.append(row['id'])
            else:
                assert sum(parts,())==w and all(p in offered for p in parts);uses.update(parts);active+=any(len(p)==2 for p in parts);entry_lengths[len(parts)]+=1
            events.append({'source':row,'initial_H_run':initial,'parse':None if parts is None else [list(p) for p in parts]})
        used=sorted(uses);singles=sorted(c[0] for c in used if len(c)==1);old=prior[reader+'_FULL'];assert old['groups']==len(rows) and old['unresolved']==['i'];prior_compatible=set(old['forced_singletons'])<=set(singles)
        success=not failures and ('i',) not in used and prior_compatible
        examples={}
        for form in SAMPLES:
            found=[e for e in events if e['source']['ivtff_group_raw']==form];examples[form]={'count':len(found),'first_id':found[0]['source']['id'] if found else None,'parse':found[0]['parse'] if found else None,'status':'ATTESTED' if found else 'ABSENT'}
        out={'status':'I_OMISSION_COVER_PASS' if success else 'FIXED_COUNTERCODE_FAIL_I_UNRESOLVED','H':sorted(H),'groups':len(rows),'types':len({tuple(r['units']) for r in rows}),'offered_entries':len(offered),'used_entries':len(used),'used_singletons':singles,'used_pairs':sum(len(c)==2 for c in used),'used_codebook':[{'units':list(c),'uses':uses[c]} for c in used],'initial_H_run_histogram':{str(k):v for k,v in sorted(hist.items())},'failures':failures,'compound_active_groups':active,'total_decoded_entries':sum(uses.values()),'decoded_entry_length_histogram':{str(k):v for k,v in sorted(entry_lengths.items())},'prior_forced_included':prior_compatible,'forced_singletons':old['forced_singletons'],'certified_not_forced':sorted(old['certified_not_forced']+['i']) if success else old['certified_not_forced'],'remaining_unresolved':[] if success else ['i'],'full_singleton_intersection_exact':success,'examples':examples};results[reader]=out;save(B/f'artifacts/EVENTS_{reader}.json.gz',events);print(json.dumps({k:v for k,v in out.items() if k not in ['used_codebook','examples','decoded_entry_length_histogram']}|{'reader':reader}),flush=True)
    save(B/'artifacts/RESULT.json',{'status':'ALL_FIXED_I_OMISSION_CODES_COVER' if all(r['full_singleton_intersection_exact'] for r in results.values()) else 'PARTIAL_FIXED_COUNTERCODE_COVER','readers':results,'scope':'Source-informed formal countercodes only; fixed22working units and wholewords, no actual phonemes, sourcevalues, language, minimalalphabet or general historical writer.'})
if __name__=='__main__':main()
