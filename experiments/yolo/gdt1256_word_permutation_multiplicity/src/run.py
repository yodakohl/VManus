import collections,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def signature(s):return sorted(collections.Counter(s).values(),reverse=True)
def main():
    lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
    spec=json.loads((B/'src/SPEC.json').read_text())
    raw=(R/spec['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==spec['source_sha256']
    wp=(R/spec['witness_profile']).read_bytes();assert hashlib.sha256(wp).hexdigest()==spec['witness_sha256']
    profile=json.loads(wp)
    p=next(p for p in profile['profiles'] if p['form']=='keeees')
    witness={}
    for reader,values in p['editions'].items():
        assert values['count']==1
        witness[reader]={'count':values['count'],'examples':values['examples']}
    data=json.loads(raw);hits=[];n=0;n6=0;types=set();sixsigs=collections.Counter()
    for sec in data['source_sections']:
        for index,w in enumerate(sec['words']):
            n+=1
            if len(w)==spec['word_length']:
                n6+=1;types.add(w);sig=signature(w);sixsigs[tuple(sig)]+=1
                if sig==spec['multiplicities']:hits.append({'section':sec['ref'],'word_index_zero_based':index,'word':w})
    assert n==spec['expected_source_tokens']==data['tokens']
    assert signature(spec['units'])==spec['multiplicities']
    valid='AABACA';assert signature(valid)==[4,1,1]
    permutations={''.join(x) for x in itertools.permutations(valid)}
    assert all(signature(x)==[4,1,1] for x in permutations)
    assert signature('AaAaAB')==[3,2,1] and signature('BBAAAA')==[4,2]
    result={'status':'FIXED_SOURCE_PERMUTATION_ENVELOPE_EXCLUDED' if not hits else 'SIGNATURE_CAPACITY_ONLY_NO_KEY','source_tokens':n,'source_sections':len(data['source_sections']),'length_six_tokens':n6,'length_six_types':len(types),'required_signature':spec['multiplicities'],'support_tokens':len(hits),'support_types':len({h['word'] for h in hits}),'hits':hits,'all_length_six_signature_counts':[{'signature':list(k),'tokens':v} for k,v in sorted(sixsigs.items())],'native_witness':witness,'fixture_unique_permutations':len(permutations),'scope':'Exact fixed-source vocabulary and working-unit premise; not a language ban or source-word meaning.'}
    (B/'artifacts/RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['native_witness','all_length_six_signature_counts','hits']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
