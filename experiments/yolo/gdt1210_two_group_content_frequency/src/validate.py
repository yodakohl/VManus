"""Separate address-based reconstruction/count check; no runner import."""
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
A = D / 'artifacts'
BASE = ROOT / 'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def address(t):
    p,x,y,z = t
    return ((p*8+x)*8+y)*4+z


def tuple_at(n):
    n,z = divmod(n,4)
    n,y = divmod(n,8)
    p,x = divmod(n,8)
    return [p,x,y,z]


def main():
    for rel,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert sha(ROOT/rel) == h
    source = json.loads((BASE/'SOURCE_MESSAGES.json').read_text())
    encoded = json.loads((A/'ENCODED_TUPLES.json').read_text())
    all_addresses = []
    for p,page in enumerate(source):
        expected = []
        for r in page:
            for ix in ((1,2,3,5),(1,0,4,6)):
                expected.append(address([r[k] for k in ix]))
        assert [tuple_at(n) for n in expected] == encoded[p]
        for j in range(len(page)):
            x,y = tuple_at(expected[j*2]),tuple_at(expected[j*2+1])
            original = [None]*7
            for t,ix in ((x,(1,2,3,5)),(y,(1,0,4,6))):
                for v,k in zip(t,ix):
                    assert original[k] in (None,v)
                    original[k] = v
            assert original == page[j]
        all_addresses.extend(expected)
    assert len(source)==256 and len(encoded)==256 and len(all_addresses)==10240
    freq = {}
    for n in all_addresses[:8000]:
        freq[n] = freq.get(n,0)+1
    saved = json.loads((A/'FREQUENCIES.json').read_text())
    assert len(saved) == len(freq)
    assert {address(r['tuple']):r['count'] for r in saved} == freq
    result = json.loads((A/'RESULT.json').read_text())
    assert result['distinct_types'] == len(freq)
    top = sorted(freq,key=lambda n:(-freq[n],n))[:10]
    t = sum(freq[n] for n in top)
    assert result['top10_count'] == t
    assert result['top10'] == [{'tuple':tuple_at(n),'count':freq[n]} for n in top]
    assert result['type_ratio']==len(freq)/8000 and result['top10_share']==t/8000
    targets = json.loads((BASE/'RESULT.json').read_text())['targets']
    checks = []
    for ed,native in targets.items():
        nv=int(round(native['type_ratio']*8000));nt=int(round(native['top10_share']*8000))
        row=result['reader_checks'][ed]
        assert row['type_interval']==[nv-400,nv+400]
        assert row['top10_interval']==[nt-400,nt+400]
        for value,baseline,label in ((len(freq),nv,'types_pass'),(t,nt,'top10_pass')):
            flag=baseline-400<=value<=baseline+400
            assert row[label]==flag
            checks.append(flag)
    status='TWO_GROUP_CONTENT_FREQUENCY_NOT_EXCLUDED' if all(checks) else 'TWO_GROUP_CONTENT_FREQUENCY_FAIL'
    assert result['status']==status
    for n in range(64*8*8*4):
        assert address(tuple_at(n))==n
    out={'status':'PASS','scientific_status':status,'full_messages':5120,
         'sample_groups':8000,'frequency_cells':len(freq),'checks_passed':sum(checks),
         'checks_total':len(checks),'validator_sha256':sha(Path(__file__)),
         'result_sha256':sha(A/'RESULT.json'),
         'scope':'Same-author independent implementation/source check; no native validation.'}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))


if __name__ == '__main__':
    main()
