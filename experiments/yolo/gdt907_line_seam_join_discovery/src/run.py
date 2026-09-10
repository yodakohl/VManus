#!/usr/bin/env python3
import argparse, collections, hashlib, json, random, re
from fractions import Fraction
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def plain(x): return re.fullmatch('[a-z]+',x) is not None
def leaf(p): return re.match(r'f\d+',p)[0]
def extract(raw,spec,ed):
    src=json.loads(raw); by=collections.defaultdict(dict); vocab=collections.defaultdict(list)
    for item in src['lines']:
        m=item['metadata']; assert m['page'] in spec['allowed_selectors'] and not m['page'].startswith('f84') and m['edition']==ed
        groups=[dict(zip(src['group_columns'],g)) for g in item['groups']]
        if m['kind']!='P': continue
        match=re.fullmatch(re.escape(m['page'])+r'\.(\d+)',m['locus'])
        if not match or len(groups)!=int(m['source_group_count']) or [int(g['source_group_index']) for g in groups]!=list(range(1,len(groups)+1)): continue
        num=int(match[1]); assert num not in by[m['page']]; by[m['page']][num]=(m,groups)
        for g in groups:
            w=g['ivtff_group_raw']
            if plain(w): vocab[w].append([m['page'],m['locus'],g['source_group_id']])
    seams=[]
    for page, lines in sorted(by.items()):
        run=None; previous=None
        for num,(m,gs) in sorted(lines.items()):
            linked=False
            if previous is not None:
                pnum,pm,pg=previous
                linked=(num==pnum+1 and pm['paragraph_end']=='0' and m['paragraph_start']=='0' and pm['hand']==m['hand'] and pm['section']==m['section'] and m['code'] in ['+P0','+P1'])
            if not linked: run=num
            if linked:
                a=pg[-1]; b=gs[0]
                if plain(a['ivtff_group_raw']) and plain(b['ivtff_group_raw']):
                    seams.append(dict(id=pm['locus']+'>'+m['locus'],page=page,leaf=leaf(page),run_start=run,left_locus=pm['locus'],right_locus=m['locus'],A=a['ivtff_group_raw'],B=b['ivtff_group_raw'],left_id=a['source_group_id'],right_id=b['source_group_id'],left_code=pm['code'],right_code=m['code']))
            previous=(num,m,gs)
    return seams,vocab

def calculate(seams,vocab,spec,rng):
    strata=collections.defaultdict(list)
    for i,x in enumerate(seams): strata[(x['page'],x['run_start'],len(x['B']))].append(i)
    wholes={w:{leaf(x[0]) for x in vv} for w,vv in vocab.items()}
    matrices=[]; expected=Fraction(); expected_long=Fraction(); observed=0; observed_long=0; exchangeable_leaves=set(); hitwords=set(); hits=[]
    null=[0]*spec['randomizations']
    for key,ii in sorted(strata.items()):
        n=len(ii); matrix=[[int(bool(wholes.get(seams[i]['A']+seams[j]['B'],set())-{seams[i]['leaf']})) for j in ii] for i in ii]
        counts=[sum(row) for row in matrix]; diag=sum(matrix[k][k] for k in range(n)); ex=Fraction(sum(counts),n)
        longrows=[k for k,i in enumerate(ii) if len(seams[i]['A'])>=2 and len(seams[i]['B'])>=2]
        observed+=diag;expected+=ex;observed_long+=sum(matrix[k][k] for k in longrows);expected_long+=Fraction(sum(counts[k] for k in longrows),n)
        if n>1: exchangeable_leaves.add(seams[ii[0]]['leaf'])
        matrices.append(dict(key=list(key),seam_indices=ii,bits=[''.join(map(str,row)) for row in matrix],observed=diag,expected=[ex.numerator,ex.denominator]))
        for k,i in enumerate(ii):
            if matrix[k][k]:
                w=seams[i]['A']+seams[i]['B'];hitwords.add(w);hits.append(dict(seam_index=i,whole=w,external_witnesses=[v for v in vocab[w] if leaf(v[0])!=seams[i]['leaf']]))
        order=list(range(n))
        for r in range(len(null)):
            order=list(range(n));rng.shuffle(order);null[r]+=sum(matrix[k][order[k]] for k in range(n))
    p=(1+sum(v>=observed for v in null))/(1+len(null))
    result=dict(eligible_seams=len(seams),physical_leaves=len({x['leaf'] for x in seams}),strata=len(matrices),exchangeable_strata=sum(len(m['seam_indices'])>1 for m in matrices),exchangeable_leaves=len(exchangeable_leaves),observed=observed,expected_fraction=[expected.numerator,expected.denominator],expected=float(expected),excess=float(observed-expected),null_upper_tail=p,null_min=min(null),null_max=max(null),distinct_hit_wholes=len(hitwords),hit_leaves=len({seams[h['seam_index']]['leaf'] for h in hits}),both_fragments_at_least_two=dict(observed=observed_long,expected=float(expected_long),expected_fraction=[expected_long.numerator,expected_long.denominator]),status='EXPLORATORY_SEAM_CENSUS_NO_HYPHENATION_OR_MEANING_IDENTIFICATION')
    return dict(seams=seams,matrices=matrices,hits=hits,null_scores=null,result=result)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();s=json.loads((E/'src/SPEC.json').read_text());rng=random.Random(s['seed']);out={};hs={}
    for ed,v in s['sources'].items():
        raw=(ROOT/v['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==v['sha256'];seams,vocab=extract(raw,s,ed);data=calculate(seams,vocab,s,rng);out[ed]=data['result'];hs[ed]={data['seams'][h['seam_index']]['id']:(data['seams'][h['seam_index']]['A'],data['seams'][h['seam_index']]['B']) for h in data['hits']}
        p=E/'artifacts'/f'{ed}.json'
        if args.check: assert p.read_text()==enc(data)
        else: p.write_text(enc(data))
    common=set.intersection(*(set(x) for x in hs.values()));same=[k for k in sorted(common) if len({v[k] for v in hs.values()})==1]
    result=dict(readings=out,all_three_hit_locus_pairs=sorted(common),all_three_same_fragment_pairs=same,claim_ceiling='Exploratory literal string relation; neither hyphenation nor semantics established.')
    p=E/'artifacts/RESULT.json'
    if args.check: assert p.read_text()==enc(result)
    else: p.write_text(enc(result))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
