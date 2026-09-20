import collections,itertools
from common import *
s=read(E/'src/SPEC.json');g=read(R/s['grammar']);packet=read(R/s['source_packet']);panel=[]
counts={k:1+int(k=='THEN') for k in g['patterns']};N=sum(counts[k]*len(v) for k,v in g['patterns'].items())
for ed,source in packet['readers'].items():
    words=[x['ivtff_group_raw'] for row in source['rows'] for x in row['groups']]
    panel.append(dict(edition=ed,page='f83r',leaf=83,words=words,source_ids=[x['source_group_id'] for row in source['rows'] for x in row['groups']],groups=len(words),whole_paragraph_contract=source['whole_paragraph_contract'],strict_anchor_eligible=source['strict_anchor_eligible'],uncertain_groups=source['uncertain_groups'],status='UNKNOWN_PARAGRAPH_CONTRACT' if not source['whole_paragraph_contract'] else 'CONTRADICTED_COMPLETE_CONTENT_COUNT' if len(words)!=N else 'SEARCH_CONDITIONALLY_SOURCE_UNCERTAIN' if not source['strict_anchor_eligible'] else 'SEARCH_LITERAL'))
raw=next(p['words'] for p in panel if p['edition']=='ZL3b');freq=collections.Counter(raw);projection=sorted({w for w,n in freq.items() if n>1}|set(s['inherited_hypothesis_forms']))
put('PANEL.json',panel);put('PREDICTIONS.json',dict(source_groups=N,pattern_counts=counts,whole_word_value_inventory=sorted({v for pat in g['patterns'].values() for t in pat for v in (g['types'][t[1:]] if t.startswith('@') else [t])}),projection_words=projection,projection_basis={w:dict(occurrences=freq[w],inherited=w in s['inherited_hypothesis_forms']) for w in projection},families=s['families'],source_world_requirements=s['source_world_requirements'],all_variants=[dict(zip(g['variants'],v)) for v in itertools.product(*g['variants'].values())],unbound_mapping='ALL_WORD_VALUES_FREE_IN_BOTH_SEARCHES',independent_meaning_capacity=0))
print(dict(readers=[(p['edition'],p['groups'],p['status']) for p in panel],projection_words=projection))
