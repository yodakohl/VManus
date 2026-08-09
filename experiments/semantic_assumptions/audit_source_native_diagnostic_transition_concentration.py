#!/usr/bin/env python3
"""Expose the folio concentration behind the frozen diagnostic nonconfirmation."""

from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path
import numpy as np
from source_native_diagnostic_transition_core import ALPHABET,INDEX,load_panel,rotation_scores

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_diagnostic_transition_masked.tsv";SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";CORE=BASE/"source_native_diagnostic_transition_core.py";TARGET=RESULTS/"source_native_diagnostic_transition_target.json";TARGET_VALIDATION=RESULTS/"source_native_diagnostic_transition_target_validation.json";SPEC=BASE/"SOURCE_NATIVE_DIAGNOSTIC_CONCENTRATION_AUDIT_SPEC.md";AUDITOR=Path(__file__).resolve();OUT_TSV=RESULTS/"source_native_diagnostic_transition_concentration.tsv";OUT_JSON=RESULTS/"source_native_diagnostic_transition_concentration.json";OUT_REPORT=RESULTS/"source_native_diagnostic_transition_concentration_report.md"
FROZEN={PANEL_PATH:"7ed9f8186dcb31bd49a446e6b7751dc0bfc0f9d508feb816314fc71105daea02",SOURCE:"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",CORE:"4494da0ec8969b44c5636c419fb55b3485d4ddad98c3406c6f0cf09a3595a211",TARGET:"f01ca643dda1030b6fb7d43efa04c87a81e111e2c43a38c669f1380a67d34182",TARGET_VALIDATION:"4b6eb35f19c0a0152ac5947e070daa026ee5d4cb549f09d5b68aea56904ec294",SPEC:"03b545c5096abcb332b4b34126feedd8eb9a8c128653402aede5db05e85bdca7"}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def join(panel):
 with SOURCE.open(encoding='utf-8',newline='') as handle:rows=list(csv.DictReader(handle,delimiter='\t'))
 by_id={row['consensus_group_id']:row for row in rows};sequences=[]
 for masked in panel.rows:
  row=by_id[masked['unit_id']];surface=row['family_surface']
  if row['strict_zero_alternative']!='1' or row['grammar_scope']!='DIAGNOSTIC_NONPROSE' or len(surface)!=int(masked['symbol_count']) or any(value not in INDEX for value in surface):raise ValueError('join')
  sequences.append(tuple(INDEX[value] for value in surface))
 return sequences
def main():
 if any(path.exists() for path in (OUT_TSV,OUT_JSON,OUT_REPORT)):raise SystemExit('refusing overwrite')
 for path,expected in FROZEN.items():
  if sha(path)!=expected:raise SystemExit(f'frozen mismatch: {path.name}')
 target=json.loads(TARGET.read_text());validation=json.loads(TARGET_VALIDATION.read_text())
 if target['status']!='NONCONFIRM_PROSE_GRAPH_TRANSFER_TO_DIAGNOSTIC_TEXT' or validation['status']!='PASS_PRODUCTION_FREE_DIAGNOSTIC_NONCONFIRMATION_RECONSTRUCTION':raise SystemExit('target state')
 panel=load_panel(PANEL_PATH);sequences=join(panel);rows=[];summaries={}
 for ensemble in ('SECTION_KIND_LENGTH','FOLIO_KIND_LENGTH'):
  orbit=rotation_scores(panel,sequences,ensemble,8192);fav_res=orbit['favored_folio'][0]-orbit['favored_folio'][1:].mean(axis=0);dis_res=orbit['disfavored_folio'][0]-orbit['disfavored_folio'][1:].mean(axis=0);fav_den=float(np.abs(fav_res).sum());dis_den=float(np.abs(dis_res).sum());total_fav=orbit['favored'];total_dis=orbit['disfavored']
  for index,folio in enumerate(panel.folios):
   fav_without=total_fav-orbit['favored_folio'][:,index];dis_without=total_dis-orbit['disfavored_folio'][:,index];mask=panel.folio_index==index;rows.append({'ensemble':ensemble,'physical_folio':folio,'groups':int(mask.sum()),'noninitial_positions':int(np.maximum(0,panel.lengths[mask]-1).sum()),'observed_favored':int(orbit['favored_folio'][0,index]),'null_mean_favored':float(orbit['favored_folio'][1:,index].mean()),'favored_residual':float(fav_res[index]),'favored_abs_contribution_fraction':float(abs(fav_res[index])/fav_den) if fav_den else 1.,'observed_disfavored':int(orbit['disfavored_folio'][0,index]),'null_mean_disfavored':float(orbit['disfavored_folio'][1:,index].mean()),'disfavored_residual':float(dis_res[index]),'disfavored_abs_contribution_fraction':float(abs(dis_res[index])/dis_den) if dis_den else 1.,'deletion_favored_upper_p':float(np.mean(fav_without>=fav_without[0])),'deletion_disfavored_lower_p':float(np.mean(dis_without<=dis_without[0]))})
  maximum=max((row for row in rows if row['ensemble']==ensemble),key=lambda row:(row['favored_abs_contribution_fraction'],row['physical_folio']));summaries[ensemble]={'maximum_favored_folio':maximum['physical_folio'],'maximum_favored_abs_contribution_fraction':maximum['favored_abs_contribution_fraction'],'maximum_folio_favored_residual':maximum['favored_residual'],'maximum_folio_groups':maximum['groups'],'maximum_folio_noninitial_positions':maximum['noninitial_positions'],'maximum_deletion_favored_upper_p':maximum['deletion_favored_upper_p'],'maximum_deletion_disfavored_lower_p':maximum['deletion_disfavored_lower_p'],'all_deletion_favored_p_at_most_01':all(row['deletion_favored_upper_p']<=.01 for row in rows if row['ensemble']==ensemble),'all_deletion_disfavored_p_at_most_01':all(row['deletion_disfavored_lower_p']<=.01 for row in rows if row['ensemble']==ensemble)}
 with OUT_TSV.open('w',encoding='utf-8',newline='') as handle:writer=csv.DictWriter(handle,fieldnames=tuple(rows[0]),delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows)
 result={'experiment':'SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_CONCENTRATION_AUDIT','status':'PASS_POST_RESULT_CONCENTRATION_DIAGNOSTIC','inputs':{path.name:sha(path) for path in (*FROZEN,AUDITOR)},'rows':len(rows),'ensembles':summaries,'tsv_sha256':sha(OUT_TSV),'original_target_status':target['status'],'original_target_decision':target['decision'],'original_gate_changed':False,'event_level_sequences_stored':0,'event_level_pairs_stored':0,'member_codes_accessed':0,'english_glosses':0,'claim_ceiling':'Post-result folio concentration diagnosis only; the frozen nonconfirmation is unchanged and no wordhood, ownership, label meaning, sound, language, cipher, plaintext, or translation follows.'};OUT_JSON.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');a=summaries['SECTION_KIND_LENGTH'];b=summaries['FOLIO_KIND_LENGTH'];OUT_REPORT.write_text(f"""# Diagnostic transition concentration audit

Status: **{result['status']}**

The largest favored contributor is **{a['maximum_favored_folio']}** under
`SECTION_KIND_LENGTH` ({a['maximum_favored_abs_contribution_fraction']:.3%};
{a['maximum_folio_groups']} groups / {a['maximum_folio_noninitial_positions']}
positions) and **{b['maximum_favored_folio']}** under `FOLIO_KIND_LENGTH`
({b['maximum_favored_abs_contribution_fraction']:.3%};
{b['maximum_folio_groups']} groups / {b['maximum_folio_noninitial_positions']}
positions). Deleting those folios gives favored p
**{a['maximum_deletion_favored_upper_p']:.6f} / {b['maximum_deletion_favored_upper_p']:.6f}**
and disfavored p
**{a['maximum_deletion_disfavored_lower_p']:.6f} / {b['maximum_deletion_disfavored_lower_p']:.6f}**.

This audit changes no registered gate or decision. The result remains a frozen
nonconfirmation and supplies no wordhood, ownership, label meaning, picture
identity, sound, language, cipher, plaintext, or translation.
""");print(json.dumps({'status':result['status'],'ensembles':summaries,'decision_unchanged':True},sort_keys=True))
if __name__=='__main__':main()
