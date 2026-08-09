#!/usr/bin/env python3
"""Execute the single within-group Markov-increment target."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import csv,hashlib,json,re,tempfile
from collections import Counter
from pathlib import Path
from source_native_within_group_markov_core import ALPHABET,evaluate,load_panel,passes

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_within_group_stage_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_within_group_stage_capacity_validation.json";CORE=BASE/"source_native_within_group_markov_core.py";TEST_SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_MARKOV_INCREMENT_TEST_SPEC.md";PREFLIGHT=RESULTS/"source_native_within_group_markov_preflight.json";PREFLIGHT_VALIDATION=RESULTS/"source_native_within_group_markov_preflight_validation.json";TARGET_SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json";SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_MARKOV_TARGET_SPEC.md";RUNNER=Path(__file__).resolve();OUT=RESULTS/"source_native_within_group_markov_target.json";REPORT=RESULTS/"source_native_within_group_markov_target_report.md"
SAFE_FROZEN={PANEL_PATH:"16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",CAPACITY_VALIDATION:"2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",CORE:"8bc3020e69bea9f50854fd1b512a327bb9322a513000e13f267bb65315fd787e",TEST_SPEC:"7a923c422b143dc4187c56a940a691959016c258bc1b83468a2cc598fd9a1b66",PREFLIGHT:"978363232bb3e2213013ac63f99dcee1b1de437ce04c5f61940039f11ea5cff3",PREFLIGHT_VALIDATION:"39221059e92c19ace099c44f574ef8926cd9e2425f7c0cbdcb4cdf9ba61b61ae",SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",SPEC:"5d9fc2826ac996ac9ad6b9f23601a9934290fcbeed2ac783d219176fdb36ad02"};TARGET_HASH="a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225";INDEX={value:index for index,value in enumerate(ALPHABET)};SOURCE_FIELDS=("consensus_group_id","locus","page","section","currier","hand","code","kind","grammar_scope","strict_zero_alternative","consensus_group_index","consensus_group_count","start_symbol_1based","end_symbol_1based","symbol_count","family_surface","zl_sta_codes","it_sta_codes","rf_sta_codes","left_boundary_profile","right_boundary_profile")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def split_for(folio):
 value=int.from_bytes(hashlib.sha256(f"SNWG001|{folio}".encode()).digest()[:8],"little")%5
 return 'TEST' if value==0 else ('CAL' if value==1 else 'TRAIN')
def aggregate(result):return {**result,'MARKOV_INCREMENT_PASS':passes(result)}
def install_pair(a,b):
 if OUT.exists() or REPORT.exists():raise FileExistsError('target exists')
 with tempfile.TemporaryDirectory(prefix='source_native_within_group_markov_target_',dir=RESULTS) as d:
  x=Path(d)/'result.json';y=Path(d)/'report.md';x.write_bytes(a);y.write_bytes(b)
  if OUT.exists() or REPORT.exists():raise FileExistsError('target appeared')
  os.link(x,OUT)
  try:os.link(y,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing second Markov target')
 for path,expected in SAFE_FROZEN.items():
  if sha(path)!=expected:raise SystemExit(f'frozen Markov target mismatch: {path.name}')
 if json.loads(CAPACITY_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION':raise SystemExit('capacity not PASS')
 p=json.loads(PREFLIGHT.read_text());v=json.loads(PREFLIGHT_VALIDATION.read_text())
 if p['status']!='PASS_TARGET_FREE_WITHIN_GROUP_MARKOV_PREFLIGHT' or not all(p['gates'].values()):raise SystemExit('preflight not PASS')
 if v['status']!='PASS_INDEPENDENT_192_WORLD_MARKOV_PREFLIGHT_RECONSTRUCTION' or not v['target_outputs_absent']:raise SystemExit('validation not PASS')
 if json.loads(SOURCE_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION':raise SystemExit('source not PASS')
 if sha(TARGET_SOURCE)!=TARGET_HASH:raise SystemExit('source hash mismatch')
 with TARGET_SOURCE.open(encoding='utf-8',newline='') as h:
  reader=csv.DictReader(h,delimiter='\t')
  if tuple(reader.fieldnames or ())!=SOURCE_FIELDS:raise ValueError('schema')
  rows=list(reader)
 if len(rows)!=26184:raise ValueError('source count')
 by={r['consensus_group_id']:r for r in rows}
 if len(by)!=len(rows):raise ValueError('duplicate source')
 panel=load_panel(PANEL_PATH);panel_ids={r['unit_id'] for r in panel.rows};eligible={r['consensus_group_id'] for r in rows if r['strict_zero_alternative']=='1' and r['grammar_scope']=='CONFIRMED_PROSE' and re.match(r'f\d+',r['page'])}
 if eligible!=panel_ids or len(eligible)!=21899:raise ValueError('eligible set')
 sequences=[];counts=Counter()
 for masked in panel.rows:
  source=by.get(masked['unit_id']);match=re.match(r'f\d+',source['page']) if source else None
  if source is None or match is None or source['strict_zero_alternative']!='1' or source['grammar_scope']!='CONFIRMED_PROSE':raise ValueError('join scope')
  surface=source['family_surface']
  if len(surface)!=int(masked['symbol_count']) or int(source['symbol_count'])!=len(surface) or any(x not in INDEX for x in surface):raise ValueError('surface')
  exact={'locus':source['locus'],'page':source['page'],'physical_folio':match.group(),'section':source['section'],'currier':source['currier'],'hand':source['hand'],'kind':source['kind'],'symbol_count':str(len(surface)),'split':split_for(match.group())}
  if any(masked[k]!=value for k,value in exact.items()):raise ValueError('metadata')
  sequences.append(tuple(INDEX[x] for x in surface));counts.update(surface)
 forward=aggregate(evaluate(panel,sequences));reverse=aggregate(evaluate(panel,[tuple(reversed(s)) for s in sequences]));target=forward['MARKOV_INCREMENT_PASS'] and reverse['MARKOV_INCREMENT_PASS'];gates={'exact_26184_source_rows':len(rows)==26184,'exact_21899_joined_groups':len(sequences)==21899,'exact_split_counts':Counter(r['split'] for r in panel.rows)=={'TRAIN':10753,'CAL':5516,'TEST':5630},'exact_94_folios':len(set(panel.folios))==94,'complete_eligible_id_set':eligible==panel_ids,'forward_MARKOV_INCREMENT_PASS':forward['MARKOV_INCREMENT_PASS'],'reversed_MARKOV_INCREMENT_PASS':reverse['MARKOV_INCREMENT_PASS'],'MARKOV_TARGET_PASS':target}
 if target:status='CONFIRM_SOURCE_NATIVE_WITHIN_GROUP_FIRST_ORDER_DEPENDENCY';decision='RETAIN_PORTABLE_LOCAL_TRANSITION_GRAMMAR'
 else:status='NONCONFIRM_SOURCE_NATIVE_WITHIN_GROUP_FIRST_ORDER_DEPENDENCY';decision='FAVOR_RECURRENT_TEMPLATES_OVER_FROZEN_FIRST_ORDER_RULE'
 result={'experiment':'SOURCE_NATIVE_WITHIN_GROUP_MARKOV_TARGET','status':status,'decision':decision,'inputs':{p.name:sha(p) for p in (*SAFE_FROZEN,TARGET_SOURCE,RUNNER)},'source_rows_accessed':len(rows),'joined_target_sequences':len(sequences),'physical_folios':len(set(panel.folios)),'family_counts':{x:counts[x] for x in ALPHABET},'forward':forward,'reversed':reverse,'gates':gates,'target_source_opened':True,'target_sequences_accessed':len(sequences),'target_evaluations_computed':2,'event_level_sequences_stored':0,'event_level_transitions_stored':0,'english_glosses':0,'claim_ceiling':'A pass establishes only transferable first-order source-family dependency beyond Currier, exact length, five-position bins, and folio. It supplies no syntax, morphology, sound, word, language, meaning, plaintext, cipher, or translation.'}
 report=f"""# Source-native within-group Markov-increment target

Status: **{status}**

The single frozen join matched **{len(sequences):,}** complete groups.
Forward/reversed transition-minus-position equal-folio gains are
**{forward['gain']['effect_equal_folio']:+.6f}** and
**{reverse['gain']['effect_equal_folio']:+.6f}** nat/symbol, with
**{forward['gain']['positive_folios']}/24** and
**{reverse['gain']['positive_folios']}/24** positive folios. Exact unseen-group
gains are **{forward['unseen']['effect_equal_folio']:+.6f}** and
**{reverse['unseen']['effect_equal_folio']:+.6f}** on
**{forward['unseen']['groups']}** held groups.

`MARKOV_TARGET_PASS` is **{str(target).lower()}**. Decision: **{decision}**.
No event-level sequence or transition is stored. This supplies no syntax,
morphology, sound, word, language, meaning, plaintext, cipher, or translation.
""";install_pair((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),report.encode());print(json.dumps({'status':status,'gates':gates,'decision':decision},sort_keys=True))
if __name__=='__main__':main()
