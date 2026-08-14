#!/usr/bin/env python3
"""Validate the frozen matched selection and build the compact GDT005 result."""
import csv, hashlib, json
from pathlib import Path

R=Path(__file__).resolve().parent
def rd(p):
    with (R/p).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sh(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def guarded(p,loci):
    with (R/p).open(encoding='utf-8') as f:
        h=f.readline().rstrip('\n').split('\t'); i=h.index('locus'); out=[]
        for line in f:
            probe=line.split('\t',i+1)
            if len(probe)<=i or probe[i] not in loci:continue
            out.append(dict(zip(h,line.rstrip('\n').split('\t'))))
    return out

sel=rd('gdt005_matched_cut_selection.tsv'); obs={x['pair_id']:x for x in rd('gdt005_matched_cut_observations.tsv')}
g4={x['target_id']:x for x in rd('gdt004_module_shape_selection.tsv')}
assert len(sel)==len(obs)==9 and len({x['locus'] for x in sel})==9 and all('f84' not in str(x) for x in sel)
loci={x['locus'] for x in sel}; sta=guarded('experiments/semantic_assumptions/results/source_sta_group_alignment.tsv',loci)
for x in sel:
    rows=[r for r in sta if r['edition']=='ZL3b' and r['locus']==x['locus']]
    t=int(x['target_group_index']); target=x['target_surface']
    candidates=sorted((abs(len(r['nearest_basic_eva_primary'])-len(target)),abs(int(r['source_group_index'])-t),int(r['source_group_index']),r['nearest_basic_eva_primary']) for r in rows if int(r['source_group_index'])!=t)
    assert candidates[0]==(int(x['length_difference']),int(x['group_index_distance']),int(x['control_group_index']),x['control_surface'])
    assert g4[x['target_id']]['locus']==x['locus'] and g4[x['target_id']]['target_surface']==target
    o=obs[x['pair_id']]; assert o['provenance']=='AI_DIRECT_VISUAL_OBSERVATION'
    assert int(o['target_registered_cuts'])==len(x['target_cut_offsets_1based'].split(';'))
    assert int(o['control_registered_pseudo_cuts'])==len(x['control_cut_offsets_1based'].split(';'))

tr=sum(int(x['target_registered_cuts']) for x in obs.values()); cr=sum(int(x['control_registered_pseudo_cuts']) for x in obs.values())
tl=sum(int(x['target_secure_cuts']) for x in obs.values()); cl=sum(int(x['control_secure_cuts']) for x in obs.values())
ts=sum(int(x['target_distinct_separators'] or 0) for x in obs.values())
inputs=['GDT005_DUPLICATE_AUDIT.md','GDT005_MATCHED_PHYSICAL_CUT_METHOD.md','gdt005_matched_cut_selection.tsv','gdt005_matched_cut_observations.tsv','gdt006_cut_localizations.tsv','gdt004_module_shape_selection.tsv','experiments/semantic_assumptions/results/source_sta_group_alignment.tsv','build_gdt005_matched_physical_cut.py']
result={'experiment':'GDT005_MATCHED_PHYSICAL_CUT','status':'INVALIDATED_NO_MATCHED_LOCALIZATION_CAPACITY','exploratory':True,'pairs':9,'physical_folios':9,'registered_target_cuts':tr,'registered_control_pseudo_cuts':cr,'securely_localized_target_cuts':tl,'securely_localized_control_cuts':cl,'target_distinct_separators_on_secure_cuts':ts,'matched_difference':'NOT_COMPUTED_NO_SECURE_CONTROL_CUTS','duplicate_audit':'GENUINELY_NEW_NARROW_MATCHED_CONTROL','microspacing_or_stroke_test':'NOT_SCORED_NO_MATCHED_LOCALIZATION','failed_fourth_cells':'FORMAL_ABSENCES_HAVE_NO_PHYSICAL_TARGET_AND_WERE_NOT_INVENTED','holdout':{'f84r_opened':False,'f84r_rows_retained_joined_or_scored':0},'headline':'Later source-aware audit retained 3/17 target cuts but 0/17 control cuts; the former 0/17 versus 0/17 matched visual claim is withdrawn.','claim_ceiling':'Localization-capacity correction only; no matched spacing result, microspacing, pen trajectory, grapheme boundary, morpheme, slot, language, meaning, or translation.','inputs':{p:sh(p) for p in inputs}}
(R/'gdt005_matched_cut_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
