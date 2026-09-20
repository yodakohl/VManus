#!/usr/bin/env python3
import collections,csv,itertools,time
from common import *
import grammar,independent

def main():
    checklock();s=read(E/'src/SPEC.json');g=read(R/s['grammar']);packet=read(R/s['source_packet']);panel=read(A/'PANEL.json');pred=read(A/'PREDICTIONS.json');result=read(A/'RESULT.json');domains=read(A/'DOMAINS.json')
    counts={k:1+int(k=='THEN') for k in g['patterns']};N=sum(counts[k]*len(p) for k,p in g['patterns'].items());assert N==pred['source_groups'] and counts==pred['pattern_counts']
    assert [p['edition'] for p in panel]==list(packet['readers'])
    for p in panel:
        src=packet['readers'][p['edition']];words=[x['ivtff_group_raw'] for line in src['rows'] for x in line['groups']]
        assert p['words']==words and p['groups']==len(words) and p['source_ids']==[x['source_group_id'] for line in src['rows'] for x in line['groups']]
        assert p['page']=='f83r' and p['leaf']==83 and p['whole_paragraph_contract']==src['whole_paragraph_contract'] and p['strict_anchor_eligible']==src['strict_anchor_eligible'] and p['uncertain_groups']==src['uncertain_groups']
        status='UNKNOWN_PARAGRAPH_CONTRACT' if not src['whole_paragraph_contract'] else 'CONTRADICTED_COMPLETE_CONTENT_COUNT' if len(words)!=N else 'SEARCH_LITERAL' if src['strict_anchor_eligible'] else 'SEARCH_CONDITIONALLY_SOURCE_UNCERTAIN'
        assert p['status']==status
    raw=next(p['words'] for p in panel if p['edition']=='ZL3b');freq=collections.Counter(raw)
    projected=sorted({w for w,n in freq.items() if n>1}|set(s['inherited_hypothesis_forms']));assert projected==pred['projection_words']
    checks=[];semantic=0;allrows=[]
    for family in s['families']:
        r=read(A/('FAMILY_'+family+'.json'));assert r['family']==family
        b=independent.build(raw,g,family,timeout=s['independent_query_ms']);begin=str(b['solver'].check());seen=[];failures=0
        assert begin!='unsat' or not r['attempts']
        for index,row in enumerate(r['attempts']):
            assert row['attempt']==index;grammar.ground(row,raw,g,family)
            # Independent fixed bit-state/reference evaluation of all32 variants.
            ev=evaluate(row['parse'],g,s,independent=True,keep_full=bool(row['coherent_variants']));semantic+=32
            assert ev['coherent_variants']==row['coherent_variants'] and ev['replays']==row['replays'],(family,index)
            if row['coherent_variants']:
                assert ev['full']==row['full_replays'];values={w:row['code'][w] for w in projected}
                for vi in ev['coherent_variants']:
                    if any(x['values']==values and x['variant_index']==vi for x in seen):continue
                    seen.append(dict(tuple=len(seen),attempt=index,values=values,variant_index=vi));independent.block_projection(b,values,vi)
            else:failures+=1
            independent.block_exact(b,row)
            allrows.append((family,row))
        assert seen==r['positive_tuples'] and failures==r['failed_maps']
        final=str(b['solver'].check())
        if r['exhaustive_projection']:assert final!='sat' and r['queries'][-1]=='unsat'
        if r['next_syntactic_witness_unexamined']:
            grammar.ground(r['next_syntactic_witness_unexamined'],raw,g,family);assert final!='unsat'
            assert not any(x['values']=={w:r['next_syntactic_witness_unexamined']['code'][w] for w in projected} and x['variant_index']==r['next_syntactic_witness_unexamined']['solver_variant'] for x in seen)
        for d in [x for x in domains if x['family']==family]:
            assert d['occurrences']==freq[d['word']] and d['values']==sorted({row['code'][d['word']] for row in r['attempts'] if row['coherent_variants']})
            assert d['projected']==(d['word'] in projected) and d['domain_exhaustive']==(d['projected'] and r['exhaustive_projection'])
        checks.append(dict(family=family,initial_cvc5=begin,final_blocked_cvc5=final,projected_tuples=len(seen),failed_complete_maps=failures,primary_exhaustive=r['exhaustive_projection']))
    assert len(domains)==len(set(raw))*len(s['families'])
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==len(allrows)
    for t,(family,row) in zip(table,allrows):
        assert t['family']==family and int(t['attempt'])==row['attempt'] and json.loads(t['code'])==row['code'] and t['coherent_variants']==','.join(map(str,row['coherent_variants']))
        assert t['status']==('COHERENT' if row['coherent_variants'] else 'ALL_32_VARIANTS_REJECTED') and t['independent_meaning_capacity']=='0'
    with (A/'PROJECTED_CANDIDATES.tsv').open() as f:tuples=list(csv.DictReader(f,delimiter='\t'))
    expected=[(family,p) for family in s['families'] for p in read(A/('FAMILY_'+family+'.json'))['positive_tuples']]
    assert len(tuples)==len(expected)
    for row,(family,p) in zip(tuples,expected):
        assert row['family']==family and int(row['tuple'])==p['tuple'] and int(row['attempt'])==p['attempt'] and int(row['variant_index'])==p['variant_index']
        for word,value in p['values'].items():assert row[word]==value
        for key,value in pred['all_variants'][p['variant_index']].items():assert row[key]==value
    for family,brief in zip(s['families'],result['families']):
        r=read(A/('FAMILY_'+family+'.json'))
        for k,v in brief.items():assert r[k]==v
    out=dict(status='INCOMPLETE_INDEPENDENT_COVERAGE' if any(q['primary_exhaustive'] and q['final_blocked_cvc5']!='unsat' for q in checks) else 'PASS',families=checks,complete_candidates_checked=len(allrows),all_variant_semantic_checks=semantic,word_domain_rows=len(domains),independent_unknown_checks=sum(x in ('unknown',) for q in checks for x in (q['initial_cvc5'],q['final_blocked_cvc5'])),scope='Complete hypothetical source-inventory code projection; independent flow and old bit-state replay, same author. Not source identity, morphology or word confirmation.',confirmed_words=0,independent_meaning_capacity=0);put('VALIDATION.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
