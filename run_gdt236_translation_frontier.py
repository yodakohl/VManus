#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
INPUTS=['gdt181_result.json','gdt182_result.json','gdt184_result.json','gdt185_result.json',
        'gdt227_result.json','gdt228_result.json','gdt229_result.json','gdt230_result.json',
        'gdt233_result.json','gdt234_result.json','gdt235_result.json']
DOCS=['GDT236_TRANSLATION_FRONTIER_METHOD.md','GDT236_TRANSLATION_FRONTIER_REPORT.md']
OUTS=['gdt236_layer_status.tsv','gdt236_theory_comparison.tsv','gdt236_prediction_registry.tsv']

def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write_tsv(name, header, rows):
    with (ROOT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n'); w.writerow(header); w.writerows(rows)

expected={
'gdt181_result.json':'LEADING_HYBRID_TECHNICAL_COMPILER_WITH_LOCAL_F57_F77_STATE_DECODING',
'gdt182_result.json':'LOCAL_F57_DECODER_DESCRIPTIVE_NOT_ABOVE_FEATURE_MULTIPLICITY',
'gdt184_result.json':'R2_FOURFOLD_REFERENCE_SEQUENCE_LEADING_FOUR_ELEMENT_ID_TABLE_FAILED',
'gdt185_result.json':'F57_R2_DOES_NOT_INDEX_F67V1_17_SECTOR_TEXT',
'gdt227_result.json':'ABSTRACT_Q13_INTERLINEAR_BUILT_IDENTITY_PLACEMENT_DESCRIPTIVE',
'gdt228_result.json':'MULTI_REGION_SHORT_ARGUMENT_LEAD_POSTSELECTED_LOW_CAPACITY',
'gdt229_result.json':'PROVISIONAL_Q13_SEMANTIC_LATTICE_BUILT_NO_LEXICAL_KEY',
'gdt230_result.json':'WRAPPER_INVARIANT_HOST_PLACEMENT_NUISANCE_EXPLAINED_NO_LEXICAL_CANDIDATE',
'gdt233_result.json':'TRANSFERRED_GRAPHICAL_LABEL_PREFIX_LAYER_PARTIAL_CONTENT_RESIDUAL_UNRESOLVED',
'gdt234_result.json':'LABEL_PREFIX_EXPLAINS_MOST_HOMOLOG_SIMILARITY_CONTENT_RESIDUAL_NOT_RECOVERED',
'gdt235_result.json':'LABEL_RESIDUAL_OBJECT_CLASS_NOT_TRANSFERABLE_SECTION_DOMINATES'}
loaded={p:json.loads((ROOT/p).read_text()) for p in INPUTS}
for p,s in expected.items(): assert loaded[p]['status']==s, (p,loaded[p].get('status'))

layers=[
('PAGE_PROFILE','page/register inventory and document ecology','SUPPORTED_FORMAL_PRIOR','content prior only; not a language or topic word'),
('PHYSICAL_LINE_RECORD','line-reset record/utterance-like compilation unit','SUPPORTED_STRUCTURAL','not a translated sentence boundary'),
('FIELD_SCAFFOLD','position/extent-derived instruction-like, short-like, close-like classes','ABSTRACT_ANALOGY_ONLY','GDT177 prevents semantic promotion'),
('GRAPHICAL_LABEL_PREFIX','14 transferred label-enriched family prefixes','SUPPORTED_PARTIAL_COMPILER','predicts label register, not object identity'),
('WRAPPER_FRAME_RIGHT_DY_B3','host-licensed record and rendering coordinates','SUPPORTED_FORMAL','no POS, morpheme, punctuation or meaning'),
('PAGE_HOST','opaque recurrent page/register-conditioned identity','CONTENT_CANDIDATE_UNRESOLVED','placement is nuisance-explained; exact dictionary tests fail'),
('LABEL_RESIDUAL','family material after strict transferred prefix','REGISTER_BOUND_OPAQUE','no held-folio object-class transfer'),
('LOCAL_DIAGRAM_STATE','f57/f77 quality-state decoder inherited from GDT181','DEMOTED_DESCRIPTIVE','feature multiplicity and failed bridge remove semantic force'),
('LANGUAGE_OR_PLAINTEXT','source language, phonology and words','UNIDENTIFIED','zero confirmed lexemes and clauses')]
write_tsv(OUTS[0],['layer','working_function','status','restriction'],layers)

theories=[
('COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE','2','real medieval abbreviation and recurrence are compatible','does not by itself generate the full line-reset compiler/algebra and no language mapping survives'),
('PURE_TECHNICAL_NOTATION','3','fits record fields, finite diagrams and rendering layers','underuses natural-language/abbreviation plausibility and still lacks a content key'),
('HYBRID_PAGE_CONDITIONED_RECORD_COMPILER','1_LEADING','explains record architecture, register-bound inventories, label compiler and opaque content channel together','content allocation may be lexical or distributed; no recovered dictionary')]
write_tsv(OUTS[1],['theory','rank','best_explanation','principal_failure'],theories)

preds=[
('TFP01','NEW_REPEATED_REFERENT','A singular human-bound referent repeated on at least two new physical folios will preserve more full-tuple or residual information than section-matched controls','required to promote any content unit'),
('TFP02','NEW_LABEL_REGISTER','On a newly annotated non-q13 label panel, the frozen GDT233 prefix union will enrich labelhood but will not by itself predict object class','tests the compiler/content separation'),
('TFP03','Q13_ROLE_GEOMETRY','Comparable pages with several independently bounded regions will contain more short fields than one-region pages under the frozen GDT229 classifier','tests the weak page-level record hypothesis'),
('TFP04','READABLE_TECHNICAL_HOMOLOG','A readable q13-like technical record will align broad long/short/closure field functions more reliably than exact source identities','tests document grammar without word guesses'),
('TFP05','FULL_TUPLE_VS_HOST','For an independently fixed repeated referent, full record tuple must beat exact PAGE_HOST alone if content is distributed','distinguishes lexical-address from distributed coding'),
('TFP06','F57_F77_REPLICATION','An independently selected comparable finite-state page must reproduce the frozen f57/f77 coordinate mapping before any local state gloss is restored','keeps the demoted decoder falsifiable')]
write_tsv(OUTS[2],['prediction_id','target','frozen_prediction','purpose'],preds)

result={
'experiment':'GDT236_TRANSLATION_FRONTIER_ARCHITECTURE',
'status':'HYBRID_RECORD_COMPILER_LEADS_CONTENT_CHANNEL_UNRESOLVED',
'working_generator':'PAGE_PROFILE + RECORD/FIELD_COMPILER + GRAPHICAL_LABEL_PREFIX? + OPAQUE_REGISTER_BOUND_CONTENT + RENDERER/CLOSURE',
'translation_frontier':'Document and field architecture are partly recoverable; no exact source unit carries a transferable meaning.',
'material_correction':'GDT181 f57/f77 semantic decoder is descriptive only after GDT182/GDT184/GDT185 and is removed from the executable semantic layer.',
'layers':len(layers),'predictions':len(preds),
'inputs':{p:sha(p) for p in INPUTS},'documents':{p:sha(p) for p in DOCS if (ROOT/p).exists()},
'outputs':{p:sha(p) for p in OUTS},'implementation':{Path(__file__).name:sha(Path(__file__).name)},
'f84':{'input':False,'retained':False,'scored':False,'prediction_target':False,'new_access':False},
'claim_ceiling':'A leading abductive generator and explicit translation frontier only; no word, morpheme, sound, language, plaintext, diagram value, semantic role, or translation.'}
core=dict(result); core.pop('content_hash',None)
result['content_hash']=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()
(ROOT/'gdt236_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':result['status'],'layers':len(layers),'predictions':len(preds)},sort_keys=True))
