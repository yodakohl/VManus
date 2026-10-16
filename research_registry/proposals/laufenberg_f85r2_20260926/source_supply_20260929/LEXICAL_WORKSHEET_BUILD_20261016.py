"""Finite exact-string worksheet rendering, without semantic evaluation."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
R=next(p for p in D.parents if (p/'VOYNICH_CURRENT_ROUTE.md').exists())
PLAN=D/'LEXICAL_WORKSHEET_PLAN_20261016.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 plan=json.loads(PLAN.read_text())
 for p,h in plan['inputs'].items():assert sha(R/p)==h,p
 path='research_registry/proposals/production_origin_supply_20261003/C1064_DERIVATION_20261016.json'; data=json.loads((R/path).read_text())
 rules=plan['rule']['expansions'];assert rules=={'olchedy':['ol','chedy'],'qolchedy':['qol','chedy'],'olshedy':['ol','shedy']}
 selected=[s for s in data['source_units'] if s['source_unit']['edition']=='IT2a'];assert len(selected)==2
 selected.sort(key=lambda s:0 if s['source_unit']['lines'][0]['metadata']['locus']=='f75v.43' else 1)
 forms=set()
 for s in selected:
  for line in s['source_unit']['lines']:
   for g in line['groups']:forms.update(rules.get(g[2],[g[2]]))
 atomids={f:f'U{i:03d}' for i,f in enumerate(sorted(forms),1)}
 units=[]
 for s,expected in zip(selected,[77,120]):
  u=s['source_unit']; lines=[]; occurrences=[]; rawcount=pieces=0; seen=set()
  for line in u['lines']:
   mappings=[]; expanded=[]; ids=[]
   for g in line['groups']:
    rawcount+=1; raw=g[2]; atoms=rules.get(raw,[raw]); start=pieces; parts=[]
    for j,form in enumerate(atoms):
     piece={'source_group_id':g[0],'piece_index':j,'form':form,'atom_id':atomids[form],'meaning':'UNASSIGNED'};parts.append(piece);expanded.append(form);ids.append(atomids[form]);pieces+=1;seen.add(form)
    joined=raw in rules
    mapping={'source_group_id':g[0],'source_group':dict(zip(u['group_columns'],g)),'raw':raw,'optional_join_flag':joined,'expansion_status':'PROPOSED_LEXICAL_IDENTITY' if joined else 'UNCHANGED_ATOMIC_UNASSIGNED','expanded_span_zero_based_half_open':[start,pieces],'pieces':parts}
    mappings.append(mapping)
    if joined:occurrences.append({'locus':line['metadata']['locus'],'source_group_id':g[0],'raw':raw,'expanded_forms':atoms,'expanded_span_zero_based_half_open':[start,pieces]})
   lines.append({'metadata':line['metadata'],'original_groups':line['groups'],'diplomatic_forms':[g[2] for g in line['groups']],'proposed_expanded_forms':expanded,'anonymous_atom_ids':ids,'source_map':mappings})
  assert rawcount==expected
  units.append({'unit_id':s['unit_id'],'original_source':s,'lines':lines,'accounting':{'raw_groups':rawcount,'expanded_atom_occurrences':pieces,'distinct_unassigned_atoms':len(seen),'expanded_join_occurrences':len(occurrences)},'expanded_occurrences':occurrences})
 out={'status':'UNSELECTED_LEXICAL_REPRESENTATION','pins':[{'path':str(PLAN.relative_to(R)),'sha256':sha(PLAN)},{'path':str(Path(__file__).resolve().relative_to(R)),'sha256':sha(Path(__file__))}]+[{'path':p,'sha256':h} for p,h in plan['inputs'].items()],'rule':plan['rule'],'atoms':[{'id':atomids[f],'form':f,'meaning':'UNASSIGNED'} for f in sorted(forms)],'units':units,'accounting':{'raw_groups':sum(u['accounting']['raw_groups'] for u in units),'expanded_atom_occurrences':sum(u['accounting']['expanded_atom_occurrences'] for u in units),'distinct_unassigned_atoms':len(forms),'expanded_join_occurrences':sum(u['accounting']['expanded_join_occurrences'] for u in units)},'limits':['Optional lexical identity is unselected; accounting is not semantic progress.','No Class/Command/Entity, assertion/restriction, reference, action or meaning assigned.','Only three exact strings expand; no wider prefix/suffix rule.','All annotations, repetitions, original boundaries and raw c remain in diplomatic source.','The f75r comparison is already exposed, not holdout; zero selected joined occurrences cannot establish positive transfer.','Existing1201 is a predecessor construction; no novelty claimed.']}
 (D/'LEXICAL_WORKSHEET_20261016.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 md=['# Two complete IT2a passages: an unselected lexical worksheet','','Status: **UNSELECTED_LEXICAL_REPRESENTATION**. This is an exact accounting worksheet, not a translation or a selected lexical analysis. Every atom below has unknown meaning. Identical exact forms reuse one anonymous ID across both passages. These IDs identify proposed form atoms, not established single meanings or individual referents.','','Only these optional joined spellings are proposed: `olchedy ↔ ol chedy`, `qolchedy ↔ qol chedy`, `olshedy ↔ ol shedy`. Their lexical identity is an assumption. All other original groups remain atomic and unassigned, including annotations and literal `c`. Expanded spaces are hypothetical internal divisions; the diplomatic source retains the original spacing and line boundaries. The JSON preserves every group ID, original separator, line flag, and source-object field.','','Unlike R771, this worksheet introduces no classes, assertions, restrictions, commands or reference links. It neither resolves nor reuses R771’s free predicate assignments. GDT1201 supplies the earlier transparent-chunk construction; this is not a novelty claim.']
 for unit in units:
  ac=unit['accounting'];md+=['',f"## {unit['unit_id']}",'',f"Original groups: {ac['raw_groups']}; proposed atom occurrences: {ac['expanded_atom_occurrences']}; distinct unknown atoms: {ac['distinct_unassigned_atoms']}; joined occurrences expanded: {ac['expanded_join_occurrences']}."]
  for line in unit['lines']:
   m=line['metadata'];md+=['',f"### {m['locus']} — PS={m.get('paragraph_start','?')}, PE={m.get('paragraph_end','?')}",'','Diplomatic:', '```text',' '.join(line['diplomatic_forms']),'```','Proposed expansion:','```text',' '.join(line['proposed_expanded_forms']),'```','Shared anonymous atom IDs:','```text',' '.join(line['anonymous_atom_ids']),'```']
  md+=['','Exact expanded occurrences:']
  if not unit['expanded_occurrences']:md+=['','None. This comparison passage does not test the three joined spellings positively.']
  for x in unit['expanded_occurrences']:md+=[f"- `{x['source_group_id']}`: `{x['raw']}` → `{' '.join(x['expanded_forms'])}`; expanded positions [{x['expanded_span_zero_based_half_open'][0]}, {x['expanded_span_zero_based_half_open'][1]})."]
 md+=['','## Shared unknown-atom inventory','','| ID | Exact form | Meaning |','|---|---|---|']
 for f in sorted(forms):md.append(f'| {atomids[f]} | `{f}` | UNASSIGNED |')
 md+=['','## Remaining obligations','','A joined and a split spelling sharing content is still hypothetical; the worksheet does not establish common referents, attachment, word boundaries, grammatical roles or meanings. Source-chosen joining remains an explicit unexplained surface choice. Repetition is preserved, not turned into a repeated event or merged away. The already exposed comparison is not independent confirmation. Accounting completeness supplies no evidence that the proposed atom inventory is linguistically correct.','','All counts and exact source maps, including full original metadata, are in `LEXICAL_WORKSHEET_20261016.json`; its pins bind the plan, source artifacts and renderer.']
 (D/'LEXICAL_WORKSHEET_20261016.md').write_text('\n'.join(md)+'\n');print(json.dumps(out['accounting']))
if __name__=='__main__':main()
