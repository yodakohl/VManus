#!/usr/bin/env python3
"""Documentation and source-account parity only. No semantic/model experiment."""
import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(name,value):
    checks.append({'check':name,'pass':bool(value)})
    if not value: raise AssertionError(name)
inputs=read(D/'AG_INPUTS.json')
for r in inputs['files']:ck('source_hash:'+r['path'],sha(ROOT/r['path'])==r['sha256'])
seedsource=ROOT/'experiments/yolo/gdt982_reciprocal_flow_clause_readings/artifacts/COMPLETE_CONTEXT.json'
freesource=D/'R_COMPLETE_UNITS.json'
ck('seed_byte_copy',(D/'AG_COMPLETE_SEED.json').read_bytes()==seedsource.read_bytes())
ck('free_byte_copy',(D/'AG_COMPLETE_FREE.json').read_bytes()==freesource.read_bytes())
a=read(D/'AG_ACCOUNT.json');seed=read(seedsource);free=read(freesource)
ck('six_whole_units',len(a['units'])==6)
for u in a['units']:
    ed=u['edition'];key=u['unit']
    if key=='f75v.38–42': expected=seed[ed];loci=[f'f75v.{n}' for n in range(38,43)]
    else:
        z=next(z for z in free['units'] if z['edition']==ed)
        expected=[{'metadata':l['metadata'],'groups':[dict(zip(z['group_columns'],g)) for g in l['groups']]} for l in z['lines']]
        loci=[f'f75v.{n}' for n in range(43,50)]
    ck(ed+key+'raw_parity',u['lines']==expected)
    ck(ed+key+'all_loci',[l['metadata']['locus'] for l in u['lines']]==loci)
    for line in u['lines']:ck(ed+line['metadata']['locus']+'source_group_count',len(line['groups'])==int(line['metadata']['source_group_count']))
    c=next(c for c in a['counts'] if c['edition']==ed and c['unit']==key)
    groups=[g for l in u['lines'] for g in l['groups']]
    ck(ed+key+'total',len(groups)==c['groups'])
    ck(ed+key+'labels',sum(g['ivtff_group_raw'] in a['lexical_obligations'] for g in groups)==c['exact_C0_label_positions'])
    ck(ed+key+'unknown',c['unknown_positions']==c['groups']-c['exact_C0_label_positions'])
expectedocc=[]
for u in a['units']:
    for l in u['lines']:
        for g in l['groups']:
            if g['ivtff_group_raw'] in a['lexical_obligations']:
                expectedocc.append((u['edition'],u['unit'],l['metadata']['locus'],g['source_group_id'],g['ivtff_group_raw']))
actualocc=[(r['edition'],r['unit'],r['locus'],r['source_group_id'],r['ivtff_group_raw']) for r in a['exact_occurrence_inventory']]
ck('all_exact_occurrences_once',expectedocc==actualocc)
ck('401_groups',sum(c['groups'] for c in a['counts'])==401)
ck('105_hypothetical_labels',sum(c['exact_C0_label_positions'] for c in a['counts'])==105)
ck('296_unknown_positions',sum(c['unknown_positions'] for c in a['counts'])==296)
ck('eight_free_base_occurrences',sum(r['ivtff_group_raw']=='qokeey' for r in a['exact_occurrence_inventory'])==8)
ck('three_derived_reading_occurrences',sum(r['ivtff_group_raw']=='qoqokeey' for r in a['exact_occurrence_inventory'])==3)
for ed in ('ZL3b','IT2a','RF1b'):
    hits=[r for r in a['exact_occurrence_inventory'] if r['edition']==ed and r['locus']=='f75v.45' and r['ivtff_group_raw']=='qokeey']
    ck(ed+'doublet_indices',[r['source_group_index'] for r in hits]==['8','9'])
    ck(ed+'doublet_definite_gap',all(r['left_separator']=='DEFINITE_SPACE' and r['right_separator']=='DEFINITE_SPACE' for r in hits))
card=read(D/'AG_01_RECIPROCAL_TRANSFER_HEAD.json')
ck('raw_not_tested',card['status']=='RAW_UNREVIEWED_PARTIAL_C0_NOT_TESTED')
ck('twelve_paid_entries',card['design']['new_semantic_and_grammar_costs']['total_semantic_entries']==12)
ck('explicit_no_semantic_test','no test' in card['design']['claim_ceiling'])
text=(D/'AG_CONSTRUCTION.md').read_text()
for token in ('GDT983','GDT985','GDT863','GDT918','GDT822','UNCERTAIN_SMALL_SPACE','FLOW_EVENT','twelve','NOT_ONCE','not new empirical'):
    ck('documented_limit:'+token,token in text)
result={'status':'PASS','kind':'documentation/source-parity only; not a semantic test','checks':len(checks),'details':checks,'total_groups':401,'hypothetical_label_positions':105,'unknown_positions':296,'no_new_target_access':True}
print(json.dumps(result,ensure_ascii=False,indent=2))
