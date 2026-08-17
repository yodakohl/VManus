#!/usr/bin/env python3
"""Build a source-native family-similarity atlas for existing q13 visual units."""
from __future__ import annotations
import csv, hashlib, itertools, json, re
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ANN=ROOT/'experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv'
FAM=ROOT/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,data):
    with Path(path).open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(data[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(data)
def lcp(a,b):
    n=0
    for x,y in zip(a,b):
        if x!=y:break
        n+=1
    return n
def lev(a,b):
    d=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        nd=[i]
        for j,y in enumerate(b,1):nd.append(min(nd[-1]+1,d[j]+1,d[j-1]+(x!=y)))
        d=nd
    return d[-1]

def main():
    annotations=[]
    with ANN.open(encoding='utf-8') as h:
        header=h.readline().rstrip('\n').split('\t')
        for raw in h:
            if raw.startswith('f84'):continue
            page=raw.split('\t',1)[0]
            if not re.fullmatch(r'f(?:7[5-9]|8[0-3])[rv]',page):continue
            vals=next(csv.reader([raw],delimiter='\t')); row=dict(zip(header,vals))
            if 'LABEL' in row['object_tags'].split(';'):annotations.append(row)
    assert all(not r['page'].startswith('f84') for r in annotations)
    whitelist={r['locus'] for r in annotations}
    families=defaultdict(list)
    with FAM.open(encoding='utf-8') as h:
        header=h.readline().rstrip('\n').split('\t'); li=header.index('locus')
        for raw in h:
            parts=raw.rstrip('\n').split('\t'); locus=parts[li]
            if locus not in whitelist:continue
            row=dict(zip(header,parts)); families[locus].append(row)
    for locus in families:families[locus].sort(key=lambda r:int(r['consensus_group_index']))
    def expr(locus):return '|'.join(r['family_surface'] for r in families.get(locus,[]))
    units=defaultdict(list)
    for r in annotations:
        if expr(r['locus']):units[(r['page'],r['unit'],r['unit_description'])].append(r)
    pairs=[]
    for (page,unit,desc),rr in sorted(units.items()):
        if len(rr)<2:continue
        for a,b in itertools.combinations(rr,2):
            x,y=expr(a['locus']),expr(b['locus']); distance=lev(x,y)
            pairs.append({
                'page':page,'unit':unit,'unit_description':desc,'locus_a':a['locus'],'locus_b':b['locus'],
                'family_expression_a':x,'family_expression_b':y,'family_length_a':len(x),'family_length_b':len(y),
                'leading_common_family_length':lcp(x,y),'trailing_common_family_length':lcp(x[::-1],y[::-1]),
                'normalized_edit_similarity':f"{1-distance/max(len(x),len(y)):.12f}",'exact_family_equal':int(x==y),
                'certainty_a':a['certainty'],'certainty_b':b['certainty'],'local_relation_a':a['local_relation_tags'],
                'local_relation_b':b['local_relation_tags'],'local_comment_a':a['local_comment'],'local_comment_b':b['local_comment'],
                'claim_state':'EXPLORATORY_VISUAL_HOMOLOG_FORMAL_SIMILARITY_NO_GLOSS',
            })
    assert len(pairs)==391
    pairs.sort(key=lambda r:(-int(r['leading_common_family_length']),-float(r['normalized_edit_similarity']),r['page'],r['locus_a'],r['locus_b']))
    write(ROOT/'gdt231_visual_homolog_pair_atlas.tsv',pairs)
    by_key={frozenset((r['locus_a'],r['locus_b'])):r for r in pairs}
    waterfall=by_key[frozenset(('f82r.35','f82r.38'))]
    pool_a=expr('f82v.3');pool_b=expr('f82v.45')
    obs=int(waterfall['leading_common_family_length'])
    same_page=[r for r in pairs if r['page']=='f82r']
    same_unit=pairs
    len_pair=sorted((len(waterfall['family_expression_a']),len(waterfall['family_expression_b'])))
    matched=[r for r in pairs if sorted((int(r['family_length_a']),int(r['family_length_b'])))==len_pair]
    tests=[]
    for name,universe in [('F82R_SAME_PAGE_UNIT_PAIRS',same_page),('ALL_Q13_SAME_UNIT_PAIRS',same_unit),('ALL_Q13_SAME_UNIT_LENGTH_MATCHED',matched)]:
        tail=sum(int(r['leading_common_family_length'])>=obs for r in universe)
        tests.append({'target':'F82R_WATERFALL_PAIR','comparison':name,'observed_common_prefix':obs,'worlds':len(universe),'inclusive_tail':tail,'descriptive_p':f"{tail/len(universe):.12f}",'postselection_status':'EXPOSED_PAIR_AND_METRIC_NO_CONFIRMATION'})
    tests.append({'target':'F82V_POOL_PAIR','comparison':'MANDATORY_COUNTEREXAMPLE','observed_common_prefix':lcp(pool_a,pool_b),'worlds':1,'inclusive_tail':1,'descriptive_p':'1','postselection_status':'DIRECT_POOL_REFERENT_DOES_NOT_REUSE_WATERFALL_PREFIX'})
    write(ROOT/'gdt231_target_tests.tsv',tests)
    counters=[
      {'counterexample':'F82V_TWO_DIRECT_POOL_LABELS','loci':'f82v.3|f82v.45','families':f'{pool_a} || {pool_b}','finding':f'leading_common={lcp(pool_a,pool_b)}','consequence':'no generic pool/water name recovered'},
      {'counterexample':'MORE_SIMILAR_NYMPH_ARRAY_PAIRS_EXIST','loci':'f75v.22|f75v.32;f80r.3|f80r.4','families':'BABBA=BABBA;AQABA=AQABA','finding':'exact family reuse in proximity/array labels','consequence':'waterfall similarity is not unique or semantically identified'},
      {'counterexample':'F82R_WATERFALL_OWNERSHIP_PROXIMITY_ONLY','loci':'f82r.35|f82r.38','families':'BACAB || BACACA','finding':'same human unit but both local relations are proximity','consequence':'shared prefix may mark array/register rather than object class'},
    ]
    write(ROOT/'gdt231_counterexamples.tsv',counters)
    result={'experiment':'GDT231_Q13_VISUAL_HOMOLOG_FAMILY_ATLAS','status':'F82R_PAIRED_WATERFALL_PREFIX_INTERESTING_EXPLORATORY_NOT_SEMANTICALLY_IDENTIFIED','label_rows':len(annotations),'family_covered_labels':sum(bool(expr(r['locus'])) for r in annotations),'multi_label_units':sum(len(v)>=2 for v in units.values()),'pair_rows':len(pairs),'waterfall_pair':{'loci':['f82r.35','f82r.38'],'families':[waterfall['family_expression_a'],waterfall['family_expression_b']],'leading_common_family_length':obs,'same_page_p':float(tests[0]['descriptive_p']),'all_same_unit_p':float(tests[1]['descriptive_p']),'length_matched_p':float(tests[2]['descriptive_p'])},'pool_counterexample':{'loci':['f82v.3','f82v.45'],'families':[pool_a,pool_b],'leading_common_family_length':lcp(pool_a,pool_b)},'interpretation':'The paired f82r waterfall positions share a source-native family prefix and remain a local apparatus-class lead; same-unit reuse and the pool counterexample prevent a water/flow gloss.','claim_ceiling':'One exposed same-folio visual-homolog family-prefix lead; no object name, water, flow, waterfall, word, morpheme, sound, language, plaintext, or translation.','f84':{'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{str(ANN.relative_to(ROOT)):sha(ANN),str(FAM.relative_to(ROOT)):sha(FAM)},'outputs':{},'documents':{},'implementation':{}}
    for n in ('gdt231_visual_homolog_pair_atlas.tsv','gdt231_target_tests.tsv','gdt231_counterexamples.tsv'):result['outputs'][n]=sha(ROOT/n)
    for n in ('GDT231_Q13_VISUAL_HOMOLOG_FAMILY_ATLAS_METHOD.md','GDT231_Q13_VISUAL_HOMOLOG_FAMILY_ATLAS_REPORT.md'):
        if (ROOT/n).exists():result['documents'][n]=sha(ROOT/n)
    result['implementation'][Path(__file__).name]=sha(Path(__file__))
    result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    (ROOT/'gdt231_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'labels':result['label_rows'],'pairs':result['pair_rows'],'waterfall':result['waterfall_pair'],'pool':result['pool_counterexample']},sort_keys=True))
if __name__=='__main__':main()
