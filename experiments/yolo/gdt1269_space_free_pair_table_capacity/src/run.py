import json,gzip,hashlib,re,itertools,datetime,sys
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
OLD=ROOT/'experiments/yolo/gdt1259_paragraph_integer_balance'
def parse(stream,marker,offset):
    pairs=[];singles=[];i=offset
    while i<len(stream):
        if marker is not None and stream[i]==marker:singles.append(i);i+=1
        elif i+1<len(stream):pairs.append([i,stream[i],stream[i+1]]);i+=2
        else:break
    return dict(pairs=pairs,singletons=singles,dangling=(i if i<len(stream) else None))
def mandatory(s,h):
    ps=[parse(s,h,k) for k in (0,1)]
    return {tuple(x[1:]) for x in ps[0]['pairs']} & {tuple(x[1:]) for x in ps[1]['pairs']}
def controls():
    books=0;clips=0
    for h,pool in [(None,['aa','ab','ba','bb']),('a',['ba','bb'])]:
        for mask in range(1<<len(pool)):
            D={tuple(w) for j,w in enumerate(pool) if mask>>j&1};code=sorted(D)+([(h,)] if h is not None else [])
            if not code:continue
            books+=1
            for n in range(5):
                for sequence in itertools.product(code,repeat=n):
                    text=sum(sequence,())
                    for start in range(len(text)+1):
                        for stop in range(start,len(text)+1):assert mandatory(text[start:stop],h)<=D;clips+=1
    assert mandatory(tuple('aaaa'),None)=={('a','a')}
    assert mandatory(tuple('aba'),None)|mandatory(tuple('bab'),None)==set()
    assert mandatory(tuple('xbcx'),'x')=={('b','c')}
    assert parse(tuple('abxc'),'x',0)['pairs']==[[0,'a','b']]
    assert parse(tuple('abxc'),'x',1)['pairs']==[[1,'b','x']]
    return dict(status='PASS',generating_codebooks=books,contiguous_clips=clips,named_fixtures=4)

def main():
    for name,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text())['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    raw=json.loads((OLD/'artifacts/CERTIFICATES.json').read_text());spec=json.loads((OLD/'src/SPEC.json').read_text());units=spec['working_signs'];regex=re.compile('|'.join(sorted(units,key=lambda u:(-len(u),u))))
    reports=[];all_packets=[]
    for reader,rows in sorted(raw.items()):
        snippets=[]
        for row in rows:
            stream=[];pointers=[]
            for g in row['raw_groups']:
                us=regex.findall(g['ivtff_group_raw']);assert ''.join(us)==g['ivtff_group_raw']
                for j,u in enumerate(us):
                    stream.append(u);pointers.append(dict(id=f"{reader}|{g['locus']}|G{int(g['source_group_index']):03d}",unit_offset=j,page=g['page'],locus=g['locus']))
            assert [Counter(stream)[u] for u in units]==row['paragraph']['counts']
            snippets.append(dict(id=row['paragraph']['id'],units=stream,pointers=pointers))
        cases=[]
        for marker in [None]+sorted(units):
            required={};snipcases=[]
            for s in snippets:
                ps=[parse(s['units'],marker,k) for k in (0,1)];common=sorted({tuple(x[1:]) for x in ps[0]['pairs']} & {tuple(x[1:]) for x in ps[1]['pairs']})
                snipcases.append(dict(id=s['id'],parses=ps,mandatory_pairs=common))
                for pair in common:
                    if pair not in required:
                        indices=[next(x[0] for x in p['pairs'] if tuple(x[1:])==pair) for p in ps]
                        required[pair]=dict(pair=pair,snippet=s['id'],indices=indices,provenance=[[s['pointers'][i],s['pointers'][i+1]] for i in indices])
            cases.append(dict(marker=marker,mandatory_pair_count=len(required),excluded_at32=len(required)>32,mandatory_pairs=sorted(required)))
            all_packets.append(dict(reader=reader,marker=marker,snippets=snipcases,witnesses=[required[k] for k in sorted(required)]))
        lower=min(c['mandatory_pair_count'] for c in cases)
        reports.append(dict(reader=reader,snippets=len(snippets),units=sum(len(s['units']) for s in snippets),minimum_necessary_pair_count=lower,minimizers=[c['marker'] for c in cases if c['mandatory_pair_count']==lower],excluded_at32=lower>32,cases=cases))
    out=dict(status='ALL_SMALL_PAIR_TABLES_EXCLUDED' if all(r['excluded_at32'] for r in reports) else 'PARTIAL_PAIR_TABLE_CAPACITY_BOUND',pair_entry_cap=32,reports=reports)
    (P/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
    (P/'artifacts/PAIR_CERTIFICATES.json.gz').write_bytes(gzip.compress(json.dumps(all_packets,sort_keys=True).encode(),mtime=0))
    (P/'artifacts/RUN_RECEIPT.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),lock_sha256=hashlib.sha256((P/'src/REGISTRATION_LOCK.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps(dict(status=out['status'],reports=[{k:v for k,v in r.items() if k!='cases'} for r in reports]),indent=2))
if __name__=='__main__':
    if '--controls' in sys.argv:
        x=controls();(P/'artifacts/CONTROLS.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x))
    else:main()
