#!/usr/bin/env python3
"""Post-result word-local envelope explanation; no original solver imports."""
import collections,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];A=E/'artifacts';ROOT=E.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compatible(word,units):
    return len(word)==len(units) and all(word[i]!=word[j] or units[i]==units[j]
        for i in range(len(word)) for j in range(i))
def main():
    source=read(A/'SOURCE_PROJECTION.json');native=read(A/'NATIVE_INPUT.json')
    assert sha(ROOT/source['source'])==source['source_sha256']
    assert sha(ROOT/native['source'])==native['source_sha256']
    records=source['records'];words={w for r in records for w in r['words']}
    edges={pair for r in records for pair in zip(r['words'],r['words'][1:])}
    assert words==set(source['words']) and edges=={tuple(pair) for pair in source['edges']}
    groups=native['groups'];assert len(groups)==len(native['ids'])==len(native['raw_groups'])==59
    assert all(''.join(g)==raw for g,raw in zip(groups,native['raw_groups']))
    bylength=collections.defaultdict(list)
    for w in sorted(words):bylength[len(w)].append(w)
    domains=[{w for w in bylength[len(g)] if compatible(w,g)} for g in groups]
    successors=collections.defaultdict(set)
    for left,right in edges:successors[left].add(right)
    reachable=set();steps=[];boundary=None
    for i,candidates in enumerate(domains):
        previous=reachable
        possible=candidates if i==0 else candidates & {v for u in previous for v in successors[u]}
        reachable=possible
        steps.append({'position':i+1,'id':native['ids'][i],'raw':native['raw_groups'][i],
            'units':groups[i],'candidate_count':len(candidates),'reachable_count':len(possible),
            'reachable_source_words':sorted(possible)})
        if not possible:
            boundary={'left_position':i,'right_position':i+1,
                'left_reachable_words':sorted(previous),
                'all_successors_of_left_reachable':sorted({v for u in previous for v in successors[u]}),
                'right_candidate_count':len(candidates),'compatible_successors':[],
                'successor_alignment_checks':[{'source_word':w,'source_length':len(w),
                    'right_native_length':len(groups[i]),'word_local_compatible':compatible(w,groups[i])}
                    for w in sorted({v for u in previous for v in successors[u]})]}
            assert i>0 and all(not x['word_local_compatible'] for x in boundary['successor_alignment_checks'])
            break
    result={'status':'POST_RESULT_INDEPENDENT_UNKEYED_PREFIX_EXPLANATION',
      'experiment_id':'GDT1426','selected_after_registered_dual_UNSAT':True,
      'pins':{n:sha(A/n) for n in ['SOURCE_PROJECTION.json','NATIVE_INPUT.json','RESULT.json','VALIDATION.json']},
      'diagnostic_code_sha256':sha(Path(__file__)),
      'all_59_candidate_counts':[len(d) for d in domains],
      'all_single_word_domains_nonempty':all(domains),'minimum_single_word_candidates':min(map(len,domains)),
      'prefix_steps_until_first_failure':steps,'first_empty_prefix_position':steps[-1]['position'] if not reachable else None,
      'last_boundary':boundary,
      'proof':'Every full shared SOURCE-letter function supplies a locally compatible word at each position and a directed graph walk. This relaxation permits a different partial function per word. An empty reachable prefix therefore already excludes every full walk before any cross-word key consistency is imposed.',
      'limits':['This is a post-result explanatory computation, not a registered new test or another original solver execution.',
                'It diagnoses reference adjacency plus local word shape under the fixed projection, not an isolated failure of global key agreement.',
                'Source alternatives and the sole prefix survivor are not adopted translations or native word values.',
                'No generic Syriac-language or letter-merger ban; graph edges, source projection, native units and word correspondence remain assumptions.',
                'No new source, case, boundary, cap or automatic removal of edges is selected.']}
    out=A/'POST_RESULT_UNKEYED_PREFIX.json'
    if out.exists():assert read(out)==result
    else:out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'all_domains_nonempty':all(domains),'minimum':min(map(len,domains)),
        'prefix_counts':[s['reachable_count'] for s in steps],'first_empty':result['first_empty_prefix_position']}))
if __name__=='__main__':main()
