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
import multiprocessing

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
SOURCE=ROOT/'experiments/yolo/gdt1106_frozen_domain_transfer/artifacts/SOURCE.tsv.gz'

def extract(lines,n):
    kept=[];lost=0
    for line in lines:
        suffix=line['locus'].split('.')
        for chunk in line['chunks']:
            units=chunk['units']
            if units is None:lost+=1;continue
            if len(units)!=n:continue
            if len(suffix)!=2 or not suffix[1].isdigit():lost+=1;continue
            kept.append({'raw':units,'ids':chunk['ids'],
                'start':[int(suffix[1]),chunk['start_index']],
                'end':[int(suffix[1]),chunk['end_index']], 'locus':line['locus'],
                'raw_groups':chunk['raw_groups']})
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
    return [{'locus':f'f2r.{i}','chunks':[{'ids':[f'fixture-{i}'],'raw_groups':['synthetic'],
        'units':t.split(),'start_index':1,'end_index':1}]} for i,t in enumerate(text,1)]

def raw_pages():
    # Separate implementation of the fixed ordered collapse/merge transform.
    merge_rows=list(csv.DictReader((ROOT/'experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv').open(),delimiter='\t'))
    assert [int(r['rank']) for r in merge_rows]==list(range(1,65))
    def tokenize(raw):
        for old,new in [('cth','T'),('ckh','K'),('cph','P'),('cfh','F'),('ch','C'),('sh','S'),('iin','N'),('in','I'),('ee','E')]:raw=raw.replace(old,new)
        symbols=list(raw)
        for merge in merge_rows:
            output=[];i=0
            while i<len(symbols):
                if i+1<len(symbols) and symbols[i]==merge['left'] and symbols[i+1]==merge['right']:
                    output.append(merge['merged']);i+=2
                else:output.append(symbols[i]);i+=1
            symbols=output
        assert ''.join(symbols)==raw
        return symbols
    raw=list(csv.DictReader(io.StringIO(gzip.decompress(SOURCE.read_bytes()).decode()),delimiter='\t'))
    groups=defaultdict(list)
    for r in raw:
        if r['section']=='H':
            assert r['kind']=='P' and not r['page'].startswith('f84') and r['page']!='f116v'
            groups[(r['edition'],r['page'],r['locus'])].append(r)
    pages=defaultdict(list)
    for (edition,page,locus),rows in sorted(groups.items()):
        assert [int(r['source_group_index']) for r in rows]==list(range(1,len(rows)+1))
        assert all(int(r['source_group_count'])==len(rows) for r in rows)
        chunks=[];left=0
        for right,row in enumerate(rows):
            if row['right_separator']=='UNCERTAIN_SMALL_SPACE':continue
            current=rows[left:right+1]
            unknown=any(re.fullmatch('[a-z]+',r['ivtff_group_raw']) is None for r in current)
            units=None if unknown else tokenize(''.join(r['ivtff_group_raw'] for r in current))
            chunks.append({'ids':[r['source_group_id'] for r in current],
                'raw_groups':[r['ivtff_group_raw'] for r in current],
                'start_index':left+1,'end_index':right+1,'units':units,'source_rows':current})
            left=right+1
        assert left==len(rows)
        pages[(edition,page)].append({'locus':locus,'chunks':chunks,'source_group_count':len(rows)})
    return pages

def check_case(task):
    key,lines,spec=task
    return key,independent(lines,spec)

def main():
    for filename in ('PREREG_LOCK.json','IMPLEMENTATION_LOCK.json'):
        for path,digest in json.loads((BASE/filename).read_text())['sha256'].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    result=json.loads((BASE/'artifacts/RESULT.json').read_text());spec=json.loads((BASE/'src/MODEL.json').read_text())
    for key,roles in [('comparison',['part','compare','reference']),('induce',['part','induce','result']),('use',['leaf','with','flower','apply','bruise'])]:
        assert spec['orientations'][key]==[list(x) for x in itertools.permutations(roles)]
    from graph import search  # fixtures only, never used to recompute target graphs
    positive=fixture();expected=independent(positive,spec);produced=search(positive,spec)
    assert canonical(expected['solutions'])==canonical(produced['solutions']) and expected['solutions']
    for mutate in ('effect','comparison'):
        control=fixture()
        if mutate=='effect':control[-1]['chunks'][0]['units'][-1]='other'
        else:control[0]['chunks'][0]['units'][1]='other'
        assert independent(control,spec)['solutions']==[] and search(control,spec)['solutions']==[]
    pages=raw_pages();assert len(pages)==357
    carriers=json.loads(gzip.decompress((BASE/'artifacts/CARRIERS.json.gz').read_bytes()))
    assert carriers==[{'edition':ed,'page':page,'lines':ls} for (ed,page),ls in sorted(pages.items())]
    cases=json.loads((BASE/'artifacts/CASES.json').read_text());by={(c['edition'],c['page']):c for c in cases}
    assert set(by)==set(pages) and len(by)==len(cases)==357
    total=[];stage=Counter()
    with multiprocessing.Pool(8) as pool:
        for key,recomputed in pool.imap(check_case,[(key,ls,spec) for key,ls in sorted(pages.items())]):
            case=by[key];lines=pages[key]
            assert case['three_unit_carriers']==recomputed['literal_triples']
            assert case['five_unit_carriers']==recomputed['literal_fives']
            assert case['stage_counts']==recomputed['stage_counts'],key
            assert case['source_groups']==sum(l['source_group_count'] for l in lines)
            assert case['full_lines']==len(lines)
            assert case['hard_chunks']==sum(len(l['chunks']) for l in lines)
            assert case['unknown_chunks']==sum(c['units'] is None for l in lines for c in l['chunks'])
            assert case['full_bindings']==len(recomputed['solutions'])
            stage.update(recomputed['stage_counts'])
            total.extend({'edition':key[0],'page':key[1],**s} for s in recomputed['solutions'])
    witnesses=json.loads(gzip.decompress((BASE/'artifacts/WITNESSES.json.gz').read_bytes()))
    assert canonical(total)==canonical(witnesses) and len(total)==result['full_bindings']
    for metric in ('source_groups','hard_chunks','unknown_chunks','three_unit_carriers','five_unit_carriers'):assert sum(c[metric] for c in cases)==result[metric]
    assert result['all_page_reader_cases']==357 and result['source_groups']==32000 and result['contracts']==4320
    assert {k:stage.get(k,0) for k in ('induce_forks','linked_use_forks','head_leaf_comparison_links')}==result['stage_counts']
    assert result['status']==('C0_UNIT_GRAPH_BINDINGS_RETAINED' if total else 'NO_FIXED_COMPLETE_CHUNK_UNIT_GRAPH')
    assert result['confirmed_words']==result['independent_meaning_confirmation_leaves']==0 and result['reserved_pages_opened']==[]
    assert result['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    table=list(csv.DictReader((BASE/'artifacts/CANDIDATE_TABLE.tsv').open(),delimiter='\t'))
    assert len(table)==len(witnesses)
    columns=['candidate','edition','page','comparison_orientation','induce_orientation','use_orientation',*spec['atom_roles']]
    for i,(row,w) in enumerate(zip(table,witnesses)):
        assert row=={'candidate':str(i),'edition':w['edition'],'page':w['page'],**{k:str(w[k]) for k in columns[3:6]},**w['values']}
    contract=list(csv.DictReader((BASE/'artifacts/CONTRACT_TABLE.tsv').open(),delimiter='\t'))
    assert len(contract)==4320
    counts=Counter((s['comparison_orientation'],s['induce_orientation'],s['use_orientation']) for s in total)
    for row,(c,i,u) in zip(contract,itertools.product(range(6),range(6),range(120))):assert row=={'comparison':str(c),'induce':str(i),'use':str(u),'full_bindings':str(counts[c,i,u])}
    output={'status':'PASS_INDEPENDENT_FULL_GRAPH_AND_PARSER_RECONSTRUCTION','page_reader_cases':357,'source_groups':32000,'hard_chunks_checked':len([c for ls in pages.values() for l in ls for c in l['chunks']]),'full_bindings_checked':len(total),'positive_and_negative_fixtures':3,'independent_meaning_confirmation':False}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
if __name__=='__main__':main()
