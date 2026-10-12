from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
PAT=re.compile('ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def read(p):
    v=p.read_bytes();return json.loads(gzip.decompress(v) if p.suffix=='.gz' else v)
def dp(word,codes):
    count=[0]*(len(word)+1);path=[None]*(len(word)+1);count[0]=1;path[0]=()
    for j in range(1,len(word)+1):
        for c in codes:
            n=len(c)
            if n<=j and word[j-n:j]==c and count[j-n]:count[j]=min(2,count[j]+count[j-n]);path[j]=path[j-n]+(c,)
    return count[-1],path[-1]
def ud(codes):
    queue={b[len(a):] for a in codes for b in codes if a!=b and b[:len(a)]==a};seen=set()
    while queue:
        s=queue.pop()
        if not s:return False
        if s in seen:continue
        seen.add(s)
        for c in codes:
            if c[:len(s)]==s:queue.add(c[len(s):])
            if s[:len(c)]==c:queue.add(s[len(c):])
    return True

def main():
    for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');prior=read(R/'experiments/yolo/gdt1353_general_ud_forced_units/artifacts/RESULT.json')['panels'];result=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};parse_checks=0;receipts={}
    for reader,rows in data.items():
        r=result['readers'][reader];H={'i','n'} if reader=='IT2a' else {'i'};assert r['H']==sorted(H);alpha=sorted({u for row in rows for u in row['units']});full={(u,) for u in alpha if u not in H}|set(itertools.product(alpha,sorted(H)));reduced={tuple(c['units']) for c in r['used_codebook']};assert len(alpha)==22 and len(full)==r['offered_entries'] and len(reduced)==r['used_entries'] and reduced<=full and ('i',) not in reduced
        for codes in [full,reduced]:assert ud(codes);assert all(b[-len(a):]!=a for a in codes for b in codes if a!=b)
        events=read(B/f'artifacts/EVENTS_{reader}.json.gz');assert len(events)==len(rows);uses=Counter();initials=Counter();lengths=Counter();active=0;fail=[];parses={};example_data={}
        for row,e in zip(rows,events):
            assert e['source']==row and row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';tokens=PAT.findall(row['ivtff_group_raw']);assert tokens==row['units'] and ''.join(tokens)==row['ivtff_group_raw'];word=tuple(tokens)
            if word not in parses:parses[word]=dp(word,full),dp(word,reduced);parse_checks+=2
            (n,path),(nr,pathr)=parses[word];prefix=next((i for i,u in enumerate(word) if u not in H),len(word));assert prefix==e['initial_H_run'];initials[prefix]+=1;assert n==int(prefix%2==0) and nr==n and path==pathr
            if n:
                assert [list(c) for c in path]==e['parse'] and sum(path,())==word;uses.update(path);lengths[len(path)]+=1;active+=any(len(c)==2 for c in path)
            else:assert e['parse'] is None;fail.append(row['id'])
            example_data.setdefault(row['ivtff_group_raw'],[]).append(e)
        assert r['groups']==len(rows) and r['types']==len(parses) and r['failures']==fail;assert uses==Counter({tuple(c['units']):c['uses'] for c in r['used_codebook']})
        assert r['initial_H_run_histogram']=={str(k):v for k,v in sorted(initials.items())};assert r['decoded_entry_length_histogram']=={str(k):v for k,v in sorted(lengths.items())};assert r['compound_active_groups']==active and r['total_decoded_entries']==sum(uses.values());assert r['used_pairs']==sum(len(c)==2 for c in reduced)
        singles=sorted(c[0] for c in reduced if len(c)==1);assert r['used_singletons']==singles;old=prior[reader+'_FULL'];compatible=set(old['forced_singletons'])<=set(singles);success=not fail and compatible;assert compatible==r['prior_forced_included'];assert r['status']==('I_OMISSION_COVER_PASS' if success else 'FIXED_COUNTERCODE_FAIL_I_UNRESOLVED');assert r['full_singleton_intersection_exact']==success
        assert r['forced_singletons']==old['forced_singletons'];assert r['certified_not_forced']==(sorted(old['certified_not_forced']+['i']) if success else old['certified_not_forced']);assert r['remaining_unresolved']==([] if success else ['i'])
        assert set(r['examples'])==set(['daldy','daiin','aiin','in','iiin','iir','qokaiii'])
        for form,x in r['examples'].items():
            rr=example_data.get(form,[]);assert x=={'count':len(rr),'first_id':rr[0]['source']['id'] if rr else None,'parse':rr[0]['parse'] if rr else None,'status':'ATTESTED' if rr else 'ABSENT'}
        receipts[reader]={'coverage':'PASS' if success else 'FAIL_FIXED_CODE','groups':len(rows),'forced_count_unchanged':len(old['forced_singletons']),'classification_exact':success}
    fixtures=0
    for H in [{'x'},{'x','y'}]:
        alpha=['a','x','y'];codes={(a,) for a in alpha if a not in H}|{(a,b) for a in alpha for b in H};assert ud(codes)
        for n in range(1,9):
            for word in itertools.product(alpha,repeat=n):
                prefix=next((i for i,u in enumerate(word) if u not in H),len(word));count,path=dp(word,codes);assert count==int(prefix%2==0)
                if count:assert sum(path,())==word and all(len(c)==1 and c[0] not in H or len(c)==2 and c[-1] in H for c in path)
                fixtures+=1
    expected='ALL_FIXED_I_OMISSION_CODES_COVER' if all(r['classification_exact'] for r in receipts.values()) else 'PARTIAL_FIXED_COUNTERCODE_COVER';assert result['status']==expected
    out={'status':'PASS','native_whole_type_parse_checks':parse_checks,'original_groups_checked':sum(len(v) for v in data.values()),'exhaustive_source_free_words':fixtures,'readers':receipts,'scope':'Formal coverage/UD/identity only; no native phonetic values, historical selection or predictive statistics.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
