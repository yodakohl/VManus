"""Independent ordered-window census over saved candidate lines."""
import collections,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def read(n):return json.loads((E/'artifacts'/n).read_text())
s=json.loads((E/'src/SPEC.json').read_text());rows=read('CANDIDATE_LINES.json');hits=read('HITS.json');tables=read('TABLES.json');shared=read('SHARED_CONTEXTS.json');result=read('RESULT.json')
assert len({r['source_group_id'] for r in rows})==len(rows)
lines=collections.defaultdict(list)
for row in rows:
 assert row['page'] in s['allowed_selectors'] and not row['page'].startswith('f84');lines[row['edition'],row['locus']].append(row)
expected={}
for (ed,locus),line in lines.items():
 line.sort(key=lambda x:int(x['source_group_index']))
 for j,x in enumerate(line):
  n=1 if x['ivtff_group_raw']=='qolchedy' else 0
  if x['ivtff_group_raw']=='qol' and j+1<len(line):
   y=line[j+1]
   if y['ivtff_group_raw']=='chedy' and int(y['source_group_index'])==int(x['source_group_index'])+1 and x['right_separator']==y['left_separator']=='DEFINITE_SPACE':n=2
  if n:
   start=int(x['source_group_index']);expected[f'{ed}|{locus}|{start}-{start+n-1}']=line[j:j+n]
assert set(expected)=={h['occurrence_id'] for h in hits} and len(expected)==len(hits)
freq=collections.Counter();strata=collections.Counter();missing=collections.Counter();ctx=collections.defaultdict(lambda:collections.defaultdict(list))
for h in hits:
 assert h['target']==expected[h['occurrence_id']];t=h['target'];ed=h['edition'];surface=h['surface'];assert surface==('JOINED' if len(t)==1 else 'SPLIT')
 lookup={int(x['source_group_index']):x for x in lines[ed,h['locus']]};start=int(t[0]['source_group_index']);end=int(t[-1]['source_group_index'])
 assert h['left']==[lookup.get(start-2),lookup.get(start-1)] and h['right']==[lookup.get(end+1),lookup.get(end+2)]
 strata[ed,surface,t[0]['section'],t[0]['hand']]+=1
 for edge,pos in [('L2',start-2),('L1',start-1),('R1',end+1),('R2',end+2)]:
  if pos not in lookup:
   reason='LINE_EDGE' if pos<1 or pos>int(t[0]['source_group_count']) else 'MISSING_INDEX';assert h['missing'][edge]==reason;missing[ed,surface,edge,reason]+=1
 for side,x,y in [('LEFT',h['left'][-1],t[0]),('RIGHT',t[-1],h['right'][0])]:
  definite=x is not None and y is not None and x['right_separator']==y['left_separator']=='DEFINITE_SPACE'
  assert h['strict'][side]==definite
  neighbor=x if side=='LEFT' else y
  if neighbor is not None:
   freq[ed,surface,side,neighbor['ivtff_group_raw'],definite]+=1
   if definite:ctx[ed,side,(neighbor['ivtff_group_raw'],)][surface].append(h['occurrence_id'])
 chain=h['left']+t+h['right'];four=all(x is not None for x in chain) and all(x['right_separator']==y['left_separator']=='DEFINITE_SPACE' for x,y in zip(chain,chain[1:]));assert four==h['strict']['FOUR']
 if four:ctx[ed,'FOUR',tuple(x['ivtff_group_raw'] for x in h['left']+h['right'])][surface].append(h['occurrence_id'])
assert freq==collections.Counter({(x['edition'],x['surface'],x['side'],x['neighbor'],x['definite_boundary']):x['n'] for x in tables['immediate_frequencies']})
assert strata==collections.Counter({(x['edition'],x['surface'],x['section'],x['hand']):x['n'] for x in tables['section_hand']})
assert missing==collections.Counter({(x['edition'],x['surface'],x['edge'],x['reason']):x['n'] for x in tables['missing_edges']})
expected_ctx={k:{surf:sorted(ids) for surf,ids in v.items()} for k,v in ctx.items() if set(v)=={'JOINED','SPLIT'}}
assert expected_ctx=={(x['edition'],x['side'],tuple(x['context'])):{surf:sorted(ids) for surf,ids in x['occurrences'].items()} for x in shared}
assert result['hits']==len(hits)
for ed in s['editions']:
 for surf in ['JOINED','SPLIT']:assert result['counts'][ed][surf]==sum(h['edition']==ed and h['surface']==surf for h in hits)
 for side in ['LEFT','RIGHT','FOUR']:assert result['shared_contexts'][ed][side]==sum(k[0]==ed and k[1]==side for k in expected_ctx)
(E/'artifacts/VALIDATION.json').write_text(json.dumps(dict(status='PASS_INDEPENDENT_SAVED_LINE_WINDOWS_AND_CONTEXT_COUNTS',hits=len(hits),semantic_validation=False,scope='Saved candidate-line completeness and aggregation; query projection hash records original full guarded source selection.'),indent=2)+'\n');print('PASS')
