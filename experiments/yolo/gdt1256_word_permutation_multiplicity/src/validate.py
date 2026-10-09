import hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
spec=json.loads((B/'src/SPEC.json').read_text());r=json.loads((B/'artifacts/RESULT.json').read_text());raw=(R/spec['source']).read_bytes()
assert hashlib.sha256(raw).hexdigest()==spec['source_sha256'];d=json.loads(raw)
def classes(w):
    remaining=set(range(len(w)));sizes=[]
    while remaining:
        i=min(remaining);equal={j for j in remaining if w[j]==w[i]};sizes.append(len(equal));remaining-=equal
    return tuple(sorted(sizes,reverse=True))
words=[(s['ref'],i,w) for s in d['source_sections'] for i,w in enumerate(s['words'])];six=[x for x in words if len(x[2])==6]
hits=[{'section':s,'word_index_zero_based':i,'word':w} for s,i,w in six if classes(w)==(4,1,1)]
assert len(words)==6288==r['source_tokens'] and len(six)==r['length_six_tokens']
assert len({w for _,_,w in six})==r['length_six_types']
assert hits==r['hits'] and len(hits)==r['support_tokens'] and len({h['word'] for h in hits})==r['support_types']
for cell in r['all_length_six_signature_counts']:
    assert cell['tokens']==sum(classes(w)==tuple(cell['signature']) for _,_,w in six)
assert sum(c['tokens'] for c in r['all_length_six_signature_counts'])==len(six)
assert r['status']==('FIXED_SOURCE_PERMUTATION_ENVELOPE_EXCLUDED' if not hits else 'SIGNATURE_CAPACITY_ONLY_NO_KEY')
assert classes(spec['units'])==(4,1,1)
perms=set(itertools.permutations('AABACA'));assert len(perms)==r['fixture_unique_permutations'] and all(classes(x)==(4,1,1) for x in perms)
assert classes('AaAaAB')!=(4,1,1) and classes('BBAAAA')!=(4,1,1)
# No correction or alternate atomization of the existing witness.
wp=(R/spec['witness_profile']).read_bytes();assert hashlib.sha256(wp).hexdigest()==spec['witness_sha256']
p=next(p for p in json.loads(wp)['profiles'] if p['form']=='keeees')
for reader,v in r['native_witness'].items():assert v=={'count':p['editions'][reader]['count'],'examples':p['editions'][reader]['examples']}
for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
out={'status':'PASS','checks':['source hash','all6288sourcepositions','equality-class signature enumeration','all retained six-letter signatures','all hit locations','existing native witness receipt','complete valid-token permutations','negative signature fixtures','registration hashes'],'scope':'Exact source/count consistency, not physical alphabet or source identification.'}
(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
