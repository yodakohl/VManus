"""Carrier-invariant counts for one frozen finite content grouping."""
from collections import Counter
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
A = D / 'artifacts'
BASE = ROOT / 'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts'
N = 8000


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, value):
    (A / name).write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')


def main():
    lock = json.loads((A / 'REGISTRATION_LOCK.json').read_text())
    for path, digest in lock['files'].items():
        assert sha(ROOT / path) == digest, path
    source = json.loads((BASE / 'SOURCE_MESSAGES.json').read_text())
    assert len(source) == 256 and all(len(page) == 20 for page in source)
    encoded = []
    for page in source:
        words = []
        for r in page:
            assert len(r) == 7 and all(0 <= x < c for x,c in zip(r,[8,64,8,8,8,4,4]))
            op, plant, part, state, medium, amount, duration = r
            words.extend([(plant,part,state,amount), (plant,op,medium,duration)])
        recovered = []
        for a,b in zip(words[::2], words[1::2]):
            assert a[0] == b[0]
            recovered.append([b[1],a[0],a[1],a[2],b[2],a[3],b[3]])
        assert recovered == page
        encoded.append(words)
    sample = [w for page in encoded for w in page][:N]
    assert len(sample) == N
    counts = Counter(sample)
    freq = [{'tuple':list(w),'count':c} for w,c in sorted(counts.items())]
    top = sorted(counts.items(), key=lambda x:(-x[1],x[0]))[:10]
    v,t = len(counts), sum(c for _,c in top)
    targets = json.loads((BASE / 'RESULT.json').read_text())['targets']
    checks = {}
    for ed,row in targets.items():
        assert row['tokens'] == N
        nv,nt = round(N*row['type_ratio']), round(N*row['top10_share'])
        checks[ed] = {'native_type_count':nv,'native_top10_count':nt,
                      'type_interval':[nv-400,nv+400],'top10_interval':[nt-400,nt+400],
                      'types_pass':abs(v-nv)<=400,'top10_pass':abs(t-nt)<=400}
    assert set(checks) == {'IT2a','RF1b','ZL3b'}
    passed = all(r['types_pass'] and r['top10_pass'] for r in checks.values())
    result = {'experiment':'GDT1210','status':'TWO_GROUP_CONTENT_FREQUENCY_NOT_EXCLUDED' if passed else 'TWO_GROUP_CONTENT_FREQUENCY_FAIL',
              'sample_groups':N,'sample_complete_pages':200,'distinct_types':v,
              'type_ratio':v/N,'top10_count':t,'top10_share':t/N,
              'top10':[{'tuple':w,'count':c} for w,c in top],
              'reader_checks':checks,'full_pages_recovered':256,
              'full_messages_recovered':5120,'full_output_groups':10240,
              'native_meanings':0,'new_target_intake':False,
              'scope':'Fixed artificial source/common injective tuple renderer only; no native carrier, general content-system exclusion or independent confirmation.'}
    save('ENCODED_TUPLES.json', encoded)
    save('FREQUENCIES.json', freq)
    save('RESULT.json', result)
    save('RUN_RECEIPT.json', {'runner_sha256':sha(Path(__file__)),'lock_sha256':sha(A/'REGISTRATION_LOCK.json'),
                            'encoded_sha256':sha(A/'ENCODED_TUPLES.json'),'frequencies_sha256':sha(A/'FREQUENCIES.json')})
    print(json.dumps({k:v for k,v in result.items() if k!='top10'},indent=2))


if __name__ == '__main__':
    main()
