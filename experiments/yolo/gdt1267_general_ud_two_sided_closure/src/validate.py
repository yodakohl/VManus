import json,gzip,itertools,sys,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def controls():
    # Explicit codeword-list comparison, independent of bridge packet producer.
    tables=[['a','ab'],['a','ab','bba'],['ab','ba'],['a','bb'],['aa','ab','b']];tested=0
    for raw in tables:
        C=[tuple(s) for s in raw];parses={():()}
        for n in range(1,5):
            for seq in itertools.product(range(len(C)),repeat=n):
                w=sum((C[i] for i in seq),())
                if w in parses:assert parses[w]==seq
                parses[w]=seq
        for xy,seq in parses.items():
            for i in range(len(xy)):
                x,y=xy[:i],xy[i:]
                if x not in parses:continue
                for yz in parses:
                    if yz[:len(y)]!=y:continue
                    z=yz[len(y):]
                    if z not in parses:continue
                    a=parses[x]+parses[yz];b=seq+parses[z];assert a==b
                    assert sum((C[k] for k in a[len(parses[x]):len(seq)]),())==y;tested+=1
    # The nonUD counterexample has a/ab/bc/c yet no singleton b.
    assert 'a'+'bc'=='ab'+'c'
    return dict(status='PASS',explicit_tables=len(tables),four_premise_instances=tested,nonUD_counterexample=True)

def main():
    for name,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text())['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
    packet=json.loads((P/'artifacts/RESULT.json').read_text());source=json.loads(gzip.decompress((ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()))
    oldleft=json.loads((ROOT/'experiments/yolo/gdt1240_prefix_expansion_fourth_power/artifacts/NATIVE_PROOF.json').read_text())
    oldright=json.loads((ROOT/'experiments/yolo/gdt1241_suffix_quotient_expansion/artifacts/PROOFS.json').read_text())
    assert set(packet['readers'])==set(source)=={'IT2a','ZL3b','RF1b'}
    conclusions=0;bridges=0;ids=set();summary=[]
    for r,v in packet['readers'].items():
        byid={g['id']:g for g in source[r]};assert set(v['singletons'])==set('kes')
        for letter,d in v['singletons'].items():
            words=[]
            for n in d['premises']:
                if n['origin'].endswith('NATIVE_PROOF.json'):
                    original=next(x for x in oldleft[r]['proof_events'] if x['event_id']==n['node_id']);units=original['units'];count=original['occurrences']
                else:
                    assert n['origin']=='experiments/yolo/gdt1241_suffix_quotient_expansion/artifacts/PROOFS.json'
                    original=next(x for x in oldright[r]['nodes'] if x['id']==n['node_id']);units=original['word'];count=original['frequency']
                assert original['parents'] is None
                assert units==n['units'] and n['frequency']==count==len(n['source_ids'])
                assert original['source_ids']==n['source_ids'] and original['pages']==n['pages']
                # Check precisely all saved IDs. No search for replacement witnesses.
                for sid in n['source_ids']:
                    g=byid[sid];assert g['edition']==r and g['units']==units;ids.add(sid)
                assert sorted({byid[sid]['page'] for sid in n['source_ids']})==sorted(n['pages'])
                words.append(units)
            if d['rule']=='WHOLE':assert words==[[letter]]
            else:
                assert d['rule']=='TWO_SIDED' and len(words)==4
                x,xy,yz,z=words;assert x+[letter]==xy and [letter]+z==yz and x+yz==xy+z;bridges+=1
            conclusions+=1
            summary.append(dict(reader=r,unit=letter,rule=d['rule'],minimum_premise_occurrences=min(n['frequency'] for n in d['premises']),minimum_premise_selectors=min(len(n['pages']) for n in d['premises'])))
        assert v['forced_parse']==list('keeees')
        assert v['whole_witness_occurrences']==oldleft[r]['whole_witness_occurrences'] and len(v['whole_witness_occurrences'])==1
        for g in v['whole_witness_occurrences']:assert byid[g['id']]==g and g['units']==list('keeees');ids.add(g['id'])
    originalsource=json.loads((ROOT/'experiments/yolo/gdt1240_prefix_expansion_fourth_power/artifacts/RESULT.json').read_text())
    assert packet['source_results']==originalsource['sources'] and len(packet['source_results'])==5
    assert all(v['supporting_tokens']==0 for v in packet['source_results'].values())
    assert sum(v['source_tokens'] for v in packet['source_results'].values())==87219
    assert packet['status']=='GENERAL_UD_FIXED_SOURCE_EXCLUSION_EXTENDED'
    assert packet['native_closure_executed'] is False and packet['new_source_census'] is False
    out=dict(status='PASS',singleton_conclusions=conclusions,two_sided_bridges=bridges,distinct_original_ids_checked=len(ids),premise_support=summary,scope='existing witness integrity and bridge algebra; no new native pattern/source census')
    (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':
    if '--controls' in sys.argv:
        out=controls();(P/'artifacts/BRIDGE_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
    else:main()
