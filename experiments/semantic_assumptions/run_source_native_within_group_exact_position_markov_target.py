#!/usr/bin/env python3
"""Execute the registered exact-position-controlled transition target once."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import csv,hashlib,json,re,tempfile
from collections import Counter
from pathlib import Path
from source_native_within_group_exact_position_markov_core import ALPHABET,evaluate,load_panel,passes

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_within_group_stage_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_within_group_stage_capacity_validation.json";CORE=BASE/"source_native_within_group_exact_position_markov_core.py";TEST_SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_EXACT_POSITION_MARKOV_SPEC.md";PREFLIGHT=RESULTS/"source_native_within_group_exact_position_markov_preflight.json";PREFLIGHT_VALIDATION=RESULTS/"source_native_within_group_exact_position_markov_preflight_validation.json";TARGET_SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json";SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_EXACT_POSITION_MARKOV_TARGET_SPEC.md";RUNNER=Path(__file__).resolve();OUT=RESULTS/"source_native_within_group_exact_position_markov_target.json";REPORT=RESULTS/"source_native_within_group_exact_position_markov_target_report.md"
SAFE_FROZEN={PANEL_PATH:"16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",CAPACITY_VALIDATION:"2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",CORE:"269d0167fb13930386eaba2398a47578c54a897bcb74f0b9b1da8c57f4d1a892",TEST_SPEC:"8b2747a55cd88cafe0f2fcc4201634b123c9bd95bcaac6bd8495e36e75aea5d1",PREFLIGHT:"3e12ded71c65d158f5e3c20301c5701536ec29f0b4bc53bd39caa994366194a9",PREFLIGHT_VALIDATION:"6926383302f914eeb958e22ee1410b2c0369312492625a04e9a54243e15585c6",SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",SPEC:"81336cfaba5cd1d2221783d01ea3a63edc8d7e0489177902ea3174501ed32671"};TARGET_HASH="a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225";INDEX={value:index for index,value in enumerate(ALPHABET)};SOURCE_FIELDS=("consensus_group_id","locus","page","section","currier","hand","code","kind","grammar_scope","strict_zero_alternative","consensus_group_index","consensus_group_count","start_symbol_1based","end_symbol_1based","symbol_count","family_surface","zl_sta_codes","it_sta_codes","rf_sta_codes","left_boundary_profile","right_boundary_profile")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def split_for(folio):
 value=int.from_bytes(hashlib.sha256(f"SNWG001|{folio}".encode()).digest()[:8],"little")%5
 return 'TEST' if value==0 else ('CAL' if value==1 else 'TRAIN')
def aggregate(result):return {**result,'EXACT_POSITION_MARKOV_PASS':passes(result)}
def install_pair(result_bytes,report_bytes):
 if OUT.exists() or REPORT.exists():raise FileExistsError('target exists')
 with tempfile.TemporaryDirectory(prefix='source_native_exact_position_markov_target_',dir=RESULTS) as directory:
  staged_result=Path(directory)/'result.json';staged_report=Path(directory)/'report.md';staged_result.write_bytes(result_bytes);staged_report.write_bytes(report_bytes)
  if OUT.exists() or REPORT.exists():raise FileExistsError('target appeared')
  os.link(staged_result,OUT)
  try:os.link(staged_report,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing second exact-position target')
 for path,expected in SAFE_FROZEN.items():
  if sha(path)!=expected:raise SystemExit(f'frozen exact-position target mismatch: {path.name}')
 if json.loads(CAPACITY_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION':raise SystemExit('capacity not PASS')
 preflight=json.loads(PREFLIGHT.read_text());validation=json.loads(PREFLIGHT_VALIDATION.read_text())
 if preflight['status']!='PASS_TARGET_FREE_EXACT_POSITION_MARKOV_PREFLIGHT' or not all(preflight['gates'].values()):raise SystemExit('preflight not PASS')
 if validation['status']!='PASS_INDEPENDENT_192_WORLD_EXACT_POSITION_MARKOV_RECONSTRUCTION' or not validation['target_outputs_absent']:raise SystemExit('validation not PASS')
 if json.loads(SOURCE_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION':raise SystemExit('source not PASS')
 if sha(TARGET_SOURCE)!=TARGET_HASH:raise SystemExit('source hash mismatch')
 with TARGET_SOURCE.open(encoding='utf-8',newline='') as handle:
  reader=csv.DictReader(handle,delimiter='\t')
  if tuple(reader.fieldnames or ())!=SOURCE_FIELDS:raise ValueError('schema')
  rows=list(reader)
 if len(rows)!=26184:raise ValueError('source count')
 by_id={row['consensus_group_id']:row for row in rows}
 if len(by_id)!=len(rows):raise ValueError('duplicate source')
 panel=load_panel(PANEL_PATH);panel_ids={row['unit_id'] for row in panel.rows};eligible={row['consensus_group_id'] for row in rows if row['strict_zero_alternative']=='1' and row['grammar_scope']=='CONFIRMED_PROSE' and re.match(r'f\d+',row['page'])}
 if eligible!=panel_ids or len(eligible)!=21899:raise ValueError('eligible set')
 sequences=[];family_counts=Counter()
 for masked in panel.rows:
  source=by_id.get(masked['unit_id']);match=re.match(r'f\d+',source['page']) if source else None
  if source is None or match is None or source['strict_zero_alternative']!='1' or source['grammar_scope']!='CONFIRMED_PROSE':raise ValueError('join scope')
  surface=source['family_surface']
  if len(surface)!=int(masked['symbol_count']) or int(source['symbol_count'])!=len(surface) or any(symbol not in INDEX for symbol in surface):raise ValueError('surface')
  exact={'locus':source['locus'],'page':source['page'],'physical_folio':match.group(),'section':source['section'],'currier':source['currier'],'hand':source['hand'],'kind':source['kind'],'symbol_count':str(len(surface)),'split':split_for(match.group())}
  if any(masked[key]!=value for key,value in exact.items()):raise ValueError('metadata')
  sequences.append(tuple(INDEX[symbol] for symbol in surface));family_counts.update(surface)
 forward=aggregate(evaluate(panel,sequences));reverse=aggregate(evaluate(panel,[tuple(reversed(sequence)) for sequence in sequences]));target=forward['EXACT_POSITION_MARKOV_PASS'] and reverse['EXACT_POSITION_MARKOV_PASS']
 gates={'exact_26184_source_rows':len(rows)==26184,'exact_21899_joined_groups':len(sequences)==21899,'exact_5521_scored_test_groups':forward['test_groups']==5521 and reverse['test_groups']==5521,'exact_17435_test_transition_symbols':forward['test_symbols']==17435 and reverse['test_symbols']==17435,'exact_split_counts':Counter(row['split'] for row in panel.rows)=={'TRAIN':10753,'CAL':5516,'TEST':5630},'exact_94_folios':len(set(panel.folios))==94,'complete_eligible_id_set':eligible==panel_ids,'forward_EXACT_POSITION_MARKOV_PASS':forward['EXACT_POSITION_MARKOV_PASS'],'reversed_EXACT_POSITION_MARKOV_PASS':reverse['EXACT_POSITION_MARKOV_PASS'],'EXACT_POSITION_MARKOV_TARGET_PASS':target}
 if target:status='CONFIRM_EXACT_POSITION_CONTROLLED_FIRST_ORDER_DEPENDENCY';decision='RETAIN_POSITION_INDEPENDENT_LOCAL_TRANSITION_GRAMMAR'
 else:status='NONCONFIRM_EXACT_POSITION_CONTROLLED_FIRST_ORDER_DEPENDENCY';decision='DOWNGRADE_COARSE_MARKOV_TO_POSITION_CONFOUND'
 result={'experiment':'SOURCE_NATIVE_WITHIN_GROUP_EXACT_POSITION_MARKOV_TARGET','status':status,'decision':decision,'inputs':{path.name:sha(path) for path in (*SAFE_FROZEN,TARGET_SOURCE,RUNNER)},'source_rows_accessed':len(rows),'joined_target_sequences':len(sequences),'scored_test_groups':forward['test_groups'],'scored_test_transition_symbols':forward['test_symbols'],'physical_folios':len(set(panel.folios)),'family_counts':{symbol:family_counts[symbol] for symbol in ALPHABET},'forward':forward,'reversed':reverse,'gates':gates,'target_source_opened':True,'target_sequences_accessed':len(sequences),'target_evaluations_computed':2,'event_level_sequences_stored':0,'event_level_transitions_stored':0,'event_level_positions_stored':0,'english_glosses':0,'claim_ceiling':'A pass establishes only transferable first-order source-family dependency beyond Currier, exact length, exact ordinal position, endpoints, and folio. It supplies no syntax, morphology, sound, word, language, meaning, plaintext, cipher, or translation.'}
 report=f"""# Exact-position-controlled transition target

Status: **{status}**

The single frozen join matched **{len(sequences):,}** complete groups and scored
**{forward['test_symbols']:,}** noninitial held transitions. Forward/reversed
transition-minus-exact-position equal-folio gains are
**{forward['gain']['effect_equal_folio']:+.6f}** and
**{reverse['gain']['effect_equal_folio']:+.6f}** nat/transition-symbol, with
**{forward['gain']['positive_folios']}/24** and
**{reverse['gain']['positive_folios']}/24** positive folios. Exact unseen-group
gains are **{forward['unseen']['effect_equal_folio']:+.6f}** and
**{reverse['unseen']['effect_equal_folio']:+.6f}** on
**{forward['unseen']['groups']}** held groups.

`EXACT_POSITION_MARKOV_TARGET_PASS` is **{str(target).lower()}**. Decision:
**{decision}**. No event-level sequence, transition, or position is stored.
This supplies no syntax, morphology, sound, word, language, meaning, plaintext,
cipher, or translation.
""";install_pair((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),report.encode());print(json.dumps({'status':status,'gates':gates,'decision':decision},sort_keys=True))
if __name__=='__main__':main()
