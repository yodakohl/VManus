#!/usr/bin/env python3
"""Publish the fixed GDT330 process-level access correction without reading source tables."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;DOC=R/'GDT330_F84R_METADATA_ACCESS_CORRECTION.md';OUT=R/'gdt330_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 v={'schema':'GDT330_F84R_METADATA_ACCESS_CORRECTION_V1','status':'F84R_PUBLIC_METADATA_ROW_TRANSIENTLY_PARSED_NO_VALUE_DISPLAYED_OR_USED','timestamp':'2026-08-18','access':{'global_page_annotation_tables_iterated_before_whitelist':True,'f84r_public_metadata_row_transiently_materialized':True,'f84r_value_printed_or_manually_inspected':False,'f84r_row_retained_selected_joined_scored_or_written':False,'f84r_transcription_family_page_host_grammar_or_formal_result_opened':False,'gdt328_gdt329_scientific_inputs_contain_f84':False},'scientific_consequence':'No GDT328 or GDT329 score or claim used f84; page-metadata no-access workflow was nevertheless breached and must be disclosed.','continuing_prohibition':'NO_FURTHER_F84R_ACCESS_WITHOUT_EXPLICIT_USER_AUTHORIZATION','documents':{DOC.name:sha(DOC)},'implementation':{Path(__file__).name:sha(Path(__file__))}};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':v['status']},sort_keys=True))
if __name__=='__main__':main()
