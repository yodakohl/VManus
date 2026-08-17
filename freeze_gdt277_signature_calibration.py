#!/usr/bin/env python3
"""Freeze GDT277 controls and exact GDT276 byte bindings before scoring."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

R=Path(__file__).resolve().parent
METHOD=R/'GDT277_GDT276_SIGNATURE_CALIBRATION_METHOD.md'
DESIGN=R/'gdt277_design.json';FM=R/'gdt277_gdt276_freeze_manifest.tsv';CM=R/'gdt277_control_manifest.tsv'

FROZEN={
'GDT276_RESIDUAL_CHANNEL_WORLD_COMPARISON_METHOD.md':'ca0fcda501dfa9c1fc6aa0f1d8e61df2c27dc9b6e77dd4416ff9c4a9669e0d5e',
'gdt276_design.json':'6d3c0da1bd32a1e7e768312a87f9d0ce9bf6605d70f4e185462b810aa2028eda',
'gdt276_design_validation.json':'a9134eab31b8eda6b1a872fb0ee8cc3cdfadecec23824941487ae7ba1ee6bdda',
'run_gdt276_residual_channel_world_comparison.py':'6ac3391d6f46c807320b7a96751dc91e6b96eccc8461888b9317b11a5b6c4fdc',
'validate_gdt276_residual_channel_world_comparison.py':'d4ad66b395d5277c1288b8edb9df78456d63939fabd6c9faf8d5f3268ff6215a',
'gdt276_result.json':'1422dc1e439be0efa453bcec9fc8f1a0846a07987b826c14863e74e330f842ac',
'gdt276_validation.json':'0b0c7c92ce92f9ae13de59e72a9a348b0d36e84aafe29fb349ad2fe4cc6b0688',
'gdt276_event_inventory.tsv':'6309382ea344ed77997980372b47161d10e5761e29d9f5cc67eda6fd1070c6d7',
'gdt276_world_scores.tsv':'b660118dc666f876db90a87290f0c64a48c42f8014c767f6f26187e4f730e3db',
'gdt276_folio_scores.tsv':'916e605989246bfc0fd8641c2914f7654244364305efa3c35f80812409844c54',
'gdt276_matched_controls.tsv':'1b231f1fff72dcb7ada98f742ea6b02601a35080755da1bde4ca022834be8e00',
'gdt276_null_worlds.tsv':'3e6e68244e01f5e5878b3428dc6650ae0c54922b7cd94e25e251c43164e3a674',
'gdt276_residual_channels.tsv':'120bb1484e2ab618b5a5dcd5c85390bad9299c32df0cefc9319185db27da8a0e',
'gdt276_residual_components.tsv':'a450ac68eedd0efc3d50936dff2bde733e6f9182269f67613e35e580d8219dad',
'gdt276_counterexamples.tsv':'af6b8a91b8fee6c56561690110746ca8e56bf641a44f2e4168353c4ad37d558c',
'GDT276_RESIDUAL_CHANNEL_WORLD_COMPARISON_REPORT.md':'ee79697627f65776118e6ce0b2fa909132d29ea8b6b76acf7268ca3577ddbf77'}

CONTROLS=[
('ORDINARY_NATURAL_LANGUAGE','Nuremberg expanded text','gdt155_unblinded_lines.tsv','gdt155_blinded_diplomatic.tsv','GDT155 held-book blind edge parser','PAIRED_EXPANSION_TRUTH','expanded source order; no meaning fields'),
('ABBREVIATION_HEAVY_MEDIEVAL','Nuremberg diplomatic abbreviation','gdt155_blinded_diplomatic.tsv','gdt155_unblinded_lines.tsv','GDT155 held-book blind edge parser','PAIRED_DIPLOMATIC_EXPANSION_TRUTH','visible abbreviation marker retained as display renderer'),
('ARBITRARY_LOCAL_CODEBOOK','GDT172 lexical System A','gdt172_blind_parses.json.gz','gdt172_sealed_oracle.json.gz','published GDT172 SURFACE_ONLY parser','FROZEN_REVERSIBLE_LEXICAL_ID_CODEBOOK','CONTROL_P only'),
('COMPOSITIONAL_TECHNICAL_NOTATION','GDT172 factorial System B','gdt172_blind_parses.json.gz','gdt172_sealed_oracle.json.gz','published GDT172 SURFACE_ONLY parser','FROZEN_REVERSIBLE_FACTORIAL_DISTRIBUTED_CONTROL','CONTROL_Q only'),
('HYBRID_SHORTHAND','GDT173 human-grown B2','gdt173_blind_parses.json.gz','gdt173_b2_sealed_oracle.json.gz','published GDT173 SURFACE_ONLY parser','FROZEN_REVERSIBLE_IRREGULAR_DISTRIBUTED_TABLE','CONTROL_R only')]

def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(path,rows):
 fields=list(rows[0]);
 with path.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 for p,h in FROZEN.items():assert sha(p)==h,(p,sha(p),h)
 frows=[{'artifact':p,'frozen_sha256':h,'immutability':'MUST_REMAIN_BYTE_IDENTICAL'} for p,h in FROZEN.items()];write(FM,frows)
 crows=[]
 for cid,label,obs,oracle,parser,truth,note in CONTROLS:
  for p in (obs,oracle):assert (R/p).is_file()
  crows.append({'control_id':cid,'ground_truth_label':label,'observation_input':obs,'observation_sha256':sha(obs),'oracle_or_pair_input':oracle,'oracle_or_pair_sha256':sha(oracle),'surface_parser':parser,'ground_truth_architecture':truth,'oracle_used_for_scoring':'0','note':note})
 write(CM,crows)
 design={'schema':'GDT277_SIGNATURE_CALIBRATION_DESIGN_V1','status':'FROZEN_BEFORE_GDT277_SCORING','gdt276_policy':'BYTE_IMMUTABLE_IMPORT_SCORER_AND_FIVE_WORLDS','control_ids':[x[0] for x in CONTROLS],
 'matched_view':{'events':4476,'length_quotas':{'2':1731,'3':277,'4':791,'5':1003,'6':448,'7':137,'8':60,'9':22,'10':7},'scaffold':'SHA256_SUBSET_OF_GDT276_EVENT_INVENTORY_WITH_EXACT_LENGTH_BY_POSITION','assignment':'SOURCE_ORDER_QUEUE_WITHIN_EXACT_PARSED_HOST_LENGTH','page_line_record_field_structure':'EXACT_GDT276_SELECTED_OPPORTUNITIES','native_adjacency':'NOT_PRESERVED_ACROSS_LENGTH_QUEUES;HYBRID_NOT_DIAGNOSTIC'},
 'alphabet_normalization':{'capacity':'20_NAMED_SYMBOLS_PLUS_UNKNOWN_PLUS_EOS_EQUALS_GDT276','map':'TOP20_VISIBLE_HOST_CHARACTERS_BY_FREQUENCY_THEN_UNICODE_TO_GDT276_USED20;OTHER_TO_QUESTION','phonetic_or_letter_claim':False},
 'instrument':{'models':['COMPRESSED_NATURAL_LANGUAGE','ABBREVIATION_HEAVY_LANGUAGE','LOCAL_CODEBOOK','TECHNICAL_NOTATION','HYBRID'],'context_buckets':256,'matched_control_worlds':64,'priors':'EXACT_GDT276','world_selector_bits':'EXACT_GDT276'},
 'diagnostic_signature':['ABBREVIATION_HEAVY_LANGUAGE_RANK_1','ABBREVIATION_BITS_LT_COMPRESSED_BITS','ABBREVIATION_MATCHED_SAVING_GT_0'],
 'representation_leakage_sensitivity':'LEARN_HOST_DEPENDENT_OPERATION_INVENTORY_AND_ALPHABET_WITHOUT_HELD_PSEUDO_FOLIO;NO_REMATCH_AFTER_REPARSE','semantic_assignments':0,'f84':{'inputs':0,'accessed':False,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},
 'inputs':{'gdt276_freeze_manifest':sha(FM.name),'control_manifest':sha(CM.name)},'documents':{METHOD.name:sha(METHOD.name)},'implementation':{Path(__file__).name:sha(Path(__file__).name)}}
 raw=json.dumps(design,sort_keys=True,separators=(',',':')).encode();design['content_sha256']=hashlib.sha256(raw).hexdigest();DESIGN.write_text(json.dumps(design,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':design['status'],'controls':len(crows),'events':4476,'gdt276_artifacts':len(frows)},sort_keys=True))
if __name__=='__main__':main()
