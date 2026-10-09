import collections,csv,hashlib,io,itertools,json,re,subprocess
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
    s=json.loads((B/'src/SPEC.json').read_text());lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
    for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
    source=json.loads((R/s['source']).read_text());old=json.loads((R/s['old_summary']).read_text())
    letters=collections.Counter(c for sec in source['source_sections'] for w in sec['words'] for c in w)
    assert set(letters)<=set(s['source_alphabet']);N=sum(letters.values());K=letters[s['value_one_source_letter']]
    assert N==24668 and source['tokens']==6288
    allowed=json.loads((R/s['scope_spec']).read_text())['allowed'];assert len(set(allowed))==len(allowed)==179
    assert all(not p.startswith('f84') and p!='f116v' for p in allowed)
    cmd=['./vmanus-exp','query-tsv',s['native_source'],'--selector','page']
    for page in allowed:cmd+=['--allow',page]
    cmd+=['--columns',','.join(s['columns'])]
    call=subprocess.run(cmd,cwd=R,text=True,capture_output=True,check=True)
    (B/'artifacts/GUARD_RECEIPT.json').write_text(json.dumps({'command':cmd,'receipt':call.stderr.strip(),'output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest()},indent=2)+'\n')
    pattern=re.compile('(?:'+'|'.join(sorted(s['working_signs'],key=lambda x:(-len(x),x)))+')+')
    eligible=collections.Counter();singles={r:[] for r in s['readers']};ids=set();rawcount=0
    for row in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
        rawcount+=1
        if row['kind']!='P' or row['left_separator'] not in ('DEFINITE_SPACE','LINE_START') or row['right_separator'] not in ('DEFINITE_SPACE','LINE_END') or not pattern.fullmatch(row['ivtff_group_raw']):continue
        key=(row['edition'],row['locus'],row['source_group_index']);assert key not in ids;ids.add(key)
        eligible[row['edition']]+=1
        if row['ivtff_group_raw'] in s['working_signs']:singles[row['edition']].append(row)
    assert dict(eligible)==old['eligible_groups'],(eligible,old['eligible_groups'])
    readers={}
    for reader in s['readers']:
        G=eligible[reader];S=len(singles[reader]);status='INSUFFICIENT_PACKET_POPULATION' if G<N else ('VALUE_ONE_CAPACITY_EXCLUDED' if K>S else 'NECESSARY_CAPACITY_ONLY')
        readers[reader]={'eligible_groups':G,'singleton_groups':S,'singleton_upper_bound_any_N_selection':min(S,N),'source_required_singletons':K,'deficit':K-S,'status':status,'singleton_forms':dict(sorted(collections.Counter(r['ivtff_group_raw'] for r in singles[reader]).items()))}
    # Positive weights permit sum1only at length1; shared weights do not matter.
    fixtures=0
    for n in range(1,6):
        for idx in itertools.product(range(3),repeat=n):
            if sum([1,1,2][i] for i in idx)==1:assert n==1
            fixtures+=1
    assert sum([1,0])==1 # zero weight explicitly violates the positive-weight premise
    result={'status':'ALL_READERS_VALUE_ONE_CAPACITY_EXCLUDED' if all(v['status']=='VALUE_ONE_CAPACITY_EXCLUDED' for v in readers.values()) else 'MIXED_OR_INCONCLUSIVE','source_sections':len(source['source_sections']),'source_words':source['tokens'],'source_letters':N,'value_one_letters':K,'source_value_one_fraction':K/N,'source_letter_counts':dict(sorted(letters.items())),'native_guarded_rows':rawcount,'readers':readers,'positive_weight_fixtures':fixtures,'scope':'No complete fixed source embedding wholly inside the declared eligible packet pool if excluded; outside-pool packets and other source/contracts remain open.'}
    (B/'artifacts/RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (B/'artifacts/SINGLETONS.json').write_text(json.dumps(singles,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','source_letters','value_one_letters','readers']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
