#!/usr/bin/env python3
"""Independent permutation and raw-window enumeration of every graph."""
import csv
import gzip
import hashlib
import io
import itertools
import json
import re
from collections import defaultdict,Counter
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
SOURCE=ROOT/'experiments/yolo/gdt1106_frozen_domain_transfer/artifacts/SOURCE.tsv.gz'

def extract(lines,n):
    kept=[];lost=0
    for line in lines:
        suffix=line['locus'].split('.')
        for i in range(len(line['groups'])-n+1):
            rows=line['groups'][i:i+n]
            if len(suffix)!=2 or not suffix[1].isdigit() or any(re.fullmatch('[a-z]+',r['ivtff_group_raw']) is None for r in rows):
                lost+=1;continue
            kept.append({'raw':[r['ivtff_group_raw'] for r in rows],'ids':[r['source_group_id'] for r in rows],
                'start':[int(suffix[1]),int(rows[0]['source_group_index'])],
                'end':[int(suffix[1]),int(rows[-1]['source_group_index'])],'locus':line['locus']})
    return kept,lost

def independent(lines,spec):
    triples,x3=extract(lines,3);fives,x5=extract(lines,5)
    # Enumerate raw pairs sharing the two non-part positions. No producer import.
    valid3=[w for w in triples if len(set(w['raw']))==3]
    valid5=[w for w in fives if len(set(w['raw']))==5]
    counts=Counter();found=[]
    for ii,io_order in enumerate(spec['orientations']['induce']):
        ip=io_order.index('part');ia=io_order.index('induce');ie=io_order.index('result')
        buckets=defaultdict(list)
        for w in valid3:buckets[(w['raw'][ia],w['raw'][ie])].append(w)
        for (action,result),bucket in buckets.items():
            for h in bucket:
                for f in bucket:
                    head=h['raw'][ip];flower=f['raw'][ip]
                    if head==flower or h['end']>=f['start'] or len({head,flower,action,result})!=4:continue
                    counts['induce_forks']+=1
                    for u in valid5:
                        if not h['end']<u['start'] or not u['end']<f['start'] or flower not in u['raw']:continue
                        for ui,uorder in enumerate(spec['orientations']['use']):
                            use=dict(zip(uorder,u['raw']))
                            if use['flower']!=flower:continue
                            values={'head':head,'flower':flower,'induce':action,'sneeze':result}|use
                            if len(set(values.values()))!=8:continue
                            counts['linked_use_forks']+=1
                            early=[w for w in valid3 if w['end']<h['start']]
                            for ci,corder in enumerate(spec['orientations']['comparison']):
                                cp=corder.index('part');cm=corder.index('compare');cr=corder.index('reference')
                                he=[w for w in early if w['raw'][cp]==head]
                                le=[w for w in early if w['raw'][cp]==use['leaf']]
                                for hc in he:
                                    for lc in le:
                                        if hc['raw'][cm]!=lc['raw'][cm]:continue
                                        marker=hc['raw'][cm]
                                        partial=values|{'compare':marker,'anthemis':hc['raw'][cr],'olive':lc['raw'][cr]}
                                        if len(set(partial.values()))!=11:continue
                                        counts['head_leaf_comparison_links']+=1
                                        for bc in early:
                                            if bc['raw'][cm]!=marker:continue
                                            full=partial|{'branch':bc['raw'][cp],'abrotonon':bc['raw'][cr]}
                                            if len(set(full.values()))!=13:continue
                                            clauses=[bc,lc,hc,h,u,f]
                                            identities=[i for clause in clauses for i in clause['ids']]
                                            if len(set(identities))!=len(identities):continue
                                            found.append({'comparison_orientation':ci,'induce_orientation':ii,'use_orientation':ui,'values':full,'clauses':clauses})
    return {'literal_triples':len(triples),'excluded_triples':x3,'literal_fives':len(fives),'excluded_fives':x5,'stage_counts':dict(counts),'solutions':found}

def canonical(items):return sorted(json.dumps(x,sort_keys=True) for x in items)

def fixture():
    text=['bran cmp abro','leaf cmp oliv','head cmp anth','head indu snez','leaf with flor app bruise','flor indu snez']
    return [{'locus':f'f2r.{i}','groups':[{'source_group_id':f'fixture-{i}-{j}','ivtff_group_raw':w,'source_group_index':j} for j,w in enumerate(t.split(),1)]} for i,t in enumerate(text,1)]

def main():
    lock=json.loads((BASE/'PREREG_LOCK.json').read_text())
    for path,digest in lock['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    result=json.loads((BASE/'artifacts/RESULT.json').read_text());spec=json.loads((BASE/'src/MODEL.json').read_text())
    assert result['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    for key,roles in [('comparison',['part','compare','reference']),('induce',['part','induce','result']),('use',['leaf','with','flower','apply','bruise'])]:
        assert spec['orientations'][key]==[list(x) for x in itertools.permutations(roles)]
    from graph import search  # fixtures only; target calculation remains independent
    positive=fixture();expected=independent(positive,spec);produced=search(positive,spec)
    assert canonical(expected['solutions'])==canonical(produced['solutions']) and expected['solutions']
    for mutate in ('effect','comparison'):
        control=fixture()
        if mutate=='effect':control[-1]['groups'][-1]['ivtff_group_raw']='other'
        else:control[0]['groups'][1]['ivtff_group_raw']='other'
        assert independent(control,spec)['solutions']==[]
        assert search(control,spec)['solutions']==[]
    raw=list(csv.DictReader(io.StringIO(gzip.decompress(SOURCE.read_bytes()).decode()),delimiter='\t'))
    groups=defaultdict(list)
    for r in raw:
        if r['section']=='Herbal':
            assert r['kind']=='P' and not r['page'].startswith('f84') and r['page']!='f116v'
            groups[(r['edition'],r['page'],r['locus'])].append(r)
    pages=defaultdict(list)
    for (edition,page,locus),rows in groups.items():
        assert [int(r['source_group_index']) for r in rows]==list(range(1,len(rows)+1))
        assert all(int(r['source_group_count'])==len(rows) for r in rows)
        pages[(edition,page)].append({'locus':locus,'groups':rows})
    cases=json.loads((BASE/'artifacts/CASES.json').read_text())
    witnesses=json.loads(gzip.decompress((BASE/'artifacts/WITNESSES.json.gz').read_bytes()))
    by={(r['edition'],r['page']):r for r in cases}
    assert set(by)==set(pages) and len(by)==len(cases)==result['all_page_reader_cases']
    total=[];stage=Counter()
    for key,lines in sorted(pages.items()):
        recomputed=independent(lines,spec);case=by[key]
        for k in ('literal_triples','excluded_triples','literal_fives','excluded_fives','stage_counts'):assert case[k]==recomputed[k],(key,k)
        assert case['source_groups']==sum(len(x['groups']) for x in lines)
        assert case['full_lines']==len(lines)
        assert case['full_bindings']==len(recomputed['solutions'])
        assert case['status']==('C0_GRAPH_BINDING' if recomputed['solutions'] else 'NO_FIXED_REALIZATION_GRAPH')
        stage.update(recomputed['stage_counts'])
        total.extend({'edition':key[0],'page':key[1],**s} for s in recomputed['solutions'])
    assert canonical(total)==canonical(witnesses)
    assert len(total)==result['full_bindings']
    assert {k:stage.get(k,0) for k in ('induce_forks','linked_use_forks','head_leaf_comparison_links')}==result['stage_counts']
    assert result['source_groups']==sum(c['source_groups'] for c in cases)
    assert result['confirmed_words']==result['independent_meaning_confirmation_leaves']==0 and result['reserved_pages_opened']==[]
    columns=['candidate','edition','page','comparison_orientation','induce_orientation','use_orientation',*spec['atom_roles']]
    table=list(csv.DictReader((BASE/'artifacts/CANDIDATE_TABLE.tsv').open(),delimiter='\t'))
    assert len(table)==len(witnesses)
    for i,(row,w) in enumerate(zip(table,witnesses)):
        expected={'candidate':str(i),'edition':w['edition'],'page':w['page'],**{k:str(w[k]) for k in columns[3:6]},**w['values']}
        assert row==expected
    output={'status':'PASS_INDEPENDENT_FULL_GRAPH_ENUMERATION','page_reader_cases':len(cases),'source_groups':result['source_groups'],
        'full_bindings_checked':len(total),'positive_and_negative_fixtures':3,'independent_meaning_confirmation':False}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))

if __name__=='__main__':main()
