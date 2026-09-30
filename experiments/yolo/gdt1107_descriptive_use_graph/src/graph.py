"""Finite whole-group clause joins, not an unknown-text decoder."""
import itertools
import re
from collections import Counter, defaultdict

LITERAL=re.compile(r'[a-z]+\Z')

def windows(lines,n):
    result=[];excluded=0
    for line in lines:
        match=re.fullmatch(r'[^.]+\.(\d+)',line['locus'])
        rows=line['groups']
        for start in range(len(rows)-n+1):
            selected=rows[start:start+n]
            if match is None or not all(LITERAL.fullmatch(r['ivtff_group_raw']) for r in selected):
                excluded+=1;continue
            result.append({'raw':[r['ivtff_group_raw'] for r in selected],
                'ids':[r['source_group_id'] for r in selected],
                'start':[int(match[1]),int(selected[0]['source_group_index'])],
                'end':[int(match[1]),int(selected[-1]['source_group_index'])], 'locus':line['locus']})
    return result,excluded

def decode(window,order):
    return dict(zip(order,window['raw']))

def before(a,b):
    return a['end']<b['start']

def distinct_clauses(clauses):
    ids=[identity for c in clauses for identity in c['ids']]
    return len(ids)==len(set(ids))

def search(lines,spec):
    triples,x3=windows(lines,3);fives,x5=windows(lines,5)
    solutions=[];forks=[];use_candidates=[];counts=Counter()
    comparison_indices=[]
    for ci,order in enumerate(spec['orientations']['comparison']):
        index=defaultdict(lambda:defaultdict(list))
        for window in triples:
            value=decode(window,order)
            if len(set(value.values()))==3:index[value['compare']][value['part']].append((value,window))
        comparison_indices.append(index)
    # Index each5group clause once per possible global orientation.
    uses=defaultdict(list)
    for ui,order in enumerate(spec['orientations']['use']):
        for window in fives:
            value=decode(window,order)
            if len(set(value.values()))==5:uses[value['flower']].append((ui,value,window))
    for ii,order in enumerate(spec['orientations']['induce']):
        related=defaultdict(list)
        for window in triples:
            value=decode(window,order)
            if len(set(value.values()))==3:related[(value['induce'],value['result'])].append((value,window))
        for (action,effect),entries in related.items():
            for (head,head_clause),(flower,flower_clause) in itertools.product(entries,repeat=2):
                if head['part']==flower['part'] or not before(head_clause,flower_clause):continue
                base={'head':head['part'],'flower':flower['part'],'induce':action,'sneeze':effect}
                if len(set(base.values()))!=4:continue
                counts['induce_forks']+=1
                forks.append({'induce_orientation':ii,'values':base,'clauses':[head_clause,flower_clause]})
                for ui,use,use_clause in uses.get(flower['part'],[]):
                    if not (before(head_clause,use_clause) and before(use_clause,flower_clause)):continue
                    values=base|use
                    if len(set(values.values()))!=len(values):continue
                    counts['linked_use_forks']+=1
                    use_candidates.append({'induce_orientation':ii,'use_orientation':ui,'values':values,
                        'clauses':[head_clause,use_clause,flower_clause]})
                    for ci,index in enumerate(comparison_indices):
                        for marker,parts in index.items():
                            if values['head'] not in parts or values['leaf'] not in parts:continue
                            hs=[(v,c) for v,c in parts[values['head']] if before(c,head_clause)]
                            ls=[(v,c) for v,c in parts[values['leaf']] if before(c,head_clause)]
                            for (hv,hc),(lv,lc) in itertools.product(hs,ls):
                                partial=values|{'compare':marker,'anthemis':hv['reference'],'olive':lv['reference']}
                                if len(set(partial.values()))!=len(partial):continue
                                counts['head_leaf_comparison_links']+=1
                                for branch,entries2 in parts.items():
                                    for bv,bc in entries2:
                                        if not before(bc,head_clause):continue
                                        full=partial|{'branch':branch,'abrotonon':bv['reference']}
                                        if len(full)!=13 or len(set(full.values()))!=13:continue
                                        clauses=[bc,lc,hc,head_clause,use_clause,flower_clause]
                                        if not distinct_clauses(clauses):continue
                                        solutions.append({'comparison_orientation':ci,'induce_orientation':ii,'use_orientation':ui,
                                            'values':full,'clauses':clauses})
    return {'literal_triples':len(triples),'excluded_triples':x3,'literal_fives':len(fives),'excluded_fives':x5,
        'stage_counts':dict(counts),'solutions':solutions,'induce_forks':forks,'linked_use_forks':use_candidates}
