#!/usr/bin/env python3
"""Freeze the form-blind CoReMA observation layer and held-oracle design."""
from __future__ import annotations
import csv, hashlib, json, re, xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'experiments/yolo/gdt376_corema_hidden_function_oracle'
ART=BASE/'artifacts'
ORACLE=ROOT/'gdt176_corema_role_oracle.tsv'
MANIFEST=ROOT/'gdt176_corema_collection_manifest.tsv'
CACHE=ROOT/'.gdt176/corema'
CONTRACT=ROOT/'experiments/yolo/gdt375_comparator_derived_functional_roadmap/artifacts/gdt375_detector_contract.tsv'
NS={'t':'http://www.tei-c.org/ns/1.0'}
XML_ID='{http://www.w3.org/XML/1998/namespace}id'
ROLE_TAGS={'title','opener','instruction','ingredient','tool','dish','name','closer','kitchenTip','householdTip','servingTip','time','dietetics','alternative','ref','unclear'}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def lname(t:str)->str:return t.rsplit('}',1)[-1]
def opaque(v:str)->str:return hashlib.sha256(('GDT376_OPAQUE_FORM_V1\0'+v).encode()).hexdigest()[:24]
def direct_text(node:ET.Element)->str:
    text=' '.join([node.text or '']+[child.tail or '' for child in node]).lower()
    return ' '.join(re.findall(r'[^\W_]+',text,flags=re.UNICODE))
def write_tsv(p:Path,rows:list[dict[str,object]]):
    with p.open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
    ART.mkdir(parents=True,exist_ok=True)
    collections=[]
    with MANIFEST.open(encoding='utf-8',newline='') as h:collections=[r['collection_id'] for r in csv.DictReader(h,delimiter='\t')]
    rows=[]
    for collection in collections:
        root=ET.parse(CACHE/f'{collection}.recipes.xml').getroot()
        recipes=root.findall('.//*[@type="recipe"]',NS)
        for recipe_ordinal,recipe in enumerate(recipes,1):
            recipe_id=recipe.get(XML_ID,f'{collection}.ordinal{recipe_ordinal}')
            nodes=[n for n in recipe.iter() if lname(n.tag) in ROLE_TAGS]
            vals=[direct_text(n) for n in nodes]
            for element_ordinal,value in enumerate(vals,1):
                rows.append({
                    'collection_id':collection,'recipe_id':recipe_id,'recipe_ordinal':recipe_ordinal,
                    'element_ordinal':element_ordinal,'opaque_form_id':opaque(value) if value else opaque(f'EMPTY:{recipe_id}:{element_ordinal}'),
                    'direct_token_count':len(value.split()),'observable_surface':int(bool(value)),
                    'record_element_count':len(nodes),'relative_position':f'{element_ordinal/max(1,len(nodes)):.9f}',
                })
    oracle=[]
    with ORACLE.open(encoding='utf-8',newline='') as h:oracle=list(csv.DictReader(h,delimiter='\t'))
    assert len(rows)==len(oracle)==27568
    assert all((a['collection_id'],a['recipe_id'],str(a['element_ordinal']))==(b['collection_id'],b['recipe_id'],b['element_ordinal']) for a,b in zip(rows,oracle))
    obs=ART/'gdt376_observation_layer.tsv';write_tsv(obs,rows)
    design={
      'schema':'GDT376_DESIGN_V1','status':'FROZEN_BEFORE_HELD_ORACLE_EVALUATION',
      'collections':collections,'folds':'leave one complete CoReMA collection out; train on remaining five',
      'hidden_oracle_fields':['role ALTERNATIVE','role TIME','role REF','role CLOSER','annotation exclusion','annotation analogy','annotation comparison','parent_instruction_ordinal'],
      'targets':['ALTERNATIVE','TIME','REF','CLOSER','EXCLUSION','ANALOGY','COMPARISON','PREDICATE_HEAD_WITH_DEPENDENTS','HIGH_VALENCY_HEAD','PARENTED_DEPENDENT','ANY_FUNCTIONAL_CLASS'],
      'observation_fields':list(rows[0]),
      'forbidden_inputs':['source strings','editor_english_label','role','annotation_flags','parent_instruction_ordinal','concept_id','Voynich data'],
      'models':['PREVALENCE','NUISANCE','OPAQUE_ID','STRUCTURE','STRUCTURE_PLUS_ID'],
      'fixed_logistic_l2':4.0,'null_worlds':1024,
      'null_strata':'held collection x record-length bucket x relative-position decile x direct-token-count bucket',
      'promotion':{'minimum_positive_collections':4,'minimum_positive_gain_folds':4,'minimum_pooled_auc':0.65,'minimum_ap_over_prevalence':1.5,'structure_gain_vs_nuisance_positive':True,'combined_gain_vs_identity_positive':True,'max_family_p_max':0.05},
      'voynich_transfer':'only detector families whose mapped hidden endpoint passes every promotion gate; no post-Voynich detector changes',
      'f84_accessed':False,'voynich_scored':False,
    }
    design['inputs']={str(p.relative_to(ROOT)):sha(p) for p in [ORACLE,MANIFEST,CONTRACT,*[CACHE/f'{c}.recipes.xml' for c in collections]]}
    design['observation_sha256']=sha(obs)
    design['oracle_commitment_sha256']=sha(ORACLE)
    design['content_hash']=hashlib.sha256(json.dumps(design,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    (ART/'gdt376_design_freeze.json').write_text(json.dumps(design,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'rows':len(rows),'observable':sum(int(r['observable_surface']) for r in rows),'collections':len(collections)}))
if __name__=='__main__':main()
