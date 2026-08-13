#!/usr/bin/env python3
import csv, hashlib, json, re
from pathlib import Path

R=Path(__file__).resolve().parent
RESULTS=R/'experiments/semantic_assumptions/results'
def rows(path):
    with path.open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f,delimiter='\t'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

selection=R/'gdt002_contact_gap_extension_selection.tsv'
method=R/'GDT002_CONTACT_GAP_EXTENSION_METHOD.md'
prior_obs=R/'gdt002_contact_gap_observations.tsv'
prior_result=R/'gdt002_contact_gap_result.json'
panel=rows(selection)
exact={r['locus']:r for r in rows(RESULTS/'existing_human_exact_locus_annotations.tsv')}
cons={r['locus']:r for r in rows(RESULTS/'source_sta_family_consensus_loci.tsv')}
wanted={
 'f99v.16','f99v.19','f100r.6',
 *{f'f88r.{i}' for i in range(2,7)},
 *{f'f102v1.{i}' for i in range(2,7)},
}
unit_loci={
 'F99V_L2':{'f99v.16','f99v.19'},
 'F100R_L2':{'f100r.6'},
 'F88R_L1':{f'f88r.{i}' for i in range(2,7)},
 'F102V1_L1':{f'f102v1.{i}' for i in range(2,7)},
}
checks={
 'rows_13':len(panel)==13,
 'unique_ids':len({r['target_id'] for r in panel})==13,
 'unique_loci':{r['locus'] for r in panel}==wanted,
 'opaque_ids':all(re.fullmatch(r'CGX[0-9A-F]{12}',r['target_id']) for r in panel),
 'four_units':{r['array_id'] for r in panel}==set(unit_loci),
 'unit_loci_exact':all({r['locus'] for r in panel if r['array_id']==u}==ls for u,ls in unit_loci.items()),
 'counts_2_1_5_5':[sum(r['array_id']==u for r in panel) for u in unit_loci]==[2,1,5,5],
 'four_physical_folios':{r['physical_folio'] for r in panel}=={'f99','f100','f88','f102'},
 'official_urls':all(r['official_image_url']==f"https://collections.library.yale.edu/iiif/2/{r['canvas_id']}/full/full/0/default.jpg" for r in panel),
 'positive_dimensions':all(int(r['width'])>0 and int(r['height'])>0 for r in panel),
 'human_rows_exist':wanted<=set(exact),
 'human_units_match':all(exact[r['locus']]['unit']=={'F99V_L2':'L2','F100R_L2':'L2','F88R_L1':'L1','F102V1_L1':'L1'}[r['array_id']] for r in panel),
 'fresh_transfer_rows_strict':all(cons[r['locus']]['strict_zero_alternative']=='1' for r in panel if r['physical_folio'] in {'f88','f102'}),
 'f99_completion_strict':all(cons[r['locus']]['strict_zero_alternative']=='1' for r in panel if r['physical_folio']=='f99'),
 'f100r6_alternative_preserved':cons['f100r.6']['strict_zero_alternative']=='0',
 'no_formal_payload':not any(k in panel[0] for k in ('family_surface','sta_codes','ivtff_group_raw','local_comment')),
 'prior_frozen_artifacts_exist':prior_obs.exists() and prior_result.exists(),
 'method_declares_two_reviewers':'Two reviewers independently receive' in method.read_text(),
 'method_declares_census_kill':'EXTRA_UNMAPPED_INSCRIPTION' in method.read_text(),
 'method_forbids_legacy_carrier':'legacy carrier/parser semantics' in method.read_text(),
}
out={
 'artifact':'GDT002_CONTACT_GAP_EXTENSION_SELECTION_VALIDATION_V1',
 'status':'PASS' if all(checks.values()) else 'FAIL',
 'checks':checks,'passed':sum(checks.values()),'total':len(checks),
 'counts':{'new_calls':13,'completion_calls':3,'fresh_transfer_calls':10,'units':4,'physical_folios':4},
 'bindings':{
  selection.name:sha(selection),method.name:sha(method),prior_obs.name:sha(prior_obs),prior_result.name:sha(prior_result),
  str((RESULTS/'existing_human_exact_locus_annotations.tsv').relative_to(R)):sha(RESULTS/'existing_human_exact_locus_annotations.tsv'),
  str((RESULTS/'source_sta_family_consensus_loci.tsv').relative_to(R)):sha(RESULTS/'source_sta_family_consensus_loci.tsv'),
 },
 'access':{
  'prior_f99_f100_full_canvases_previously_opened':True,
  'new_13_target_calls_reviewed_after_this_freeze':False,
  'fresh_transfer_formal_payload_opened_for_selection':False,
  'automated_vision_used':False,
 },
 'claim_ceiling':'Registration only; no new visual call, construction association, semantic role, word, meaning, or translation.',
}
(R/'gdt002_contact_gap_extension_selection_validation.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
print(json.dumps({'status':out['status'],'passed':out['passed'],'total':out['total']}))
if out['status']!='PASS': raise SystemExit(1)
