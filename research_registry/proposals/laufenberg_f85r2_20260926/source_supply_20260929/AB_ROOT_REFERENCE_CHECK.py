#!/usr/bin/env python3
"""Independent finite replay of owned source counts/reference positions only."""
import collections, hashlib, json
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'vmanus-work').is_file())
P=ROOT/'experiments/yolo/gdt943_solkain_second_leaf_complete_clause/artifacts'
source=json.loads((P/'CONTEXT_SOURCE_LINES.json').read_text())
lex=json.loads((P/'LEXICONS.json').read_text())
old=set(next(iter(lex.values())))
assert len(old)==41 and all(set(v)==old for v in lex.values())
new={'keey','qoty','dalched','qokair','dalom'}
assert not old & new
counts=collections.Counter(); bins=collections.Counter(); units=collections.defaultdict(list)
for line in source:
    for raw in line['groups']:
        g=dict(zip(line['columns'],raw)); units[g['edition'],g['page']].append(g)
        w=g['ivtff_group_raw'];bins['inherited' if w in old else 'new' if w in new else 'unknown']+=1
        if w in new:counts[g['edition'],w]+=1
refs=[]
for (edition,page),groups in units.items():
    for i,g in enumerate(groups):
        if g['ivtff_group_raw']!='keey':continue
        preceding=[j for j in range(i) if groups[j]['ivtff_group_raw']=='qokeedy']
        j=max(preceding) if preceding else None
        interval=groups[j+1:i] if j is not None else None
        refs.append({'target':g['source_group_id'],'prior_exact_source':groups[j]['source_group_id'] if j is not None else None,
                     'left_separator':g['left_separator'],'right_separator':g['right_separator'],
                     'paragraph_basis':'RF_WINDOW_CONDITIONAL' if edition=='RF1b' else 'OWNED_COMPLETE_PARAGRAPH',
                     'all_prior_exact_sources':[groups[k]['source_group_id'] for k in preceding],
                     'intervening_groups':len(interval) if interval is not None else None,
                     'intervening_unassigned':sum(x['ivtff_group_raw'] not in old|new for x in interval) if interval is not None else None,
                     'intervening_source_ids':[x['source_group_id'] for x in interval] if interval is not None else None})
assert len(source)==140 and sum(bins.values())==1553 and sum(counts.values())==17 and len(refs)==4
assert bins=={'inherited':394,'new':17,'unknown':1142}
assert (BASE/'AB_CONTEXT_SOURCE_LINES.json').read_bytes()==(P/'CONTEXT_SOURCE_LINES.json').read_bytes()
assert (BASE/'AB_CONTEXT_PARAGRAPHS.json').read_bytes()==(P/'CONTEXT_PARAGRAPHS.json').read_bytes()
assert (BASE/'AB_INHERITED_LEXICONS.json').read_bytes()==(P/'LEXICONS.json').read_bytes()
# All ZL/IT page windows used here are their one existing whole paragraph.
paragraphs=json.loads((P/'CONTEXT_PARAGRAPHS.json').read_text())
assert len({(x['edition'],x['page']) for x in paragraphs})==len(paragraphs)==6
out={'status':'SOURCE_ACCOUNT_REPLAY_PASS_NOT_MEANING_TEST','source_hash':hashlib.sha256((P/'CONTEXT_SOURCE_LINES.json').read_bytes()).hexdigest(),
     'source_lines':len(source),'groups':sum(bins.values()),'value_status_counts':dict(bins),
     'five_word_counts':[{'edition':e,'word':w,'count':v} for (e,w),v in sorted(counts.items())],
     'references':refs,'coverage':'Exact owned inputs, literal counts and conditional latest-source consequences. No semantic or paragraph-boundary validation.'}
(BASE/'AB_ROOT_REFERENCE_ACCOUNT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':out['status'],'groups':out['groups'],'references':[{k:v for k,v in x.items() if k not in ['intervening_source_ids','all_prior_exact_sources']} for x in refs]},ensure_ascii=False,indent=2))
