#!/usr/bin/env python3
"""Execute the single endpoint-free interior-position target."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"

import csv,hashlib,json,re,tempfile
from collections import Counter
from pathlib import Path
from source_native_within_group_interior_core import ALPHABET,evaluate,load_panel,passes


BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results"
PANEL_PATH=RESULTS/"source_native_within_group_interior_masked.tsv"
CAPACITY_VALIDATION=RESULTS/"source_native_within_group_interior_capacity_validation.json"
CORE=BASE/"source_native_within_group_interior_core.py";TEST_SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_TEST_SPEC.md"
PREFLIGHT=RESULTS/"source_native_within_group_interior_preflight.json";PREFLIGHT_VALIDATION=RESULTS/"source_native_within_group_interior_preflight_validation.json"
TARGET_SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";TARGET_SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json"
SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_TARGET_SPEC.md";RUNNER=Path(__file__).resolve()
OUT=RESULTS/"source_native_within_group_interior_target.json";REPORT=RESULTS/"source_native_within_group_interior_target_report.md"
SAFE_FROZEN={
 PANEL_PATH:"0b6202641045ed11fd1ae4870353b4bec17adcc658c9687fd766f35bfbfe51ad",
 CAPACITY_VALIDATION:"1513617bafcc3c4143af7be129251cf9dd7e7aa5cfa429c414c55eaa8fe923f8",
 CORE:"f516e87c5f0c3be14a9187ffd87f935ea92331147fd3f14241a5ad754ed7bd98",
 TEST_SPEC:"3f278d5ef39432084c9f200039e20799d53b07269f48d6aef7f9b4726ad19696",
 PREFLIGHT:"564fe586a118962344211a8fd7e33c8ac8130bab6b4104c893fb9e6e214107e3",
 PREFLIGHT_VALIDATION:"654aeca00226b198e1f198b922aa999251e1fe5886f44ceb4205a445c9050a9f",
 TARGET_SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
 SPEC:"fa665d4659aa3aab776da34b970bf2aa03b5bd1d0368c11fc86e5ccc8acde670",
}
TARGET_HASH="a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225"
INDEX={value:index for index,value in enumerate(ALPHABET)}
SOURCE_FIELDS=("consensus_group_id","locus","page","section","currier","hand","code","kind","grammar_scope","strict_zero_alternative","consensus_group_index","consensus_group_count","start_symbol_1based","end_symbol_1based","symbol_count","family_surface","zl_sta_codes","it_sta_codes","rf_sta_codes","left_boundary_profile","right_boundary_profile")


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def split_for(folio):
 value=int.from_bytes(hashlib.sha256(f"SNWG001|{folio}".encode()).digest()[:8],"little")%5
 return "TEST" if value==0 else ("CAL" if value==1 else "TRAIN")
def aggregate(result):return {**result,"INTERIOR_POSITION_PASS":passes(result)}
def install_pair(result_bytes,report_bytes):
 if OUT.exists() or REPORT.exists():raise FileExistsError("interior target artifact exists")
 with tempfile.TemporaryDirectory(prefix="source_native_within_group_interior_target_",dir=RESULTS) as directory:
  a=Path(directory)/"result.json";b=Path(directory)/"report.md";a.write_bytes(result_bytes);b.write_bytes(report_bytes)
  if OUT.exists() or REPORT.exists():raise FileExistsError("interior target artifact appeared")
  os.link(a,OUT)
  try:os.link(b,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise


def main():
 if OUT.exists() or REPORT.exists():raise SystemExit("refusing a second interior target run")
 for path,expected in SAFE_FROZEN.items():
  if sha(path)!=expected:raise SystemExit(f"frozen interior target input mismatch: {path.name}")
 if json.loads(CAPACITY_VALIDATION.read_text())["status"]!="PASS_INDEPENDENT_SCORE_BLIND_INTERIOR_CAPACITY_RECONSTRUCTION":raise SystemExit("capacity validation not PASS")
 preflight=json.loads(PREFLIGHT.read_text())
 if preflight["status"]!="PASS_TARGET_FREE_WITHIN_GROUP_INTERIOR_PREFLIGHT" or not all(preflight["gates"].values()):raise SystemExit("preflight not PASS")
 validation=json.loads(PREFLIGHT_VALIDATION.read_text())
 if validation["status"]!="PASS_INDEPENDENT_192_WORLD_INTERIOR_PREFLIGHT_RECONSTRUCTION" or not validation["target_outputs_absent"]:raise SystemExit("preflight validation not PASS")
 if json.loads(TARGET_SOURCE_VALIDATION.read_text())["status"]!="PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":raise SystemExit("source validation not PASS")
 if sha(TARGET_SOURCE)!=TARGET_HASH:raise SystemExit("target source hash mismatch")
 with TARGET_SOURCE.open(encoding="utf-8",newline="") as handle:
  reader=csv.DictReader(handle,delimiter="\t")
  if tuple(reader.fieldnames or ())!=SOURCE_FIELDS:raise ValueError("target schema")
  source_rows=list(reader)
 if len(source_rows)!=26184:raise ValueError("source row count")
 source_by_id={r['consensus_group_id']:r for r in source_rows}
 if len(source_by_id)!=len(source_rows):raise ValueError("duplicate source ID")
 panel=load_panel(PANEL_PATH);panel_ids={r['unit_id'] for r in panel.rows};eligible=set()
 for source in source_rows:
  if source['strict_zero_alternative']=='1' and source['grammar_scope']=='CONFIRMED_PROSE' and re.match(r'f\d+',source['page']) and int(source['symbol_count'])>=3:eligible.add(source['consensus_group_id'])
 if eligible!=panel_ids or len(eligible)!=19203:raise ValueError("eligible ID set")
 sequences=[];family_counts=Counter()
 for masked in panel.rows:
  source=source_by_id.get(masked['unit_id']);match=re.match(r'f\d+',source['page']) if source else None
  if source is None or match is None or source['strict_zero_alternative']!='1' or source['grammar_scope']!='CONFIRMED_PROSE':raise ValueError("join scope")
  surface=source['family_surface'];interior=surface[1:-1]
  if len(surface)!=int(masked['original_symbol_count']) or len(interior)!=int(masked['interior_symbol_count']) or int(source['symbol_count'])!=len(surface):raise ValueError("join length")
  if not interior or any(value not in INDEX for value in interior):raise ValueError("invalid interior family")
  exact={'locus':source['locus'],'page':source['page'],'physical_folio':match.group(),'section':source['section'],'currier':source['currier'],'hand':source['hand'],'kind':source['kind'],'original_symbol_count':str(len(surface)),'interior_symbol_count':str(len(interior)),'split':split_for(match.group())}
  if any(masked[key]!=value for key,value in exact.items()):raise ValueError("metadata mismatch")
  sequences.append(tuple(INDEX[value] for value in interior));family_counts.update(interior)
 forward=aggregate(evaluate(panel,sequences));reversed_result=aggregate(evaluate(panel,[tuple(reversed(sequence)) for sequence in sequences]))
 target_pass=forward['INTERIOR_POSITION_PASS'] and reversed_result['INTERIOR_POSITION_PASS']
 gates={'exact_26184_source_rows':len(source_rows)==26184,'exact_19203_joined_groups':len(sequences)==19203,'exact_45867_interior_symbols':sum(map(len,sequences))==45867,'exact_split_counts':Counter(r['split'] for r in panel.rows)=={'TRAIN':9364,'CAL':4887,'TEST':4952},'exact_94_folios':len(set(panel.folios))==94,'complete_eligible_id_set':eligible==panel_ids,'forward_INTERIOR_POSITION_PASS':forward['INTERIOR_POSITION_PASS'],'reversed_INTERIOR_POSITION_PASS':reversed_result['INTERIOR_POSITION_PASS'],'INTERIOR_POSITION_TARGET_PASS':target_pass}
 if target_pass:status="CONFIRM_ENDPOINT_FREE_WITHIN_GROUP_INTERIOR_POSITION_STRUCTURE";decision="RETAIN_INTERIOR_POSITION_STRUCTURE_BEYOND_ENDPOINTS_AND_LENGTH"
 else:status="NONCONFIRM_ENDPOINT_FREE_WITHIN_GROUP_INTERIOR_POSITION_STRUCTURE";decision="DOWNGRADE_COMPLETE_GROUP_POSITION_RESULT_TO_ENDPOINT_DOMINATED"
 result={'experiment':'SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_TARGET','status':status,'decision':decision,'inputs':{p.name:sha(p) for p in (*SAFE_FROZEN,TARGET_SOURCE,RUNNER)},'source_rows_accessed':len(source_rows),'joined_target_sequences':len(sequences),'interior_symbols':sum(map(len,sequences)),'physical_folios':len(set(panel.folios)),'interior_family_counts':{family:family_counts[family] for family in ALPHABET},'forward':forward,'reversed':reversed_result,'gates':gates,'target_source_opened':True,'target_sequences_accessed':len(sequences),'target_evaluations_computed':2,'endpoint_values_stored':0,'event_level_sequences_stored':0,'english_glosses':0,'claim_ceiling':'A pass establishes only transferable relative-position structure inside source-group interiors beyond endpoints and exact length. It supplies no prefix, root, suffix, sound, word, part of speech, language, cipher operation, meaning, plaintext, or translation.'}
 report=f"""# Endpoint-free source-group interior-position target

Status: **{status}**

The single frozen join matched **{len(sequences):,}** groups and removed every
first and last family before fitting. Forward/reversed CAL selection chooses
**{forward['selected_model']}** and **{reversed_result['selected_model']}**.
Held equal-folio gains are **{forward['gain']['effect_equal_folio']:+.6f}** and
**{reversed_result['gain']['effect_equal_folio']:+.6f}** nat/interior-symbol,
with **{forward['gain']['positive_folios']}/24** and
**{reversed_result['gain']['positive_folios']}/24** positive folios.

`INTERIOR_POSITION_TARGET_PASS` is **{str(target_pass).lower()}**. Decision:
**{decision}**. No endpoint value or event-level interior sequence is stored.
This test supplies no prefix, root, suffix, sound, word, part of speech,
language, cipher operation, meaning, plaintext, or translation.
"""
 install_pair((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),report.encode());print(json.dumps({'status':status,'selected_forward':forward['selected_model'],'selected_reversed':reversed_result['selected_model'],'gates':gates,'decision':decision},sort_keys=True))


if __name__=='__main__':main()
