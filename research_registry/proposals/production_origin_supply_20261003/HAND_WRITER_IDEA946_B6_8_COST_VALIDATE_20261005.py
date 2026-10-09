#!/usr/bin/env python3
"""Bind the raw first-use cost to the complete old source; no new writer run."""
from pathlib import Path
from collections import Counter
import json,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[2];P='HAND_WRITER_IDEA946_B6_8_COST'
def main():
 lock=json.loads((D/(P+'_INPUTS_20261005.json')).read_text())
 for rel,h in lock['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
 old=ROOT/'experiments/yolo/gdt1175_fixed_writer_b6_8_transfer/artifacts'
 account=json.loads((old/'SOURCE_ACCOUNT.json').read_text());prior=json.loads((old/'RESULT.json').read_text())
 occurrences=[]
 def visit(t,clause):
  name,kids=t
  if name.startswith('LIT:') or name.startswith('QUOTE'):
   value=name.split(':',1)[1];assert value and all('a'<=c<='z' for c in value)
   # a..s one working sign; t..z two. Old literal framing two;
   # QUOTE has two additional explicit predicate/arity signs.
   cost=sum(1 if c<='s' else 2 for c in value)+2+(2 if name.startswith('QUOTE') else 0)
   occurrences.append({'clause':clause,'name':name,'glyphs':cost})
  for kid in kids:visit(kid,clause)
 for clause in account['clauses']:visit(clause['tree'],clause['id'])
 assert occurrences==prior['literal_occurrences']
 names=[r['name'].split(':',1)[1] for r in occurrences];counts=Counter(names)
 assert len(names)==16 and len(counts)==16
 old_channel=sum(x['glyphs'] for x in occurrences);assert old_channel==prior['literal_glyphs']==175
 old_total=prior['glyphs'];assert old_total==278
 # All first uses. Pointer choice, slot count, and traversal reordering cannot
 # produce a hit when no exact name occurs twice.
 extra=3*len(names);new_channel=old_channel+extra;new_total=old_total+extra
 result={'status':'NO_LITERAL_NAME_REUSE_IN_FIXED_B6_8','source_clauses':len(account['clauses']),'name_occurrences':occurrences,'distinct_names':len(counts),'hits_possible_with_any_number_of_initially_empty_slots':0,'old_open_channel_glyphs':old_channel,'old_total_glyphs':old_total,'extra_definition_glyphs':extra,'new_open_channel_glyphs_by_contract':new_channel,'new_total_glyphs_by_contract':new_total,'new_open_channel_fraction_by_contract':new_channel/new_total,'full_new_writer_executed':False,'claim_ceiling':'Exact first-use cost consequence on the old exposed source trees only; no carrier integration, general cache rejection, native meaning or independent confirmation.'}
 target=D/(P+'_RESULT_20261005.json')
 if target.exists():assert json.loads(target.read_text())==result
 else:target.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='name_occurrences'},indent=2))
if __name__=='__main__':main()
