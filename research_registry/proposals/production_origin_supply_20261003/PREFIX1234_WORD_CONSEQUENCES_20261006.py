"""Post-result descriptive consequence, not a new model fit or error filter."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import json,gzip,hashlib
P=Path('research_registry/proposals/production_origin_supply_20261003');D=Path('experiments/yolo/gdt1234_prefix_quotient_code_capacity');spec=json.loads((D/'src/SPEC.json').read_text());groups=json.loads(gzip.decompress(Path(spec['source']).read_bytes()));result=json.loads((D/'artifacts/RESULT.json').read_text());packet=json.loads((P/'HAND_WORD_EXTREMES_PACKET_20261005.json').read_text())
forms=packet['forms']; assert all(isinstance(w,str) for w in forms)
def tokens(word):
 paths=[()]
 def visit(tail,path):
  if not tail:return[path]
  return [x for g in spec['signs'] if tail.startswith(g) for x in visit(tail[len(g):],path+(g,))]
 p=visit(word,());assert len(p)==1;return p[0]
def pattern(w):
 d={};out=[]
 for g in w:
  if g not in d:d[g]=chr(65+len(d))
  out.append(d[g])
 return ''.join(out)
out={'status':'POST_RESULT_CONDITIONAL_WORD_CONSEQUENCES','created_utc':datetime.now(timezone.utc).isoformat(),'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(spec['source']),D/'artifacts/RESULT.json',P/'HAND_WORD_EXTREMES_PACKET_20261005.json']},'scope':'Same1233strict-interior groups and previously selected12manual forms. No new filter, native reading or dictionary values. Forced-singleton consequence assumes the exact1234prefix-free whole-word contract.','zero_panel_count_limit':'Zero-panel manual forms remain previous uncertain/line-edge examples, not newly admitted complete-group obligations.','readers':{}}
for reader,rows in groups.items():
 F=set(result['readers'][reader]['summary']['F']);counts=Counter(tuple(r['units']) for r in rows);forced={w:n for w,n in counts.items() if set(w)<=F};items=[]
 for raw in forms:
  w=tokens(raw);items.append({'raw':raw,'units':list(w),'selected_panel_count':counts[w],'all_signs_forced_singleton':set(w)<=F,'unforced_heads':sorted(set(w)-F),'forced_decoded_letter_count':len(w) if set(w)<=F else None,'forced_equality_pattern':pattern(w) if set(w)<=F else None,'interpretation':'Each different forced sign denotes a different abstract sourceletter under the fixed prefix-free code; letters A/B/etc label equality only, not phonetic values.'})
 out['readers'][reader]={'whole_groups':len(rows),'types':len(counts),'fully_forced_groups':sum(forced.values()),'fully_forced_types':len(forced),'fully_forced_group_fraction':sum(forced.values())/len(rows),'manual_forms':items}
# Separate simple accounting of positions: every nonforced group must contain
# at least one unit absent from F; exact complement totals must agree.
for reader,rows in groups.items():
 F=set(result['readers'][reader]['summary']['F']);bad=sum(any(g not in F for g in r['units']) for r in rows)
 assert len(rows)-bad==out['readers'][reader]['fully_forced_groups']
 for item in out['readers'][reader]['manual_forms']:
  if item['raw']=='daldy':assert item['forced_equality_pattern']=='ABCAD'
(P/'PREFIX1234_WORD_CONSEQUENCES_20261006.json').write_text(json.dumps(out,indent=2)+'\n')
for reader,r in out['readers'].items():
 print(reader,r['fully_forced_groups'],r['whole_groups'],round(100*r['fully_forced_group_fraction'],3),r['fully_forced_types'])
 print([(x['raw'],x['selected_panel_count'],x['forced_decoded_letter_count'],x['forced_equality_pattern'])for x in r['manual_forms']])
