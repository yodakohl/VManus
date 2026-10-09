"""Fixed head/follower capacity; only original whole physical groups."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip, hashlib, json, sys

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
A = D / 'artifacts'
S = json.loads((D / 'src/SPEC.json').read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assess(rows, signs):
    counts = Counter(r['ivtff_group_raw'] for r in rows)
    branches = defaultdict(list)
    for r in rows:
        u = r['units']
        if len(u) >= 2:
            branches[(u[0], u[1])].append(r)
    heads = []
    for h in signs:
        followers = [x for x in signs if (h, x) in branches]
        different = [x for x in followers if x != h]
        witnesses = []
        for x in followers:
            matches = branches[(h, x)]
            r = min(matches, key=lambda v: (v['ivtff_group_raw'], v['id']))
            witnesses.append(dict(follower=x, id=r['id'], page=r['page'],
                                  locus=r['locus'], word=r['ivtff_group_raw'],
                                  units=r['units'], whole_form_occurrences=counts[r['ivtff_group_raw']],
                                  branch_occurrences=len(matches)))
        heads.append(dict(head=h, followers=followers, nonself_followers=different,
                          initial_nonsingleton_occurrences=sum(len(branches[(h, x)]) for x in followers),
                          excluded=len(different) > 3,
                          contradiction_followers=different[:4] if len(different) > 3 else [],
                          witnesses=witnesses))
    survivors = [h['head'] for h in heads if not h['excluded']]
    qfollowers = next(h['followers'] for h in heads if h['head'] == 'q')
    return dict(groups=len(rows), types=len(counts), heads=heads,
                survivors=survivors,
                status='ALL_RENAMINGS_EXCLUDED' if not survivors else 'NECESSARY_SURVIVORS_ONLY',
                literal_q_key_excluded=not set(qfollowers) <= {'q', 'a', 'o', 'e'})


def fixtures():
    signs = S['signs']
    words = [('q',), ('q','q'), ('q','a'), ('q','o'), ('q','e'), ('a','q','t')]
    def make(ws):
        return [dict(units=list(w), ivtff_group_raw=''.join(w), id=str(i), page='toy', locus='toy') for i,w in enumerate(ws)]
    h = next(x for x in assess(make(words), signs)['heads'] if x['head'] == 'q')
    assert not h['excluded'] and h['nonself_followers'] == ['a','o','e']
    for ws in [words+[('q','i')], [w for w in words if w != ('q','q')]+[('q','i')]]:
        assert next(x for x in assess(make(ws), signs)['heads'] if x['head'] == 'q')['excluded']
    rename = dict(zip(signs, reversed(signs)))
    renamed = [tuple(rename[x] for x in w) for w in words]
    assert not next(x for x in assess(make(renamed), signs)['heads'] if x['head'] == rename['q'])['excluded']
    carrier = json.loads((ROOT / S['carrier']).read_text())
    high = {signs[j//22] for j in range(len(carrier['literal_code']['escaped_source']))}
    assert high == {'a','o','e'} and 'q' not in high
    return dict(status='PASS', checks=['singleton ignored','noninitial ignored','three plus self survives','four without self excludes','bijection invariance','all escape high digits'])


def main():
    if '--fixtures' in sys.argv:
        print(json.dumps(fixtures(), indent=2)); return
    assert not (A / 'RESULT.json').exists()
    for p, h in json.loads((A / 'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert digest(ROOT / p) == h, p
    assert digest(ROOT / S['source']) == S['source_sha256']
    assert digest(ROOT / S['carrier']) == S['carrier_sha256']
    source = json.loads(gzip.decompress((ROOT / S['source']).read_bytes()))
    allowed = set(json.loads((ROOT / S['scope_spec']).read_text())['allowed'])
    result = dict(experiment='GDT1249', readers={}, started_utc=datetime.now(timezone.utc).isoformat())
    for ed in S['readers']:
        rows = source[ed]
        for r in rows:
            assert r['page'] in allowed and not r['page'].startswith('f84') and r['page'] != 'f116v'
            assert r['kind'] == 'P' and r['left_separator'] == r['right_separator'] == 'DEFINITE_SPACE'
            assert r['edition'] == ed and ''.join(r['units']) == r['ivtff_group_raw']
        result['readers'][ed] = assess(rows, S['signs'])
    result['status'] = ('ALL_RENAMINGS_EXCLUDED_ALL_READINGS' if all(not v['survivors'] for v in result['readers'].values()) else 'READER_SPECIFIC_NECESSARY_SURVIVORS')
    result['completed_utc'] = datetime.now(timezone.utc).isoformat()
    (A / 'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({ed:{'survivors':v['survivors'], 'nonself_degrees':{h['head']:len(h['nonself_followers']) for h in v['heads']}} for ed,v in result['readers'].items()},indent=2))


if __name__ == '__main__': main()
