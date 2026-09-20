"""Post-result exact search quotient; prepares inputs only, no target solving."""
from common import *
import collections,csv,itertools

def main():
    s,g=inputs();panel=read(A/'PANEL.json');originals=read(A/'ORIGINAL_CANDIDATES.json');settings=[dict(zip(g['variants'],values)) for values in itertools.product(*g['variants'].values())];names=('C','G','W');groups={};total=0
    for row in originals:
        for pi in (2,4):
            shared={w:row['code'][w] for w in sorted(set(panel[pi]['words'])&row['code'].keys())}
            klass='FIRST_REFERENCE' if shared['chedy']=='FIRST_CARGO' else 'DIFFERENT_CARGO_NAME'
            canonical={'chedy':'FIRST_CARGO' if klass=='FIRST_REFERENCE' else 'G','otaiin':'THERE','qokedy':'C','qoky':'FERRY'}
            matches=[]
            for image in itertools.permutations(names):
                rename=dict(zip(names,image))
                if {w:rename.get(v,v) for w,v in shared.items()}==canonical:matches.append(rename)
            assert len(matches)==(2 if klass=='FIRST_REFERENCE' else 1)
            for vi in row['valid_variants']:
                key=(pi,klass,vi);group=groups.setdefault(key,dict(context_index=pi,context=panel[pi]['id'],class_name=klass,variant_index=vi,variant=settings[vi],canonical_lexicon=canonical,members=[]))
                group['members'].append(dict(original_id=row['id'],original_to_canonical=matches));total+=1
    out=[]
    for i,(_,group) in enumerate(sorted(groups.items()),1):out.append(dict(id='FULL'+str(i).zfill(2),**group,status='PREPARED_NOT_QUERIED'))
    assert len(out)==20 and total==312
    assert {r['variant_index'] for r in out if r['class_name']=='DIFFERENT_CARGO_NAME'}=={0,2,4,6,8,10,12,14}
    assert {r['variant_index'] for r in out if r['class_name']=='FIRST_REFERENCE'}=={0,2}
    # Different reconstruction: every original-setting/context membership must occur once.
    actual=[(m['original_id'],r['context_index'],r['variant_index']) for r in out for m in r['members']]
    expected=[(r['id'],pi,vi) for pi in (2,4) for r in originals for vi in r['valid_variants']]
    assert collections.Counter(actual)==collections.Counter(expected)
    for r in out:
        for m in r['members']:
            original=next(x for x in originals if x['id']==m['original_id'])
            for rename in m['original_to_canonical']:
                inverse={v:k for k,v in rename.items()};assert len(inverse)==3
                assert {w:inverse.get(v,v) for w,v in r['canonical_lexicon'].items()}=={w:original['code'][w] for w in r['canonical_lexicon']}
    put('NEXT_FULL_CONTENT_CASES.json',out)
    put('FOLLOWUP_SCOPE_CHECK.json',dict(status='PASS',original_setting_context_cases=312,canonical_full_content_queries=20,negative_reduction='Full grammar/meaning is invariant under anonymous cargo bijections;only four old spellings occur in either added paragraph.',positive_lifting='Keep every valid original member and every listed cargo inverse,plus its unchanged original parse;full replays required.',target_queries_executed=0,meaning_claim='No new SAT,UNSAT,translation or independent capacity.'))
    with (A/'NEXT_FULL_CONTENT_CASES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['system','context_index','class','variant','original_members','status'])
        for r in out:w.writerow([r['id'],r['context_index'],r['class_name'],r['variant_index'],len(r['members']),r['status']])
    print('PASS:312original-setting/context cases covered by20unexecuted canonical full-content inputs')
if __name__=='__main__':main()
