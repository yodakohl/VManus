#!/usr/bin/env python3
from pathlib import Path
from itertools import permutations
from datetime import datetime,timezone
import hashlib,importlib.util,json
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
P=ROOT/'research_registry/proposals/production_origin_supply_20261003'
def main():
 started=datetime.now(timezone.utc).isoformat()
 for rel,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
 spec=importlib.util.spec_from_file_location('frozen_word_grammar',P/'B6_7_PRODUCTIVE_STEMS.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 def accepted(gs):
  options=[gs]
  if gs[0]=='m':options.append(gs[1:])
  for option in options:
   try:m.read_word(''.join(option))
   except (ValueError,KeyError,IndexError,TypeError):continue
   return True
  return False
 grid=[]
 for a,b in permutations(m.GLYPHS,2):
  base=accepted([a,b]);double=accepted([a,b,a,b])
  grid.append({'A':a,'B':b,'base_readable':base,'double_readable':double,'both_readable':base and double})
 prior=json.loads((P/'PAIRED_PIECE_GLOBAL_UD_RESULT_20261005.json').read_text());binding=[]
 assert {w['edition'] for w in prior['witnesses']}=={'ZL3b','IT2a','RF1b'}
 for w in prior['witnesses']:
  assert w['base']['ivtff_group_raw']=='ol' and w['double']['ivtff_group_raw']=='olol'
  for name in ('base','double'):
   row=w[name];assert row['left_separator'] in ('DEFINITE_SPACE','LINE_START') and row['right_separator'] in ('DEFINITE_SPACE','LINE_END')
  binding.append({'edition':w['edition'],'base_id':w['base']['source_group_id'],'double_id':w['double']['source_group_id'],'base':'ol','double':'olol'})
 result={'experiment':'GDT1214','status':'NO_SHORT_SQUARE_GRAMMAR_RENAMING' if not any(x['both_readable'] for x in grid) else 'SHORT_SQUARE_GRAMMAR_RENAMING_NOT_EXCLUDED','ordered_pairs':len(grid),'base_readable_pairs':sum(x['base_readable'] for x in grid),'double_readable_pairs':sum(x['double_readable'] for x in grid),'joint_readable_pairs':sum(x['both_readable'] for x in grid),'binding':binding,'grid':grid,'claim_ceiling':'Fixed old grammar and bijective22-working-sign mapping with preserved whole-group boundaries only; no native atoms, meanings, all semantic grammars or redesigned root formats excluded.'}
 (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 (A/'RUN_RECEIPT.json').write_text(json.dumps({'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('grid','binding')},indent=2))
if __name__=='__main__':main()
