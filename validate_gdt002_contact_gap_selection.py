#!/usr/bin/env python3
import csv, hashlib, json, re
from pathlib import Path

R=Path(__file__).resolve().parent
RESULTS=R/'experiments/semantic_assumptions/results'

def table(p):
    with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

selection=R/'gdt002_contact_gap_selection.tsv'
method=R/'GDT002_CONTACT_GAP_ACQUISITION_METHOD.md'
rows=table(selection)
wanted={'f89r2.32','f89r2.33','f89r2.34','f99v.15','f99v.17','f99v.18','f99v.20','f100r.7','f100r.8','f100r.9','f100r.10','f100r.11'}
exact={x['locus']:x for x in table(RESULTS/'existing_human_exact_locus_annotations.tsv')}
cons={x['locus']:x for x in table(RESULTS/'source_sta_family_consensus_loci.tsv')}
checks={
 'rows_12':len(rows)==12,
 'unique_ids':len({x['target_id'] for x in rows})==12,
 'unique_loci_exact_panel':{x['locus'] for x in rows}==wanted,
 'three_folios':{x['physical_folio'] for x in rows}=={'f89','f99','f100'},
 'three_arrays':{x['array_id'] for x in rows}=={'F89R2_L4','F99V_L2','F100R_L2'},
 'opaque_id_shape':all(re.fullmatch(r'CG[0-9A-F]{12}',x['target_id']) for x in rows),
 'counts_3_4_5':[sum(x['physical_folio']==f for x in rows) for f in ('f89','f99','f100')]==[3,4,5],
 'official_urls':all(x['official_image_url']==f"https://collections.library.yale.edu/iiif/2/{x['canvas_id']}/full/full/0/default.jpg" for x in rows),
 'human_source_rows_exist':wanted<=set(exact),
 'human_source_arrays_exact':all(exact[x['locus']]['unit']=={'f89':'L4','f99':'L2','f100':'L2'}[x['physical_folio']] for x in rows),
 'strict_zero_alternative_formal_coverage':all(cons[x['locus']]['strict_zero_alternative']=='1' for x in rows),
 'formal_payload_not_in_selection':not any(k in rows[0] for k in ('family_surface','sta_codes','ivtff_group_raw')),
}
out={'artifact':'GDT002_CONTACT_GAP_SELECTION_VALIDATION_V1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'passed':sum(checks.values()),'total':len(checks),'counts':{'rows':len(rows),'folios':3,'arrays':3},'inputs':{selection.name:sha(selection),method.name:sha(method),str((RESULTS/'existing_human_exact_locus_annotations.tsv').relative_to(R)):sha(RESULTS/'existing_human_exact_locus_annotations.tsv'),str((RESULTS/'source_sta_family_consensus_loci.tsv').relative_to(R)):sha(RESULTS/'source_sta_family_consensus_loci.tsv')},'access':{'target_images_opened':False,'formal_payload_opened_for_selection':False,'ocr_or_automated_vision_used':False},'claim_ceiling':'Registration and capacity panel only; no visual state, formal association, role, word, meaning, or translation.'}
(R/'gdt002_contact_gap_selection_validation.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
print(json.dumps({'status':out['status'],'passed':out['passed'],'total':out['total']}))
if out['status']!='PASS':raise SystemExit(1)
